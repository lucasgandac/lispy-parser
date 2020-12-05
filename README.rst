=============================
Analisador sintático de Lispy
=============================

Complete o código do arquivo parser.py para passar em todos os testes em test_parser.py. 
As expressões regulares do analisador sintático Lark já estão implementadas e não precisam 
ser alteradas. Assim como no trabalho anterior, você deve instalar o pyest no computador 
para rodar a suite de testes (`apt install pytest`). A partir daí, basta digitar `pytest` 
para executar os testes.

Existem algumas opções do pytest que facilitam a execução de conjuntos específicos 
de testes, como mostram os exemplos abaixo:

* `pytest --maxfail=1` - para a execução após a primeira falha
* `pytest --lf` - repete apenas os testes que falharam da última vez
* `pytest -k quote` - seleciona apenas os testes que possuem "quote" no nome. Você pode trocar "quote" por qualquer outra palavra. 

A proficiência é demonstrada a partir do resultado dos testes:

* 6 ou mais acertos: [cfg-bnf]
* 8 ou mais acertos: anteriores + [cfg-ebnf]
* 10 ou mais acertos: anteriores + [cfg-reduce]


**ATENÇÃO** A suite de testes utilizada para correção pode conter exemplos adicionais para evitar
implementações que mirem especificamente nos testes.


Entrega
-------

O trabalho deverá ser entregue até dia 03/02 utilizando formulário disponibilizado pelo professor.
Atrasos de até 1 emana serão penalizados em 2 acertos e atrasos maiores implicarão no não-recebimento 
do trabalho. O aluno nesta situação terá que propor outra atividade para comprovar proficiência.


Regras sintáticas
-----------------

Scheme/Lispy possui pouquíssimas regras gramaticais. Cada código em Lispy é formado por uma 
sequência de valores, onde cada valor pode ser um elemento atômico como número, string, símbolo/variável,
caractere ou booleano ou ainda por uma S-Expression, que consiste basicamente numa lista 
como `(+ 1 2)` onde o primeiro elemento é interpretado como uma função e os seguintes como 
seus operadores. 

Listas de Lispy podem conter quaisquer elementos em quaisquer posições, inclusive outras listas.
Além destes elementos básicos, também temos a regra de "quoting", que evita a avaliação de um pedaço
de código, preservando seu valor como elemento da árvore sintática. O quoting é feito com o operador
de aspas simples (``'``) e pode ser aplicado antes de qualquer elemento como em ``'(1 2 3)`` ou ``'quoted-symbol``
ou ainda ``'42``. 

Implemente as regras desta gramática completando a string de declaração da gramática no arquivo
parser.py. 

Árvores sintáticas
------------------

As árvores sintáticas resultantes devem ser convertidas em estruturas de dados Python correspondentes.
Isto pode ser feito implementando os métodos da classe LispyTransformer, associando-os a cada símbolo
relevante da gramática.

As árvores sintáticas de Lispy devem ser traduzidas em listas ou tuplas do Python. Desta forma,
um código Scheme como ``(1 2 3)`` deve ser traduzido para a lista Python ``[1, 2, 3]``

Além disto, os elementos atômicos devem ser convertidos para os seus valores correspondentes em Python.
Por simplicidade, é possível converter todos números pra float e interpretar strings apenas pela remoção
das aspas de início e fim. Além disto, os elementos do tipo caractere devem ser convertidos para strings
de tamanho 1, onde as formas especiais como ``#\space`` dadas pelo dicionário LispyTransformer.CHARS devem ser 
respeitadas. Lembrem-se que os elementos especiais de um único carater são sensíveis à capitalização, 
enquanto que os que possuem mais de um carater não. Assim, ``#\A`` difere de ``#\a``, mas ``#\Space`` é
distinto de ``#\space``.