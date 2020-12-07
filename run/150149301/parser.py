import re
from lark import Lark, InlineTransformer, v_args
from typing import NamedTuple


class Symbol(NamedTuple):
    value: str


grammar = Lark(
    r"""
        ?start : expr+

            ?expr : atom
                | list_
                | quote 
            

            list_  : "(" expr+ ")"

            quote : "'" expr
            
            ?atom : STRING -> string
                | NUMBER -> num
                | BOOLEAN -> boolean
                | NAME -> name
                | CHAR -> char

            NAME   : /[a-zA-Z][-?\w]*/ | /[-+=\/*<><=]+/
            STRING : /\"[^"\\]*(\\[^\n\t\r\f][^"\\]*)*\"/
            NUMBER : /\+?\-?\d+(\.\d*)?([eE][+-]?\d+)?/
            BOOLEAN: /\#t|\#f/
            CHAR   : /\#\\[\w]+|\d+/

            %ignore /\s+/
            %ignore /\;([^\n\r]+)/
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

    def start(self, *args):
        if len(list(args)) > 1:
            return [Symbol("begin")] + list(args)
        else:
            return args
   
    def string(self, tk):
        return eval(tk)
    
    def num(self, tk):
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
    
    def list_(self, *args):
        return list(args)

    def quote(self, tk):
        return [Symbol("quote"), tk]