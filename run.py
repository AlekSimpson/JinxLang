from lexer import Lexer


def run(text, fn):
    lexer = Lexer(text)
    lexer.make_tokens()


while True:
    textInput = input("sona> ")
    if str(textInput) == "stop":
        break 

    result = run(textInput, "repl")

    # if error != None:
    #     print(error.as_string())
    
    if result != None:
        print(result.print_self())
