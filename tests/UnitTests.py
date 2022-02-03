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
            res = self.run_package(setups[i])
            # s = setups[i][0]
            # n = setups[i][1]
            # c = setups[i][2]
            # res = self.run_test(s, n, c)

            for r in res:
                if r:
                    passed.append(r)
                else:
                    failed.append(r)
        print(
            f"------------------------- {len(passed)} Passed, {len(failed)} failed -------------------------"
        )

    def run_package(self, full_package):
        package = full_package[0]
        package_results = []
        messages = []

        print(f"{full_package[1]}:")
        for test in package:
            res = self.run_test(test[0], test[1], test[2])
            package_results.extend(res[0])
            messages.extend(res[1])

        output = []
        even = len(messages) % 2 == 0
        half = int(len(messages) / 2)
        if len(messages) != 1:
            if even:
                output.append(messages[0:half])
                output.append(messages[half : len(messages)])
            else:
                i = 0
                while True:
                    if not i + 2 > len(messages):
                        output.append([messages[i], messages[i + 1]])
                        i += 2
                        continue
                    output.append(messages[i])
                    break
            # print(output)

            for out in output:
                if len(out) > 1:
                    print(f"{out[0]}   {out[1]}")
                else:
                    print(out[0])

            return package_results
        print(messages[0])
        return package_results

    def run_test(self, code_samples, test_names, correct):
        # Run tests
        results = []

        for i in range(0, len(code_samples)):
            result, error = run.run(code_samples[i], test_names[i])
            results.append(self.process_result(result, error))

        # Process results
        test_results = []
        print_results = []
        for i in range(0, len(code_samples)):
            res = results[i]
            name = test_names[i]

            msg = ""
            if res == correct:
                msg = f"{bc.OKGREEN}\t[\u2713] {name}\n{bc.ENDC}"
            else:
                msg = f"{bc.FAIL}\t[!!] {name}, with results:\n\t{res}\n{bc.ENDC}"
            test_results.append(res == correct)
            print_results.append(msg)
        return [test_results, print_results]


validator = Validator()
validator.run_tests()
