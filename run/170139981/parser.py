import re
from lark import Lark, InlineTransformer
from typing import NamedTuple


class Symbol(NamedTuple):
    value: str


grammar = Lark(
    r"""
        ?start: expression*

        ?expression: atomic 
            | quote
            | array

        ?atomic: NUMBER -> number 
            | STRING -> string
            | SYMBOL -> symbol
            | NAME -> name
            | TRUE -> true
            | FALSE -> false
            | CHAR -> char

        array: "(" expression+ ")"
        
        quote: "'" expression

        NUMBER: /-?(0|[1-9]\d*)(\.\d+)?/
        STRING: /"[-\w\s!?+%\/]+"/
        SYMBOL: /[-!$?@%\/^&*+~=:<>]+/
        NAME: /\w*[-?_\w]+/
        TRUE: /\#[tT]/
        FALSE: /\#[fF]/
        CHAR: /\#\\.*/
        
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
    
    def name(self, tk):
        return Symbol(tk)
    
    def number(self, tk):
        return float(tk)

    def true(self, tk):
        return True
    
    def false(self, tk):
        return False
    
    def char(self, tk):
        tk = tk.split("\\")[-1]
        for value in self.CHARS:
            if value == tk.lower():
                return self.CHARS[value]
        return tk

    def symbol(self, tk):
        return Symbol(tk)

    def quote(self, tk):
        return [Symbol('quote'), tk]

    def array(self, *args):
        return list(args)

    def start(self, *args):
        tree = list(args)
        tree.insert(0, Symbol('begin'))
        return tree