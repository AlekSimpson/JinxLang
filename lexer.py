from token import Position, Token
import token as tk

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

    def advance(self):
        if self.curr_idx < len(self.items) - 1:
            self.curr_idx = self.curr_idx + 1

    def isKeyword(self, word):
        for i in range(0, len(keywords)):
            if keywords[i] == word:
                return keywordTokens[i]
        return tk.TT_ID 

    def isLetter(self):
        letters = list("abcdefghijklmnopqrstuvwxyz")
        for ltr in letters:
            if self.items[self.curr_idx] == ltr and (self.curr_idx != len(self.items) - 1):
                return True 
        return False 

    def isNum(self):
        isNumber = True
        try:
            int(self.items[self.curr_idx])
        except:
            isNumber = False 
        return isNumber

    def check_for_letters(self):
        if self.isLetter():
            pos = Position(0, self.curr_idx, self.filename)
            full_word = self.items[self.curr_idx]
            isLtr = True 
            while isLtr:
                isLtr = self.isLetter()
                self.advance()

                if isLtr: full_word = full_word + self.items[self.curr_idx]
            
            tokenType = self.isKeyword(full_word)
            tok = Token(tk.MT_NONFAC, tokenType, full_word, pos)
            self.tokens.append(tok)
        
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

            
            tok = Token(tk.MT_FACTOR, tk.TT_INT, int(full_num), pos)
            self.tokens.append(tok)

    def check_subsequent(self):
        pos = Position(0, self.curr_idx, self.filename)
        if self.items[self.curr_idx + 1] == "=":
            if self.items[self.curr_idx] == "=":
                return Token(tk.MT_NONFAC, tk.TT_EE, "==", pos)
            elif self.items[self.curr_idx] == "!":
                return Token(tk.MT_NONFAC, tk.TT_NE, "!=", pos)
            elif self.items[self.curr_idx] == "<":
                return Token(tk.MT_NONFAC, tk.TT_LOE, "<=", pos)
            elif self.items[self.curr_idx] == ">":
                return Token(tk.MT_NONFAC, tk.TT_GOE, ">=", pos)
        return None 
                

    def check_for_symbols(self):
        symbols = ["+", "-", "/", "*", "^", "(", ")", "=", "!", "<", ">", "&&", "||", "{", "}", ":", ","]
        symbolsTokens = [tk.TT_PLUS, tk.TT_MINUS, tk.TT_DIV, tk.TT_MUL, tk.TT_POW, tk.TT_LPAREN, tk.TT_RPAREN, tk.TT_EQ, tk.TT_NOT, tk.TT_LT, tk.TT_GT, tk.TT_AND, tk.TT_OR, tk.TT_LCURLY, tk.TT_RCURLY, tk.TT_COLON, tk.TT_COMMA]
        for i in range(0, len(symbols) - 1):
            if self.items[self.curr_idx] == symbols[i]:
                pos = Position(0, self.curr_idx, self.filename)
                nilTok = Token(tk.MT_NONFAC, symbolsTokens[i], self.items[self.curr_idx], pos)
                
                checkSub = self.check_subsequent()
                tok = nilTok if checkSub == None else checkSub

                self.tokens.append(tok)
                self.advance()
                if checkSub: self.advance()

    def check_for_arrow(self):
        if self.items[self.curr_idx] == "-":
            if self.items[self.curr_idx + 1] == ">":
                pos = Position(0, self.curr_idx, self.filename)
                tok = Token(tk.MT_NONFAC, tk.ARROW, "->", pos)
                self.tokens.append(tok)
                self.advance()

    def make_tokens(self):
        while self.curr_idx < len(self.items) - 1:
            if self.items[self.curr_idx] == ' ': self.advance()
            # check for numbers
            self.check_for_numbers()
            # check for strings type
            self.check_for_letters()
            # check for arrows
            self.check_for_arrow()
            # check for symbols
            self.check_for_symbols()
        
        for tok in self.tokens:
            print(tok.as_string())
