class RuntimeResult:
    def __init__(self, value=None, error=None):
        self.value =  value 
        self.error = error 

    def register(self, result):
        if result.error != None: self.error = result.error 
        self.value = result.value 
        return self 

    def success(self, value):
        self.value = value 
        return self 

    def failure(self, error):
        self.error = error 
        return self 
