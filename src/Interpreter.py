from SymbolTable import SymbolTable
from Error import *
import tokens as tk
from Context import Context
from Types import *
from Position import Position
from GlobalTable import global_symbol_table
from TypeKeywords import type_keywords, type_values
from TypeValue import TypeValue

class BaseFunction(Type):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos)
        new_context.symbolTable = SymbolTable()

        return new_context

    def check_args(self, arg_names, args):
        if len(args) > len(arg_names):
            return RuntimeError(f"to many arguements passed into function {self.name}", Context(), self.pos)

        if len(args) < len(arg_names):
            return RuntimeError(f"to few arguements passed into function {self.name}", Context(), self.pos)

        return None

    def populate_args(self, arg_names, args, exec_ctx):
        for i in range(0, len(arg_names)):
            arg_name = arg_names[i]
            arg_value = args[i]

            arg_value.set_context(exec_ctx)
            exec_ctx.symbolTable.set_val(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_ctx):
        check = self.check_args(arg_names, args)
        if isinstance(check, Error):
            return check

        self.populate_args(arg_names, args, exec_ctx)

        return None

class Function(BaseFunction):
    def __init__(self, name=None, returnType=None, body_node=None, arg_nodes=None, arg_types=None, should_return_nil=False):
        super().__init__(name)
        self.body_node = body_node
        self.arg_nodes = arg_nodes
        self.arg_types = arg_types
        self.returnType = returnType
        self.should_return_nil = should_return_nil

    def execute(self, args):
        interpreter = Interpreter()

        exec_ctx = self.generate_new_context()

        check = self.check_and_populate_args(self.arg_nodes, args, exec_ctx)
        if isinstance(check, Error):
            return check

        body = interpreter.visit(self.body_node, exec_ctx)
        if isinstance(body, Error):
            return body

        final_value = body
        if not isinstance(body, Number):
            final_value = Number() if self.should_return_nil else body.elements[-1]

        self.context = exec_ctx
        return final_value

    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_nodes, self.should_return_nil)
        copy.set_context(self.context)
        return copy

    def print_self(self):
        return f"<function {self.name}>"


