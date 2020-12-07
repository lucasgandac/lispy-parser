import re
from lark import Lark, InlineTransformer
from typing import NamedTuple
import math
import re

class Symbol(NamedTuple):
    value: str

grammar = Lark(r"""
?start : expr               -> start               

?expr   :   expr " " atom   -> expr
        |   atom

?atom   :   BEGIN  -> begin
        |   STRING          -> string
        |   BOOL            -> booler
        |   QUOTE           -> quote
        |   NUMBER          -> number
        |   NAME            -> name
        |   OP              -> name
        |   CHAR            -> char
        |   "(" expr ")"    -> listing 
        |   expr "(" expr ")" -> listingquote       
        |   expr expr         -> expr    
        
BEGIN   : /(([(][^(^)]*[)])([\\n ]*)([(][^()]*[)]))|(^([1-9][ ])*[1-9]$)/
CHAR   : /[#][\\[\w&.-?<>%!]*/
BOOL    : /#t|#f|null/
STRING  : /(^([\"])+([-+%$#\s<>\[\]\n\r\b\f]|[\\]|[\"]|[\']|(\w))+(\")(?!.*\"))/
QUOTE   : /^[']+/
NUMBER  : /-?\d+(\.\d+)?/
NAME    : /[\w&.\-?<>%!]+/
OP      : /[+-\/*=]/

%ignore /\s+/
%ignore /\n /
%ignore /[^~]+[']$/
%ignore /([;]([\w&.\-?<>%!;]|[^\n])*)/
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

    def start(self, x):

        valueReturn = x
        strValue = str(valueReturn)
        numSymbol = strValue.count('Symbol(value')

        if Symbol(value='quote') in x:
            valueReturn = x
        elif isinstance(valueReturn, list):
            if  len(x) == 1:
                valueReturn = x[0]
            elif numSymbol == 0:
                valueReturn = x
            else:
                valueReturn = x[0]
        else:
            valueReturn = x[0]

        if isinstance(valueReturn, list):
            if numSymbol == 0 and len(valueReturn) > 1:
                symbolReturn = [Symbol('begin')]
                valueReturn = symbolReturn + valueReturn
        
        return valueReturn

    def begin(self, x, y):
        symbolReturn = [Symbol('begin')]
        return symbolReturn

    def expr(self, x, y):
        x = x + y
        return x

    def duolisting(self, x, y):
        x = x + y
        return x

    def listingquote(self, x, y):
        x = x + [y]
        valueReturn = x
        strValue = str(valueReturn)
        numSymbol = strValue.count(str(Symbol(value='quote')))

        if numSymbol == 0:
            symbolReturn = [Symbol('begin')]
            valueReturn = symbolReturn + valueReturn
        return list([valueReturn])

    def string(self, x):
        return list([str(x.strip('\"'))])

    def booler(self, x):
        return list([bool(x)])

    def number(self, x):
        return list([float(x)])
    
    def name(self, x):
        symbolReturn = Symbol(str(x))
        return list([symbolReturn])


    def quote(self, x):
        symbolReturn = Symbol('quote')
        return list([symbolReturn])

    def char(self, x):

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

        charText = str(x)
        charText = charText.strip('#\\')
        charAsk = charText.lower()

        if CHARS.get(charAsk):
            return list([CHARS[str(charAsk)]])
        else:
            return list([charText])
    
    def listing(self, x):
        return list([x])