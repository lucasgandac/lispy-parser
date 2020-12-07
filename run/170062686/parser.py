import re
from typing import NamedTuple
from lark import Lark, InlineTransformer


class Symbol(NamedTuple):
    value: str


grammar = Lark(r"""
    ?start : expr+

    ?expr  : atom
           | list_
           | quote
    ?atom  : STRING -> string
           | SYMBOL -> symbol
           | NUMBER -> number
           | BOOLEAN -> boolean
           | NAME -> name
           | CHAR -> char
    list_  : "(" expr+ ")"
    quote  : "'" expr

    STRING : /"[^"\\]*"/
    SYMBOL: /[-+=\/*!@$^&~<>?]+/
    NUMBER : /-?\d+(\.\d+)?/
    BOOLEAN: /\#t|\#nil/
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

    def name(self, tok):
        return Symbol(tok)

    def string(self, tok):
        return eval(tok)

    def char(self, tok):
        tok = tok.split('#\\')[-1]

        if tok.lower() in self.CHARS:
            return self.CHARS[tok.lower()]
        else:
            return tok

    def number(self, tok):
        return float(tok)

    def list_(self, *elem):
        return list(elem)

    def boolean(self, tok):
        if tok == '#t':
            return True
        else:
            return False

    def symbol(self, tok):
        return Symbol(tok)

    def quote(self, tok):
        return [Symbol('quote'), tok]

    def start(self, *elem):
        proc_list = list()
        proc_list = list(elem)
        proc_list.insert(0, Symbol('begin'))

        return proc_list
