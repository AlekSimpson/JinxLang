class Error:
    def __init__(self, error_name, details, pos):
        self.error_name = error_name
        self.details = details
        self.pos = pos

    def as_string(self):
        return f"{self.error_name}: {self.details}"


class IllegalCharError(Error):
    def __init__(self, details, pos):
        super().__init__("IllegalCharError", details, pos)


class InvalidSyntaxError(Error):
    def __init__(self, details, pos):
        super().__init__("InvalidSyntaxError", details, pos)


class ExpectedCharError(Error):
    def __init__(self, details, pos):
        super().__init__(self, "ExpectedCharError", details, pos)


class RuntimeError(Error):
    def __init__(self, details=None, context=None, pos=None):
        super().__init__("Runtime Error", details, pos)
        self.context = context

    def as_string(self):
        result = self.generate_traceback()
        result += f"{self.error_name}: {self.details}"
        return result

    def generate_traceback(self):
        result = f""
        p = self.pos
        ctx = self.context

        #while True:
        #    if ctx.parent is None or p is None:
        #        break
        #    result += f"File: {p.fn}, line: {p.ln}, in {ctx.display_name}\n{result}"
        #    p = ctx.parent_entry_pos
        #    ctx = ctx.parent

        #return f"Traceback:\n{result}"

        if p is not None:
            return f"File: {p.fn}, line: {p.ln}:\n"
        else:
            return ""
