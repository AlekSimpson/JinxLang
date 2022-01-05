import tokens as tk  
from Error import InvalidSyntaxError 
from Node import NumberNode, VarAccessNode, VarAssignNode, VariableNode, IfNode, ForNode, WhileNode, FuncDefNode, CallNode, StringNode, BinOpNode, UnaryNode
from ParseResult import ParseResult
from tokens import Token 

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens 
        self.token_idx = 0
        self.curr_token = self.tokens[self.token_idx]

    def advance(self):
        self.token_idx += 1
        if self.token_idx < len(self.tokens):
            self.curr_token = self.tokens[self.token_idx]

    def parse(self): # returns Node, Error
        node_result, parse_result = self.expr()
        if parse_result.error != None:
            if self.curr_token.type != tk.TT_EOF:
                return (None, parse_result.failure(parse_result.error))
            return (None, parse_result.error)

        return (node_result, None)

    def call(self):
        res = ParseResult()
        atom, atom_res = self.atom()
        _ = res.register(atom_res)
        if res.error != None: return (None, res)
        
        if self.curr_token.type_name == tk.TT_LPAREN:
            _ = res.register(self.advance())
            arg_nodes = []
            
            if self.curr_token.type_name == tk.TT_RPAREN:
                _ = res.register(self.advance())
            else:
                expr, expr_res = self.expr()
                if expr_res.error != None: return (None, expr_res)
                arg_nodes.append(res.register(expr))
                if expr_res.error != None:
                    p = expr.token.pos
                    err = InvalidSyntaxError("Expected closing parenthese in function declaration", pos)
                    _ = res.failure(err)
                    return (None, res)
                
                while self.curr_token.type_name == tk.TT_COMMA:
                    _ = res.register(self.advance())

                    expr, expr_res = self.expr()
                    if expr_res.error != None: return (None, expr_res)
                    arg_nodes.append(res.register(expr))
                
                if self.curr_token.type_name != tk.TT_RPAREN:
                    pos = expr.token.pos 
                    err = InvalidSyntaxError("Expected closing parenthese in function declaration", pos)
                    _ = res.failure(err)
                    return (None, res)

                _ = res.register(self.advance())
            return (res.success(CallNode(atom, arg_nodes)), res)
        return (res.success(atom), res)

    def atom(self):
        res = ParseResult()
        tok = self.curr_token 
        returnVal = (None, res)
        
        if tok.type == tk.MT_FACTOR:
            val = NumberNode(self.curr_token)
            _ = res.register(self.advance())
            returnVal = (res.success(val), res)
        elif tok.type_name == tk.TT_ID:
            _ = res.register(self.advance())
            return (res.success(VarAccessNode(tok)), res)
        elif tok.type_name == tk.TT_STRING:
            _ = res.register(self.advance())
            return (res.success(StringNode(tok)), res)
        elif tok.type_name == "LPAREN":
            _ = res.register(self.advance())
            expr, err = self.expr()
            if expr != None:
                _ = res.register(expr)
                if self.curr_token.type_name == "RPAREN":
                    _ = res.register(self.advance())
                    returnVal = (res.success(expr), res)
                else: 
                    p = tok.pos 
                    _ = res.failure(InvalidSyntaxError("Expected ')'", p))
            if err != None:
                _ = res.register(err)
        elif tok.type_name == "IF":
            if_expr, expr_res = self.if_expr()
            _ = res.register(expr_res)
            if res.error != None:
                _ = res.failure(res.error)
            else:
                returnVal = (if_expr, res)
        elif tok.type_name == "FOR":
            for_expr, expr_res = self.for_expr()
            _ = res.register(expr_res)
            if res.error != None:
                _ = res.failure(res.error)
            else:
                returnVal = (for_expr, res)
        elif tok.type_name == "WHILE":
            while_expr, expr_res = self.while_expr()
            _ = res.register(expr_res)
            if res.error != None:
                _ = res.failure(res.error)
            else:
                returnVal = (while_expr, res)
        elif tok.type_name == "FUNC":
            func_def, func_res = self.func_def()
            _ = res.register(func_res)
            if res.error != None:
                _ = res.failure(res.error)
            else:
                returnVal = (func_def, res)
        else:
            p = tok.pos 
            _ = res.failure(InvalidSyntaxError("Expected, int, float, identifier, '+', '-', or '('", p))
        return returnVal 

    def func_def(self):
        res = ParseResult()

        if not (self.curr_token.type_name == "FUNC"):
            p = self.curr_token.pos 
            _ = res.failure(InvalidSyntaxError("Expected 'method' keyword in function declaration", p))
            return (None, res)

        _ = res.register(self.advance())

        name_token = Token()
        if self.curr_token.type_name == tk.TT_ID:
            name_token = self.curr_token 
            _ = res.register(self.advance())
        
        if not (self.curr_token.type_name == tk.TT_LPAREN):
            p = self.curr_token.pos 
            _ = res.failure(InvalidSyntaxError("Expected '(' in function defintion", p))
            return (None, res)

        _ = res.register(self.advance())
        arg_name_tokens = []

        if self.curr_token.type_name == tk.TT_ID:
            arg_name_tokens.append(self.curr_token)
            _ = res.register(self.advance())

            while self.curr_token.type_name == tk.TT_COMMA:
                _ = res.register(self.advance())

                if self.curr_token.type_name != tk.TT_ID:
                    p = self.curr_token.pos 
                    _ = res.failure(InvalidSyntaxError("Expected identifier after comma in function definition", p))
                    return (None, res)
                
                arg_name_tokens.append(self.curr_token)
                _ = res.register(self.advance())

            if not (self.curr_token.type_name == tk.TT_RPAREN):
                p = self.curr_token.pos 
                _ = res.failure(InvalidSyntaxError("Expected ')' in function defintion", p))
                return (None, res)
        else:
            if not (self.curr_token.type_name == tk.TT_RPAREN):
                p = self.curr_token.pos 
                _ = res.failure(InvalidSyntaxError("Expected identifier or ')' in function definition", p))
                return (None, res)
        
        _ = res.register(self.advance())

        if self.curr_token.type_name != tk.TT_ARROW:
            p = self.curr_token.pos 
            _ = res.failure(InvalidSyntaxError("Expected '->' in function definition", p))
            return (None, res)
        
        _ = res.register(self.advance())
        
        node_to_return, return_res = self.expr()
        _ = res.register(return_res)
        if res.error != None: return (None, res)
        
        return (res.success(FuncDefNode(node_to_return, name_token, arg_name_tokens)), res)

    def for_expr(self):
        res = ParseResult()

        if not (self.curr_token.type_name == "FOR"):
            p = self.curr_token.pos 
            _ = res.failure(InvalidSyntaxError("Expected 'for'", p))
            return (None, res)
        
        _ = res.register(self.advance())
        
        if not (self.curr_token.type_name == "IDENTIFIER"):
            p = self.curr_token.pos 
            _ = res.failure(InvalidSyntaxError("Expected variable", p))
            return (None, res)

        iterator_token = self.curr_token
        _ = res.register(self.advance())
        
        if not (self.curr_token.type_name == "IN"):
            p = self.curr_token.pos
            _ = res.failure(InvalidSyntaxError("Expected 'in' keyword", p))
            return (None, res)

        _ = res.register(self.advance())

        start_value, start_res = self.expr()
        _ = res.register(start_res)
        if res.error != None: return (None, res)

        iterator_var = VarAssignNode(iterator_token, start_value)
        
        if not (self.curr_token.type_name == "COLON"):
            p = self.curr_token.pos 
            _ = res.failure(InvalidSyntaxError("Expected ':' in range", p))
            return (None, res)

        _ = res.register(self.advance())

        end_value, end_res = self.expr()
        _ = res.register(end_res)
        if res.error != None: return (None, res)
        
        if not (self.curr_token.type_name == "LCURLY"):
            p = self.curr_token.pos 
            _ = res.failure(InvalidSyntaxError("Expected '{' in for loop", p))
            return (None, res)

        _ = res.register(self.advance())
        
        body, body_res = self.expr()
        _ = res.register(body_res)
        if res.error != None: return (None, res)
        
        if not (self.curr_token.type_name == "RCURLY"):
            p = self.curr_token.pos 
            _ = res.failure(InvalidSyntaxError("Expected '}' in for loop", p))
            return (None, res)
        
        return (res.success(ForNode(iterator_var, start_value, end_value, body)), res)

    def while_expr(self):
        res = ParseResult()

        if not (self.curr_token.type_name == "WHILE"):
            p = self.curr_token.pos 
            _ = res.failure(InvalidSyntaxError("Expected 'while' keyword in while loop", p))
            return (None, res)

        _ = res.register(self.advance())

        cond_value, cond_res = self.expr()
        _ = res.register(cond_res)
        if res.error != None: return (None, res)

        if not (self.curr_token.type_name == "LCURLY"):
            p = self.curr_token.pos 
            _ = res.failure(InvalidSyntaxError("Expected '{' in while loop", p))
            return (None, res)

        _ = res.register(self.advance())

        body_value, body_res = self.expr()
        _ = res.register(body_res)
        if res.error != None: return (None, res)

        if not (self.curr_token.type_name == "RCURLY"):
            p = self.curr_token.pos 
            _ = res.failure(InvalidSyntaxError("Expected '}' in while loop"), p)
            return (None, res)
        
        return (res.success(WhileNode(cond_value, body_value)), res)

    def if_expr(self):
        res = ParseResult()
        cases = []
        else_case = None 

        if not (self.curr_token.type_name == "IF"):
            p = self.curr_token.pos 
            _ = res.failure(InvalidSyntaxError("Expected 'if'", p))
            return (None, res)

        _ = res.register(self.advance())
        
        condition, cond_result = self.expr()
        _ = res.register(cond_result)
        if res.error != None: return (None, res)
        
        if not (self.curr_token.type_name == "LCURLY"):
            p = self.curr_token.pos 
            _ = res.register(InvalidSyntaxError("Expected '{'", p))
            return (None, res)
        
        _ = res.register(self.advance())
        
        expression, expr_res = self.expr()
        _ = res.register(expr_res)
        if res.error != None: return (None, res)
        
        new_element = [condition, expression]
        cases.append(new_element)
        
        if not (self.curr_token.type_name == "RCURLY"):
            p = self.curr_token.pos 
            _ = res.failure(InvalidSyntaxError("Expected '}'", p))
            return (None, res)

        _ = res.register(self.advance())

        while self.curr_token.type_name == "ELSE IF":
            _ = res.register(self.advance())

            cond, result = self.expr()
            _ = res.register(result)
            if res.error != None: return (None, res)

            if not (self.curr_token.type_name == "LCURLY"):
                p = self.curr_token.pos 
                _ = res.failure(InvalidSyntaxError("Expected '{'", p))
                return (None, res)

            _ = res.register(self.advance())

            exp, exp_result = self.expr()
            _ = res.register(exp_result)
            if res.error != None: return (None, res)

            new_element = [cond, exp]
            cases.append(new_element)

            if not (self.curr_token.type_name == "RCURLY"):
                p = self.curr_token.pos 
                _ = res.failure(InvalidSyntaxError("Expected '}'", p))
                return (None, res)

        if self.curr_token.type_name == "ELSE":
            _ = res.register(self.advance())

            if not (self.curr_token.type_name == "LCURLY"):
                p = self.curr_token.pos 
                _ = res.failure(InvalidSyntaxError("Expected '{'", p))
                return (None, res)

            _ = res.register(self.advance())

            e, e_result = self.expr()
            _ = res.register(e_result)
            if res.error != None: return (None, res)
    
            else_case = e 

            if not (self.curr_token.type_name == "RCURLY"):
                p = self.curr_token.pos 
                _ = res.failure(InvalidSyntaxError("Expected '}'", p))
                return (None, res)
        return (res.success(IfNode(cases, else_case)), res)

    def power(self):
        return self.bin_op(self.call, [tk.TT_POW], self.factor)

    def factor(self):
        res = ParseResult()
        tok = self.curr_token
        returnVal = (None, res)

        if tok.type_name == "PLUS" or tok.type_name == "MINUS":
            _ = res.register(self.advance())
            fac_node, fac_res = self.factor()
            
            if fac_node != None:
                _ = res.register(self.factor())
                returnVal = (res.success(UnaryNode(tok, fac_node)), res)
            
            if fac_res.error != None: 
                _ = res.failure(err)
                returnVal = (None, res)
        else:
            returnVal = self.power()
        return returnVal 

    def term(self):
        return self.bin_op(self.factor, [tk.TT_MUL, tk.TT_DIV])

    def expr(self):
        res = ParseResult()
        
        if self.curr_token.type_name == tk.TT_ID:
            next = self.token_idx + 1 if (self.token_idx + 1) <= (len(self.tokens) - 1) else self.token_idx
            next_tok = self.tokens[next]
            
            if next_tok.type_name == tk.TT_EQ:
                var_name = self.curr_token 
                
                _ = res.register(self.advance())
                _ = res.register(self.advance())     
                
                val, result = self.expr()
                _ = res.register(result)
                
                if res.error != None:
                    return (None, res)
                else: 
                    return (res.success(VarAssignNode(var_name, val)), res)
        
        return self.bin_op(self.comp_expr, [tk.TT_AND, tk.TT_OR])

    def comp_expr(self):
        res = ParseResult()

        if self.curr_token.type_name == "NOT" or self.curr_token.type_name == "AND":
            op_tok = self.curr_token
            _ = res.register(self.advance())

            node, node_result = self.comp_expr()
            _ = res.register(node_result)
            if res.error != None: return (None, res)

            return (UnaryOpNode(op_tok, node), res)

        node, node_result = self.bin_op(self.arith_expr, [tk.TT_EE, tk.TT_NE, tk.TT_LT, tk.TT_GT, tk.TT_LOE, tk.TT_GOE])
        _ = res.register(node_result)
        if res.error != None:
            _ = res.failure(res.error)
            return (None, res)
        return (node, res)

    def arith_expr(self):
        return self.bin_op(self.term, [tk.TT_PLUS, tk.TT_MINUS])

    def check_equal_to_ops(self, ops, type_name):
        for op in ops:
            if type_name == op:
                return True 

        return False 

    def bin_op(self, functionA, ops, functionB=None):
        res = ParseResult()

        func = functionB
        if functionB == None:
            func = functionA

        left, parse_result = functionA()
        _ = res.register(parse_result)
        if res.error != None: return (None, res)
        
        loop_condition = self.check_equal_to_ops(ops, self.curr_token.type_name)
        while loop_condition:
            op_tok = VariableNode(self.curr_token)
            _ = res.register(self.advance())

            right, parse_result_ = func()
            _ = res.register(parse_result_)
            if res.error != None: return (None, res)

            left = BinOpNode(left, op_tok, right)
            loop_condition = self.check_equal_to_ops(ops, self.curr_token.type_name)

        return (res.success(left), res)
