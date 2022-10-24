from utils import Context, SymbolTable
from constants     import *
from classes.error import *
from classes.node  import *
from classes.runtime import RuntimeResult


### VALUE is HERE to avoid circular import with INTERPRETER

### VALUES ###

class Value:
    def __init__(self):
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end   = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def illegal_operation(self, other=None):
        if not other: other = self
        return RuntimeError(
            self.pos_start, 
            self.pos_end,
            'Illegal operation', 
            self.context
        )

    def added_to(self, other):
        return None, self.illegal_operation(other)

    def subtracted_by(self, other):
        return None, self.illegal_operation(other)

    def multiplied_by(self, other):
        return None, self.illegal_operation(other)

    def divided_by(self, other):
        return None, self.illegal_operation(other)

    def powed_by(self, other):
        return None, self.illegal_operation(other)

    def get_comp_eq(self, other):
        return None, self.illegal_operation(other)

    def get_comp_ne(self, other):
        return None, self.illegal_operation(other)

    def get_comp_lt(self, other):
        return None, self.illegal_operation(other)

    def get_comp_lte(self, other):
        return None, self.illegal_operation(other)

    def get_comp_gt(self, other):
        return None, self.illegal_operation(other)

    def get_comp_gte(self, other):
        return None, self.illegal_operation(other)

    def anded_by(self, other):
        return None, self.illegal_operation(other)

    def ored_by(self, other):
        return None, self.illegal_operation(other)

    def notted(self):
        return None, self.illegal_operation()

    def copy(self):
        raise Exception('No copy method defined')

    def is_true(self):
        return False

class Number(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        else: return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def subtracted_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        else: return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
    def multiplied_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        else: return None, Value.illegal_operation(self.pos_start, other.pos_end)
    
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
        else: return None, Value.illegal_operation(self.pos_start, other.pos_end)

    def powed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value ** other.value).set_context(self.context), None
        else: return None, Value.illegal_operation(self.pos_start, other.pos_end)

    # Logical Operators
    def get_comp_eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else: return None, Value.illegal_operation(self.pos_start, other.pos_end)

    def get_comp_ne(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(self.context), None
        else: return None, Value.illegal_operation(self.pos_start, other.pos_end)

    def get_comp_lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <  other.value)).set_context(self.context), None
        else: return None, Value.illegal_operation(self.pos_start, other.pos_end)

    def get_comp_lte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(self.context), None
        else: return None, Value.illegal_operation(self.pos_start, other.pos_end)

    def get_comp_gt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >  other.value)).set_context(self.context), None
        else: return None, Value.illegal_operation(self.pos_start, other.pos_end)

    def get_comp_gte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(self.context), None
        else: return None, Value.illegal_operation(self.pos_start, other.pos_end)

    def anded_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value and other.value)).set_context(self.context), None
        else: return None, Value.illegal_operation(self.pos_start, other.pos_end)

    def ored_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value or  other.value)).set_context(self.context), None
        else: return None, Value.illegal_operation(self.pos_start, other.pos_end)
        
    def notted(self):
        return Number(1 if self.value == 0 else 0).set_context(self.context), None

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def is_true(self):
        return self.value != 0

    def __repr__(self):
        return str(self.value)

Number.null  = Number(0)
Number.false = Number(0)
Number.true  = Number(1)



### FUNCTIONS ###
class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name or '<anonymous>'

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context

    def check_args(self, arg_names, args):
        res = RuntimeResult()
        expected_args_size = len(arg_names)

        if len(args) != expected_args_size:
            return res.failure(RuntimeError(
                self.pos_start, self.pos_end,
                f"'{self.name}' expected {expected_args_size} args, but received {len(args)}",
                self.context
                ))

        return res.success(None)

    def populate_args(self, arg_names, args, exec_context):
        '''Populate the symbol_table'''
        for idx, arg_value in enumerate(args):
            arg_name = arg_names[idx]
            arg_value.set_context(exec_context)
            exec_context.symbol_table.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_context):
        res = RuntimeResult()
        res.register(self.check_args(arg_names, args))
        if res.error: return res
        self.populate_args(arg_names, args, exec_context)
        return res.success(None)


