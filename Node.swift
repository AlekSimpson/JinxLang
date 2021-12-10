/* NODE */

protocol AbstractNode {
    var token: Token { get set }
    var description: String { get }
    var classType: Int { get }

    func as_string() -> String
}

struct NumberNode: AbstractNode {
    var token: Token
    var direct_value: Number? = nil 
    var description: String { return "NumberNode(\(token.type_name))" }
    var classType: Int { return 1 }

    init(direct_value: Number) {
        self.direct_value = direct_value
        self.token = Token()
    }

    init(token: Token) {
        self.token = token 
        self.direct_value = nil 
    }

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

struct IfNode: AbstractNode {
    var token: Token
    var cases: [[AbstractNode]]
    var else_case: AbstractNode?
    var description: String { return "IfNode(\(token.type_name))" } 
    var classType: Int { return 6 }

    init(cases: [[AbstractNode]], else_case: AbstractNode?=nil) {
        self.cases = cases
        self.else_case = else_case
        self.token = cases[0][0].token
    }

    func as_string() -> String {
        return token.as_string()
    }
}

struct ForNode: AbstractNode {
    var token: Token 
    var startValue: NumberNode 
    var endValue: NumberNode 
    var bodyNode: AbstractNode
    var iterator: VarAssignNode
    var description:String { return "ForNode(\(token.type_name))" }
    var classType: Int { return 7 }

    init(iterator: VarAssignNode, startValue: NumberNode, endValue: NumberNode, bodyNode: AbstractNode) {
        self.iterator = iterator 
        self.startValue = startValue
        self.endValue = endValue
        self.bodyNode = bodyNode
        self.token = startValue.token 
    }

    func as_string() -> String {
        return token.as_string()
    }
}

struct WhileNode: AbstractNode {
    var token: Token 
    var conditionNode: AbstractNode 
    var bodyNode: AbstractNode
    var description: String { return "WhileNode(\(token.type_name))" }
    var classType: Int { return 8 }

    init(conditionNode: AbstractNode, bodyNode: AbstractNode) {
        self.conditionNode = conditionNode
        self.bodyNode = bodyNode
        self.token = conditionNode.token 
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