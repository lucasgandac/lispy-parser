import re
from lark import Lark, InlineTransformer
from typing import NamedTuple


class Symbol(NamedTuple):
    value: str


grammar = Lark( r"""
        ?start: value*
        ?value: atom 
            | quote
            | array
        ?atom: NUMBER -> num
            | STRING -> string
            | NAME -> name
            | "true" -> true
            | "false" -> false
            | "null" -> null
            | SYMBOL -> symbol


        quote: "'" value    
        array: "(" value+ ")"
        
                
        STRING: /"([^"\\\n\r\b\f]+|\\["\\\/bfnrt]|\\u[0-9a-fA-F]{4})*"/
        NAME: /\w*[-?_\w]+/
        NUMBER: /-?(0|[1-9]\d*)(\.\d+)?([eE][+-]?\d+)?/
        SYMBOL: /[-!$?@%\/^&*+~=:<>]+/
        
        
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
    
    def quote(self, tk):
        return [Symbol('quote'), tk]

    def array(self, *args):
        return list(args)    

    def true(self, tk):
        return True
    
    def false(self, tk):
        return False
    
    def null(self, tk):
        return None    

    def num(self, tk):
        return float(tk)

    def symbol(self, tk):
        return Symbol(tk)

    