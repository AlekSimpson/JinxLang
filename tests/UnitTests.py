import sys
from TestSetups import setups
from termcolors import bcolors as bc

try:
    import run
    from Compiler import Compiler
    from Error import Error
except ImportError:
    sys.path.append("/home/alek/Desktop/projects/JinxLang/src/")

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
            if result.elements[-1] is not None:
                return result.elements[-1].value

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
            pass
        else:
            print(f"{bc.FAIL}[X] - {package[1]}:\n{bc.ENDC}")
            for m in msgs:
                if m is not None:
                    print(f"\t{m}")

        return package_results

    def execute_test(self, test):
        output = run.run(test.sample, test.name, True)
        #print("+++++++++++")
        #print(repr(output))
        #print("+++++++++++")

        eval_, msg = test.evaluate(output)
        return [eval_, msg]

validator = Validator()
validator.run_tests()
