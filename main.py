import os
from lexer import Lexer
from enum_tokens import TipoToken


def main():
    # Garante que as pastas testes e output existem (cria se não existir)
    os.makedirs("testes", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    
    # Caminho para o arquivo de teste e arquivo de saída do debug
    test_file = os.path.join("testes", "01_variaveis.txt")
    output_file = os.path.join("output", "tokens_debug.txt")
    
    if not os.path.exists(test_file):
        print(f"Erro: O arquivo {test_file} não foi encontrado.")
        return

    # Lê o conteúdo do código-fonte
    with open(test_file, 'r', encoding='utf-8') as f:
        source_code = f.read()

    print("--- Código Fonte ---")
    print(source_code)
    print("-" * 20)
    print("--- Tokens ---")

    # Bloco try-except estruturado para capturar erros do compilador
    try:
        # Inicializa o Lexer e varre os tokens
        lexer = Lexer(source_code)
        token = lexer.get_next_token()
        
        # Abre o arquivo de saída para gravar os logs
        with open(output_file, 'w', encoding='utf-8') as f_out:
            f_out.write("--- Log de Tokens gerados pelo Lexer ---\n")
            
            while token.type != TipoToken.EOF:
                print(token)
                f_out.write(f"{token}\n")  # Grava no arquivo txt
                token = lexer.get_next_token()
            
            f_out.write(f"{token}\n")      # Grava o token EOF
            
        print(f"\n[Sucesso] Log de tokens salvo no arquivo: {output_file}")
            
    except Exception as e:
        error_msg = f"FALHA NA COMPILAÇÃO:\n{e}"
        print(f"\n{error_msg}")
        with open(output_file, 'w', encoding='utf-8') as f_out:
            f_out.write(error_msg)

if __name__ == "__main__":
    main()