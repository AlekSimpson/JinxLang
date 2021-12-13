#!/bin/bash 

cat Error.swift Number.swift Position.swift SymbolTable.swift Context.swift Lexer.swift Node.swift Parser.swift Interpreter.swift ParseResult.swift RuntimeResult.swift Tokens.swift Run.swift > main.swift
clear
swift main.swift 
