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
        super.init(error_name: "Invalid Syntax Error", details: details, pos: pos)
    }
}

class ExpectedCharError: Error {
    init(details: String, pos: Position) {
        super.init(error_name: "Expected Character", details: details, pos: pos)
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

    init() {
        self.value = 0.0
        self.pos = nil
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
        let new_num = Number(self.value - other.value)
        new_num.set_context(ctx: other.context)
        return (new_num, nil)
    }

    func multiplied(by other: Number) -> (Number?, Error?) {
        let new_num = Number(self.value * other.value)
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

    func power(by other: Number) -> (Number?, Error?) {
        let new_num = Number(pow(self.value, other.value))
        new_num.set_context(ctx: other.context)
        return (new_num, nil)
    }

    func comp_eq(by other: Number) -> (Number?, Error?) {
        let new_num = Number((self.value == other.value ? 1 : 0))
        new_num.set_context(ctx: other.context)
        return (new_num, nil)
    }

    func comp_ne(by other: Number) -> (Number?, Error?) {
        let new_num = Number((self.value != other.value ? 1 : 0))
        new_num.set_context(ctx: other.context)
        return (new_num, nil)
    }

    func comp_lt(by other: Number) -> (Number?, Error?) {
        let new_num = Number((self.value < other.value ? 1 : 0))
        new_num.set_context(ctx: other.context)
        return (new_num, nil)
    }

    func comp_gt(by other: Number) -> (Number?, Error?) {
        let new_num = Number((self.value > other.value ? 1 : 0))
        new_num.set_context(ctx: other.context)
        return (new_num, nil)
    }

    func comp_loe(by other: Number) -> (Number?, Error?) {
        let new_num = Number((self.value <= other.value ? 1 : 0))
        new_num.set_context(ctx: other.context)
        return (new_num, nil)
    }

    func comp_goe(by other: Number) -> (Number?, Error?) {
        let new_num = Number((self.value >= other.value ? 1 : 0))
        new_num.set_context(ctx: other.context)
        return (new_num, nil)
    }

    func comp_and(by other: Number) -> (Number?, Error?) {
        let new_num = Number((self.value == 1 && other.value == 1 ? 1 : 0))
        new_num.set_context(ctx: other.context)
        return (new_num, nil)
    }

    func comp_or(by other: Number) -> (Number?, Error?) {
        let new_num = Number((self.value == 1 || other.value == 1 ? 1 : 0))
        new_num.set_context(ctx: other.context)
        return (new_num, nil)
    }

    func not() -> (Number?, Error?) {
        let new_num = Number((self.value == 1 ? 0 : 1))
        new_num.set_context(ctx: self.context)
        return (new_num, nil)
    }

    func is_true() -> Bool {
        return self.value != 0.0
    }

    func print_self() -> String {
        return "\(self.value)"
    }
}


class Function: Number {
    var name: String?
    var body_node: AbstractNode
    var arg_nodes: [String]?

    init(name: String?="anonymous", body_node: AbstractNode, arg_nodes: [String]?=nil) {
        self.name = name 
        self.body_node = body_node
        self.arg_nodes = arg_nodes
        super.init()
    }

    override init() {
        self.name = ""
        self.body_node = BinOpNode()
        self.arg_nodes = nil 
        super.init()
    }

    func execute(args: [Number]) -> (Number?, RuntimeResult) {
        let res = RuntimeResult()
        let interpreter = Interpreter()

        var str = ""
        if let s = name { str = s }

        let new_context = Context(display_name: str, parent: self.context, parent_entry_pos: self.pos)
        var par = Context()
        if let p = new_context.parent { par = p }
        new_context.symbolTable = par.symbolTable

        var a_nodes: [String] = []
        if let a = self.arg_nodes { a_nodes = a }

        var pos = Position()
        if let unwrapped = body_node.token.pos { pos = unwrapped }


        if a_nodes.count != 0 {
            if args.count > a_nodes.count {
                let err = RuntimeError(details: "to many arguements passed into function \(String(describing: name))", context: new_context, pos: pos)
                _ = res.failure(err)
                return (nil, res)
            }

            if args.count < a_nodes.count {
                let err = RuntimeError(details: "to few arguements passed into function \(String(describing: name))", context: new_context, pos: pos)
                _ = res.failure(err)
                return (nil, res)
            }

            for i in 0...(a_nodes.count - 1) {
                let arg_name = a_nodes[i] 
                let arg_value = args[i]
                arg_value.set_context(ctx: new_context)
                var sTable = SymbolTable()
                if let unwrapped = new_context.symbolTable { sTable = unwrapped }
                sTable.set_val(name: arg_name, value: arg_value)
            }
        }

        let body_res = interpreter.visit(node: self.body_node, context: new_context)
        _ = res.register(body_res)
        let value = res.value
        if res.error != nil { return (nil, res) }
        self.context = new_context
        return (value, res)
    }

    func copy() -> Function {
        let copy = Function(name: self.name, body_node: self.body_node, arg_nodes: self.arg_nodes) 
        copy.set_context(ctx: self.context)
        return copy 
    }

    override func print_self() -> String {
        return "<function \(self.name ?? "lambda")>"
    }
}

class string: Number {
    var str_value: String?

    init(value: String?=nil) {
        self.str_value = value
        super.init()
    }

    func added(to other: string) -> (string?, Error?) {
        var otherVal = ""
        var str = ""
        if let unwrapped = other.str_value { otherVal = unwrapped }
        if let unwrapped = self.str_value { str = unwrapped }
        let new_str = string(value: str + otherVal)
        new_str.set_context(ctx: other.context)
        return (new_str, nil)
    }

    override func is_true() -> Bool {
        return self.str_value != nil 
    }

    override func print_self() -> String {
        return "<string \(self.str_value ?? "")>"
    }
}/* POSITION */

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
}/* SYMBOL TABLE */

class SymbolTable {
    var symbols = [String:Number]()
    var parent:SymbolTable? = nil 

