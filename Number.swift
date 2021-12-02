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

    func set_context(ctx: Context?=nil) {
        self.context = ctx 
    }

    func added(to other: Number) -> (Number?, Error?) {
        let new_num = Number(self.value + other.value)
        new_num.set_context(ctx: other.context)
        return (new_num, nil)
    }

    func subtracted(from other: Number) -> (Number?, Error?) {
        let new_num = Number(self.value + other.value)
        new_num.set_context(ctx: other.context)
        return (new_num, nil)
    }

    func multiplied(by other: Number) -> (Number?, Error?) {
        let new_num = Number(self.value + other.value)
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

    func print_self() -> String {
        return "\(self.value)"
    }
}
