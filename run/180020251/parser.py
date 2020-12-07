import re
from lark import Lark, InlineTransformer
from typing import NamedTuple


class Symbol(NamedTuple):
    value: str


grammar = Lark(
    r"""
    ?start : expr+ 

    ?expr : atom | array | quoted
    
    quoted : "'" expr
    
    array : "(" expr+ ")"

    ?atom : STRING -> string
        |  NUMBER -> number
        |  BOOLEAN -> boolean
        |  CHAR -> char
        |  NAME -> name
        
        
        STRING : /"([^"\\\n\r\b\f]+|\\["\\\/bfnrt]|\\u[0-9a-fA-F]{4})*"/
        NUMBER : /-?\d+(\.\d+)?([eE][+-]?\d+)?/ 
        BOOLEAN : /\#t|\#f]/
        CHAR : /\#\\[a-zA-Z]*/
        NAME : /([a-zA-Z_%\+\-]|[-+=\/*!@$^&~<>?])[-?+*\/=<>\w]*/
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
        return True if (tk == "#t") else False

    def char(self, tk):
        tk = tk.split('#\\')[-1]
        return tk if tk.lower() not in self.CHARS else self.CHARS[tk.lower()]

    def name(self, tk):
        return Symbol(tk)

    def array(self, *args):
        return list(args)

    def quoted(self, tk):
        return [Symbol('quote'), tk]

    def start(self, *args):
        expr = list(args)
        expr.insert(0, Symbol('begin'))
        return expr