/* Parse Result */

class ParserResult { 
    var error: Error?
    var node: AbstractNode? 

    init() {
        self.error = nil 
        self.node = nil 
    }

    ///////////////////////////////////////////

    func register(_ res: ParserResult) -> AbstractNode {
        if res.error != nil { self.error = res.error }
        return res.node ?? VariableNode()
    }

    func register(_ _node: AbstractNode) -> AbstractNode {
        return _node
    }

    func register(_ _token: Token ) -> Token {
        return _token 
    }

    ///////////////////////////////////////////

    func success(_ node: AbstractNode) -> AbstractNode {
        self.node = node
        return node 
    }

    func failure(_ error: Error) -> Error {
        self.error = error 
        return self.error!
    }
}