class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)

    def execute(self, args):
        '''
        Create separate execute methods for 
        each builtInFunction. Ex: 
            If name function is print, we will call execute_print()
        '''
        res = RuntimeResult()
        exec_context = self.generate_new_context()
        
        
        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit_method)

        res.register(self.check_and_populate_args(method.arg_names, args, exec_context))
        if res.error: return res

        return_value = res.register(method(exec_context))
        if res.error: return res
        return res.success(return_value)

    def no_visit_method(self, node, context):
        raise Exception(f'No execute_{self.name} method defined')

    def copy(self):
        copy = BuiltInFunction(self.name)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return f'<built-in function {self.name}>'

    ## Creating the built-in functions

    def execute_print(self, exec_context):
        print(str(exec_context.symbol_table.get('value')))
        return RuntimeResult().success(Number.null)
    execute_print.arg_names = ['value']

    def execute_print_ret(self, exec_context):
        str_ = String(str(exec_context.symbol_table.get('value')))
        return RuntimeResult().success(str_)
    execute_print_ret.arg_names = ['value']
    
    def execute_input(self, exec_context):
        text = input()
        return RuntimeResult().success(String(text))
    execute_input.arg_names = []

    def execute_input_int(self, exec_context):
        text = input()
        while True:
            try:
                number = int(text)
                break
            except ValueError:
                    print(f"'{text}' must be an integer. Try again!")
        return RuntimeResult().success(Number(number))


BuiltInFunction.print     = BuiltInFunction("print")
BuiltInFunction.print_ret = BuiltInFunction("print_ret")
BuiltInFunction.input     = BuiltInFunction("input")
BuiltInFunction.input_int = BuiltInFunction("input_int")


class Function(BaseFunction):
    def __init__(self, name, body_node, arg_names):
        super().__init__(name)
        self.body_node = body_node
        self.arg_names = arg_names

    def execute(self, args):
        res = RuntimeResult()
        interpreter = Interpreter()
        exec_context = self.generate_new_context()

        res.register(self.check_and_populate_args(self.arg_names, args, exec_context))
        if res.error: return res

        value = res.register(interpreter.visit(self.body_node, exec_context))
        if res.error: return res
        return res.success(value)

    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return f'<function {self.name}>'


class String(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_to(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)
    
    def multiplied_by(self, other):
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def is_true(self):
        return len(self.value) > 0

    def get_comp_eq(self, other):
        if isinstance(other, String):
            return Number(int(self.value == other.value)).set_context(self.context), None
        else: return None, Value.illegal_operation(self.pos_start, other.pos_end)

    def copy(self):
        copy = String(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy
    
    def __str__(self):
        return self.value

    def __repr__(self):
        return f'"{self.value}"'

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
                            context
                        )
        value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
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

        func_name = node.var_name_tok.value if node.var_name_tok else None
        arg_names = [arg_name.value for arg_name in node.arg_name_toks]
        node_to_call = node.node_to_call
        func_value = Function(func_name, node_to_call, arg_names).set_context(context).set_pos(node.pos_start, node.pos_end)

        #If function has name, add it to the symbol_table
        if node.var_name_tok:
            context.symbol_table.set(func_name, func_value)
        return res.success(func_value)


    def visit_CallNode(self, node, context):
        res = RuntimeResult()
        args = []

        value_to_call = res.register(self.visit(node.node_to_call, context))
        if res.error: return res
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node, context)))
            if res.error: return res

        return_value = res.register(value_to_call.execute(args))
        if res.error: return res
        return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
        return res.success(return_value)

    def visit_StringNode(self, node, context):
        return RuntimeResult().success(
            String(node.tok.value).set_context(context).set_pos(node.pos_start,node.pos_end)
        )

