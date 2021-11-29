/* NUMBERS */

// This class is for storing numbers
class Number {
    var value: Int 
    var pos_start: Int? 
    var pos_end: Int? 

    init(_ value: Int) {
        self.value = value 
        self.set_pos()
    }

    func set_pos(start: Int?=nil, end: Int?=nil) {
        self.pos_start = start
        self.pos_end = end 
    }

    func added(to other: Number) -> Number {
        // if type(of: other) === Number {
            return Number(self.value + other.value)
        // }
    }

    func subtracted(from other: Number) -> Number {
        // if type(of: other) === Number {
            return Number(self.value - other.value)
        // }
    }

    func multiplied(by other: Number) -> Number {
        // if type(of: other) === Number {
            return Number(self.value * other.value)
        // }
    }

    func divided(by other: Number) -> Number {
        // if type(of: other) === Number {
            return Number(self.value / other.value)
        // }
    }

    func print_self() -> String {
        return "\(self.value)"
    }
}

/* INTERPRETER */

class Interpreter {
    init(){}

    func visit(node: AbstractNode) -> Number {
        let func_index = node.classType
        var result: Number = Number(0)

        switch func_index {
            case 0:
                result = visit_binop(node: node as! BinOpNode)
            case 1: 
                result = visit_number(node: node as! NumberNode)
            // case 2: 
            //     result = visit_variable(node: node as! VariableNode)
            case 3: 
                result = visit_unary(node: node as! UnaryOpNode)
            default:
                print("no visit method found")
        }

        return result
    }

    // Bin Op Node 
    func visit_binop(node: BinOpNode) -> Number {
        var result: Number = Number(0)
        let left = self.visit(node: node.lhs)
        let right = self.visit(node: node.rhs)

        let op_node = node.op as! VariableNode

        switch op_node.token.type_name {
            case TT_PLUS: 
                result = left.added(to: right)
            case TT_MINUS:
                result = left.subtracted(from: right)
            case TT_MUL:
                result = left.multiplied(by: right)
            case TT_DIV: 
                result = left.divided(by: right)
            default: 
                result = Number(0)
        }

        return result 
    }

    // Visit Number
    func visit_number(node: NumberNode) -> Number {
        return Number(node.token.value as! Int)
    }

    // Variable Node 
    // func visit_variable(node: VariableNode) {
    //     print("found variable node")
    // }

    // Unary Node 
    func visit_unary(node: UnaryOpNode) -> Number{
        var number = self.visit(node: node.node)

        if node.op_tok.type_name == TT_MINUS {
            number = number.multiplied(by: Number(-1))
        }

        return number
    }
}

