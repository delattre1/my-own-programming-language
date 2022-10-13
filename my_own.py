# Credits to https://youtu.be/Eythq9848Fg
# And also:  https://ruslanspivak.com/lsbasi-part1/
# Extremely helpfull to build the compiler

import string
from classes.node    import *
from classes.error   import *
from classes.number  import Number
from classes.runtime import RuntimeResult


DIGITS  = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

### POSITION ###

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx  = idx
        self.ln   = ln
        self.col  = col
        self.fn   = fn
        self.ftxt = ftxt

    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1
        
        if current_char == '\n':
            self.ln  =+ 1
            self.col = 0
        
        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

### TOKENS ###

TT_EOF         = 'EOF'
TT_INT         = 'INT'
TT_FLOAT       = 'FLOAT'
TT_PLUS        = 'PLUS'
TT_MINUS       = 'MINUS'
TT_MUL         = 'MUL'
TT_DIV         = 'DIV'
TT_LPAREN      = 'LPAREN'
TT_POW         = 'POW'
TT_RPAREN      = 'RPAREN'

TT_EQ          = 'EQ'
TT_IDENTIFIER  = 'IDENTIFIER'
TT_KEYWORD     = 'KEYWORD'

# Logical Operators
TT_EE  = 'EE'
TT_NE  = 'NE'
TT_LT  = 'LT'
TT_GT  = 'GT'
TT_LTE = 'LTE'
TT_GTE = 'GTE'

KEYWORDS = ['VAR', 'AND', 'OR', 'NOT']

class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None) -> None:
        self.type  = type_
        self.value = value

        if pos_start: 
            self.pos_start = pos_start.copy()
            self.pos_end   = pos_start.copy()
            self.pos_end.advance()

        if pos_end: self.pos_end = pos_end.copy()

    def matches(self, type_, value):
        return self.type == type_ and self.value == value

    def __repr__(self):
        if self.value : return f'{self.type}:{self.value}'
        return f'{self.type}'


### LEXER ###

class Lexer:
    def __init__(self, fn, text):
        self.fn   = fn
        self.text = text
        self.pos  = Position(-1, 0, -1, fn, text) 
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_number(self):
        num_str = ''
        dot_count = 0 
        pos_start = self.pos.copy()

        while (self.current_char != None and self.current_char in (DIGITS + '.')):
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char

            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start, self.pos)
        else: 
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)

    def make_identifier(self):
        id_str = ''
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in LETTERS_DIGITS + '_':
            id_str += self.current_char
            self.advance()

        tok_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
        return Token(tok_type, id_str, pos_start, self.pos)
    
    def make_not_equals(self):
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            return Token(TT_NE, pos_start=pos_start, pos_end=self.pos), None
        
        self.advance()
        return None, ExpectedCharError(pos_start, self.pos, "'=' (after '!')")

    def make_equals(self):
        tok_type = TT_EQ
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_EE
        
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_less_than(self):
        tok_type = TT_LT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_LTE
        
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_greater_than(self):
        tok_type = TT_GT
        pos_start = self.pos.copy()
        self.advance()

        if self.current_char == '=':
            self.advance()
            tok_type = TT_GTE
        
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)


    def make_tokens(self):
        tokens = []

        #import pdb; pdb.set_trace()

        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()

            elif self.current_char in DIGITS:
                tokens.append(self.make_number())

            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())

            elif self.current_char == '+':
                token = Token(TT_PLUS, pos_start=self.pos)
                tokens.append(token)
                self.advance()

            elif self.current_char == '-':
                token = Token(TT_MINUS, pos_start=self.pos)
                tokens.append(token)
                self.advance()

            elif self.current_char == '*':
                token = Token(TT_MUL, pos_start=self.pos)
                tokens.append(token)
                self.advance()

            elif self.current_char == '/':
                token = Token(TT_DIV, pos_start=self.pos)
                tokens.append(token)
                self.advance()

            elif self.current_char == '^':
                token = Token(TT_POW, pos_start=self.pos)
                tokens.append(token)
                self.advance()

            elif self.current_char == '(':
                token = Token(TT_LPAREN, pos_start=self.pos)
                tokens.append(token)
                self.advance()

            elif self.current_char == ')':
                token = Token(TT_RPAREN, pos_start=self.pos)
                tokens.append(token)
                self.advance()

            elif self.current_char == '!':
                tok, error = self.make_not_equals()
                if error: return [], error
                tokens.append(tok)

            elif self.current_char == '=':
                tokens.append(self.make_equals())

            elif self.current_char == '<':
                tokens.append(self.make_less_than())

            elif self.current_char == '>':
                tokens.append(self.make_greater_than())

            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                tokens = []
                return tokens, IllegalCharError(pos_start, self.pos, f'"{char}"')
        
        # Indicar fim de arquivo
        token = Token(TT_EOF, pos_start=self.pos)
        tokens.append(token)
        return tokens, None

### PARSE RESULT ###

class ParseResult:
    def __init__(self):
        self.error, self.node = None, None
        self.advance_count = 0

    def register_advancement(self):
        self.advance_count += 1
    
    def register(self, res):
        self.advance_count += res.advance_count
        if res.error: self.error = res.error
        return res.node
        
    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.advance_count == 0:
            self.error = error
        return self


### PARSER ###

