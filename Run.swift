/* RUN */

func run(text: String, fn: String) -> (AbstractNode?, Error?) {
    let lexer = Lexer(text_: text, fn: fn)
    let (tokens, error) = lexer.make_tokens()
    if error != nil { 
        return (nil, error)
    }

    // Generate AST 
    let parser = Parser(tokens: tokens)
    let (node, parse_error) = parser.parse()

    return (node, parse_error) 
}

while true {
    print("aqua> ", terminator:"")
    let text:String = readLine() ?? ""
    if text == "stop" { break }

    let (node, error) = run(text: text, fn: "file.aqua")

    if error != nil {
        print(error!.as_string())
        break 
    }

    print(node!.description)
}
