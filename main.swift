import Foundation

/* ERRORS */

class Error {
    var error_name: String 
    var details: String 
    var pos: Position 

    init(error_name: String, details: String, pos: Position) {
        self.error_name = error_name
        self.details = details
        self.pos = pos
    }

    func as_string() -> String {
        return ("\(self.error_name): \(self.details)")
    }
}

class IllegalCharError: Error {
    init(details: String, pos: Position) {
        super.init(error_name: "Illegal Character", details: details, pos: pos)
    }
}

class InvalidSyntaxError: Error {
    init(details: String, pos: Position) {
        super.init(error_name: "Illegal Character", details: details, pos: pos)
    }
}

class RuntimeError: Error {
    var context: Context
    init(details: String, context: Context, pos: Position) {
        self.context = context
        super.init(error_name: "Runtime Error", details: details, pos: pos)
    }

    override func as_string() -> String {
        var result = self.generate_traceback()
        result += "\(self.error_name): \(self.details)"
        return result
    }

    func generate_traceback() -> String {
        var result = ""
        var p = self.pos 
        var ctx = self.context
        
        while true {
            if ctx.parent == nil { break }
            result += "\tFile: \(p.fn), line: \(p.ln), in \(ctx.display_name)\n\(result)"
            if let par_pos = ctx.parent_entry_pos { p = par_pos }
            if let par_ctx = ctx.parent { ctx = par_ctx }
        }  

        return "Traceback (most recent call last):\n\(result)"
    }
}/* NUMBERS */

// This class is for storing numbers
class Number {
    var value: Double 
    var pos: Position?
    var context: Context?

    init(_ value: Double, pos: Position?=nil) {
        self.value = value
        self.pos = pos 
        self.set_context()
    }

    func set_context(ctx: Context?=nil) {
        self.context = ctx 
    }

    func added(to other: Number) -> (Number?, Error?) {
        let new_num = Number(self.value + other.value)
        new_num.set_context(ctx: other.context)
        return (new_num, nil)
    }

    func subtracted(from other: Number) -> (Number?, Error?) {
        let new_num = Number(self.value + other.value)
        new_num.set_context(ctx: other.context)
        return (new_num, nil)
    }

    func multiplied(by other: Number) -> (Number?, Error?) {
        let new_num = Number(self.value + other.value)
        new_num.set_context(ctx: other.context)
        return (new_num, nil)
    }

    func divided(by other: Number) -> (Number?, Error?) {
        var p = Position()
        if let position = self.pos { p = position }

        let new_num = Number(self.value / other.value)
        new_num.set_context(ctx: other.context)

        var c = Context()
        if let ctx = self.context { c = ctx }
        if other.value == 0 { return (nil, RuntimeError(details: "cannot divide by zero", 
                                                        context: c, 
                                                        pos: p)) }

        return (new_num, nil)
    }

    func print_self() -> String {
        return "\(self.value)"
    }
}
/* POSITION */

class Position {
    var ln: Int 
    var col: Int 
    var fn: String 

    init(ln: Int, col: Int, fn: String) {
        self.ln = ln 
        self.col = col 
        self.fn = fn 
    }

    init() {
        self.ln = 0
        self.col = 0
        self.fn = ""
    }

    func copy() -> Position {
        // return LinePosition(idx: self.idx, ln: self.ln, col: self.col)
        return self 
    }
}/* CONTEXT */

class Context {
    var display_name: String 
    var parent: Context?
    var parent_entry_pos: Position?

    init(display_name: String, parent: Context?=nil, parent_entry_pos: Position?=nil) {
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
    }

    init() {
        self.display_name = ""
        self.parent = nil 
        self.parent_entry_pos = nil 
    }
}/* LEXER */

class Lexer {
    var text:String 
    var ln_pos:Int 
    var filename: String 

    // var curr_line:String 

    init(text_:String, fn:String) {
        self.text = text_
        self.ln_pos = 0
        self.filename = fn
    }

