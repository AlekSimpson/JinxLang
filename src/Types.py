from Context import Context
from Error import RuntimeError

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
    def __init__(self, value=None, pos=None):
        self.value = value
        self.pos = pos
        self.context = None

    def set_context(self, ctx):
        self.context = ctx

    def print_self(self):
        return self.value


class Void:
    def __init__(self, pos=None):
        self.pos = pos
        self.context = None

    def print_self(self):
        return "Void"


class Real(Type):
    def __init__(self, value=None, pos=None):
        super().__init__(value, pos)

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
        self.ID = "NUMBER_TYPE"

    def added(self, other):
        new_num = Number(self.value + other.value)
        new_num.set_context(other.context)
        return new_num

    def subtracted(self, other):
        new_num = Number(self.value - other.value)
        new_num.set_context(other.context)
        return new_num

    def multiplied(self, other):
        new_num = Number(self.value * other.value)
        new_num.set_context(other.context)
        return new_num

    def divided(self, other):
        if other.value == 0:
            pos = other.pos
            return RuntimeError("Cannot divide by zero", self.context, pos)

        new_num = Number(self.value / other.value)
        new_num.set_context(other.context)
        return new_num

    def power(self, other):
        new_num = Number(pow(self.value, other.value))
        new_num.set_context(other.context)
        return new_num

    def is_true(self):
        return self.value != 0

    def print_self(self):
        return self.value


class Integer(Number):
    def __init__(self, bitsize, value=None, pos=None):
        super().__init__(value, pos)
        self.bitsize = bitsize
        self.ID = "NUMBER_TYPE"


class Bool(Number):
    def __init__(self, value):
        self.value = value
        self.ID = "BOOL_TYPE"


# class UInt(Integer):
#    def __init__(self, value=None, pos=None, bitsize=64):
#        super().__init__(value, pos, bitsize)

# class Int(Integer):
#    def __init__(self, value=None, pos=None, bitsize=64):
#        super().__init__(value, pos, bitsize)


class Float(Number):
    def __init__(self, bitsize, value=None, pos=None):
        super().__init__(value, pos)
        self.bitsize = bitsize
        self.ID = "NUMBER_TYPE"


class Array(Type):
    def __init__(self, elements=[]):
        super().__init__()
        self.elements = elements
        self.length = len(self.elements)
        self.ID = "ARRAY_TYPE"

    def print_self(self):
        new_arr = []
        for el in self.elements:
            if el != None:
                new_arr.append(el.value)

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
