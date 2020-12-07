import re
from lark import Lark, InlineTransformer
from typing import NamedTuple


class Symbol(NamedTuple):
    value: str

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
	def converte_elementos_atomicos(self,value):
		try:
			value = float(value)
		except:
			value = str(value)
			value = value.replace('\"',"")
		return value
	
	def converte_chars(self,a):
		a = str(a)
		a = a[a.rindex('\\')+1:].upper()
		return "\n" if a == "LINEFEED" else a
		
	def to_str(self,a):
		a = str(a)
		if a.contains("\\"):
			a = a[a.rindex('\\')+1:].upper()
			return "\n" if a == "LINEFEED" else a
		return a

grammar = Lark(r"""

start : expression

expression : LPAR operator expression* number* RPAR 
			| LPAR operator expression* string* RPAR
			| STRING*
			| NAME*
			| NUMBER*
			
number : NUMBER -> converte_elementos_atomicos
string : NAME -> converte_elementos_atomicos

operator : OPERATOR | NAME

NUMBER : /-?(0|[1-9]\d*)(\.\d+)?([eE][+-]?\d+)?/
LPAR   : /\(/
RPAR   : /\)/
NAME   : /[#?\\?%?\w\w*\-?>?\w*\!?\??\.?]+/
BOOL   : /#t|#f|true|false/
//STRING : /^\'+\"+[\w].*[\w]*'/
STRING: /^\"[\w].*[\w]*\"/
CHAR   : /[#|\\a|\b|\\Backspace]+\"+/
COMMENT: /[;;].*$/
QUOTES : /\'+|\"+)/
OPERATOR : /[\?==|<=|=|>=\-+\*\/<>]+/

%ignore /\s+/
""")

exemplo = [
	'"hello world"',
	"42",
	"3.1415",
	"#t",
	"#\\A",
	"some-lispy-name",
	"name?",
]
tranformer = LispyTransformer()

for ex in exemplo:
	tree = grammar.parse(ex)
	result  = tranformer.transform(tree)