    func make_tokens() -> ([Token], Error?) {
        var tokens:[Token] = []

        let items = Array(self.text).map(String.init)
        let new_items = make_numbers(items: items)

        var txt_col = 0
        for item in new_items {
            if item == " " { continue }

            let tok_pos = Position(ln: 1, col: txt_col, fn: self.filename)

            if let float = Float(item) {
                let num:Int = Int(float)
                let temp:Float = Float(num)
                let isInt = (float / temp) == 1

                if isInt {
                    let token = Token(type: .FACTOR, type_name: TT_INT, value: num, pos: tok_pos)
                    tokens.append(token)
                }else {
                    let token = Token(type: .FACTOR, type_name: TT_FLOAT, value: float, pos: tok_pos)
                    tokens.append(token)
                }
                continue
            } 

            switch item {
                case "+":
                    let token = Token(type: .OPERATOR, type_name: TT_PLUS, value: item, pos: tok_pos)
                    tokens.append(token)
                case "-": 
                    let token = Token(type: .OPERATOR, type_name: TT_MINUS, value: item, pos: tok_pos)
                    tokens.append(token)
                case "/":
                    let token = Token(type: .OPERATOR, type_name: TT_DIV, value: item, pos: tok_pos)
                    tokens.append(token)
                case "*":
                    let token = Token(type: .OPERATOR, type_name: TT_MUL, value: item, pos: tok_pos)
                    tokens.append(token)
                case "(":
                    let token = Token(type: .GROUP, type_name: TT_LPAREN, value: item, pos: tok_pos)
                    tokens.append(token)
                case ")":
                    let token = Token(type: .GROUP, type_name: TT_RPAREN, value: item, pos: tok_pos)
                    tokens.append(token)
                default: 
                    return ([], IllegalCharError(details: "'\(item)'", pos: tok_pos))
            }
            txt_col += 1
        }
        tokens.append(Token(type: .EOF, type_name: TT_EOF, value: TT_EOF))
        return (tokens, nil)
    }

    func make_numbers(items: [String]) -> [String] {
        var curr_num = ""
        var new_items: [String] = []

        for item in items {
            if item == " " {
                curr_num = ""
                continue
            }

            if isNum(item) || (item == ".") {
                let new_num = curr_num == ""

                curr_num = curr_num + item 

                if new_num {
                    new_items.append(curr_num)
                }else {
                    let idx = last_index(items: new_items)
                    new_items[idx] = curr_num
                }
            }else {
                new_items.append(item)
                curr_num = ""
            }
        }     

        return new_items
    }

    func last_index(items: [String]) -> Int {
        if items.count == 1 {
            return 0
        }else {
            return (items.count - 1)
        }
    }

    // returns whether item is a number or not (PROBABLY NEEDS REFACTOR)
    func isNum(_ item: String) -> Bool {
        if item == "0" { return true }
        if let float = Float(item) {
            let num:Int = Int(float)
            let temp:Float = Float(num)
            let isInt = (float / temp) == 1

            if isInt {
                return true 
            }else {
                return false 
            }
        } 
        return false 
    }

    // .
}/* NODE */

protocol AbstractNode {
    var description: String { get }
    var classType: Int { get }

    func as_string() -> String 
}

struct NumberNode: AbstractNode {
    var token: Token
    var description: String { return "NumberNode(\(token.type_name))" }
    var classType: Int { return 1 }

    func as_string() -> String {
        return token.as_string()
    }
}

struct VariableNode: AbstractNode {
    var token: Token
    var description: String { return "VariableName(\(token.type_name))" }
    var classType: Int { return 2 }


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
    var description: String { return "(\(lhs.as_string()), \(op.as_string()), \(rhs.as_string()))" }
    var classType: Int { return 0 }

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
        if self.token_idx < self.tokens.count {
            self.curr_token = self.tokens[self.token_idx]
        }
        return self.curr_token
    }

    func parse() -> (AbstractNode?, Error?) {
        let (node_result, parse_result) = self.expr()

        if let _ = parse_result.error {
            if self.curr_token.type != .EOF {
                var p = Position()
                if let position = self.curr_token.pos { p = position }
                return (nil, parse_result.failure(InvalidSyntaxError(details: "Expected an operator", pos: p)))
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
                    var p = Position()
                    if let position = tok.pos { p = position }
                    _ = res.failure(InvalidSyntaxError(details: "Expected ')'", pos: p))
                    returnVal = (nil, res)
                }
            }

            if let err = recurrsion.1.error {
                _ = res.failure(err)
                returnVal = (nil, res)
            }
        }else {
            var p = Position()
            if let position = tok.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected int or float", pos: p))
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

/* Parse Result */

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
}/* INTERPRETER */

class Interpreter {
    func visit(node: AbstractNode, context: Context) -> RuntimeResult {
        let func_index = node.classType
        var result = RuntimeResult()

        switch func_index {
            case 0:
                result = visit_binop(node: node as! BinOpNode, ctx: context)
            case 1:
                result = visit_number(node: node as! NumberNode, ctx: context)
            case 3:
                result = visit_unary(node: node as! UnaryOpNode, ctx: context)
            default:
                print("no visit method found")
        }

        return result
    }

