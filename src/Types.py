from Context import Context
from Error import RuntimeError
from Position import Position
from SymbolTable import SymbolTable

# Type (Supertype for all)
# Number
#   Real?
#   Integer
#      Signed
#         Int8, 16, 32, 64, 128
#      Unsigned
#         UInt8, 16, 32, 64, 128
#      Bool
#   AbstractFloat
#      Float64, 32, 16
# String

class Type:
    def __init__(self, value=None, pos=None, description="AnyType"):
        self.value = value
        self.pos = pos
        self.context = None
        self.description = description

    def set_context(self, ctx):
        self.context = ctx

    def print_self(self):
        return self.value

class Object(Type):
    def __init__(self, name, body_node=None, attr_names=None, attr_types=None):
        self.name = name
        self.body_node = body_node
        self.attr_names = attr_names
        self.context = Context()
        self.attr_types = attr_types
        self.ID = self.name + "_TYPE"
        self.value = self.name
        self.description = self.name

    def generate_new_context(self):
        # Those last two values will probably have to be filled in with
        # real values some day
        new_ctx = Context(self.name, None, Position())
        new_ctx.symbolTable = SymbolTable()
        self.context = new_ctx

    def check_types_match(self, a, b):
        #if not isinstance(a, type(b)):
        if a.ID != b.ID:
            return RuntimeError("Cannot assign type {a.description} to parameter type {b.description}, in object {self.name}, initialization", Position(), self.context)
        return None

    def initialize(self, values):
        self.generate_new_context()
        # check if length of values is same as attr_names
        if len(values) > len(self.attr_names):
            return RuntimeError("Given amount of parameters exceeds object {self.name}'s initialization parameters", Position(), self.context)
        elif len(values) < len(self.attr_names):
            return RuntimeError(f"Given amount of parameters does not meet object {self.name}'s amount of initialization parameters", Position(), self.context)

        for i in range(0, len(values)):
            # check type is same as first attr
            does_match = self.check_types_match(values[i], self.attr_types[i])
            if does_match is not None:
                return does_match
            # populate local symbol table with value
            self.context.symbolTable.set_val(self.attr_names[i], values[i])

        # Need to initialization any functions or variables inside of the body node
        return self

    def print_self(self):
        return f"Object: {self.name}"


class Void:
    def __init__(self, pos=None):
        self.pos = pos
        self.context = None

    def print_self(self):
        return "Void"


class Real(Type):
    def __init__(self, value=None, pos=None):
        super().__init__(value, pos, "Real")

    ### NEED TO ADD CHECK FOR THE TYPE BEING THE SAME AND NOT JUST THE VALUE ###
    def comp_eq(self, other):
        new_num = Number(1 if self.value == other.value else 0)
        new_num.set_context(other.context)
        return new_num

    def comp_ne(self, other):
        new_num = Number(1 if self.value != other.value else 0)
        new_num.set_context(other.context)
        return new_num

    def comp_lt(self, other):
        new_num = Number(1 if self.value < other.value else 0)
        new_num.set_context(other.context)
        return new_num

    def comp_gt(self, other):
        new_num = Number(1 if self.value > other.value else 0)
        new_num.set_context(other.context)
        return new_num

    def comp_loe(self, other):
        new_num = Number(1 if self.value <= other.value else 0)
        new_num.set_context(other.context)
        return new_num

    def comp_goe(self, other):
        new_num = Number(1 if self.value >= other.value else 0)
        new_num.set_context(other.context)
        return new_num

    def comp_and(self, other):
        new_num = Number(1 if self.value == 1 and other.value == 1 else 0)
        new_num.set_context(other.context)
        return new_num

    def comp_or(self, other):
        new_num = Number(1 if self.value == 1 or other.value == 1 else 0)
        new_num.set_context(other.context)
        return new_num

    def not_op(self):
        new_num = Number(0 if self.value == 1 else 1)
        new_num.set_context(self.context)
        return new_num


