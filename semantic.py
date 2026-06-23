from enum_tokens import TipoToken

class ErroSemantico(Exception):
    pass
# Classe responsável por gerenciar a tabela de símbolos,
# realiza a analise da AST e verifica os tipos de dados compativéis, o sentido
class TabelaSimbolos:
    def __init__(self):
        self.escopos = [{}]
        self.offset_atual = 0

    def definir(self, nome, tipo, linha, coluna):
    # posteriormente, o metódo vai reescrever a AST com o offset da variável
    # garantindo que a variável seja declarada apenas uma vez no mesmo escopo
    # e facilitando a geração do sam code.
        escopo_atual = self.escopos[-1]
        if nome in escopo_atual:
            raise ErroSemantico(f"Erro Semântico na linha {linha}, coluna {coluna}: Variável '{nome}' já foi declarada neste escopo.")
        offset = self.offset_atual
        escopo_atual[nome] = {
            'tipo': tipo,
            'offset': offset
        }
        self.offset_atual += 1
        return offset

    def buscar(self, nome, linha, coluna): # busca do mais interno para o mais externo
        for escopo in reversed(self.escopos):
            if nome in escopo:
                return escopo[nome]
        raise ErroSemantico(f"Erro Semântico na linha {linha}, coluna {coluna}: Variável '{nome}' não declarada.")

    def entrar_escopo(self):
        self.escopos.append({})

    def sair_escopo(self):
        if len(self.escopos) > 1:
            self.escopos.pop()

    @property # @property permite acessar o metódo como se fosse um atributo 
    def simbolos(self):
        return {k: v for escopo in self.escopos for k, v in escopo.items()}

