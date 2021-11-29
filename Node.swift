/* POSITION */

class LinePosition {
    var idx: Int
    var ln: Int 
    var col: Int 

    init(idx: Int, ln: Int, col: Int) {
        self.idx = idx 
        self.ln = ln 
        self.col = col 
    }

    func advance() { 
        self.idx += 1
        self.col += 1
    }

    // func copy() {
    //     return LinePosition(idx: self.idx, ln: self.ln, col: self.col)
    // }
}

/* NODE */

protocol AbstractNode {
    var description: String { get }
    var classType: Int { get }

    func as_string() -> String 
}

struct NumberNode: AbstractNode {
    var token: Token
    var description: String {
        return "NumberNode(\(token.type_name))"
    }
    var classType: Int {
        return 1
    }

    func as_string() -> String {
        return token.as_string()
    }
}

struct VariableNode: AbstractNode {
    var token: Token
    var description: String {
        return "VariableName(\(token.type_name))"
    }
    var classType: Int {
        return 2
    }

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
    var description: String {
        return "(\(lhs.as_string()), \(op.as_string()), \(rhs.as_string()))"
    }
    var classType: Int {
        return 0
    }

    init(lhs: AbstractNode, op: AbstractNode, rhs: AbstractNode) {
        self.lhs = lhs 
        self.op = op
        self.rhs = rhs 
    }

    init() {
        self.lhs = VariableNode()
        self.op = VariableNode()
        self.rhs = VariableNode()
    }

    func as_string() -> String {
        return self.description
    }
}

class UnaryOpNode: AbstractNode {
    var op_tok: Token 
    var node: AbstractNode
    var description: String {
        return "\(op_tok.as_string()) \(node.as_string())"
    }
    var classType: Int {
        return 3
    }

    init(op_tok: Token, node: AbstractNode){
        self.op_tok = op_tok
        self.node = node 
    }

    func as_string() -> String {
        return self.description 
    }
}