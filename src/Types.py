from Context import Context
from Error import RuntimeError
from Position import Position
from SymbolTable import SymbolTable
from llvmlite import ir

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

class Void:
    def __init__(self, pos=None):
        self.pos = pos
        self.context = None
        self.ptr = None

    def print_self(self):
        return "Void"

class Real(Type):
    def __init__(self, value=None, pos=None):
        super().__init__(value, pos, "Real")

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
    def __init__(self, bitsize, value=None, pos=None, ir_value=None):
        super().__init__(value, pos)
        self.description = "Integer"
        self.bitsize = bitsize
        self.value = value
        self.ir_value = ir_value
        self.ir_type = ir.IntType(bitsize)
        self.ID = "NUMBER_TYPE"
        self.ptr = None

    def addc(self, other, builder):
        return builder.add(self.ir_value, other.ir_value)

    def subc(self, other, builder):
        return builder.sub(self.ir_value, other.ir_value)

    def divc(self, other, builder):
        return builder.sdiv(self.ir_value, other.ir_value)

    def mulc(self, other, builder):
        return builder.mul(self.ir_value, other.ir_value)

    def powc(self, other, builder):
        val = 1
        for i in range(0, other.value):
            val = val * builder.fmul(self.ir_value, self.ir_value)
        return val

    # Interpreter code

    def added(self, other):
        new_num = Integer(64, self.value + other.value)
        new_num.set_context(other.context)
        return new_num

    def subtracted(self, other):
        new_num = Integer(64, self.value - other.value)
        new_num.set_context(other.context)
        return new_num

    def multiplied(self, other):
        new_num = Integer(64, self.value * other.value)
        new_num.set_context(other.context)
        return new_num

    def divided(self, other):
        if other.value == 0:
            pos = other.pos
            return RuntimeError("Cannot divide by zero", self.context, pos)

        new_num = Integer(64, int(self.value / other.value))
        new_num.set_context(other.context)
        return new_num

    def power(self, other):
        new_num = Integer(64, pow(self.value, other.value))
        new_num.set_context(other.context)
        return new_num

    def print_self(self):
        return self.value

class Bool(Number):
    def __init__(self, value, ir_value=None):
        super().__init__(value)
        self.description = "Bool"
        self.value = value
        self.ir_value = ir_value 
        self.ir_type = ir.IntType(1)
        self.ID = "BOOL_TYPE"
        self.ptr = None

        def print_self(self):
            if self.value == 1:
                return "true"
            else:
                return "false"
    def print_self(self):
        return self.value

class Float(Number):
    def __init__(self, bitsize, value=None, pos=None, ir_value=None):
        super().__init__(value, pos)
        self.description = "Float"
        self.bitsize = bitsize
        self.value = value
        self.ir_value = ir_value
        self.ir_type = ir.IntType(bitsize)
        self.ID = "FLOAT_TYPE"
        self.ptr = None

    def addc(self, other, builder):
        return builder.fadd(self.value, other.value)

    def subc(self, other, builder):
        return builder.fsub(self.value, other.value)

    def divc(self, other, builder):
        return builder.fdiv(self.value, other.value)

    def mulc(self, other, builder):
        return builder.fmul(self.value, other.value)

    def powc(self, other, builder):
        val = 1
        for i in range(0, other.value):
            val = val * builder.fmul(self.value, self.value)
        return val

    ## Interpreter code

    def added(self, other):
        new_num = Float(64, self.value + other.value)
        new_num.set_context(other.context)
        return new_num

    def subtracted(self, other):
        new_num = Float(64, self.value - other.value)
        new_num.set_context(other.context)
        return new_num

    def multiplied(self, other):
        new_num = Float(64, self.value * other.value)
        new_num.set_context(other.context)
        return new_num

    def divided(self, other):
        if other.value == 0:
            pos = other.pos
            return RuntimeError("Cannot divide by zero", self.context, pos)

        new_num = Float(64, self.value / other.value)
        new_num.set_context(other.context)
        return new_num

    def power(self, other):
        new_num = Float(64, pow(self.value, other.value))
        new_num.set_context(other.context)
        return new_num

    def print_self(self):
        return self.value

class Array(Type):
    def __init__(self, elements=[], element_id=None, ir_value=None, ir_type=None):
        super().__init__(description="Array")
        self.elements = elements
        self.length = len(self.elements)
        self.ID = "ARRAY_TYPE"
        self.element_id = element_id
        self.ir_value = ir_value
        self.ir_type = ir_type
        self.ptr = None
        self.description = f"{self.print_self()}"

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
    def __init__(self, str_value=None, ir_value=None):
        super().__init__(str_value)
        self.description = "String"
        self.str_value = str_value
        self.ID = "STRING_TYPE"
        self.ir_value = ir_value
        if str_value is not None:
            length = len(self.str_value)
        else:
            length = 0
        self.ir_type = ir.ArrayType(ir.IntType(8), length)
        self.ptr = None

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


Number.nil = Integer(bitsize=1, value=0, ir_value=ir.Constant(ir.IntType(1), 0))
Number.true = Bool(1, ir_value=ir.Constant(ir.IntType(1), 1))
Number.false = Bool(0, ir_value=ir.Constant(ir.IntType(1), 0))
