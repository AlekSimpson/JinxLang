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
}

/* NODE */

protocol AbstractNode {
    var error: Error? { get set }
    var description: String { get }
}

struct NumberNode: AbstractNode {
    var token: Token
    var error: Error?

    var description: String {
        return "NumberNode(\(token))"
    }
}

struct VariableNode: AbstractNode {
    var token: Token
    var error: Error? 

    var description: String {
        return "VariableName(\(token))"
    }
}

struct BinOpNode: AbstractNode {
    let lhs: AbstractNode
    let op: AbstractNode 
    let rhs: AbstractNode
    var error: Error?

    var description: String {
        return "BinOpNode(\(lhs), \(op), \(rhs))"
    }

    init(lhs: AbstractNode, op: AbstractNode, rhs: AbstractNode) {
        self.lhs = lhs 
        self.op = op
        self.rhs = rhs 
    }

    init(_ error: Error) {
        self.error = error 
    }
}