from SymbolTable import SymbolTable
from Error import *
import tokens as tk
from Context import Context
from Types import *
from Position import Position
from GlobalTable import global_symbol_table
from TypeKeywords import type_keywords, type_values
from TypeValue import TypeValue
from Interpreter import Function, BuiltinFunction

from llvmlite import ir, binding
import llvmlite.binding as llvm
from ctypes import CFUNCTYPE

class Compiler:
    def __init__(self):
        self.binding = binding # <-------- might not need this actually
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()
        self.table = None
        self.debug = False
        self._config_llvm()
        self.init_string_formats()

        printf_ty = ir.FunctionType(ir.IntType(32), [ir.IntType(8).as_pointer()], var_arg=True)
        printf = ir.Function(self.module, printf_ty, name="printf")

        # This helps to keep track of Defined Variabled
        # NOTE: Probably can replace this with Context and GlobalTable I think
        # NOTE: Variables are stored in tuples ex: (ptr, Type)
        self.builtin = {'print' : (printf, self.printf)}
        self.variables = {}

    def init_string_formats(self):
        str_c_fmt = ir.Constant(ir.ArrayType(ir.IntType(8), len("%s\n\0")), bytearray("%s\n\0".encode("utf8")))
        self.str_global_fmt = ir.GlobalVariable(self.module, str_c_fmt.type, name="fstr")
        self.str_global_fmt.linkage = 'internal'
        self.str_global_fmt.global_constant = True
        self.str_global_fmt.initializer = str_c_fmt

        int_c_fmt = ir.Constant(ir.ArrayType(ir.IntType(8), len("%d\n\0")), bytearray("%d\n\0".encode("utf8")))
        self.int_global_fmt = ir.GlobalVariable(self.module, int_c_fmt.type, name="fint")
        self.int_global_fmt.linkage = 'internal'
        self.int_global_fmt.global_constant = True
        self.int_global_fmt.initializer = int_c_fmt

    def printf(self, params):
        print_res = params[0]

        fmt = self.int_global_fmt
        print_res = params[0].ir_value
        if not isinstance(params[0], Integer):
            fmt = self.str_global_fmt

        printf = self.builtin['print'][0]

        if not isinstance(print_res.type, ir.IntType):
            before = print_res
            print_res = self.builder.alloca(print_res.type)
            self.builder.store(before, print_res)

        voidptr_ty = ir.IntType(8).as_pointer()
        fmt_arg = self.builder.bitcast(fmt, voidptr_ty)
        self.builder.call(printf, [fmt_arg, print_res])

    # NOTE: End builtin functions

    def _config_llvm(self):
        # Config LLVM
        self.module = ir.Module(name="main")
        func_type = ir.FunctionType(ir.VoidType(), [], False)
        self.base_func = ir.Function(self.module, func_type, name="main")
        block = self.base_func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)

    def create_execution_engine(self):
        target = llvm.Target.from_default_triple()
        target_machine = target.create_target_machine()
        # Add an execution engine with an empty backing module
        backing_mod = llvm.parse_assembly(str(self.module))
        engine = llvm.create_mcjit_compiler(backing_mod, target_machine)
        return engine

    def compile_ir(self, engine, llvm_ir):
        ir_ = str(llvm_ir)

        if self.debug:
            print("==================================")
            print(ir_)
            print("==================================")

        mod = llvm.parse_assembly(ir_)
        mod.verify()

        engine.add_module(mod)
        engine.finalize_object()
        engine.run_static_constructors()

        main_func_ptr = engine.get_function_address("main")
        cfunc = CFUNCTYPE(None)(main_func_ptr)
        res = cfunc()
        return res

    def compile_ir_and_output(self, ir_):
        self.builder.ret_void()
        engine = self.create_execution_engine()
        mod = self.compile_ir(engine, ir_)
        return mod

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
            self.visit_number,         # 1
            "VariableNode",            # 2
            self.visit_unary,          # 3
            self.AccessNode,           # 4
            self.visit_VarAssignNode,  # 5
            self.visit_IfNode,         # 6
            self.visit_ForNode,        # 7
            self.visit_WhileNode,      # 8
            self.visit_FuncDefNode,    # 9
            self.visit_CallNode,       # 10
            self.visit_StringNode,     # 11
            self.visit_ListNode,       # 12
        #    self.visit_SetArrNode,     # 13
        #    self.visit_GetArrNode,     # 14
        #    self.visit_ReturnNode,     # 15
        #    self.visit_VarUpdateNode,  # 16
        #    self.visit_float,          # 17
        #    self.visit_ObjectDefNode,  # 18
        #    self.visit_DotNode,        # 19
        ]

        if func_index < 0 or func_index > 19:
            return RuntimeError("No visit methods found", context, Position()) # Should probably pass in a real position here at some point
        result = visit_map[func_index](node, context)

        return result

    def visit_unary(self, node, ctx): pass
    def visit_VarAssignNode(self, node, ctx): pass
    def visit_IfNode(self, node, ctx): pass
    def visit_ForNode(self, node, ctx): pass
    def visit_WhileNode(self, node, ctx): pass

    def visit_VarAccessNode(self, node, ctx):
        if node.token.value in self.variables:
            ptr, _ = self.variables[node.token.value]
        elif node.token.value in self.builtin:
            ptr, _ = self.builtin[node.token.value]
        #return self.builder.load(ptr), Type
        return ptr

    # NOTE: Not tested yet
    def visit_FuncDefNode(self, node, ctx):
        name = node.token.value
        body_node = node.body_node

        func_arg_names = []
        func_arg_types = []

        for n in node.arg_name_tokens:
            func_arg_names.append(n.value)

        for n in node.arg_type_tokens:
            func_arg_types.append(n.type_dec.type_obj)

        return_type = node.return_type

        fnty = ir.FunctionType(return_type, func_arg_types)
        func = ir.Function(self.module, fnty, name=name)

        block = func.append_basic_block(f'{name}_entry')
        previous_builder = self.builder

        self.builder = ir.IRBuilder(block)
        params_ptr = []

        for i, typ in enumerate(func_arg_types):
            ptr = self.builder.alloca(typ)
            self.builder.store(func.args[i], ptr)
            params_ptr.append(ptr)

        previous_variables = self.variables.copy()
        for i, x in enumerate(zip(func_arg_types, func_arg_names)):
            typ = func_arg_types[i]
            ptr = params_ptr[i]

            self.variables[x[1]] = ptr, typ

        self.variables[name] = func, return_type

        self.compile(body_node, ctx)

        # Removing function's variables so that they cannot be accessed out of scope
        self.variables = previous_variables
        self.variables[name] = func, return_type

        self.builder = previous_builder

    def visit_CallNode(self, node, ctx):
        args = []
        types = []

        value_to_call = self.compile(node.node_to_call, ctx)
        if isinstance(value_to_call, Error):
            return value_to_call

        func_value = Function()
        if value_to_call is not None:
            func_value = value_to_call

        val_cal = node.node_to_call.token.value

        # get args and their types
        i = 0
        for arg_node in node.arg_nodes:
            new = arg_node.token.value
            new = self.compile(arg_node, ctx)
            typ = ir.IntType(64)
            if isinstance(new, Array):
                 new = Array(new.elements, new.element_id)

            args.append(new)
            types.append(typ)
            i += 1

        if val_cal in self.builtin:
            builtin_func = self.builtin[val_cal][1]
            ret = builtin_func(args)
            ret_type = ir.IntType(32)
        else:
            func, ret_type = self.variables[val_cal]
            ret = self.builder.call(func, args)

        return ret, ret_type

        #return_value = self.variables[val_cal]()

        #func_return = func_value.returnType.type_dec.type_obj
        #types_match = self.check_types_match(return_value, func_return, return_value.name, ctx, node)
        #if types_match is not None:
        #    return types_match

        #return return_value

    def check_types_match(self, a, b, name, ctx, node):
        if a.ID != b.ID:
            pos = node.token.pos
            return RuntimeError(f"Cannot assign value of {a.description} to type {b.description} {name}", ctx, pos)
        return None

    def visit_StringNode(self, node, ctx):
        str_value = node.token.value + "\0"
        c_str_val = ir.Constant(ir.ArrayType(ir.IntType(8), len(str_value)),
                        bytearray(str_value.encode("utf8")))

        # NOTE: Returning None now just cause I don't know what to do with it right now,
        #       need to flesh out more of the context and symbol table integration first
        str = string(ir_value=c_str_val)
        return str


    def visit_ListNode(self, node, ctx):
        elements = []

        for element_node in node.element_nodes:
            el = self.compile(element_node, ctx)
            elements.append(el)
            
            if isinstance(el, Error):
                return el
            if element_node.classType == 15:
                break

            element_id = Void()
            if len(elements) != 0:
                type_dec = node.element_nodes[0].token.type_dec
                if type_dec is not None:
                    element_id = node.element_nodes[0].token.type_dec.type_obj

        arr_ty = ir.ArrayType(ir.IntType(8), len(elements))
        return ir.Constant(arr_ty, elements), arr_ty
        #arr = Array(elements, element_id, element_type=arr_ty)
        #arr.set_context(ctx)
        #return arr

    def visit_number(self, node, ctx):
        entry = node.token.pos
        child_context = Context("<number>", ctx, entry)

        val = node.token.value
        p = node.token.pos

        Type = ir.IntType(64)
        return Integer(64, ir_value=ir.Constant(Type, val))

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

        left_vst = self.compile(node.lhs, ctx)
        if isinstance(left_vst, Error):
            return left_vst
        #left_ty = left_vst[1]
        #left = left_vst[0]
        left = left_vst

        right_vst = self.compile(node.rhs, ctx)
        if isinstance(right_vst, Error):
            return right_vst
        #right_ty = right_vst[1]
        #right = right_vst[0]
        right = right_vst

        op_node = node.op
        name_cond = op_node.token.type_name

        if left.ID == right.ID:
            if name_cond == tk.TT_PLUS:
                result = left.addc(right, self.builder)
            elif name_cond == tk.TT_MINUS:
                result = left.subc(right, self.builder)
            elif name_cond == tk.TT_MUL:
                result = left.mulc(right, self.builder)
            elif name_cond == tk.TT_DIV:
                result = left.divc(right, self.builder)
            elif name_cond == tk.TT_POW:
                result = left.powc(right, self.builder)
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

        num = Integer(64, ir_value=result)

        return num

    def AccessNode(self, node, ctx):
        err = self.check_for_declaration(self.table, node, ctx)
        if err is not None:
            return err
        else:
            return self.visit_VarAccessNode(node, ctx)