class Number(Real):
    def __init__(self, value=None, pos=None):
        super().__init__(value, pos)
        self.description = "Number"
        self.ID = "NUMBER_TYPE"

    def get_dominant_type(self, a, b):
        if a == "FLOAT_TYPE" or b.ID == "FLOAT_TYPE":
            return Float
        return Integer

    def added(self, other):
        var_type = self.get_dominant_type(self.ID, other)
        new_num = var_type(64, self.value + other.value)
        new_num.set_context(other.context)
        return new_num

    def subtracted(self, other):
        var_type = self.get_dominant_type(self.ID, other)
        new_num = var_type(64, self.value - other.value)
        new_num.set_context(other.context)
        return new_num

    def multiplied(self, other):
        var_type = self.get_dominant_type(self.ID, other)
        new_num = var_type(64, self.value * other.value)
        new_num.set_context(other.context)
        return new_num

    def divided(self, other):
        var_type = self.get_dominant_type(self.ID, other)
        if other.value == 0:
            pos = other.pos
            return RuntimeError("Cannot divide by zero", self.context, pos)

        new_num = var_type(64, self.value / other.value)
        new_num.set_context(other.context)
        return new_num

    def power(self, other):
        var_type = self.get_dominant_type(self.ID, other)
        new_num = var_type(64, pow(self.value, other.value))
        new_num.set_context(other.context)
        return new_num

    def is_true(self):
        return self.value != 0

    def print_self(self):
        return self.value

class Integer(Number):
    def __init__(self, bitsize, value=None, pos=None):
        super().__init__(value, pos)
        self.description = "Integer"
        self.bitsize = bitsize
        self.value = value
        self.ID = "NUMBER_TYPE"

    def print_self(self):
        return self.value

class Bool(Number):
    def __init__(self, value):
        super().__init__(value)
        self.description = "Bool"
        self.value = value
        self.ID = "BOOL_TYPE"

        def print_self(self):
            if self.value == 1:
                return "true"
            else:
                return "false"
    def print_self(self):
        return self.value

# class UInt(Integer):
#    def __init__(self, value=None, pos=None, bitsize=64):
#        super().__init__(value, pos, bitsize)

# class Int(Integer):
#    def __init__(self, value=None, pos=None, bitsize=64):
#        super().__init__(value, pos, bitsize)


class Float(Number):
    def __init__(self, bitsize, value=None, pos=None):
        super().__init__(value, pos)
        self.description = "Float"
        self.bitsize = bitsize
        self.value = value
        self.ID = "FLOAT_TYPE"

    def print_self(self):
        return self.value

class Array(Type):
    def __init__(self, elements=[], element_id=None):
        super().__init__(description="Array")
        self.elements = elements
        self.length = len(self.elements)
        self.ID = "ARRAY_TYPE"
        self.element_id = element_id

    def print_self(self):
        new_arr = []
        for element in self.elements:
            if element is not None:
                new_arr.append(element.value)

        return new_arr

    def get(self, index):
        if index < 0 or index > self.length - 1:
            return RuntimeError("Index out of range", self.context, self.pos)

        return self.elements[index]

    def set(self, index, new):
        if index < 0 or index > self.length - 1:
            return RuntimeError("Index out of range", self.context, self.pos)

        self.elements[index] = new
        return None

class string(Real):
    def __init__(self, str_value=None):
        super().__init__(str_value)
        self.description = "String"
        self.str_value = str_value
        self.ID = "STRING_TYPE"

    def added(self, other):
        other_val = other.str_value
        string_val = self.str_value

        new_str = string(string_val + other_val)
        new_str.set_context(other.context)
        return new_str

    def is_true(self):
        return self.str_value is not None

    def print_self(self):
        return str(self.str_value)


Number.nil = Number(0)
Number.true = Bool(1)
Number.false = Bool(0)
