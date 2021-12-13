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

    func call() -> (AbstractNode?, ParserResult) {
        let res = ParserResult()

        let (atom, atom_res) = self.atom()
        _ = res.register(atom_res)
        if res.error != nil { return (nil, res) }
        
        if self.curr_token.type_name == TT_LPAREN {
            _ = res.register(self.advance())
            
            var arg_nodes:[AbstractNode] = []

            if self.curr_token.type_name == TT_RPAREN {
                _ = res.register(self.advance())
            }else {
                let (expr, expr_res) = self.expr()
                if expr_res.error != nil { return (nil, expr_res) }
                arg_nodes.append(res.register(expr!))
                if expr_res.error != nil {
                    var p = Position()
                    if let unwrapped = expr!.token.pos { p = unwrapped }
                    let err = InvalidSyntaxError(details: "Expected closing parenthese in function declaration", pos: p) 
                    _ = res.failure(err)
                    return (nil, res)
                }

                while self.curr_token.type_name == TT_COMMA {
                    _ = res.register(self.advance())

                    let (expr, expr_res) = self.expr()
                    if expr_res.error != nil { return (nil, expr_res) }
                    arg_nodes.append(res.register(expr!))
                }

                if self.curr_token.type_name != TT_RPAREN {
                    var p = Position()
                    if let unwrapped = expr!.token.pos { p = unwrapped }
                    let err = InvalidSyntaxError(details: "Expected closing parenthese in function declaration", pos: p) 
                    _ = res.failure(err)
                    return (nil, res)
                }

                _ = res.register(self.advance())
            }
            return (res.success(CallNode(node_to_call: atom!, arg_nodes: arg_nodes)), res)
        }
        
        return (res.success(atom!), res)
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
        }else if tok.type_name == TT_STRING {
            _ = res.register(self.advance())
            return (res.success(StringNode(token: tok)), res)
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
                }
            }

            if let err = recurrsion.1.error {
                _ = res.failure(err)
            }
        }else if tok.type_name == "IF" {
            var (if_expr, expr_res) = self.if_expr()
            _ = res.register(expr_res)
            if let err = res.error {
                _ = res.failure(err)
            }else {
                if let unwrapped = if_expr { if_expr = unwrapped }
                returnVal = (if_expr, res)
            }
        }else if tok.type_name == "FOR" {
            var (for_expr, expr_res) = self.for_expr()
            _ = res.register(expr_res)
            if let err = res.error {
                _ = res.failure(err)
            }else {
                if let unwrapped = for_expr { for_expr = unwrapped }
                returnVal = (for_expr, res)
            }
        }else if tok.type_name == "WHILE" {
            var (while_expr, expr_res) = self.while_expr()
            _ = res.register(expr_res)
            if let err = res.error {
                _ = res.failure(err)
            }else {
                if let unwrapped = while_expr { while_expr = unwrapped }
                returnVal = (while_expr, res)
            }
        }else if tok.type_name == "FUNC" {
            var (func_def, func_res) = self.func_def()
            _ = res.register(func_res)
            if let err = res.error {
                _ = res.failure(err)
            }else {
                if let unwrapped = func_def { func_def = unwrapped }
                returnVal = (func_def, res)
            }
        }
        else {
            var p = Position()
            if let position = tok.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected int, float, identifier, '+', '-', or '('", pos: p))
        }

        return returnVal
    }

    func func_def() -> (AbstractNode?, ParserResult) {
        let res = ParserResult()

        if !(self.curr_token.type_name == "FUNC") {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected 'method' keyword in function definition", pos: p))
            return (nil, res)
        }

        _ = res.register(self.advance())

        var name_token = Token()
        if self.curr_token.type_name == TT_ID { 
            name_token = self.curr_token 
            _ = res.register(self.advance())
        }

        if !(self.curr_token.type_name == TT_LPAREN) {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected '(' in function definition", pos: p))
            return (nil, res)
        }

        _ = res.register(self.advance())
        var arg_name_tokens: [Token] = []

        if self.curr_token.type_name == TT_ID {
            arg_name_tokens.append(self.curr_token)
            _ = res.register(self.advance())

            while self.curr_token.type_name == TT_COMMA {
                _ = res.register(self.advance())

                if self.curr_token.type_name != TT_ID {
                    var p = Position()
                    if let position = self.curr_token.pos { p = position }
                    _ = res.failure(InvalidSyntaxError(details: "Expected identifier after comma in function definition", pos: p))
                    return (nil, res)
                }

                arg_name_tokens.append(self.curr_token)
                _ = res.register(self.advance())
            }

            if !(self.curr_token.type_name == TT_RPAREN) {
                var p = Position()
                if let position = self.curr_token.pos { p = position }
                _ = res.failure(InvalidSyntaxError(details: "Expected ')' in function defintion", pos: p))
                return (nil, res)
            }
        }else {
            if !(self.curr_token.type_name == TT_RPAREN) {
                var p = Position()
                if let position = self.curr_token.pos { p = position }
                _ = res.failure(InvalidSyntaxError(details: "Expected identifier or ')' in function defintion", pos: p))
                return (nil, res)
            }
        }

        _ = res.register(self.advance())

        if self.curr_token.type_name != TT_ARROW {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected '->' in function defintion", pos: p))
            return (nil, res)
        }

        _ = res.register(self.advance())

        let (node_to_return, return_res) = self.expr()
        _ = res.register(return_res)
        if res.error != nil { return (nil, res) }

        return (res.success(FuncDefNode(token: name_token, arg_name_tokens: arg_name_tokens, body_node: node_to_return!)), res)
    }

    func for_expr() -> (AbstractNode?, ParserResult) {
        let res = ParserResult()

        if !(self.curr_token.type_name == "FOR") {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected 'for'", pos: p))
            return (nil, res)
        }

        _ = res.register(self.advance())

        if !(self.curr_token.type_name == "IDENTIFIER") {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected variable", pos: p))
            return (nil, res)
        }

        let iterator_token = self.curr_token
        _ = res.register(self.advance())

        if !(self.curr_token.type_name == "IN") {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected 'in' keyword", pos: p))
            return (nil, res)
        }

        _ = res.register(self.advance())

        let (start_value, start_res) = self.expr()
        _ = res.register(start_res)
        if res.error != nil { return (nil, res) }

        let iterator_var = VarAssignNode(token: iterator_token, value_node: start_value as! NumberNode)

        if !(self.curr_token.type_name == "INDICATOR") {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected ':' in range", pos: p))
            return (nil, res)
        }

        _ = res.register(self.advance())

        let (end_value, end_res) = self.expr()
        _ = res.register(end_res)
        if res.error != nil { return (nil, res) }

        if !(self.curr_token.type_name == "LCURLY") {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected '{' in for loop", pos: p))
            return (nil, res)
        }

        _ = res.register(self.advance())

        let (body, body_res) = self.expr()
        _ = res.register(body_res)
        if res.error != nil { return (nil, res) }

        if !(self.curr_token.type_name == "RCURLY") {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected '}' in for loop", pos: p))
            return (nil, res)
        }
        
        return (res.success(ForNode(iterator: iterator_var, startValue: start_value as! NumberNode, endValue: end_value as! NumberNode, bodyNode: body!)), res)
    }

    func while_expr() -> (AbstractNode?, ParserResult) {
        let res = ParserResult()

        if !(self.curr_token.type_name == "WHILE") {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected 'while' keyword in while loop", pos: p))
            return (nil, res)
        }

        _ = res.register(self.advance())

        let (cond_value, cond_res) = self.expr()
        _ = res.register(cond_res)
        if res.error != nil { return (nil, res) }

        if !(self.curr_token.type_name == "LCURLY") {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected '{' in for loop", pos: p))
            return (nil, res)
        }

        _ = res.register(self.advance())

        let (body_value, body_res) = self.expr()
        _ = res.register(body_res)
        if res.error != nil { return (nil, res) }

        if !(self.curr_token.type_name == "RCURLY") {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected '}' in for loop", pos: p))
            return (nil, res)
        }

        return (res.success(WhileNode(conditionNode: cond_value!, bodyNode: body_value!)), res)
    }

    func if_expr() -> (AbstractNode?, ParserResult) {
        let res = ParserResult()
        var cases:[[AbstractNode]] = []
        var else_case:AbstractNode? = nil 

        if !(self.curr_token.type_name == "IF") {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected 'if'", pos: p))
            return (nil, res)
        }

        _ = res.register(self.advance())

        let (condition, cond_result) = self.expr()
        _ = res.register(cond_result)
        if res.error != nil { return (nil, res) }

        if !(self.curr_token.type_name == "LCURLY") {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected '{'", pos: p))
            return (nil, res)
        }

        _ = res.register(self.advance())

        let (expression, expr_result) = self.expr()
        _ = res.register(expr_result)
        if res.error != nil { return (nil, res) }

        let new_element: [AbstractNode] = [condition!, expression!]
        cases.append(new_element)

        if !(self.curr_token.type_name == "RCURLY") {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected '}'", pos: p))
            return (nil, res)
        }

        _ = res.register(self.advance())
        
        while self.curr_token.type_name == "ELSE IF" {
            _ = res.register(self.advance())

            let (cond, result) = self.expr()
            _ = res.register(result)
            if res.error != nil { return (nil, res) }

            if !(self.curr_token.type_name == "LCURLY") {
                var p = Position()
                if let position = self.curr_token.pos { p = position }
                _ = res.failure(InvalidSyntaxError(details: "Expected '{'", pos: p))
                return (nil, res)
            }

            _ = res.register(self.advance())

            let (exp, exp_result) = self.expr()
            _ = res.register(exp_result)
            if res.error != nil { return (nil, res) }

            let new_element:[AbstractNode] = [cond!, exp!]
            cases.append(new_element)

            if !(self.curr_token.type_name == "RCURLY") {
                var p = Position()
                if let position = self.curr_token.pos { p = position }
                _ = res.failure(InvalidSyntaxError(details: "Expected '}'", pos: p))
                return (nil, res)
            }
        }

        if self.curr_token.type_name == "ELSE" {
            _ = res.register(self.advance())

            if !(self.curr_token.type_name == "LCURLY") {
                var p = Position()
                if let position = self.curr_token.pos { p = position }
                _ = res.failure(InvalidSyntaxError(details: "Expected '{'", pos: p))
                return (nil, res)
            }

            _ = res.register(self.advance())

            let (e, e_result) = self.expr()
            _ = res.register(e_result)
            if res.error != nil { return (nil, res) }

            else_case = e

            if !(self.curr_token.type_name == "RCURLY") {
                var p = Position()
                if let position = self.curr_token.pos { p = position }
                _ = res.failure(InvalidSyntaxError(details: "Expected '}'", pos: p))
                return (nil, res)
            }
        }

        return (res.success(IfNode(cases: cases, else_case: else_case)), res)
    }

    func power() -> (AbstractNode?, ParserResult) {
        // return bin_op(funcA: atom, ops: TT_POW, funcB: factor)
        return bin_op(funcA: call, ops: TT_POW, funcB: factor)
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

