/* PARSER */

class Parser {
    var tokens: [Token]
    var token_idx: Int = 0
    var curr_token: Token 

    init(tokens: [Token]) {
        self.tokens = tokens 
        self.curr_token = self.tokens[self.token_idx]
    }

    func advance() -> Token {
        self.token_idx += 1
        if self.token_idx < self.tokens.count {
            self.curr_token = self.tokens[self.token_idx]
        }
        return self.curr_token
    }

    func parse() -> (AbstractNode?, Error?) {
        let (node_result, parse_result) = self.expr()

        if let _ = parse_result.error {
            if self.curr_token.type != .EOF {
                var p = Position()
                if let position = self.curr_token.pos { p = position }
                return (nil, parse_result.failure(InvalidSyntaxError(details: "Expected an operator", pos: p)))
            }
            return (nil, parse_result.error)
        }

        return (node_result, nil)
    }

    func atom() -> (AbstractNode?, ParserResult) {
        let res = ParserResult()
        let tok = self.curr_token
        var returnVal: (AbstractNode?, ParserResult) = (nil, res)

        if tok.type == .FACTOR {
            let val = NumberNode(token: self.curr_token)
            _ = res.register(self.advance())
            returnVal = (res.success(val), res)
        }else if tok.type_name == "LPAREN" {
            _ = res.register(self.advance())
            let recurrsion = self.expr()
            if let epr = recurrsion.0 {
                _ = res.register(epr)
                if self.curr_token.type_name == "RPAREN" {
                    _ = res.register(self.advance())
                    returnVal = (res.success( epr ), res)
                }else {
                    var p = Position()
                    if let position = tok.pos { p = position }
                    _ = res.failure(InvalidSyntaxError(details: "Expected ')'", pos: p))
                    returnVal = (nil, res)
                }
            }

            if let err = recurrsion.1.error {
                _ = res.failure(err)
                returnVal = (nil, res)
            }
        }else {
            var p = Position()
            if let position = tok.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected int, float, '+', '-', or '('", pos: p))
            returnVal = (nil, res)
        }

        return returnVal
    }

    func power() -> (AbstractNode?, ParserResult) {
        return bin_op(funcA: atom, ops: TT_POW, funcB: factor)
    }

    func factor() -> (AbstractNode?, ParserResult) {
        let res = ParserResult()
        let tok = self.curr_token
        var returnVal: (AbstractNode?, ParserResult) = (nil, res)

        if tok.type_name == "PLUS" || tok.type_name == "MINUS" {
            _ = res.register(self.advance())
            let recurrsion = self.factor()
            if let ftr = recurrsion.0 {
                _ = res.register(ftr)
                returnVal = (res.success( UnaryOpNode(op_tok: tok, node: ftr) ), res)
            }

            if let err = recurrsion.1.error {
                _ = res.failure(err)
                returnVal = (nil, res)
            }
        }else {
            returnVal = self.power()
        }
        return returnVal
    }

    func term() -> (AbstractNode?, ParserResult) {
        return self.bin_op(func: factor, ops: [TT_MUL, TT_DIV])
    }

    func expr() -> (AbstractNode?, ParserResult) {
        return self.bin_op(func: term, ops: [TT_PLUS, TT_MINUS])
    }

    func bin_op(func function: () -> (AbstractNode?, ParserResult), ops: [String]) -> (AbstractNode?, ParserResult) {
        let res = ParserResult()

        var (left, parse_result) = function()
        _ = res.register(parse_result)
        if res.error != nil { return (nil, res) }

        while self.curr_token.type_name == ops[0] || self.curr_token.type_name == ops[1] {
            let op_tok = VariableNode(token: self.curr_token)
            _ = res.register(self.advance())

            let (right, parse_result_) = function()
            _ = res.register(parse_result_)
            if res.error != nil { return (nil, res) }

            left = BinOpNode(lhs: left!, op: op_tok, rhs: right!)
        }

        return (res.success(left ?? VariableNode()), res)
    }

    func bin_op(funcA functionA: () -> (AbstractNode?, ParserResult), ops: String, funcB functionB: () -> (AbstractNode?, ParserResult)) -> (AbstractNode?, ParserResult) {
        let res = ParserResult()

        var (left, parse_result) = functionA()
        _ = res.register(parse_result)
        if res.error != nil { return (nil, res) }

        // let condition = ((ops.count == 2) : (self.curr_token.type_name == ops[0] || self.curr_token.type_name == ops[1]) ? self.curr_token.type_name == ops[0])

        while self.curr_token.type_name == ops {
            let op_tok = VariableNode(token: self.curr_token)
            _ = res.register(self.advance())

            let (right, parse_result_) = functionB()
            _ = res.register(parse_result_)
            if res.error != nil { return (nil, res) }

            left = BinOpNode(lhs: left!, op: op_tok, rhs: right!)
        }
        return (res.success(left ?? VariableNode()), res)
    }
}

/* Parse Result */

class ParserResult { 
    var error: Error?
    var node: AbstractNode? 

    init() {
        self.error = nil 
        self.node = nil 
    }

    ///////////////////////////////////////////

    func register(_ res: ParserResult) -> AbstractNode {
        if res.error != nil { self.error = res.error }
        return res.node ?? VariableNode()
    }

    func register(_ _node: AbstractNode) -> AbstractNode {
        return _node
    }

    func register(_ _token: Token ) -> Token {
        return _token 
    }

    ///////////////////////////////////////////

    func success(_ node: AbstractNode) -> AbstractNode {
        self.node = node
        return node 
    }

    func failure(_ error: Error) -> Error {
        self.error = error 
        return self.error!
    }
}