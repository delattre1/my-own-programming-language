from constants     import *
from classes.error import *
from classes.node  import *
from classes.number  import Number
from classes.runtime import RuntimeResult

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

    def visit_IfNode(self, node, context):
        res = RuntimeResult()
        
        for condition, expr in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.error: return res

            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.error: return res
                return res.success(expr_value)

        if node.else_case:
            else_value = res.register(self.visit(node.else_case, context))
            if res.error: return res
            return res.success(else_value)

        return res.success(None)


    def visit_ForNode(self, node, context):
        res = RuntimeResult()

        start_value = res.register(self.visit(node.start_value_node, context))
        if res.error: return res

        end_value = res.register(self.visit(node.end_value_node, context))
        if res.error: return res

        if node.step_value_node:
            step_value = res.register(self.visit(node.step_value_node, context))
            if res.error: return res
        else: step_value = Number(1)

        for i in range(start_value.value, end_value.value, step_value.value):
            # Adding the idx to the symbol table so It can be accessed inside the loop
            context.symbol_table.set(node.var_name_tok.value, Number(i))
            res.register(self.visit(node.body_node, context))
            if res.error: return res

        return res.success(None)

    def visit_WhileNode(self, node, context):
        res = RuntimeResult()

        condition = res.register(self.visit(node.condition_node, context))
        if res.error: return res

        while condition.is_true():
            res.register(self.visit(node.body_node, context))
            if res.error: return res

            condition = res.register(self.visit(node.condition_node, context))
            if res.error: return res

        return res.success(None)

    def visit_FuncDefNode(self, node, context):
        res = RuntimeResult()

        condition = res.register(self.visit(node.condition_node, context))
        if res.error: return res

        while condition.is_true():
            res.register(self.visit(node.body_node, context))
            if res.error: return res

            condition = res.register(self.visit(node.condition_node, context))
            if res.error: return res

        return res.success(None)


