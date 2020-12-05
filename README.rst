====================
Calculadora avançada
====================

Complete o código do arquivo parser.py para passar em todos os testes em test_parser.py. 
As expressões regulares do analisador sintático Lark já estão implementadas e não precisam 
ser alteradas. Você deve instalar o pyest e a biblioteca hypothesis no computador 
para rodar a suite de testes (`apt install pytest && pip3 install hypothesis --user`). A partir daí, 
basta digitar `pytest` para executar os testes.

Existem algumas opções do pytest que facilitam a execução de conjuntos específicos 
de testes, como mostram os exemplos abaixo:

* `pytest --maxfail=1` - para a execução após a primeira falha
* `pytest --lf` - repete apenas os testes que falharam da última vez
* `pytest -k quote` - seleciona apenas os testes que possuem "quote" no nome. Você pode trocar "quote" por qualquer outra palavra. 

A proficiência é demonstrada a partir do resultado dos testes:
 
* 10 ou mais acertos: [re-criar], [lex-ler], [lex-criar], [cfg-classicas]
* 13 ou mais acertos: anteriores + [cfg-bnf] + [cfg-ebnf]
* 15 ou mais acertos: anteriores + [cfg-op] + [comp-org]
* 17 ou mais acertos: anteriores + [cfg-reduce] + [cfg-ast]
* 19 ou mais acertos: anteriores + [proj-calc]


**ATENÇÃO** A suite de testes utilizada para correção pode conter exemplos adicionais para evitar
implementações que mirem especificamente nos testes.


Calculadora iterativa
---------------------

Este repositório contem o arquivo calc.py, que lê a gramática definida em parser.py e implementa 
um terminal interativo para a calculadora. Este recurso pode ser utilizado para testar a 
calculadora durante o desenvolvimento da mesma, mas não será avaliado. Você pode executar o
terminal interativo com o comando::
    
    $ python calc.py


Entrega
-------

O trabalho deverá ser entregue até dia 18/12 submetendo um pull request para o repositório do trabalho.
Lembre-se sempre de completar as informações no arquivo aluno.py


Regras sintáticas
-----------------

A calculadora avançada possui símbolos de controle como operadores matemáticos e parênteses. Fora isto,
possui também dois tipos de elementos léxicos importantes:

* Números: Números não possuem sinal, a parte decimal é opcional e ainda podem conter uma terminação 
  em formato de notação científica. Exemplos: 1, 42, 3.14, 6.022e23, 6.67E-11, etc.  
* Nomes: Nomes de variáveis contem letras, números e underscores, mas não podem começar com um 
  número. Exemplos: x, y1, nome, variavel_com_nome_longo, OutroNomeLongo 


Regras de precedência e operadores
-----------------------------------

A calculadora avançada entende as quatro operações fundamentais (``+, -, *, /``). Além de potências, que 
são representadas pelo operador ``^`` (diferentemente do Python que utiliza ``**``). A precedência e 
associatividade destes operadores é a usual: potências possuem a maior precedência, seguida de 
multiplicação e divisão e, por último, somas e subtrações. Destas operações, apenas a de exponenciação
possui precedência à direita, enquanto todas as outras possuem precedência à esquerda.

A calculadora também deve aceitar operadores de comparação (``>, <, >=, <=, ==, !=``). Estes operadores
possuem precedência **menor** que os operadores aritimeticos, de forma que ``x + y > z`` deve ser 
interpretada como ``(x + y) > z`` (o mesmo vale para qualquer outra operação aritimetica). Os operadores
de comparação **não** são associativos e comparações encadeadas como ``x > y > z`` são consideradas 
inválidas.

A calculadora entende operações matemáticas do módulo math como chamada de funções. A calculadora
entende funções de 1 ou mais variáveis. Exemplos: ``cos(x), sin(3.14), exp(2), min(1, 2)``.

Finalmente, a calculadora também aceita declaração de variáveis e várias linhas de entrada. Variáveis podem 
ser salvas e posteriormente utilizadas em outras expressões como no exemplo::

    # Esta é uma linha de comentário!
    x = 42
    x ^ x / x - x * x