from tokens import Token
from Position import Position
from tokens import *
from Error import InvalidSyntaxError, IllegalCharError
from Types import Float, Integer, string, Void, Array, Bool
from TypeValue import TypeValue

keywords = ["if", "else", "elif", "for", "in", "while", "method", "return", "break", "continue"]
keywordTokens = [TT_IF, TT_ELSE, TT_ELIF, TT_FOR, TT_IN, TT_WHILE, TT_FUNC, TT_RETURN, TT_BREAK, TT_CONTINUE]

type_keywords = [
    "Int",
    "Int64",
    "Int32",
    "Int16",
    "Int8",
    "Float",
    "Float64",
    "Float32",
    "Float16",
    "Float8",
    "String",
    "Bool",
    "Void",
    "Array",
    "UInt",
    "UInt64",
    "UInt32",
    "UInt16",
    "UInt8",
]

type_values = [
    TypeValue(1, Integer(64)),
    TypeValue(1, Integer(64)),
    TypeValue(1, Integer(32)),
    TypeValue(1, Integer(16)),
    TypeValue(1, Integer(8)),
    TypeValue(2, Float(64)),
    TypeValue(2, Float(64)),
    TypeValue(2, Float(32)),
    TypeValue(2, Float(16)),
    TypeValue(2, Float(8)),
    TypeValue(11, string()),
    TypeValue(1, Bool(1)),
    TypeValue(404, Void()),
    TypeValue(12, Array()),
    TypeValue(1, Integer(64)),
    TypeValue(1, Integer(64)),
    TypeValue(1, Integer(32)),
    TypeValue(1, Integer(16)),
    TypeValue(1, Integer(8)),
]

