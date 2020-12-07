import re
from lark import Lark, InlineTransformer
from typing import NamedTuple


class Symbol(NamedTuple):
    value: str


grammar = Lark(r"""
    ?start  : exp+

    ?exp    : value
            | list_ 
            | quote 

    ?value  : NUMBER -> number
            | STRING -> string
            | BOOLEAN -> boolean
            | CHAR -> char
            | NAME -> name

    list_   : "(" exp+ ")"

    quote   : "'" exp

    NUMBER  : /(\+|\-)?\d+(\.\d+)?/ 
    STRING  : /\"[^\b\f\n\r\t]*\"/ 
    BOOLEAN : /#(t|f)/
    CHAR    : /#\\([a-zA-z]+|.)/
    NAME    : /([a-zA-Z]|[\-\?\+\*\/=<>])[\w\-\?\+\*\/=<>]*/
    
    %ignore /\s+/
    %ignore /;;.*/
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

    def string(self, tk):
        return eval(tk)
    
    def number(self, tk):
        return float(tk)
    
    def boolean(self, tk):
        if tk == "#f":
            return False
        else:
            return True

    def name(self, tk):
        return Symbol(tk)

    def char(self, tk):    
        if len(tk) == 3:
            return str(tk[2])
        else:
            tk = tk[2:].lower()
            return self.CHARS[tk]
    
    def list_(self, *args):
        return list(args)

    def quote(self, tk):
        return [Symbol("quote"), tk]

    def start(self, *args):
        if len(list(args)) > 1:
            return [Symbol("begin")] + list(args)
        else:
            return args