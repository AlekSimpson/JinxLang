import tokens as tk
from Types import Integer
from Error import *
from Node import *
from tokens import Token
from TypeValue import TypeValue

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

    def throw_error(self, msg, token=None):
        pos = self.curr_token if token is None else token.pos
        return InvalidSyntaxError(msg, pos)

    def parse(self):
        AST = self.statements()
        return AST

    def call(self):
        atom = self.atom()
        if isinstance(atom, Error):
            return self.throw_error(atom.details)

        if self.curr_token.type_name == tk.TT_LPAREN:
            self.advance()
            arg_nodes = []

            if self.curr_token.type_name == tk.TT_RPAREN:
                self.advance()
            else:
                expr = self.expr()
                if isinstance(expr, Error):
                    return self.throw_error("Expected closing parenthese in function declaration", expr.token)
                arg_nodes.append(expr)

                while self.curr_token.type_name == tk.TT_COMMA:
                    self.advance()

                    expr = self.expr()
                    if isinstance(expr, Error):
                        return self.throw_error(expr.token, expr.details)
                    arg_nodes.append(expr)

                if self.curr_token.type_name != tk.TT_RPAREN:
                    return self.throw_error("Expected closing parenthese in function declaration", expr.token)

                self.advance()

            return CallNode(atom, arg_nodes)
        elif self.curr_token.type_name == tk.TT_LBRACKET:
            self.advance()

            if (self.curr_token.type_name != tk.TT_INT and self.curr_token.type_name != tk.TT_ID):
                return self.throw_error("Array index must be an integer")

            index = self.atom()
            if isinstance(index, Error):
                return self.throw_error(index.details)

            if self.curr_token.type_name != tk.TT_RBRACKET:
                return self.throw_error("Array subscripts must have a closing bracket")

            self.advance()
            if self.curr_token.type_name == tk.TT_EQ:
                self.advance()

                # BUG: Probably should make it so that this is not the case, arrays should be able to hold any theoretical value
                if (not self.curr_token.type_name != tk.TT_INT and not self.curr_token.type_name != tk.TT_STRING):
                    return self.throw_error("Array can only hold value types of int or string")

                new_val = self.atom()
                if isinstance(new_val, Error):
                    return self.throw_error(new_val.details)

                self.advance()

                return ArraySetNode(atom, index, new_val)
            return ArrayGetNode(atom, index)
        return atom

    def atom(self):
        tok = self.curr_token

        if tok.type_name == tk.TT_INT:
            self.advance()
            return NumberNode(tok)

        elif tok.type_name == tk.TT_ID:
            self.advance()
            return VarAccessNode(tok)

        elif tok.type_name == tk.TT_STRING:
            self.advance()
            return StringNode(tok)

        elif tok.type_name == tk.TT_FLOAT:
            self.advance()
            return FloatNode(tok)

        elif tok.type_name == "LPAREN":
            self.advance()
            expr = self.expr()
            if expr is not None:
                if self.curr_token.type_name == "RPAREN":
                    self.advance()
                    return expr
                else:
                    return self.throw_error("Expected ')'", tok.pos)

            elif isinstance(expr, Error):
                return self.throw_error(expr.details)

        elif tok.type_name == tk.TT_LBRACKET:
            list_expr = self.list_expr()
            if isinstance(list_expr, Error):
                return self.throw_error(list_expr.details)
            return list_expr

        elif tok.type_name == "IF":
            if_expr = self.if_expr()
            if isinstance(if_expr, Error):
                return self.throw_error(if_expr.details)
            return if_expr

        elif tok.type_name == "FOR":
            for_expr = self.for_expr()
            if isinstance(for_expr, Error):
                return self.throw_error(for_expr.details)
            return for_expr

        elif tok.type_name == "WHILE":
            while_expr = self.while_expr()
            if isinstance(while_expr, Error):
                return self.throw_error(while_expr.details)
            return while_expr

        elif tok.type_name == "FUNC":
            func_def = self.func_def()
            if isinstance(func_def, Error):
                return self.throw_error(func_def.details)
            return func_def

    def list_expr(self):
        element_nodes = []

        if self.curr_token.type_name != tk.TT_LBRACKET:
            return self.throw_error("Expected '[' in list")

        self.advance()

        if self.curr_token.type_name == tk.TT_RBRACKET:
            self.advance()
        else:
            expr = self.expr()
            if isinstance(expr, Error):
                return self.throw_error(expr.details)

            element_nodes.append(expr)

            while self.curr_token.type_name == tk.TT_SPACE: # TT_COMMA
                self.advance()

                expr = self.expr()
                if isinstance(expr, Error):
                    return self.throw_error(expr.details)
                element_nodes.append(expr)

            if self.curr_token.type_name != tk.TT_RBRACKET:
                return self.throw_error("Expected closing bracket in list declaration")

            self.advance()
        return ListNode(element_nodes)

    def func_def(self):
        if not (self.curr_token.type_name == "FUNC"):
            return self.throw_error("Expected 'method' keyword in function declaration")

        self.advance()

        name_token = Token()
        if self.curr_token.type_name == tk.TT_ID:
            name_token = self.curr_token
            self.advance()

        if not (self.curr_token.type_name == tk.TT_LPAREN):
            return self.throw_error("Expected '(' in function defintion")

        self.advance()
        arg_name_tokens = []
        arg_type_tokens = []

        if self.curr_token.type_name == tk.TT_ID:
            look_for_args = True
            while look_for_args:
                if self.curr_token.type_name != tk.TT_ID:
                    err = self.throw_error("Expected value after comma in function defintion")
                    return err

                arg_name_tokens.append(self.curr_token)
                self.advance()

                if self.curr_token.type_name != tk.TT_COLON:
                    err = self.throw_error(f"Expected ':' in argument type declaration in function {name_token.value}")
                    return err
                self.advance()

                if self.curr_token.type_dec is None:
                    err = self.throw_error(f"Expected argument {arg_name_tokens[-1].value} to have a type declaration in function {name_token.value}")
                    return err

                arg_type_tokens.append(self.curr_token)
                self.advance()

                look_for_args = self.curr_token.type_name == tk.TT_COMMA
                if not look_for_args:
                    break
                self.advance()

        if not (self.curr_token.type_name == tk.TT_RPAREN):
            err = self.throw_error("Expected value or ')' in function definition")
            return err

        self.advance()

        if self.curr_token.type_name != tk.TT_COLON:
            err = self.throw_error("Expected ':' in function defintion")
            return err

        self.advance()

        if self.curr_token.type_dec is None:
            err = self.throw_error("Expected return type in function declaration")
            return err

        returnType = self.curr_token

        self.advance()

        if self.curr_token.type_name == tk.TT_ARROW:
            self.advance()

            node_to_return = self.expr()
            if isinstance(node_to_return, Error):
                err = self.throw_error(node_to_return.details)
                return err

            return FuncDefNode(node_to_return, returnType, name_token, arg_name_tokens, arg_type_tokens, False)

        if self.curr_token.type_name != "LCURLY":
            err = self.throw_error("Expected '{'")
            return err

        self.advance()

        if self.curr_token.type_name != tk.TT_NEWLINE:
            err = self.throw_error("Expected '->' in function or '{'")
            return err

        self.advance()

        body = self.statements()
        if isinstance(body, Error):
            err = self.throw_error(body.details)
            return err

        return_nil = True
        for node in body.element_nodes:
            if node.classType == 15:
                return_nil = False
                break

        if self.curr_token.type_name != "RCURLY":
            err = self.throw_error("Expected '}'")
            return err

        self.advance()
        returnVal = FuncDefNode(body, returnType, name_token, arg_name_tokens, arg_type_tokens, return_nil)
        return returnVal

    def for_expr(self):
        if not (self.curr_token.type_name == "FOR"):
            err = self.throw_error("Expected 'for'")
            return err

        self.advance()

        if not (self.curr_token.type_name == "IDENTIFIER"):
            err = self.throw_error("Expected variable")
            return err

        iterator_token = self.curr_token
        self.advance()

        if not (self.curr_token.type_name == "IN"):
            err = self.throw_error("Expected 'in' keyword")
            return err

        self.advance()

        start_value = self.expr()
        if isinstance(start_value, Error):
            err = self.throw_error(start_value.details)
            return err

        iterator_var = VarAssignNode(iterator_token, start_value, TypeValue(1, Integer(64)))

        if not (self.curr_token.type_name == "COLON"):
            err = self.throw_error("Expected ':' in range")
            return err

        self.advance()

        end_value = self.expr()
        if isinstance(end_value, Error):
            err = self.throw_error(end_value.details)
            return err

        if not (self.curr_token.type_name == "LCURLY"):
            err = self.throw_error("Expected '{' in for loop")
            return err

        self.advance()

        if self.curr_token.type_name == tk.TT_NEWLINE:
            self.advance()

            body = self.statements()
            if isinstance(body, Error):
                return self.throw_error(body.details)

            if self.curr_token.type_name != "RCURLY":
                return self.throw_error("Expected '}'")

            self.advance()

            return ForNode(iterator_var, start_value, end_value, body, True)

        body = self.expr()
        if isinstance(body, Error):
            return self.throw_error(body.details)

        if not (self.curr_token.type_name == "RCURLY"):
            return self.throw_error("Expected '}' in for loop")

        return ForNode(iterator_var, start_value, end_value, body, False)

    def while_expr(self):
        if not (self.curr_token.type_name == "WHILE"):
            return self.throw_error("Expected 'while' keyword in while loop")

        self.advance()

        cond_value = self.expr()
        if isinstance(cond_value, Error):
            return self.throw_error(cond_value.details)

        if not (self.curr_token.type_name == "LCURLY"):
            return self.throw_error("Expected '{' in while loop")

        self.advance()

        if self.curr_token.type_name == tk.TT_NEWLINE:
            self.advance()

            body = self.statements()
            if isinstance(body, Error):
                return self.throw_error(body.details)

            if self.curr_token.type_name != "RCURLY":
                return self.throw_error("Expected '}'")

            self.advance()

            return WhileNode(cond_value, body, True)

        body_value = self.expr()
        if isinstance(body_value, Error):
            return self.throw_error(body_value.details)

        if not (self.curr_token.type_name == "RCURLY"):
            return self.throw_error("Expected '}' in while loop")

        return WhileNode(cond_value, body_value, False)

    def if_expr(self):
        all_cases = self.if_expr_cases("IF")
        if isinstance(all_cases, Error):
            return self.throw_error(all_cases.details)
        cases, else_case = all_cases

        return IfNode(cases, else_case)

    def if_expr_cases(self, case_keyword):
        cases = []
        else_case = None

        if self.curr_token.type_name != case_keyword:
            return self.throw_error("Expected 'if'")

        self.advance()

        condition = self.expr()
        if isinstance(condition, Error):
            return self.throw_error(condition.details)

        if self.curr_token.type_name != "LCURLY":
            return self.throw_error("Expected '{'")

        self.advance()

        if self.curr_token.type_name == tk.TT_NEWLINE:
            self.advance()

            all_statements = self.statements()
            if isinstance(all_statements, Error):
                return self.throw_error(all_statements.details)
            statements = all_statements
            cases.append([condition, statements, True])

            if self.curr_token.type_name != "RCURLY":
                return self.throw_error("Expected '}'")
            self.advance()

            all_cases = self.if_expr_b_or_c()
            if isinstance(all_cases, Error):
                return self.throw_error(all_cases.details)

            new_cases, else_case = all_cases
            if len(new_cases) != 0:
                cases.extend(new_cases)
        else:
            expr = self.expr()
            if isinstance(expr, Error):
                return self.throw_error(expr.details)
            cases.append([condition, expr, False])

            if self.curr_token.type_name != "RCURLY":
                return self.throw_error("Expected '}'")
            self.advance()

            all_cases = self.if_expr_b_or_c()
            if isinstance(all_cases, Error):
                return self.throw_error(all_cases.details)
            new_cases, else_case = all_cases
            if len(new_cases) != 0:
                cases.extend(new_cases)

        return [cases, else_case]

    def if_expr_c(self):
        else_case = None

        if self.curr_token.type_name == "ELSE":
            self.advance()

            if self.curr_token.type_name != "LCURLY":
                return self.throw_error("Expected '{'in else statement")

            self.advance()

            if self.curr_token.type_name == tk.TT_NEWLINE:
                self.advance()

                statements = self.statements()
                if isinstance(statements, Error):
                    return self.throw_error(statements.details)
                else_case = [statements, True]

                if self.curr_token.type_name == "RCURLY":
                    self.advance()
                else:
                    return self.throw_error("Expected '}' in if statement")
            else:
                expr = self.expr()
                if isinstance(expr, Error):
                    return self.throw_error(expr.details)

                else_case = [expr, False]

        return else_case

    def if_expr_b_or_c(self):
        cases = []
        else_case = None

        if self.curr_token.type_name == "ELIF":
            all_cases = self.if_expr_b()
            if isinstance(all_cases, Error):
                return self.throw_error(all_cases.error)
            cases, else_case = all_cases
        else:
            else_case = self.if_expr_c()
            if isinstance(else_case, Error):
                return self.throw_error(else_case.error)

        return [cases, else_case]

    def if_expr_b(self):
        return self.if_expr_cases("ELIF")

    def power(self):
        return self.bin_op(self.call, [tk.TT_POW], self.factor)

    def factor(self):
        tok = self.curr_token
        return_val = tok

        if tok.type_name == "PLUS" or tok.type_name == "MINUS":
            self.advance()
            fac_node = self.factor()
            if isinstance(fac_node, Error):
                return self.throw_error(fac_node.details)

            return_val = UnaryNode(tok, fac_node)
        else:
            return_val = self.power()

        return return_val

    def term(self):
        return self.bin_op(self.factor, [tk.TT_MUL, tk.TT_DIV])

    def statements(self):
        statements = []

        while self.curr_token.type_name == tk.TT_NEWLINE:
            self.advance()

        statement = self.statement()
        if isinstance(statement, Error):
            return self.throw_error(statement.details)

        statements.append(statement)

        more_statements = True

        while True:
            newline_count = 0
            while self.curr_token.type_name == tk.TT_NEWLINE:
                self.advance()
                newline_count += 1
            if newline_count == 0:
                more_statements = False

            if not more_statements:
                break
            statement = self.statement()
            if not statement:
                more_statements = False
                continue
            statements.append(statement)

        return_value = ListNode(statements)

        return return_value

    def statement(self):
        return_node = None

        if self.curr_token.type_name == "RETURN":
            self.advance()
            if self.curr_token.type_name != "NEWLINE":
                expr = self.expr()
                if isinstance(expr, Error):
                    return self.throw_error(expr.details)
                return_node = ReturnNode(expr)
            return return_node

        expr = self.expr()
        if isinstance(expr, Error):
            return self.throw_error(expr.details)

        return expr

    def expr(self):
        jump_back = self.token_idx

        if self.curr_token.type_name == tk.TT_ID:
            var_name = self.curr_token
            self.advance()

            if self.curr_token.type_name == tk.TT_COLON:
                self.advance()

                if self.curr_token.type_dec is None:
                    return self.throw_error("Variable declaration must have a type")

                type_tok = self.curr_token
                self.advance()

                if self.curr_token.type_name == tk.TT_EQ:
                    self.advance()

                    val = self.expr()
                    if isinstance(val, Error):
                        return self.throw_error(val.details)

                    return VarAssignNode(var_name, val, type_tok.type_dec)

            if self.curr_token.type_name == tk.TT_EQ:
                self.advance()

                val = self.expr()
                if isinstance(val, Error):
                    return self.throw_error(val.details)

                return VarUpdateNode(var_name, val)

        self.token_idx = jump_back
        self.curr_token = self.tokens[self.token_idx]

        return self.bin_op(self.comp_expr, [tk.TT_AND, tk.TT_OR])

    def comp_expr(self):
        if self.curr_token.type_name == "NOT" or self.curr_token.type_name == "AND":
            op_tok = self.curr_token
            self.advance()

            node = self.comp_expr()
            if isinstance(node, Error):
                return self.throw_error(node.details)

            # BUG: Is this why unary ops don't work??
            return UnaryOpNode(op_tok, node)

        node = self.bin_op(self.arith_expr, [tk.TT_EE, tk.TT_NE, tk.TT_LT, tk.TT_GT, tk.TT_LOE, tk.TT_GOE])
        if isinstance(node, Error):
            return self.throw_error(node.details)

        return node

    def arith_expr(self):
        return self.bin_op(self.term, [tk.TT_PLUS, tk.TT_MINUS])

    def check_equal_to_ops(self, ops, type_name):
        for op in ops:
            if type_name == op:
                return True

        return False

    def bin_op(self, functionA, ops, functionB=None):
        func = functionB
        if functionB is None:
            func = functionA

        left = functionA()
        if isinstance(left, Error):
            return self.throw_error(left.details)

        loop_condition = self.check_equal_to_ops(ops, self.curr_token.type_name)
        while loop_condition:
            op_tok = VariableNode(self.curr_token)
            self.advance()

            right = func()
            if isinstance(right, Error):
                return self.throw_error(right.details)

            left = BinOpNode(left, op_tok, right)
            loop_condition = self.check_equal_to_ops(ops, self.curr_token.type_name)

        return left
