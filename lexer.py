from enum_tokens import TipoToken, KEYWORDS, Token


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
        if self.current_char == '\n':
            self.line += 1
            self.column = 0
            
        self.pos += 1
        self.column += 1
        
        if self.pos >= len(self.text):
            self.current_char = None  
        else:
            self.current_char = self.text[self.pos]

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos >= len(self.text):
            return None
        return self.text[peek_pos]

    def skip_comment(self):
        while self.current_char is not None and self.current_char != '\n':
            self.advance()
        self.skip_whitespace() 

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def number(self):
        result = ''
        start_col = self.column
        is_float = False
        
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if is_float:
                    break 
                is_float = True
            result += self.current_char
            self.advance()

        if is_float:
            return Token(TipoToken.NUM_FLOAT, float(result), self.line, start_col)
        return Token(TipoToken.NUM_INT, int(result), self.line, start_col)

    def identifier(self):
        result = ''
        start_col = self.column
        
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()

        token_type = KEYWORDS.get(result, TipoToken.ID)
        return Token(token_type, result, self.line, start_col)

    def get_next_token(self):
        while self.current_char is not None:
            
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == '/' and self.peek() == '/':
                self.skip_comment()
                continue

            if self.current_char.isalpha() or self.current_char == '_':
                return self.identifier()

            if self.current_char.isdigit():
                return self.number()

            char = self.current_char
            col = self.column
            
            if char == '+':
                self.advance()
                if self.current_char == '+':
                    self.advance()
                    return Token(TipoToken.INC, '++', self.line, col)
                return Token(TipoToken.PLUS, char, self.line, col)
            if char == '-':
                self.advance()
                if self.current_char == '-':
                    self.advance()
                    return Token(TipoToken.DEC, '--', self.line, col)
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
                if self.current_char == '=':
                    self.advance()
                    return Token(TipoToken.EQ, '==', self.line, col)
                return Token(TipoToken.ASSIGN, '=', self.line, col)
                
            if char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TipoToken.NEQ, '!=', self.line, col)
                return Token(TipoToken.NOT, '!', self.line, col)
                
            if char == '>':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TipoToken.GE, '>=', self.line, col)
                return Token(TipoToken.GT, '>', self.line, col)
                
            if char == '<':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TipoToken.LE, '<=', self.line, col)
                return Token(TipoToken.LT, '<', self.line, col)
                
            if char == '&':
                self.advance()
                if self.current_char == '&':
                    self.advance()
                    return Token(TipoToken.AND, '&&', self.line, col)
                raise LexicalError(f"Erro Léxico: Esperado '&' após '&' na linha {self.line}, coluna {self.column}")
                
            if char == '|':
                self.advance()
                if self.current_char == '|':
                    self.advance()
                    return Token(TipoToken.OR, '||', self.line, col)
                raise LexicalError(f"Erro Léxico: Esperado '|' após '|' na linha {self.line}, coluna {self.column}")

            if char == ';':
                self.advance()
                return Token(TipoToken.SEMI, char, self.line, col)
            if char == ',':
                self.advance()
                return Token(TipoToken.COMMA, char, self.line, col)
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

            raise LexicalError(f"Erro Léxico: Caractere inesperado '{self.current_char}' na linha {self.line}, coluna {self.column}")

        return Token(TipoToken.EOF, None, self.line, self.column)