import sys
from sys import platform

if platform == "linux" or platform == "linux2":
    sys.path.append("/home/alek/Desktop/projects/aqua/src/")
elif platform == "darwin":
    sys.path.append("/Users/aleksimpson/desktop/projects/aqua/src/")

from Error import RuntimeError
from Types import *
from termcolors import bcolors as color


class Test:
    def __init__(self, sample, test_name, correct_value):
        self.sample = sample
        self.name = test_name
        self.correct_value = correct_value

    def evaluate(self, value):
        if value != self.correct_value:
            return [
                False,
                f"{color.FAIL}[!!] {self.name}, with results:\n\t\t{value}\n{color.ENDC}",
            ]
        return [True, None]


class CrashTest(Test):
    def __init__(self, sample, test_name, correct_value):
        super().__init__(sample, test_name, correct_value)

    def evaluate(self, value):
        if isinstance(value, RuntimeError):
            return [
                False,
                f"{color.FAIL}[!!] [self.name], with results:\n\t\t{value}\n{color.ENDC}",
            ]
        return [True, None]


# Inline Conditional Tests
InlineConditionalOne = Test("if 1 == 1 { 1 + 1 }", "Inline If Statements", 2)
InlineConditionalTwo = Test(
    "if 1 == 23 { 1 + 2 } elif 1 == 1 { 1 + 1 }", "Inline Elif Statements", 2
)
InlineCondtionalThree = Test(
    "if 1 == 23 { 1 + 2 } elif 1 == 234 { 1 + 2 } else { 1 + 1 }",
    "Inline Else Statements",
    2,
)

# Newline Conditional Tests
NewlineConditionalOne = Test("if 1 == 1 {; 1 + 1; }", "Newline If Statements", 0)
NewlineConditionalTwo = Test(
    "if 1 == 23 {; 1 + 2; } elif 1 == 1 {; 1 + 1; }", "Newline Elif Statements", 0
)
NewlineConditionalThree = Test(
    "if 1 == 23 {; 1 + 2; } elif 1 == 234 {; 1 + 2; } else {; 1 + 1; }",
    "Newline Else Statements",
    0,
)

# Variable Tests
VariableTestOne = Test("a:Int = 5", "Variable Declaration", 5)
VariableTestTwo = Test("a:Int = 5; a", "Variable Reference", 5)
VariableDecString = Test('a:String = "test"', "String Variable Declaration", "test")
VariableRefString = Test('a:String = "test"; a', "String Variable Reference", "test")
VariableRefBool = Test("a:Bool = true", "Bool Variable Reference", 1)
VariableDecBool = Test("a:Bool = true; a", "Bool Variable Declaration", 1)
VariableDecFloat = Test("a:Float = 5.0", "Float Variable Declaration", 5.0)
VariableRefFloat = Test("a:Float = 5.0; a", "Float Variable Reference", 5.0)

VariableErrorOne = CrashTest('a:Int = "test"', "Assigning String to Int", RuntimeError())
VariableErrorTwo = CrashTest("a:String = 45", "Assigning Int to String", RuntimeError())
VariableErrorThree = CrashTest('a:Int = 4; a = "test"', "Updating String to Int", RuntimeError())
VariableErrorFour = CrashTest('a:String = "test"; a = 45', "Updating String to Int", RuntimeError())

# Arithmetic Tests
AdditionTest = Test("3 + 1", "Addition", 4)
SubtractionTest = Test("6 - 2", "Subtraction", 4)
MultiplicationTest = Test("2 * 2", "Multiplication", 4)
DivisionTest = Test("8 / 2", "Division", 4)
ExponentialTest = Test("2 ^ 2", "Exponents", 4)
UnaryDeclaration = Test("-30", "Unary Value Declaration", -30)
UnaryOperation = Test("1 + -1", "Unary Operations", 0)
UnaryFloatDeclaration = Test("-30.0", "Unary Float Declaration", -30.0)
UnaryFloatOperation = Test("-30.0 + 20.0", "Unary Float Operations", -10.0)
DivideByZero = CrashTest("2 / 0", "Divide by Zero Error", RuntimeError())

# For Loops
InlineForTest = Test("for i in 1:5 { 1 + 1 }", "Inline For Loops", 0)
NewlineForTest = Test("for i in 1:5 {; 1 + 1; }", "Newline For Loops", 0)
InlineWhileTest = Test("a:Int = 0; while a < 5 { a = a + 1 }", "Inline While Loops", 0)
NewlineWhileTest = Test("a:Int = 0; while a < 5 {; a = a + 1; }", "Newline While Loops", 0)

