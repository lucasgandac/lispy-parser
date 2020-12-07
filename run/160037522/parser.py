import re
from lark import Lark, InlineTransformer
from typing import NamedTuple

class Symbol(NamedTuple):
    value: str

grammar = Lark(
    r"""
?start : exp

?exp    : atom
        | "(" atom+ ")"
        | "(" exp+ ")"
        | "(" atom+ exp+ ")"
        | "(" exp+ atom+ ")"
        | qt

?qt     : QUOTE exp
        | QUOTE sb
        | QUOTE qt

?sb     : SYMBOL

?atom   : STRING            ->string
        | NUMBER            ->number
        | "#t"              ->true
        | "#f"              ->false
        | A                 ->a
        | SYMBOL            ->symbol
        | OP                ->operacao

STRING  : /".*"/                    

NUMBER  : /-?\d+(\.\d+)?/           

SYMBOL  : /[a-zA-Z-\?]+/

QUOTE   : "'"

A       : "#\A" | "#\linefeed" | "#\LineFeed"

OP      : "+" | "-" | "*" | "/"

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
    def exp(self, *tokens):
        return list(tokens)

    def qt(self, *tokens):
        return [Symbol('quote'), tokens[1]]

    def a(self, token):
        if token == r"#\A":
            return "A"
        elif token == r"#\linefeed" or token == r"#\LineFeed":
            return "\n"

    def number(self, token):
        return float(token.value)

    def string(self, token):
        temp = str(token.value)
        if temp[0] == '"':
            temp = temp[1:]
        if temp[-1] == '"':
            temp = temp[:-1]
        return temp

    def symbol(self, token):
        return Symbol(token.value)

    def true(self):
        return True

    def false(self):
        return False