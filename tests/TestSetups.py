# Inline Contional Tests 
inlineSamples = ["if 1 == 1 { 1 + 1 }", 
                 "if 1 == 23 { 1 + 1 } elif 1 == 1 { 1 + 1 }", 
                 "if 1 == 23 { 1 + 1 } elif 1 == 234 { 1 + 1 } else { 1 + 1 }"]
inlineTestNames = ["Inline If Statements", 
                   "Inline Elif Statements", 
                   "Inline Else Statements"]
inlineCorrect = 2

# Newline Conditional Tests 
newlineSamples = ["if 1 == 1 {; 1 + 1; }",
                  "if 1 == 23 {; 1 + 2; } elif 1 == 1 {; 1 + 1; }",
                  "if 1 == 23 {; 1 + 2; } elif 1 == 23 {; 1 + 2; } else {; 1 + 1; }"]
newlineTestNames = ["Newline IfStatements",
                    "Newline Elif Statements",
                    "Newline Else Statements"]
newlineCorrect = 0

# Variable Tests
variableSamples  = ["a = 5", "a = 5; a"]
testNames        = ["Variable Declaration", "Variable Reference"]
variablesCorrect = 5

# Arithmetic Tests 
arithSamples   = ["3 + 1", "6 - 2", "2 * 2", "8 / 2", "2 ^ 2"]
arithTestNames = ["Addition", "Subtraction", "Multiplication", "Division", "Power"]
arithCorrect   = 4

# For Loops 
forSamples   = ["for i in 1:5 { 1 + 1 }", "for i in 1:5 {; 1 + 1; }"]
forTestNames = ["Inline For Loops", "Newline For Loops"]
forCorrect   = 0 

# While Loops 
whileSample    = ["a = 0; while a < 5 { a = a + 1 }", "a = 0; while a < 5 {; a = a + 1; }"]
whileTestNames = ["Inline While Loops", "Newline While Loops"]
whileCorrect   = 0 

# Method Defintion Tests 
mdSample    = ["method test() -> 1 + 1", "method test() {; 1 + 1; }"]
mdTestNames = ["Inline Method Definition", "Newline Method Definition"]
mdCorrect   = None

# Inline Method Call Tests 
mcSampleInline    = ["method test() -> 1 + 1; test()"]
mcTestNamesInline = ["Inline Method Calls"]
mcCorrectInline = 2

# Newline Method Call Tests
mcSampleNewline    = ["method test() {; 1 + 1; }; test()"]
mcTestNamesNewline = ["Newline Method Calls"]
mcCorrectNewline   = 0

# Method Arguements Tests 
maSamples = ["method add(a, b) {; new = a + b; }; add(2, 2)"]
maTests   = ["Method Arguemnts"]
maCorrect = 0

# Array Tests 
arraySamples = ["a = [1,2,3,4]", "a = [1,2,3,4]; a", "a = [1,2,3]; append(a, 123)"]
arrayTests   = ["Array Declaration", "Array Reference", "Array Append"]
arrayCorrect = None

setups = [[inlineSamples, inlineTestNames, inlineCorrect], 
          [newlineSamples, newlineTestNames, newlineCorrect], 
          [variableSamples, testNames, variablesCorrect],
          [arithSamples, arithTestNames, arithCorrect],
          [forSamples, forTestNames, forCorrect],
          [whileSample, whileTestNames, whileCorrect],
          [mdSample, mdTestNames, mdCorrect],
          [mcSampleInline, mcTestNamesInline, mcCorrectInline],
          [mcSampleNewline, mcTestNamesNewline, mcCorrectNewline],
          [maSamples, maTests, maCorrect],
          [arraySamples, arrayTests, arrayCorrect]]
