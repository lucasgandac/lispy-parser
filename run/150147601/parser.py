import re
from lark import Lark, InlineTransformer
from typing import NamedTuple


class Symbol(NamedTuple):
    value: str


grammar = Lark(r"""
?start : value+

?value : "(" value* ")" -> list_
    | atom
    | "'" value+ -> quote

?atom : STRING -> string
    | NUMBER -> number
    | BOOL -> boolean
    | CHAR -> char
    | SYMBOL -> symbol
    | NAME -> name


STRING : /"[^"\\]*(\\[^\n\t\r\f][^"\\]*)*"/
NUMBER : /-?(0|[1-9]+)(\.\d+)?/
NAME   : /([a-zA-Z]+[\-\_]?)+\??/
BOOL   : /(#t|#f)/
CHAR   : /#\\\w+/
SYMBOL : /[-+.*\/<=>!?$%_&~^@]+/

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

    def start(self, *args):
        return [Symbol('begin'), *args]

    def string(self, tk):
        return eval(tk)

    def name(self, tk):
        return Symbol(tk)

    def char(self, tk):
        # char = #\<word>

        c = tk[2:].lower()
        if c in self.CHARS:
            return self.CHARS[c]

        return tk[2:]

    def number(self, tk):
        return float(tk)

    def list_(self, *args):
        return list(args)

    def boolean(self, tk):
        return True if tk == '#t' else False

    def symbol(self, tk):
        return Symbol(tk)

    def quote(self, value):
        return [self.symbol('quote'), value]


exemplo = r"""
42
(1 2 3)
(let ((x 1) (y 2)) (+ x y))
''double-quote
"""


tree = grammar.parse(exemplo)
print(tree)
print(list(grammar.lex(exemplo)))

transformer = LispyTransformer(tree)
