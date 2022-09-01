from Error import *
import tokens as tk
from tokens import Token
from Types import *
from Position import Position
from TypeValue import TypeValue
from Types import Function, FunctionIrPackage, Type
from Node import *
from tokens import *
from Parser import DotNode

from llvmlite import ir
import llvmlite.binding as llvm
from ctypes import CFUNCTYPE

class Compiler:
    def __init__(self, unit_testing=False):
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()
        self.table = None
        self.debug = False
        self.unit_testing = unit_testing
        self._config_llvm()
        if not self.unit_testing:
            self.init_string_formats()

        printf_ty = ir.FunctionType(ir.IntType(64), [ir.IntType(8).as_pointer()], var_arg=True)
        printf = ir.Function(self.module, printf_ty, name="printf")

        if "Array" not in ir.global_context.identified_types:
            self.array_type = ir.global_context.get_identified_type("Array")
            arr_attrs = [ir.IntType(64).as_pointer()]
            self.array_type.set_body(*arr_attrs)
        else:
            self.array_type = ir.global_context.identified_types["Array"]
        if "String" not in ir.global_context.identified_types:
            self.string_type = ir.global_context.get_identified_type("String")
            string_attrs = [ir.IntType(8).as_pointer()]
            self.string_type.set_body(*string_attrs)
        else:
            self.string_type = ir.global_context.identified_types["String"]

        self.builtin = {'print' : (printf, self.printf)}

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

        flt_c_fmt = ir.Constant(ir.ArrayType(ir.IntType(8), len("%.2f\n\0")), bytearray("%.2f\n\0".encode("utf8")))
        self.flt_global_fmt = ir.GlobalVariable(self.module, flt_c_fmt.type, name="flt_str")
        self.flt_global_fmt.linkage = 'internal'
        self.flt_global_fmt.global_constant = True
        self.flt_global_fmt.initializer = flt_c_fmt

    def generate_new_context(self, name, parent_ctx=None):
        new_context = Context(name, parent_ctx, None)
        new_context.symbolTable = parent_ctx.symbolTable
        return new_context

    # MARK: This function initializes Jinx Structures
    def initialize_object(self, object, values, parent_ctx):
        if len(values) > len(object.attr_names):
            return RuntimeError(f"Given amount of parameters exceeds object {object.name}'s initialization parameters", Position(), parent_ctx)
        elif len(values) < len(object.attr_names):
            return RuntimeError(f"Given amount of parameters does not meet object {object.name}'s amount of initialization parameters", Position(), parent_ctx)

        concrete_obj = Object(object.name, attr_names=object.attr_names)

        block = self.builder.append_basic_block(f'{object.name}_entry')
        previous_builder = self.builder

        self.builder = ir.IRBuilder(block)
        concrete_obj.builder = self.builder

        params = []
        i = 0
        for val in values:
            concrete_obj.values[concrete_obj.attr_names[i]] = val
            params.append(val.ir_value)
            i = i + 1

        # initialize object ir_value
        obj_irval = ir.Constant.literal_struct(params)
        obj_ptr = self.builder.alloca(obj_irval.type)

        self.builder.store(obj_irval, obj_ptr)

        i = 0
        for name in object.attr_names:
            zero = ir.Constant(ir.IntType(32), 0)
            index = ir.Constant(ir.IntType(32), i)
            ptr = self.builder.gep(obj_ptr, [zero, index])
            concrete_obj.context.symbolTable.set_val(name, ptr)
            i += 1

        concrete_obj.ir_value = obj_irval
        concrete_obj.ptr = ptr

        parent_ctx.symbolTable.set_val(object.name, concrete_obj)

        # Compile body node under object context
        self.compile(object.body_node, object.context)

        self.builder.ret_void()

        # move builder back to top level
        self.builder = previous_builder

        return concrete_obj

    def printf(self, params):
        arg = params[0]
        printf = self.builtin['print'][0]
        zero = ir.Constant(ir.IntType(32), 0)
        # Check if arg is a complex type, if so we need to print its string representation
        if isinstance(arg, Object):
            str_value = arg.name + "\0"
            c_str_val = ir.Constant(ir.ArrayType(ir.IntType(8), len(str_value)),
                           bytearray(str_value.encode("utf8")))
            arg = string(str_value=str_value, ir_value=c_str_val)

        fmt = self.int_global_fmt
        if arg.ptr is not None:
            arg = arg.ptr

            if arg.type == ir.PointerType(self.array_type):
                #NOTE:: Only prints first element of array but should print more

                # get array attribute of array
                arg = self.builder.gep(arg, [zero, zero])
                # load array attribute
                arg = self.builder.load(arg)
                # get first element of array
                arg = self.builder.gep(arg, [ir.Constant(ir.IntType(64), 0)])
                ## load array
                arg = self.builder.load(arg)
            elif arg.type == ir.PointerType(ir.IntType(64)):
                arg = self.builder.load(arg)
            elif arg.type == ir.PointerType(self.string_type):
                fmt = self.str_global_fmt

                arg = self.builder.gep(arg, [zero, zero])
                arg = self.builder.load(arg)
            elif isinstance(arg.type, ir.DoubleType):
                fmt = self.flt_global_fmt
        else:
            if isinstance(arg, string):
                fmt = self.str_global_fmt
            elif isinstance(arg, Float):
                fmt = self.flt_global_fmt

            arg = arg.ir_value

            if isinstance(arg.type, ir.ArrayType):
                before = arg
                arg = self.builder.alloca(arg.type)
                self.builder.store(before, arg)

        voidptr_ty = ir.IntType(8).as_pointer()
        fmt_arg = self.builder.bitcast(fmt, voidptr_ty)
        self.builder.call(printf, [fmt_arg, arg])

    # NOTE: End builtin functions

    def _config_llvm(self):
        # Config LLVM
        self.module = ir.Module(name="main")
        func_type = ir.FunctionType(ir.VoidType(), [], False)
        self.base_func = ir.Function(self.module, func_type, name="main")
        self.block = self.base_func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(self.block)

    def create_execution_engine(self):
        target = llvm.Target.from_default_triple()
        target_machine = target.create_target_machine()
        # Add an execution engine with an empty backing module
        backing_mod = llvm.parse_assembly(str(self.module))
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

        if self.debug:
            print("==================================")
            print(str(ir_))
            print("==================================")
        if self.unit_testing:
            return str(ir_)

        engine = self.create_execution_engine()
        mod = self.compile_ir(engine, ir_)
        return mod

    def check_for_error(self, node):
        if isinstance(node, Error):
            return node
        return None

    def compile(self, node, context, debug=False):
        err_check = self.check_for_error(node)
        if err_check is not None:
            return err_check
        if node is None:
            return

        func_index = node.classType
        if self.debug or debug:
            print(f"[{func_index}] - {node.as_string()}")

        self.table = context.symbolTable.symbols
        result = None

        visit_map = [
            self.visit_binop,          # 0  |
            self.visit_number,         # 1  |
            "VariableNode",            # 2  |
            self.visit_unary,          # 3  |
            self.AccessNode,           # 4  |
            self.visit_VarAssignNode,  # 5  |
            self.visit_IfNode,         # 6  |
            self.visit_ForNode,        # 7  |
            self.visit_WhileNode,      # 8  |
            self.visit_FuncDefNode,    # 9  |
            self.visit_CallNode,       # 10 |
            self.visit_StringNode,     # 11 |
            self.visit_ListNode,       # 12 |
            self.visit_SetArrNode,     # 13 x
            self.visit_GetArrNode,     # 14 |
            self.visit_ReturnNode,     # 15 |
            self.visit_VarUpdateNode,  # 16 |
            self.visit_float,          # 17 |
            self.visit_ObjectDefNode,  # 18 |
            self.visit_DotNode,        # 19 |
        ]

        if func_index < 0 or func_index > 19:
            return RuntimeError("No visit methods found", context, Position()) # Should probably pass in a real position here at some point
        result = visit_map[func_index](node, context)

        return result

    def visit_unary(self, node, ctx):
        val = node.token.value

        Type = ir.IntType(64)
        if node.op_tok.type_name == tk.TT_MINUS:
            return Integer(64, ir_value=ir.Constant(Type, (val * -1)))
        elif node.op_tok.type_name == tk.TT_NOT:
            return Integer(64, ir_value=ir.Constant(Type, (0 if val == 1 else 1)))

    def visit_VarAssignNode(self, node, ctx):
        var_name = node.token.value
        value = self.compile(node.value_node, ctx)
        if isinstance(value, Error):
            return value

        if var_name not in ctx.symbolTable.symbols:
            # This allocates the string pointer so that we are with a reference to the string instead of directly with the string array
            # Doing this because we need to be able to hide the size of the string/array so that we can pass it into functions and stuff like that
            if not isinstance(value, string):
                ptr = self.builder.alloca(value.ir_value.type)
                value.ptr = ptr
                self.builder.store(value.ir_value, ptr)
            else:
                ptr = self.builder.alloca(value.ptr.type)
                self.builder.store(value.ptr, ptr)
            ctx.symbolTable.set_val(var_name, value)

        return value

    def else_if_block(self, case, ctx, itr, node):
        max_len = len(node.cases) - 1
        condition_value = self.compile(case[0], ctx)
        if isinstance(condition_value, Error):
            return condition_value

        with self.builder.if_else(condition_value.ir_value) as (true, otherwise):
            with true:
                self.compile(case[1], ctx)

            if itr == max_len:
                with otherwise:
                    self.compile(node.else_case[0], ctx)
            else:
                with otherwise:
                    self.else_if_block(node.cases[itr + 1], ctx, itr + 1, node)

    def visit_IfNode(self, node, ctx):
        cases = node.cases
        else_case = node.else_case

        condition_value = self.compile(cases[0][0], ctx)
        if isinstance(condition_value, Error):
            return condition_value

        if else_case is None:
            with self.builder.if_then(condition_value.ir_value):
                return self.compile(cases[0][1], ctx)
        else:
            self.else_if_block(node.cases[0], ctx, 0, node)

    def create_iterator(self, node, startValue, ctx):
        iterator = node.iterator
        sVal = self.compile(startValue, ctx)
        sValNode = NumberNode(Token(tk.MT_FACTOR, tk.TT_INT, sVal.value, type_dec=TypeValue(1, Integer(64))))
        itr = VarAssignNode(Token(value=iterator.token.value), sValNode, type=TypeValue(1, Integer(64)))
        self.compile(itr, ctx)

        itr_access = VarAccessNode(Token(value=iterator.token.value))
        op_node = VariableNode(Token(tk.MT_NONFAC, tk.TT_LOE, "<="))
        condition_node = BinOpNode(itr_access, op_node, node.endValue)
        condition = self.compile(condition_node, ctx)

        return condition, condition_node

    def append_inc_to_for_body(self, node):
        body = node.bodyNode
        itr = VarAccessNode(Token(value=node.iterator.token.value))
        one = NumberNode(Token(tk.MT_FACTOR, tk.TT_INT, 1, type_dec=TypeValue(1, Integer(64))))
        # increment instructions
        op_node = VariableNode(Token(tk.MT_NONFAC, tk.TT_PLUS, "+"))
        increment_node = BinOpNode(itr, op_node, one)
        # update instructions
        update = VarUpdateNode(node.iterator.token, increment_node)
        #body.element_nodes.append(update)

    def visit_ForNode(self, node, ctx):
        itr = 0
        body = node.bodyNode
        startValue = node.startValue
        condition, condition_node = self.create_iterator(node, startValue, ctx)
        if isinstance(condition, Error):
            return condition
        self.append_inc_to_for_body(node)

        for_loop_entry = self.builder.append_basic_block("for_loop_entry"+str(itr + 1))

        for_loop_otherwise = self.builder.append_basic_block("for_loop_otherwise"+str(itr))

        self.builder.cbranch(condition.ir_value, for_loop_entry, for_loop_otherwise)

        self.builder.position_at_start(for_loop_entry)
        self.compile(body, ctx)
        condition = self.compile(condition_node, ctx)
        if isinstance(condition, Error):
            return condition
        self.builder.cbranch(condition.ir_value, for_loop_entry, for_loop_otherwise)
        self.builder.position_at_start(for_loop_otherwise)

    def visit_WhileNode(self, node, ctx):
        itr = 0
        condition = self.compile(node.conditionNode, ctx)
        if isinstance(condition, Error):
            return condition
        body = node.bodyNode

        while_loop_entry = self.builder.append_basic_block("while_loop_entry"+str(itr + 1))

        while_loop_otherwise = self.builder.append_basic_block("while_loop_otherwise"+str(itr))

        self.builder.cbranch(condition.ir_value, while_loop_entry, while_loop_otherwise)

        self.builder.position_at_start(while_loop_entry)
        self.compile(body, ctx)
        condition = self.compile(node.conditionNode, ctx)
        if isinstance(condition, Error):
            return condition
        self.builder.cbranch(condition.ir_value, while_loop_entry, while_loop_otherwise)
        self.builder.position_at_start(while_loop_otherwise)

    def visit_SetArrNode(self, node, ctx): pass

    def visit_GetArrNode(self, node, ctx):
        # should return pointer to array
        array = self.compile(node.array, ctx)
        if isinstance(array, Error):
            return array

        index = self.compile(node.index, ctx)
        if isinstance(index, Error):
            return index

        # get needed index constants
        zero = ir.Constant(ir.IntType(32), 0)
        ir_index = ir.Constant(ir.IntType(32), index.value)
        # load array pointer
        arr_ptr = array.ptr
        if arr_ptr.type != ir.PointerType(self.array_type):
            arr_ptr = self.builder.load(array.ptr)

        # get array attribute of Array
        ir_array = self.builder.gep(arr_ptr, [zero, zero])
        # load array attribute
        ir_array = self.builder.load(ir_array)
        # get the pointer to the desired index
        ir_array = self.builder.gep(ir_array, [ir_index])
        # Load value at index and return it
        retval = self.builder.load(ir_array)

        val = Type(ir_value=retval)
        return val

    def visit_ReturnNode(self, node, ctx):
        if node.node_to_return is None:
            self.builder.ret_void()
            return
        else:
            ret_val = self.compile(node.node_to_return, ctx)
            if ret_val.ir_value is not None:
                ret_val = ret_val.ir_value
            elif ret_val.ptr is not None:
                ret_val = self.builder.load(ret_val.ptr)
            else:
                return RuntimeError("Expected return value", ctx, Position())

        self.builder.ret(ret_val)

    def types_match(self, a, b, ctx):
        if a.type != b.type:
            return RuntimeError(f"Mismatched Types: Cannot assign value of type {b.type}, to type {a.type}", ctx, Position())
        return None

    def visit_VarUpdateNode(self, node, ctx):
        var_name = node.token.value
        new_val = self.compile(node.value_node, ctx)

        if isinstance(new_val, Error):
            return new_val

        if var_name in ctx.symbolTable.symbols:
            storage = ctx.symbolTable.get_val(var_name)
            types_match = self.types_match(storage.ir_value, new_val.ir_value, ctx)
            if isinstance(types_match, Error):
                return types_match

            storage.ir_value = new_val.ir_value
            if isinstance(storage, Array):
                storage.elements = new_val.elements
                storage.description = f"{storage.print_self()}"

            ptr = storage.ptr
            self.builder.store(new_val.ir_value, ptr)
            ctx.symbolTable.set_val(var_name, storage)
        else:
            return RuntimeError(f"UndefVarError: {var_name} is not defined")

        return new_val

    def visit_float(self, node, ctx):
        val = node.token.value

        Type = ir.DoubleType()
        return Float(64, value=val, ir_value=ir.Constant(Type, val))

    def visit_ObjectDefNode(self, node, ctx):
        obj_name = node.name.value
        body_node = node.body_node

        obj_arg_names = []
        obj_arg_types = []

        for n in node.attribute_name_tokens:
            obj_arg_names.append(n.value)

        for n in node.attribute_type_tokens:
            obj_arg_types.append(n.type_dec.type_obj.ir_type)

        objty = ir.global_context.get_identified_type(obj_name)
        objty.set_body(*obj_arg_types)

        object = Object(obj_name, body_node, obj_arg_names, obj_arg_types, ir_value=objty)
        ctx.symbolTable.set_val(obj_name, object)

    #NOTE:: This is temporary, should be copied in the bootstrap compiler
    #       it is necessary now because the Parser creates a SINGLE DotNode and that node holds the ENTIRE chain in a list
    #       it should instead be a chain of DotNodes, each comprised of exactly one LHS slot and one RHS slot
    def find_dotnodes(self, nodes):
        list_ = nodes
        list_.reverse()
        new_node = DotNode(rhs=list_[0])
        del list_[0]
        first_node = new_node
        first_pass = True

        for node in list_:
            if node == list_[-1]:
                new_node.lhs = node
                break
            else:
                new_node.lhs = DotNode(rhs=node)
                new_node = new_node.lhs

        return first_node

    def visit_DotNode(self, node, ctx):
        zero = ir.Constant(ir.IntType(32), 0)
        node_ = node
        if isinstance(node.lhs, list):
            node.lhs.append(node.rhs)
            node_ = self.find_dotnodes(node.lhs)

        obj = self.compile(node_.lhs, ctx)

        idx = obj.attr_table[node_.rhs.token.value]

        ir_idx = ir.Constant(ir.IntType(32), idx)

        ptr = self.builder.gep(obj.ptr, [zero, ir_idx])

        val = Type(ptr=ptr)
        test = obj.values[node_.rhs.token.value]
        if not isinstance(test, Object):
            return val

        val.attr_table = test.attr_table
        val.values = test.values
        return val

    def visit_VarAccessNode(self, node, ctx):
        if node.token.value in self.builtin:
            ptr = self.builtin[node.token.value]
        else:
            ptr = ctx.symbolTable.get_val(node.token.value)
        return ptr

    def visit_FuncDefNode(self, node, ctx):
        name = node.token.value
        body_node = node.body_node

        func_arg_names = []
        func_arg_types = []

        for n in node.arg_name_tokens:
            func_arg_names.append(n.value)

        for n in node.arg_type_tokens:
            typ = n.type_dec.type_obj.ir_type
            if isinstance(typ, str):
                typ = ir.global_context.get_identified_type(typ).as_pointer()

            func_arg_types.append(typ)

        return_type = node.returnType.type_dec.type_obj.ir_type

        fnty = ir.FunctionType(return_type, func_arg_types)
        func = ir.Function(self.module, fnty, name=name)

        block = func.append_basic_block(f'{name}_entry')
        previous_builder = self.builder

        self.builder = ir.IRBuilder(block)
        params_ptr = []

        new_ctx = self.generate_new_context(name, ctx)

        ### stores pointers in SymbolTable
        i = 0
        for arg in func.args:
            val = Type(ptr=arg)
            arg_name = func_arg_names[i]

            new_ctx.symbolTable.set_val(arg_name, val)
            i = i + 1

        ir_pack = FunctionIrPackage(new_ctx, func_arg_types, func_arg_names, params_ptr, self.builder)
        ctx.symbolTable.set_val(name, Function(name, return_type, ir_value=func, ir_type=fnty, ir_pack=ir_pack))

        self.compile(body_node, new_ctx)

        self.builder = previous_builder

    def visit_CallNode(self, node, ctx):
        args = []
        types = []

        value_to_call = self.compile(node.node_to_call, ctx)
        if isinstance(value_to_call, Error):
            return value_to_call

        val_cal = node.node_to_call.token.value

        # get args and their types
        i = 0
        for arg_node in node.arg_nodes:
            new = arg_node.token.value
            new = self.compile(arg_node, ctx)
            typ = ir.IntType(64)

            args.append(new)
            types.append(typ)
            i += 1

        if val_cal in self.builtin:
            # Builtin Function
            builtin_func = self.builtin[val_cal][1]
            ret = builtin_func(args)
        else:
            func = ctx.symbolTable.get_val(val_cal)

            # Defined Function
            ir_args = []
            for arg in args:
                if isinstance(arg, string):
                    ir_args.append(arg.bt_ptr)
                else:
                    ir_args.append(arg.ir_value)

            if isinstance(func, Object):
                conc_obj = self.initialize_object(func, args, ctx)
                return conc_obj
            else: # its a function
                ret = self.builder.call(func.ir_value, ir_args)

        # NOTE:: This probably shouldn't be blindly converted to an Int but I can change it later
        convToValue = Integer(64, ir_value=ret)
        return convToValue

    def check_types_match(self, a, b, name, ctx, node):
        if a.ID != b.ID:
            pos = node.token.pos
            return RuntimeError(f"Cannot assign value of {a.description} to type {b.description} {name}", ctx, pos)
        return None

    def visit_StringNode(self, node, ctx):
        str_value = node.token.value + "\0"
        c_str_val = ir.Constant(ir.ArrayType(ir.IntType(8), len(str_value)), bytearray(str_value.encode("utf8")))
        zero = ir.Constant(ir.IntType(32), 0)

        c_str_ptr = self.builder.alloca(c_str_val.type)
        self.builder.store(c_str_val, c_str_ptr)

        str_first_el = self.builder.gep(c_str_ptr, [zero, zero])

        str_ptr = self.builder.alloca(self.string_type)
        str_attr = self.builder.gep(str_ptr, [zero, zero])
        self.builder.store(str_first_el, str_attr)

        # create string type
        str_ = string(str_value=str_value, ir_value=c_str_val, ptr=str_ptr, bt_ptr=str_ptr)
        return str_

    def visit_ListNode(self, node, ctx):
        zero = ir.Constant(ir.IntType(32), 0)
        elements = []
        ir_elements = []

        for element_node in node.element_nodes:
            el = self.compile(element_node, ctx)
            elements.append(el)
            if node.actually_array:
                ir_elements.append(el.ir_value)

            if isinstance(el, Error):
                return el

            if element_node.classType == 15:
                break

        if node.actually_array:
            complextype = False
            typ = elements[0].ir_type
            if isinstance(elements[0].ir_type, str):
                complextype = True
                typ = ir.global_context.get_identified_type(typ).as_pointer()
            arr_ty = ir.ArrayType(typ, len(ir_elements))
            arr_ir = ir.Constant(arr_ty, ir_elements)

            arr_ptr = self.builder.alloca(arr_ir.type)
            self.builder.store(arr_ir, arr_ptr)

            first_arr_el = self.builder.gep(arr_ptr, [zero, zero])
            if complextype:
                first_arr_el = self.builder.bitcast(first_arr_el, ir.IntType(64).as_pointer())

            ir_arr = self.builder.alloca(self.array_type)
            gep = self.builder.gep(ir_arr, [zero, zero])
            self.builder.store(first_arr_el, gep)

            arr = Array(elements, ir_value=ir_arr, ptr=gep)
            arr.set_context(ctx)

            return arr

    def visit_number(self, node, ctx):
        val = node.token.value

        Type = ir.IntType(64)
        return Integer(64, value=val, ir_value=ir.Constant(Type, val))

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

        left_vst = self.compile(node.lhs, ctx)
        if isinstance(left_vst, Error):
            return left_vst
        left = left_vst

        right_vst = self.compile(node.rhs, ctx)
        if isinstance(right_vst, Error):
            return right_vst
        right = right_vst

        op_node = node.op
        name_cond = op_node.token.type_name

        # NOTE: should clean this up with an array or something
        if left.ptr is not None:
            if left.ptr.type == ir.IntType(64):
                left = Integer(64, ir_value=left.ptr)
        if right.ptr is not None:
            if right.ptr.type == ir.IntType(64):
                right = Integer(64, ir_value=right.ptr)
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
                result = left.comp_eqc(right, self.builder)
            elif name_cond == tk.TT_NE:
                result = left.comp_nec(right, self.builder)
            elif name_cond == tk.TT_LT:
                result = left.comp_ltc(right, self.builder)
            elif name_cond == tk.TT_GT:
                result = left.comp_gtc(right, self.builder)
            elif name_cond == tk.TT_LOE:
                result = left.comp_loec(right, self.builder)
            elif name_cond == tk.TT_GOE:
                result = left.comp_goec(right, self.builder)
            elif name_cond == tk.TT_AND:
                result = left.comp_andc(right, self.builder)
            elif name_cond == tk.TT_OR:
                result = left.comp_orc(right, self.builder)
            else:
                result = Number(0)

        if isinstance(result.type, ir.IntType):
            num = Integer(64, ir_value=result)
        else:
            num = Float(64, ir_value=result)

        return num

    def AccessNode(self, node, ctx):
        err = self.check_for_declaration(self.table, node, ctx)
        if err is not None:
            return err
        else:
            return self.visit_VarAccessNode(node, ctx)
