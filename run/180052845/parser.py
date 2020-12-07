import re
from lark import Lark, InlineTransformer
from typing import NamedTuple


class Symbol(NamedTuple):
    value: str


grammar = Lark(r"""
    ?start  : exp+

    ?exp    : value
            | lista
            | quoted

    ?value  : NUMBER -> number
            | STRING -> string
            | BOOLEAN -> boolean
            | CHAR -> char
            | NAME -> name

    lista   : "(" exp+ ")"

    quoted  : "'" exp

    NUMBER  : /-?\d+(\.\d+)?/
    STRING  : /"[^"\\]*"/
    BOOLEAN : /\#(t|f)/
    CHAR    : /\#\\\w+/
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



    def lista(self, *args):
        return list(args)

    def quoted(self, token):
        return [Symbol('quote'), token]

    def number(self, token):
        return float(token)
    
    def string(self, token):
        return eval(token)

    def symbol(self, token):
        return Symbol(token)

    def boolean(self, token):
        return True if token.value == "#t" else False
    
    def name(self, token):
        return Symbol(token)

    def char(self, token):    
        token = token.split('#\\')[-1]

        if token.lower() not in self.CHARS:
            return token
        else:
            return self.CHARS[token.lower()]

    def start(self, *args):
        if len(list(args)) > 1:
            return [Symbol("begin")] + list(args)
        else:
            return args


exemplo = [
    "5.63245",
    "89", 
    '"hello world"', 
    "#t",
    "#f",
    r"#\A",
    r"#\linefeed",
    "name-saying-something",
    "name?",
    "(odd? 42)",
    "(+ 1 2)",
    "(let ((x 1) (y 2)) (+ x y))",
    "((diff cos) x)",
    "'(1 2 3)",
    "'symbol",
    "''double-quote",
]

for src in exemplo:
    print(src)

    tree = grammar.parse(src)
    print(tree.pretty())

    tranformer = LispyTransformer()
    lispy = tranformer.transform(tree)
    print(lispy)

    print("____________________________________________________________\n")