    init() {
        self.symbols = [String : Number]()
        self.parent = nil
    }

    func get_val(name: String) -> Number {
        let value = symbols[name]
        var returnVal: Number = Number(0.0)

        if let v = value {
            returnVal = v 
        }

        if let p = parent {
            returnVal = p.get_val(name: name)
        }

        return returnVal
    }

    func set_val(name: String, value: Number) {
        self.symbols[name] = value 
    }

    func remove_val(name: String) {
        self.symbols.removeValue(forKey: name)
    }
}/* CONTEXT */

class Context {
    var display_name: String 
    var parent: Context?
    var parent_entry_pos: Position?
    var symbolTable: SymbolTable?

    init(display_name: String, parent: Context?=nil, parent_entry_pos: Position?=nil) {
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbolTable = nil 
    }

    init() {
        self.display_name = ""
        self.parent = nil 
        self.parent_entry_pos = nil 
        self.symbolTable = nil 
    }
}/* LEXER */

class Lexer {
    var text:String 
    var ln_pos:Int 
    var filename: String 
    var tokens:[Token] = []

    init(text_:String, fn:String) {
        self.text = text_
        self.ln_pos = 0
        self.filename = fn
    }

    func make_tokens() -> ([Token], Error?) {
        let items = Array(self.text).map(String.init)
        var new_items = make_numbers(items: items)
        new_items = make_strings(items: new_items)
        if new_items.count != 1 {
            new_items = make_letters(items: new_items)
            new_items = make_else_if(items: new_items)
            new_items = make_comparison(for: "-", op: ">", items: new_items)
            new_items = make_comparison(for: "!", items: new_items)
            new_items = make_comparison(for: "=", items: new_items)
            new_items = make_comparison(for: "<", items: new_items)
            new_items = make_comparison(for: ">", items: new_items)
        }

        var txt_col = 0
        for item in new_items {
            if item == " " { continue }

            let tok_pos = Position(ln: 1, col: txt_col, fn: self.filename)

            // tokenize string types 
            let string_check = tokenize_strings(item: item, pos: tok_pos)
            if string_check { continue }

            // tokenize numbers
            let num_check = tokenize_number(item: item, pos: tok_pos)
            if num_check { continue }

            // tokenize words
            let word_check = tokenize_letters(item: item, pos: tok_pos)
            if word_check { continue } 

            var token = Token()

            switch item {
                case "+":
                    token = Token(type: .OPERATOR, type_name: TT_PLUS, value: item, pos: tok_pos)
                case "-": 
                    token = Token(type: .OPERATOR, type_name: TT_MINUS, value: item, pos: tok_pos)
                case "/":
                    token = Token(type: .OPERATOR, type_name: TT_DIV, value: item, pos: tok_pos)
                case "*":
                    token = Token(type: .OPERATOR, type_name: TT_MUL, value: item, pos: tok_pos)
                case "^":
                    token = Token(type: .OPERATOR, type_name: TT_POW, value: item, pos: tok_pos)
                case "(":
                    token = Token(type: .GROUP, type_name: TT_LPAREN, value: item, pos: tok_pos)
                case ")":
                    token = Token(type: .GROUP, type_name: TT_RPAREN, value: item, pos: tok_pos)
                case "=":
                    token = Token(type: .EQ, type_name: TT_EQ, value: item, pos: tok_pos)
                case "!":
                    token = Token(type: .NOT, type_name: TT_NOT, value: item, pos: tok_pos)
                case "<":
                    token = Token(type: .LT, type_name: TT_LT, value: item, pos: tok_pos)
                case ">":
                    token = Token(type: .GT, type_name: TT_GT, value: item, pos: tok_pos)
                case "!=":
                    token = Token(type: .NE, type_name: TT_NE, value: item, pos: tok_pos)
                case "<=":
                    token = Token(type: .LOE, type_name: TT_LOE, value: item, pos: tok_pos)
                case ">=":
                    token = Token(type: .GOE, type_name: TT_GOE, value: item, pos: tok_pos)
                case "&":
                    token = Token(type: .AND, type_name: TT_AND, value: item, pos: tok_pos)
                case "|":
                    token = Token(type: .OR, type_name: TT_OR, value: item, pos: tok_pos)
                case "==":
                    token = Token(type: .EE, type_name: TT_EE, value: item, pos: tok_pos)
                case "->": 
                    token = Token(type: .ARROW, type_name: TT_ARROW, value: item, pos: tok_pos)
                case "{":
                    token = Token(type: .LCURLY, type_name: TT_LCURLY, value: item, pos: tok_pos)
                case "}":
                    token = Token(type: .RCURLY, type_name: TT_RCURLY, value: item, pos: tok_pos)
                case ":":
                    token = Token(type: .INDICATOR, type_name: TT_INDICATOR, value: item, pos: tok_pos)
                case ",":
                    token = Token(type: .COMMA, type_name: TT_COMMA, value: item, pos: tok_pos)
                default: 
                    return ([], IllegalCharError(details: "'\(item)'", pos: tok_pos))
            }
            self.tokens.append(token)
            txt_col += 1
        }
        self.tokens.append(Token(type: .EOF, type_name: TT_EOF, value: TT_EOF))

        return (self.tokens, nil)
    }

    func isLetter(item: String) -> Bool {
        let range = item.rangeOfCharacter(from: letters)
        if let _ = range {
            return true 
        }
        return false 
    }

    func tokenize_strings(item: String, pos: Position) -> Bool {
        let characters = Array(item)
        
        if characters[0] == "\"" {
            let token = Token(type: .STRING, type_name: TT_STRING, value: item, pos: pos)
            self.tokens.append(token)
            return true
        }
        return false 
    }

