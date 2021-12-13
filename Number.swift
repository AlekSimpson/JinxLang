/* NUMBERS */

// This class is for storing numbers
class Number {
    var value: Double 
    var pos: Position?
    var context: Context?

    init(_ value: Double, pos: Position?=nil) {
        self.value = value
        self.pos = pos 
        self.set_context()
    }

    init() {
        self.value = 0.0
        self.pos = nil
    }

    func set_context(ctx: Context?=nil) {
        self.context = ctx 
    }

    func added(to other: Number) -> (Number?, Error?) {
        let new_num = Number(self.value + other.value)
        new_num.set_context(ctx: other.context)
        return (new_num, nil)
    }

    func subtracted(from other: Number) -> (Number?, Error?) {
        let new_num = Number(self.value - other.value)
        new_num.set_context(ctx: other.context)
        return (new_num, nil)
    }

    func multiplied(by other: Number) -> (Number?, Error?) {
        let new_num = Number(self.value * other.value)
        new_num.set_context(ctx: other.context)
        return (new_num, nil)
    }

    func divided(by other: Number) -> (Number?, Error?) {
        var p = Position()
        if let position = self.pos { p = position }

        let new_num = Number(self.value / other.value)
        new_num.set_context(ctx: other.context)

        var c = Context()
        if let ctx = self.context { c = ctx }
        if other.value == 0 { return (nil, RuntimeError(details: "cannot divide by zero", 
                                                        context: c, 
                                                        pos: p)) }

        return (new_num, nil)
    }

    func power(by other: Number) -> (Number?, Error?) {
        let new_num = Number(pow(self.value, other.value))
        new_num.set_context(ctx: other.context)
        return (new_num, nil)
    }

    func comp_eq(by other: Number) -> (Number?, Error?) {
        let new_num = Number((self.value == other.value ? 1 : 0))
        new_num.set_context(ctx: other.context)
        return (new_num, nil)
    }

    func comp_ne(by other: Number) -> (Number?, Error?) {
        let new_num = Number((self.value != other.value ? 1 : 0))
        new_num.set_context(ctx: other.context)
        return (new_num, nil)
    }

    func comp_lt(by other: Number) -> (Number?, Error?) {
        let new_num = Number((self.value < other.value ? 1 : 0))
        new_num.set_context(ctx: other.context)
        return (new_num, nil)
    }

    func comp_gt(by other: Number) -> (Number?, Error?) {
        let new_num = Number((self.value > other.value ? 1 : 0))
        new_num.set_context(ctx: other.context)
        return (new_num, nil)
    }

    func comp_loe(by other: Number) -> (Number?, Error?) {
        let new_num = Number((self.value <= other.value ? 1 : 0))
        new_num.set_context(ctx: other.context)
        return (new_num, nil)
    }

    func comp_goe(by other: Number) -> (Number?, Error?) {
        let new_num = Number((self.value >= other.value ? 1 : 0))
        new_num.set_context(ctx: other.context)
        return (new_num, nil)
    }

    func comp_and(by other: Number) -> (Number?, Error?) {
        let new_num = Number((self.value == 1 && other.value == 1 ? 1 : 0))
        new_num.set_context(ctx: other.context)
        return (new_num, nil)
    }

    func comp_or(by other: Number) -> (Number?, Error?) {
        let new_num = Number((self.value == 1 || other.value == 1 ? 1 : 0))
        new_num.set_context(ctx: other.context)
        return (new_num, nil)
    }

    func not() -> (Number?, Error?) {
        let new_num = Number((self.value == 1 ? 0 : 1))
        new_num.set_context(ctx: self.context)
        return (new_num, nil)
    }

    func is_true() -> Bool {
        return self.value != 0.0
    }

    func print_self() -> String {
        return "\(self.value)"
    }
}


class Function: Number {
    var name: String?
    var body_node: AbstractNode
    var arg_nodes: [String]?

    init(name: String?="anonymous", body_node: AbstractNode, arg_nodes: [String]?=nil) {
        self.name = name 
        self.body_node = body_node
        self.arg_nodes = arg_nodes
        super.init()
    }

    override init() {
        self.name = ""
        self.body_node = BinOpNode()
        self.arg_nodes = nil 
        super.init()
    }

    func execute(args: [Number]) -> (Number?, RuntimeResult) {
        let res = RuntimeResult()
        let interpreter = Interpreter()

        var str = ""
        if let s = name { str = s }

        let new_context = Context(display_name: str, parent: self.context, parent_entry_pos: self.pos)
        var par = Context()
        if let p = new_context.parent { par = p }
        new_context.symbolTable = par.symbolTable

        var a_nodes: [String] = []
        if let a = self.arg_nodes { a_nodes = a }

        var pos = Position()
        if let unwrapped = body_node.token.pos { pos = unwrapped }


        if args.count != 0 {
            if args.count > a_nodes.count {
                let err = RuntimeError(details: "to many arguements passed into function \(String(describing: name))", context: new_context, pos: pos)
                _ = res.failure(err)
                return (nil, res)
            }

            if args.count < a_nodes.count {
                let err = RuntimeError(details: "to few arguements passed into function \(String(describing: name))", context: new_context, pos: pos)
                _ = res.failure(err)
                return (nil, res)
            }

            for i in 0...(a_nodes.count - 1) {
                let arg_name = a_nodes[i] 
                let arg_value = args[i]
                arg_value.set_context(ctx: new_context)
                var sTable = SymbolTable()
                if let unwrapped = new_context.symbolTable { sTable = unwrapped }
                sTable.set_val(name: arg_name, value: arg_value)
            }
        }

        let body_res = interpreter.visit(node: self.body_node, context: new_context)
        _ = res.register(body_res)
        let value = res.value
        if res.error != nil { return (nil, res) }
        self.context = new_context
        return (value, res)
    }

    func copy() -> Function {
        let copy = Function(name: self.name, body_node: self.body_node, arg_nodes: self.arg_nodes) 
        copy.set_context(ctx: self.context)
        return copy 
    }

    override func print_self() -> String {
        return "<function \(self.name ?? "lambda")>"
    }
}