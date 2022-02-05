import sys
from sys import platform

if platform == "linux" or platform == "linux2":
    sys.path.append("/home/alek/Desktop/projects/aqua/src/")
elif platform == "darwin":
    sys.path.append("/Users/aleksimpson/desktop/projects/aqua/src/")

import run
import Error
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
            res = self.run_package(setups[i])

            for r in res:
                if r:
                    passed.append(r)
                else:
                    failed.append(r)
        print(
            f"------------------------- {len(passed)} Passed, {len(failed)} Failed -------------------------"
        )

    def run_package(self, package):
        package_results = []
        msgs = []

        for test in package[0]:
            res = self.run_test(test[0], test[1], test[2])
            package_results.extend(res[0])
            msgs.extend(res[1])

        product = 1
        for i in package_results:
            product = product * int(i)

        if product == 1:
            print(f"{bc.OKGREEN}[\u2713] - {package[1]}\n{bc.ENDC}")
        else:
            print(f"{bc.FAIL}[X] - {package[1]}:\n{bc.ENDC}")
            for m in msgs:
                print(f"\t{m}")

        return package_results

    def run_test(self, code_samples, test_names, correct):
        # Run tests
        results = []

        for i in range(0, len(code_samples)):
            result, error = run.run(code_samples[i], test_names[i])
            results.append(self.process_result(result, error))

        # Process results
        test_results = []
        msg = []
        for i in range(0, len(code_samples)):
            res = results[i]
            name = test_names[i]

            if res != correct:
                msg.append(f"{bc.FAIL}[!!] {name}, with results:\n\t\t{res}\n{bc.ENDC}")
            test_results.append(res == correct)
        return [test_results, msg]


validator = Validator()
validator.run_tests()
