import re
import math
from lark import Lark, InlineTransformer
from typing import NamedTuple

class Symbol(NamedTuple):
    value: str


grammar = Lark(r"""
?start : expr+

?quote_rule : QUOTE expr+ -> quote

?expr : STRING -> string 
      | NUMBER -> number
      | array
      | quote_rule
      | KEYWORD -> keyword
      | BOOLEAN -> boolean
      | CHARACTER -> character
      | ATOM -> atom

array : "(" ( expr (expr)* )? ")"

QUOTE: /([\']{1,2})/
KEYWORD: /(cmd|and|begin|case|cond|define|delay|do|if|else|lambda|let|let\*|letrec|or|quasiquote|quote|set!|unquote|unquote-splicing)/
NUMBER : /[-+]?\d+(\.\d*)?/
STRING: /"(([^\\"\b\n\r\f])+|\\(["\\bfnrt\/]|u[0-9a-fA-F]{4}))*"/
BOOLEAN : /(\#\\?t|\#\\?f)/
CHARACTER: /\#\\[\w]*/
ATOM: /[a-zA-Z_+\-.<>=\?\*\/!:$%&~^\t\\\"][a-zA-Z_0-9+\-.<>=\?\*\/!:$%&~^\t\\\"]*/
%ignore /\s+/
%ignore /;.*/
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
        "a": "A"
    }

    def number(self, token):
        return float(token)

    def string(self, string):
        return eval(string)

    def boolean(self, token):
        if (token == '#t'):
            return True
        elif (token == '#f'):
            return False

    def atom(self, token):
        return Symbol(token)

    def array(self, *itens):
        return list(itens)

    def start(self, *a):
        l = list(a)
        l.insert(0, Symbol('begin'))
        return l

    def quote(self, token, *itens):
        l = list(itens)
        l.insert(0, Symbol('quote'))
        return l

    def character(self, token):
        t = str(token)[2:]
        return str(self.CHARS.get(t.lower()))
    
    def keyword(self, token):
        return Symbol(token)