''' 
INSTITUTO FEDERAL DE BRASÍLIA (CAMPUS TAGUATINGA)
PROFESSOR: DANIEL SAAD
ALUNO: ERICK SOUSA SARAIVA
DISCIPINA: COMPILADORES
DATA: 23/06/2026 '''

import os
import sys
from lexer import Lexer, LexicalError
from parser import Parser, ErroSintatico
from semantic import AnalisadorSemantico, ErroSemantico
from code_sam import GeradorCodigo 

def main():
    os.makedirs("testes", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    if len(sys.argv) > 1:
        test_file = sys.argv[1]
    else:
        default_filename = "01_variaveis.txt"
        test_file = os.path.join("testes", default_filename)
        print(f"Nenhum arquivo de entrada especificado. Usando o padrão: {test_file}")

    output_file_ast = os.path.join("output", "ast_debug.txt")
    output_file_sam = os.path.join("output", "programa.sam") 

    if not os.path.exists(test_file):
        print(f"Erro: O arquivo {test_file} não foi encontrado.")
        return

    with open(test_file, "r", encoding="utf-8") as f:
        source_code = f.read()

    print("--- Iniciando Compilação ---")

    try:
        # 1. Léxico
        lexer = Lexer(source_code)

        # 2. Sintático, os tokens terão uma noção hierárquica, e serão organizados em uma árvore de sintaxe abstrata (AST)
        parser = Parser(lexer)
        ast = parser.parse_programa() # gera a AST (Árvore de Sintaxe Abstrata)

        # 3. Semântico
        semantico = AnalisadorSemantico() 
        semantico.visitar(ast)
        
        # 4. Geração de Código SAM 
        gerador = GeradorCodigo(total_vars=semantico.tabela.offset_atual)
        codigo_sam = gerador.gerar(ast)

        with open(output_file_ast, "w", encoding="utf-8") as f_out:
            f_out.write("--- AST ---\n" + repr(ast) + "\n\n--- Tabela de Símbolos ---\n" + str(semantico.tabela.simbolos))

        with open(output_file_sam, "w", encoding="utf-8") as f_out:
            f_out.write(codigo_sam)

        print("\n--- Código Assembly SAM Gerado ---")
        print(codigo_sam)
        print(f"\n[Sucesso] Compilação finalizada! Arquivo salvo em: {output_file_sam}")

    except (LexicalError, ErroSintatico, ErroSemantico) as e:
        print(f"\nFALHA NA COMPILAÇÃO:\n{e}")

if __name__ == "__main__":
    main()