# Method Defintion Tests
InlineMethodDef = Test("method test():Int -> 1 + 1", "Inline Method Definition", None)
NewlineMethodDef = Test("method test():Int {; return 1 + 1; }", "Newline Method Definition", None)

# Inline Method Call Tests
InlineMethodCall = Test("method test(): Int -> 1 + 1; test()", "Inline Method Calls", 2)

# Newline Method Call Tests
NewlineMethodCall = Test("method test():Int {; return 1 + 1; }; test()", "Newline Method Calls", 2)

# Method Arguements Tests
MethodArguements = Test("method add(a:Int, b:Int):Int {; return a + b; }; add(2, 2)", "Method Arguements", 4)

# Method Return Tests
MethodReturnOne = Test("method test():Int {; return 1 + 1; }; test()", "Method Return Statements", 2)
MethodReturnTwo = Test(
    "method test():Int {; new:Int = 23 + 321; return 323; }; test()",
    "Method Returns One Value",
    323,
)
MethodReturnThree = Test(
    'method test():Int {; new:Int = 20 + 20; return 20; print("SHOULD NOT PRINT"); }; test()',
    "Method Return Control Flow",
    20,
)

# Array Tests
ArrayDec = Test("a:Array{Int} = [1 2 3 4]", "ArrayDeclaration", None)
ArrayRef = Test("a:Array{Int} = [1 2 3 4]; a", "Array Reference", None)
ArrayApp = Test("a:Array{Int} = [1 2 3]; append(a, 123)", "Array Append", None)
ArrayVarRef = Test("a:Array{Int} = [1 2 3]; i:Int = 0; a[i]", "Array Variable Index Reference", 1)
ArrayTypeMisMatch = CrashTest("a:Array{Int} = [1 2 3 4]; str:String = \"test\"; append(a, str)", "Appending String to Int Array", RuntimeError())

# Print Tests
PrintTestOne = Test('print("Hello World")', "Print Statements", "Hello World")
PrintTestTwo = Test("print(404)", "Printing Numbers", 404)
PrintTestThree = Test('new:String = "Hello World"', "Printing Variables", "Hello World")

# Standard Library Tests
stdlength = Test("array:Array{Int} = [1 2 3]; length(array)", "STD length() Function", 3)
stdremove = Test("array:Array{Int} = [1 2 3]; remove(array, 2); length(array)", "STD remove() Function", 2)
stdremovelast = Test("array:Array{Int} = [1 2 3]; removeLast(array); length(array)", "STD removeLast() Function", 2)

# Package Related Tests
conditionalsPackage = [
    InlineConditionalOne,
    InlineConditionalTwo,
    InlineCondtionalThree,
    NewlineConditionalOne,
    NewlineConditionalTwo,
    NewlineConditionalThree,
]

variablesPackage = [
    VariableTestOne,
    VariableTestTwo,
    VariableErrorOne,
    VariableErrorTwo,
    VariableErrorThree,
    VariableErrorFour,
    VariableDecString,
    VariableRefString,
    VariableDecBool,
    VariableRefBool,
    VariableDecFloat,
    VariableRefFloat
]

arithmeticPackage = [
    AdditionTest,
    SubtractionTest,
    MultiplicationTest,
    DivisionTest,
    ExponentialTest,
    UnaryDeclaration,
    UnaryOperation,
    UnaryFloatDeclaration,
    UnaryFloatOperation,
    DivideByZero
]

loopsPackage = [InlineForTest, NewlineForTest, InlineWhileTest, NewlineWhileTest]

methodsPackage = [
    InlineMethodDef,
    NewlineMethodDef,
    InlineMethodCall,
    NewlineMethodCall,
    MethodArguements,
    MethodReturnOne,
    MethodReturnTwo,
    MethodReturnThree,
]

arraysPackage = [ArrayDec, ArrayRef, ArrayApp, ArrayVarRef, ArrayTypeMisMatch]

stdPackage = [stdlength, stdremove, stdremovelast]

# Meta array to send to unit tests file
setups = [
    [conditionalsPackage, "Conditionals"],
    [variablesPackage, "Variables"],
    [arithmeticPackage, "Arithmetic"],
    [loopsPackage, "Loops"],
    [methodsPackage, "Methods"],
    [arraysPackage, "Arrays"],
    [stdPackage, "Standard Library"]
]
