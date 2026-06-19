import os
from lexer import Lexer, LexicalError
from parser import Parser, ErroSintatico


def main():
    # Garante que as pastas testes e output existem (cria se não existir)
    os.makedirs("testes", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    # Caminho para o arquivo de teste e arquivo de saída do debug
    test_file = os.path.join("testes", "01_variaveis.txt")
    output_file = os.path.join("output", "ast_debug.txt")

    if not os.path.exists(test_file):
        print(f"Erro: O arquivo {test_file} não foi encontrado.")
        return

    # Lê o conteúdo do código-fonte
    with open(test_file, "r", encoding="utf-8") as f:
        source_code = f.read()

    print("--- Código Fonte ---")
    print(source_code)
    print("-" * 20)

    # Bloco try-except estruturado para capturar erros do compilador
    try:
        # 1. Fase Léxica: Cria o lexer
        lexer = Lexer(source_code)

        # 2. Fase Sintática: Cria o parser e constrói a AST
        parser = Parser(lexer)
        ast = parser.parse_programa()

        # 3. Impressão e gravação da AST
        print("--- Árvore Sintática Abstrata (AST) ---")
        print(ast)

        with open(output_file, "w", encoding="utf-8") as f_out:
            f_out.write("--- Árvore Sintática Abstrata (AST) ---\n")
            f_out.write(repr(ast))

        print(f"\n[Sucesso] AST salva no arquivo: {output_file}")

    except (LexicalError, ErroSintatico) as e:
        error_msg = f"FALHA NA COMPILAÇÃO:\n{e}"
        print(f"\n{error_msg}")
        with open(output_file, "w", encoding="utf-8") as f_out:
            f_out.write(error_msg)

if __name__ == "__main__":
    main()