    func tokenize_letters(item: String, pos: Position) -> Bool {
        let chars:[String] = Array(arrayLiteral: item)
        var token = Token()
        if isLetter(item: chars[0]) {
            switch item {
                case "and":
                    token = Token(type: .AND, type_name: TT_AND, value: item, pos: pos)
                case "or":
                    token = Token(type: .OR, type_name: TT_OR, value: item, pos: pos)
                case "not":
                    token = Token(type: .NOT, type_name: TT_NOT, value: item, pos: pos)
                case "if":
                    token = Token(type: .IF, type_name: TT_IF, value: item, pos: pos)
                case "else":
                    token = Token(type: .ELSE, type_name: TT_ELSE, value: item, pos: pos)
                case "else if":
                    token = Token(type: .ELIF, type_name: TT_ELIF, value: item, pos: pos)
                case "for":
                    token = Token(type: .FOR, type_name: TT_FOR, value: item, pos: pos)
                case "in":
                    token = Token(type: .IN, type_name: TT_IN, value: item, pos: pos)
                case "while":
                    token = Token(type: .WHILE, type_name: TT_WHILE, value: item, pos: pos)
                case "method":
                    token = Token(type: .FUNC, type_name: TT_FUNC, value: item, pos: pos)
                default:
                    token = Token(type: .IDENTIFIER, type_name: TT_ID, value: item, pos: pos)
            }

            self.tokens.append(token)
            return true // continue 
        }
        return false 
    }

    // checks if current token is a number and creates a number token if it is
    // returning true means it will skip the for loop (calls continue), returning false means it will not skip the for loop
    func tokenize_number(item: String, pos: Position) -> Bool {
        if let float = Float(item) {
            let num:Int = Int(float)
            let temp:Float = Float(num)
            let isInt = (float / temp) == 1

            if isInt {
                let token = Token(type: .FACTOR, type_name: TT_INT, value: num, pos: pos)
                self.tokens.append(token)
            }else {
                let token = Token(type: .FACTOR, type_name: TT_FLOAT, value: float, pos: pos)
                self.tokens.append(token)
            }
            return true // continue
        } 
        return false 
    }

    // Creates string type tokens 
    func make_strings(items: [String]) -> [String] {
        var new_items:[String] = []
        var curr_str = ""
        // var escape_char = false 
        var isStr = false

        for i in 0...(items.count - 1) {
            if isStr {
                if items[i] == "\"" { 
                    curr_str = curr_str + items[i]
                    new_items.append(curr_str)
                    isStr = false 
                    curr_str = ""
                    continue 
                }

                curr_str = curr_str + items[i]
                continue       
            }

            if items[i] == "\"" {
                curr_str = curr_str + items[i]
                isStr = true 
            }else {
                new_items.append(items[i])
            }
        }
        return new_items
    }

    func make_comparison(for comparison: String, op: String="=", items: [String]) -> [String] {
        var new_items:[String] = []
        var skipNext = false 

        for i in 0...(items.count - 1) {
            if skipNext { 
                skipNext = false 
                continue 
            }

            if items[i] == comparison && items[i + 1] == op {
                let new_char = "\(comparison)\(op)"
                new_items.append(new_char)
                skipNext = true 
                continue 
            }
            new_items.append(items[i])
        }

        return new_items
    }

    func make_else_if(items: [String]) -> [String] {
        var new_items:[String] = []
        var skipNext = false 

        for i in 0...(items.count - 1) {
            if skipNext {
                skipNext = false 
                continue
            }

            if items[i] == "else" && items[i + 1] == "if" {
                let new_word = "else if"
                new_items.append(new_word)
                skipNext = true
                continue 
            }
            new_items.append(items[i])
        }
        
        return new_items
    }

    func make_letters(items: [String]) -> [String] {
        var curr_word = ""
        var new_items:[String] = []

        for item in items {
            if item == " " {
                curr_word = ""
                continue
            }

            if isLetter(item: item) || (item == "_") {
                let new_word = curr_word == ""

                curr_word = curr_word + item 

                if new_word {
                    new_items.append(curr_word)
                }else {
                    let idx = last_index(items: new_items)
                    new_items[idx] = curr_word
                }
            }else {
                new_items.append(item)
                curr_word = ""
            }
        }

        return new_items
    }

