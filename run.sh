#!/bin/bash 

cat Error.swift Position.swift Context.swift Lexer.swift Node.swift Parser.swift Interpreter.swift Tokens.swift Run.swift > main.swift
clear
swift main.swift 
