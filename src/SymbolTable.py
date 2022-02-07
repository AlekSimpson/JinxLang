class SymbolTable:
    def __init__(self, symbols={}, parent=None):
        self.symbols = symbols
        self.parent = parent

    def get_val(self, name):
        from Types import Number

        value = self.symbols[name]
        return_val = Number(0)

        if value is not None:
            return_val = value

        if self.parent is not None:
            return_val = self.parent.get_val(name)

        return return_val

    def set_val(self, name, value):
        self.symbols[name] = value

    def remove_val(self, name):
        del self.symbols[name]
