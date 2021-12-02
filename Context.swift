/* CONTEXT */

class Context {
    var display_name: String 
    var parent: Context?
    var parent_entry_pos: Position?

    init(display_name: String, parent: Context?=nil, parent_entry_pos: Position?=nil) {
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
    }

    init() {
        self.display_name = ""
        self.parent = nil 
        self.parent_entry_pos = nil 
    }
}