class AnalisadorSemantico:
    # principal classe responsável por percorrer a AST e verificar a semântica do código, como tipos de dados, declarações e atribuições
    # vai visitar os nós da AST, e reescrever a AST com o offset da variável de acordo
    # com a tabela de símbolos
    def __init__(self):
        self.tabela = TabelaSimbolos()

    def visitar(self, no):
        if no is None:
            return
        
        nome_metodo = f'visit_{type(no).__name__}'
        metodo = getattr(self, nome_metodo, self.visit_generico)
        return metodo(no)

    def visit_generico(self, no):
        for child in no.__dict__.values():
            if isinstance(child, list):
                for item in child:
                    if hasattr(item, 'linha'): # Garante que é um nó
                        self.visitar(item)
            elif hasattr(child, 'linha'): # Heurística para identificar um nó
                self.visitar(child)

    def visit_NoPrograma(self, no):
        for comando in no.comandos:
            self.visitar(comando)

    def visit_NoDeclVariavel(self, no):
        tipo_declarado = no.tipo

        if no.inicializacao:
            tipo_expressao = self.visitar(no.inicializacao)
            if tipo_declarado == TipoToken.INT and tipo_expressao == TipoToken.FLOAT:
                raise ErroSemantico(f"Erro Semântico na linha {no.linha}: Não é possível atribuir um valor FLOAT a uma variável INT ('{no.nome}').")
            if tipo_declarado != tipo_expressao and not (tipo_declarado == TipoToken.FLOAT and tipo_expressao == TipoToken.INT):
                 raise ErroSemantico(f"Erro Semântico na linha {no.linha}: Tipo da expressão ({tipo_expressao.name}) é incompatível com o tipo declarado ({tipo_declarado.name}) para a variável '{no.nome}'.")
        
        no.offset = self.tabela.definir(no.nome, no.tipo, no.linha, no.coluna)

    def visit_NoAtribuicao(self, no):
        simbolo = self.tabela.buscar(no.nome, no.linha, no.coluna)
        no.offset = simbolo['offset']
        tipo_variavel = simbolo['tipo']

        tipo_expressao = self.visitar(no.expressao)

        if tipo_variavel == TipoToken.INT and tipo_expressao == TipoToken.FLOAT:
            raise ErroSemantico(f"Erro Semântico na linha {no.linha}: Não é possível atribuir um valor FLOAT a uma variável INT ('{no.nome}').")
        if tipo_variavel != tipo_expressao and not (tipo_variavel == TipoToken.FLOAT and tipo_expressao == TipoToken.INT):
            raise ErroSemantico(f"Erro Semântico na linha {no.linha}: Tipo da expressão ({tipo_expressao.name}) é incompatível com o tipo da variável '{no.nome}' ({tipo_variavel.name}).")

    def visit_NoVariavel(self, no):
        simbolo = self.tabela.buscar(no.nome, no.linha, no.coluna)
        no.offset = simbolo['offset']
        return simbolo['tipo']

    def visit_NoOpBinaria(self, no):
        tipo_esq = self.visitar(no.esq)
        tipo_dir = self.visitar(no.dir)

        op = no.op.type

        if op in (TipoToken.PLUS, TipoToken.MINUS, TipoToken.MUL, TipoToken.DIV, TipoToken.MOD):
            if not (tipo_esq in (TipoToken.INT, TipoToken.FLOAT) and tipo_dir in (TipoToken.INT, TipoToken.FLOAT)):
                raise ErroSemantico(f"Erro Semântico na linha {no.linha}: Operação aritmética '{no.op.value}' inválida entre os tipos {tipo_esq.name} e {tipo_dir.name}.")
            if tipo_esq == TipoToken.FLOAT or tipo_dir == TipoToken.FLOAT:
                return TipoToken.FLOAT
            return TipoToken.INT

        if op in (TipoToken.EQ, TipoToken.NEQ, TipoToken.LT, TipoToken.GT, TipoToken.LE, TipoToken.GE):
            if not (tipo_esq in (TipoToken.INT, TipoToken.FLOAT) and tipo_dir in (TipoToken.INT, TipoToken.FLOAT)):
                 raise ErroSemantico(f"Erro Semântico na linha {no.op.line}: Comparação '{no.op.value}' inválida entre os tipos {tipo_esq.name} e {tipo_dir.name}.")
            return TipoToken.INT

        if op in (TipoToken.AND, TipoToken.OR):
            if not (tipo_esq == TipoToken.INT and tipo_dir == TipoToken.INT):
                raise ErroSemantico(f"Erro Semântico na linha {no.op.line}: Operação lógica '{no.op.value}' requer operandos do tipo INT (booleano), mas recebeu {tipo_esq.name} e {tipo_dir.name}.")
            return TipoToken.INT

        raise ErroSemantico(f"Erro Semântico na linha {no.linha}: Operador binário desconhecido ou não suportado '{op.name}'.")

    def visit_NoOpUnaria(self, no):
        tipo_expr = self.visitar(no.expressao)
        op = no.op.type

        if op == TipoToken.MINUS: 
            if tipo_expr not in (TipoToken.INT, TipoToken.FLOAT):
                raise ErroSemantico(f"Erro Semântico na linha {no.linha}: Operador '-' não pode ser aplicado ao tipo {tipo_expr.name}.")
            return tipo_expr

        if op == TipoToken.NOT: 
            if tipo_expr != TipoToken.INT:
                 raise ErroSemantico(f"Erro Semântico na linha {no.linha}: Operador '!' requer um operando do tipo INT (booleano), mas recebeu {tipo_expr.name}.")
            return TipoToken.INT

        raise ErroSemantico(f"Erro Semântico na linha {no.linha}: Operador unário desconhecido '{op.name}'.")

    def visit_NoIf(self, no):
        tipo_condicao = self.visitar(no.condicao)
        if tipo_condicao != TipoToken.INT:
            raise ErroSemantico(f"Erro Semântico na linha {no.linha}: A condição do 'if' deve ser do tipo booleano (INT), mas é do tipo {tipo_condicao.name}.")
        self.visitar(no.bloco_then)
        if no.bloco_else:
            self.visitar(no.bloco_else)

    def visit_NoWhile(self, no):
        tipo_condicao = self.visitar(no.condicao)
        if tipo_condicao != TipoToken.INT:
            raise ErroSemantico(f"Erro Semântico na linha {no.linha}: A condição do 'while' deve ser do tipo booleano (INT), mas é do tipo {tipo_condicao.name}.")
        self.visitar(no.corpo)

    def visit_NoBloco(self, no):
        self.tabela.entrar_escopo()
        for comando in no.comandos:
            self.visitar(comando)
        self.tabela.sair_escopo()

    def visit_NoLiteralInt(self, no):
        return TipoToken.INT

    def visit_NoLiteralFloat(self, no):
        return TipoToken.FLOAT

    def visit_NoComandoVazio(self, no):
        pass