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
        return self.token.as_string()

class VarAccessNode:
    def __init__(self, token):
        self.token = token 
        self.description = "VarAccessNode"
        self.classType = 4

    def as_string(self):
        return self.token.as_string()

class VarAssignNode:
    def __init__(self, token, value_node):
        self.token = token 
        self.value_node = value_node
        self.classType = 5

    def as_string(self):
        return self.token.as_string()

class VariableNode:
    def __init__(self, token):
        self.token = token
        self.description = "VariableNode"
        self.classType = 2

    def as_string(self):
        return self.token.as_string()

class IfNode:
    def __init__(self, cases, else_case=None):
        self.cases = cases 
        self.else_case = else_case
        self.token = cases[0][0].token
        self.description = "IfNode"
        self.classType = 6

    def as_string(self):
        return self.token.as_string()

class ForNode:
    def __init__(self, iterator, startValue, endValue, bodyNode):
        self.iterator = iterator 
        self.startValue = startValue 
        self.endValue = endValue 
        self.bodyNode = bodyNode
        self.token = startValue.token
        self.description = "ForNode"
        self.classType = 7

    def as_string(self):
        return self.token.as_string()

class WhileNode:
    def __init__(self, conditionNode, bodyNode):
        self.conditionNode = conditionNode 
        self.bodyNode = bodyNode 
        self.token = conditionNode.token
        self.description = "WhileNode"
        self.classType = 8

    def as_string(self):
        return self.token.as_string()

class FuncDefNode:
    def __init__(self, body_node, token=None, arg_name_tokens=None):
        if token == None: 
            lambda_ = Token(tk.MT_NONFAC, tk.TT_ID, "lambda")
            self.token = lambda_
        else:
            self.token = token 

        self.arg_name_tokens = arg_name_tokens 
        self.body_node = body_node
        self.description = "FuncDefNode"
        self.classType = 9

    def as_string(self):
        return self.token.as_string()

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
        return self.token.as_string()

class StringNode:
    def __init__(self, token):
        self.token = token 
        self.description = "StringNode" 
        self.classType = 11

    def as_string(self):
        return self.token.as_string()

class BinOpNode:
    def __init__(self, lhs=None, op=None, rhs=None):
        self.lhs = lhs 
        self.op = op
        self.rhs = rhs 
        self.token = Token()
        self.description = "BinOpNode" 
        self.classType = 0

    def as_string(self):
        return self.token.as_string()

class UnaryNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok 
        self.node = node 
        self.description = "UnaryNode" 
        self.classType = 3

    def as_string(self):
        return self.token.as_string()

class ListNode:
    def __init__(self, element_nodes):
        self.element_nodes = element_nodes 
        self.token = Token()
        self.description = "ListNode"
        self.classType = 12

    def as_string(self):
        return self.token.as_string()
