/* TOKENS */

let letters = CharacterSet.letters

enum TT {
    case FACTOR 
    case OPERATOR
    case GROUP
    case KEYWORD
    // case UNASSIGNED
    case IDENTIFIER
    
    case EQ
    case EOF
    case EE 
    case NE 
    case LT 
    case GT 
    case LOE 
    case GOE 
    case AND 
    case OR 
    case NOT
}

let KEYWORDS:[String] = ["and", "or", "not", "&&", "||", "!"]

let TT_INT        = "INT"
let TT_FLOAT      = "FLOAT"
let TT_PLUS       = "PLUS"
let TT_MINUS      = "MINUS"
let TT_MUL        = "MUL"
let TT_DIV        = "DIV"
let TT_POW        = "POW"
let TT_LPAREN     = "LPAREN"
let TT_RPAREN     = "RPAREN"
let TT_KEYWORD    = "KEYWORD"
let TT_EQ         = "EQ"
let TT_ID         = "IDENTIFIER" // name of variables
let TT_EOF        = "EOF"
// let TT_UNASSIGNED = "UNASSIGNED"
let TT_EE         = "EQUALS"
let TT_NE         = "NOT EQUALS"
let TT_NOT        = "NOT"
let TT_LT         = "LESS THAN"
let TT_GT         = "GREATER THAN"
let TT_LOE        = "LESS THAN OR EQUALS"
let TT_GOE        = "GREATER THAN OR EQUALS"

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