# Credits to https://youtu.be/Eythq9848Fg
# And also:  https://ruslanspivak.com/lsbasi-part1/
# Extremely helpfull to build the compiler

from utils import Context, SymbolTable
from classes.lexer  import Lexer
from classes.parser import Parser
from classes.interpreter import Interpreter, Number, BuiltInFunction

### RUN ###

global_symbol_table = SymbolTable()
global_symbol_table.set("null",  Number.null)
global_symbol_table.set("True",  Number.true)
global_symbol_table.set("False", Number.false)
global_symbol_table.set("print",     BuiltInFunction.print)
global_symbol_table.set("print_ret", BuiltInFunction.print_ret)
global_symbol_table.set("input",     BuiltInFunction.input)
global_symbol_table.set("input_int", BuiltInFunction.input_int)

def run(fn, text):
    # Generate Tokens
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error: return None, error
    
    #Generate AST (Abstract Syntax Three)
    parser = Parser(tokens)
    ast    = parser.parse()
    if ast.error: return None, ast.error

    # Run program 
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    res = interpreter.visit(ast.node, context)

    return res.value, res.error
