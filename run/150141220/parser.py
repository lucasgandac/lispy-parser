import re
from lark import Lark, InlineTransformer
from typing import NamedTuple


class Symbol(NamedTuple):
    value: str


grammar = Lark(r"""
    ?start : exp+
    
    ?exp  : atom
           | list
           | quoted
           
    quoted : "'" exp
    
    list   : "(" exp+ ")"
    
    ?atom  : STRING -> string
           | SYMBOL -> symbol
           | NUMBER -> number
           | BOOLEAN -> bool
           | NAME -> name
           | CHAR -> char
           
    STRING : /"[^"\\]*(\\[^\n\t\r\f][^"\\]*)*"/
    SYMBOL: /[-=+\/*!@$%^&~<>?]+/
    NUMBER : /-?\d+(\.\d+)?/
    BOOLEAN: /#[tf]/
    NAME   : /[a-zA-Z][-?\w]*/
    CHAR   : /\#\\\w+/
    
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

    def symbol(self, token):
        return Symbol(token)

    def bool(self, token):
        if token.value == "#t":
            value = True
        else:
            value = False
        return value

    def number(self, token):
        return float(token)

    def char(self, token):
        token = token.split('#\\')[-1]
        if token.lower() not in self.CHARS:
            valid_token = token
        else:
            valid_token = self.CHARS[token.lower()]
        return valid_token

    def string(self, token):
        return eval(token)

    def name(self, token):
        return Symbol(token)

    def list(self, *args):
        return list(args)

    def quoted(self, token):
        return [Symbol('quote'), token]

    def start(self, *args):
        start = list(args)
        start.insert(0, Symbol('begin'))
        return start