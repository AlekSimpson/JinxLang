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

    func copy() {
        return LinePosition(idx: self.idx, ln: self.ln, col: self.col)
    }
}

/* NODE */

protocol AbstractNode {
    var error: Error? { get set }
    var description: String { get }

    func as_string() -> String 
}

struct NumberNode: AbstractNode {
    var token: Token
    var error: Error?
    var description: String {
        return "NumberNode(\(token.type_name))"
    }

    func as_string() -> String {
        return token.as_string()
    }
}

struct VariableNode: AbstractNode {
    var token: Token
    var error: Error? 
    var description: String {
        return "VariableName(\(token.type_name))"
    }

    init() {
        self.token = Token()
        self.error = nil 
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
    var error: Error?
    var description: String {
        return "\(lhs.as_string()), \(op.as_string()), \(rhs.as_string())"
    }

    init(lhs: AbstractNode, op: AbstractNode, rhs: AbstractNode) {
        self.lhs = lhs 
        self.op = op
        self.rhs = rhs 
    }

    init(_ error: Error) {
        self.error = error
        self.lhs = VariableNode()
        self.op = VariableNode()
        self.rhs = VariableNode()
    }

    init() {
        self.error = Error(error_name: "", details: "")
        self.lhs = VariableNode()
        self.op = VariableNode()
        self.rhs = VariableNode()
    }

    func as_string() -> String {
        return self.description
    }
}