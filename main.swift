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
}

class InvalidSyntaxError: Error {
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
        tokens.append(Token(type_: .EOF, type_name: TT_EOF, value_: TT_EOF))
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

    // func copy() {
    //     return LinePosition(idx: self.idx, ln: self.ln, col: self.col)
    // }
}

/* NODE */

protocol AbstractNode {
    var description: String { get }
    var classType: Int { get }

    func as_string() -> String 
}

struct NumberNode: AbstractNode {
    var token: Token
    var description: String {
        return "NumberNode(\(token.type_name))"
    }
    var classType: Int {
        return 1
    }

    func as_string() -> String {
        return token.as_string()
    }
}

struct VariableNode: AbstractNode {
    var token: Token
    var description: String {
        return "VariableName(\(token.type_name))"
    }
    var classType: Int {
        return 2
    }

    init() {
        self.token = Token()
    }

    init(token: Token) {
        self.token = token 
    }
    
    func as_string() -> String {
        return token.as_string()
    }
}

struct BinOpNode: AbstractNode {
    let lhs: AbstractNode
    let op: AbstractNode
    let rhs: AbstractNode
    var description: String {
        return "(\(lhs.as_string()), \(op.as_string()), \(rhs.as_string()))"
    }
    var classType: Int {
        return 0
    }

    init(lhs: AbstractNode, op: AbstractNode, rhs: AbstractNode) {
        self.lhs = lhs 
        self.op = op
        self.rhs = rhs 
    }

    init() {
        self.lhs = VariableNode()
        self.op = VariableNode()
        self.rhs = VariableNode()
    }

    func as_string() -> String {
        return self.description
    }
}

class UnaryOpNode: AbstractNode {
    var op_tok: Token 
    var node: AbstractNode
    var description: String {
        return "\(op_tok.as_string()) \(node.as_string())"
    }
    var classType: Int {
        return 3
    }

    init(op_tok: Token, node: AbstractNode){
        self.op_tok = op_tok
        self.node = node 
    }

    func as_string() -> String {
        return self.description 
    }
}/* PARSER */

class Parser {
    var tokens: [Token]
    var token_idx: Int = 0
    var curr_token: Token 

    init(tokens: [Token]) {
        self.tokens = tokens 
        self.curr_token = self.tokens[self.token_idx]
    }

    func advance() -> Token {
        self.token_idx += 1
        // print(self.token_idx)
        if self.token_idx < self.tokens.count {
            self.curr_token = self.tokens[self.token_idx]
        }
        return self.curr_token
    }

    func parse() -> (AbstractNode?, Error?) {
        let (node_result, parse_result) = self.expr()

        if let _ = parse_result.error {
            if self.curr_token.type != .EOF {
                return (nil, parse_result.failure(InvalidSyntaxError(details: "Expected an operator")))
            }
            return (nil, parse_result.error)
        }

        return (node_result, nil)
    }

    func factor() -> (AbstractNode?, ParserResult) {
        let res = ParserResult()
        let tok = self.curr_token
        var returnVal: (AbstractNode?, ParserResult) = (nil, res)

        if tok.type_name == "PLUS" || tok.type_name == "MINUS" {
            _ = res.register(self.advance())
            let recurrsion = self.factor()
            if let ftr = recurrsion.0 {
                _ = res.register(ftr)
                returnVal = (res.success( UnaryOpNode(op_tok: tok, node: ftr) ), res)
            }

            if let err = recurrsion.1.error {
                _ = res.failure(err)
                returnVal = (nil, res)
            }
        }else if tok.type == .FACTOR {
            let val = NumberNode(token: self.curr_token)
            _ = res.register(self.advance())
            returnVal = (res.success(val), res)
        }else if tok.type_name == "LPAREN" {
            _ = res.register(self.advance())
            let recurrsion = self.expr()
            if let epr = recurrsion.0 {
                _ = res.register(epr)
                if self.curr_token.type_name == "RPAREN" {
                    _ = res.register(self.advance())
                    returnVal = (res.success( epr ), res)
                }else {
                    _ = res.failure(InvalidSyntaxError(details: "Expected ')'"))
                    returnVal = (nil, res)
                }
            }

            if let err = recurrsion.1.error {
                _ = res.failure(err)
                returnVal = (nil, res)
            }
        }else {
            _ = res.failure(InvalidSyntaxError(details: "Expected int or float"))
            returnVal = (nil, res)
        }

        return returnVal
    }

    func term() -> (AbstractNode?, ParserResult) {
        return self.bin_op(func: factor, ops: [TT_MUL, TT_DIV])
    }

    func expr() -> (AbstractNode?, ParserResult) {
        return self.bin_op(func: term, ops: [TT_PLUS, TT_MINUS])
    }

