/* INTERPRETER */

class Interpreter {
    func visit(node: AbstractNode, context: Context) -> RuntimeResult {
        let func_index = node.classType
        var result = RuntimeResult()

        switch func_index {
            case 0:
                result = visit_binop(node: node as! BinOpNode, ctx: context)
            case 1:
                result = visit_number(node: node as! NumberNode, ctx: context)
            case 3:
                result = visit_unary(node: node as! UnaryOpNode, ctx: context)
            default:
                print("no visit method found")
        }

        return result
    }

    // Bin Op Node 
    func visit_binop(node: BinOpNode, ctx: Context) -> RuntimeResult {
        let rt = RuntimeResult()
        var result: Number? = nil
        var error: Error? = nil 
        var returnVal: RuntimeResult = RuntimeResult()

        // Get context for nodes
        var entry = Position()
        if node.lhs is NumberNode {
            let node = node.lhs as! NumberNode
            if let position = node.token.pos { entry = position }
        }
        let child_context = Context(display_name: "<binary operation>", parent: ctx, parent_entry_pos: entry)
        
        // Get left node 
        let left_vst = self.visit(node: node.lhs, context: child_context)
        let _ = rt.register(left_vst)
        let left = rt.value!
        if rt.error != nil { return rt }

        // Get right node
        let right_vst = self.visit(node: node.rhs, context: child_context)
        let _ = rt.register(right_vst)
        let right = rt.value!
        if rt.error != nil { return rt }

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

        if node.op_tok.type_name == TT_MINUS {
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
}

/* RUNTIME RESULT */

class RuntimeResult {
    var value: Number? 
    var error: Error?

    init(value: Number, error: Error){
        self.value = value 
        self.error = error 
    }

    init() {
        self.value = nil 
        self.error = nil 
    }
    
    func register(_ result: RuntimeResult) -> RuntimeResult {
        if result.error != nil { self.error = result.error } 
        self.value = result.value
        return self 
    } 

    func success(_ value: Number) -> RuntimeResult {
        self.value = value 
        return self 
    }

    func failure(_ error: Error) -> RuntimeResult {
        self.error = error 
        return self
    }
}