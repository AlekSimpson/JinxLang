/* POSITION */

class Position {
    var ln: Int 
    var col: Int 
    var fn: String 

    init(ln: Int, col: Int, fn: String) {
        self.ln = ln 
        self.col = col 
        self.fn = fn 
    }

    init() {
        self.ln = 0
        self.col = 0
        self.fn = ""
    }

    func copy() -> Position {
        // return LinePosition(idx: self.idx, ln: self.ln, col: self.col)
        return self 
    }
}