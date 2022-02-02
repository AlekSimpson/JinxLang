from RuntimeResult import RuntimeResult
from SymbolTable import SymbolTable
from Error import RuntimeError
import tokens as tk
from Context import Context
from Types import Number, string, Array, Type
from Position import Position
from GlobalTable import global_symbol_table


class BaseFunction(Type):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos)

        # table = SymbolTable()
        # if new_context.parent.symbolTable != None: table = new_context.parent.symbolTable
        new_context.symbolTable = SymbolTable()

        return new_context

    def check_args(self, arg_names, args):
        res = RuntimeResult()

        if len(args) > len(arg_names):
            err = RuntimeError(
                f"to many arguements passed into function {name}", new_context, self.pos
            )
            _ = res.failure(err)
            return res

        if len(args) < len(arg_names):
            err = RuntimeError(
                f"to few arguements passed into function {name}", new_context, self.pos
            )
            _ = res.failure(err)
            return res

        return res.success(None)

    def populate_args(self, arg_names, args, exec_ctx):
        for i in range(0, len(arg_names)):
            arg_name = arg_names[i]
            arg_value = args[i]

            arg_value.set_context(exec_ctx)
            exec_ctx.symbolTable.set_val(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_ctx):
        res = RuntimeResult()

        res.register(self.check_args(arg_names, args))
        if res.error != None:
            return res

        self.populate_args(arg_names, args, exec_ctx)

        return res.success(None)


class Function(BaseFunction):
    def __init__(
        self,
        name=None,
        returnType=None,
        body_node=None,
        arg_nodes=None,
        should_return_nil=False,
    ):
        super().__init__(name)
        self.body_node = body_node
        self.arg_nodes = arg_nodes
        self.returnType = returnType
        self.should_return_nil = should_return_nil

    def execute(self, args):
        res = RuntimeResult()
        interpreter = Interpreter()

        exec_ctx = self.generate_new_context()

        res.register(self.check_and_populate_args(self.arg_nodes, args, exec_ctx))
        if res.error != None:
            return (None, res)

        body_res = interpreter.visit(self.body_node, exec_ctx)
        _ = res.register(body_res)

        final_value = res.value
        if not isinstance(res.value, Number):
            final_value = Number() if self.should_return_nil else res.value.elements[-1]
        if res.error != None:
            return (None, res)

        self.context = exec_ctx
        return (final_value, res)

    def copy(self):
        copy = Function(
            self.name, self.body_node, self.arg_nodes, self.should_return_nil
        )
        copy.set_context(self.context)
        return copy

    def print_self(self):
        return f"<function {self.name}>"


class BuiltinFunction(BaseFunction):
    def __init__(self, name_id):
        super().__init__(name_id)
        self.name_id = name_id

    def isNum(self, value):
        returnVal = True
        try:
            int(value)
        except:
            returnVal = False
        return returnVal

    def check_is_var(self, value):
        if value in global_symbol_table.symbols:
            return True
        return False

    def execute(self, args):
        res = RuntimeResult()
        exec_ctx = self.generate_new_context()

        method_arg_names = [["value"], ["array", "value"], ["fn"]]
        methods = [self.execute_print, self.execute_append, self.execute_run]

        if self.name_id < 0 or self.name_id > len(methods) - 1:
            return "built in method undefined"

        method = methods[self.name_id]
        method_a_names = method_arg_names[self.name_id]

        res.register(self.check_and_populate_args(method_a_names, args, exec_ctx))
        if res.error != None:
            return res

        return_value, return_res = method(exec_ctx)
        res.register(return_res)

        return (return_value, res)

    def execute_print(self, exec_ctx):
        res = RuntimeResult()
        value_arg = exec_ctx.symbolTable.get_val("value")
        value = Number(value_arg.value)
        isNumber = True
        if not self.isNum(value.value):
            isNumber = False
            value = string(value)

        # Check if printing a number
        if isNumber:
            print(value.value)
        else:
            # Check if value is a variable
            if value.value.value in global_symbol_table.symbols:
                val = global_symbol_table.get_val(value.value.value)
                # Check if variable is an array
                if isinstance(val, Array):
                    print(val.print_self())
                else:
                    # print variable
                    print(val.value)
            else:
                # value is a string
                print(value.value.value)
        return (Number(0), res)

    def execute_append(self, exec_ctx):
        res = RuntimeResult()
        arr_arg = exec_ctx.symbolTable.get_val("array").value
        value_obj = exec_ctx.symbolTable.get_val("value")
        value = value_obj.value
        arr = global_symbol_table.get_val(arr_arg).elements

        if not self.isNum(value_obj):
            if self.check_is_var(value):
                value_obj = global_symbol_table.get_val(value)

        arr.append(value_obj)

        return (None, res)

    def copy(self):
        copy = BuiltinFunction(self.name_id)
        copy.set_context(self.context)
        return copy

    def print_self(self):
        return f"<function {self.name}>"

    def execute_run(self, exec_ctx):
        res = RuntimeResult()
        fn = exec_ctx.symbolTable.get_val("fn")

        if not isinstance(fn.value, str):
            err = RuntimeError("Arguements must be string", Context(), Position())
            res.failure(err)
            return (None, res)

        fn = fn.value

        try:
            with open(fn, "r") as f:
                script = f.read()
        except Exception as e:
            err = RuntimeError("Failed to execute file" + str(e), Context(), Position())
            res.failure(err)
            return (None, res)

        from run import run

        return_value, error = run(script, fn)

        if error != None:
            err = RuntimeError("Failed to finish file", Context(), Position())
            res.failure(err)
            return (None, res)

        return (return_value, res)


