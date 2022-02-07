TT_INT = "INT"
TT_STRING = "STRING"

MT_FACTOR = "FACTOR"
MT_NONFAC = "NON FACTOR"

TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_MUL = "MUL"
TT_DIV = "DIV"
TT_POW = "POW"

TT_LCURLY = "LCURLY"
TT_RCURLY = "RCURLY"
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
TT_LBRACKET = "LBRACKET"
TT_RBRACKET = "RBRACKET"

TT_ID = "IDENTIFIER"
TT_EOF = "EOF"
TT_COLON = "COLON"
TT_NEWLINE = "NEWLINE"

TT_EQ = "EQ" # This the assignment equals
TT_EE = "EQUALS" # This is the comparison equals
TT_NE = "NOT EQUALS"
TT_LT = "LESS THAN"
TT_GT = "GREATER THAN"
TT_LOE = "LESS THAN OR EQUAL"
TT_GOE = "GREATER THAN OR EQUALS"

TT_NOT = "NOT"
TT_AND = "AND"
TT_OR = "OR"

TT_IF = "IF"
TT_ELIF = "ELIF"
TT_ELSE = "ELSE"
TT_FOR = "FOR"
TT_WHILE = "WHILE"
TT_IN = "IN"
TT_RETURN = "RETURN"
TT_BREAK = "BREAK"
TT_CONTINUE = "CONTINUE"

TT_FUNC = "FUNC"
TT_COMMA = "COMMA"
TT_ARROW = "ARROW"

class Token:
    def __init__(self, type="", type_name="", value="", pos=None, type_dec=None):
        self.type = type
        self.type_name = type_name
        self.value = value
        self.pos = pos
        self.type_dec = type_dec

    def as_string(self):
        return (f'{self.type_name} : {self.value}')
