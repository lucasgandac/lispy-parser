import re
from lark import Lark, InlineTransformer
from typing import NamedTuple

class Symbol(NamedTuple):
    value: str

grammar = Lark(
r"""
?start: lispy
?lispy:  quote |atom*
quote: /(?:quote\s|\'{1,2})/ atom
?atom: STRING -> string 
    | list
    | CHARACTER -> char
    | "#t" -> true
    | "#f" -> false
    | INTEGER -> integer
    | FLOAT -> float
    | variable
variable: /[a-zA-Z-_?+<=*]+/
STRING: "\"" (/.+/) "\""
CHARACTER: /#\\.*/
FLOAT: /\d+(\.\d+)?/
INTEGER: /\d+/
list: "(" atom* ")"
%ignore /\s+|\\n|;;.*\n/
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
        token = token[1:-1]
        return str(token)

    def char(self, token):
        value = token[2:]

        if self.CHARS.get(value.lower()):
            return self.CHARS[value.lower()]
        return value

    def float(self, token):
        return float(token)

    def integer(self, token):
        return int(token)

    def false(self):
        return False

    def true(self):
        return True

    def variable(self, token):
        return Symbol(token.value)

    def list(self, *args):

        return list(args)
    def quote(self, quote_token, value):

        print("====<<<")
        print(value)
        return [Symbol('quote'), value]

    def lispy(self, *args):
        return args

    def command(self, *args):
        print(args)
        return args

if __name__ == '__main__':

    code = r'''
    '(1 2 3)
    '''

    parsed_code = grammar.parse(code)
    print(code)
    print(parsed_code.pretty())
    print(LispyTransformer().transform(parsed_code))