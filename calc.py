# Atenção! Este arquivo não será avaliado!!!
#
# O arquivo calc.py importa o conteúdo do módulo parser e fornece scripts úteis para testar o
# analisador sintático interativamente a partir da linha de comando.
#
import parser


def repl():
    print("CALCULADORA++")
    print("Digite comandos no prompt. O comando quit encerra a sessão.\n")
    print('O comando "debug" mostra ou oculta as árvores sintáticas intermediárias')

    env = parser.CalcTransformer()
    tree = None
    debug = False

    while True:
        src = input(">>> ")
        if src == "quit":
            break
        if src == "debug":
            debug = True
            if tree:
                print(tree.pretty())
            continue

        try:
            tree = parser.grammar.parse(src)
        except Exception as e:
            print(f"Erro de sintaxe: {e}")
            continue

        if debug:
            print(tree.pretty())
        print(env.transform(tree))


if __name__ == "__main__":
    repl()
