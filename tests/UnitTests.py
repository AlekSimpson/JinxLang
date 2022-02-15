import sys
from sys import platform

if platform == "linux" or platform == "linux2":
    sys.path.append("/home/alek/Desktop/projects/aqua/src/")
elif platform == "darwin":
    sys.path.append("/Users/aleksimpson/desktop/projects/aqua/src/")

import run
from Error import *
from TestSetups import *
from termcolors import bcolors as bc


class Validator:
    def process_result(self, result):
        if result is None:
            return None
        if isinstance(result, Error):
            return result.as_string()

        if len(result.elements) == 1:
            if result.elements[0] is not None:
                return result.elements[0].value
        else:
            for ele in result.elements:
                if ele is not None:
                    return ele.value

    def run_tests(self):
        passed = []
        failed = []

        print("\n")
        for setup in setups:
            results = self.run_package(setup)

            for res in results:
                if res:
                    passed.append(res)
                else:
                    failed.append(res)
        print(f"-------------------------[ {len(passed)} Passed | {len(failed)} Failed ]-------------------------")

    def run_package(self, package):
        package_results = []
        msgs = []

        for test in package[0]:
            res = self.execute_test(test)
            package_results.append(res[0])
            msgs.append(res[1])

        product = 1
        for i in package_results:
            product = product * int(i)

        if product == 1:
            print(f"{bc.OKGREEN}[\u2713] - {package[1]}\n{bc.ENDC}")
        else:
            print(f"{bc.FAIL}[X] - {package[1]}:\n{bc.ENDC}")
            for m in msgs:
                if m is not None:
                    print(f"\t{m}")

        return package_results

    def execute_test(self, test):
        output = run.run(test.sample, test.name)
        result = self.process_result(output)
        eval, msg = test.evaluate(result)
        return [eval, msg]


validator = Validator()
validator.run_tests()
