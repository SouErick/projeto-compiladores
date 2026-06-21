# semantic.py
from enum_tokens import TipoToken
from ast_nodes import NoDeclVariavel, NoAtribuicao, NoVariavel

class ErroSemantico(Exception):
    pass

class TabelaSimbolos:
    def __init__(self):
        # Dicionário que mapeia o nome da variável para seus metadados (tipo e offset)
        self.simbolos = {}
        # O offset atual na pilha de memória local (FBR)
        self.offset_atual = 0

    def definir(self, nome, tipo, linha, coluna):
        if nome in self.simbolos:
            raise ErroSemantico(f"Erro Semântico na linha {linha}, coluna {coluna}: Variável '{nome}' já foi declarada.")
        
        self.simbolos[nome] = {
            'tipo': tipo,
            'offset': self.offset_atual
        }
        self.offset_atual += 1

    def buscar(self, nome, linha, coluna):
        if nome not in self.simbolos:
            raise ErroSemantico(f"Erro Semântico na linha {linha}, coluna {coluna}: Variável '{nome}' não declarada.")
        return self.simbolos[nome]


class AnalisadorSemantico:
    def __init__(self):
        self.tabela = TabelaSimbolos()

    def visitar(self, no):
        """Método despachante: chama o método visit_ especifico para o tipo de nó."""
        if no is None:
            return
        
        # Cria o nome do método dinamicamente baseado na classe do Nó (ex: visit_NoPrograma)
        nome_metodo = f'visit_{type(no).__name__}'
        metodo = getattr(self, nome_metodo, self.visit_generico)
        return metodo(no)

    def visit_generico(self, no):
        raise Exception(f"Nenhum método visit_{type(no).__name__} definido no Analisador Semântico.")

    def visit_NoPrograma(self, no):
        for comando in no.comandos:
            self.visitar(comando)

    def visit_NoDeclVariavel(self, no):
        # 1. Verifica a expressão de inicialização (se houver) ANTES de declarar
        if no.inicializacao:
            self.visitar(no.inicializacao)
        
        # 2. Adiciona a variável na Tabela de Símbolos
        self.tabela.definir(no.nome, no.tipo, no.linha, no.coluna)

    def visit_NoAtribuicao(self, no):
        # 1. Verifica se a variável existe
        self.tabela.buscar(no.nome, no.linha, no.coluna)
        # 2. Visita a expressão do lado direito
        self.visitar(no.expressao)

    def visit_NoVariavel(self, no):
        # Verifica se a variável que está a ser usada numa expressão existe
        self.tabela.buscar(no.nome, no.linha, no.coluna)

    def visit_NoOpBinaria(self, no):
        self.visitar(no.esq)
        self.visitar(no.dir)

    def visit_NoOpUnaria(self, no):
        self.visitar(no.expressao)

    def visit_NoIf(self, no):
        self.visitar(no.condicao)
        self.visitar(no.bloco_then)
        if no.bloco_else:
            self.visitar(no.bloco_else)

    def visit_NoWhile(self, no):
        self.visitar(no.condicao)
        self.visitar(no.corpo)

    def visit_NoBloco(self, no):
        for comando in no.comandos:
            self.visitar(comando)

    def visit_NoLiteralInt(self, no):
        pass # Literais não precisam de checagem semântica aqui

    def visit_NoLiteralFloat(self, no):
        pass

    def visit_NoComandoVazio(self, no):
        pass