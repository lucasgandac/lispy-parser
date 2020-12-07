import re
from lark import Lark, InlineTransformer
from typing import NamedTuple


class Symbol(NamedTuple):
    value: str


grammar = Lark(
    r"""
?start : command

?command : (s_expression | atomic)+

?quote : QUOTE -> quote
QUOTE : /'/

?atomic : NUMBER -> number
        | STRING -> string
        | SYMBOL -> symbol
        | CHAR -> char
        | BOOLEAN -> boolean
        | quoted_atomic
?quoted_atomic : quote atomic

NUMBER : /[+-]?[\d]+((\/[\d]+)|((\.[\d]+)?([esfdl][+-]?[\d]+)?))/
STRING : /".*"/
SYMBOL : /[a-zA-Z+\-.*\/<=>!?:$%_&~^][\w+\-.*\/<=>!?:$%&~^]*/
CHAR : /#\\[!-~]*/
BOOLEAN : /#[tf]/

s_expression : "(" (atomic | s_expression)* ")"
              | quote s_expression

%ignore /(;[^\n]*)|([\s]+)/

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

    def command(self, *tk):
        tk = list(tk)
        if (len(tk) > 1):
            tk.insert(0, Symbol("begin"))
        return tk

    def quote(self, tk):
        return Symbol("quote")

    def quoted_atomic(self, *tk):
        return tuple(tk)

    def number(self, tk):
        return float(tk)

    def string(self, tk):
        return eval(tk)

    def symbol(self, tk):
        return Symbol(str(tk))

    def char(self, tk):
        if (len(tk) > 3):
            tk = tk[2:].lower()
            if tk in self.CHARS:
                return self.CHARS[tk]
        return tk[2:]

    def boolean(self, tk):
        if (tk == "#t"):
            return True
        else:
            return False

    def s_expression(self, *tk):
        return list(tk)

if __name__ == "__main__":
    examples = (
            "1",
            "#t",
            "#f",
            r"#\A",
            r"#\b",
            r"#\Space",
            r"#\space",
            "hello?",
            '"test string"',
            "(n)",
            "( a )",
            r"( #\b )",
            "1.2345",
            "1e-3",
            "-0.12",
            "(1 2 3 4)",
            "'1",
            "(print '1)",
            "(print '(+ 2 2 2))",
            "'(1 2 3)",
            "(print (+ 2 3))",
            "(print (+ (* 2 3) (* 1 4)))",
            "(let ((x 1) (y 2)) (+ x y))",
            "(let ((x 1) (y 2)) (print (+ x y)))",
            "((diff cos) x)",
            "(print '(1 2 3))",
            "(print ''a)"
    )

    for ex in examples:
        print(f"Example {ex}")

        print("Regular tree")
        tree = grammar.parse(ex)
        print(tree.pretty())

        print("Transformed tree")
        transformer = LispyTransformer()
        lispy = transformer.transform(tree)
        print(lispy)

        print('-'*50)