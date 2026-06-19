# ast_nodes.py

class NoAST:
    """Classe base para todos os nós da Árvore Sintática Abstrata."""
    pass

class NoPrograma(NoAST):
    """Nó raiz do programa, que contém uma lista de comandos/declarações."""
    def __init__(self, comandos):
        self.comandos = comandos  # Lista de nós (declarações, atribuições, ifs, whiles)

    def __repr__(self):
        return f"NoPrograma(comandos={self.comandos})"

class NoDeclVariavel(NoAST):
    """Nó que representa a declaração de uma variável (ex: int a = 10;)."""
    def __init__(self, tipo, nome, inicializacao=None, linha=0, coluna=0):
        self.tipo = tipo          # TipoToken (INT, FLOAT, CHAR)
        self.nome = nome          # String (nome da variável)
        self.inicializacao = inicializacao  # Nó de expressão opcional (ex: NoLiteralInt)
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        return f"NoDeclVariavel(tipo={self.tipo.name}, nome='{self.nome}', init={self.inicializacao})"

class NoAtribuicao(NoAST):
    """Nó que representa a atribuição de um valor a uma variável existente (ex: a = a + 5;)."""
    def __init__(self, nome, expressao, linha=0, coluna=0):
        self.nome = nome          # String (nome da variável destino)
        self.expressao = expressao # Nó da expressão a ser avaliada
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        return f"NoAtribuicao(nome='{self.nome}', expr={self.expressao})"

class NoOpBinaria(NoAST):
    """Nó para operações aritméticas, relacionais ou lógicas com dois operandos (ex: a + 5, x <= 10)."""
    def __init__(self, esq, op, dir, linha=0, coluna=0):
        self.esq = esq            # Nó do operando esquerdo
        self.op = op              # TipoToken (+, -, *, /, %, ==, <=, &&, etc.)
        self.dir = dir            # Nó do operando direito
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        return f"NoOpBinaria(esq={self.esq}, op={self.op.type.name}, dir={self.dir})"

class NoOpUnaria(NoAST):
    """Nó para operações com apenas um operando (ex: Negação lógica !a ou inversão -x)."""
    def __init__(self, op, expressao, linha=0, coluna=0):
        self.op = op              # TipoToken (NOT, MINUS)
        self.expressao = expressao # Nó da expressão
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        return f"NoOpUnaria(op={self.op.type.name}, expr={self.expressao})"

class NoLiteralInt(NoAST):
    """Nó para constantes inteiras (ex: 10, 42)."""
    def __init__(self, valor, linha=0, coluna=0):
        self.valor = valor        # int
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        return f"NoLiteralInt({self.valor})"

class NoLiteralFloat(NoAST):
    """Nó para constantes de ponto-flutuante (ex: 3.14)."""
    def __init__(self, valor, linha=0, coluna=0):
        self.valor = valor        # float
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        return f"NoLiteralFloat({self.valor})"

class NoVariavel(NoAST):
    """Nó que representa o uso/leitura de uma variável numa expressão (ex: o 'a' dentro de 'a + 5')."""
    def __init__(self, nome, linha=0, coluna=0):
        self.nome = nome          # String (nome da variável)
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        return f"NoVariavel('{self.nome}')"

class NoBloco(NoAST):
    """Nó que agrupa vários comandos dentro de chaves { ... }."""
    def __init__(self, comandos):
        self.comandos = comandos  # Lista de nós de comandos

    def __repr__(self):
        return f"NoBloco(comandos={self.comandos})"

class NoIf(NoAST):
    """Nó para estruturas de decisão condicional (se/então/senão)."""
    def __init__(self, condicao, bloco_then, bloco_else=None, linha=0, coluna=0):
        self.condicao = condicao    # Nó da expressão condicional
        self.bloco_then = bloco_then # Nó do tipo NoBloco ou comando único
        self.bloco_else = bloco_else # Nó opcional para o ramo 'else'
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        return f"NoIf(cond={self.condicao}, then={self.bloco_then}, else={self.bloco_else})"

class NoWhile(NoAST):
    """Nó para estruturas de repetição com teste no início (while)."""
    def __init__(self, condicao, corpo, linha=0, coluna=0):
        self.condicao = condicao    # Nó da expressão condicional
        self.corpo = corpo          # Nó do tipo NoBloco ou comando único
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        return f"NoWhile(cond={self.condicao}, corpo={self.corpo})"

class NoComandoVazio(NoAST):
    """Nó para representar um comando vazio (apenas ';')."""
    def __init__(self, linha=0, coluna=0):
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        return "NoComandoVazio()"