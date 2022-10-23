## Grammar
```
expr       : KEYWORD:VAR IDENTIFIER EQ expr
           : comp-expr ((KEYWORD:AND|KEYWORD:OR) comp-expr)*

comp-expr  : NOT comp-expr
           : arith-expr ((EE|TL|GT|LTE|GTE) arith-expr)*

arith-expr : term ((PLUS|MINUS) term)*

term   : factor ((MUL | DIV) factor)*

factor : (PLUS | MINUS) factor
       : power

power  : call (POW factor)*

call   : atom (LPAREN (expr (COMMA expr)*)? RPAREN)?

atom   : INT | FLOAT | STRING | IDENTIFIER
       : LPAREN expr RPAREN
       : if-expr
       : for-expr
       : while-expr
       : func-def

if-expr : KEYWORD:IF expr KEYWORD:THEN expr
        : (KEYWORD:ELIF expr KEYWORD:THEN expr)*
        : (KEYWORD:ELSE expr)?


for-expr : KEYWORD:FOR IDENTIFIER EQ expr KEYWORD: TO expr
         : (KEYWORD:STEP expr)? KEYWORD:THEN expr

while-expr : KEYWORD:WHILE expr KEYWORD:THEN  expr

func-def   : KEYWORD:FUN IDENTIFIER?
           : LPAREN (IDENTIFIER (COMMA IDENTIFIER)*)? RPAREN
           : ARROW expr


```
