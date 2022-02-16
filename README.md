# Table of Contents 

* TODO
* What is Laplace?
* Laplace Goals
* Laplace Documentation 

## TODO

* ~Overhaul Type System~ 
* ~Fix Error System~
* Floats literally have been broken this entire time, needs fix
* Optimize Parser Code 
* Fix straggling bugs and weird edge cases
* Added structures 
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

