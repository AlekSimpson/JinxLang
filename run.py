from lexer import Lexer
from Parser import Parser

def run(text, fn):
    lexer = Lexer(text, fn)
    tokens, error = lexer.make_tokens()
    
    if error != None: return (None, error)

    parser = Parser(tokens)
    nodes, parse_error = parser.parse()

    if parse_error != None: return (None, parse_error)

    print(nodes)
    for node in nodes:
        print(node.as_string())


while True:
    textInput = input("sona> ")
    if str(textInput) == "stop":
        break 

    text = run(textInput, "repl")
