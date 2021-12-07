/* RUNTIME RESULT */

class RuntimeResult {
    var value: Number? 
    var error: Error?

    init(value: Number, error: Error){
        self.value = value 
        self.error = error 
    }

    init() {
        self.value = nil 
        self.error = nil 
    }
    
    func register(_ result: RuntimeResult) -> RuntimeResult {
        if result.error != nil { self.error = result.error } 
        self.value = result.value
        return self 
    } 

    func success(_ value: Number) -> RuntimeResult {
        self.value = value 
        return self 
    }

    func failure(_ error: Error) -> RuntimeResult {
        self.error = error 
        return self
    }
}