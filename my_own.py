# Credits to https://youtu.be/Eythq9848Fg
# Extremely helpfull to build the compiler

CTE_NUM     = '0123456789'
TT_INT      = 'TT_INT'
TT_FLOAT    = 'TT_FLOAT'
TT_PLUS     = 'TT_PLUS'
TT_MINUS    = 'TT_MINUS'
TT_MUL      = 'TT_MUL'
TT_DIV      = 'TT_DIV'
TT_LPAREN   = 'TT_LPAREN'
TT_RPAREN   = 'TT_RPAREN'
TT_EOF      = 'TT_EOF'

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
        return result

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)


### POSITION ###

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx  = idx
        self.ln   = ln
        self.col  = col
        self.fn   = fn
        self.ftxt = ftxt

    def advance(self, current_char):
        self.idx += 1
        self.col += 1
        
        if current_char == '\n':
            self.ln  =+ 1
            self.col = 0
        
        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)



### TOKENS ###

class Token:
    def __init__(self, type_, value=None) -> None:
        self.type  = type_
        self.value = value

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
        while (self.current_char != None and self.current_char in (CTE_NUM + '.')):
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char

            self.advance()

            if dot_count == 0:
                return Token(TT_INT, int(num_str))
            else: 
                return Token(TT_FLOAT, float(num_str))

    def make_tokens(self):
        tokens = []

        #import pdb; pdb.set_trace()

        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()

            elif self.current_char in CTE_NUM:
                tokens.append(self.make_number())

            elif self.current_char == '+':
                token = Token(TT_PLUS)
                tokens.append(token)
                self.advance()

            elif self.current_char == '-':
                token = Token(TT_MINUS)
                tokens.append(token)
                self.advance()

            elif self.current_char == '*':
                token = Token(TT_MUL)
                tokens.append(token)
                self.advance()

            elif self.current_char == '/':
                token = Token(TT_DIV)
                tokens.append(token)
                self.advance()

            elif self.current_char == '(':
                token = Token(TT_LPAREN)
                tokens.append(token)
                self.advance()

            elif self.current_char == ')':
                token = Token(TT_RPAREN)
                tokens.append(token)
                self.advance()

            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                tokens = []
                return tokens, IllegalCharError(pos_start, self.pos, f'"{char}"')
        
        # Indicar fim de arquivo
        token = Token(TT_EOF)
        tokens.append(token)
        return tokens, None


### RUN ###

def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    return tokens, error