class Lexer:
    def __init__(self, text, ln_pos=0, filename="repl"):
        self.text = text
        self.ln_pos = ln_pos
        self.filename = filename
        self.tokens = []
        self.items = list(self.text)
        self.curr_idx = 0
        self.item_count = len(self.items)
        self.last_idx = 0
        self.quoteCount = 0
        self.parsingArray = False

    def advance(self):
        if self.curr_idx < len(self.items) - 1:
            self.curr_idx = self.curr_idx + 1

    def get_array_type(self):
        element_type = None
        pos = Position(0, self.curr_idx, self.filename)

        if self.items[self.curr_idx] != "{":
            return InvalidSyntaxError("Expected opening curly brace in array declaration", pos)
        self.advance()

        element_type = self.parse_letters()
        typeref_check = self.isTypeRef(element_type)
        if typeref_check is None:
            return InvalidSyntaxError(f"Array cannot be of unrecognized type '{element_type}'", pos)

        element_type = typeref_check

        if self.items[self.curr_idx] != "}":
            return InvalidSyntaxError("Expected closing curly brace in array declaration", pos)
        self.advance()

        return element_type

    def peek_next(self):
        if self.curr_idx >= len(self.items):
            return self.curr_idx
        return self.curr_idx + 1

    def isKeyword(self, word):
        for i in range(0, len(keywords)):
            if keywords[i] == word:
                return keywordTokens[i]
        return TT_ID

    def isTypeRef(self, word):
        return_value = None
        for i in range(0, len(type_keywords)):
            if type_keywords[i] == word:
                return_value = type_values[i]

        if word == "Array":
            arr_type = self.get_array_type()
            if isinstance(arr_type, InvalidSyntaxError):
                return arr_type
            return_value.element_type = arr_type

        return return_value

    def isLetter(self):
        letters = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXQZ_")
        for ltr in letters:
            if self.items[self.curr_idx] == ltr:
                return True
        return False

    def isNum(self, num=None):
        isNumber = True
        number = self.items[self.curr_idx] if num is None else num
        try:
            int(number)
        except:
            isNumber = False
        return isNumber

    def check_for_letters(self):
        if self.isLetter():
            pos = Position(0, self.curr_idx, self.filename)
            full_word = self.parse_letters()

            tokenType = self.isKeyword(full_word)
            typeRef = self.isTypeRef(full_word)
            if isinstance(typeRef, InvalidSyntaxError):
                return typeRef
            tok = Token(MT_NONFAC, tokenType, full_word, pos, typeRef)
            self.tokens.append(tok)
        return None

    def parse_letters(self):
        full_word = ""
        isLetter = True
        while isLetter:
            isLetter = self.isLetter()
            if isLetter:
                full_word = full_word + self.items[self.curr_idx]
                if self.curr_idx == len(self.items) - 1:
                    break
                self.advance()
                self.item_count = self.item_count - 1
        return full_word

    def check_for_numbers(self):
        if self.isNum():
            pos = Position(0, self.curr_idx, self.filename)
            full_num = self.parse_numbers()
            tok = Token(MT_FACTOR, TT_INT, int(full_num), pos, TypeValue(1, Integer(64)))
            self.tokens.append(tok)
        return None

    def parse_numbers(self):
        full_num = ""
        isNumber = True
        while isNumber:
            isNumber = self.isNum()
            if isNumber:
                full_num = full_num + self.items[self.curr_idx]
                if self.curr_idx == len(self.items) - 1:
                    break
                self.advance()
                self.item_count = self.item_count - 1
        return full_num

    def check_for_floats(self):
        if self.items[self.curr_idx] == ".":
            if self.tokens[-1].type_name == "INT":
                num = str(self.tokens[-1].value)
                self.tokens.pop()
            self.advance()
            if self.isNum():
                decimal_val = str(self.parse_numbers())
            full_float = float(num + "." + decimal_val)
            tok = Token(MT_FACTOR, TT_FLOAT, full_float)
            self.tokens.append(tok)
        return None

    def check_subsequent(self):
        pos = Position(0, self.curr_idx, self.filename)
        # checks if at end of string
        if (self.curr_idx + 1) >= (len(self.items) - 1):
            return None

        if self.items[self.curr_idx + 1] == "=":
            if self.items[self.curr_idx] == "=":
                return Token(MT_NONFAC, TT_EE, "==", pos)
            elif self.items[self.curr_idx] == "!":
                return Token(MT_NONFAC, TT_NE, "!=", pos)
            elif self.items[self.curr_idx] == "<":
                return Token(MT_NONFAC, TT_LOE, "<=", pos)
            elif self.items[self.curr_idx] == ">":
                return Token(MT_NONFAC, TT_GOE, ">=", pos)
        elif self.items[self.curr_idx + 1] == self.items[self.curr_idx]:
            if self.curr_idx == "|":
                return Token(MT_NONFAC, TT_OR, "||", pos)
            elif self.curr_idx == "&":
                return Token(MT_NONFAC, TT_AND, "&&", pos)
        return None

    def check_for_string(self):
        full_str = ""
        pos = Position(0, self.curr_idx, self.filename)
        if self.items[self.curr_idx] == '"':
            self.quoteCount += 1
            self.advance()
            while True:
                if self.items[self.curr_idx] == '"':
                    self.quoteCount += 1
                    self.advance()
                    break
                if len(self.items) - 1 == self.curr_idx:
                    break
                full_str = full_str + self.items[self.curr_idx]
                self.advance()
            tok = Token(MT_NONFAC, TT_STRING, full_str, pos)
            self.tokens.append(tok)
        return None

    def check_for_symbols(self):
        symbols = ["+", "-", "/", "*", "^", "(", ")", "=", "!", "<", ">", "{", "}", ":", ",", "[", "]", ";", "\n"]
        symbolsTokens = [TT_PLUS, TT_MINUS, TT_DIV, TT_MUL, TT_POW, TT_LPAREN, TT_RPAREN, TT_EQ, TT_NOT,
                         TT_LT, TT_GT, TT_LCURLY, TT_RCURLY, TT_COLON, TT_COMMA, TT_LBRACKET, TT_RBRACKET,
                         TT_NEWLINE, TT_NEWLINE]
        pos = Position(0, self.curr_idx, self.filename)

        for i in range(0, len(symbols)):
            if self.items[self.curr_idx] == symbols[i]:
                if self.items[self.curr_idx] == "[":
                    self.parsingArray = True
                elif self.items[self.curr_idx] == "]":
                    self.parsingArray = False
                nilTok = Token(MT_NONFAC, symbolsTokens[i], self.items[self.curr_idx], pos)

                checkSub = self.check_subsequent()
                tok = nilTok if checkSub is None else checkSub

                self.tokens.append(tok)
                self.advance()
                if checkSub:
                    self.advance()

        endOfLine = (self.curr_idx + 1) >= (len(self.items) - 1)

        # check for and, or symbols
        if self.items[self.curr_idx] == "|" and not endOfLine:
            if self.items[self.curr_idx + 1] == "|":
                tok = Token(MT_NONFAC, TT_OR, "||", pos)
                self.tokens.append(tok)
                self.advance()
                self.advance()
            else:
                # return an error here
                return IllegalCharError(self.items[self.curr_idx], pos)
        elif self.items[self.curr_idx] == "&" and not endOfLine:
            if self.items[self.curr_idx + 1] == "&":
                tok = Token(MT_NONFAC, TT_AND, "&&", pos)
                self.tokens.append(tok)
                self.advance()
                self.advance()
            else:
                # return an error here
                return IllegalCharError(self.items[self.curr_idx], pos)
        return None

    def check_for_arrow(self):
        if self.items[self.curr_idx] == "-":
            if self.items[self.curr_idx + 1] == ">":
                pos = Position(0, self.curr_idx, self.filename)
                tok = Token(MT_NONFAC, TT_ARROW, "->", pos)
                self.tokens.append(tok)
                self.advance()
                self.advance()

    def skip_comment(self):
        self.advance()
        while self.items[self.curr_idx] != "\n":
            self.advance()
        self.advance()

    def make_tokens(self):
        error = None

        self.items.append("EOF")

        while True:
            self.last_idx = self.curr_idx
            if self.items[self.curr_idx] == " ":
                if self.parsingArray:
                    pos = Position(0, self.curr_idx, self.filename)
                    spaceTok = Token(MT_NONFAC, TT_SPACE, self.items[self.curr_idx], pos)
                    self.tokens.append(spaceTok)
                self.advance()
            if self.items[self.curr_idx] == "\t":
                self.advance()
            if self.items[self.curr_idx] == "#":
                self.skip_comment()

            # check for string
            error = self.check_for_string()
            if error is not None:
                break
            # check for numbers
            error = self.check_for_numbers()
            if error is not None:
                break

            # check for floats
            error = self.check_for_floats()
            if error is not None:
                break

            # check for strings type
            error = self.check_for_letters()
            if error is not None:
                break
            # check for arrows
            error = self.check_for_arrow()
            if error is not None:
                break
            # check for symbols
            error = self.check_for_symbols()
            if error is not None:
                break

            if self.items[self.curr_idx] == "EOF":
                pos = Position(0, self.curr_idx, self.filename)
                EOF = Token(MT_NONFAC, TT_EOF, "EOF", pos)
                self.tokens.append(EOF)

                if self.quoteCount % 2 != 0:
                    return (None, InvalidSyntaxError(self.items[self.curr_idx], pos))
                break
        return (self.tokens, error)
