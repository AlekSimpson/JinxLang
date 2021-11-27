import Foundation

/* ERRORS */

class Error {
    var error_name: String 
    var details: String 

    init(error_name: String, details: String) {
        self.error_name = error_name
        self.details = details
    }

    func as_string() -> String {
        return ("\(self.error_name): \(self.details)")
    }
}

class IllegalCharError: Error {
    init(details: String) {
        super.init(error_name: "Illegal Character", details: details)
    }
}/* LEXER */

class Lexer {
    var text:String 
    var ln_pos:Int 
    var filename: String 
    // var curr_line:String 

    init(text_:String, fn:String) {
        self.text = text_
        self.ln_pos = -1 
        self.filename = fn
    }

    func make_tokens() -> ([Token], Error?) {
        var tokens:[Token] = []

        let items = Array(self.text).map(String.init)

        for item in items {
            if item == " " { continue }

            if let float = Float(item) {
                let num:Int = Int(float)
                let temp:Float = Float(num)
                let isInt = (float / temp) == 1

                if isInt {
                    tokens.append(Token(type_: .FACTOR, type_name: TT_INT, value_: num))
                }else {
                    tokens.append(Token(type_: .FACTOR, type_name: TT_FLOAT, value_: float))
                }
                continue
            } 

            switch item {
                case "+":
                    tokens.append(Token(type_: .OPERATOR, type_name: TT_PLUS, value_: item))
                case "-": 
                    tokens.append(Token(type_: .OPERATOR, type_name: TT_MINUS, value_: item))
                case "/":
                    tokens.append(Token(type_: .OPERATOR, type_name: TT_DIV, value_: item))
                case "*":
                    tokens.append(Token(type_: .OPERATOR, type_name: TT_MUL, value_: item))
                case "(":
                    tokens.append(Token(type_: .GROUP, type_name: TT_LPAREN, value_: item))
                case ")":
                    tokens.append(Token(type_: .GROUP, type_name: TT_RPAREN, value_: item))
                default: 
                    return ([], IllegalCharError(details: "'\(item)'"))
            }
        }

        return (tokens, nil)
    }
}/* POSITION */

class LinePosition {
    var idx: Int
    var ln: Int 
    var col: Int 

    init(idx: Int, ln: Int, col: Int) {
        self.idx = idx 
        self.ln = ln 
        self.col = col 
    }

    func advance() { 
        self.idx += 1
        self.col += 1
    }
}

/* NODE */

protocol AbstractNode {
    var error: Error? { get set }
    var description: String { get }
}

struct NumberNode: AbstractNode {
    var token: Token
    var error: Error?

    var description: String {
        return "NumberNode(\(token))"
    }
}

struct VariableNode: AbstractNode {
    var token: Token
    var error: Error? 

    var description: String {
        return "VariableName(\(token))"
    }
}

struct BinOpNode: AbstractNode {
    let lhs: AbstractNode
    let op: AbstractNode 
    let rhs: AbstractNode
    var error: Error?

    var description: String {
        return "BinOpNode(\(lhs), \(op), \(rhs))"
    }

    init(lhs: AbstractNode, op: AbstractNode, rhs: AbstractNode) {
        self.lhs = lhs 
        self.op = op
        self.rhs = rhs 
    }

    init(_ error: Error) {
        self.error = error 
    }
}/* PARSER */

class Parser {
    var tokens: [Token]
    var token_idx: Int = -1
    var curr_token: Token 

    let operatorPrecedence: [String: Int] = [
        "PLUS" : 20,
        "MINUS" : 20,
        "MUL" : 40,
        "DIV" : 40
    ]

    init(tokens: [Token]) {
        self.tokens = tokens 
        self.curr_token = self.tokens[self.token_idx]
        self.advance()
    }

    func advance() {
        self.token_idx += 1
        if self.token_idx < self.tokens.count {
            self.curr_token = self.tokens[self.token_idx]
        }
    }

    func parse() -> AbstractNode {
        if self.token_idx == self.tokens.count { return }

        let left = NumberNode(token: self.curr_token)
        self.advance() 
        var op: AbstractNode

        if self.curr_token.type == .OPERATOR {
            op = VariableNode(token: self.curr_token)
            self.advance()
        }else {
            return BinOpNode(Error(error_name: "InvalidSyntax", details: "Expected an operator"))
        }

        return BinOpNode(lhs: left, op: op, rhs: parse())
    }
}
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

    init() {
        self.type = .FACTOR 
        self.type_name = ""
        self.value = ""
    }

    init(type_: TT, type_name: String, value_: Any?=nil) {
        self.type = type_
        self.type_name = type_name
        self.value = value_
    }

    func as_string() -> String {
        return ("\(self.type) : \(self.value ?? "")")
    }
}/* CONSTANTS */

//let CHAR_SET = CharacterSet(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])

/* RUN */

func run(text: String, fn: String) -> AbstractNode {
    let lexer = Lexer(text_: text, fn: fn)
    let (tokens, error) = lexer.make_tokens()

    if let err = error { return BinOpNode(err) }

    // Generate AST 
    let parser = Parser(tokens: tokens)
    let ast = parser.parse()

    return ast 
}

while true {
    print("aqua> ", terminator:"")
    let text:String = readLine() ?? ""
    if text == "stop" { break }

    let result = run(text: text, fn: "file.aqua")

    if let err = result.error {
        print(err.as_string())
        break 
    }

    print(result.description)
}
