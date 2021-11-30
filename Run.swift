/* RUN */

func run(text: String, fn: String) -> (Number?, Error?) {
    let lexer = Lexer(text_: text, fn: fn)
    let (tokens, error) = lexer.make_tokens()
    if error != nil { 
        return (nil, error)
    }

    // Generate AST 
    let parser = Parser(tokens: tokens)
    let (node, parse_error) = parser.parse()

    if let err = parse_error {
        return (nil, err)
    }

    // Run program
    let interpreter = Interpreter()
    let result = interpreter.visit(node: node!)

    return (result.value, result.error) 
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
}
