from Context import Context
from Error import RuntimeError
from Position import Position
from SymbolTable import SymbolTable
from llvmlite import ir
from Error import *

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


# NOTE: Opaque types are like abstract types in julia

class Type:
    def __init__(self, value=None, pos=None, description="AnyType", ir_value=None, ptr=None):
        self.value = value
        self.ir_value = ir_value
        self.pos = pos
        self.context = None
        self.description = description
        self.ptr = ptr

    def set_context(self, ctx):
        self.context = ctx

    def print_self(self):
        return self.value

class Void:
    def __init__(self, pos=None):
        self.pos = pos
        self.context = None
        self.ptr = None
        self.ir_type = ir.VoidType()
        self.ir_value = ir.VoidType()

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
    def __init__(self, bitsize, value=None, pos=None, ir_value=None, ptr=None):
        super().__init__(value, pos)
        self.description = "Integer"
        self.bitsize = bitsize
        self.value = value
        self.ir_value = ir_value
        self.ir_type = ir.IntType(bitsize)
        self.ID = "NUMBER_TYPE"
        self.ptr = ptr

    def get_value(self, builder):
        if self.ptr is not None:
            return builder.load(self.ptr)
        return self.ir_value

    def addc(self, other, builder):
        return builder.add(self.get_value(builder), other.get_value(builder))

    def subc(self, other, builder):
        return builder.sub(self.get_value(builder), other.get_value(builder))

    def divc(self, other, builder):
        return builder.sdiv(self.get_value(builder), other.get_value(builder))

    def mulc(self, other, builder):
        return builder.mul(self.get_value(builder), other.get_value(builder))

    # NOTE: compiled exponentiation is bugged I'm prety sure
    def powc(self, other, builder):
        val = 1
        for i in range(0, other.value):
            val = val * builder.fmul(self.ir_value, self.ir_value)
        return val

    def comp_eqc(self, other, builder):
        return builder.icmp_signed("==", self.get_value(builder), other.get_value(builder))

    def comp_goec(self, other, builder):
        return builder.icmp_signed(">=", self.get_value(builder), other.get_value(builder))

    def comp_gtc(self, other, builder):
        return builder.icmp_signed(">", self.get_value(builder), other.get_value(builder))

    def comp_loec(self, other, builder):
        return builder.icmp_signed("<=", self.get_value(builder), other.get_value(builder))

    def comp_ltc(self, other, builder):
        return builder.icmp_signed("<", self.get_value(builder), other.get_value(builder))

    def comp_nec(self, other, builder):
        return builder.icmp_signed("!=", self.get_value(builder), other.get_value(builder))

    def comp_andc(self, other, builder):
        return builder.and_(self.get_value(builder), other.get_value(builder))

    def comp_orc(self, other, builder):
        return builder.or_(self.get_value(builder), other.get_value(builder))

    def not_opc(self, builder):
        return builder.neg(self.get_value(builder))

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

    def get_value(self, builder):
        if self.ptr is not None:
            return builder.load(self.ptr)
        return self.ir_value

    def print_self(self):
        if self.value == 1:
            return "true"
        else:
            return "false"

