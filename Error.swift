import Foundation

/* ERRORS */

class Error {
    var error_name: String 
    var details: String 
    var pos: Position 

    init(error_name: String, details: String, pos: Position) {
        self.error_name = error_name
        self.details = details
        self.pos = pos
    }

    func as_string() -> String {
        return ("\(self.error_name): \(self.details)")
    }
}

class IllegalCharError: Error {
    init(details: String, pos: Position) {
        super.init(error_name: "Illegal Character", details: details, pos: pos)
    }
}

class InvalidSyntaxError: Error {
    init(details: String, pos: Position) {
        super.init(error_name: "Invalid Syntax Error", details: details, pos: pos)
    }
}

class ExpectedCharError: Error {
    init(details: String, pos: Position) {
        super.init(error_name: "Expected Character", details: details, pos: pos)
    }
}

class RuntimeError: Error {
    var context: Context
    init(details: String, context: Context, pos: Position) {
        self.context = context
        super.init(error_name: "Runtime Error", details: details, pos: pos)
    }

    override func as_string() -> String {
        var result = self.generate_traceback()
        result += "\(self.error_name): \(self.details)"
        return result
    }

    func generate_traceback() -> String {
        var result = ""
        var p = self.pos 
        var ctx = self.context
        
        while true {
            if ctx.parent == nil { break }
            result += "\tFile: \(p.fn), line: \(p.ln), in \(ctx.display_name)\n\(result)"
            if let par_pos = ctx.parent_entry_pos { p = par_pos }
            if let par_ctx = ctx.parent { ctx = par_ctx }
        }  

        return "Traceback (most recent call last):\n\(result)"
    }
}