class Parser:
    def __init__(self, tokens):
        self.tokens  = tokens
        self.tok_idx = -1
        self.advance()

    def parse(self):
        result = self.expression()
        if not result.error and self.current_tok.type != TT_EOF:
            error_msg = "Expected '+', '-', '*', '/' or '^'"
            return result.failure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start, 
                        self.current_tok.pos_end, 
                        error_msg)
                    )
        return result

    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_INT, TT_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        elif tok.type == TT_IDENTIFIER:
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))
        
        elif tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            expression = res.register(self.expression())
            if res.error: return res
            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expression)
            else:
                error_msg = "Expected ')'" 
                return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        error_msg
                    ))

        error_msg = "Expected int, float, identifier, '+', '-', or '('"
        return res.failure(InvalidSyntaxError(tok.pos_start, tok.pos_end, error_msg))

    def power(self):
        return self.bin_op(self.atom, (TT_POW, ), self.factor) 

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def arith_expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def comp_expr(self):
        res = ParseResult()
        if self.current_tok.matches(TT_KEYWORD, 'NOT'):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()

            node = res.register(self.comp_expr())
            if res.error: return res
            return res.success(UnaryOpNode(op_tok, node))

        node = res.register(self.bin_op(self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_LTE, TT_GT, TT_GTE)))
        if res.error:
            error_msg = "Expected int, float, identifier, '+', '-', '(' or 'NOT'"
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start,
                self.current_tok.pos_end, 
                error_msg
            ))
        
        return res.success(node)



    def expression(self):
        res = ParseResult()
        if self.current_tok.matches(TT_KEYWORD, 'VAR'):
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_IDENTIFIER:
                error_msg = "Expected identifier"
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, error_msg))

            var_name = self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_EQ:
                error_msg = "Expected '='"
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, error_msg))

            res.register_advancement()
            self.advance()
            expression = res.register(self.expression())
            if res.error: return res
            return res.success(VarAssignNode(var_name, expression))

        node = res.register(self.bin_op(self.comp_expr, ((TT_KEYWORD, 'AND'), (TT_KEYWORD, 'OR'))))
        if res.error: 
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start,
                self.current_tok.pos_end,
                "Expected 'VAR', int, float, identifier, '+', '-' or '('"
                ))

        return res.success(node)

    def bin_op(self, func_a, ops, func_b=None):
        if not func_b: func_b = func_a

        res  = ParseResult()
        left = res.register(func_a()) 
        if res.error: return res
        while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            if res.error: return res
            right  = res.register(func_b())
            if res.error: return res
            left   = BinOpNode(left, op_tok, right)
        
        return res.success(left)


### CONTEXT ###

class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None

### SYMBOLTABLE ###

class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.parent = None

    def get(self, name):
        value = self.symbols.get(name, None)
        if value == None and self.parent:
            return self.parent.get(name)
        return value

    def set(self, name, value):
        self.symbols[name] = value

    def remove(self, name):
        del self.symbols[name]


### INTERPRETER ###

class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}' #visit_BinOpNOde or visitNumberNode
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        exception_msg = f'No visit_{type(node).__name__} method defined'
        raise Exception(exception_msg)
        
    def visit_NumberNode(self, node, context):
        number = Number(node.tok.value).set_context(context)
        number = number.set_pos(node.pos_start, node.pos_end)
        return RuntimeResult().success(number)

    def visit_VarAccessNode(self, node, context):
        res = RuntimeResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)

        if not value:
            error_msg = f"'{var_name}' is not defined"
            return None, RuntimeError(
                            node.pos_start, 
                            node.pos_end,
                            error_msg, 
                            self.context
                        )
        value = value.copy().set_pos(node.pos_start, node.pos_end)
        return res.success(value)

    def visit_VarAssignNode(self, node, context):
        res = RuntimeResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context))
        if res.error: return res
        
        context.symbol_table.set(var_name, value)
        return res.success(value)

    def visit_BinOpNode(self, node, context):
        res = RuntimeResult()
        left  = res.register(self.visit(node.left_node, context))
        if res.error: return res
        right = res.register(self.visit(node.right_node, context))
        if res.error: return res

        op     = node.op_tok.type
        
        if   op == TT_PLUS:
            result, error = left.added_to(right)
        elif op == TT_MINUS:
            result, error = left.subtracted_by(right)
        elif op == TT_MUL:
            result, error = left.multiplied_by(right)
        elif op == TT_DIV:
            result, error = left.divided_by(right)
        elif op == TT_POW:
            result, error = left.powed_by(right)
        #Logical Operators
        elif op == TT_EE:
            result, error = left.get_comp_eq(right)
        elif op == TT_NE:
            result, error = left.get_comp_ne(right)
        elif op == TT_LT:
            result, error = left.get_comp_lt(right)
        elif op == TT_LTE:
            result, error = left.get_comp_lte(right)
        elif op == TT_GT:
            result, error = left.get_comp_gt(right)
        elif op == TT_GTE:
            result, error = left.get_comp_gte(right)
        elif node.op_tok.matches(TT_KEYWORD, 'AND'):
            result, error = left.anded_by(right)
        elif node.op_tok.matches(TT_KEYWORD, 'OR'):
            result, error = left.ored_by(right)



        if error: return res.failure(error)
        else:
            result = result.set_pos(node.pos_start, node.pos_end)
            return res.success(result)
    
    def visit_UnaryOpNode(self, node, context):
        res = RuntimeResult()

        number = res.register(self.visit(node.node, context))
        if res.error: return res

        error = None

        if node.op_tok.type == TT_MINUS:
            number, error = number.multiplied_by(Number(-1))
        elif node.op_tok.matches(TT_KEYWORD, 'NOT'):
            number, error = number.notted()

        if error: return res.failure(error)
        else:
            number = number.set_pos(node.pos_start, node.pos_end) 
            return res.success(number)

### RUN ###

global_symbol_table = SymbolTable()
global_symbol_table.set("null",  Number(0))
global_symbol_table.set("TRUE",  Number(1))
global_symbol_table.set("FALSE", Number(0))

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