    // takes the individual digits of numbers and combines them together so that they are counted as full numbers (ex: ["3", "4"] => "34")
    func make_numbers(items: [String]) -> [String] {
        var curr_num = ""
        var new_items: [String] = []

        for item in items {
            if item == " " {
                curr_num = ""
                new_items.append(item)
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
}/* NODE */

protocol AbstractNode {
    var token: Token { get set }
    var description: String { get }
    var classType: Int { get }

    func as_string() -> String
}

struct NumberNode: AbstractNode {
    var token: Token
    var direct_value: Number? = nil 
    var description: String { return "NumberNode(\(token.type_name))" }
    var classType: Int { return 1 }

    init(direct_value: Number) {
        self.direct_value = direct_value
        self.token = Token()
    }

    init(token: Token) {
        self.token = token 
        self.direct_value = nil 
    }

    func getNumber() -> Number {
        return Number(token.value as! Double)
    }

    func as_string() -> String {
        return token.as_string()
    }
}

struct VarAccessNode: AbstractNode {
    var token: Token 
    var description: String { return "VarAccessNode(\(token.type_name))" }
    var classType: Int { return 4 }
    init(token: Token) {
        self.token = token
    }

    func as_string() -> String {
        return token.as_string()
    }
}

struct VarAssignNode: AbstractNode {
    var token: Token 
    var value_node: AbstractNode 
    var description: String { return "VarAssignNode(\(token.type_name), \(value_node))" }
    var classType: Int { return 5 }

    init(token: Token, value_node: AbstractNode) {
        self.token = token
        self.value_node = value_node
    }

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

struct IfNode: AbstractNode {
    var token: Token
    var cases: [[AbstractNode]]
    var else_case: AbstractNode?
    var description: String { return "IfNode(\(token.type_name))" } 
    var classType: Int { return 6 }

    init(cases: [[AbstractNode]], else_case: AbstractNode?=nil) {
        self.cases = cases
        self.else_case = else_case
        self.token = cases[0][0].token
    }

    func as_string() -> String {
        return token.as_string()
    }
}

struct ForNode: AbstractNode {
    var token: Token 
    var startValue: NumberNode 
    var endValue: NumberNode 
    var bodyNode: AbstractNode
    var iterator: VarAssignNode
    var description:String { return "ForNode(\(token.type_name))" }
    var classType: Int { return 7 }

    init(iterator: VarAssignNode, startValue: NumberNode, endValue: NumberNode, bodyNode: AbstractNode) {
        self.iterator = iterator 
        self.startValue = startValue
        self.endValue = endValue
        self.bodyNode = bodyNode
        self.token = startValue.token 
    }

    func as_string() -> String {
        return token.as_string()
    }
}

struct WhileNode: AbstractNode {
    var token: Token 
    var conditionNode: AbstractNode 
    var bodyNode: AbstractNode
    var description: String { return "WhileNode(\(token.type_name))" }
    var classType: Int { return 8 }

    init(conditionNode: AbstractNode, bodyNode: AbstractNode) {
        self.conditionNode = conditionNode
        self.bodyNode = bodyNode
        self.token = conditionNode.token 
    }

    func as_string() -> String {
        return token.as_string()
    }
}

struct FuncDefNode: AbstractNode {
    var token: Token 
    var arg_name_tokens: [Token]?
    var body_node: AbstractNode
    var description: String { return "FuncDefNode(\(token.type_name))" }
    var classType: Int { return 9 }
    var lambda = Token(type: .IDENTIFIER, type_name: TT_ID, value: "lambda")

    init(token: Token?=nil, arg_name_tokens: [Token]?=nil, body_node: AbstractNode) {
        if token == nil {
            self.token = lambda 
        }else {
            self.token = token!
        }
        self.arg_name_tokens = arg_name_tokens
        self.body_node = body_node
    }

    func as_string() -> String {
        return token.as_string()
    }
}

struct CallNode: AbstractNode {
    var token: Token 
    var node_to_call: AbstractNode
    var arg_nodes: [AbstractNode]
    var description: String { return "CallNode(\(token.type_name))" }
    var classType: Int { return 10 }

    init(token: Token?=nil, node_to_call: AbstractNode, arg_nodes: [AbstractNode]) {
        if token == nil {
            self.token = Token()
        }else {
            self.token = token!
        }
        self.node_to_call = node_to_call
        self.arg_nodes = arg_nodes
    }

    func as_string() -> String {
        return token.as_string()
    }
}

struct StringNode: AbstractNode {
    var token: Token 
    var description: String { return "StringNode(\(token.type_name))" }
    var classType: Int { return 11 }

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
    var token: Token

    init(lhs: AbstractNode, op: AbstractNode, rhs: AbstractNode) {
        self.lhs = lhs 
        self.op = op
        self.rhs = rhs 
        self.token = Token() 
    }

    init() {
        self.lhs = VariableNode()
        self.op = VariableNode()
        self.rhs = VariableNode()
        self.token = Token() 
    }

    func as_string() -> String {
        return self.description
    }
}

class UnaryOpNode: AbstractNode {
    var token: Token 
    var node: AbstractNode
    var description: String {
        return "\(token.as_string()) \(node.as_string())"
    }
    var classType: Int {
        return 3
    }

    init(op_tok: Token, node: AbstractNode){
        self.token = op_tok
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

        if let err = parse_result.error {
            if self.curr_token.type != .EOF {
                return (nil, parse_result.failure(err))
            }
            return (nil, parse_result.error)
        }

        return (node_result, nil)
    }

    func call() -> (AbstractNode?, ParserResult) {
        let res = ParserResult()

        let (atom, atom_res) = self.atom()
        _ = res.register(atom_res)
        if res.error != nil { return (nil, res) }
        
        if self.curr_token.type_name == TT_LPAREN {
            _ = res.register(self.advance())
            
            var arg_nodes:[AbstractNode] = []

            if self.curr_token.type_name == TT_RPAREN {
                _ = res.register(self.advance())
            }else {
                let (expr, expr_res) = self.expr()
                if expr_res.error != nil { return (nil, expr_res) }
                arg_nodes.append(res.register(expr!))
                if expr_res.error != nil {
                    var p = Position()
                    if let unwrapped = expr!.token.pos { p = unwrapped }
                    let err = InvalidSyntaxError(details: "Expected closing parenthese in function declaration", pos: p) 
                    _ = res.failure(err)
                    return (nil, res)
                }

                while self.curr_token.type_name == TT_COMMA {
                    _ = res.register(self.advance())

                    let (expr, expr_res) = self.expr()
                    if expr_res.error != nil { return (nil, expr_res) }
                    arg_nodes.append(res.register(expr!))
                }

                if self.curr_token.type_name != TT_RPAREN {
                    var p = Position()
                    if let unwrapped = expr!.token.pos { p = unwrapped }
                    let err = InvalidSyntaxError(details: "Expected closing parenthese in function declaration", pos: p) 
                    _ = res.failure(err)
                    return (nil, res)
                }

                _ = res.register(self.advance())
            }
            return (res.success(CallNode(node_to_call: atom!, arg_nodes: arg_nodes)), res)
        }
        
        return (res.success(atom!), res)
    }

    func atom() -> (AbstractNode?, ParserResult) {
        let res = ParserResult()
        let tok = self.curr_token
        var returnVal: (AbstractNode?, ParserResult) = (nil, res)

        if tok.type == .FACTOR {
            let val = NumberNode(token: self.curr_token)
            _ = res.register(self.advance())
            returnVal = (res.success(val), res)
        }else if tok.type == .IDENTIFIER {
            _ = res.register(self.advance())
            return (res.success(VarAccessNode(token: tok)), res)
        }else if tok.type_name == TT_STRING {
            _ = res.register(self.advance())
            return (res.success(StringNode(token: tok)), res)
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
                }
            }

            if let err = recurrsion.1.error {
                _ = res.failure(err)
            }
        }else if tok.type_name == "IF" {
            var (if_expr, expr_res) = self.if_expr()
            _ = res.register(expr_res)
            if let err = res.error {
                _ = res.failure(err)
            }else {
                if let unwrapped = if_expr { if_expr = unwrapped }
                returnVal = (if_expr, res)
            }
        }else if tok.type_name == "FOR" {
            var (for_expr, expr_res) = self.for_expr()
            _ = res.register(expr_res)
            if let err = res.error {
                _ = res.failure(err)
            }else {
                if let unwrapped = for_expr { for_expr = unwrapped }
                returnVal = (for_expr, res)
            }
        }else if tok.type_name == "WHILE" {
            var (while_expr, expr_res) = self.while_expr()
            _ = res.register(expr_res)
            if let err = res.error {
                _ = res.failure(err)
            }else {
                if let unwrapped = while_expr { while_expr = unwrapped }
                returnVal = (while_expr, res)
            }
        }else if tok.type_name == "FUNC" {
            var (func_def, func_res) = self.func_def()
            _ = res.register(func_res)
            if let err = res.error {
                _ = res.failure(err)
            }else {
                if let unwrapped = func_def { func_def = unwrapped }
                returnVal = (func_def, res)
            }
        }
        else {
            var p = Position()
            if let position = tok.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected int, float, identifier, '+', '-', or '('", pos: p))
        }

        return returnVal
    }

    func func_def() -> (AbstractNode?, ParserResult) {
        let res = ParserResult()

        if !(self.curr_token.type_name == "FUNC") {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected 'method' keyword in function definition", pos: p))
            return (nil, res)
        }

        _ = res.register(self.advance())

        var name_token = Token()
        if self.curr_token.type_name == TT_ID { 
            name_token = self.curr_token 
            _ = res.register(self.advance())
        }

        if !(self.curr_token.type_name == TT_LPAREN) {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected '(' in function definition", pos: p))
            return (nil, res)
        }

        _ = res.register(self.advance())
        var arg_name_tokens: [Token] = []

        if self.curr_token.type_name == TT_ID {
            arg_name_tokens.append(self.curr_token)
            _ = res.register(self.advance())

            while self.curr_token.type_name == TT_COMMA {
                _ = res.register(self.advance())

                if self.curr_token.type_name != TT_ID {
                    var p = Position()
                    if let position = self.curr_token.pos { p = position }
                    _ = res.failure(InvalidSyntaxError(details: "Expected identifier after comma in function definition", pos: p))
                    return (nil, res)
                }

                arg_name_tokens.append(self.curr_token)
                _ = res.register(self.advance())
            }

            if !(self.curr_token.type_name == TT_RPAREN) {
                var p = Position()
                if let position = self.curr_token.pos { p = position }
                _ = res.failure(InvalidSyntaxError(details: "Expected ')' in function defintion", pos: p))
                return (nil, res)
            }
        }else {
            if !(self.curr_token.type_name == TT_RPAREN) {
                var p = Position()
                if let position = self.curr_token.pos { p = position }
                _ = res.failure(InvalidSyntaxError(details: "Expected identifier or ')' in function defintion", pos: p))
                return (nil, res)
            }
        }

        _ = res.register(self.advance())

        if self.curr_token.type_name != TT_ARROW {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected '->' in function defintion", pos: p))
            return (nil, res)
        }

        _ = res.register(self.advance())

        let (node_to_return, return_res) = self.expr()
        _ = res.register(return_res)
        if res.error != nil { return (nil, res) }

        return (res.success(FuncDefNode(token: name_token, arg_name_tokens: arg_name_tokens, body_node: node_to_return!)), res)
    }

    func for_expr() -> (AbstractNode?, ParserResult) {
        let res = ParserResult()

        if !(self.curr_token.type_name == "FOR") {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected 'for'", pos: p))
            return (nil, res)
        }

        _ = res.register(self.advance())

        if !(self.curr_token.type_name == "IDENTIFIER") {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected variable", pos: p))
            return (nil, res)
        }

        let iterator_token = self.curr_token
        _ = res.register(self.advance())

        if !(self.curr_token.type_name == "IN") {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected 'in' keyword", pos: p))
            return (nil, res)
        }

        _ = res.register(self.advance())

        let (start_value, start_res) = self.expr()
        _ = res.register(start_res)
        if res.error != nil { return (nil, res) }

        let iterator_var = VarAssignNode(token: iterator_token, value_node: start_value as! NumberNode)

        if !(self.curr_token.type_name == "INDICATOR") {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected ':' in range", pos: p))
            return (nil, res)
        }

        _ = res.register(self.advance())

        let (end_value, end_res) = self.expr()
        _ = res.register(end_res)
        if res.error != nil { return (nil, res) }

        if !(self.curr_token.type_name == "LCURLY") {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected '{' in for loop", pos: p))
            return (nil, res)
        }

        _ = res.register(self.advance())

        let (body, body_res) = self.expr()
        _ = res.register(body_res)
        if res.error != nil { return (nil, res) }

        if !(self.curr_token.type_name == "RCURLY") {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected '}' in for loop", pos: p))
            return (nil, res)
        }
        
        return (res.success(ForNode(iterator: iterator_var, startValue: start_value as! NumberNode, endValue: end_value as! NumberNode, bodyNode: body!)), res)
    }

    func while_expr() -> (AbstractNode?, ParserResult) {
        let res = ParserResult()

        if !(self.curr_token.type_name == "WHILE") {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected 'while' keyword in while loop", pos: p))
            return (nil, res)
        }

        _ = res.register(self.advance())

        let (cond_value, cond_res) = self.expr()
        _ = res.register(cond_res)
        if res.error != nil { return (nil, res) }

        if !(self.curr_token.type_name == "LCURLY") {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected '{' in for loop", pos: p))
            return (nil, res)
        }

        _ = res.register(self.advance())

        let (body_value, body_res) = self.expr()
        _ = res.register(body_res)
        if res.error != nil { return (nil, res) }

        if !(self.curr_token.type_name == "RCURLY") {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected '}' in for loop", pos: p))
            return (nil, res)
        }

        return (res.success(WhileNode(conditionNode: cond_value!, bodyNode: body_value!)), res)
    }

    func if_expr() -> (AbstractNode?, ParserResult) {
        let res = ParserResult()
        var cases:[[AbstractNode]] = []
        var else_case:AbstractNode? = nil 

        if !(self.curr_token.type_name == "IF") {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected 'if'", pos: p))
            return (nil, res)
        }

        _ = res.register(self.advance())

        let (condition, cond_result) = self.expr()
        _ = res.register(cond_result)
        if res.error != nil { return (nil, res) }

        if !(self.curr_token.type_name == "LCURLY") {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected '{'", pos: p))
            return (nil, res)
        }

        _ = res.register(self.advance())

        let (expression, expr_result) = self.expr()
        _ = res.register(expr_result)
        if res.error != nil { return (nil, res) }

        let new_element: [AbstractNode] = [condition!, expression!]
        cases.append(new_element)

        if !(self.curr_token.type_name == "RCURLY") {
            var p = Position()
            if let position = self.curr_token.pos { p = position }
            _ = res.failure(InvalidSyntaxError(details: "Expected '}'", pos: p))
            return (nil, res)
        }

        _ = res.register(self.advance())
        
        while self.curr_token.type_name == "ELSE IF" {
            _ = res.register(self.advance())

            let (cond, result) = self.expr()
            _ = res.register(result)
            if res.error != nil { return (nil, res) }

            if !(self.curr_token.type_name == "LCURLY") {
                var p = Position()
                if let position = self.curr_token.pos { p = position }
                _ = res.failure(InvalidSyntaxError(details: "Expected '{'", pos: p))
                return (nil, res)
            }

            _ = res.register(self.advance())

            let (exp, exp_result) = self.expr()
            _ = res.register(exp_result)
            if res.error != nil { return (nil, res) }

            let new_element:[AbstractNode] = [cond!, exp!]
            cases.append(new_element)

            if !(self.curr_token.type_name == "RCURLY") {
                var p = Position()
                if let position = self.curr_token.pos { p = position }
                _ = res.failure(InvalidSyntaxError(details: "Expected '}'", pos: p))
                return (nil, res)
            }
        }

        if self.curr_token.type_name == "ELSE" {
            _ = res.register(self.advance())

            if !(self.curr_token.type_name == "LCURLY") {
                var p = Position()
                if let position = self.curr_token.pos { p = position }
                _ = res.failure(InvalidSyntaxError(details: "Expected '{'", pos: p))
                return (nil, res)
            }

            _ = res.register(self.advance())

            let (e, e_result) = self.expr()
            _ = res.register(e_result)
            if res.error != nil { return (nil, res) }

            else_case = e

            if !(self.curr_token.type_name == "RCURLY") {
                var p = Position()
                if let position = self.curr_token.pos { p = position }
                _ = res.failure(InvalidSyntaxError(details: "Expected '}'", pos: p))
                return (nil, res)
            }
        }

        return (res.success(IfNode(cases: cases, else_case: else_case)), res)
    }

    func power() -> (AbstractNode?, ParserResult) {
        // return bin_op(funcA: atom, ops: TT_POW, funcB: factor)
        return bin_op(funcA: call, ops: TT_POW, funcB: factor)
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
        }else {
            returnVal = self.power()
        }
        return returnVal
    }

    func term() -> (AbstractNode?, ParserResult) {
        return self.bin_op(func: factor, ops: [TT_MUL, TT_DIV])
    }

    func expr() -> (AbstractNode?, ParserResult) {
        let res = ParserResult()

        if self.curr_token.type == .IDENTIFIER {
            let next = self.tokens[self.token_idx + 1]
            
            if next.type == .EQ {    
                let var_name = self.curr_token
                _ = res.register(self.advance())
                _ = res.register(self.advance())
                let (val, result) = self.expr()
                _ = res.register(result)
                if res.error != nil {
                    return (nil, res)
                }else {
                    return (res.success(VarAssignNode(token: var_name, value_node: val!)), res)
                }
            }
        }

        return self.bin_op(func: comp_expr, ops: [TT_AND, TT_OR])
    }

    func comp_expr() -> (AbstractNode?, ParserResult) {
        let res = ParserResult()

        if self.curr_token.type_name == "NOT" || self.curr_token.type_name == "AND" {
            let op_tok = self.curr_token
            _ = res.register(self.advance())

            let (node, node_result) = self.comp_expr()
            _ = res.register(node_result)
            if let _ = res.error { return (nil, res) }

            return (UnaryOpNode(op_tok: op_tok, node: node!), res)
        }

        let (node, node_result) = self.bin_op(func: self.arith_expr, ops: [TT_EE, TT_NE, TT_LT, TT_GT, TT_LOE, TT_GOE])
        _ = res.register(node_result)
        if let err = res.error {
            _ = res.failure(err)
            return (nil, res) 
        }

        return (node, res)
    }

    func arith_expr() -> (AbstractNode?, ParserResult) {
        return self.bin_op(func: self.term, ops: [TT_PLUS, TT_MINUS])
    }

    func check_equal_to_ops(ops: [String], type_name: String) -> Bool {
        for op in ops {
            if type_name == op {
                return true 
            }
        }
        return false 
    }

    func bin_op(func function: () -> (AbstractNode?, ParserResult), ops: [String]) -> (AbstractNode?, ParserResult) {
        let res = ParserResult()

        var (left, parse_result) = function()
        _ = res.register(parse_result)
        if res.error != nil { return (nil, res) }
        
        var loop_condition = check_equal_to_ops(ops: ops, type_name: self.curr_token.type_name)

        while  loop_condition { //self.curr_token.type_name == ops[0] || self.curr_token.type_name == ops[1]
            let op_tok = VariableNode(token: self.curr_token)
            _ = res.register(self.advance())

            let (right, parse_result_) = function()
            _ = res.register(parse_result_)
            if res.error != nil { return (nil, res) }
            
            left = BinOpNode(lhs: left!, op: op_tok, rhs: right!)
            loop_condition = check_equal_to_ops(ops: ops, type_name: self.curr_token.type_name)
        }

        return (res.success(left ?? VariableNode()), res)
    }

    func bin_op(funcA functionA: () -> (AbstractNode?, ParserResult), ops: String, funcB functionB: () -> (AbstractNode?, ParserResult)) -> (AbstractNode?, ParserResult) {
        let res = ParserResult()

        var (left, parse_result) = functionA()
        _ = res.register(parse_result)
        if res.error != nil { return (nil, res) }

        while self.curr_token.type_name == ops {
            let op_tok = VariableNode(token: self.curr_token)
            _ = res.register(self.advance())

            let (right, parse_result_) = functionB()
            _ = res.register(parse_result_)
            if res.error != nil { return (nil, res) }

            left = BinOpNode(lhs: left!, op: op_tok, rhs: right!)
        }
        return (res.success(left ?? VariableNode()), res)
    }
}

/* INTERPRETER */

class Interpreter {
    func visit(node: AbstractNode, context: Context) -> RuntimeResult {
        let func_index = node.classType
        var result = RuntimeResult()
        var table = [String : Number]()
        if let t = context.symbolTable { table = t.symbols }

        switch func_index {
            case 0:
                result = visit_binop(node: node as! BinOpNode, ctx: context)
            case 1:
                result = visit_number(node: node as! NumberNode, ctx: context)
            case 3:
                result = visit_unary(node: node as! UnaryOpNode, ctx: context)
            case 4: 
                let err = check_for_declaration(table: table, node: node, context: context)

                if let e = err { 
                    _ = result.failure(e)
                }else {
                    result = visit_VarAccessNode(node: node as! VarAccessNode, ctx: context)
                }
            case 5: 
                result = visit_VarAssignNode(node: node as! VarAssignNode, ctx: context)
            case 6:
                result = visit_IfNode(node: node as! IfNode, ctx: context)
            case 7: 
                result = visit_ForNode(node: node as! ForNode, ctx: context)
            case 8: 
                result = visit_WhileNode(node: node as! WhileNode, ctx: context)
            case 9:
                result = visit_FuncDefNode(node: node as! FuncDefNode, ctx: context)
            case 10:
                result = visit_CallNode(node: node as! CallNode, ctx: context)
            case 11: 
                result = visit_StringNode(node: node as! StringNode, ctx: context)
            default:
                print("no visit method found")
        }

        return result
    }

