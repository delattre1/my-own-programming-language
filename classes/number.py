from classes.runtime import RuntimeResult
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
        super()__init__()
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


class Function(Value):
    def __init__(self, name, body_node, arg_names):
        super()__init__()
        self.name = name or '<anonymous>'
        self.body_node = body_node
        self.arg_names = arg_names

    def execute(self, args):
        res = RuntimeResult()
        interpreter = Interpreter()
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)

