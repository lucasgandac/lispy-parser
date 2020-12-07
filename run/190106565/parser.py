import re
from operator import contains

from lark import Lark, InlineTransformer
from typing import NamedTuple


class Symbol(NamedTuple):
    value: str


grammar = Lark(
    r"""
?start : symbol+
        
?symbol : STRING  -> string 
        | NUMBER  -> number 
        | quote
        | list
        | "null"  -> null
        | BOOL    -> bool
        | CHAR    -> char
        | NAME    -> name
        | BQUOTE
        | COMMA

quote  : "'" symbol
list   : "(" symbol* ")"
STRING : /"([^"\\\n\r\b\f]+|\\["\\\/bfnrt]|\\u[0-9a-fA-F]{4})*"/
NUMBER : /[-+]?(0|[1-9]\d*)(\.\d+)?([eE][+-]?\d+)?/
BOOL   : /#[tf]/
NAME   : /(\.{3}|[+-.]|[!$%&*\/:<=>?_\^\w][\w+\-.*\/<=>!?:$%_&~\^]*)/
CHAR   : /#\\[a-zA-Z0-9]+/
BQUOTE : /`/
COMMA  : /-?(,|,@)/
%ignore /([\s]+|;(.*)\n)/
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

    def name(self, tk):
        return Symbol(str(tk))

    def number(self, tk):
        if '+' in tk:
            return '{:+}'.format(float(tk)) if '.' in tk else '{:+}'.format(int(tk))
        else:
            return float(tk) if '.' in tk else int(tk)

    def quote(self, tk):
        return Symbol('quote'), tk

    def start(self, *args):
        list = [Symbol('begin')]
        for arg in args:
            list.append(arg)
        return list

    def char(self, tk):
        if tk[2:].lower() in self.CHARS:
            return self.CHARS.get(tk[2:].lower())
        else:
            return tk[2:]

    def list(self, *args):
        return list(args)

    def null(self):
        return None

    def bool(self, tk):
        return tk == '#t'
