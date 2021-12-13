/* TOKENS */

let letters = CharacterSet.letters

enum TT {
    case FACTOR 
    case OPERATOR
    case GROUP
    
    case STRING

    case IDENTIFIER
    case EOF
    case INDICATOR
    
    case EQ
    case EE 
    case NE 
    case LT 
    case GT 
    case LOE 
    case GOE 

    case NOT
    case OR 
    case AND 

    case IF
    case ELIF 
    case ELSE 
    case FOR
    case IN
    case WHILE

    case LCURLY 
    case RCURLY 

    case FUNC
    case ARROW
    case COMMA
}

let TT_INT       = "INT"
let TT_FLOAT     = "FLOAT"
let TT_STRING    = "STRING"

let TT_PLUS      = "PLUS"
let TT_MINUS     = "MINUS"
let TT_MUL       = "MUL"
let TT_DIV       = "DIV"
let TT_POW       = "POW"

let TT_LPAREN    = "LPAREN"
let TT_RPAREN    = "RPAREN"
let TT_LCURLY = "LCURLY"
let TT_RCURLY = "RCURLY"

let TT_ID        = "IDENTIFIER" // name of variables
let TT_EOF       = "EOF"
let TT_INDICATOR = "INDICATOR"

let TT_EQ        = "EQ"
let TT_EE        = "EQUALS"
let TT_NE        = "NOT EQUALS"
let TT_LT        = "LESS THAN"
let TT_GT        = "GREATER THAN"
let TT_LOE       = "LESS THAN OR EQUALS"
let TT_GOE       = "GREATER THAN OR EQUALS"

let TT_NOT       = "NOT"
let TT_AND       = "AND"
let TT_OR        = "OR"

let TT_IF        = "IF" 
let TT_ELIF      = "ELSE IF"
let TT_ELSE      = "ELSE"
let TT_FOR       = "FOR"
let TT_WHILE     = "WHILE"
let TT_IN        = "IN"

let TT_FUNC      = "FUNC"
let TT_COMMA     = "COMMA"
let TT_ARROW     = "ARROW"



class Token {
    // This is is Metatype, (ex: factor, operator, etc)
    var type: TT 
    // This is the name of the type (ex: int, add, minus, etc)
    var type_name: String 
    var value: Any?
    var pos: Position?

    init() {
        self.type = .FACTOR 
        self.type_name = ""
        self.value = ""
        self.pos = nil
    }

    init(type: TT, type_name: String, value: Any?=nil, pos: Position?=nil) {
        self.type = type
        self.type_name = type_name
        self.value = value
        self.pos = pos
    }

    func as_string() -> String {
        return ("\(self.type) : \(self.value ?? "")")
    }
}