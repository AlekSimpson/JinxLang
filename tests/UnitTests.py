import sys
from sys import platform

if platform == "linux" or platform == "linux2":
    sys.path.append("/home/alek/Desktop/projects/aqua/src/")
elif platform == "darwin":
    sys.path.append("/Users/aleksimpson/desktop/projects/aqua/src/")

import run
from TestSetups import *
from termcolors import bcolors as bc


class Validator:
    def process_result(self, result, error):
        return_val = None
        if error is not None:
            return_val = error.as_string()
        else:
            if len(result.elements) == 1 and len(result.elements) != 0:
                if result.elements[0] is not None:
                    return_val = result.elements[0].value
            else:
                for ele in result.elements:
                    if ele is not None:
                        return_val = ele.value
        return return_val

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
        print(
            f"------------------------- {len(passed)} Passed, {len(failed)} failed -------------------------"
        )

    def run_test(self, code_samples, test_names, correct):
        # Run tests
        results = []

        for i in range(0, len(code_samples)):
            result, error = run.run(code_samples[i], test_names[i])
            results.append(self.process_result(result, error))

        # Process results
        test_results = []
        for i in range(0, len(code_samples)):
            res = results[i]
            name = test_names[i]

            if res == correct:
                print(f"{bc.OKGREEN}[ PASSED ] - {name}\n{bc.ENDC}")
            else:
                print(
                    f"{bc.FAIL}[ FAILED ] - {name}, with results:\n\t{res}\n{bc.ENDC}"
                )
            test_results.append(res == correct)
        return test_results


validator = Validator()
validator.run_tests()
