from run import run

while True:
    textInput = input("aqua> ")
    if textInput == "": continue
    if str(textInput) == "stop":
        break 

    result, error = run(textInput, "repl")

    if error != None: 
        print(error.as_string())
    elif result != None:
        if len(result.elements) == 1 and len(result.elements) != 0:
            if result.elements[0] != None:
                print(result.elements[0].print_self())
        else:
            for ele in result.elements:
                if ele != None: 
                    print(ele.print_self())

