/* PARSER */

class Parser {
    var tokens: [Token]
    var token_idx: Int = -1
    var curr_token: Token 

    init(tokens: [Token]) {
        self.tokens = tokens 
        self.curr_token = self.tokens[self.token_idx]
        self.advance()
    }

    func advance() {
        self.token_idx += 1
        if self.token_idx < (self.tokens.count - 1) {
            self.curr_token = self.tokens[self.token_idx]
        }
    }

    func parse() -> AbstractNode {
        let result = self.expr()
        return result
    }

    func factor() -> AbstractNode {
        let tok = self.curr_token
        var returnVal: AbstractNode = VariableNode()

        if tok.type == .FACTOR {
            self.advance()
            returnVal = NumberNode(token: self.curr_token)
        }

        return returnVal
    }

    func term() -> AbstractNode {
        return self.bin_op(func: factor, ops: [TT_MUL, TT_DIV])
    }

    func expr() -> AbstractNode {
        return self.bin_op(func: term, ops: [TT_PLUS, TT_MINUS])
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





    // func parse() -> AbstractNode {

    // }

    // func parse() -> AbstractNode {
    //     let left = NumberNode(token: self.curr_token)
    //     if self.token_idx == (self.tokens.count - 1) { return left }

    //     self.advance() 
    //     var op: AbstractNode

    //     if self.curr_token.type == .OPERATOR {
    //         op = VariableNode(token: self.curr_token)
    //         self.advance()
    //     }else {
    //         return BinOpNode(Error(error_name: "InvalidSyntax", details: "Expected an operator"))
    //     }

    //     return BinOpNode(lhs: left, op: op, rhs: parse())
    // }
}
