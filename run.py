from lexer import Lexer
from Parser import Parser
from Interpreter import Interpreter
from Context import Context 
from SymbolTable import SymbolTable 

global_symbol_table = SymbolTable()

def run(text, fn):
    lexer = Lexer(text, fn)
    tokens, error = lexer.make_tokens()
    
    if error != None: return (None, error)

    # Generate AST 
    parser = Parser(tokens)
    nodes, parse_error = parser.parse()

    if parse_error != None: return (None, error)

    # Run program
    interpreter = Interpreter()
    ctx = Context("<program>")
    ctx.symbolTable = global_symbol_table

    result = interpreter.visit(nodes, ctx)

    return (result.value, result.error)

while True:
    textInput = input("aqua> ")
    if str(textInput) == "stop":
        break 

    result, error = run(textInput, "repl")

    if error != None: print(error.as_string())
    if result != None: print(result.print_self())



## KNOWN ERRORS ##
#  String interpolation does not work 
#  Division by zero is not handled for, needs to output an error 
