from RuntimeResult import RuntimeResult 
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

# Probably should watch that video about compiling python to assembly
# Because I am not sure how that will work with other python libraries like numpy
# And I need numpy to to create Int64, 32, etc

class Type:
    def __init__(self, value=None, pos=None):
        self.value = value 
        self.pos = pos 
        self.context = None

    def set_context(self, ctx):
        self.context = ctx

    def print_self():
        return self.value

class Natural(Type):
    def __init__(self, value=None, pos=None):
        super().__init__(value, pos)

    def comp_eq(self, other):
        new_num = Number(1 if self.value == other.value else 0)
        new_num.set_context(other.context)
        return (new_num, None)

    def comp_ne(self, other):
        new_num = Number(1 if self.value != other.value else 0)
        new_num.set_context(other.context)
        return (new_num, None)

    def comp_lt(self, other):
        new_num = Number(1 if self.value < other.value else 0)
        new_num.set_context(other.context)
        return (new_num, None)

    def comp_gt(self, other):
        new_num = Number(1 if self.value > other.value else 0)
        new_num.set_context(other.context)
        return (new_num, None)

    def comp_loe(self, other):
        new_num = Number(1 if self.value <= other.value else 0)
        new_num.set_context(other.context)
        return (new_num, None)

    def comp_goe(self, other):
        new_num = Number(1 if self.value >= other.value else 0)
        new_num.set_context(other.context)
        return (new_num, None)

    def comp_and(self, other):
        new_num = Number(1 if self.value == 1 and other.value == 1 else 0)
        new_num.set_context(other.context)
        return (new_num, None)

    def comp_or(self, other):
        new_num = Number(1 if self.value == 1 or other.value == 1 else 0)
        new_num.set_context(other.context)
        return (new_num, None)

    def not_op(self):
        new_num = Number(0 if self.value == 1 else 1)
        new_num.set_context(self.context)
        return (new_num, None)

class Number(Natural):
    def __init__(self, value=None, pos=None):
        super().__init__(value, pos)

    def added(self, other):
        new_num = Number(self.value + other.value)
        new_num.set_context(other.context)
        return (new_num, None)

    def subtracted(self, other):
        new_num = Number(self.value - other.value)
        new_num.set_context(other.context)
        return (new_num, None)

    def multiplied(self, other):
        new_num = Number(self.value * other.value)
        new_num.set_context(other.context)
        return (new_num, None)

    def divided(self, other):
        if other.value == 0:
            pos = other.pos
            err = RuntimeError("Cannot divide by zero", self.context, pos)
            return (None, err)

        new_num = Number(self.value / other.value)
        new_num.set_context(other.context)
        return (new_num, None)

    def power(self, other):
        new_num = Number(pow(self.value, other.value))
        new_num.set_context(other.context)
        return (new_num, None)

    def is_true(self):
        return self.value != 0

    def print_self(self):
        return self.value

class Integer(Number):
    def __init__(self, value=None, pos=None):
        super().__init__(value, pos)

class UInt(Integer):
    def __init__(self, value=None, pos=None):
        super().__init__(value, pos)

class Int(Integer):
    def __init__(self, value=None, pos=None):
        super().__init__(value, pos)

class Float(Number):
    def __init__(self, value=None, pos=None):
        super().__init__(value, pos)
    # Need 64 bit floats and stuff

class Array(Type):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements
        self.length = len(self.elements)

    def print_self(self):
        new_arr = []
        for el in self.elements:
            if el != None:
                new_arr.append(el.value)

        return new_arr

    def get(self, index):
        res = RuntimeResult()
        if index.value < 0 or index.value > self.length - 1:
            err = RuntimeError("Index out of range", self.context, self.pos)
            return (None, err) 
        
        return (self.elements[index.value], res)

    def set(self, index, new):
        res = RuntimeResult()

        if index < 0 or index > self.length - 1:
            err = RuntimeError("Index out of range", self.context, self.pos)
            return (None, err)

        self.elements[index] = new
        return (None, res)

class string(Natural):
    def __init__(self, str_value=None):
        super().__init__(str_value)
        self.str_value = str_value 

    def added(self, other):
        otherVal = other.str_value 
        str = self.str_value 
        
        new_str = string(str + otherVal)
        new_str.set_context(other.context)
        return (new_str, None)

    def is_true(self):
        return self.str_value != None 

    def print_self(self):
        return str(self.str_value)

Number.nil = Number(0)
Number.true = Number(1)
Number.false = Number(0)

