class ParseResult:
    def __init__(self, error=None, node=None):
        self.error = error 
        self.node = node 
        self.to_reverse_count = 0
        self.advance_count = 0

    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error != None: self.error = res.error 
            return res.node
        else:
            return res 
    
    def try_register(self, res):
        if res.error != None:
            self.to_reverse_count = res.advance_count 
            return None 
        return self.register(res)

    def success(self, node):
        self.node = node 
        return node 

    def failure(self, error):
        self.error = error 
        return self.error  