class BuiltinFunction(BaseFunction):
    def __init__(self, name_id):
        super().__init__(name_id)
        self.name_id = name_id

    def isNum(self, value):
        return_val = True
        try:
            int(value)
        except:
            return_val = False
        return return_val

    def check_is_var(self, value):
        if value in global_symbol_table.symbols:
            return True
        return False

    # checks for variables and makes sure passed in arguments are valid
    def process_parameter(self, parameter, exec_ctx):
        return_value = parameter
        if parameter.value in global_symbol_table.symbols:
            val = global_symbol_table.get_val(parameter.value)
            return val.print_self()

        if isinstance(return_value, Array):
            return_value = return_value.print_self()
        elif isinstance(return_value, Integer) or isinstance(parameter, Number):
            return_value = parameter.value
        elif isinstance(return_value, string):
            return_value = parameter.print_self()
        else:
            return_value = RuntimeError("Cannot reference undefined variable", exec_ctx, Position())

        return return_value

    def process_parameters(self, parameters, exec_ctx):
        processed = []
        for param in parameters:
            processed.append(self.process_parameter(param, exec_ctx))

        return processed

    def execute(self, args):
        exec_ctx = self.generate_new_context()

        method_arg_names = [
            ["value"], ["array", "value"], ["fn"],
            ["array"], ["array", "index"], ["array"]
        ]
        methods = [
            self.execute_print, self.execute_append, self.execute_run,
            self.execute_length, self.execute_remove, self.execute_removeLast
        ]

        if self.name_id < 0 or self.name_id > len(methods) - 1:
            return "built in method undefined"

        method = methods[self.name_id]
        method_a_names = method_arg_names[self.name_id]

        check = self.check_and_populate_args(method_a_names, args, exec_ctx)
        if isinstance(check, Error):
            return check

        return_value = method(exec_ctx)

        return return_value

    def execute_print(self, exec_ctx):
        arg_name = exec_ctx.symbolTable.get_val("value")
        proc = self.process_parameter(arg_name, exec_ctx)

        if isinstance(proc, Error):
            print(proc.as_string())
            return None
        print(proc)

        return None

    def execute_append(self, exec_ctx):
        array = exec_ctx.symbolTable.get_val("array")
        new_value = exec_ctx.symbolTable.get_val("value")
        procs = self.process_parameters([array, new_value], exec_ctx)

        for proc in procs:
            if isinstance(proc, Error):
                print(proc.as_string())
                return None

        el_id = array.element_id
        type_check = self.check_types_match(el_id, new_value, array)
        if type_check is not None:
            return type_check

        array.elements.append(new_value)
        return None

    def execute_remove(self, exec_ctx):
        array = exec_ctx.symbolTable.get_val("array")
        index = exec_ctx.symbolTable.get_val("index")
        procs = self.process_parameters([array, index], exec_ctx)

        for proc in procs:
            if isinstance(proc, Error):
                print(proc.as_string())
                return None

        array.elements.pop(index.value)

        return None

    def execute_removeLast(self, exec_ctx):
        array = exec_ctx.symbolTable.get_val("array")
        proc = self.process_parameter(array, exec_ctx)

        if isinstance(proc, Error):
            print(proc.as_string())
            return None

        array.elements.pop()

        return None

    def check_types_match(self, a, b, name):
        #if not isinstance(a, type(b)):
        if a.ID != b.ID:
            return RuntimeError(f"Cannot assign value of {b.description} to array of type {a.description} {name}", Context(), Position())
        return None

    def execute_length(self, exec_ctx):
        arr_arg = exec_ctx.symbolTable.get_val("array")
        length = arr_arg.length
        return Integer(64, length)

    def copy(self):
        copy = BuiltinFunction(self.name_id)
        copy.set_context(self.context)
        return copy

    def print_self(self):
        return f"<function {self.name}>"

    def execute_run(self, exec_ctx):
        fn = exec_ctx.symbolTable.get_val("fn")

        if not isinstance(fn.value, str):
            return RuntimeError("Arguements must be string", Context(), Position())

        fn = fn.value

        try:
            with open(fn, "r") as f:
                script = f.read()
        except Exception as e:
            return RuntimeError("Failed to execute file" + str(e), Context(), Position())

        from run import run

        return_value, error = run(script, fn)

        if error is not None:
            return RuntimeError("Failed to finish file", Context(), Position())

        return return_value

BuiltinFunction.print = BuiltinFunction(0)
BuiltinFunction.append = BuiltinFunction(1)
BuiltinFunction.run = BuiltinFunction(2)
BuiltinFunction.length = BuiltinFunction(3)
BuiltinFunction.remove = BuiltinFunction(4)
BuiltinFunction.removeLast = BuiltinFunction(5)