class Float(Number):
    def __init__(self, bitsize, value=None, pos=None, ir_value=None, ptr=None):
        super().__init__(value, pos)
        self.description = "Float"
        self.bitsize = bitsize
        self.value = value
        self.ir_value = ir_value
        self.ir_type = ir.DoubleType()
        self.ID = "FLOAT_TYPE"
        self.ptr = ptr

    def get_value(self, builder):
        if self.ptr is not None:
            return builder.load(self.ptr)
        return self.ir_value

    def addc(self, other, builder):
        return builder.fadd(self.ir_value, other.ir_value)

    def subc(self, other, builder):
        return builder.fsub(self.ir_value, other.ir_value)

    def divc(self, other, builder):
        return builder.fdiv(self.ir_value, other.ir_value)

    def mulc(self, other, builder):
        return builder.fmul(self.ir_value, other.ir_value)

    def powc(self, other, builder):
        val = 1
        for i in range(0, other.value):
            val = val * builder.fmul(self.ir_value, self.ir_value)
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

    def get_value(self, builder):
        if self.ptr is not None:
            return builder.load(self.ptr)
        return self.ir_value

    def print_self(self):
        new_arr = []

        for element in self.elements:
            if element is not None:
                new_arr.append(element)

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
    def __init__(self, str_value=None, ir_value=None, ptr=None, bt_ptr=None):
        super().__init__(str_value)
        self.description = "String"
        self.str_value = str_value
        self.ID = "STRING_TYPE"
        self.ir_value = ir_value
        if str_value is not None:
            self.length = len(self.str_value)
        else:
            self.length = 3

        self.ir_type = ir.PointerType(ir.IntType(64).as_pointer())
        self.ptr = ptr
        self.bt_ptr = bt_ptr

    def get_value(self, builder):
        if self.ptr is not None:
            return builder.load(self.ptr)
        return self.ir_value

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

## Functions and Objects

class Object(Type):
    def __init__(self, name, body_node=None, attr_names=None, attr_types=None, ir_value=None, params_ptrs=None,
                 builder=None, ptr=None):
        self.name = name
        self.body_node = body_node
        self.attr_names = attr_names
        self.context = self.generate_new_context()
        self.attr_types = attr_types
        self.ID = self.name + "_TYPE"
        self.ir_value = ir_value
        self.ir_type = self.ir_value
        self.builder = builder
        self.ptr = ptr

        self.params_ptrs = params_ptrs
        i = 0
        self.attr_table = {}
        if self.attr_names is not None:
            for n in self.attr_names:
                self.attr_table[n] = i
                i = i + 1

    def generate_new_context(self, parent_ctx=None, pos=None):
        new_context = Context(self.name, parent_ctx, None)
        #new_context.symbolTable = parent_ctx.symbolTable
        new_context = Context()
        return new_context

    def print_self(self):
        return f"Abstract Object: {self.name}"

class BaseFunction(Type):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def generate_new_context(self):
        new_context = Context(self.name, self.context, self.pos)
        new_context.symbolTable = SymbolTable()

        return new_context

    def check_args(self, arg_names, args):
        if len(args) > len(arg_names):
            return RuntimeError(f"to many arguements passed into function {self.name}", Context(), self.pos)

        if len(args) < len(arg_names):
            return RuntimeError(f"to few arguements passed into function {self.name}", Context(), self.pos)

        return None

    def populate_args(self, arg_names, args, exec_ctx):
        for i in range(0, len(arg_names)):
            arg_name = arg_names[i]
            arg_value = args[i]

            arg_value.set_context(exec_ctx)
            exec_ctx.symbolTable.set_val(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_ctx):
        check = self.check_args(arg_names, args)
        if isinstance(check, Error):
            return check

        self.populate_args(arg_names, args, exec_ctx)

        return None

class FunctionIrPackage:
    def __init__(self, context, arg_types, arg_names, param_ptrs, builder):
        self.context = context
        self.arg_types = arg_types
        self.arg_names = arg_names
        self.param_ptrs = param_ptrs
        self.builder = builder

class Function(BaseFunction):
    def __init__(self, name=None, returnType=None, body_node=None, arg_nodes=None, arg_types=None, should_return_nil=False, ir_value=None, ir_type=None, ir_pack=None):
        super().__init__(name)
        self.body_node = body_node
        self.arg_nodes = arg_nodes
        self.arg_types = arg_types
        self.returnType = returnType
        self.should_return_nil = should_return_nil
        self.ir_value = ir_value
        self.ir_type = ir_type
        self.ir_pack = ir_pack

    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_nodes, self.should_return_nil)
        copy.set_context(self.context)
        return copy

    def print_self(self):
        return f"<function {self.name}>"


class BuiltinFunction(BaseFunction):
    def __init__(self, name_id, ir_value=None):
        super().__init__(name_id)
        self.name_id = name_id
        self.ir_value = ir_value

BuiltinFunction.print = BuiltinFunction(0)
