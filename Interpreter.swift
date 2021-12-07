/* INTERPRETER */

class Interpreter {
    func visit(node: AbstractNode, context: Context) -> RuntimeResult {
        let func_index = node.classType
        var result = RuntimeResult()
        var table = [String : Double]()
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
            default:
                print("no visit method found")
        }

        return result
    }

    func check_for_declaration(table: [String : Double], node: AbstractNode, context: Context) -> Error? {
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
        
        var value:Double? = nil
        if let table = ctx.symbolTable { 
            value = table.get_val(name: var_name) 
        }
        

        if value != nil {
            return res.success(Number(value!))
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

        ctx.symbolTable!.set_val(name: var_name, value: value.value!.value)
        return res.success(value.value!)
    }
}

/* SYMBOL TABLE */

class SymbolTable {
    var symbols = [String:Double]()
    var parent:SymbolTable? = nil 

    init() {
        self.symbols = [String : Double]()
        self.parent = nil
    }

    func get_val(name: String) -> Double {
        let value = symbols[name]
        var returnVal: Double = 0.0

        if let v = value {
            returnVal = v 
        }

        if let p = parent {
            returnVal = p.get_val(name: name)
        }

        return returnVal
    }

    func set_val(name: String, value: Double) {
        self.symbols[name] = value 
    }

    func remove_val(name: String) {
        self.symbols.removeValue(forKey: name)
    }
}