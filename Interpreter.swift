/* INTERPRETER */

class Interpreter {
    func visit(node: AbstractNode, context: Context) -> RuntimeResult {
        let func_index = node.classType
        var result = RuntimeResult()
        var table = [String : Number]()
        if let t = context.symbolTable { table = t.symbols }

        switch func_index {
            case 0:
                result = visit_binop(node: node as! BinOpNode, ctx: context)
            case 1:
                result = visit_number(node: node as! NumberNode, ctx: context)
            case 3:
                result = visit_unary(node: node as! UnaryOpNode, ctx: context)
            case 4: 
                let err = check_for_declaration(table: table, node: node, context: context)

                if let e = err { 
                    _ = result.failure(e)
                }else {
                    result = visit_VarAccessNode(node: node as! VarAccessNode, ctx: context)
                }
            case 5: 
                result = visit_VarAssignNode(node: node as! VarAssignNode, ctx: context)
            case 6:
                result = visit_IfNode(node: node as! IfNode, ctx: context)
            case 7: 
                result = visit_ForNode(node: node as! ForNode, ctx: context)
            case 8: 
                result = visit_WhileNode(node: node as! WhileNode, ctx: context)
            case 9:
                result = visit_FuncDefNode(node: node as! FuncDefNode, ctx: context)
            case 10:
                result = visit_CallNode(node: node as! CallNode, ctx: context)
            default:
                print("no visit method found")
        }

        return result
    }

    func visit_ForNode(node: ForNode, ctx: Context) -> RuntimeResult {
        let rt = RuntimeResult()    
        
        var res_value = rt.register(self.visit(node: node.startValue, context: ctx))
        if rt.error != nil { return rt }
        let start_value = res_value.value!

        res_value = rt.register(self.visit(node: node.endValue, context: ctx))
        if rt.error != nil { return rt }
        let end_value = res_value.value!.value 

        res_value = rt.register(self.visit(node: node.iterator, context: ctx))
        if rt.error != nil { return rt }
        let iterator_name = node.iterator.token.value as! String 

        let i = start_value

        var table = SymbolTable()
        if let t = ctx.symbolTable { table = t } 

        while i.value < end_value {
            table.set_val(name: iterator_name, value: i)
            i.value += 1

            _ = rt.register(self.visit(node: node.bodyNode, context: ctx))
            if rt.error != nil { return rt }
        }

        return RuntimeResult()
    }

    func visit_WhileNode(node: WhileNode, ctx: Context) -> RuntimeResult {
        let rt = RuntimeResult()

        while true {
            let condition = rt.register(self.visit(node: node.conditionNode, context: ctx))
            if rt.error != nil { return rt }
            let cond_value = condition.value!

            if !cond_value.is_true() { break }
            
            _ = rt.register(self.visit(node: node.bodyNode, context: ctx))
            if rt.error != nil { return rt }
        }

        return RuntimeResult()
    }

    func check_for_declaration(table: [String : Number], node: AbstractNode, context: Context) -> Error? {
        let access_node = node as! VarAccessNode
        let name = access_node.token.value as! String 
        var err:Error? = nil         

        if table[name] == nil {
            var pos = Position()
            if let p = access_node.token.pos { pos = p }
            err = RuntimeError(details: "'\(name)' is not defined", context: context, pos: pos)
        }
        return err
    }

    // Bin Op Node 
    func visit_binop(node: BinOpNode, ctx: Context) -> RuntimeResult {
        let rt = RuntimeResult()
        var result: Number? = nil
        var error: Error? = nil 
        var returnVal: RuntimeResult = RuntimeResult()
        
        // Get left node 
        let left_vst = self.visit(node: node.lhs, context: ctx)
        let _ = rt.register(left_vst)
        if rt.error != nil { return rt }
        let left = rt.value!

        // Get right node
        let right_vst = self.visit(node: node.rhs, context: ctx)
        let _ = rt.register(right_vst)
        if rt.error != nil { return rt }
        let right = rt.value!

        let op_node = node.op as! VariableNode
        
        switch op_node.token.type_name {
            case TT_PLUS: 
                (result, error) = left.added(to: right)
            case TT_MINUS:
                (result, error) = left.subtracted(from: right)
            case TT_MUL:
                (result, error) = left.multiplied(by: right)
            case TT_DIV: 
                (result, error) = left.divided(by: right)
            case TT_POW:
                (result, error) = left.power(by: right)
            case TT_EE:
                (result, error) = left.comp_eq(by: right)
            case TT_NE:
                (result, error) = left.comp_ne(by: right)
            case TT_LT:
                (result, error) = left.comp_lt(by: right)
            case TT_GT:
                (result, error) = left.comp_gt(by: right)
            case TT_LOE:
                (result, error) = left.comp_loe(by: right)
            case TT_GOE:
                (result, error) = left.comp_goe(by: right)
            case TT_AND: 
                (result, error) = left.comp_and(by: right)
            case TT_OR: 
                (result, error) = left.comp_or(by: right)
            default: 
                (result, error) = (Number(0), nil)
        }
        
        if let err = error { returnVal = rt.failure(err) }

        if let res = result { returnVal = rt.success(res) }
        return returnVal 
    }

