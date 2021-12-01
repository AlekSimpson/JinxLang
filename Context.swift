/* CONTEXT */

class Context {
    var display_name: String 
    var parent: String?
    var parent_entry_pos: String?

    init(display_name: String, parent: String?=nil, parent_entry_pos: String?=nil) {
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
    }
}