class Interpreter:
    def check_for_error(self, node):
        if isinstance(node, Error):
            return node
        return None

    def visit(self, node, context):
        err_check = self.check_for_error(node)
        if err_check is not None:
            return err_check
        if node is None:
            return RuntimeError("Invalid syntax", context, Position())

        func_index = node.classType
        #print(f"[{func_index}] - {node.as_string()}")
        # ^^^^ Keep for debugging purposes ^^^^
        table = context.symbolTable.symbols
        result = None

        options = [
            self.visit_binop,          # 0
            self.visit_number,         # 1
            "VariableNode",            # 2
            self.visit_unary,          # 3
            "VarAccessNode",           # 4
            self.visit_VarAssignNode,  # 5
            self.visit_IfNode,         # 6
            self.visit_ForNode,        # 7
            self.visit_WhileNode,      # 8
            self.visit_FuncDefNode,    # 9
            self.visit_CallNode,       # 10
            self.visit_StringNode,     # 11
            self.visit_ListNode,       # 12
            self.visit_SetArrNode,     # 13
            self.visit_GetArrNode,     # 14
            self.visit_ReturnNode,     # 15
            self.visit_VarUpdateNode,  # 16
            self.visit_float,          # 17
            self.visit_ObjectDefNode,  # 18
            self.visit_DotNode,        # 19
        ]

        if func_index == 4:
            result = self.AccessNode(node, context, table)
        elif func_index != 4:
            result = options[func_index](node, context)
        elif func_index >= 0 or func_index <= 11:
            print("no visi method found")

        return result

    def AccessNode(self, node, ctx, table):
        err = self.check_for_declaration(table, node, ctx)
        if err is not None:
            return err
        else:
            return self.visit_VarAccessNode(node, ctx)

    def visit_StringNode(self, node, ctx):
        string_val = string(node.token.value)
        string_val.set_context(ctx)

        return string_val

    def visit_ListNode(self, node, context):
        elements = []

        for element_node in node.element_nodes:
            el = self.visit(element_node, context)
            elements.append(el)

            if isinstance(el, Error):
                return el
            if element_node.classType == 15:
                break

        element_id = Void()
        if len(elements) != 0:
            type_dec = node.element_nodes[0].token.type_dec
            if type_dec is not None:
                element_id = node.element_nodes[0].token.type_dec.type_obj

        arr = Array(elements, element_id)
        arr.set_context(context)

        return arr

    def visit_ForNode(self, node, ctx):
        res_value = self.visit(node.startValue, ctx)
        if isinstance(res_value, Error):
            return res_value

        start_value = res_value.value

        res_value = self.visit(node.endValue, ctx)
        if isinstance(res_value, Error):
            return res_value
        end_value = res_value.value

        res_value = self.visit(node.iterator, ctx)
        if isinstance(res_value, Error):
            return res_value
        iterator_name = node.iterator.token.value

        i = start_value

        table = ctx.symbolTable

        while i < end_value:
            table.set_val(iterator_name, Number(i))
            i += 1

            body_vst = self.visit(node.bodyNode, ctx)
            if isinstance(body_vst, Error):
                return body_vst

        return Number(0)

    def visit_WhileNode(self, node, ctx):
        while True:
            condition = self.visit(node.conditionNode, ctx)
            if isinstance(condition, Error):
                return condition

            if not condition.is_true():
                break

            body_vst = self.visit(node.bodyNode, ctx)
            if isinstance(body_vst, Error):
                return body_vst

        return Number(0)

    def check_for_declaration(self, table, node, context):
        access_node = node
        name = access_node.token.value
        err = None

        if not name in table:
            pos = access_node.token.pos
            err = RuntimeError(f'"{name}" is not defined', context, pos)

        return err

    def visit_binop(self, node, ctx):
        result = None
        error = None

        left_vst = self.visit(node.lhs, ctx)
        if isinstance(left_vst, Error):
            return left_vst
        left = left_vst

        right_vst = self.visit(node.rhs, ctx)
        if isinstance(right_vst, Error):
            return right_vst
        right = right_vst

        op_node = node.op
        name_cond = op_node.token.type_name
        if name_cond == tk.TT_PLUS:
            result = left.added(right)
        elif name_cond == tk.TT_MINUS:
            result = left.subtracted(right)
        elif name_cond == tk.TT_MUL:
            result = left.multiplied(right)
        elif name_cond == tk.TT_DIV:
            result = left.divided(right)
        elif name_cond == tk.TT_POW:
            result = left.power(right)
        elif name_cond == tk.TT_EE:
            result = left.comp_eq(right)
        elif name_cond == tk.TT_NE:
            result = left.comp_ne(right)
        elif name_cond == tk.TT_LT:
            result = left.comp_lt(right)
        elif name_cond == tk.TT_GT:
            result = left.comp_gt(right)
        elif name_cond == tk.TT_LOE:
            result = left.comp_loe(right)
        elif name_cond == tk.TT_GOE:
            result = left.comp_goe(right)
        elif name_cond == tk.TT_AND:
            result = left.comp_and(right)
        elif name_cond == tk.TT_OR:
            result = left.comp_or(right)
        else:
            result = Number(0)

        return result

    def visit_number(self, node, ctx):
        entry = node.token.pos
        child_context = Context("<number>", ctx, entry)

        val = node.token.value

        p = node.token.pos

        num = Number(val, p)
        num.set_context(child_context)

        return num

    def visit_float(self, node, ctx):
        entry = node.token.pos
        child_context = Context("<float>", ctx, entry)

        val = node.token.value

        p = node.token.pos

        flt = Float(64, val)
        flt.set_context(child_context)

        return flt

    def visit_IfNode(self, node, ctx):
        for case_ in node.cases:
            condition_value = self.visit(case_[0], ctx)
            if isinstance(condition_value, Error):
                return condition_value
            c_value = condition_value

            if c_value.is_true():
                expr_value = self.visit(case_[1], ctx)
                if isinstance(expr_value, Error):
                    return expr_value

                return Number.nil if case_[2] else expr_value

        if node.else_case is not None:
            else_value = self.visit(node.else_case[0], ctx)
            if isinstance(else_value, Error):
                return else_value

            return Number.nil if node.else_case[1] else else_value

        return Number.nil

    def visit_unary(self, node, ctx):
        number = self.visit(node.node, ctx)

        if isinstance(number, Error):
            return number

        if node.op_tok.type_name == tk.TT_MINUS:
            if number is not None:
                number = number.multiplied(Number(-1))
        elif node.op_tok.type_name == tk.TT_NOT:
            if number is not None:
                number = number.not_op()

        return number

    def visit_VarUpdateNode(self, node, ctx):
        var_name = node.token.value

        # check if variable exsits
        isDeclaredErr = self.check_for_declaration(ctx.symbolTable.symbols, node, ctx)
        if isDeclaredErr is not None:
            return isDeclaredErr

        # check if types match
        value = ctx.symbolTable.get_val(var_name)

        new_val = self.visit(node.value_node, ctx)
        if isinstance(new_val, Error):
            return new_val

        # Check if types match
        new = new_val
        previous_value = value
        types_match = self.check_types_match(new, previous_value, var_name, ctx, node)
        if types_match is not None:
            return types_match

        # update
        ctx.symbolTable.set_val(var_name, new_val)
        return new_val

    def visit_VarAccessNode(self, node, ctx):
        var_name = node.token.value

        value = None
        if ctx.symbolTable is not None:
            value = ctx.symbolTable.get_val(var_name)
        if value is not None:
            return value
        else:
            p = node.token.pos
            return RuntimeError(f"{var_name} is not defined", ctx, p)

    def check_element_types(self, array_type, elements, var_name, ctx, node):
        for element in elements:
            #element_value = element.token.type_dec.type_obj
            type_check = self.check_types_match(array_type, element, var_name, ctx, node)
            if type_check is not None:
                return type_check
        return "TYPES MATCH"

    def visit_VarAssignNode(self, node, ctx):
        var_name = node.token.value
        value = self.visit(node.value_node, ctx)
        if isinstance(value, Error):
            return value

        variable_type = node.type.type_obj
        types_match = self.check_types_match(value, variable_type, var_name, ctx, node)
        if types_match is not None:
            return types_match

        if isinstance(value, Array):
            #list_values = node.value_node.element_nodes
            list_values = value.elements
            array_type = node.type.element_type.type_obj
            types_match = self.check_element_types(array_type, list_values, var_name, ctx, node)
            if types_match != "TYPES MATCH":
                return types_match

        ctx.symbolTable.set_val(var_name, value)
        return value

    def visit_FuncDefNode(self, node, ctx):
        func_name = node.token.value
        body_node = node.body_node
        func_arg_names = []
        func_arg_types = []

        # Checks if arguements exist
        a_name_tokens = []
        if node.arg_name_tokens is not None:
            a_name_tokens = node.arg_name_tokens

        a_type_tokens = []
        if node.arg_type_tokens is not None:
            a_type_tokens = node.arg_type_tokens

        # Populates arguement arrays with arg types and names
        for arg_name in a_name_tokens:
            func_arg_names.append(arg_name.value)

        for arg_type in a_type_tokens:
            func_arg_types.append(arg_type.type_dec.type_obj)

        method = Function(func_name, node.returnType, body_node, func_arg_names, func_arg_types, node.should_return_nil)
        method.set_context(ctx)

        if func_name is not None:
            sTable = SymbolTable()
            if ctx.symbolTable is not None:
                sTable = ctx.symbolTable
            sTable.set_val(func_name, method)

        return method

    def visit_ObjectDefNode(self, node, ctx):
        object_name = node.name.value
        body_node = node.body_node
        obj_atrr_names = []
        obj_atrr_types = []

        o_name_tokens = []
        if node.attribute_name_tokens is not None:
            o_name_tokens = node.attribute_name_tokens

        o_type_tokens = []
        if node.attribute_type_tokens is not None:
            o_type_tokens = node.attribute_type_tokens

        # Populate atrribute arrays with attr names and types
        for attr_name in o_name_tokens:
            obj_atrr_names.append(attr_name.value)

        for attr_type in o_type_tokens:
            obj_atrr_types.append(attr_type.type_dec.type_obj)

        object = Object(object_name, body_node, obj_atrr_names, obj_atrr_types)
        ctx.symbolTable.set_val(object_name, object)
        type_keywords.append(object_name)
        type_values.append(TypeValue(1, object))

        #XXX: May or may not have to check for if the object has already been declared here

        return object

    def visit_DotNode(self, node, ctx):
        reference_chain = node.lhs
        root_ref = None
        for ref in reference_chain:
            c = ctx if root_ref is None else root_ref.context
            root_ref = self.visit(ref, c)
            if isinstance(root_ref, Error):
                return root_ref

        final_node = self.visit(node.rhs, root_ref.context)
        return final_node

    def visit_ReturnNode(self, node, ctx):
        value = Number.nil
        if node.node_to_return is not None:
            value = self.visit(node.node_to_return, ctx)
            return value
        return value

    def visit_CallNode(self, node, ctx):
        args = []

        value_to_call = self.visit(node.node_to_call, ctx)
        if isinstance(value_to_call, Error):
            return value_to_call

        func_value = Function()
        if value_to_call is not None:
            func_value = value_to_call

        val_cal = func_value

        i = 0
        for arg_node in node.arg_nodes:
            new = arg_node.token.value
            new = self.visit(arg_node, ctx)
            if isinstance(new, Array):
                new = Array(new.elements, new.element_id)

            #if not isinstance(func_value, BuiltinFunction):
            #    types_match = self.check_types_match(new, func_value.arg_types[i], func_value.name, ctx, node)
            #    if types_match is not None:
            #        return types_match

            args.append(new)
            i += 1

        return_value = None
        if isinstance(val_cal, Object):
            return_value = val_cal.initialize(args)
        else:
            return_value = val_cal.execute(args)
        if isinstance(return_value, Error):
            return return_value

        # Check if return value and declared return value match
        if not isinstance(func_value, BuiltinFunction) and not isinstance(func_value, Object):
            _return = return_value
            func_return = func_value.returnType.type_dec.type_obj
            if not isinstance(func_value, BuiltinFunction):
                types_match = self.check_types_match(_return, func_return, func_value.name, ctx, node)
                if types_match is not None:
                    return types_match
        return return_value

    def check_types_match(self, a, b, name, ctx, node):
        #if not isinstance(a, type(b)):
        if a.ID != b.ID:
            pos = node.token.pos
            return RuntimeError(f"Cannot assign value of {a.description} to type {b.description} {name}", ctx, pos)
        return None

    def visit_GetArrNode(self, node, ctx):
        array_node = self.visit(node.array, ctx)
        if isinstance(array_node, Error):
            return array_node

        index = self.visit(node.index, ctx)
        if isinstance(index, Error):
            return index

        return_value = array_node.get(index.value)

        return return_value

    def visit_SetArrNode(self, node, ctx):
        array_node = self.visit(node.array, ctx)
        if isinstance(array_node, Error):
            return array_node

        index = self.visit(node.index, ctx)
        if isinstance(index, Error):
            return index

        idx = index.value

        new_val = self.visit(node.new_val, ctx)
        if isinstance(new_val, Error):
            return new_val

        set_return = array_node.set(idx, new_val)

        return set_return
