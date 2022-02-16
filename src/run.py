from lexer import Lexer
from Parser import Parser
from Context import Context
from GlobalTable import global_symbol_table
from Types import Number
from Interpreter import BuiltinFunction, Interpreter
from Node import *
from Error import *

global_symbol_table.set_val("nil", Number.nil)
global_symbol_table.set_val("true", Number.true)
global_symbol_table.set_val("false", Number.false)
global_symbol_table.set_val("print", BuiltinFunction.print)
global_symbol_table.set_val("append", BuiltinFunction.append)
global_symbol_table.set_val("run", BuiltinFunction.run)
global_symbol_table.set_val("length", BuiltinFunction.length)

def check_for_errors(payload):
    if isinstance(payload, Error):
        return payload
    if isinstance(payload, ListNode):
        for node in payload.element_nodes:
            if isinstance(node, Error):
                return node
    return None

def run(text, fn):
    #print("---------- RUNNING ----------")
    lexer = Lexer(text, fn)
    tokens, error = lexer.make_tokens()

    if error is not None:
        return (None, error)

    # Generate AST
    parser = Parser(tokens)
    nodes = parser.parse()

    #print(f"CHECKING {nodes.as_string()}")
    parse_check = check_for_errors(nodes)
    if parse_check is not None:
        return parse_check

    # Run program
    interpreter = Interpreter()
    ctx = Context("<program>")
    ctx.symbolTable = global_symbol_table
    result = interpreter.visit(nodes, ctx)

    return result

# XXX: Converge Error return value and result value into one value. Basically so that parser parser.parse() returns only one value and that value is either a return or just an error.

## BUG - KNOWN ##
#  Error handling for non recognized keywords/variables is broken
#  Last I checked arithmetic stopped working when there was no spaces between the characters
#  Binary operations with unary nodes do not work, the unary nodes must be mistaken for multiple operators in one operation

# TODO:
# When an array is declared the types stored in the array must also be included in the type declaration
# Update and add tests
#    - Things like tests for variable type checks (ex: a:Int = "test" should return an error)
#    - Add test for checking if returns work properly, like making sure statements after return don't run and stuff
