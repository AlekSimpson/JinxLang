/* TOKENS */

enum TT {
    case FACTOR 
    case OPERATOR
    case GROUP
}

struct TokenType {
    // This is is Metatype, (ex: factor, operator, etc)
    var type: TT 
    // This is the name of the type (ex: int, add, minus, etc)
    var name: String 
}

let TT_INT = "INT"
let TT_FLOAT = "FLOAT"
let TT_PLUS = "PLUS"
let TT_MINUS = "MINUS"
let TT_MUL = "MUL"
let TT_DIV = "DIV"
let TT_LPAREN = "LPAREN"
let TT_RPAREN = "RPAREN"

class Token {
    var type: TT 
    var type_name: String 
    var value: Any?
    var pos: LinePosition?

    init() {
        self.type = .FACTOR 
        self.type_name = ""
        self.value = ""
        self.pos = nil
    }

    init(type_: TT, type_name: String, value_: Any?=nil, pos: LinePosition?=nil) {
        self.type = type_
        self.type_name = type_name
        self.value = value_
        self.pos = pos
    }

    func as_string() -> String {
        return ("\(self.type) : \(self.value ?? "")")
    }
}