from lexer import Lexer
from Parser import Parser
from Context import Context
from GlobalTable import global_symbol_table
from Types import Number
from Interpreter import BuiltinFunction, Interpreter
from Node import *
from Error import *
from Compiler import Compiler

global_symbol_table.set_val("nil", Number.nil)
global_symbol_table.set_val("true", Number.true)
global_symbol_table.set_val("false", Number.false)
global_symbol_table.set_val("print", BuiltinFunction.print)
global_symbol_table.set_val("append", BuiltinFunction.append)
global_symbol_table.set_val("run", BuiltinFunction.run)
global_symbol_table.set_val("length", BuiltinFunction.length)
global_symbol_table.set_val("remove", BuiltinFunction.remove)
global_symbol_table.set_val("removeLast", BuiltinFunction.removeLast)

def check_for_errors(payload):
    if isinstance(payload, Error):
        return payload
    if isinstance(payload, ListNode):
        for node in payload.element_nodes:
            if isinstance(node, Error):
                return node
    return None

def run(text, fn):
    lexer = Lexer(text, fn)
    tokens, error = lexer.make_tokens()

    if error is not None:
        return error

    # Generate AST
    parser = Parser(tokens)
    nodes = parser.parse()

    parse_check = check_for_errors(nodes)
    if parse_check is not None:
        return parse_check

    # Run program
    #interpreter = Interpreter()
    #ctx = Context("<program>")
    #ctx.symbolTable = global_symbol_table
    #result = interpreter.visit(nodes, ctx)

    compiler = Compiler()
    ctx = Context("<program>")
    ctx.symbolTable = global_symbol_table
    result = compiler.compile(nodes, ctx)

    # NOTE: temporary conditional check here, should eventually create an LLVM binding for the Error types
    if not isinstance(result, Error):
        result = compiler.compile_ir_and_output(compiler.module)

    return result

# TODO:
# Add for in loops (ex: for token in tokens) type thing
