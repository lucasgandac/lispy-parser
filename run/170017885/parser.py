import re
from lark import Lark, InlineTransformer
from typing import NamedTuple


class Symbol(NamedTuple):
    value: str

grammar =  Lark(r'''
start : value*

?value : NUMBER     -> number
      | CHAR -> char
      | STRING  -> string
      | SYMBOL  -> symbol
      | "nil"   -> nil
      | bool
      | quoted
      | sexpr
      | infix

NUMBER: /[+-]?(\d+(\.\d+)?)/

CHAR : /#\\[^ ]*/

bool : "#t" -> true | "true" -> true 
     | "#f" -> false | "false" -> false

infix: "[" value value value "]" 

quoted : "'" value

sexpr : "(" value* ")"

SYMBOL : /([a-zA-Z_!?%$@<>\^~&$:=\/*.][-\w+*\/!?%$@<>\^~&$:=\/*.]*)|([+-])/
STRING   : /"[^"]*"/

%ignore /;[^\n]*/
%ignore /\s+/
''', parser='lalr')
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
        if len(args) == 1:
            return args[0]
        return [Symbol('begin'), *args]
    
    def number(self,x):
        return float(x)
    def char(self, x):
        x = x.split("#\\",1)[1] 
        return self.CHARS[x.lower()] if self.CHARS.get(x.lower()) else x

    def string(self, x):
        return x[1:-1]
    
    def true(self):
        return True
    
    def false(self):
        return False
    
    def nil(self):
        return None
    
    def symbol(self, x):
        return Symbol(x)
    
    def quoted(self, x):
        return [Symbol('quote'), x]
    
    def sexpr(self, *args):
        return [*args]
    
    def infix(self, x, y, z):
        if(y == Symbol("<-")):
            return [Symbol("define"), x, z]
        else:
            return [y, x, z]