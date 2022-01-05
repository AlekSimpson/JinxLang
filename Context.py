from SymbolTable import SymbolTable 

class Context:
    def __init__(self, display_name=None, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent 
        self.parent_entry_pos = parent_entry_pos
        self.symbolTable = SymbolTable()
