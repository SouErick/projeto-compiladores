# codegen.py
from enum_tokens import TipoToken

class GeradorCodigo:
    def __init__(self, tabela_simbolos):
        self.tabela = tabela_simbolos
        self.codigo = []
        self.label_count = 0  # Usado para gerar nomes únicos (ex: while0, endwhile0)

    def gerar_label(self, prefixo):
        """Gera um nome de label único para os jumps (saltos)."""
        nome = f"{prefixo}{self.label_count}"
        self.label_count += 1
        return nome

    def emitir(self, instrucao):
        """Adiciona uma instrução ao código final."""
        self.codigo.append(f"{instrucao} //")

    def emitir_label(self, label):
        """Adiciona uma label (marcação) no código final."""
        self.codigo.append(f"{label}: //")

    def gerar(self, ast):
        """Inicia a geração de código a partir da raiz (AST)."""
        self.visitar(ast)
        return "\n".join(self.codigo)

    def visitar(self, no):
        """Despachante do padrão Visitor."""
        if no is None:
            return
        nome_metodo = f'visit_{type(no).__name__}'
        metodo = getattr(self, nome_metodo, self.visit_generico)
        return metodo(no)

    def visit_generico(self, no):
        raise Exception(f"Geração de código não implementada para {type(no).__name__}")

    def visit_NoPrograma(self, no):
        # 1. Alocar espaço para todas as variáveis globais/locais no início
        total_vars = self.tabela.offset_atual
        if total_vars > 0:
            self.emitir(f"ADDSP {total_vars}")

        # 2. Visitar todos os comandos
        for comando in no.comandos:
            self.visitar(comando)

        # 3. Limpar a pilha e parar a máquina
        if total_vars > 0:
            self.emitir(f"ADDSP -{total_vars}")
        self.emitir("STOP")

    def visit_NoDeclVariavel(self, no):
        if no.inicializacao:
            # Visita a expressão (deixa o resultado no topo da pilha)
            self.visitar(no.inicializacao)
            # Pega o offset da variável na tabela de símbolos
            simbolo = self.tabela.buscar(no.nome, no.linha, no.coluna)
            # Guarda o valor na variável
            self.emitir(f"STOREOFF {simbolo['offset']}")

    def visit_NoAtribuicao(self, no):
        self.visitar(no.expressao)
        simbolo = self.tabela.buscar(no.nome, no.linha, no.coluna)
        self.emitir(f"STOREOFF {simbolo['offset']}")

    def visit_NoVariavel(self, no):
        # Quando lemos uma variável, colocamos o valor dela no topo da pilha
        simbolo = self.tabela.buscar(no.nome, no.linha, no.coluna)
        self.emitir(f"PUSHOFF {simbolo['offset']}")

    def visit_NoLiteralInt(self, no):
        self.emitir(f"PUSHIMM {no.valor}")

    def visit_NoLiteralFloat(self, no):
        # SAM normalmente lida com float de forma similar no push, mas como texto
        self.emitir(f"PUSHIMM {no.valor}")

    def visit_NoComandoVazio(self, no):
        pass

    def visit_NoBloco(self, no):
        for comando in no.comandos:
            self.visitar(comando)

    def visit_NoOpBinaria(self, no):
        self.visitar(no.esq)
        self.visitar(no.dir)
        
        # Mapeamento de operadores para instruções SAM
        if no.op.type == TipoToken.PLUS:
            self.emitir("ADD")
        elif no.op.type == TipoToken.MINUS:
            self.emitir("SUB")
        elif no.op.type == TipoToken.MUL:
            self.emitir("MUL")
        elif no.op.type == TipoToken.DIV:
            self.emitir("DIV")
        elif no.op.type == TipoToken.MOD:
            self.emitir("MOD")
            
        # Relacionais
        elif no.op.type == TipoToken.EQ:
            self.emitir("EQUAL")
        elif no.op.type == TipoToken.NEQ:
            # != é o EQUAL seguido de ISNIL (que inverte 1 para 0 e 0 para 1)
            self.emitir("EQUAL")
            self.emitir("ISNIL")
        elif no.op.type == TipoToken.LT:
            self.emitir("LESS")
        elif no.op.type == TipoToken.GT:
            self.emitir("GREATER")
        elif no.op.type == TipoToken.LE: # <= (Menor ou igual)
            # Não é maior, logo inverte o GREATER
            self.emitir("GREATER")
            self.emitir("ISNIL")
        elif no.op.type == TipoToken.GE: # >= (Maior ou igual)
            # Não é menor, logo inverte o LESS
            self.emitir("LESS")
            self.emitir("ISNIL")
            
        # Lógicos (Implementação simplificada sem curto-circuito)
        elif no.op.type == TipoToken.AND:
            self.emitir("MUL") # 1 * 1 = 1 (True), 1 * 0 = 0 (False)
        elif no.op.type == TipoToken.OR:
            self.emitir("ADD")
            self.emitir("PUSHIMM 0")
            self.emitir("GREATER") # Se a soma for > 0, é True

    def visit_NoOpUnaria(self, no):
        self.visitar(no.expressao)
        if no.op.type == TipoToken.NOT:
            # A negação em SAM é verificar se é Nulo/Zero
            self.emitir("ISNIL")
        elif no.op.type == TipoToken.MINUS:
            # Multiplicar por -1
            self.emitir("PUSHIMM -1")
            self.emitir("MUL")

    def visit_NoIf(self, no):
        label_else = self.gerar_label("else")
        label_end = self.gerar_label("endif")

        self.visitar(no.condicao)
        
        # Se a condição for falsa (0), o ISNIL transforma em 1 e salta para o Else
        self.emitir("ISNIL")
        self.emitir(f"JUMPC {label_else}")
        
        # Bloco Then
        self.visitar(no.bloco_then)
        self.emitir(f"JUMP {label_end}")
        
        # Bloco Else
        self.emitir_label(label_else)
        if no.bloco_else:
            self.visitar(no.bloco_else)
            
        self.emitir_label(label_end)

    def visit_NoWhile(self, no):
        label_start = self.gerar_label("while")
        label_end = self.gerar_label("endwhile")

        self.emitir_label(label_start)
        self.visitar(no.condicao)
        
        # Avalia a condição. Se for 0 (falso), salta para o fim
        self.emitir("ISNIL")
        self.emitir(f"JUMPC {label_end}")
        
        # Executa o corpo do laço
        self.visitar(no.corpo)
        
        # Volta ao início para testar de novo
        self.emitir(f"JUMP {label_start}")
        
        self.emitir_label(label_end)