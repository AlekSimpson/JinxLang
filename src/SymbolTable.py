class SymbolTable:
    def __init__(self,  symbols={}, parent=None):
        self.symbols = symbols
        self.parent = parent

    def get_val(self, name):
        from Types import Number
        value = self.symbols[name]
        returnVal = Number(0)

        if value != None:
            returnVal = value

        if self.parent != None:
            returnVal = parent.get_val(name)

        return returnVal

    def set_val(self, name, value):
        self.symbols[name] = value

    def remove_val(self, name):
        del self.symbols[name]

