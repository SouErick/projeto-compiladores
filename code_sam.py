from enum_tokens import TipoToken

# visita a AST com offset da variável, percorrendo pós ordem 
# vai emitir a quantidade de variáveis declaradas, 
# e gerar o sam code com base na AST
class GeradorCodigo:
    def __init__(self, total_vars):
        self.total_vars = total_vars
        self.codigo = []
        self.label_count = 0  

    # bloco para condições e laços, para gerar labels únicas
    def gerar_label(self, prefixo):
        nome = f"{prefixo}{self.label_count}"
        self.label_count += 1
        return nome

    def emitir(self, instrucao, comentario=""):
        self.codigo.append(f"{instrucao:<12} // {comentario}")

    def emitir_label(self, label):
        self.codigo.append(f"{label}:")

    def gerar(self, ast):
        self.visitar(ast)
        return "\n".join(self.codigo)

    # visita a AST, chamando o método específico para cada tipo de nó
    def visitar(self, no):
        if no is None:
            return
        if isinstance(no, list):
            for item in no:
                self.visitar(item)
            return
        nome_metodo = f'visit_{type(no).__name__}'
        metodo = getattr(self, nome_metodo, self.visit_generico)
        return metodo(no)

    def visit_generico(self, no):
        raise Exception(f"Geração de código não implementada para {type(no).__name__}")

    def visit_NoPrograma(self, no):
        if self.total_vars > 0:
            self.emitir(f"ADDSP {self.total_vars}", f"Aloca espaço para {self.total_vars} variáveis")

        for comando in no.comandos:
            self.visitar(comando)

        if self.total_vars > 0:
            self.emitir(f"ADDSP -{self.total_vars}", "Libera espaço das variáveis")
        self.emitir("STOP", "Fim do programa")

    def visit_NoDeclVariavel(self, no):
        if no.inicializacao:
            self.visitar(no.inicializacao)
            self.emitir(f"STOREOFF {no.offset}", f"Salva valor inicial em '{no.nome}'")

    def visit_NoAtribuicao(self, no):
        self.visitar(no.expressao)
        self.emitir(f"STOREOFF {no.offset}", f"Atribuição para '{no.nome}'")

    def visit_NoVariavel(self, no):
        self.emitir(f"PUSHOFF {no.offset}", f"Lê valor de '{no.nome}'")

    def visit_NoLiteralInt(self, no):
        self.emitir(f"PUSHIMM {no.valor}", f"Literal inteiro {no.valor}")

    def visit_NoLiteralFloat(self, no):
        self.emitir(f"PUSHIMM {no.valor}", f"Literal float {no.valor}")

    def visit_NoComandoVazio(self, no):
        pass

    def visit_NoBloco(self, no): # sempre que entrar em um bloco, cria um novo escopo, e ao sair do bloco, remove o escopo
        for comando in no.comandos:
            self.visitar(comando)

    def visit_NoOpBinaria(self, no):
        self.visitar(no.esq)
        self.visitar(no.dir)

        # Operadores        
        if no.op.type == TipoToken.PLUS:
            self.emitir("ADD", f"{no.esq} + {no.dir}")
        elif no.op.type == TipoToken.MINUS:
            self.emitir("SUB", f"{no.esq} - {no.dir}")
        elif no.op.type == TipoToken.MUL:
            self.emitir("MUL", f"{no.esq} * {no.dir}")
        elif no.op.type == TipoToken.DIV:
            self.emitir("DIV", f"{no.esq} / {no.dir}")
        elif no.op.type == TipoToken.MOD:
            self.emitir("MOD", f"{no.esq} % {no.dir}")
            
        # Relacionais
        elif no.op.type == TipoToken.EQ:
            self.emitir("EQUAL", f"{no.esq} == {no.dir}")
        elif no.op.type == TipoToken.NEQ:
            self.emitir("EQUAL", f"{no.esq} == {no.dir}")
            self.emitir("ISNIL", "Inverte para !=")
        elif no.op.type == TipoToken.LT:
            self.emitir("LESS", f"{no.esq} < {no.dir}")
        elif no.op.type == TipoToken.GT:
            self.emitir("GREATER", f"{no.esq} > {no.dir}")
        elif no.op.type == TipoToken.LE: 
            self.emitir("GREATER", f"{no.esq} > {no.dir}")
            self.emitir("ISNIL", "Inverte para <=")
        elif no.op.type == TipoToken.GE: 
            self.emitir("LESS", f"{no.esq} < {no.dir}")
            self.emitir("ISNIL", "Inverte para >=")
            
        elif no.op.type == TipoToken.AND:
            self.emitir("MUL", "Lógica AND (a*b)")
        elif no.op.type == TipoToken.OR:
            self.emitir("ADD", "Lógica OR (a+b)")
            self.emitir("PUSHIMM 0", "Comparar com 0")
            self.emitir("GREATER", "Se soma > 0, é true")

    def visit_NoOpUnaria(self, no):
        self.visitar(no.expressao)
        if no.op.type == TipoToken.NOT:
            self.emitir("ISNIL", "Negação lógica (!)")
        elif no.op.type == TipoToken.MINUS:
            self.emitir("PUSHIMM -1", "Para negação aritmética")
            self.emitir("MUL", "Inverte o sinal")

    def visit_NoIf(self, no):
        label_else = self.gerar_label("else")
        label_end = self.gerar_label("endif")

        self.visitar(no.condicao)
        
        self.emitir(f"JUMPZ {label_else}", "Pula se a condição for falsa")
        
        self.visitar(no.bloco_then)
        self.emitir(f"JUMP {label_end}", "Pula o bloco else")
        
        self.emitir_label(label_else)
        if no.bloco_else:
            self.visitar(no.bloco_else)
            
        self.emitir_label(label_end)

    def visit_NoWhile(self, no):
        label_start = self.gerar_label("while")
        label_end = self.gerar_label("endwhile")

        self.emitir_label(label_start)
        self.visitar(no.condicao)
        
        self.emitir(f"JUMPZ {label_end}", "Sai do laço se a condição for falsa")
        
        self.visitar(no.corpo)
        
        self.emitir(f"JUMP {label_start}", "Volta para o início do while")
        
        self.emitir_label(label_end)