import os
from lexer import Lexer, LexicalError
from parser import Parser, ErroSintatico
from semantic import AnalisadorSemantico, ErroSemantico
from code_sam import GeradorCodigo 

def main():
    os.makedirs("testes", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    test_file = os.path.join("testes", "01_variaveis.txt")
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

        # 2. Sintático
        parser = Parser(lexer)
        ast = parser.parse_programa()

        # 3. Semântico
        semantico = AnalisadorSemantico()
        semantico.visitar(ast)
        
        # 4. Geração de Código SAM 
        gerador = GeradorCodigo(semantico.tabela)
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