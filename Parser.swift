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

        if let err = parse_result.error {
            if self.curr_token.type != .EOF {
                return (nil, parse_result.failure(err))
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
        }else if tok.type == .IDENTIFIER {
            _ = res.register(self.advance())
            return (res.success(VarAccessNode(token: tok)), res)
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
            _ = res.failure(InvalidSyntaxError(details: "Expected int, float, identifier, '+', '-', or '('", pos: p))
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
        let res = ParserResult()

        if self.curr_token.type == .IDENTIFIER {
            let next = self.tokens[self.token_idx + 1]
            
            if next.type == .EQ {    
                let var_name = self.curr_token
                _ = res.register(self.advance())
                _ = res.register(self.advance())
                let (val, result) = self.expr()
                _ = res.register(result)
                if res.error != nil {
                    return (nil, res)
                }else {
                    return (res.success(VarAssignNode(token: var_name, value_node: val!)), res)
                }
            }
        }

        return self.bin_op(func: comp_expr, ops: [TT_AND, TT_OR])
    }

    func comp_expr() -> (AbstractNode?, ParserResult) {
        let res = ParserResult()

        if self.curr_token.type_name == "NOT" || self.curr_token.type_name == "AND" {
            let op_tok = self.curr_token
            _ = res.register(self.advance())

            let (node, node_result) = self.comp_expr()
            _ = res.register(node_result)
            if let _ = res.error { return (nil, res) }

            return (UnaryOpNode(op_tok: op_tok, node: node!), res)
        }

        let (node, node_result) = self.bin_op(func: self.arith_expr, ops: [TT_EE, TT_NE, TT_LT, TT_GT, TT_LOE, TT_GOE])
        _ = res.register(node_result)
        if let err = res.error {
            _ = res.failure(err)
            return (nil, res) 
        }

        return (node, res)
    }

    func arith_expr() -> (AbstractNode?, ParserResult) {
        return self.bin_op(func: self.term, ops: [TT_PLUS, TT_MINUS])
    }

    func check_equal_to_ops(ops: [String], type_name: String) -> Bool {
        for op in ops {
            if type_name == op {
                return true 
            }
        }
        return false 
    }

    func bin_op(func function: () -> (AbstractNode?, ParserResult), ops: [String]) -> (AbstractNode?, ParserResult) {
        let res = ParserResult()

        var (left, parse_result) = function()
        _ = res.register(parse_result)
        if res.error != nil { return (nil, res) }
        
        var loop_condition = check_equal_to_ops(ops: ops, type_name: self.curr_token.type_name)

        while  loop_condition { //self.curr_token.type_name == ops[0] || self.curr_token.type_name == ops[1]
            let op_tok = VariableNode(token: self.curr_token)
            _ = res.register(self.advance())

            let (right, parse_result_) = function()
            _ = res.register(parse_result_)
            if res.error != nil { return (nil, res) }
            
            left = BinOpNode(lhs: left!, op: op_tok, rhs: right!)
            loop_condition = check_equal_to_ops(ops: ops, type_name: self.curr_token.type_name)
        }

        return (res.success(left ?? VariableNode()), res)
    }

    func bin_op(funcA functionA: () -> (AbstractNode?, ParserResult), ops: String, funcB functionB: () -> (AbstractNode?, ParserResult)) -> (AbstractNode?, ParserResult) {
        let res = ParserResult()

        var (left, parse_result) = functionA()
        _ = res.register(parse_result)
        if res.error != nil { return (nil, res) }

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