    // Bin Op Node 
    func visit_binop(node: BinOpNode, ctx: Context) -> RuntimeResult {
        let rt = RuntimeResult()
        var result: Number? = nil
        var error: Error? = nil 
        var returnVal: RuntimeResult = RuntimeResult()

        // Get context for nodes
        var entry = Position()
        if node.lhs is NumberNode {
            let node = node.lhs as! NumberNode
            if let position = node.token.pos { entry = position }
        }
        let child_context = Context(display_name: "<binary operation>", parent: ctx, parent_entry_pos: entry)
        
        // Get left node 
        let left_vst = self.visit(node: node.lhs, context: child_context)
        let _ = rt.register(left_vst)
        let left = rt.value!
        if rt.error != nil { return rt }

        // Get right node
        let right_vst = self.visit(node: node.rhs, context: child_context)
        let _ = rt.register(right_vst)
        let right = rt.value!
        if rt.error != nil { return rt }

        let op_node = node.op as! VariableNode
        
        switch op_node.token.type_name {
            case TT_PLUS: 
                (result, error) = left.added(to: right)
            case TT_MINUS:
                (result, error) = left.subtracted(from: right)
            case TT_MUL:
                (result, error) = left.multiplied(by: right)
            case TT_DIV: 
                (result, error) = left.divided(by: right)
            default: 
                (result, error) = (Number(0), nil)
        }
        
        if let err = error { returnVal = rt.failure(err) }

        if let res = result { returnVal = rt.success(res) }
        return returnVal 
    }

    // Visit Number
    func visit_number(node: NumberNode, ctx: Context) -> RuntimeResult {
        var entry = Position()
        if let position = node.token.pos { entry = position }
        let child_context = Context(display_name: "<number>", parent: ctx, parent_entry_pos: entry)

        var val = 0.0
        if let v = node.token.value as? Float {
            val = Double(v)
        }else if let v = node.token.value as? Int {
            val = Double(v)
        }
        
        var p = Position()
        if let position = node.token.pos { p = position }

        let num = Number(val, pos: p)
        num.set_context(ctx: child_context)

        return RuntimeResult().success(
            num 
        )
    }

    // Unary Node 
    func visit_unary(node: UnaryOpNode, ctx: Context) -> RuntimeResult {
        let rt = RuntimeResult()
        let number_reg = rt.register(self.visit(node: node.node, context: ctx))
        var number: Number? = number_reg.value!
        if rt.error != nil { return rt }

        var error: Error? = nil 

        if node.op_tok.type_name == TT_MINUS {
            if let num = number {
                (number, error) = num.multiplied(by: Number(-1))
            }
        }

        if let err = error {
            return rt.failure(err)
        }else {
            return rt.success(number!)
        }
    }
}

/* RUNTIME RESULT */

class RuntimeResult {
    var value: Number? 
    var error: Error?

    init(value: Number, error: Error){
        self.value = value 
        self.error = error 
    }

    init() {
        self.value = nil 
        self.error = nil 
    }
    
    func register(_ result: RuntimeResult) -> RuntimeResult {
        if result.error != nil { self.error = result.error } 
        self.value = result.value
        return self 
    } 

    func success(_ value: Number) -> RuntimeResult {
        self.value = value 
        return self 
    }

    func failure(_ error: Error) -> RuntimeResult {
        self.error = error 
        return self
    }
}/* TOKENS */

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
}/* RUN */

func run(text: String, fn: String) -> (Number?, Error?) {
    let lexer = Lexer(text_: text, fn: fn)
    let (tokens, error) = lexer.make_tokens()
    if error != nil { 
        return (nil, error)
    }

    // Generate AST 
    let parser = Parser(tokens: tokens)
    let (nodes, parse_error) = parser.parse()

    if let err = parse_error {
        return (nil, err)
    }

    // Run program
    let interpreter = Interpreter()
    let ctx = Context(display_name: "<program>")
    let result = interpreter.visit(node: nodes!, context: ctx)

    return (result.value, result.error) 
}

while true {
    print("aqua> ", terminator:"")
    let text:String = readLine() ?? ""
    if text == "stop" { break }

    let (result, error) = run(text: text, fn: "stdin")

    if let err = error {
        print(err.as_string())
        break 
    }

    print(result!.print_self())
}
