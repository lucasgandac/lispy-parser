import re
from lark import Lark, InlineTransformer
from typing import NamedTuple


class Symbol(NamedTuple):
    value: str


grammar = Lark(
    r"""

?start : expr

?bool: TRUE -> boolean | FALSE -> boolean

?atom: STRING -> string 
     | NUMBER -> number 
     | SYMBOL -> symbol 
     | bool 
     | NAME -> name 
     | CHAR -> char

?list : "(" expr* ")" -> lista

?expr : atom | list | quote

?quote : "'" expr -> quote

SYMBOL  : /[-!+\/*@$%^&~<>?|\\\w=]+/
STRING    : /"[^"\\]*(\\[^\n\t\r\f][^"\\]*)*"/
NUMBER : /-?(0|[1-9]\d*)(\.\d+)?([eE][+-]?\d+)?/
NAME   : /[a-zA-Z][-?\w]*/
CHAR   : /\#\\\w+/
TRUE : "#t"
FALSE: "#f"

%ignore /\s+/
%ignore /;[^\n]*/
""")


class LispyTransformer(InlineTransformer):
    CHARS = {
        "altmode": "\x1b",
        "backnext": "\x1f",
        "backspace": "\b",
        "call": "SUB",
        "linefeed": "\n",
        "page": "\f",
        "return": "\r",
        "rubout": "\xc7",
        "space": " ",
        "tab": "\t",
    }

    def string(self, value):
        return str(eval(value))

    def number(self, token):
        return float(token)

    def boolean(self, bool):
        if bool == '#t':
            return True
        elif bool == '#f':
            return False

    def symbol(self, value):
        return Symbol(value)
    
    def lista(self, *expr):
        return list(expr)

    def quote(self, expr):
        return [Symbol('quote'), expr]

"""
    def char(self, token):
        return 

    def start(self, token):
        return
"""
