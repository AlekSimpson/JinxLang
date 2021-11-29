import Foundation

/* ERRORS */

class Error {
    var error_name: String 
    var details: String 

    init(error_name: String, details: String) {
        self.error_name = error_name
        self.details = details
    }

    func as_string() -> String {
        return ("\(self.error_name): \(self.details)")
    }
}

class IllegalCharError: Error {
    init(details: String) {
        super.init(error_name: "Illegal Character", details: details)
    }
}

class InvalidSyntaxError: Error {
    init(details: String) {
        super.init(error_name: "Illegal Character", details: details)
    }
}