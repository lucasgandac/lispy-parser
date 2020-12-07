import re
from lark import Lark, InlineTransformer
from typing import NamedTuple


class Symbol(NamedTuple):
    value: str


grammar = Lark(
    r"""
    ?start : values | quoting

    ?values :     STRING        -> string
                | "#t"          -> true
                | "#f"          -> false
                | CHAR          -> char
                | list_elem
                | command_sequence

    STRING :  /"[^"]+"/
    NUMBER : /(0|[1-9]+)(\.\d+)?/
    NAME : /([a-z\-]+)\??/
    CHAR : /#.+/
    OPERATOR : /[+\-\/*^=]+|<=|>=|\.\.\./

    quoting: "'" values+ | "'" quoting

    ?list_elem : OPERATOR       -> operator
                | NUMBER        -> double
                | NAME          -> name
                | array

    array:   "(" list_elem+ ")"

    command_sequence :   array+
                        | NUMBER+ -> number_sequence

    %ignore /\s+/
    %ignore /;;.+/


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

    def double(self, tk):
        return float(tk)

    def number_sequence(self, *args):
        return [Symbol('begin')] + [float(arg) for arg in args]

    def true(self):
        return True

    def false(self):
        return False

    def name(self, tk):
        return Symbol(str(tk))

    def operator(self, tk):
        return Symbol(str(tk))

    def array(self, *args):
        return list(args)

    def char(self, tk):
        tk = str(tk).replace('#\\', '')

        if self.CHARS.get(tk.lower()):
            return self.CHARS[tk.lower()]

        return tk.replace('#\\', '')

    def quoting(self, args):
        return [Symbol("quote"), args]

    def command_sequence(self, *args):
        return [Symbol('begin'), *args]
