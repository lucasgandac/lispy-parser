import re
from lark import Lark, InlineTransformer
from typing import NamedTuple


class Symbol(NamedTuple):
    value: str


grammar = Lark(
    r"""
        ?start : expr+  
        ?expr : atom
            | lisp_list
            | quote

        lisp_list   : "(" expr+ ")"
        quote : "'" expr

        ?atom : STRING -> string
            | NUMBER -> number
            | BOOLEAN -> boolean
            | CHAR -> char
            | NAME -> name

        STRING : /\"(.+\'?)\"/
        NUMBER : /(\+|\-)?\d+(\.\d*)?([eE][+-]?\d+)?/
        BOOLEAN : /\#[t|f]/
        CHAR : /\#\\(\w|\d)+/
        NAME : /[^()\"\n \#\;']+/

        %ignore /\s+/
        %ignore /\;([\w\ \d \S])+/
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
        if len(list(args)) > 1:
            return [Symbol("begin")] + list(args)
        else:
            return args
   
    def string(self, tk):
        return eval(tk)
    
    def number(self, tk):
        return float(tk)
    
    def boolean(self, tk):
        if tk == '#t':
            return True
        else:
            return False

    def name(self, tk):
        return Symbol(tk)

    def char(self, tk):    
        if len(tk) == 3:
            return str(tk[2])
        else:
            tk = tk[2:].lower()
            return self.CHARS[tk]
    
    def lisp_list(self, *args):
        return list(args)

    def quote(self, tk):
        print (tk)
        return [Symbol("quote"), tk]


if __name__ == '__main__':
    
    src = [       
        "(max 1 2)",
        "(max (list 1 2 3))",
        "'(1 2 3)",
        "'symbol",
            ]
    for exemplo in src:
        print(exemplo)
        transformer = LispyTransformer()
        tree = grammar.parse(exemplo)
        result = transformer.transform(tree)
        print(result)
        print(40* '-')