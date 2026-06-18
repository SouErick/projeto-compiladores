from enum import Enum, auto

class TipoToken(Enum):
    # Tipos e Palavras-chave
    INT = auto()       # Tipo inteiro
    FLOAT = auto()     # Tipo ponto-flutuante
    CHAR = auto()      # Tipo caractere
    IF = auto()        # se
    ELSE = auto()      # senao
    WHILE = auto()     # enquanto
    
    # Identificadores e Literais
    ID = auto()        # Nome de variável/função
    NUM_INT = auto()   # Valor inteiro (ex: 42)
    NUM_FLOAT = auto() # Valor float (ex: 3.14)
    
    # Operadores Aritméticos
    PLUS = auto()      # +
    MINUS = auto()     # -
    MUL = auto()       # *
    DIV = auto()       # /
    MOD = auto()       # %
    
    # Atribuição e Delimitadores
    ASSIGN = auto()    # =
    SEMI = auto()      # ;
    LPAREN = auto()    # (
    RPAREN = auto()    # )
    LBRACE = auto()    # {
    RBRACE = auto()    # }
    
    EOF = auto()       # Fim de arquivo

# Dicionário rápido para identificar palavras-chave reservadas
KEYWORDS = {
    'int': TipoToken.INT,
    'float': TipoToken.FLOAT,
    'char': TipoToken.CHAR,
    'if': TipoToken.IF,
    'else': TipoToken.ELSE,
    'while': TipoToken.WHILE,
}

class Token:
    def __init__(self, type_, value, line, column):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type.name}, {repr(self.value)}, ln:{self.line}, col:{self.column})"