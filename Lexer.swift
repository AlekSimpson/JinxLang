/* LEXER */

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
        new_items = make_letters(items: new_items)
        new_items = make_else_if(items: new_items)
        new_items = make_comparison(for: "!", items: new_items)
        new_items = make_comparison(for: "=", items: new_items)
        new_items = make_comparison(for: "<", items: new_items)
        new_items = make_comparison(for: ">", items: new_items)

        var txt_col = 0
        for item in new_items {
            if item == " " { continue }

            let tok_pos = Position(ln: 1, col: txt_col, fn: self.filename)

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
                case "{":
                    token = Token(type: .LCURLY, type_name: TT_LCURLY, value: item, pos: tok_pos)
                case "}":
                    token = Token(type: .RCURLY, type_name: TT_RCURLY, value: item, pos: tok_pos)
                case ":":
                    token = Token(type: .INDICATOR, type_name: TT_INDICATOR, value: item, pos: tok_pos)
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

    func make_comparison(for comparison: String, items: [String]) -> [String] {
        var new_items:[String] = []
        var skipNext = false 

        for i in 0...(items.count - 1) {
            if skipNext { 
                skipNext = false 
                continue 
            }

            if items[i] == comparison && items[i + 1] == "=" {
                let new_char = "\(comparison)="
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
}