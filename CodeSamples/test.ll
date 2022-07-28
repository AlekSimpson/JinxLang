%"Array" = type {i64*}
define void @"main"() 
{
entry:
  %".2" = alloca [4 x i64]
  store [4 x i64] [i64 1, i64 2, i64 3, i64 4], [4 x i64]* %".2"
  %".4" = getelementptr [4 x i64], [4 x i64]* %".2", i32 0, i32 0
  %".5" = alloca %"Array"
  %".6" = getelementptr %"Array", %"Array"* %".5", i32 0, i32 0
  store i64* %".4", i64** %".6"
  %".10" = call i64 @"big"(%"Array"* %".5")
  ret void
}

@"fstr" = internal constant [4 x i8] c"%s\0a\00"
@"fint" = internal constant [4 x i8] c"%d\0a\00"
@"flt_str" = internal constant [6 x i8] c"%.2f\0a\00"
declare i64 @"printf"(i8* %".1", ...) 

define i64 @"big"(%"Array"* %".1") 
{
big_entry:
  ; get pointer to first array attribute
  %".3" = getelementptr %"Array", %"Array"* %".1", i32 0, i32 0
  %".4" = load i64*, i64** %".3"
  ; gep from that pointer the desired index
  %".5" = getelementptr i64, i64* %".4", i64 1
  ; load it
  %".55" = load i64, i64* %".5"
  ; print
  %".6" = bitcast [4 x i8]* @"fint" to i8*
  %".7" = call i64 (i8*, ...) @"printf"(i8* %".6", i64 %".55")
  ret i64 5
}
