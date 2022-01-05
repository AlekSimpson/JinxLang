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

#class Function(Number):
#    def __init__(self, name=None, body_node=None, arg_nodes=None):
#        super().__init__()
#        self.name = name 
#        self.body_node = body_node 
#        self.arg_nodes = arg_nodes 
#
#    def execute(self, args):
#        res = RuntimeResult()
#        interpreter = Interpreter()
#
#        str = self.name 
#
#        new_context = Context(str, self.context, self.pos)
#        par = new_context.parent
#
#        a_nodes = self.arg_nodes 
#
#        pos =  body_node.token.pos 
#
#        if len(a_nodes) != 0:
#            if len(args) > len(a_nodes):
#                err = RuntimeError(f'to many arguements passed into function {name}', new_context, pos)
#                _ = res.failure(err)
#                return (None, res)
#
#            if len(args) < len(a_nodes):
#                err = RuntimeError(f'to few arguements passed into function {name}', new_context, pos)
#                _ = failure(err)
#                return (None, res)
#
#            for i in range(0, (len(a_nodes) - 1)):
#                arg_name = a_nodes[i]
#                arg_value = args[i]
#
#                arg_value.set_context(new_context)
#                sTable = new_context.symbolTable ## NOT IMPLEMENTED YET ##
#                sTable.set_val(arg_name, arg_value)
#
#        body_res = interpreter.visit(self.body_node, new_context)
#        _ = res.register(body_res)
#
#        value = res.value 
#        if res.error != None: return (None, res)
#        self.context = new_context 
#        return (value, res)
#
#    def copy(self):
#        copy = Function(self.name, self.body_node, self.arg_nodes)
#        copy.set_context(self.context)
#        return copy 
#
#    def print_self(self):
#        return f'<function {self.name}>'

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



















































