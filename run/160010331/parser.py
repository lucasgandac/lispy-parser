import re
from lark import Lark, InlineTransformer, Token
from typing import NamedTuple
import math
import operator as op


class Symbol(NamedTuple):
    value: str


grammar = Lark(
    r"""
    ?start : WS? cell WS?
        |WS? quote start WS?
        |WS? begin WS?
    ?expression:
    ?begin: cell (WS? cell)+
    ?quote: "'" -> quote
        |"quote" ->quote
    ?list: "(" WS? ( list_content )? WS?")"
    ?list_content: cell (WS? cell)*
    ?cell: value
        |NAME -> name
    
    ?value: STRING -> string
        |CHAR -> char
        |NUMBER -> number
        |BOOL -> bool
        |list -> list
    
    STRING: /"([^"\\\n\r\b\f]+|\\["\\\/bfnrt])*"/
    NUMBER: /[\+\-]?\d+(\.\d*)?/
    CHAR:  /#\\\S+/
    BOOL: "#"("t"|"f")    
    NAME: /[a-zA-Z_\-\/<=>!?:$%&~^.+*][a-zA-Z_0-9\-\/<=>!?:$%&~^.+*]*/
    WS: /\s+/
    COMENT: /;.*\s*/
    %ignore COMENT
"""
)

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

    def char(self, tk):
        result = tk[2:]
        if len(result) <= 1:
            return result
        else:
            return self.CHARS[result.lower()]

    def list(self, *tree):
        result = []

        if isinstance(tree[0], list):
            return tree[0]
        if isinstance(tree[0], Symbol):
            return [tree[0]]
        if not isinstance(tree[0], Token):
            for x in tree[0].children:
                # remove whitespace
                if isinstance(x, Token):
                    if x.type == "WS":
                        continue
                result.append(x)
            return result

    def bool(self, tk):
        if tk == "#t":
            return True
        elif tk == "#f":
            return False

    def name(self, tk):
        return Symbol(tk)

    def quote(self):
        return Symbol("quote")

    # def expression(self,*args):

    def start(self, *args):
        result = list(args)
        if isinstance(result[0], str):
            if result[0].isspace():
                del result[0]
                result = result[0] if result[0][0] == Symbol("begin") else result
        if isinstance(result[-1], str):
            if result[-1].isspace():
                del result[-1]
                result = result[0] if result[0][0] == Symbol("begin") else result
        return result

    def begin(self, *args):
        result = [Symbol("begin")]
        for x in args:
            if isinstance(x, Token):
                if x.type == "WS":
                    continue
            result.append(x)
        return result
