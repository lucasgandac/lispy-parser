import re
from lark import Lark, InlineTransformer
from typing import NamedTuple


class Symbol(NamedTuple):
    value: str


grammar = Lark(
    r"""
?start : value*
?value  : lista
        | quoted 
        |STRING -> string
        | SYMBOL -> symbol
        | NUMBER -> number
        | BOOL -> boolean
        | NAME -> name
        | CHAR -> char

quoted : "'" value
lista : "(" value* ")"   
     
BOOL : /#(t)?(f)?/
CHAR : /\#\\\w+/
NUMBER : /[+-]?\d+(\.\d*)?([eE][+-]?\d+)?/
SYMBOL: /[-+=\/*!@$^&~<>?]+/
STRING: /"[^"]*"/
NAME   : /[a-zA-Z_\?\$\&\~\^\%\!\>\<\+\-\*\/\.][a-zA-Z_\?\$\&\~\^\%\!\>\<\+\-\*\/\.0-9]*/

%ignore /;[^\n]*/
%ignore /\s+/
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
    def start(self, *args):
        if len(args) == 1:
            return args[0]
        return [Symbol('begin'), *args]

    def string(self, x):
        return x[1:-1]
    def number(self, x):
        return float(x)
    def name(self, x):
        return Symbol(x)
    def quoted(self, x):
        return [Symbol('quote'), x]
    def boolean(self, x):
        return False if x.value == "#f" else True
    def lista(self, *args):
        return [*args]
    def char(self, x):
        token = x.split('#\\')[-1]
        tk = token if token.lower() not in self.CHARS else self.CHARS[token.lower()]
        return tk
    def symbol(self, x):
        return Symbol(x)