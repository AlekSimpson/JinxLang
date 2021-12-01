/* NUMBERS */

// This class is for storing numbers
class Number {
    var value: Double 
    var pos_start: Int? 
    var pos_end: Int?

    init(_ value: Double) {
        self.value = value
        self.set_pos()
    }

    func set_pos(start: Int?=nil, end: Int?=nil) {
        self.pos_start = start
        self.pos_end = end 
    }

    func added(to other: Number) -> (Number?, Error?) {
        return (Number(self.value + other.value), nil)
    }

    func subtracted(from other: Number) -> (Number?, Error?) {
        return (Number(self.value - other.value), nil)
    }

    func multiplied(by other: Number) -> (Number?, Error?) {
        return (Number(self.value * other.value), nil)
    }

    func divided(by other: Number) -> (Number?, Error?) {
        if other.value == 0 { return (nil, RuntimeError(details: "cannot divide by zero")) }

        return (Number(self.value / other.value), nil)
    }

    func print_self() -> String {
        return "\(self.value)"
    }
}

/* INTERPRETER */

class Interpreter {
    func visit(node: AbstractNode) -> RuntimeResult {
        let func_index = node.classType
        var result = RuntimeResult()

        switch func_index {
            case 0:
                result = visit_binop(node: node as! BinOpNode)
            case 1:
                result = visit_number(node: node as! NumberNode)
            case 3:
                result = visit_unary(node: node as! UnaryOpNode)
            default:
                print("no visit method found")
        }

        return result
    }

    // Bin Op Node 
    func visit_binop(node: BinOpNode) -> RuntimeResult {
        let rt = RuntimeResult()
        var result: Number? = nil
        var error: Error? = nil 
        var returnVal: RuntimeResult = RuntimeResult()


        let left_vst = self.visit(node: node.lhs)
        let _ = rt.register(left_vst)
        let left = rt.value!
        if rt.error != nil { return rt }

        let right_vst = self.visit(node: node.rhs)
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
            default: 
                (result, error) = (Number(0), nil)
        }
        
        if let err = error { returnVal = rt.failure(err) }

        if let res = result { returnVal = rt.success(res) }
        return returnVal 
    }

    // Visit Number
    func visit_number(node: NumberNode) -> RuntimeResult {
        var val = 0.0
        if let v = node.token.value as? Float {
            val = Double(v)
        }else if let v = node.token.value as? Int {
            val = Double(v)
        }
        
        return RuntimeResult().success(
            Number(val)
        )
    }

    // Unary Node 
    func visit_unary(node: UnaryOpNode) -> RuntimeResult {
        let rt = RuntimeResult()
        let number_reg = rt.register(self.visit(node: node.node))
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