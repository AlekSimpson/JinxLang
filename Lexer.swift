/* LEXER */

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
                case "^":
                    let token = Token(type: .OPERATOR, type_name: TT_POW, value: item, pos: tok_pos)
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
}