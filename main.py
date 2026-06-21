import os
from lexer import Lexer, LexicalError
from parser import Parser, ErroSintatico
from semantic import AnalisadorSemantico, ErroSemantico # <--- NOVA IMPORTAÇÃO

def main():
    os.makedirs("testes", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    test_file = os.path.join("testes", "01_variaveis.txt")
    output_file = os.path.join("output", "ast_debug.txt")

    if not os.path.exists(test_file):
        print(f"Erro: O arquivo {test_file} não foi encontrado.")
        return

    with open(test_file, "r", encoding="utf-8") as f:
        source_code = f.read()

    print("--- Código Fonte ---")
    print(source_code)
    print("-" * 20)

    try:
        # 1. Fase Léxica
        lexer = Lexer(source_code)

        # 2. Fase Sintática
        parser = Parser(lexer)
        ast = parser.parse_programa()

        print("--- Árvore Sintática Abstrata (AST) ---")
        print(ast)

        # 3. Fase Semântica <--- NOVA FASE
        semantico = AnalisadorSemantico()
        semantico.visitar(ast)
        
        print("\n--- Tabela de Símbolos ---")
        for nome, dados in semantico.tabela.simbolos.items():
            print(f"Var: '{nome}' | Tipo: {dados['tipo'].name} | Endereço SAM (Offset): {dados['offset']}")

        with open(output_file, "w", encoding="utf-8") as f_out:
            f_out.write("--- Árvore Sintática Abstrata (AST) ---\n")
            f_out.write(repr(ast))
            f_out.write("\n\n--- Tabela de Símbolos ---\n")
            f_out.write(str(semantico.tabela.simbolos))

        print(f"\n[Sucesso] Compilação passou por Léxico, Sintático e Semântico sem erros!")

    except (LexicalError, ErroSintatico, ErroSemantico) as e: # <--- CAPTURAR ERRO SEMÂNTICO
        error_msg = f"FALHA NA COMPILAÇÃO:\n{e}"
        print(f"\n{error_msg}")
        with open(output_file, "w", encoding="utf-8") as f_out:
            f_out.write(error_msg)

if __name__ == "__main__":
    main()