from constants     import *
from classes.error import *
from classes.node  import *


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

    def func_def(self):
        res = ParseResult()

        # Check 'FOR' KEYWORD
        if not self.current_tok.matches(TT_KEYWORD, 'FUN'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, 
                self.current_tok.pos_end,
                f"Expected 'FUN'"
            ))
        res.register_advancement()
        self.advance()

        # Check identifier
        if self.current_tok.type == TT_IDENTIFIER:
            #Store the function name
            var_name_tok = self.current_tok
            res.register_advancement()
            self.advance()
    
            if self.current_tok.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, 
                    self.current_tok.pos_end,
                    f"Expected '('"
                ))

        else:
            var_name_tok = None
            if self.current_tok.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, 
                    self.current_tok.pos_end,
                    f"Expected identifier or '('"
                ))
        res.register_advancement()
        self.advance()
        arg_name_toks = []

        # Check func arguments
        if self.current_tok.type == TT_IDENTIFIER:
            #Store the arg name
            arg_name_toks.append(self.current_tok)
            res.register_advancement()
            self.advance()

            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()

                # Check func arguments
                if self.current_tok.type != TT_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, 
                        self.current_tok.pos_end,
                        f"Expected identifier"
                    ))
                #Store the arg name
                arg_name_toks.append(self.current_tok)
                res.register_advancement()
                self.advance()
                
            # Check RPAREN (case when func has args)
            if self.current_tok.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, 
                    self.current_tok.pos_end,
                    f"Expected ')' or ','"
                ))

        # Check RPAREN (case func doesnt have args)
        else:
            if self.current_tok.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, 
                    self.current_tok.pos_end,
                    f"Expected ')' or 'identifier'"
                ))

        res.register_advancement()
        self.advance()

        # Check arrow
        if self.current_tok.type != TT_ARROW:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, 
                self.current_tok.pos_end,
                f"Expected ->"
            ))
        res.register_advancement()
        self.advance()

        body_node = res.register(self.expression())
        if res.error: return res
        return res.success(FuncDefNode(var_name_tok, 
                                       arg_name_toks, 
                                       body_node))




    def for_expr(self):
        res = ParseResult()

        # Check 'FOR' KEYWORD
        if not self.current_tok.matches(TT_KEYWORD, 'FOR'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, 
                self.current_tok.pos_end,
                f"Expected 'FOR'"
            ))
        res.register_advancement()
        self.advance()

        # Check identifier
        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, 
                self.current_tok.pos_end,
                f"Expected identifier"
            ))

        #Store the variable name
        var_name = self.current_tok
        res.register_advancement()
        self.advance()
        # Check '='
        if self.current_tok.type != TT_EQ:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, 
                self.current_tok.pos_end,
                f"Expected '='"
            ))
        res.register_advancement()
        self.advance()
        
        # Assign the result of the expression as the start_value of the for loop
        start_value = res.register(self.expression())
        if res.error: return res
        
        # Check 'TO' keyword
        if not self.current_tok.matches(TT_KEYWORD, 'TO'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, 
                self.current_tok.pos_end,
                f"Expected 'TO'"
            ))
        res.register_advancement()
        self.advance()

        # Assign the result of the expression as the end_value of the for loop
        end_value = res.register(self.expression())
        if res.error: return res
        # Check if a custom STEP value is present
        if self.current_tok.matches(TT_KEYWORD, 'STEP'):
            res.register_advancement()
            self.advance()

            step_value = res.register(self.expression())
            if res.error: return res
        else:
            step_value = None

        # Check 'THEN' keyword
        if not self.current_tok.matches(TT_KEYWORD, 'THEN'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, 
                self.current_tok.pos_end,
                f"Expected 'THEN'"
            ))
        res.register_advancement()
        self.advance()

        # 
        body = res.register(self.expression())
        if res.error: return res
        return res.success(ForNode(var_name, 
                                   start_value, 
                                   end_value, 
                                   step_value, 
                                   body))

    def while_expr(self):
        res = ParseResult()

        # Check 'WHILE' KEYWORD
        if not self.current_tok.matches(TT_KEYWORD, 'WHILE'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, 
                self.current_tok.pos_end,
                f"Expected 'WHILE'"
            ))
        res.register_advancement()
        self.advance()

        condition = res.register(self.expression())
        if res.error: return res

        # Check 'THEN' keyword
        if not self.current_tok.matches(TT_KEYWORD, 'THEN'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, 
                self.current_tok.pos_end,
                f"Expected 'THEN'"
            ))
        res.register_advancement()
        self.advance()

        # 
        body = res.register(self.expression())
        if res.error: return res
        return res.success(WhileNode(condition, body))

    def if_expr(self):
        res = ParseResult()
        cases = []
        else_case = None
        
        # Check IF 
        if not self.current_tok.matches(TT_KEYWORD, 'IF'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, 
                self.current_tok.pos_end,
                f"Expected 'IF'"
            ))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expression())
        if res.error: return res
        
        # Check Then
        if not self.current_tok.matches(TT_KEYWORD, 'THEN'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, 
                self.current_tok.pos_end,
                f"Expected 'THEN'"
            ))

        res.register_advancement()
        self.advance()

        expr = res.register(self.expression())
        if res.error: return res
        cases.append((condition, expr))
        
        # Check multiple ELIF's
        while self.current_tok.matches(TT_KEYWORD, 'ELIF'):
            res.register_advancement()
            self.advance()

            condition = res.register(self.expression())
            if res.error: return res
            
            # Check Then
            if not self.current_tok.matches(TT_KEYWORD, 'THEN'):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, 
                    self.current_tok.pos_end,
                    f"Expected 'THEN'"
                ))

            res.register_advancement()
            self.advance()

            expr = res.register(self.expression())
            if res.error: return res
            cases.append((condition, expr))

        if self.current_tok.matches(TT_KEYWORD, 'ELSE'):
            res.register_advancement()
            self.advance()

            else_case = res.register(self.expression())
            if res.error: return res

        return res.success(IfNode(cases, else_case))


    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_INT, TT_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        elif tok.type == TT_STRING:
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok))

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
        elif tok.matches(TT_KEYWORD, 'IF'):
            if_expr = res.register(self.if_expr())
            if res.error: return res
            return res.success(if_expr)


        elif tok.matches(TT_KEYWORD, 'FOR'):
            for_expr = res.register(self.for_expr())
            if res.error: return res
            return res.success(for_expr)

        elif tok.matches(TT_KEYWORD, 'WHILE'):
            while_expr = res.register(self.while_expr())
            if res.error: return res
            return res.success(while_expr)

        elif tok.matches(TT_KEYWORD, 'FUN'):
            func_def = res.register(self.func_def())
            if res.error: return res
            return res.success(func_def)

        error_msg = "Expected int, float, identifier, '+', '-', '(', 'IF', 'FOR', WHILE', 'FUN'"
        return res.failure(InvalidSyntaxError(tok.pos_start, tok.pos_end, error_msg))

    def power(self):
        return self.bin_op(self.call, (TT_POW, ), self.factor) 

    def call(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error: return res

        arg_nodes = []
        if self.current_tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            
            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
            else:
                # Register function arguments
                expr = res.register(self.expression())
                if res.error: 
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start,
                        self.current_tok.pos_end,
                        "Expected ')', 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-'"))

                arg_nodes.append(expr)

                while self.current_tok.type == TT_COMMA:
                    res.register_advancement()
                    self.advance()

                    expr = res.register(self.expression())
                    if res.error: return res
                    arg_nodes.append(expr)
                    
                # Check RPAREN (case when func has args)
                if self.current_tok.type != TT_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, 
                        self.current_tok.pos_end,
                        f"Expected ')' or ','"
                    ))

                res.register_advancement()
                self.advance()
            return res.success(CallNode(atom, arg_nodes))
        # If there's no parenthesis, dont 'call the function', just pass the value of the atom.
        return res.success(atom)


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
                "Expected 'VAR', int, float, identifier, 'IF', 'FOR', WHILE', 'FUN', '+', '-' or '('"
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
