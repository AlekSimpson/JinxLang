/* POSITION */

class Position {
    var idx: Int?
    var ln: Int 
    var col: Int 

    init(idx: Int, ln: Int, col: Int) {
        self.idx = idx 
        self.ln = ln 
        self.col = col 
    }

    init(ln: Int, col: Int) {
        self.idx = nil 
        self.ln = ln 
        self.col = col 
    }

    func copy() -> Position {
        // return LinePosition(idx: self.idx, ln: self.ln, col: self.col)
        return self 
    }
}