%"Person" = type {%String}
%"Array" = type {i64*}
%"String" = type {i8*}
define void @"main"() 
{
entry:
  %".2" = alloca [5 x i8]
  store [5 x i8] c"test\00", [5 x i8]* %".2"
  %".4" = getelementptr [5 x i8], [5 x i8]* %".2", i32 0, i32 0
  %".5" = alloca %"String"
  %".6" = getelementptr %"String", %"String"* %".5", i32 0, i32 0
  store i8* %".4", i8** %".6"
  %".12" = alloca {[5 x i8]}
  store {[5 x i8]} {[5 x i8] c"test\00"}, {[5 x i8]}* %".12"
  %".14" = getelementptr {[5 x i8]}, {[5 x i8]}* %".12", i32 0, i32 0
  %".15" = bitcast [4 x i8]* @"fstr" to i8*
  %".16" = call i64 (i8*, ...) @"printf"(i8* %".15", [5 x i8]* %".14")
  ret void
Person_entry:
  %".8" = alloca {[5 x i8]}
  store {[5 x i8]} {[5 x i8] c"test\00"}, {[5 x i8]}* %".8"
  %".10" = getelementptr {[5 x i8]}, {[5 x i8]}* %".8", i32 0, i32 0
  ret void
}

@"fstr" = internal constant [4 x i8] c"%s\0a\00"
@"fint" = internal constant [4 x i8] c"%d\0a\00"
@"flt_str" = internal constant [6 x i8] c"%.2f\0a\00"
declare i64 @"printf"(i8* %".1", ...) 
