/* INTERPRETER */

class Interpreter {
    init(){}

    func visit(node: AbstractNode) {
        let func_index = node.classType

        switch func_index {
            case 0:
                visit_binop(node: node as! BinOpNode)
            case 1: 
                visit_number(node: node as! NumberNode)
            case 2: 
                visit_variable(node: node as! VariableNode)
            case 3: 
                visit_unary(node: node as! UnaryOpNode)
            default:
                print("no visit method found")
        }
    }

    // bin op
    func visit_binop(node: BinOpNode) {
        print("found bin op node")
        self.visit(node: node.lhs)
        self.visit(node: node.rhs)
    }

    // visit number
    func visit_number(node: NumberNode) {
        print("found number node")
    }

    // variable node 
    func visit_variable(node: VariableNode) {
        print("found variable node")
    }

    // unary node
    func visit_unary(node: UnaryOpNode) {
        print("found unary node")
        self.visit(node: node.node)
    }
}

