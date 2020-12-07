import re
from lark import Lark, InlineTransformer
from typing import NamedTuple


class Symbol(NamedTuple):
    value: str


grammar = Lark(
    r"""
?start  : COMMENT* quote* (("(" (list | atom)* ")") | (list | atom)*)

?list   : "(" (atom* | list*) ")" -> list

?atom  : NUMBER -> number
       | BOOL -> bool
       | STRING -> string
       | CHAR -> char
       | NAME -> name
       
?quote : QUOTE -> symbol

STRING : /\".*\"/
NUMBER : /[+\-]?\d+(\.\d*)?([eE][+-]?\d+)?/
BOOL   : /#[tf]/
CHAR   : /#\\[^ \n]*/
NAME   : /[a-zA-Z\+\-\.\*\/<=>!\?:\$%_&~\^][a-zA-Z\+\-\.\*\/<=>!\?:\$%_&~\^0-9]*/
LPAR   : /\(/
RPAR   : /\)/
QUOTE  : /\'\'?[^\n\']+/
COMMENT : /;[^\n]*/

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
        "tab": "\t"
    }

    def string(self, tk):
        return eval(tk)

    def number(self, tk):
        return float(tk)

    def bool(self, tk):
        if tk == '#t':
            return True
        return False

    def char(self, tk):
        return Symbol(tk)

    def name(self, tk):
        return Symbol(str(tk))

    def list(self, *args):
        return (list(args))
