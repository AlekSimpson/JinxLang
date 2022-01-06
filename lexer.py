from tokens import Token
from Position import Position
import tokens as tk
from Error import InvalidSyntaxError, IllegalCharError

keywords = ["if", "else", "elif", "for", "in", "while", "method"]
keywordTokens = [tk.TT_IF, tk.TT_ELSE, tk.TT_ELIF, tk.TT_FOR, tk.TT_IN, tk.TT_WHILE, tk.TT_FUNC]

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
        self.reached_end = False

        self.quoteCount = 0

    def advance(self):
        if self.curr_idx < len(self.items) - 1:
            self.curr_idx = self.curr_idx + 1

    def isKeyword(self, word):
        for i in range(0, len(keywords)):
            if keywords[i] == word:
                return keywordTokens[i]
        return tk.TT_ID 

    def isLetter(self):
        letters = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXQZ_")
        for ltr in letters:
            if self.items[self.curr_idx] == ltr:
                return True 
        return False 

    def isNum(self, num=None):
        isNumber = True
        number = self.items[self.curr_idx] if num == None else num 
        try:
            int(number)
        except:
            isNumber = False 
        return isNumber

    def check_for_letters(self):
        if self.isLetter():
            pos = Position(0, self.curr_idx, self.filename)
            full_word = ''
            isLetter = True 
            while isLetter:
                isLetter = self.isLetter()
                if isLetter:
                    full_word = full_word + self.items[self.curr_idx]
                    if self.curr_idx == len(self.items) - 1: break 
                    self.advance()
                    self.item_count = self.item_count - 1
            
            tokenType = self.isKeyword(full_word)
            tok = Token(tk.MT_NONFAC, tokenType, full_word, pos)
            self.tokens.append(tok)
        return None 

    def check_for_numbers(self):
        if self.isNum():
            pos = Position(0, self.curr_idx, self.filename)
            full_num = ''
            isNumber = True 
            while isNumber:
                isNumber = self.isNum()
                if isNumber:
                    full_num = full_num + self.items[self.curr_idx]
                    if self.curr_idx == len(self.items) - 1: break
                    self.advance()
                    self.item_count = self.item_count - 1
            tok = Token(tk.MT_FACTOR, tk.TT_INT, int(full_num), pos)
            self.tokens.append(tok)
        return None 

    def check_subsequent(self):
        pos = Position(0, self.curr_idx, self.filename)
        # checks if at end of string 
        if (self.curr_idx + 1) >= (len(self.items) - 1): return None 
        
        if self.items[self.curr_idx + 1] == "=":
            if self.items[self.curr_idx] == "=":
                return Token(tk.MT_NONFAC, tk.TT_EE, "==", pos)
            elif self.items[self.curr_idx] == "!":
                return Token(tk.MT_NONFAC, tk.TT_NE, "!=", pos)
            elif self.items[self.curr_idx] == "<":
                return Token(tk.MT_NONFAC, tk.TT_LOE, "<=", pos)
            elif self.items[self.curr_idx] == ">":
                return Token(tk.MT_NONFAC, tk.TT_GOE, ">=", pos)
        elif self.items[self.curr_idx + 1] == self.items[self.curr_idx]:
            if self.curr_idx == "|":
                return Token(tk.Mt_NONFAC, tk.TT_OR, "||", pos)
            elif self.curr_idx == "&":
                return Token(tk.MT_NONFAC, tk.TT_AND, "&&", pos)
        return None 

    def check_for_string(self):
        full_str = ""
        pos = Position(0, self.curr_idx, self.filename)
        if self.items[self.curr_idx] == "\"":
            self.quoteCount += 1
            self.advance()
            while True:
                if self.items[self.curr_idx] == "\"":
                    self.quoteCount += 1
                    self.advance()
                    break
                if len(self.items) - 1 == self.curr_idx:
                    break 
                full_str = full_str + self.items[self.curr_idx]
                self.advance()
            tok = Token(tk.MT_NONFAC, tk.TT_STRING, full_str, pos)
            self.tokens.append(tok)
        return None 

    def check_for_symbols(self):
        symbols = ["+", "-", "/", "*", "^", "(", ")", "=", "!", "<", ">", "{", "}", ":", ",", "[", "]"]
        symbolsTokens = [tk.TT_PLUS, tk.TT_MINUS, tk.TT_DIV, tk.TT_MUL, tk.TT_POW, tk.TT_LPAREN, tk.TT_RPAREN, tk.TT_EQ, tk.TT_NOT, tk.TT_LT, tk.TT_GT, tk.TT_LCURLY, tk.TT_RCURLY, tk.TT_COLON, tk.TT_COMMA, tk.TT_LBRACKET, tk.TT_RBRACKET]
        pos = Position(0, self.curr_idx, self.filename)
        
        for i in range(0, len(symbols)):
            if self.items[self.curr_idx] == symbols[i]:
                nilTok = Token(tk.MT_NONFAC, symbolsTokens[i], self.items[self.curr_idx], pos)
                
                checkSub = self.check_subsequent()
                tok = nilTok if checkSub == None else checkSub

                self.tokens.append(tok)
                self.advance()
                if checkSub: self.advance()
        
        endOfLine = (self.curr_idx + 1) >= (len(self.items) - 1) 

        # check for and, or symbols 
        if self.items[self.curr_idx] == "|" and not endOfLine:
            if self.items[self.curr_idx + 1] == "|":
                tok = Token(tk.MT_NONFAC, tk.TT_OR, "||", pos)
                self.tokens.append(tok)
                self.advance()
                self.advance()
            else:
                # return an error here
                return IllegalCharError(self.items[self.curr_idx], pos) 
        elif self.items[self.curr_idx] == "&" and not endOfLine:
            if self.items[self.curr_idx + 1] == "&":
                tok = Token(tk.MT_NONFAC, tk.TT_AND, "&&", pos)
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
                tok = Token(tk.MT_NONFAC, tk.TT_ARROW, "->", pos)
                self.tokens.append(tok)
                self.advance()
                self.advance()

    def make_tokens(self):
        error = None 
        while True:
            self.last_idx = self.curr_idx
            if self.items[self.curr_idx] == ' ': self.advance()
            # check for string 
            error = self.check_for_string()
            if error != None: break 
            # check for numbers
            error = self.check_for_numbers()
            if error != None: break 
            # check for strings type
            error = self.check_for_letters()
            if error != None: break 
            # check for arrows
            error = self.check_for_arrow()
            if error != None: break 
            # check for symbols
            error = self.check_for_symbols()
            if error != None: break

            # check if all tokens collected
            if len(self.tokens) == len(self.items): break
            
            # Checks if it has checked everything and add EOF 
            self.reached_end = self.last_idx == self.curr_idx
            if self.reached_end:
                if self.quoteCount % 2 != 0:
                    pos = Position(0, self.curr_idx, self.filename)
                    return (None, InvalidSyntaxError(self.items[self.curr_idx], pos))
                self.tokens.pop()
                pos = Position(0, self.curr_idx, self.filename)
                EOF = Token(tk.MT_NONFAC, tk.TT_EOF, "EOF", pos)
                self.tokens.append(EOF)
                break

        return (self.tokens, error)
