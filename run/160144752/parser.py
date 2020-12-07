from lark import Lark, InlineTransformer
from typing import NamedTuple


class Symbol(NamedTuple):
    value: str


grammar = Lark(r"""
    ?start : value+

    ?value : atom | list_ | quote

    ?atom  : string | number | name | boolean | char | symbol

    number : /[+-]?\d+(\.\d+)?/
    name   : /(([a-zA-Z\-\?>%!+.]+)|(?:;+.+))/
    char   : /#\\\w*/
    boolean: /#[t|f]/
    string : /\".+\"/
    symbol : /[-+\/*=!?@$&^~<>]+/

    list_  : "(" value+ ")"

    quote  : "'" value

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

    def number(self, token):
        return float(token)

    def name(self, token):
        return Symbol(token)

    def char(self, token):
        token = token[2:]
        if token.lower() not in self.CHARS:
            return token
        else:
            return self.CHARS[token.lower()]

    def boolean(self, token):
        return True if token == "#t" else False

    def string(self, token):
        return eval(token)

    def symbol(self, token):
        return Symbol(token)

    def list_(self, *args):
        return list(args)

    def quote(self, token):
        return [Symbol('quote'), token]

    def start(self, *args):
        return [Symbol("begin")] + list(args)