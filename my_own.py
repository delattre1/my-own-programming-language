# Credits to https://youtu.be/Eythq9848Fg
# And also:  https://ruslanspivak.com/lsbasi-part1/
# Extremely helpfull to build the compiler


import string
DIGITS  = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS


def string_with_arrows(text, pos_start, pos_end):
    result = ''

    # Calculate indices
    idx_start = max(text.rfind('\n', 0, pos_start.idx), 0)
    idx_end = text.find('\n', idx_start + 1)
    if idx_end < 0: idx_end = len(text)
    
    # Generate each line
    line_count = pos_end.ln - pos_start.ln + 1
    for i in range(line_count):
        # Calculate line columns
        line = text[idx_start:idx_end]
        col_start = pos_start.col if i == 0 else 0
        col_end = pos_end.col if i == line_count - 1 else len(line) - 1

        # Append to result
        result += line + '\n'
        result += ' ' * (col_start + 1) + '^' * (col_end - col_start)

        # Re-calculate indices
        idx_start = idx_end
        idx_end = text.find('\n', idx_start + 1)
        if idx_end < 0: idx_end = len(text)

    return result.replace('\t', '')

### ERRORS ###


class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start  = pos_start
        self.pos_end    = pos_end
        self.error_name = error_name
        self.details    = details

    def as_string(self):
        result  = f'{self.error_name}: {self.details}\n'
        result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
        result += f'\n\n {string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)}'
        return result

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Invalid Syntax', details)

class RuntimeError(Error):
    def __init__(self, pos_start, pos_end, details, context):
        super().__init__(pos_start, pos_end, 'Runtime Error', details)
        self.context = context
    
    def as_string(self):
        result  = self.generate_traceback()
        result += f'{self.error_name}: {self.details}\n'
        result += f'\n\n {string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)}'
        return result

    def generate_traceback(self):
        result = ''
        pos = self.pos_start
        context = self.context

        while context:
            result = f'File {pos.fn}, line {str(pos.ln + 1)}, in {context.display_name}\n {result}'
            pos = context.parent_entry_pos
            context = context.parent
        
        traceback_msg = f'Traceback (most recent call last):\n{result}'
        return traceback_msg

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

KEYWORDS = ['VAR']

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

            elif self.current_char == '=':
                token = Token(TT_EQ, pos_start=self.pos)
                tokens.append(token)
                self.advance()

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


### NODES ###

class NumberNode:
    def __init__(self, tok):
        self.tok = tok

        self.pos_start = self.tok.pos_start
        self.pos_end   = self.tok.pos_end

    def __repr__(self):
        return f'{self.tok}'


class VarAccessNode:
    def __init__(self, var_name_tok):
        self.var_name_tok = var_name_tok

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end   = self.var_name_tok.pos_end

class VarAssignNode:
    def __init__(self, var_name_tok, value_node):
        self.var_name_tok = var_name_tok
        self.value_node   = value_node

        self.pos_start = self.var_name_tok.pos_start
        self.pos_end   = self.value_node.pos_end


class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):
        self.left_node  = left_node
        self.op_tok     = op_tok
        self.right_node = right_node

        self.pos_start = self.left_node.pos_start
        self.pos_end   = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node   = node

        self.pos_start = self.op_tok.pos_start
        self.pos_end   = self.node.pos_end
    
    def __repr__(self):
        return f'({self.op_tok}, {self.node})'


### PARSE RESULT ###

class ParseResult:
    def __init__(self):
        self.error, self.node = None, None
    
    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error: self.error = res.error
            return res.node
        
        return res

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
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
            res.register(self.advance())
            return res.success(NumberNode(tok))

        elif tok.type == TT_IDENTIFIER:
            res.register(self.advance())
            return res.success(VarAccessNode(tok))
        
        elif tok.type == TT_LPAREN:
            res.register(self.advance())
            expression = res.register(self.expression())
            if res.error: return res
            if self.current_tok.type == TT_RPAREN:
                res.register(self.advance())
                return res.success(expression)
            else:
                error_msg = "Expected ')'" 
                return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        error_msg
                    ))

        error_msg = "Expected int or float, '+', '-', or '('"
        return res.failure(InvalidSyntaxError(tok.pos_start, tok.pos_end, error_msg))

    def power(self):
        return self.bin_op(self.atom, (TT_POW, ), self.factor) 

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def expression(self):
        res = ParseResult()
        if self.current_tok.matches(TT_KEYWORD, 'VAR'):
            res.register(self.advance())

            if self.current_tok.type != TT_IDENTIFIER:
                error_msg = "Expected identifier"
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, error_msg))

            var_name = self.current_tok
            res.register(self.advance())

            if self.current_tok.type != TT_EQ:
                error_msg = "Expected '='"
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end, error_msg))

            res.register(self.advance())
            expression = res.register(self.expression())
            if res.error: return res
            return res.success(VarAssignNode(var_name, expression))

        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

         



        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def bin_op(self, func_a, ops, func_b=None):
        if not func_b: func_b = func_a

        res  = ParseResult()
        left = res.register(func_a()) 
        if res.error: return res

        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            if res.error: return res
            right  = res.register(func_b())
            if res.error: return res
            left   = BinOpNode(left, op_tok, right)
        
        return res.success(left)


### RUNTIME RESULT ###

class RuntimeResult:
    def __init__(self):
        self.value, self.error = None, None

    def register(self, res):
        if res.error: self.error = res.error
        return res.value
    
    def success(self, value):
        self.value = value
        return self

    def failure(self, error):
        self.error = error
        return self

### VALUES ###

class Number:
    def __init__(self, value):
        self.value = value
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end   = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
    
    def subtracted_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
    
    def multiplied_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
    
    def divided_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                error_msg = 'Division by zero'
                return None, RuntimeError(
                                other.pos_start, 
                                other.pos_end,
                                error_msg, 
                                self.context
                            )

            return Number(self.value / other.value).set_context(self.context), None

    def powed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None

    def __repr__(self):
        return str(self.value)

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

        if error: return res.failure(error)
        else:
            number = number.set_pos(node.pos_start, node.pos_end) 
            return res.success(number)



### RUN ###

global_symbol_table = SymbolTable()
global_symbol_table.set("null", Number(0))

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










