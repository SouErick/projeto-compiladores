from enum_tokens import TipoToken, KEYWORDS, Token


# Exceção customizada para erros na fase Léxica
class LexicalError(Exception):
    pass

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
        self.line = 1
        self.column = 1

    def advance(self):
        """Avança o ponteiro e atualiza o caractere atual."""
        if self.current_char == '\n':
            self.line += 1
            self.column = 0
            
        self.pos += 1
        self.column += 1
        
        if self.pos >= len(self.text):
            self.current_char = None  # Indica o fim do arquivo
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        """Ignora espaços em branco, tabulações e quebras de linha."""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def number(self):
        """Lê um número e decide se é INT ou FLOAT."""
        result = ''
        start_col = self.column
        is_float = False
        
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if is_float:
                    break # Já tem um ponto, então para (evita 3.14.15)
                is_float = True
            result += self.current_char
            self.advance()

        if is_float:
            return Token(TipoToken.NUM_FLOAT, float(result), self.line, start_col)
        return Token(TipoToken.NUM_INT, int(result), self.line, start_col)

    def identifier(self):
        """Lê identificadores e verifica se são palavras-chave."""
        result = ''
        start_col = self.column
        
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()

        # Verifica se o texto lido é uma palavra reservada
        token_type = KEYWORDS.get(result, TipoToken.ID)
        return Token(token_type, result, self.line, start_col)

    def get_next_token(self):
        """O cérebro do Lexer: retorna o próximo token do código."""
        while self.current_char is not None:
            
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isalpha() or self.current_char == '_':
                return self.identifier()

            if self.current_char.isdigit():
                return self.number()

            # Operadores de um caractere
            char = self.current_char
            col = self.column
            
            if char == '+':
                self.advance()
                return Token(TipoToken.PLUS, char, self.line, col)
            if char == '-':
                self.advance()
                return Token(TipoToken.MINUS, char, self.line, col)
            if char == '*':
                self.advance()
                return Token(TipoToken.MUL, char, self.line, col)
            if char == '/':
                self.advance()
                return Token(TipoToken.DIV, char, self.line, col)
            if char == '%':
                self.advance()
                return Token(TipoToken.MOD, char, self.line, col)
            if char == '=':
                self.advance()
                return Token(TipoToken.ASSIGN, char, self.line, col)
            if char == ';':
                self.advance()
                return Token(TipoToken.SEMI, char, self.line, col)
            if char == '{':
                self.advance()
                return Token(TipoToken.LBRACE, char, self.line, col)
            if char == '}':
                self.advance()
                return Token(TipoToken.RBRACE, char, self.line, col)
            if char == '(':
                self.advance()
                return Token(TipoToken.LPAREN, char, self.line, col)
            if char == ')':
                self.advance()
                return Token(TipoToken.RPAREN, char, self.line, col)

            # Se chegou aqui e não reconheceu o caractere, levanta um erro
            raise LexicalError(f"Erro Léxico: Caractere inesperado '{self.current_char}' na linha {self.line}, coluna {self.column}")

        return Token(TipoToken.EOF, None, self.line, self.column)