import string
DIGITS  = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

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

# Logical and Comparison Operators
TT_EE  = 'EE'
TT_NE  = 'NE'
TT_LT  = 'LT'
TT_GT  = 'GT'
TT_LTE = 'LTE'
TT_GTE = 'GTE'

KEYWORDS = ['VAR', 'AND', 'OR', 'NOT', 'IF', 'THEN', 'ELIF', 'ELSE', 'FOR', 'TO', 'STEP', 'WHILE']


