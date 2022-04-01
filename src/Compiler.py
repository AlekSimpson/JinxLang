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
        self.binding = binding
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()
        self.table = None
        self._config_llvm()

        # NOTE: They define builtin functions here in the init method
        fnty = ir.FunctionType(ir.IntType(32), [ir.IntType(8).as_pointer()], var_arg=True)
        printf_func = ir.Function(self.module, fnty, 'printf')

        # This helps to keep track of Defined Variabled
        # NOTE: Probably can replace this with context I think
        # NOTE: Variables are stored in tuples ex: (ptr, Type)
        self.variables = {
            'printf' : (printf_func,ir.IntType(32))
        }

    def printf(self,params,Type):
        '''
            C's builtin Printf function
        '''
        format = params[0]
        params = params[1:]
        zero = ir.Constant(ir.IntType(32),0)
        ptr = self.builder.alloca(Type)
        self.builder.store(format,ptr)
        format = ptr
        format = self.builder.gep(format, [zero, zero])
        format = self.builder.bitcast(format, ir.IntType(8).as_pointer())
        func, _ = self.variables['printf']
        return self.builder.call(func,[format,*params])

    # NOTE: End builtin functions

    def _config_llvm(self):
        # Config LLVM
        self.module = ir.Module(name="main")
        func_type = ir.FunctionType(ir.VoidType(), [], False)
        base_func = ir.Function(self.module, func_type, name="main")
        block = base_func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)

    def create_execution_engine(self):
        target = llvm.Target.from_default_triple()
        target_machine = target.create_target_machine()
        # Add an execution engine with an empty backing module
        backing_mod = llvm.parse_assembly("")
        engine = llvm.create_mcjit_compiler(backing_mod, target_machine)
        return engine

    def compile_ir(self, engine, llvm_ir):
        ir_ = str(llvm_ir)
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

        value_to_call = self.compile(node.node_to_call, ctx)
        if isinstance(value_to_call, Error):
            return value_to_call

        func_value = Function()
        if value_to_call is not None:
            func_value = value_to_call

        val_cal = func_value.name

        i = 0
        for arg_node in node.arg_nodes:
            new = arg_node.token.value
            new = self.compile(arg_node, ctx)
            if isinstance(new, Array):
                 new = Array(new.elements, new.element_id)

            args.append(new)
            i += 1

        #return_value = val_cal.execute(args)
        return_value = self.variables[val_cal]()

        func_return = func_value.returnType.type_dec.type_obj
        types_match = self.check_types_match(return_value, func_return, return_value.name, ctx, node)
        if types_match is not None:
            return types_match

        return return_value

    def check_types_match(self, a, b, name, ctx, node):
        if a.ID != b.ID:
            pos = node.token.pos
            return RuntimeError(f"Cannot assign value of {a.description} to type {b.description} {name}", ctx, pos)
        return None

    def visit_StringNode(self, node, ctx): pass

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
        return Integer(64, ir_value=ir.Constant(Type, val)), Type

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
        left_ty = left_vst[1]
        left = left_vst[0]

        right_vst = self.compile(node.rhs, ctx)
        if isinstance(right_vst, Error):
            return right_vst
        right_ty = right_vst[1]
        right = right_vst[0]

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

        return result

    def AccessNode(self, node, ctx):
        err = self.check_for_declaration(self.table, node, ctx)
        if err is not None:
            return err
        else:
            return self.visit_VarAccessNode(node, ctx)
