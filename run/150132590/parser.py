import re
from lark import Lark, InlineTransformer
from typing import NamedTuple


class Symbol(NamedTuple):
    value: str


grammar = Lark(r"""
    ?start        : value+
    ?value        : atom|lista|quote
    ?quote        : QUOTE (atom|lista)+
    ?atom         : string|constant|int|float|boolean|symbol

    lista : "("+ (elementolista) | (")"? elementolista) ")"?  // ")" //")")+
    elementolista : (atom+ (lista)*)+ ")"
    symbol        : /[-!+\/*@$%^&~<>?|\\\w=]+/
    string        : /"[^"\\]*(\\[^\n\t\r\f][^"\\]*)*"/
    int           : /-?\d+/
    float         : /-?\d+\.\d+/
    boolean       : /(\#t)|(\#f)/
    constant      : /\#\\\w+/
    QUOTE         : /^\'+/

    %ignore /\s+/
    %ignore /;[^\n]*/
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
    def string(self, token):
       return eval(token)
    
    def int(self, token):
        return int(token)
    
    def float(self, token):
        return float(token)

    def boolean(self, token):
        return True if token.value == "#t" else False
    
    def symbol(self, token):
        return Symbol(token)

    def quote(self, *args):
        parsed = []
        for arg in args:
            if arg == "'":
                parsed.append(Symbol("quote"))
            elif isinstance(arg, Symbol):
                symbol_token = arg.value
                parsed.append(Symbol(symbol_token.value))
            else:
                parsed.append(arg)
        return parsed

    def constant(self, token):
        constant = token.split('#\\')[-1]
        return (
            constant if constant.lower() not in self.CHARS 
            else self.CHARS[constant.lower()]
        )
    
    def lista(self, *args):
        for i, _ in enumerate(args):
            if isinstance(args[i], Symbol) and len(args) >= 2 and isinstance(args[i+1], list):
                return [*args]
            else:
                return list(*args)

    
    def elementolista(self, *args):
        parsed = []
        for i, _ in enumerate(args):
            if len(args) > 1 and isinstance(args[i], Symbol):
                parsed.append(Symbol(args[i].value.value))
                parsed.extend(args[i+1:])
            elif len(args) == 1 and isinstance(args[i], Symbol):
                return Symbol(args[i].value.value)
            else:
                return list(args)
        return parsed