    func visit_StringNode(node: StringNode, ctx: Context) -> RuntimeResult {
        let rt = RuntimeResult()

        let str = string(value: (node.token.value as! String))
        str.set_context(ctx: ctx)

        return rt.success(str)
    }

    func visit_ForNode(node: ForNode, ctx: Context) -> RuntimeResult {
        let rt = RuntimeResult()    
        
        var res_value = rt.register(self.visit(node: node.startValue, context: ctx))
        if rt.error != nil { return rt }
        let start_value = res_value.value!

        res_value = rt.register(self.visit(node: node.endValue, context: ctx))
        if rt.error != nil { return rt }
        let end_value = res_value.value!.value 

        res_value = rt.register(self.visit(node: node.iterator, context: ctx))
        if rt.error != nil { return rt }
        let iterator_name = node.iterator.token.value as! String 

        let i = start_value

        var table = SymbolTable()
        if let t = ctx.symbolTable { table = t } 

        while i.value < end_value {
            table.set_val(name: iterator_name, value: i)
            i.value += 1

            _ = rt.register(self.visit(node: node.bodyNode, context: ctx))
            if rt.error != nil { return rt }
        }

        return RuntimeResult()
    }

    func visit_WhileNode(node: WhileNode, ctx: Context) -> RuntimeResult {
        let rt = RuntimeResult()

        while true {
            let condition = rt.register(self.visit(node: node.conditionNode, context: ctx))
            if rt.error != nil { return rt }
            let cond_value = condition.value!

            if !cond_value.is_true() { break }
            
            _ = rt.register(self.visit(node: node.bodyNode, context: ctx))
            if rt.error != nil { return rt }
        }

        return RuntimeResult()
    }

