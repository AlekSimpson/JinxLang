import sys 
sys.path.append("/Users/aleksimpson/desktop/projects/aqua/src/") 
import run
from TestSetups import *
from termcolors import bcolors as bc 

class Validator:
    def process_result(self, result, error):
        returnVal = None 
        if error != None:
            returnVal = error.as_string()
        else:
            if len(result.elements) == 1 and len(result.elements) != 0:
                if result.elements[0] != None:
                    returnVal = result.elements[0].value 
            else:
                for ele in result.elements:
                    if ele != None:
                        returnVal = ele.value
        return returnVal 
    
    def run_tests(self):
        passed = []
        failed = []
        
        print("\n")
        for i in range(0, len(setups)):
            s = setups[i][0]
            n = setups[i][1]
            c = setups[i][2]
            res = self.run_test(s, n, c)
            
            for r in res:
                if r:
                    passed.append(r)
                else:
                    failed.append(r)
        print(f"------------------------- {len(passed)} Passed, {len(failed)} failed -------------------------")

    def run_test(self, codeSamples, testNames, correct):
        # Run tests 
        results = []

        for i in range(0, len(codeSamples)):
            result, error = run.run(codeSamples[i], testNames[i])
            results.append(self.process_result(result, error))

        # Process results
        test_results = []
        for i in range(0, len(codeSamples)):
            res = results[i]
            name = testNames[i]

            if res == correct:
                print(f"{bc.OKGREEN}[ PASSED ] - {name}\n{bc.ENDC}")
            else:
                print(f"{bc.FAIL}[ FAILED ] - {name}, with results:\n\t{res}\n{bc.ENDC}")
            test_results.append(res == correct)
        return test_results

validator = Validator()
validator.run_tests()