BuiltinFunction.print = BuiltinFunction(0)
BuiltinFunction.append = BuiltinFunction(1)
BuiltinFunction.run = BuiltinFunction(2)


class Interpreter:
    def visit(self, node, context):
        func_index = node.classType
        # print(f"[{func_index}] - {node.as_string()}")
        # ^^^^ Keep for debugging purposes ^^^^
        result = RuntimeResult()
        table = context.symbolTable.symbols

        options = [
            self.visit_binop,
            self.visit_number,
            "VariableNode",
            self.visit_unary,
            "VarAccessNode",
            self.visit_VarAssignNode,
            self.visit_IfNode,
            self.visit_ForNode,
            self.visit_WhileNode,
            self.visit_FuncDefNode,
            self.visit_CallNode,
            self.visit_StringNode,
            self.visit_ListNode,
            self.visit_SetArrNode,
            self.visit_GetArrNode,
            self.visit_ReturnNode,
            self.visit_VarUpdateNode,
        ]

        if func_index == 4:
            result = self.AccessNode(node, context, table)
        elif func_index != 4:
            result = options[func_index](node, context)
        elif func_index >= 0 or func_index <= 11:
            print("no visi method found")

        return result

    def AccessNode(self, node, ctx, table):
        res = RuntimeResult()
        err = self.check_for_declaration(table, node, ctx)
        if err is not None:
            res.failure(err)
        else:
            return self.visit_VarAccessNode(node, ctx)

    def visit_StringNode(self, node, ctx):
        rt = RuntimeResult()

        str = string(node.token.value)
        str.set_context(ctx)

        return rt.success(str)

    def visit_ListNode(self, node, context):
        res = RuntimeResult()
        elements = []
        for element_node in node.element_nodes:
            el = self.visit(element_node, context)
            _ = res.register(el)
            elements.append(el.value)
            if res.error != None:
                return res
            if element_node.classType == 15:
                break

        arr = Array(elements)
        arr.set_context(context)

        return res.success(arr)

    def visit_ForNode(self, node, ctx):
        rt = RuntimeResult()

        res_value = rt.register(self.visit(node.startValue, ctx))
        if rt.error != None:
            return rt
        start_value = res_value.value.value

        res_value = rt.register(self.visit(node.endValue, ctx))
        if rt.error != None:
            return rt
        end_value = res_value.value.value

        res_value = rt.register(self.visit(node.iterator, ctx))
        if rt.error != None:
            return rt
        iterator_name = node.iterator.token.value

        i = start_value

        table = ctx.symbolTable

        while i < end_value:
            table.set_val(iterator_name, Number(i))
            i += 1

            _ = rt.register(self.visit(node.bodyNode, ctx))
            if rt.error != None:
                return rt

        return rt.success(Number(0))

    def visit_WhileNode(self, node, ctx):
        rt = RuntimeResult()

        while True:
            condition = rt.register(self.visit(node.conditionNode, ctx))
            if rt.error != None:
                return rt
            cond_value = condition.value

            if not cond_value.is_true():
                break

            _ = rt.register(self.visit(node.bodyNode, ctx))
            if rt.error != None:
                return rt

        return rt.success(Number(0))

    def check_for_declaration(self, table, node, context):
        access_node = node
        name = access_node.token.value
        err = None

        if table[name] == None:
            pos = access_node.token.pos
            err = RuntimeError(f'"{name}" is not defined', context, pos)

        return err

    def visit_binop(self, node, ctx):
        rt = RuntimeResult()
        result = None
        error = None
        returnVal = RuntimeResult()

        left_vst = self.visit(node.lhs, ctx)
        _ = rt.register(left_vst)
        if rt.error != None:
            return rt
        left = rt.value

        right_vst = self.visit(node.rhs, ctx)
        _ = rt.register(right_vst)
        if rt.error != None:
            return rt
        right = rt.value

        op_node = node.op
        name_cond = op_node.token.type_name
        if name_cond == tk.TT_PLUS:
            result, error = left.added(right)
        elif name_cond == tk.TT_MINUS:
            result, error = left.subtracted(right)
        elif name_cond == tk.TT_MUL:
            result, error = left.multiplied(right)
        elif name_cond == tk.TT_DIV:
            result, error = left.divided(right)
        elif name_cond == tk.TT_POW:
            result, error = left.power(right)
        elif name_cond == tk.TT_EE:
            result, error = left.comp_eq(right)
        elif name_cond == tk.TT_NE:
            result, error = left.comp_ne(right)
        elif name_cond == tk.TT_LT:
            result, error = left.comp_lt(right)
        elif name_cond == tk.TT_GT:
            result, error = left.comp_gt(right)
        elif name_cond == tk.TT_LOE:
            result, error = left.comp_loe(right)
        elif name_cond == tk.TT_GOE:
            result, error = left.comp_goe(right)
        elif name_cond == tk.TT_AND:
            result, error = left.comp_and(right)
        elif name_cond == tk.TT_OR:
            result, error = left.comp_or(right)
        else:
            result, error = (Number(0), None)

        if error != None:
            returnVal = rt.failure(error)
        if result != None:
            returnVal = rt.success(result)
        return returnVal

    def visit_number(self, node, ctx):
        entry = node.token.pos
        child_context = Context("<number>", ctx, entry)

        val = node.token.value

        p = node.token.pos

        num = Number(val, p)
        num.set_context(child_context)

        return RuntimeResult().success(num)

    def visit_IfNode(self, node, ctx):
        res = RuntimeResult()

        for case_ in node.cases:
            condiion_value = res.register(self.visit(case_[0], ctx))
            if res.error != None:
                return res
            c_value = condiion_value.value

            if c_value.is_true():
                expr_value = self.visit(case_[1], ctx)
                res.register(expr_value)
                if res.error != None:
                    return res
                e_value = expr_value.value

                return res.success(Number.nil if case_[2] else e_value)

        if node.else_case != None:
            else_value = res.register(self.visit(node.else_case[0], ctx))
            if res.error != None:
                return res
            e_value = else_value.value

            return res.success(Number.nil if node.else_case[1] else e_value)

        return res.success(Number.nil)

    def visit_unary(self, node, ctx):
        rt = RuntimeResult()
        number_reg = rt.register(self.visit(node.node, ctx))
        number = number_reg.value
        if rt.error != None:
            return rt

        error = None

        if node.op_tok.type_name == tk.TT_MINUS:
            if number != None:
                (number, error) = number.multiplied(Number(-1))
        elif node.op_tok.type_name == tk.TT_NOT:
            if number != None:
                (number, error) = number.not_op()

        if error != None:
            return rt.failure(error)
        else:
            return rt.success(number)

    def visit_VarUpdateNode(self, node, ctx):
        res = RuntimeResult()
        var_name = node.token.value

        # check if variable exsits
        isDeclaredErr = self.check_for_declaration(ctx.symbolTable.symbols, node, ctx)
        if isDeclaredErr != None:
            return isDeclaredErr

        # check if types match
        value = ctx.symbolTable.get_val(var_name)

        new_val = res.register(self.visit(node.value_node, ctx))
        if res.error is not None:
            return res

        if not isinstance(new_val.value, type(value)):
            pos = node.token.pos
            _ = res.failure(
                RuntimeError(
                    f"Cannot assign {type(new_val.value)} value to {type(value)} type {var_name}",
                    ctx,
                    pos,
                )
            )
            return res
        # update
        ctx.symbolTable.set_val(var_name, new_val.value)
        return res.success(new_val.value)

    def visit_VarAccessNode(self, node, ctx):
        res = RuntimeResult()
        var_name = node.token.value

        value = None
        if ctx.symbolTable is not None:
            value = ctx.symbolTable.get_val(var_name)
        if value is not None:
            return res.success(value)
        else:
            p = node.token.pos
            error = RuntimeError(f"{var_name} is not defined", ctx, p)
            return res.failure(error)

    def visit_VarAssignNode(self, node, ctx):
        res = RuntimeResult()
        var_name = node.token.value
        value = res.register(self.visit(node.value_node, ctx))
        if res.error != None:
            return res

        ctx.symbolTable.set_val(var_name, value.value)
        return res.success(value.value)

    def visit_FuncDefNode(self, node, ctx):
        res = RuntimeResult()

        func_name = node.token.value
        body_node = node.body_node
        func_arg_names = []

        a_name_tokens = []
        if node.arg_name_tokens != None:
            a_name_tokens = node.arg_name_tokens

        for arg_name in a_name_tokens:
            func_arg_names.append(arg_name.value)

        method = Function(
            func_name,
            node.returnType,
            body_node,
            func_arg_names,
            node.should_return_nil,
        )
        method.set_context(ctx)

        if func_name != None:
            sTable = SymbolTable()
            if ctx.symbolTable != None:
                sTable = ctx.symbolTable
            sTable.set_val(func_name, method)

        return res.success(method)

    def visit_ReturnNode(self, node, ctx):
        res = RuntimeResult()
        value = Number.nil
        if node.node_to_return != None:
            value = res.register(self.visit(node.node_to_return, ctx))
            return res.success(value.value)
        return res.success(value)

    def visit_CallNode(self, node, ctx):
        res = RuntimeResult()
        args = []

        value_to_call = res.register(self.visit(node.node_to_call, ctx))
        if res.error != None:
            return res

        func_value = Function()
        if value_to_call.value != None:
            func_value = value_to_call.value

        val_cal = func_value

        for arg_node in node.arg_nodes:
            x = arg_node.token.value
            new = Number(x)

            args.append(new)

        return_value, return_res = val_cal.execute(args)
        res.register(return_res)
        if res.error is not None:
            return res

        # Check if return value and declared return value match
        if not isinstance(
            return_value.value, type(value_to_call.value.returnType.type_dec[0])
        ):
            pos = node.token.pos
            error = RuntimeError(
                f"type of return value does not match return type of function {value_to_call.value.name}()",
                ctx,
                pos,
            )
            return res.failure(error)

        return res.success(return_value)

    def visit_GetArrNode(self, node, ctx):
        res = RuntimeResult()

        arrayNodeRes = res.register(self.visit(node.array, ctx))
        if res.error != None:
            return res
        arrayNode = arrayNodeRes.value

        index = res.register(self.visit(node.index, ctx))
        if res.error != None:
            return res

        return_value, return_res = arrayNode.get(index.value)
        _ = res.register(return_res)
        if return_res.error != None:
            return res

        return res.success(return_value)

    def visit_SetArrNode(self, node, ctx):
        res = RuntimeResult()

        arrayNodeRes = res.register(self.visit(node.array, ctx))
        if res.error != None:
            return res
        arrayNode = arrayNodeRes.value

        index = res.register(self.visit(node.index, ctx))
        if res.error != None:
            return res

        idx = index.value.value

        new_val = res.register(self.visit(node.new_val, ctx))
        if res.error != None:
            return res

        set_return, set_res = arrayNode.set(idx, new_val.value)
        _ = res.register(set_res)
        if res.error != None:
            return res

        return res
