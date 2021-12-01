/* TOKENS */

enum TT {
    case FACTOR 
    case OPERATOR
    case GROUP
    case EOF
}

let TT_INT = "INT"
let TT_FLOAT = "FLOAT"
let TT_PLUS = "PLUS"
let TT_MINUS = "MINUS"
let TT_MUL = "MUL"
let TT_DIV = "DIV"
let TT_LPAREN = "LPAREN"
let TT_RPAREN = "RPAREN"
let TT_EOF = "EOF"

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