from lexer import Lexer
from Parser import Parser
from Context import Context
from GlobalTable import global_symbol_table
from Types import Number
from Interpreter import BuiltinFunction, Interpreter

global_symbol_table.set_val("nil", Number.nil)
global_symbol_table.set_val("true", Number.true)
global_symbol_table.set_val("false", Number.false)
global_symbol_table.set_val("print", BuiltinFunction.print)
global_symbol_table.set_val("append", BuiltinFunction.append)
global_symbol_table.set_val("run", BuiltinFunction.run)


def run(text, fn):
    lexer = Lexer(text, fn)
    tokens, error = lexer.make_tokens()

    if error is not None:
        return (None, error)

    # Generate AST
    parser = Parser(tokens)
    nodes, parse_error = parser.parse()

    if parse_error is not None:
        return (None, error)

    # Run program
    interpreter = Interpreter()
    ctx = Context("<program>")
    ctx.symbolTable = global_symbol_table
    result = interpreter.visit(nodes, ctx)

    return (result.value, result.error)


## BUG - KNOWN ##
#  Error handling for non recognized keywords/variables is broken
#  Last I checked arithmetic stopped working when there was no spaces between the characters

# TODO:
# When an array is declared the types stored in the array must also be included in the type declaration
# Update and add tests
#    - Things like tests for variable type checks (ex: a:Int = "test" should return an error)
#    - Add test for checking if returns work properly, like making sure statements after return don't run and stuff
