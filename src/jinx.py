from run import run
import sys
from Context import Context
from Position import Position
from Error import *

if len(sys.argv) == 1:
    while True:
        textInput = input("jinx> ")
        if textInput == "":
            continue
        if str(textInput) == "stop":
            break

        result = run(textInput, "repl")

        if isinstance(result, Error):
            print(result.as_string())
        elif result is not None:
            if len(result.elements) == 1:
                if result.elements[0] is not None:
                    print(result.elements[0].print_self())
            else:
                for ele in result.elements:
                    if ele is not None:
                        print(ele.print_self())
else:
    filename = sys.argv[1]
    script = None
    try:
        with open(filename, "r") as f:
            script = f.read()
    except Exception as e:
        err = RuntimeError("Failed to execute file" + str(e), Context(), Position())
        print(err.as_string())

    result = run(script, filename)

    if isinstance(result, Error):
        print(result.as_string())
