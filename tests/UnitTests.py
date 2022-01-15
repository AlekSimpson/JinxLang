from ..run import run 

class Validator:
    def process_result(self, result, error):
        if error != None:
            print(error.as_string())
        else:
            if len(result.elements) == 1 and len(result.elements) != 0:
                if result.elements[0] != None:
                    print(result.elements[0].print_self())
            else:
                for ele in result.elements:
                    if ele != None:
                        print(ele.print_self())

    def test_Conditionals(self):
        # Setup
        inlineIf    = "if 1 == 1 { print(\"true\") }"
        inlineElif  = "if 1 == 23 { print(\"false\") } elif 1 == 1 { print(\"true\") }"
        inelineElse = "if 1 == 23 { print(\"false\") } elif 1 == 234 { print(\"false\") } else { print(\"true\") }"

        newlineIf    = "if 1 == 1 {; print(\"true\"); }"
        newlineElif  = "if 1 == 23 {; print(\"false\"); } elif 1 == 1 {; print(\"true\"); }"
        newlineElse  = "if 1 == 23 {; print(\"false\"); } elif 1 == 234 {; print(\"false\"); } else {; print(\"true\"); }"

        # Test 
        inlineIfResult, error = run(inlineIf, "InlineIfTest")
        inlineElifResult, error = run(elifResult, "InlineElifTest")
        inlineElseResult, error = run(elseResult, "InlineElseTest")
        
        newlineIfResult, error = run(newlineIf, "NewlineIfTest")
        newlineElifResult, error = run(newlineElif, "NewlineElifTest")
        newlineElseResult, error = run(newlineElse, "NewlineElseTest")

        # Process results
        process_result(inlineIfResult, error)