    func bin_op(func function: () -> (AbstractNode?, ParserResult), ops: [String]) -> (AbstractNode?, ParserResult) {
        let res = ParserResult()

        var (left, parse_result) = function()
        _ = res.register(parse_result)
        if res.error != nil { return (nil, res) }

        while self.curr_token.type_name == ops[0] || self.curr_token.type_name == ops[1] {
            let op_tok = VariableNode(token: self.curr_token)
            _ = res.register(self.advance())

            let (right, parse_result_) = function()
            _ = res.register(parse_result_)
            if res.error != nil { return (nil, res) }

            left = BinOpNode(lhs: left!, op: op_tok, rhs: right!)
        }

        return (res.success(left ?? VariableNode()), res)
    }
}

class ParserResult { 
    var error: Error?
    var node: AbstractNode? 

    init() {
        self.error = nil 
        self.node = nil 
    }

    ///////////////////////////////////////////

    func register(_ res: ParserResult) -> AbstractNode {
        if res.error != nil { self.error = res.error }
        return res.node ?? VariableNode()
    }

    func register(_ _node: AbstractNode) -> AbstractNode {
        return _node
    }

    func register(_ _token: Token ) -> Token {
        return _token 
    }

    ///////////////////////////////////////////

    func success(_ node: AbstractNode) -> AbstractNode {
        self.node = node
        return node 
    }

    func failure(_ error: Error) -> Error {
        self.error = error 
        return self.error!
    }
}/* NUMBERS */

// This class is for storing numbers
class Number {
    var value: Int 
    var pos_start: Int? 
    var pos_end: Int? 

    init(_ value: Int) {
        self.value = value 
        self.set_pos()
    }

    func set_pos(start: Int?=nil, end: Int?=nil) {
        self.pos_start = start
        self.pos_end = end 
    }

    func added(to other: Number) -> Number {
        // if type(of: other) === Number {
            return Number(self.value + other.value)
        // }
    }

    func subtracted(from other: Number) -> Number {
        // if type(of: other) === Number {
            return Number(self.value - other.value)
        // }
    }

    func multiplied(by other: Number) -> Number {
        // if type(of: other) === Number {
            return Number(self.value * other.value)
        // }
    }

    func divided(by other: Number) -> Number {
        // if type(of: other) === Number {
            return Number(self.value / other.value)
        // }
    }

    func print_self() -> String {
        return "\(self.value)"
    }
}

/* INTERPRETER */

class Interpreter {
    init(){}

    func visit(node: AbstractNode) -> Number {
        let func_index = node.classType
        var result: Number = Number(0)

        switch func_index {
            case 0:
                result = visit_binop(node: node as! BinOpNode)
            case 1: 
                result = visit_number(node: node as! NumberNode)
            // case 2: 
            //     result = visit_variable(node: node as! VariableNode)
            case 3: 
                result = visit_unary(node: node as! UnaryOpNode)
            default:
                print("no visit method found")
        }

        return result
    }

    // Bin Op Node 
    func visit_binop(node: BinOpNode) -> Number {
        var result: Number = Number(0)
        let left = self.visit(node: node.lhs)
        let right = self.visit(node: node.rhs)

        let op_node = node.op as! VariableNode

        switch op_node.token.type_name {
            case TT_PLUS: 
                result = left.added(to: right)
            case TT_MINUS:
                result = left.subtracted(from: right)
            case TT_MUL:
                result = left.multiplied(by: right)
            case TT_DIV: 
                result = left.divided(by: right)
            default: 
                result = Number(0)
        }

        return result 
    }

    // Visit Number
    func visit_number(node: NumberNode) -> Number {
        return Number(node.token.value as! Int)
    }

    // Variable Node 
    // func visit_variable(node: VariableNode) {
    //     print("found variable node")
    // }

    // Unary Node 
    func visit_unary(node: UnaryOpNode) -> Number{
        var number = self.visit(node: node.node)

        if node.op_tok.type_name == TT_MINUS {
            number = number.multiplied(by: Number(-1))
        }

        return number
    }
}

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
}/* RUN */

func run(text: String, fn: String) -> (Number?, Error?) {
    let lexer = Lexer(text_: text, fn: fn)
    let (tokens, error) = lexer.make_tokens()
    if error != nil { 
        return (nil, error)
    }

    // Generate AST 
    let parser = Parser(tokens: tokens)
    let (node, parse_error) = parser.parse()

    // Run program
    let interpreter = Interpreter()
    let result = interpreter.visit(node: node!)

    return (result, parse_error) 
}

while true {
    print("aqua> ", terminator:"")
    let text:String = readLine() ?? ""
    if text == "stop" { break }

    let (result, error) = run(text: text, fn: "file.aqua")

    if error != nil {
        print(error!.as_string())
        break 
    }

    print(result!.print_self())

    // print(node!.description)
}
