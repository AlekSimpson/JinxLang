/* LEXER */

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
}