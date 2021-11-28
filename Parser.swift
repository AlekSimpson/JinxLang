/* PARSER */

class Parser {
    var tokens: [Token]
    var token_idx: Int = 0
    var curr_token: Token 

    init(tokens: [Token]) {
        self.tokens = tokens 
        self.curr_token = self.tokens[self.token_idx]
    }

    func advance() {
        self.token_idx += 1
        // print(self.token_idx)
        if self.token_idx < self.tokens.count {
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
            returnVal = NumberNode(token: self.curr_token)
            self.advance()
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
        var left: AbstractNode = function()

        while self.curr_token.type_name == ops[0] || self.curr_token.type_name == ops[1] {
            let op_tok = VariableNode(token: self.curr_token)
            self.advance()
            let right:AbstractNode = function()
            left = BinOpNode(lhs: left, op: op_tok, rhs: right)
        }

        return left
    }
}

class ParserResult { 
    var error: Bool?
    var node: AbstractNode? 

    init() {
        self.error = nil 
        self.token = nil 
    }

    func register(res:ParserResult){
        if res === ParserResult {
            if res.error { self.error = res.error }
            return res.node 
        }

        return res 
    }
    func success(){}
    func failure(){}
}