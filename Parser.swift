/* PARSER */

class Parser {
    var tokens: [Token]
    var token_idx: Int = -1
    var curr_token: Token 

    let operatorPrecedence: [String: Int] = [
        "PLUS" : 20,
        "MINUS" : 20,
        "MUL" : 40,
        "DIV" : 40
    ]

    init(tokens: [Token]) {
        self.tokens = tokens 
        self.curr_token = self.tokens[self.token_idx]
        self.advance()
    }

    func advance() {
        self.token_idx += 1
        if self.token_idx < self.tokens.count {
            self.curr_token = self.tokens[self.token_idx]
        }
    }

    func parse() -> AbstractNode {
        if self.token_idx == self.tokens.count { return }

        let left = NumberNode(token: self.curr_token)
        self.advance() 
        var op: AbstractNode

        if self.curr_token.type == .OPERATOR {
            op = VariableNode(token: self.curr_token)
            self.advance()
        }else {
            return BinOpNode(Error(error_name: "InvalidSyntax", details: "Expected an operator"))
        }

        return BinOpNode(lhs: left, op: op, rhs: parse())
    }
}
