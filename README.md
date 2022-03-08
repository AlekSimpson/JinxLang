# Table of Contents 

* TODO
* What is Laplace?
* Laplace Goals
* Laplace Documentation 

## TODO

* ~Overhaul Type System~ 
* ~Fix Error System~
* ~Floats literally have been broken this entire time, needs fix~
* ~Add tests for testing Int64, Int32, etc values~
* ~Add unit tests for unary operations~
* Add structures 
* Write compiler

*continue writing README and Docs*

## What is Laplace?

Laplace is a simple and powerful imperative programming language, with a focus on computational computing. All documentation and instructions, as of now, can be found here.  
I started this project for a couple reasons:
	* As a passion project, I found the idea of creating a programming langauge interesting.
	* For educational reasons, I wanted to learn more about how programming languages work.
	* I wanted a language like Julia/Python but with built in support for low level byte management.
As of writing this Laplace is very unfinished and there is still a lot to do. If you have happened to stumble upon this wayward README in the corners of the internet; First of, thanks for the read! Secondly, feel free to clone this repo and contribute to the project.  

## Laplace Goals 

I have a couple specific goals in mind for Laplace. Firstly, I want a programming langauage with simple syntax similar to Julia's and Swift's. I want it to be statically typed and I want it to be compiled. I want it to be easy to work with and approachable. Writing simple scripts in Laplace should be straightforward with no package manager nonsense. 
(PM is non-exsistent as of writing this)
I want Laplace to be support both functional and object oriented programming paradigms.
I recognize these are fairly lofty goals, and I am unsure whether the final product will achieve all of them. However, I am willing to try and potentially fail. 

## Laplace Documentation 

##### *Note: These docs are incomplete and subject to change.*

### Getting Started

first clone this repository. For now you have to create an alias to ../src/run.py in your .bashrc file.
After you have created your laplace alias you should be able to run and use Laplace. 
To run a file:
```
laplace filename.lc
```
To start the REPL, just type laplace into your terminal. 

### Hello World!

The traditional Hello World program can be written Laplace simply.
Printing to the screen is very simple in Laplace. It can be done in one line with:
```
print("Hello, World!")
# Prints Hello, World!
```

No libraries or main entry point functions are created. 

### Simple Values 

There is no special keyword for creating variables in Laplace. You simply type the name of the variable, declare its type and assign a value. To update the variable just type its name and new value with the assignment operator. The new value must conform to the type the variable was originally declared with. 
```
myVariable:Int = 42
myVariable = 404
```

Creating an array is done with values and brackets ([]). Brackets are also used to access an element by its index and assign at an index. Spaces between the array elements are required. Commas are not used to seperate array elements. 
```
shoppingList: Array{String} = ["apples" "water" "bananas"]
shoppingList[2] = "ice cream"
print(shoppingList[2])

# Prints: ice cream 
```

To append to an array you use the append function. The append function takes in two arguments, the first is the array to append to and the second is the item to append to the array. This code samples will add the string "chocolate" to the end of the array. 
```
append(shoppingList, "chocolate")
```

To create an empty array.
```
myArray: Array{Int} = []
```

### Control Flow 

You can use if statements to create conditionals. You use for, while and recurrsion to make loops. Parenthese around the body are optional, brackets around the body are not. 
```
playerScores: Array{Int} = [75 43 103 87 12]
teamScore: Int = 0

for i in 0:length(playerScores) {
	if playerScore[i] > 50 {
		teamScore = teamScore + 3 // IMPORTANT: the '+=' operator is not appart of the language yet, but it will be.
	} else {
		teamScore = teamScore + 1
	}
}

print(teamScore)
# Prints "11"
```
*NOTE: iterating over elements of an array and not just a range will be added soon but it is not right now*
In if statements the statement MUST be a conditional. There are no implicit comparisons to zero. 
