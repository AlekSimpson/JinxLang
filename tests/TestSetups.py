import sys
from sys import platform

try:
    from Error import RuntimeError
except ImportError:
    sys.path.append("/home/alek/Desktop/projects/JinxLang/src/")

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
InlineConditionalOne = Test("if 1 == 1 { 1 + 1 }", "Inline If Statements", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = icmp eq i64 1, 1\n  br i1 %".2", label %"entry.if", label %"entry.endif"\nentry.if:\n  %".4" = add i64 1, 1\n  br label %"entry.endif"\nentry.endif:\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n')
InlineConditionalTwo = Test(
    "if 1 == 23 { 1 + 2 } elif 1 == 1 { 1 + 1 }", "Inline Elif Statements", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = icmp eq i64 1, 23\n  br i1 %".2", label %"entry.if", label %"entry.endif"\nentry.if:\n  %".4" = add i64 1, 2\n  br label %"entry.endif"\nentry.endif:\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n'
)
InlineCondtionalThree = Test(
    "if 1 == 23 { 1 + 2 } elif 1 == 234 { 1 + 2 } else { 1 + 1 }",
    "Inline Else Statements",
    '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = icmp eq i64 1, 23\n  %".3" = icmp eq i64 1, 23\n  br i1 %".3", label %"entry.if", label %"entry.else"\nentry.if:\n  %".5" = add i64 1, 2\n  br label %"entry.endif"\nentry.else:\n  %".7" = icmp eq i64 1, 234\n  br i1 %".7", label %"entry.else.if", label %"entry.else.else"\nentry.endif:\n  ret void\nentry.else.if:\n  %".9" = add i64 1, 2\n  br label %"entry.else.endif"\nentry.else.else:\n  %".11" = add i64 1, 1\n  br label %"entry.else.endif"\nentry.else.endif:\n  br label %"entry.endif"\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n',
)

# Newline Conditional Tests
NewlineConditionalOne = Test("if 1 == 1 {; 1 + 1; }", "Newline If Statements", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = icmp eq i64 1, 1\n  br i1 %".2", label %"entry.if", label %"entry.endif"\nentry.if:\n  %".4" = add i64 1, 1\n  br label %"entry.endif"\nentry.endif:\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n')
NewlineConditionalTwo = Test(
    "if 1 == 23 {; 1 + 2; } elif 1 == 1 {; 1 + 1; }", "Newline Elif Statements", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = icmp eq i64 1, 23\n  br i1 %".2", label %"entry.if", label %"entry.endif"\nentry.if:\n  %".4" = add i64 1, 2\n  br label %"entry.endif"\nentry.endif:\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n'
)
NewlineConditionalThree = Test(
    "if 1 == 23 {; 1 + 2; } elif 1 == 234 {; 1 + 2; } else {; 1 + 1; }",
    "Newline Else Statements",
    '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = icmp eq i64 1, 23\n  %".3" = icmp eq i64 1, 23\n  br i1 %".3", label %"entry.if", label %"entry.else"\nentry.if:\n  %".5" = add i64 1, 2\n  br label %"entry.endif"\nentry.else:\n  %".7" = icmp eq i64 1, 234\n  br i1 %".7", label %"entry.else.if", label %"entry.else.else"\nentry.endif:\n  ret void\nentry.else.if:\n  %".9" = add i64 1, 2\n  br label %"entry.else.endif"\nentry.else.else:\n  %".11" = add i64 1, 1\n  br label %"entry.else.endif"\nentry.else.endif:\n  br label %"entry.endif"\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n',
)

# Variable Tests
VariableTestOne = Test("a:Int = 5", "Variable Declaration", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = alloca i64\n  store i64 5, i64* %".2"\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n')
VariableTestTwo = Test("a:Int = 5; a", "Variable Reference", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = alloca i64\n  store i64 5, i64* %".2"\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n')
VariableDecString = Test('a:String = "test"', "String Variable Declaration", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = alloca i64*\n  %".3" = alloca [5 x i8]\n  store [5 x i8] c"test\\00", [5 x i8]* %".3"\n  %".5" = bitcast [5 x i8]* %".3" to i64**\n  %".6" = load i64*, i64** %".5"\n  store i64* %".6", i64** %".2"\n  %".8" = alloca [5 x i8]*\n  store [5 x i8]* %".3", [5 x i8]** %".8"\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n')
VariableRefString = Test('a:String = "test"; a', "String Variable Reference", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = alloca i64*\n  %".3" = alloca [5 x i8]\n  store [5 x i8] c"test\\00", [5 x i8]* %".3"\n  %".5" = bitcast [5 x i8]* %".3" to i64**\n  %".6" = load i64*, i64** %".5"\n  store i64* %".6", i64** %".2"\n  %".8" = alloca [5 x i8]*\n  store [5 x i8]* %".3", [5 x i8]** %".8"\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n')
VariableRefBool = Test("a:Bool = true", "Bool Variable Reference", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = alloca i1\n  store i1 1, i1* %".2"\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n')
VariableDecBool = Test("a:Bool = true; a", "Bool Variable Declaration", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = alloca i1\n  store i1 1, i1* %".2"\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n')
VariableDecFloat = Test("a:Float = 5.0", "Float Variable Declaration", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = alloca double\n  store double 0x4014000000000000, double* %".2"\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n')
VariableRefFloat = Test("a:Float = 5.0; a", "Float Variable Reference", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = alloca double\n  store double 0x4014000000000000, double* %".2"\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n')

VariableErrorOne = CrashTest('a:Int = "test"', "Assigning String to Int", RuntimeError())
VariableErrorTwo = CrashTest("a:String = 45", "Assigning Int to String", RuntimeError())
VariableErrorThree = CrashTest('a:Int = 4; a = "test"', "Updating String to Int", RuntimeError())
VariableErrorFour = CrashTest('a:String = "test"; a = 45', "Updating String to Int", RuntimeError())

# Arithmetic Tests
AdditionTest = Test("3 + 1", "Addition", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = add i64 3, 1\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n')
SubtractionTest = Test("6 - 2", "Subtraction", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = sub i64 6, 2\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n')
MultiplicationTest = Test("2 * 2", "Multiplication", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = mul i64 2, 2\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n')
DivisionTest = Test("8 / 2", "Division", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = sdiv i64 8, 2\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n')
ExponentialTest = Test("2 ^ 2", "Exponents", 4)
UnaryDeclaration = Test("-30", "Unary Value Declaration", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n')
UnaryOperation = Test("1 + -1", "Unary Operations", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = add i64 1, -1\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n')
UnaryFloatDeclaration = Test("-30.0", "Unary Float Declaration", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n')
UnaryFloatOperation = Test("-30.0 + 20.0", "Unary Float Operations", -10.0)
DivideByZero = CrashTest("2 / 0", "Divide by Zero Error", RuntimeError())

# For Loops
InlineForTest = Test("for i in 1:5 { 1 + 1 }", "Inline For Loops", 0)
NewlineForTest = Test("for i in 1:5 {; 1 + 1; }", "Newline For Loops", 0)
InlineWhileTest = Test("a:Int = 0; while a < 5 { a = a + 1 }", "Inline While Loops", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = alloca i64\n  store i64 0, i64* %".2"\n  %".4" = load i64, i64* %".2"\n  %".5" = icmp slt i64 %".4", 5\n  br i1 %".5", label %"while_loop_entry1", label %"while_loop_otherwise0"\nwhile_loop_entry1:\n  %".7" = load i64, i64* %".2"\n  %".8" = add i64 %".7", 1\n  store i64 %".8", i64* %".2"\n  %".10" = load i64, i64* %".2"\n  %".11" = icmp slt i64 %".10", 5\n  br i1 %".11", label %"while_loop_entry1", label %"while_loop_otherwise0"\nwhile_loop_otherwise0:\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n')
NewlineWhileTest = Test("a:Int = 0; while a < 5 {; a = a + 1; }", "Newline While Loops", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = alloca i64\n  store i64 0, i64* %".2"\n  %".4" = load i64, i64* %".2"\n  %".5" = icmp slt i64 %".4", 5\n  br i1 %".5", label %"while_loop_entry1", label %"while_loop_otherwise0"\nwhile_loop_entry1:\n  %".7" = load i64, i64* %".2"\n  %".8" = add i64 %".7", 1\n  store i64 %".8", i64* %".2"\n  %".10" = load i64, i64* %".2"\n  %".11" = icmp slt i64 %".10", 5\n  br i1 %".11", label %"while_loop_entry1", label %"while_loop_otherwise0"\nwhile_loop_otherwise0:\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n')

#NOTE: Method Defintion Tests
InlineMethodDef = Test("method test():Int -> 1 + 1", "Inline Method Definition", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n\ndefine i64 @"test"() \n{\ntest_entry:\n  %".2" = add i64 1, 1\n}\n')
NewlineMethodDef = Test("method test():Int {; return 1 + 1; }", "Newline Method Definition", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n\ndefine i64 @"test"() \n{\ntest_entry:\n  %".2" = add i64 1, 1\n  ret i64 %".2"\n}\n')

# Inline Method Call Tests
InlineMethodCall = Test("method test(): Int -> 1 + 1; test()", "Inline Method Calls", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = call i64 @"test"()\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n\ndefine i64 @"test"() \n{\ntest_entry:\n  %".2" = add i64 1, 1\n}\n')

# Newline Method Call Tests
NewlineMethodCall = Test("method test():Int {; return 1 + 1; }; test()", "Newline Method Calls", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = call i64 @"test"()\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n\ndefine i64 @"test"() \n{\ntest_entry:\n  %".2" = add i64 1, 1\n  ret i64 %".2"\n}\n')

# Method Arguements Tests
MethodArguements = Test("method add(a:Int, b:Int):Int {; return a + b; }; add(2, 2)", "Method Arguements", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = call i64 @"add"(i64 2, i64 2)\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n\ndefine i64 @"add"(i64 %".1", i64 %".2") \n{\nadd_entry:\n  %".4" = alloca i64\n  store i64 %".1", i64* %".4"\n  %".6" = alloca i64\n  store i64 %".2", i64* %".6"\n  %".8" = load i64, i64* %".4"\n  %".9" = load i64, i64* %".6"\n  %".10" = add i64 %".8", %".9"\n  ret i64 %".10"\n}\n')

# Method Return Tests
MethodReturnOne = Test("method test():Int {; return 1 + 1; }; test()", "Method Return Statements", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = call i64 @"test"()\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n\ndefine i64 @"test"() \n{\ntest_entry:\n  %".2" = add i64 1, 1\n  ret i64 %".2"\n}\n')
MethodReturnTwo = Test(
    "method test():Int {; new:Int = 23 + 321; return 323; }; test()",
    "Method Returns One Value",
    '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = call i64 @"test"()\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n\ndefine i64 @"test"() \n{\ntest_entry:\n  %".2" = add i64 23, 321\n  %".3" = alloca i64\n  store i64 %".2", i64* %".3"\n  ret i64 323\n}\n',
)
MethodReturnThree = Test(
    'method test():Int {; new:Int = 20 + 20; return 20; print("SHOULD NOT PRINT"); }; test()',
    "Method Return Control Flow",
    '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = call i64 @"test"()\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n\ndefine i64 @"test"() \n{\ntest_entry:\n  %".2" = add i64 20, 20\n  %".3" = alloca i64\n  store i64 %".2", i64* %".3"\n  ret i64 20\n}\n',
)

# Array Tests
ArrayDec = Test("a:Array{Int} = [1 2 3 4]", "ArrayDeclaration", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = alloca [4 x i64]\n  store [4 x i64] [i64 1, i64 2, i64 3, i64 4], [4 x i64]* %".2"\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n')
ArrayRef = Test("a:Array{Int} = [1 2 3 4]; a", "Array Reference", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = alloca [4 x i64]\n  store [4 x i64] [i64 1, i64 2, i64 3, i64 4], [4 x i64]* %".2"\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n')
#ArrayApp = Test("a:Array{Int} = [1 2 3]; append(a, 123)", "Array Append", None)
ArrayVarRef = Test("a:Array{Int} = [1 2 3]; i:Int = 0; a[i]", "Array Variable Index Reference", '; ModuleID = "main"\ntarget triple = "unknown-unknown-unknown"\ntarget datalayout = ""\n\ndefine void @"main"() \n{\nentry:\n  %".2" = alloca [3 x i64]\n  store [3 x i64] [i64 1, i64 2, i64 3], [3 x i64]* %".2"\n  %".4" = alloca i64\n  store i64 0, i64* %".4"\n  %".6" = extractvalue [3 x i64] [i64 1, i64 2, i64 3], 0\n  ret void\n}\n\ndeclare i64 @"printf"(i8* %".1", ...) \n')
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
    #
    #VariableErrorOne,
    #VariableErrorTwo,
    #VariableErrorThree,
    #VariableErrorFour,
    #
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
    #
    #ExponentialTest,
    #
    UnaryDeclaration,
    UnaryOperation,
    UnaryFloatDeclaration,
    #UnaryFloatOperation,
    #DivideByZero
]

loopsPackage = [
    #InlineForTest,
    NewlineForTest,
    #-InlineWhileTest,
    #-NewlineWhileTest
]

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

arraysPackage = [
    ArrayDec,
    ArrayRef,
    #ArrayApp,
    ArrayVarRef,
    #ArrayTypeMisMatch
]

stdPackage = [stdlength, stdremove, stdremovelast]

# Meta array to send to unit tests file
setups = [
    #[conditionalsPackage, "Conditionals"],
    #[variablesPackage, "Variables"],
    #[arithmeticPackage, "Arithmetic"],
    [loopsPackage, "Loops"],
    #[methodsPackage, "Methods"],
    #[arraysPackage, "Arrays"],
    #[stdPackage, "Standard Library"] ##NOTE: Will implement later, requires some other things first I think
]
