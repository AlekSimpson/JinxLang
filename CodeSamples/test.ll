%"Array" = type {i64*}
%"String" = type {i8*}
define void @"main"() 
{
entry:
  %".2" = alloca [2 x i8]
  store [2 x i8] c"a\00", [2 x i8]* %".2"
  %".4" = getelementptr [2 x i8], [2 x i8]* %".2", i32 0, i32 0
  %".5" = alloca %"String"
  %".6" = getelementptr %"String", %"String"* %".5", i32 0, i32 0
  store i8* %".4", i8** %".6"
  %".8" = alloca [2 x i8]
  store [2 x i8] c"b\00", [2 x i8]* %".8"
  %".10" = getelementptr [2 x i8], [2 x i8]* %".8", i32 0, i32 0
  %".11" = alloca %"String"
  %".12" = getelementptr %"String", %"String"* %".11", i32 0, i32 0
  store i8* %".10", i8** %".12"
  %".14" = alloca [2 x i8]
  store [2 x i8] c"c\00", [2 x i8]* %".14"
  %".16" = getelementptr [2 x i8], [2 x i8]* %".14", i32 0, i32 0
  %".17" = alloca %"String"
  %".18" = getelementptr %"String", %"String"* %".17", i32 0, i32 0
  store i8* %".16", i8** %".18"
  %".20" = alloca [3 x %"String"*]
  store [3 x %"String"*] [%"String"* %".5", %"String"* %".11", %"String"* %".17"], [3 x %"String"*]* %".20"
  %".22" = getelementptr [3 x %"String"*], [3 x %"String"*]* %".20", i32 0, i32 0
  %".23" = bitcast %"String"** %".22" to i64*
  %".24" = alloca %"Array"
  %".25" = getelementptr %"Array", %"Array"* %".24", i32 0, i32 0
  store i64* %".23", i64** %".25"
  %".27" = alloca %"Array"*
  store %"Array"* %".24", %"Array"** %".27"
  ret void
}

@"fstr" = internal constant [4 x i8] c"%s\0a\00"
@"fint" = internal constant [4 x i8] c"%d\0a\00"
@"flt_str" = internal constant [6 x i8] c"%.2f\0a\00"
declare i64 @"printf"(i8* %".1", ...) 
