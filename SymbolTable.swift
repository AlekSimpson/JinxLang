/* SYMBOL TABLE */

class SymbolTable {
    var symbols = [String:Number]()
    var parent:SymbolTable? = nil 

    init() {
        self.symbols = [String : Number]()
        self.parent = nil
    }

    func get_val(name: String) -> Number {
        let value = symbols[name]
        var returnVal: Number = Number(0.0)

        if let v = value {
            returnVal = v 
        }

        if let p = parent {
            returnVal = p.get_val(name: name)
        }

        return returnVal
    }

    func set_val(name: String, value: Number) {
        self.symbols[name] = value 
    }

    func remove_val(name: String) {
        self.symbols.removeValue(forKey: name)
    }
}