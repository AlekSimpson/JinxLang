from run import run
import sys

if len(sys.argv) == 1:
    while True:
        textInput = input("laplace> ")
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
else:
    filename = sys.argv[1]
    script = None 
    try:
        with open(filename, "r") as f:
            script = f.read()
    except Exception as e:
        err = RuntimeError("Failed to execute file" + str(e), Context(), Position())
        res.failure(err)
        print(err.as_string())
    
    result, error = run(script, filename)

    if error != None: 
        print(error.as_string())
    #elif result != None:
    #    if len(result.elements) == 1 and len(result.elements) != 0:
    #        if result.elements[0] != None:
    #            print(result.elements[0].print_self())
    #    else:
    #        for ele in result.elements:
    #            if ele != None: 
    #                print(ele.print_self())
   


