/* RUN */

var global_symbol_table = SymbolTable()

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

    if let err = error {
        print(err.as_string())
        break 
    }

    print(result!.print_self())
}
