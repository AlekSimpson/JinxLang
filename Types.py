from RuntimeResult import RuntimeResult 
#from Interpreter import Interpreter
from Context import Context 
from Error import RuntimeError

class Number:
    def __init__(self, value=None, pos=None):
        self.value = value 
        self.pos = pos 
        self.context = None 

    def set_context(self, ctx):
        self.context = ctx

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
        new_num = Number(self.value / other.value)
        new_num.set_context(other.context)
        return (new_num, None)

    def power(self, other):
        new_num = Number(pow(self.value, other.value))
        new_num.set_context(other.context)
        return (new_num, None)

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

    def is_true(self):
        return self.value != 0

    def print_self(self):
        return self.value 

class Array(Number):
    def __init__(self, elements):
        super().__init__()
        self.elements = elements

    def print_self(self):
        new_arr = []
        for el in self.elements:
            new_arr.append(el.value)

        return new_arr

    ## MIGHT NEED TO ADD ARRAY FUNCTIONS HERE LATER ##

class string(Number):
    def __init__(self, str_value=None):
        super().__init__()
        self.str_value = str_value 

    def added(self, other):
        otherVal = other.str_value 
        str = self.str_value 
        print("is called")
        new_str = string(str + otherVal)
        new_str.set_context(other.context)
        return (new_str, None)

    def is_true(self):
        return self.str_value != None 

    def print_self(self):
        return f'<string {self.str_value}>'



















































