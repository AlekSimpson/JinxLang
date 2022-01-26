import tokens as tk 
from tokens import Token

class NumberNode:
    def __init__(self, token):
        self.token = token  
        self.description = "NumberNode"
        self.classType = 1

    def getNumber(self):
        #return Number(token.value)
        pass 

    def as_string(self):
        return f"{self.description}: {self.token.as_string()}"

class VarAccessNode:
    def __init__(self, token):
        self.token = token 
        self.description = "VarAccessNode"
        self.classType = 4

    def as_string(self):
        return f"{self.description}: {self.token.as_string()}"

class VarAssignNode:
    def __init__(self, token, value_node, type):
        self.token = token 
        self.value_node = value_node
        self.type = type
        self.description = "VarAssignNode"
        self.classType = 5

    def as_string(self):
        return f"{self.description}: {self.token.as_string()}"

class VariableNode:
    def __init__(self, token):
        self.token = token
        self.description = "VariableNode"
        self.classType = 2

    def as_string(self):
        return f"{self.description}: {self.token.as_string()}"

class IfNode:
    def __init__(self, cases, else_case=None):
        self.cases = cases 
        self.else_case = else_case
        #self.token = cases[0][0].token
        self.token = Token()
        self.description = "IfNode"
        self.classType = 6

    def as_string(self):
        return f"{self.description}: {self.token.as_string()}"

class ForNode:
    def __init__(self, iterator, startValue, endValue, bodyNode, should_return_nil):
        self.iterator = iterator 
        self.startValue = startValue 
        self.endValue = endValue 
        self.bodyNode = bodyNode
        self.token = startValue.token
        self.should_return_nil = should_return_nil 
        self.description = "ForNode"
        self.classType = 7

    def as_string(self):
        return f"{self.description}: {self.token.as_string()}"

class WhileNode:
    def __init__(self, conditionNode, bodyNode, should_return_nil):
        self.conditionNode = conditionNode 
        self.bodyNode = bodyNode 
        self.token = conditionNode.token
        self.should_return_nil = should_return_nil 
        self.description = "WhileNode"
        self.classType = 8

    def as_string(self):
        return f"{self.description}: {self.token.as_string()}"

class FuncDefNode:
    def __init__(self, body_node, token=None, arg_name_tokens=None, should_return_nil=False):
        if token == None: 
            lambda_ = Token(tk.MT_NONFAC, tk.TT_ID, "lambda")
            self.token = lambda_
        else:
            self.token = token 
        self.arg_name_tokens = arg_name_tokens 
        self.body_node = body_node
        self.should_return_nil = should_return_nil 
        self.description = "FuncDefNode"
        self.classType = 9

    def as_string(self):
        return f"{self.description}: {self.token.as_string()}"

class CallNode:
    def __init__(self, node_to_call, arg_nodes, token=None):
        if token == None:
            self.token = Token()
        else:
            self.token = token 
        self.node_to_call = node_to_call 
        self.arg_nodes = arg_nodes
        self.description = "CallNode"
        self.classType = 10
    
    def as_string(self):
        return f"{self.description}: {self.token.as_string()}"

class ArrayGetNode:
    def __init__(self, array, index):
        self.token = array.token 
        self.array = array 
        self.index = index 
        self.description = "ArrayGetNode"
        self.classType = 14

    def as_string(self):
        return f'{self.description}: {self.token.as_string()}'

class ArraySetNode:
    def __init__(self, array, index, new_val):
        self.token = array.token
        self.array = array 
        self.index = index 
        self.new_val = new_val
        self.description = "ArraySetNode"
        self.classType = 13

    def as_string(self):
        return f'{self.description}: {self.token.as_string()}'

class StringNode:
    def __init__(self, token):
        self.token = token 
        self.description = "StringNode" 
        self.classType = 11

    def as_string(self):
        return f"{self.description}: {self.token.as_string()}"

class BinOpNode:
    def __init__(self, lhs=None, op=None, rhs=None):
        self.lhs = lhs 
        self.op = op
        self.rhs = rhs 
        self.token = Token()
        self.description = "BinOpNode" 
        self.classType = 0

    def as_string(self):
        return f'{self.description}: {self.token.as_string()}'

class UnaryNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok 
        self.node = node 
        self.description = "UnaryNode" 
        self.classType = 3

    def as_string(self):
        return f"{self.description}: {self.token.as_string()}"

class ListNode:
    def __init__(self, element_nodes):
        self.element_nodes = element_nodes 
        self.token = Token()
        self.description = "ListNode"
        self.classType = 12

    def as_string(self):
        return f"{self.description}: {self.element_nodes}"

class ReturnNode:
    def __init__(self, node_to_return):
        self.node_to_return = node_to_return 
        self.token = node_to_return.token 
        self.description = "ReturnNode"
        self.classType = 15

    def as_string(self):
        return f'{self.description}: {self.token.as_string()}'

class ContinueNode:
    def __init__(self, token):
        self.token = token
        self.pos = self.token.pos
        self.description = "ContinueNode"
        self.classType = 16

    def as_string(self):
        return f'{self.description}: {self.token.as_string()}'

class BreakNode:
    def __init__(self, token):
        self.token = token 
        self.pos = self.token.pos 
        self.description = "BreakNode"
        self.classType = 17

    def as_string(self):
        return f'f{self.description}: {self.token.as_string()}'
