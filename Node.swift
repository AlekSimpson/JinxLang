/* NODE */

protocol AbstractNode {
    var token: Token { get set }
    var description: String { get }
    var classType: Int { get }

    func as_string() -> String
}

struct NumberNode: AbstractNode {
    var token: Token
    var description: String { return "NumberNode(\(token.type_name))" }
    var classType: Int { return 1 }

    func as_string() -> String {
        return token.as_string()
    }
}

struct VarAccessNode: AbstractNode {
    var token: Token 
    var description: String { return "VarAccessNode(\(token.type_name))" }
    var classType: Int { return 4 }
    init(token: Token) {
        self.token = token
    }

    func as_string() -> String {
        return token.as_string()
    }
}

struct VarAssignNode: AbstractNode {
    var token: Token 
    var value_node: AbstractNode 
    var description: String { return "VarAssignNode(\(token.type_name), \(value_node))" }
    var classType: Int { return 5 }

    init(token: Token, value_node: AbstractNode) {
        self.token = token
        self.value_node = value_node
    }

    func as_string() -> String {
        return token.as_string()
    }
}

struct VariableNode: AbstractNode {
    var token: Token
    var description: String { return "VariableName(\(token.type_name))" }
    var classType: Int { return 2 }

    init() {
        self.token = Token()
    }

    init(token: Token) {
        self.token = token 
    }
    
    func as_string() -> String {
        return token.as_string()
    }
}

struct BinOpNode: AbstractNode {
    let lhs: AbstractNode
    let op: AbstractNode
    let rhs: AbstractNode
    var description: String { return "(\(lhs.as_string()), \(op.as_string()), \(rhs.as_string()))" }
    var classType: Int { return 0 }
    var token: Token

    init(lhs: AbstractNode, op: AbstractNode, rhs: AbstractNode) {
        self.lhs = lhs 
        self.op = op
        self.rhs = rhs 
        self.token = Token() 
    }

    init() {
        self.lhs = VariableNode()
        self.op = VariableNode()
        self.rhs = VariableNode()
        self.token = Token() 
    }

    func as_string() -> String {
        return self.description
    }
}

class UnaryOpNode: AbstractNode {
    var token: Token 
    var node: AbstractNode
    var description: String {
        return "\(token.as_string()) \(node.as_string())"
    }
    var classType: Int {
        return 3
    }

    init(op_tok: Token, node: AbstractNode){
        self.token = op_tok
        self.node = node 
    }

    func as_string() -> String {
        return self.description 
    }
}