import pytest
from lark import Lark
from functools import lru_cache


class Error(str):
    def __bool__(self):
        return False


@lru_cache(1)
def mod():
    ns = {"__name__": "parser"}
    exec(open("parser.py").read(), ns)
    try:
        grammar = ns["grammar"]
    except KeyError:
        raise ValueError(
            "não definiu a gramática lark no módulo parser.py\n"
            "Defina a gramática e salve-a na variável grammar."
        )
        if isinstance(grammar, str):
            grammar = Lark(grammar)

    try:
        transformer_class = ns["LispyTransformer"]
    except KeyError:
        raise ValueError("não definiu a classe LispyTransformer no módulo parser.py")

    try:
        symbol_class = ns["Symbol"]
    except KeyError:
        raise ValueError("não definiu a classe Symbol no módulo parser.py")

    return grammar, transformer_class(), symbol_class


def accepts(st):
    grammar, _, _ = mod()
    try:
        grammar.parse(st)
        return True
    except Exception as ex:
        return Error(str(ex))


def rejects(st):
    return not accepts(st)


def value(st):
    grammar, transformer, _ = mod()
    try:
        tree = grammar.parse(st)
    except Exception as ex:
        return Error(str(ex))
    else:
        value = transformer.transform(tree)
        if type(value) is tuple:
            return list(value)
        return value


@lru_cache
def symbol(x):
    return mod()[-1](x)


class TestAnalisadorSintatico:
    def test_aceita_elementos_atomicos(self):
        for src in [
            '"hello world"',
            "42",
            "3.1415",
            "#t",
            "#\\A",
            "some-lispy-name",
            "name?",
        ]:
            assert accepts(src), f'rejeitou comando "{src}"'

    def test_aceita_listas_simples(self):
        assert accepts("(+ 1 2)")
        assert accepts("(odd? 42)")

    def test_aceita_listas_aninhadas(self):
        assert accepts("(let ((x 1) (y 2)) (+ x y))")
        assert accepts("((diff cos) x)")

    def test_aceita_valor_com_quote(self):
        assert accepts("'(1 2 3)")
        assert accepts("'symbol")
        assert accepts("''double-quote")

    def test_rejeita_listas_desalinhadas(self):
        assert rejects(")a b c(")
        assert rejects("(a b")
        assert rejects("(a b))")

    def test_rejeita_quotes_inválidos(self):
        assert rejects("'foo'")
        assert rejects("foo'")
        assert rejects("'")

    def test_converte_elementos_atomicos(self):
        assert value('"hello world"') == "hello world"
        assert value("42") == 42.0
        assert value("3.1415") == 3.1415
        assert value("#t") is True
        assert value("some-lispy-name") == symbol("some-lispy-name")
        assert value("name?") == symbol("name?")

    def test_converte_listas(self):
        assert value("(max 1 2)") == [symbol("max"), 1, 2]
        assert value("(max (list 1 2 3))") == [symbol("max"), [symbol("list"), 1, 2, 3]]

    def test_converte_quotes(self):
        assert value("'(1 2 3)") == [symbol("quote"), [1, 2, 3]]
        assert value("'symbol") == [symbol("quote"), symbol("symbol")]

    def test_converte_chars(self):
        assert value(r"#\A") == "A"
        assert value(r"#\linefeed") == "\n"
        assert value(r"#\LineFeed") == "\n"

    def test_inclui_comando_begin_em_sequencia_de_comandos(self):
        assert value("(cmd 1)\n(cmd 2)") == [
            symbol("begin"),
            [symbol("cmd"), 1],
            [symbol("cmd"), 2],
        ]
        assert value("1 2 3") == [symbol("begin"), 1, 2, 3]

    def test_aceita_programa_completo_com_comentário(self):
        src = """
        ;; Fatorial
        (define fat (lambda (n) 
            (if (<= n 1)
                1
                (* n (fat (- n 1))))))

        (print (fat 5))
        """
        print("Testando comando")
        print(src)
        s = symbol
        assert value(src) == [
            s("begin"),
            [
                s("define"),
                s("fat"),
                [
                    s("lambda"),
                    [s("n")],
                    [
                        s("if"),
                        [s("<="), s("n"), 1],
                        1,
                        [s("*"), s("n"), [s("fat"), [s("-"), s("n"), 1]]],
                    ],
                ],
            ],
            [s("print"), [s("fat"), 5]],
        ]