    // Visit Number
    func visit_number(node: NumberNode, ctx: Context) -> RuntimeResult {
        var entry = Position()
        if let position = node.token.pos { entry = position }
        let child_context = Context(display_name: "<number>", parent: ctx, parent_entry_pos: entry)

        var val = 0.0
        if let v = node.token.value as? Float {
            val = Double(v)
        }else if let v = node.token.value as? Int {
            val = Double(v)
        }
        
        var p = Position()
        if let position = node.token.pos { p = position }

        let num = Number(val, pos: p)
        num.set_context(ctx: child_context)

        return RuntimeResult().success(
            num 
        )
    }

    func visit_IfNode(node: IfNode, ctx: Context) -> RuntimeResult {
        let res = RuntimeResult()

        for _case in node.cases {
            let condition_value = res.register(self.visit(node: _case[0], context: ctx))
            if res.error != nil { return res }
            let c_value = condition_value.value!

            if c_value.is_true() {
                let expr_value = res.register(self.visit(node: _case[1], context: ctx))
                if res.error != nil { return res }
                let e_value = expr_value.value!
                return res.success(e_value)
            }
        }

        if let e_case = node.else_case {
            let else_value = res.register(self.visit(node: e_case, context: ctx))
            if res.error != nil { return res }
            let e_value = else_value.value!
            return res.success(e_value)
        }
        return RuntimeResult()
    }

    // Unary Node 
    func visit_unary(node: UnaryOpNode, ctx: Context) -> RuntimeResult {
        let rt = RuntimeResult()
        let number_reg = rt.register(self.visit(node: node.node, context: ctx))
        var number: Number? = number_reg.value!
        if rt.error != nil { return rt }

        var error: Error? = nil 

        if node.token.type_name == TT_MINUS {
            if let num = number {
                (number, error) = num.multiplied(by: Number(-1))
            }
        }else if node.token.type_name == TT_NOT {
            if let num = number {
                (number, error) = num.not()
            }
        }

        if let err = error {
            return rt.failure(err)
        }else {
            return rt.success(number!)
        }
    }

    func visit_VarAccessNode(node: VarAccessNode, ctx: Context) -> RuntimeResult {
        let res = RuntimeResult()
        let var_name = node.token.value as! String
        
        var value:Number? = nil
        if let table = ctx.symbolTable { 
            value = table.get_val(name: var_name) 
        }
        

        if value != nil {
            return res.success(value!)
        }else {
            var p = Position()
            if let pos = node.token.pos { p = pos }
            let error = RuntimeError(details: "'\(var_name)' is not defined", context: ctx, pos: p)
            return res.failure(error)
        }
    }

    func visit_VarAssignNode(node: VarAssignNode, ctx: Context) -> RuntimeResult {
        let res = RuntimeResult()
        let var_name = node.token.value as! String
        let value = res.register(self.visit(node: node.value_node, context: ctx))
        if res.error != nil { return res }

        ctx.symbolTable!.set_val(name: var_name, value: value.value!)
        return res.success(value.value!)
    }

    // create Function type and add it to the symbol table [function name (String) : function (Function)]
    func visit_FuncDefNode(node: FuncDefNode, ctx: Context) -> RuntimeResult {
        let res = RuntimeResult()

        let func_name = node.token.value 
        let body_node = node.body_node
        var func_arg_names:[String] = []
        
        var a_name_tokens: [Token] = []
        if let unwrapped = node.arg_name_tokens { a_name_tokens = unwrapped }

        for arg_name in a_name_tokens {
            func_arg_names.append(arg_name.value as! String)
        }

        let method = Function(name: func_name as? String, body_node: body_node, arg_nodes: func_arg_names)
        method.set_context(ctx: ctx)

        if func_name != nil {
            var sTable = SymbolTable()
            if let unwrapped = ctx.symbolTable { sTable = unwrapped }
            sTable.set_val(name: func_name as! String, value: method)
        }

        return res.success(method)
    }

    // Get function name (value_to_call) then get the Function type from the symbol tree and then execute that function 
    func visit_CallNode(node: CallNode, ctx: Context) -> RuntimeResult {
        let res = RuntimeResult()
        var args: [Number] = []
        
        let value_to_call = res.register(self.visit(node: node.node_to_call, context: ctx))
        if res.error != nil { return (res) }

        var func_value = Function()
        if let unwrapped = value_to_call.value { func_value = unwrapped as! Function }

        let val_cal = func_value.copy()

        for arg_node in node.arg_nodes {
            let x = Double(arg_node.token.value as! Int)
            let new = Number(x)

            args.append(new)
        }

        let (return_value, return_res) = val_cal.execute(args: args)
        _ = res.register(return_res)
        if res.error != nil { return res }
        return res.success(return_value!)
    }
}