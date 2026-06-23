# estrutura de dados responsavel por armazenar a arvore de sintaxe abstrata, para uso
# auxiliar na analise semantica e geração de código. Cada nó representa uma construção da linguagem (ex: declaração, expressão).
class NoAST:
    pass
class NoPrograma(NoAST):
    def __init__(self, comandos):
        self.comandos = comandos

    def __repr__(self):
        return f"NoPrograma(comandos={self.comandos})"

class NoDeclVariavel(NoAST):
    def __init__(self, tipo, nome, inicializacao=None, linha=0, coluna=0):
        self.tipo = tipo          
        self.nome = nome          
        self.inicializacao = inicializacao  
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        tipo_str = self.tipo.name if hasattr(self.tipo, 'name') else str(self.tipo)
        return f"NoDeclVariavel(tipo={tipo_str}, nome='{self.nome}', init={self.inicializacao})"

class NoAtribuicao(NoAST):
    def __init__(self, nome, expressao, linha=0, coluna=0):
        self.nome = nome          
        self.expressao = expressao 
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        return f"NoAtribuicao(nome='{self.nome}', expr={self.expressao})"

class NoOpBinaria(NoAST):
    def __init__(self, esq, op, dir, linha=0, coluna=0):
        self.esq = esq            
        self.op = op              
        self.dir = dir            
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        return f"NoOpBinaria(esq={self.esq}, op={self.op.type.name}, dir={self.dir})"

class NoOpUnaria(NoAST):
    def __init__(self, op, expressao, linha=0, coluna=0):
        self.op = op              
        self.expressao = expressao 
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        return f"NoOpUnaria(op={self.op.type.name}, expr={self.expressao})"

class NoLiteralInt(NoAST):
    def __init__(self, valor, linha=0, coluna=0):
        self.valor = valor        
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        return f"NoLiteralInt({self.valor})"

class NoLiteralFloat(NoAST):
    def __init__(self, valor, linha=0, coluna=0):
        self.valor = valor        
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        return f"NoLiteralFloat({self.valor})"

class NoVariavel(NoAST):
    def __init__(self, nome, linha=0, coluna=0):
        self.nome = nome          
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        return f"NoVariavel('{self.nome}')"

class NoBloco(NoAST):
    def __init__(self, comandos):
        self.comandos = comandos  

    def __repr__(self):
        return f"NoBloco(comandos={self.comandos})"

class NoIf(NoAST):
    def __init__(self, condicao, bloco_then, bloco_else=None, linha=0, coluna=0):
        self.condicao = condicao    
        self.bloco_then = bloco_then 
        self.bloco_else = bloco_else 
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        return f"NoIf(cond={self.condicao}, then={self.bloco_then}, else={self.bloco_else})"

class NoWhile(NoAST):
    def __init__(self, condicao, corpo, linha=0, coluna=0):
        self.condicao = condicao    
        self.corpo = corpo          
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        return f"NoWhile(cond={self.condicao}, corpo={self.corpo})"

class NoComandoVazio(NoAST):
    def __init__(self, linha=0, coluna=0):
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        return "NoComandoVazio()"