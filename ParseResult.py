class ParseResult:
    def __init__(self, error=None, node=None):
        self.error = error 
        self.node = node 

    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error != None: self.error = res.error 
            return res.node
        else:
            return res 

    def success(self, node):
        self.node = node 
        return node 

    def failure(self, error):
        self.error = error 
        return self.error  
