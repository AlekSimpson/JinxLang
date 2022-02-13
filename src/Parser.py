import tokens as tk
from Types import Integer
from Error import InvalidSyntaxError
from Node import *
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

    def reverse(self, amount=1):
        self.token_idx -= amount
        self.update_current_token()
        return self.curr_token

    def update_current_token(self):
        if self.token_idx >= 0 and self.token_idx < len(self.tokens):
            self.curr_token = self.tokens[self.token_idx]

    def throw_error(self, res, msg, token=None):
        pos = self.curr_token if token is None else token.pos
        return res.failure(InvalidSyntaxError(msg, pos))

    def parse(self):
        AST = self.statements()

        return AST

    def call(self):
        res = ParseResult()

        atom = self.atom()
        if isinstance(atom, ParseResult):
            res.register(atom)
            return res.failure(atom.error)

        if self.curr_token.type_name == tk.TT_LPAREN:
            res.register(self.advance())
            arg_nodes = []

            if self.curr_token.type_name == tk.TT_RPAREN:
                res.register(self.advance())
            else:
                expr = self.expr()
                if isinstance(expr, ParseResult):
                    return self.throw_error(res, "Expected closing parenthese in function declaration", expr.token)
                arg_nodes.append(res.register(expr))

                while self.curr_token.type_name == tk.TT_COMMA:
                    res.register(self.advance())

                    expr = self.expr()
                    if isinstance(expr, ParseResult):
                        return self.throw_error(res, expr.token, expr.error.details)
                    arg_nodes.append(res.register(expr))

                if self.curr_token.type_name != tk.TT_RPAREN:
                    return self.throw_error(res, "Expected closing parenthese in function declaration", expr.token)

                res.register(self.advance())

            return res.success(CallNode(atom, arg_nodes))
        elif self.curr_token.type_name == tk.TT_LBRACKET:
            res.register(self.advance())

            if (self.curr_token.type_name != tk.TT_INT and self.curr_token.type_name != tk.TT_ID):
                return self.throw_error(res, "Array index must be an integer")

            index = self.atom()
            if isinstance(index, ParseResult):
                return self.throw_error(res, index.error.details)

            if self.curr_token.type_name != tk.TT_RBRACKET:
                return self.throw_error(res, "Array subscripts must have a closing bracket")

            res.register(self.advance())
            if self.curr_token.type_name == tk.TT_EQ:
                res.register(self.advance())

                # BUG: Probably should make it so that this is not the case, arrays should be able to hold any theoretical value
                if (not self.curr_token.type_name != tk.TT_INT and not self.curr_token.type_name != tk.TT_STRING):
                    return self.throw_error(res, "Array can only hold value types of int or string")

                new_val = self.atom()
                if isinstance(new_val, ParseResult):
                    return self.throw_error(res, new_val.error.details)

                res.register(self.advance())

                return res.success(ArraySetNode(atom, index, new_val))
            return res.success(ArrayGetNode(atom, index))
        return res.success(atom)

    def atom(self):
        res = ParseResult()
        tok = self.curr_token

        if tok.type_name == tk.TT_INT:
            val = NumberNode(self.curr_token)
            res.register(self.advance())
            return res.success(val)

        elif tok.type_name == tk.TT_ID:
            res.register(self.advance())
            return res.success(VarAccessNode(tok))

        elif tok.type_name == tk.TT_STRING:
            res.register(self.advance())
            return res.success(StringNode(tok))

        elif tok.type_name == "LPAREN":
            res.register(self.advance())
            expr = self.expr()
            if expr is not None:
                res.register(expr)
                if self.curr_token.type_name == "RPAREN":
                    res.register(self.advance())
                    return res.success(expr)
                else:
                    return self.throw_error(res, "Expected ')'", tok.pos)

            if isinstance(expr, ParseResult):
                return self.throw_error(res, expr.error.details)

        elif tok.type_name == tk.TT_LBRACKET:
            list_expr = res.register(self.list_expr())
            if isinstance(list_expr, ParseResult):
                res.register(list_expr)
                return self.throw_error(res, res.error.details)
            return res.success(list_expr)

        elif tok.type_name == "IF":
            if_expr = self.if_expr()
            if isinstance(if_expr, ParseResult):
                res.register(expr)
                return self.throw_error(res, res.error.details)
            return res.success(if_expr)

        elif tok.type_name == "FOR":
            for_expr = self.for_expr()
            if isinstance(for_expr, ParseResult):
                res.register(expr)
                return self.throw_error(res, res.error.details)
            return res.success(for_expr)

        elif tok.type_name == "WHILE":
            while_expr = self.while_expr()
            if isinstance(while_expr, ParseResult):
                res.register(expr)
                return self.throw_error(res, res.error.details)
            return res.success(while_expr)

        elif tok.type_name == "FUNC":
            func_def = self.func_def()
            if isinstance(func_def, ParseResult):
                res.register(func_def)
                return self.throw_error(res, res.error.details)
            return res.success(func_def)

    def list_expr(self):
        res = ParseResult()
        element_nodes = []

        if self.curr_token.type_name != tk.TT_LBRACKET:
            return self.throw_error(res, "Expected '[' in list")

        res.register(self.advance())

        if self.curr_token.type_name == tk.TT_RBRACKET:
            res.register(self.advance())
        else:
            expr = self.expr()
            if isinstance(expr, ParseResult):
                return self.throw_error(res, expr.error.details)

            element_nodes.append(res.register(expr))
            #if expr_res.error is not None:
            #    err = self.throw_error(res, "Expected closing bracket in list declaration")
            #    return (None, err)

            while self.curr_token.type_name == tk.TT_COMMA:
                res.register(self.advance())

                expr = self.expr()
                if isinstance(expr, ParseResult):
                    return self.throw_error(res, expr.error.details)
                element_nodes.append(res.register(expr))

            if self.curr_token.type_name != tk.TT_RBRACKET:
                return self.throw_error(res, "Expected closing bracket in list declaration")

            res.register(self.advance())
        return res.success(ListNode(element_nodes))

    def func_def(self):
        res = ParseResult()

        if not (self.curr_token.type_name == "FUNC"):
            return self.throw_error(res, "Expected 'method' keyword in function declaration")

        res.register(self.advance())

        name_token = Token()
        if self.curr_token.type_name == tk.TT_ID:
            name_token = self.curr_token
            res.register(self.advance())

        if not (self.curr_token.type_name == tk.TT_LPAREN):
            return self.throw_error(res, "Expected '(' in function defintion")

        res.register(self.advance())
        arg_name_tokens = []
        arg_type_tokens = []

        if self.curr_token.type_name == tk.TT_ID:
            look_for_args = True
            while look_for_args:
                if self.curr_token.type_name != tk.TT_ID:
                    err = self.throw_error(res, "Expected value after comma in function defintion")
                    return res.failure(err)

                arg_name_tokens.append(self.curr_token)
                res.register(self.advance())

                if self.curr_token.type_name != tk.TT_COLON:
                    err = self.throw_error(res, f"Expected ':' in argument type declaration in function {name_token.value}")
                    return res.failure(err)
                res.register(self.advance())

                if self.curr_token.type_dec is None:
                    err = self.throw_error(res, f"Expected argument {arg_name_tokens[-1].value} to have a tyhpe declaration in function {name_token.value}")
                    return res.failure(err)

                arg_type_tokens.append(self.curr_token)
                res.register(self.advance())

                look_for_args = self.curr_token.type_name == tk.TT_COMMA
                if not look_for_args:
                    break
                res.register(self.advance())

            if not (self.curr_token.type_name == tk.TT_RPAREN):
                err = self.throw_error(res, "Expected ')' in function defintion")
                return res.failure(err)
        else:
            # BUG The check for RPAREN could probably just be moved into one check if statement instead of having one in an else
            if not (self.curr_token.type_name == tk.TT_RPAREN):
                err = self.throw_error(res, "Expected value or ')' in function definition")
                return res.failure(err)

        res.register(self.advance())

        if self.curr_token.type_name != tk.TT_COLON:
            err = self.throw_error(res, "Expected ':' in function defintion")
            return res.failure(err)

        res.register(self.advance())

        if self.curr_token.type_dec is None:
            err = self.throw_error(res, "Expected return type in function declaration")
            return res.failure(err)

        returnType = self.curr_token

        res.register(self.advance())

        if self.curr_token.type_name == tk.TT_ARROW:
            res.register(self.advance())

            node_to_return = self.expr()
            if isinstance(node_to_return, ParseResult):
                res.register(node_to_return)
                err = self.throw_error(res, res.error.details)
                return res.failure(err)

            return res.success(FuncDefNode(node_to_return, returnType, name_token, arg_name_tokens, arg_type_tokens, False))

        if self.curr_token.type_name != "LCURLY":
            err = self.throw_error(res, "Expected '{'")
            return res.failure(err)

        res.register(self.advance())

        if self.curr_token.type_name != tk.TT_NEWLINE:
            err = self.throw_error(res, "Expected '->' in function or '{'")
            return res.failure(err)

        res.register(self.advance())

        body = self.statements()
        if isinstance(body, ParseResult):
            res.register(body)
            err = self.throw_error(res, res.error.details)
            return res.failure(err)

        return_nil = True
        for node in body.element_nodes:
            if node.classType == 15:
                return_nil = False
                break

        if self.curr_token.type_name != "RCURLY":
            err = self.throw_error(res, "Expected '}'")
            return res.failure(err)

        res.register(self.advance())
        returnVal = res.success(FuncDefNode(body, returnType, name_token, arg_name_tokens, arg_type_tokens, return_nil))
        return returnVal

    def for_expr(self):
        res = ParseResult()

        if not (self.curr_token.type_name == "FOR"):
            err = self.throw_error(res, "Expected 'for'")
            return res.failure(err)

        res.register(self.advance())

        if not (self.curr_token.type_name == "IDENTIFIER"):
            err = self.throw_error(res, "Expected variable")
            return res.failure(err)

        iterator_token = self.curr_token
        res.register(self.advance())

        if not (self.curr_token.type_name == "IN"):
            err = self.throw_error(res, "Expected 'in' keyword")
            return res.failure(err)

        res.register(self.advance())

        start_value = self.expr()
        if isinstance(start_value, ParseResult):
            res.register(start_value)
            err = self.throw_error(res, res.error.details)
            return res.failure(err)

        iterator_var = VarAssignNode(iterator_token, start_value, [1, Integer(64)])

        if not (self.curr_token.type_name == "COLON"):
            err = self.throw_error(res, "Expected ':' in range")
            return res.failure(err)

        res.register(self.advance())

        end_value = self.expr()
        if isinstance(end_value, ParseResult):
            res.register(end_value)
            err = self.throw_error(res, res.error.details)
            return res.failure(err)

        if not (self.curr_token.type_name == "LCURLY"):
            err = self.throw_error(res, "Expected '{' in for loop")
            return res.failure(err)

        res.register(self.advance())

        if self.curr_token.type_name == tk.TT_NEWLINE:
            res.register(self.advance())

            body = res.register(self.statements())
            if isinstance(body, ParseResult):
                res.register(body)
                return res.failure(body.error)

            if self.curr_token.type_name != "RCURLY":
                err = self.throw_error(res, "Expected '}'")
                return res.failure(err)

            res.register(self.advance())

            return res.success(ForNode(iterator_var, start_value, end_value, body, True))

        body = self.expr()
        if isinstance(body, ParseResult):
            res.register(body)
            return res.failure(body.error)

        if not (self.curr_token.type_name == "RCURLY"):
            err = self.throw_error(res, "Expected '}' in for loop")
            return res.failure(err)

        return res.success(ForNode(iterator_var, start_value, end_value, body, False))

    def while_expr(self):
        res = ParseResult()

        if not (self.curr_token.type_name == "WHILE"):
            err = self.throw_error(res, "Expected 'while' keyword in while loop")
            return res.failure(err)

        res.register(self.advance())

        cond_value = self.expr()
        if isinstance(cond_value, ParseResult):
            res.register(cond_value)
            return res.failure(cond_value.error)

        if not (self.curr_token.type_name == "LCURLY"):
            err = self.throw_error(res, "Expected '{' in while loop")
            return res.failure(err)

        res.register(self.advance())

        if self.curr_token.type_name == tk.TT_NEWLINE:
            res.register(self.advance())

            body = res.register(self.statements())
            if isinstance(body, ParseResult):
                return res.failure(body.error)

            if self.curr_token.type_name != "RCURLY":
                err = self.throw_error(res, "Expected '}'")
                return res.failure(err)

            res.register(self.advance())

            return res.success(WhileNode(cond_value, body, True))

        body_value = self.expr()
        if isinstance(body_value, ParseResult):
            res.register(body_value)
            return res.failure(body_value.error)

        if not (self.curr_token.type_name == "RCURLY"):
            err = self.throw_error(res, "Expected '}' in while loop")
            return res.failure(err)

        return res.success(WhileNode(cond_value, body_value, False))

    def if_expr(self):
        res = ParseResult()
        all_cases = self.if_expr_cases("IF")
        if isinstance(all_cases, ParseResult):
            res.register(all_cases)
            return res.failure(all_cases.error)
        cases, else_case = all_cases

        return res.success(IfNode(cases, else_case))

    def if_expr_cases(self, case_keyword):
        res = ParseResult()
        cases = []
        else_case = None

        if self.curr_token.type_name != case_keyword:
            err = self.throw_error(res, "Expected 'if'")
            return res.failure(err)

        res.register(self.advance())

        condition = self.expr()
        if isinstance(condition, ParseResult):
            res.register(condition)
            return res.failure(condition.error)

        if self.curr_token.type_name != "LCURLY":
            err = self.throw_error(res, "Expected '{'")
            return res.failure(err)

        res.register(self.advance())

        if self.curr_token.type_name == tk.TT_NEWLINE:
            res.register(self.advance())

            all_statements = self.statements()
            if isinstance(all_statements, ParseResult):
                res.register(all_statements)
                return res.failure(all_statements.error)
            statements = all_statements
            cases.append([condition, statements, True])

            if self.curr_token.type_name != "RCURLY":
                err = self.throw_error(res, "Expected '}'")
                return res.failure(err)
            res.register(self.advance())

            all_cases = self.if_expr_b_or_c()
            if isinstance(all_cases, ParseResult):
                res.register(all_cases)
                return res.failure(all_cases.error)

            new_cases, else_case = all_cases
            if len(new_cases) != 0:
                cases.extend(new_cases)
        else:
            expr = self.expr()
            if isinstance(expr, ParseResult):
                res.register(expr)
                return res.failure(expr.error)
            cases.append([condition, expr, False])

            if self.curr_token.type_name != "RCURLY":
                err = self.throw_error(res, "Expected '}'")
                return res.failure(err)
            res.register(self.advance())

            all_cases = self.if_expr_b_or_c()
            if isinstance(all_cases, ParseResult):
                res.register(all_cases)
                return res.failure(res)
            new_cases, else_case = all_cases
            if len(new_cases) != 0:
                cases.extend(new_cases)

        return [cases, else_case]

    def if_expr_c(self):
        res = ParseResult()
        else_case = None

        if self.curr_token.type_name == "ELSE":
            res.register(self.advance())

            if self.curr_token.type_name != "LCURLY":
                err = self.throw_error(res, "Expected '{'in else statement")
                return res.failure(err)

            res.register(self.advance())

            if self.curr_token.type_name == tk.TT_NEWLINE:
                res.register(self.advance())

                statements = self.statements()
                if isinstance(statements, ParseResult):
                    res.register(statements)
                    return res.failure(statements.error)
                else_case = [statements, True]

                if self.curr_token.type_name == "RCURLY":
                    res.register(self.advance())
                else:
                    err = self.throw_error(res, "Expected '}' in if statement")
                    return res.failure(err)
            else:
                expr = self.expr()
                if isinstance(expr, ParseResult):
                    res.register(expr)
                    return res.failure(expr.error)

                else_case = [expr, False]
        res.success(else_case)

        return else_case

    def if_expr_b_or_c(self):
        res = ParseResult()
        cases = []
        else_case = None

        if self.curr_token.type_name == "ELIF":
            all_cases = self.if_expr_b()
            if isinstance(all_cases, ParseResult):
                res.register(all_cases)
                return res.failure(all_cases.error)
            cases, else_case = all_cases
        else:
            else_case = self.if_expr_c()
            if isinstance(else_case, ParseResult):
                res.register(else_case)
                return res.failure(else_case.error)

        return res.success([cases, else_case])

    def if_expr_b(self):
        return self.if_expr_cases("ELIF")

    def power(self):
        return self.bin_op(self.call, [tk.TT_POW], self.factor)

    def factor(self):
        res = ParseResult()
        tok = self.curr_token
        return_val = res

        if tok.type_name == "PLUS" or tok.type_name == "MINUS":
            res.register(self.advance())
            fac_node = self.factor()
            if isinstance(fac_node, ParseResult):
                res.register(self.factor())
                return_val = res.failure(fac_node.error)

            return_val = res.success(UnaryNode(tok, fac_node))
        else:
            return_val = self.power()

        return return_val

    def term(self):
        return self.bin_op(self.factor, [tk.TT_MUL, tk.TT_DIV])

    def statements(self):
        res = ParseResult()
        statements = []

        while self.curr_token.type_name == tk.TT_NEWLINE:
            res.register(self.advance())

        statement = res.register(self.statement())
        if res.error is not None:
            return res

        statements.append(statement)

        more_statements = True

        while True:
            newline_count = 0
            while self.curr_token.type_name == tk.TT_NEWLINE:
                res.register(self.advance())
                newline_count += 1
            if newline_count == 0:
                more_statements = False

            if not more_statements:
                break
            statement = res.register(self.statement())
            if not statement:
                more_statements = False
                continue
            statements.append(statement)

        return_value = ListNode(statements)
        res.success(return_value)

        return return_value

    def statement(self):
        res = ParseResult()
        return_node = None

        if self.curr_token.type_name == "RETURN":
            res.register(self.advance())
            if self.curr_token.type_name != "NEWLINE":
                expr = self.expr()
                if isinstance(expr, ParseResult):
                    return res.failure(expr.error)
                return_node = ReturnNode(expr)
            return return_node

        expr = self.expr()
        if isinstance(expr, ParseResult):
            return res.failure(expr.error)

        return expr

    def expr(self):
        res = ParseResult()
        jump_back = self.token_idx

        if self.curr_token.type_name == tk.TT_ID:
            var_name = self.curr_token
            res.register(self.advance())

            if self.curr_token.type_name == tk.TT_COLON:
                res.register(self.advance())

                if self.curr_token.type_dec is None:
                    err = self.throw_error(res, "Variable declaration must have a type")
                    return res.failure(err)

                type_tok = self.curr_token
                res.register(self.advance())

                if self.curr_token.type_name == tk.TT_EQ:
                    res.register(self.advance())

                    val = self.expr()
                    if isinstance(val, ParseResult):
                        return res.failure(val)

                    return res.success(VarAssignNode(var_name, val, type_tok.type_dec))

            if self.curr_token.type_name == tk.TT_EQ:
                res.register(self.advance())

                val = self.expr()
                if isinstance(val, ParseResult):
                    return res.failure(val)

                return res.success(VarUpdateNode(var_name, val))

        self.token_idx = jump_back
        self.curr_token = self.tokens[self.token_idx]

        return self.bin_op(self.comp_expr, [tk.TT_AND, tk.TT_OR])

    def comp_expr(self):
        res = ParseResult()

        if self.curr_token.type_name == "NOT" or self.curr_token.type_name == "AND":
            op_tok = self.curr_token
            res.register(self.advance())

            node = self.comp_expr()
            if isinstance(node, ParseResult):
                res.register(node)
                err = self.throw_error(res, res.error.details)
                return err

            # BUG: Is this why unary ops don't work??
            return UnaryOpNode(op_tok, node)

        node = self.bin_op(self.arith_expr, [tk.TT_EE, tk.TT_NE, tk.TT_LT, tk.TT_GT, tk.TT_LOE, tk.TT_GOE])
        if isinstance(node, ParseResult):
            res.register(node)
            err = self.throw_error(res, res.error.details)
            return res.failure(err)

        return node

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
        if functionB is None:
            func = functionA

        left = functionA()
        if isinstance(left, ParseResult):
            return res.failure(left)

        loop_condition = self.check_equal_to_ops(ops, self.curr_token.type_name)
        while loop_condition:
            op_tok = VariableNode(self.curr_token)
            res.register(self.advance())

            right = func()
            if isinstance(right, ParseResult):
                return res.failure(right)

            left = BinOpNode(left, op_tok, right)
            loop_condition = self.check_equal_to_ops(ops, self.curr_token.type_name)

        return res.success(left)
