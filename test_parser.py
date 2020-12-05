import pytest
import math
from typing import Dict, Any, Union
from lark import Lark
from functools import lru_cache
from hypothesis import given
from hypothesis.strategies import floats, integers, one_of


Xs = integers(-1_000, 1_000)
pos_Xs = integers(1, 1_000)
neg_Xs = integers(-1_000, -1)
nonzero_Xs = one_of(pos_Xs, neg_Xs)
short = integers(-5, 5)


class Error(str):
    def __bool__(self):
        return False


@lru_cache(1)
def mod():
    ns: Dict[str, Any] = {"__name__": "parser"}
    exec(open("parser.py").read(), ns)
    try:
        grammar = ns["grammar"]
    except KeyError:
        raise ValueError(
            "não definiu a gramática lark no módulo parser.py\n"
            "Defina a gramática e salve-a na variável grammar."
        )
    if isinstance(grammar, str):
        grammar: Lark = Lark(grammar)

    try:
        transformer_class = ns["CalcTransformer"]
    except KeyError:
        raise ValueError("não definiu a classe CalcTransformer no módulo parser.py")

    return grammar, transformer_class


def accepts(st):
    grammar = mod()[0]
    try:
        grammar.parse(st)
        return True
    except Exception as ex:
        return Error(str(ex))


def rejects(st):
    return not accepts(st)


def value(st) -> Union[float, list, Error]:
    grammar, transformer_class = mod()
    try:
        tree = grammar.parse(st)
    except Exception as ex:
        return Error(str(ex))
    else:
        transformer = transformer_class()
        value = transformer.transform(tree)
        if type(value) is tuple:
            return list(value)
        return value


def tree(st):
    grammar, _ = mod()
    return grammar.parse(st)


class TestAnalisadorSintatico:
    def test_aceita_variaveis(self):
        assert accepts("pi")
        assert accepts("x")
        assert accepts("x0")
        assert accepts("variavel_como_nome_longo")

    def test_aceita_numeros_em_varios_formatos(self):
        assert accepts("42")
        assert accepts("42.0")
        assert accepts("3.1415")
        assert accepts("4.2e1")
        assert accepts("4.2e+1")
        assert accepts("12.34e-10")

    def testa_aceita_expressoes_matematicas_simples(self):
        assert accepts("40 + 2")
        assert accepts("21 * 2")
        assert accepts("84 / 2")
        assert accepts("50 - 8")
        assert accepts("10^5")

    def testa_aceita_expressoes_matematicas_compostas(self):
        assert accepts("(20 + 20) + 2")
        assert accepts("(10 + 11) * 2")
        assert accepts("2 * (2 * (3 + 2) + 11)")

    def test_calcula_numeros(self):
        assert value("42") == 42
        assert value("42.0") == 42.0
        assert value("3.1415") == 3.1415
        assert value("4.2e1") == 4.2e1
        assert value("4.2e+1") == 4.2e1
        assert value("12.34e-10") == 12.34e-10

    def testa_calcula_expressoes_matematicas_simples(self):
        assert value("40 + 2") == 42
        assert value("21 * 2") == 42
        assert value("84 / 2") == 42
        assert value("50 - 8") == 42
        assert value("10^5") == 100_000

    @given(Xs, short, nonzero_Xs)
    def test_precedencia_de_operacoes_basicas(self, x, y, z):
        assert value(f"{x} + {y} * {z}") == x + y * z
        assert value(f"{x} + {y} / {z}") == x + y / z
        assert value(f"{x} - {y} * {z}") == x - y * z
        assert value(f"{x} * {y} + {z}") == x * y + z
        
        if y > 0 or x != 0:
            assert value(f"{x} ^ {y} + {z}") == x ** y + z
            assert value(f"{x} ^ {y} * {z}") == x ** y * z

    @given(Xs, nonzero_Xs, nonzero_Xs)
    def test_associatividade_a_esquerda(self, x, y, z):
        assert value(f"{x} - {y} - {z}") == (x - y) - z
        assert value(f"{x} / {y} / {z}") == (x / y) / z
        assert value(f"{x} - {y} + {z}") == (x - y) + z
        assert value(f"{x} / {y} * {z}") == (x / y) * z

    def test_calcula_comparacoes(self):
        assert value("40 > 2")
        assert value("40 >= 2")
        assert value("2 >= 2")
        assert value("4 < 20")
        assert value("4 <= 20")
        assert value("4 <= 4")
        assert value("40 != 2")
        assert not value("40 == 2")

    def test_precedencia_de_comparacoes(self):
        assert value("2 + 2 > 3") is True
        assert value("2 + 3 == 5") is True

    def test_rejeita_comparacoes_aninhadas(self):
        assert rejects("3 > 2 > 1")
        assert rejects("3 < 2 < 1")
        assert rejects("3 == 2 == 1")

    @given(nonzero_Xs, short, short)
    def test_associatividade_a_direita(self, x, y, z):
        if y != 0 or z > 0: 
            assert value(f"{x} ^ {y} ^ {z}") == x ** (y ** z)

    def test_calcula_valores_de_variaveis_padrao(self):
        assert value("pi") == math.pi 
        assert callable(value("sin"))
        
    def test_chamada_de_funcao_simples(self):
        assert value("cos(pi)") == -1
        assert value("abs(-2)") == 2

    def test_chamada_de_funcao_de_varios_argumentos(self):
        assert value("max(1, 2, 3)") == 3
        assert value("min(1, 2, 3, 4)") == 1

    def test_calcula_negativos(self):
        assert value("-42") == -42
        assert value("-2 * 2") == -4
        assert value("2 * (-2)") == -4
        assert value("-pi") <= -3.14
        if value("cos(pi)"):
            assert value("-cos(pi)") == 1
        else:
            assert accepts("-cos(pi)")

    def test_realiza_atribuicao_de_variaveis(self):
        assert value("x = 21\n2 * x") == 42
        assert value("x = 0\nx = 21\n2 * x") == 42

    def test_atribuicao_de_variaveis_retorna_valor_salvo(self):
        assert value("x = 42") == 42

    def test_aceita_comentarios_com_hashtags(self):
        assert value("42  # a resposta para a pergunta fundamental") == 42
        assert value("2 + 2  # uma operação simples") == 4

    def test_programa_completo(self):
        src = """
        # Exemplo de código
        x = 10
        y = cos(pi)
        z = 2 ^ 2 - 2
        (2 * x - y) * z
        """
        print(src)
        print(tree(src).pretty())
        assert value(src) == 42

