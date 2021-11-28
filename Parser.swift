/* PARSER */

class Parser {
    var tokens: [Token]
    var token_idx: Int = 0
    var curr_token: Token 

    init(tokens: [Token]) {
        self.tokens = tokens 
        self.curr_token = self.tokens[self.token_idx]
        // print("token count: \(self.tokens.count)")
    }

    func advance() {
        self.token_idx += 1
        // print("advancing \(self.token_idx)")
        if self.token_idx < self.tokens.count {
            self.curr_token = self.tokens[self.token_idx]
        }
    }

    func parse() -> AbstractNode {
        print(self.token_idx)
        let result = self.expr()
        return result
    }

    func factor() -> AbstractNode {
        let tok = self.curr_token
        var returnVal: AbstractNode = VariableNode()

        if tok.type == .FACTOR {
            returnVal = NumberNode(token: self.curr_token)
            self.advance()
        }

        return returnVal
    }

    func term() -> AbstractNode {
        return self.bin_op(func: factor, ops: [TT_MUL, TT_DIV])
    }

    func expr() -> AbstractNode {
        return self.bin_op(func: factor, ops: [TT_PLUS, TT_MINUS])
    }

    func bin_op(func function: () -> AbstractNode, ops: [String]) -> AbstractNode {
        let left: AbstractNode = function()
        var term: AbstractNode = VariableNode()

        while self.curr_token.type_name == ops[0] || self.curr_token.type_name == ops[1] {
            let op_tok = VariableNode(token: self.curr_token)
            self.advance()
            let right:AbstractNode = function()
            term = BinOpNode(lhs: left, op: op_tok, rhs: right)
        }

        return term
    }
}
