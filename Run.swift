/* CONSTANTS */

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
