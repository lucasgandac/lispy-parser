import re
from lark import Lark, InlineTransformer
from typing import NamedTuple


class Symbol(NamedTuple):
    value: str


grammar = Lark(
    r"""

    ?start  : expr+

    lst     : "(" expr+ ")"

    quote   : "'" expr

    ?expr   : lst
            | quote
            | atom


    ?atom   : NUMBER -> number
            | NAME -> name
            | STRING -> string
            | BOOL -> bool
            | CHAR -> char
            
    NUMBER  : /[-+]?\d+(\.\d+)?/
    NAME    : /[a-zA-Z\.<=>\+\-\*\?!%][a-zA-Z0-9\.<=>\+\-\*\?!%]*/
    STRING  : /\".*\"/
    BOOL    : /#t|#f|#nil/
    CHAR    : /#\\[^\s]+/

    %ignore /\s+/
    %ignore /;;[^\n]+/

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

    def start(self, *args):
        l = list(args)
        l.insert(0, Symbol("begin"))
        return l

    def lst(self, *args):
        return list(args)

    def quote(self, tk):
        return [Symbol("quote"), tk]

    def number(self, tk):
        return float(tk)

    def name(self, tk):
        return Symbol(tk)

    def string(self, tk):
        return eval(tk)

    def bool(self, tk):
        if tk == "#t":
            return True
        elif tk == "#f":
            return False
        else:
            return None

    def char(self, tk):
        tk = tk[2:]
        if tk.lower() in self.CHARS:
            return self.CHARS[tk.lower()]
        else:
            return tk