    func check_for_declaration(table: [String : Number], node: AbstractNode, context: Context) -> Error? {
        let access_node = node as! VarAccessNode
        let name = access_node.token.value as! String 
        var err:Error? = nil         

        if table[name] == nil {
            var pos = Position()
            if let p = access_node.token.pos { pos = p }
            err = RuntimeError(details: "'\(name)' is not defined", context: context, pos: pos)
        }
        return err
    }

    // Bin Op Node 
    func visit_binop(node: BinOpNode, ctx: Context) -> RuntimeResult {
        let rt = RuntimeResult()
        var result: Number? = nil
        var error: Error? = nil 
        var returnVal: RuntimeResult = RuntimeResult()
        
        // Get left node 
        let left_vst = self.visit(node: node.lhs, context: ctx)
        let _ = rt.register(left_vst)
        if rt.error != nil { return rt }
        let left = rt.value!

        // Get right node
        let right_vst = self.visit(node: node.rhs, context: ctx)
        let _ = rt.register(right_vst)
        if rt.error != nil { return rt }
        let right = rt.value!

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
            case TT_POW:
                (result, error) = left.power(by: right)
            case TT_EE:
                (result, error) = left.comp_eq(by: right)
            case TT_NE:
                (result, error) = left.comp_ne(by: right)
            case TT_LT:
                (result, error) = left.comp_lt(by: right)
            case TT_GT:
                (result, error) = left.comp_gt(by: right)
            case TT_LOE:
                (result, error) = left.comp_loe(by: right)
            case TT_GOE:
                (result, error) = left.comp_goe(by: right)
            case TT_AND: 
                (result, error) = left.comp_and(by: right)
            case TT_OR: 
                (result, error) = left.comp_or(by: right)
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

    func visit_IfNode(node: IfNode, ctx: Context) -> RuntimeResult {
        let res = RuntimeResult()

        for _case in node.cases {
            let condition_value = res.register(self.visit(node: _case[0], context: ctx))
            if res.error != nil { return res }
            let c_value = condition_value.value!

            if c_value.is_true() {
                let expr_value = res.register(self.visit(node: _case[1], context: ctx))
                if res.error != nil { return res }
                let e_value = expr_value.value!
                return res.success(e_value)
            }
        }

        if let e_case = node.else_case {
            let else_value = res.register(self.visit(node: e_case, context: ctx))
            if res.error != nil { return res }
            let e_value = else_value.value!
            return res.success(e_value)
        }
        return RuntimeResult()
    }

    // Unary Node 
    func visit_unary(node: UnaryOpNode, ctx: Context) -> RuntimeResult {
        let rt = RuntimeResult()
        let number_reg = rt.register(self.visit(node: node.node, context: ctx))
        var number: Number? = number_reg.value!
        if rt.error != nil { return rt }

        var error: Error? = nil 

        if node.token.type_name == TT_MINUS {
            if let num = number {
                (number, error) = num.multiplied(by: Number(-1))
            }
        }else if node.token.type_name == TT_NOT {
            if let num = number {
                (number, error) = num.not()
            }
        }

        if let err = error {
            return rt.failure(err)
        }else {
            return rt.success(number!)
        }
    }

    func visit_VarAccessNode(node: VarAccessNode, ctx: Context) -> RuntimeResult {
        let res = RuntimeResult()
        let var_name = node.token.value as! String
        
        var value:Number? = nil
        if let table = ctx.symbolTable { 
            value = table.get_val(name: var_name) 
        }
        

        if value != nil {
            return res.success(value!)
        }else {
            var p = Position()
            if let pos = node.token.pos { p = pos }
            let error = RuntimeError(details: "'\(var_name)' is not defined", context: ctx, pos: p)
            return res.failure(error)
        }
    }

    func visit_VarAssignNode(node: VarAssignNode, ctx: Context) -> RuntimeResult {
        let res = RuntimeResult()
        let var_name = node.token.value as! String
        let value = res.register(self.visit(node: node.value_node, context: ctx))
        if res.error != nil { return res }

        ctx.symbolTable!.set_val(name: var_name, value: value.value!)
        return res.success(value.value!)
    }

    // create Function type and add it to the symbol table [function name (String) : function (Function)]
    func visit_FuncDefNode(node: FuncDefNode, ctx: Context) -> RuntimeResult {
        let res = RuntimeResult()

        let func_name = node.token.value 
        let body_node = node.body_node
        var func_arg_names:[String] = []
        
        var a_name_tokens: [Token] = []
        if let unwrapped = node.arg_name_tokens { a_name_tokens = unwrapped }

        for arg_name in a_name_tokens {
            func_arg_names.append(arg_name.value as! String)
        }

        let method = Function(name: func_name as? String, body_node: body_node, arg_nodes: func_arg_names)
        method.set_context(ctx: ctx)

        if func_name != nil {
            var sTable = SymbolTable()
            if let unwrapped = ctx.symbolTable { sTable = unwrapped }
            sTable.set_val(name: func_name as! String, value: method)
        }

        return res.success(method)
    }

    // Get function name (value_to_call) then get the Function type from the symbol tree and then execute that function 
    func visit_CallNode(node: CallNode, ctx: Context) -> RuntimeResult {
        let res = RuntimeResult()
        var args: [Number] = []
        
        let value_to_call = res.register(self.visit(node: node.node_to_call, context: ctx))
        if res.error != nil { return (res) }

        var func_value = Function()
        if let unwrapped = value_to_call.value { func_value = unwrapped as! Function }

        let val_cal = func_value.copy()

        for arg_node in node.arg_nodes {
            let x = Double(arg_node.token.value as! Int)
            let new = Number(x)

            args.append(new)
        }

        let (return_value, return_res) = val_cal.execute(args: args)
        _ = res.register(return_res)
        if res.error != nil { return res }
        return res.success(return_value!)
    }
}/* Parse Result */

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
}/* RUNTIME RESULT */

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
}/* RUN */

var global_symbol_table = SymbolTable()
// global_symbol_table.set_val(name: "nil", value: 0.0)
// global_symbol_table.set_val(name: "true", value: 1.0)
// global_symbol_table.set_val(name: "false", value: 0.0)

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
    ctx.symbolTable = global_symbol_table
    
    let result = interpreter.visit(node: nodes!, context: ctx)

    return (result.value, result.error) 
}

while true {
    print("aqua> ", terminator:"")
    let text:String = readLine() ?? ""
    if text == "stop" { break }

    let (result, error) = run(text: text, fn: "stdin")

    if let err = error { print(err.as_string()) }
    if let r = result { print(r.print_self()) }
}
