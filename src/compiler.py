from SymbolTable import SymbolTable
from Error import *
import tokens as tk
from Context import Context
from Types import *
from Position import Position
from GlobalTable import global_symbol_table
from TypeKeywords import type_keywords, type_values
from TypeValue import TypeValue
from llvimlite import ir

class Compiler:
    def __init__(self):
        self.table = None


        #XXX: They define builtin functions here in the init method

    def check_for_error(self, node):
        if isinstance(node, Error):
            return node
        return None

    def compile(self, node, context):
        err_check = self.check_for_error(node)
        if err_check is not None:
            return err_check
        if node is None:
            return

        func_index = node.classType
        #print(f"[{func_index}] - {node.as_string()}")
        # ^^^^ Keep for debugging purposes ^^^^
        self.table = context.symbolTable.symbols
        result = None

        visit_map = [
            self.visit_binop,          # 0
        #    self.visit_number,         # 1
        #    "VariableNode",            # 2
        #    self.visit_unary,          # 3
        #    self.AccessNode,           # 4
        #    self.visit_VarAssignNode,  # 5
        #    self.visit_IfNode,         # 6
        #    self.visit_ForNode,        # 7
        #    self.visit_WhileNode,      # 8
        #    self.visit_FuncDefNode,    # 9
        #    self.visit_CallNode,       # 10
        #    self.visit_StringNode,     # 11
        #    self.visit_ListNode,       # 12
        #    self.visit_SetArrNode,     # 13
        #    self.visit_GetArrNode,     # 14
        #    self.visit_ReturnNode,     # 15
        #    self.visit_VarUpdateNode,  # 16
        #    self.visit_float,          # 17
        #    self.visit_ObjectDefNode,  # 18
        #    self.visit_DotNode,        # 19
        ]

        if func_index <= 0 or func_index >= 19:
            return RuntimeError("No visit methods found", context, Position()) # Should probably pass in a real position here at some point
        visit_map[func_index](node, context)

        #return result

    def check_for_declaration(self, table, node, context):
        access_node = node
        name = access_node.token.value
        err = None

        if not name in table:
            pos = access_node.token.pos
            err = RuntimeError(f'"{name}" is not defined', context, pos)

        return err

    def visit_binop(self, node, ctx):
        result = None
        error = None

        left_vst = self.visit(node.lhs, ctx)
        if isinstance(left_vst, Error):
            return left_vst
        left = left_vst

        right_vst = self.visit(node.rhs, ctx)
        if isinstance(right_vst, Error):
            return right_vst
        right = right_vst

        op_node = node.op
        name_cond = op_node.token.type_name

        if left.ID == right.ID:
            if name_cond == tk.TT_PLUS:
                result = left.added(right)
            elif name_cond == tk.TT_MINUS:
                result = left.subtracted(right)
            elif name_cond == tk.TT_MUL:
                result = left.multiplied(right)
            elif name_cond == tk.TT_DIV:
                result = left.divided(right)
            elif name_cond == tk.TT_POW:
                result = left.power(right)
            elif name_cond == tk.TT_EE:
                result = left.comp_eq(right)
            elif name_cond == tk.TT_NE:
                result = left.comp_ne(right)
            elif name_cond == tk.TT_LT:
                result = left.comp_lt(right)
            elif name_cond == tk.TT_GT:
                result = left.comp_gt(right)
            elif name_cond == tk.TT_LOE:
                result = left.comp_loe(right)
            elif name_cond == tk.TT_GOE:
                result = left.comp_goe(right)
            elif name_cond == tk.TT_AND:
                result = left.comp_and(right)
            elif name_cond == tk.TT_OR:
                result = left.comp_or(right)
            else:
                result = Number(0)

    #def AccessNode(self, node, ctx):
    #    err = self.check_for_declaration(self.table, node, ctx)
    #    if err is not None:
    #        return err
    #    else:
    #        return self.visit_VarAccessNode(node, ctx)
