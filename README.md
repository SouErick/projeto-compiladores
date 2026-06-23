# Projeto de Compilador

Este repositório contém um compilador simples para uma linguagem imperativa, similar a C. O compilador passa por todas as fases clássicas: análise léxica, sintática, semântica e geração de código para a máquina virtual SAM (Stack Abstract Machine).

## Como Executar

1. Certifique-se de ter o Python 3 instalado.
2. Coloque o código-fonte que deseja compilar no arquivo `testes/01_variaveis.txt` (ou outro arquivo de teste).
3. Execute o compilador:
   ```bash
   python main.py
   ```
4. O código Assembly SAM será gerado em `output/programa.sam`.

## Gramática da Linguagem (EBNF)

A gramática a seguir descreve a estrutura da linguagem aceita pelo compilador.

```ebnf
programa        ::= (comando)*

comando         ::= declaracao | atribuicao | estrutura_controle | bloco | comando_vazio

declaracao      ::= tipo declarador ( "," declarador )* ";"
declarador      ::= ID ( "=" expressao )?
atribuicao      ::= ID "=" expressao ";" | ID ( "++" | "--" ) ";"
estrutura_controle ::= if | while
bloco           ::= "{" (comando)* "}"
comando_vazio   ::= ";"

if              ::= "if" "(" expressao ")" comando ( "else" comando )?
while           ::= "while" "(" expressao ")" comando

tipo            ::= "int" | "float" | "char"

expressao       ::= expr_logica_ou
expr_logica_ou  ::= expr_logica_e ( "||" expr_logica_e )*
expr_logica_e   ::= expr_igualdade ( "&&" expr_igualdade )*
expr_igualdade  ::= expr_soma ( ( "==" | "!=" | "<" | ">" | "<=" | ">=" ) expr_soma )*
expr_soma       ::= expr_mult ( ( "+" | "-" ) expr_mult )*
expr_mult       ::= fator ( ( "*" | "/" | "%" ) fator )*
fator           ::= ( "+" | "-" | "!" ) fator | NUM_INT | NUM_FLOAT | ID | "(" expressao ")"
```