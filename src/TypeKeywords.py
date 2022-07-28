from TypeValue import TypeValue
from Types import *

type_keywords = [
    "Int",
    "Int64",
    "Int32",
    "Int16",
    "Int8",
    "Float",
    "Float64",
    "Float32",
    "Float16",
    "Float8",
    "String",
    "Bool",
    "Void",
    "Array",
    "UInt",
    "UInt64",
    "UInt32",
    "UInt16",
    "UInt8",
]

arr = Array()
arr.testval = "bruh"

type_values = [
    TypeValue(1, Integer(64)),
    TypeValue(1, Integer(64)),
    TypeValue(1, Integer(32)),
    TypeValue(1, Integer(16)),
    TypeValue(1, Integer(8)),
    TypeValue(2, Float(64)),
    TypeValue(2, Float(64)),
    TypeValue(2, Float(32)),
    TypeValue(2, Float(16)),
    TypeValue(2, Float(8)),
    TypeValue(11, string()),
    TypeValue(1, Bool(1)),
    TypeValue(3, Void()),
    TypeValue(12, arr),
    TypeValue(1, Integer(64)),
    TypeValue(1, Integer(64)),
    TypeValue(1, Integer(32)),
    TypeValue(1, Integer(16)),
    TypeValue(1, Integer(8)),
]
