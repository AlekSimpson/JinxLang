from RuntimeResult import RuntimeResult 
from SymbolTable import SymbolTable  
from Error import RuntimeError 
import tokens as tk 
from Context import Context 
from Types import Number, string

class Interpreter:
    def visit(self, node, context):
        func_index = node.classType
        result = RuntimeResult()
        table = context.symbolTable.symbols
        print(f'given node is {node.as_string()}') 
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
                     self.visit_StringNode
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
        if err != None: 
            _ = result.failure(err)
        else: 
            return self.visit_VarAccessNode(node, ctx)

    def visit_StringNode(self, node, ctx):
        rt = RuntimeResult()
        print("string node visited")
        str = string(node.token.value)
        str.set_context(ctx)

        return rt.success(str)

    def visit_ForNode(self, node, ctx):
        rt = RuntimeResult()

        res_value = rt.register(self.visit(node.startValue, ctx))
        if rt.error != None: return rt 
        start_value = res_value.value.value 

        res_value = rt.register(self.visit(node.endValue, ctx))
        if rt.error != None: return rt 
        end_value = res_value.value.value 

        res_value = rt.register(self.visit(node.iterator, ctx))
        if rt.error != None: return rt 
        iterator_name = node.iterator.token.value 

        i = start_value

        table = ctx.symbolTable 

        while i.value < end_value:
            table.set_val(iterator_name, i)
            i.value += 1

            _ = rt.register(self.visit(node.bodyNode, ctx))
            if rt.error != None: return rt 

        return RuntimeResult()

    def visit_WhileNode(self, node, ctx):
        rt = RuntimeResult()

        while True:
            condition = rt.register(self.visit(node.conditionNode, ctx))
            if rt.error != None: return rt 
            cond_value = condition.value

            if not cond_value.is_true(): break 

            _ = rt.register(self.visit(node.bodyNode, ctx))
            if rt.error != None: return rt 

        return RuntimeResult()

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
        print("bin op being visited")
        left_vst = self.visit(node.lhs, ctx)
        _ = rt.register(left_vst)
        if rt.error != None: return rt 
        left = rt.value  

        right_vst = self.visit(node.rhs, ctx)
        _ = rt.register(right_vst)
        if rt.error != None: return rt 
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

        if error != None: returnVal = rt.failure(errr)
        if result != None: returnVal = rt.success(result)

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
            if res.error != None: return res 
            c_value = condiion_value.value

            if c_value.is_true():
                expr_value = res.register(self.visit(case_[1], ctx))
                if res.error != None: return res 
                e_value = expr_value.value
                return res.success(e_value)

        if node.else_case != None:
            else_value = res.register(self.visit(node.else_case, ctx))
            if res.error != None: return res 
            e_value = else_value.value
            return res.success(e_value)
        return RuntimeResult()

    def visit_unary(self, node, ctx):
        rt = RuntimeResult()
        number_reg = rt.register(self.visit(node.node, ctx))
        number = number_reg.value
        if rt.error != None: return rt 

        error = None 

        if node.token.type_name == tk.TT_MINUS:
            if number != None:
                (number, error) = number.multiplied(Number(-1))
        elif node.token.type_name == tk.TT_NOT:
            if number != None:
                (number, error) = number.not_op()

        if error != None:
            return rt.failure(error)
        else:
            return rt.success(number)

    def visit_VarAccessNode(self, node, ctx):
        res = RuntimeResult()
        var_name = node.token.value 

        value = None 
        if ctx.symbolTable != None:
            value = ctx.symbolTable.get_val(var_name)

        if value != None:
            return res.success(value)
        else:
            p = node.token.pos 
            error = RuntimeError(f'{var_name} is not defined', ctx, p)
            return res.failure(error)

    def visit_VarAssignNode(self, node, ctx):
        res = RuntimeResult()
        var_name = node.token.value 
        value = res.register(self.visit(node.value_node, ctx))
        if res.error != None: return res 

        ctx.symbolTable.set_val(var_name, value.value)
        return res.success(value.value)

    def visit_FuncDefNode(self, node, ctx):
        res = RuntimeResult()

        func_name = node.token.value 
        body_node = node.body_node
        func_arg_names = []

        a_name_tokens = []
        if node.arg_name_tokens != None: a_name_tokens = node.arg_name_tokens

        for arg_name in a_name_tokens:
            func_arg_names.append(arg_name.value)

        method = Function(func_name, body_node, func_arg_names)
        method.set_context(ctx)

        if func_name != None:
            sTable = SymbolTable()
            if ctx.symbolTable != None: sTable = ctx.symbolTable 
            sTable.set_val(func_name, method)

        return res.success(method) 

    def visit_CallNode(self, node, ctx):
        res = RuntimeResult()
        args = []

        value_to_call = res.register(self.visit(node.node_to_call, ctx))
        if res.error != None: return res 

        func_value = Function()
        if value_to_call.value != None: func_value = value_to_call.value 

        val_cal = func_value.copy()

        for arg_node in node.arg_nodes:
            x = arg_node.token.value 
            new = Number(x)

            args.append(new)

        return_value, return_res = val_cal.execute(args)
        _ = res.register(return_res)
        if res.error != None: return res 

        return res.success(return_value)
