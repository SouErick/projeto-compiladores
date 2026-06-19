from enum_tokens import TipoToken
from ast_nodes import (
    NoPrograma, NoDeclVariavel, NoAtribuicao, NoOpBinaria, NoOpUnaria,
    NoLiteralInt, NoLiteralFloat, NoVariavel, NoBloco, NoIf, NoWhile,
    NoComandoVazio
)

class ErroSintatico(Exception):
    pass

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        # Pede o primeiro token ao lexer para inicializar
        self.current_token = self.lexer.get_next_token()

    def error(self, mensagem):
        """Lança uma exceção detalhada caso a sintaxe esteja incorreta."""
        raise ErroSintatico(f"Erro Sintático na linha {self.current_token.line}, coluna {self.current_token.column}: {mensagem}")

    def eat(self, tipo_esperado):
        """
        Verifica se o token atual é o esperado. 
        Se for, 'come' o token e avança para o próximo.
        Se não for, lança erro sintático.
        """
        if self.current_token.type == tipo_esperado:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Esperado token {tipo_esperado.name}, mas encontrou {self.current_token.type.name}")

    def parse_programa(self):
        """programa -> comando* EOF"""
        comandos = []
        while self.current_token.type != TipoToken.EOF:
            comandos.append(self.parse_comando())
        return NoPrograma(comandos)

    def parse_comando(self):
        """Roteia para o tipo certo de comando baseado no token atual."""
        tipo = self.current_token.type
        
        # Se começar com um tipo primitivo, é uma declaração
        if tipo in (TipoToken.INT, TipoToken.FLOAT, TipoToken.CHAR):
            return self.parse_declaracao()
            
        # Se começar com ID, é uma atribuição (por agora, ignoramos chamadas de função independentes)
        elif tipo == TipoToken.ID:
            return self.parse_atribuicao()
            
        # Se for { é um bloco de comandos
        elif tipo == TipoToken.LBRACE:
            return self.parse_bloco()
            
        elif tipo == TipoToken.IF:
            return self.parse_if()
            
        elif tipo == TipoToken.WHILE:
            return self.parse_while()
            
        # Adiciona suporte para o "comando vazio" (empty statement)
        elif tipo == TipoToken.SEMI:
            return self.parse_comando_vazio()
            
        else:
            self.error(f"Comando inválido ou inesperado. Token atual: {self.current_token.value}")

    def parse_comando_vazio(self):
        """comando_vazio -> ';'"""
        token = self.current_token
        self.eat(TipoToken.SEMI)
        return NoComandoVazio(token.line, token.column)

    def parse_bloco(self):
        """bloco -> '{' comando* '}'"""
        self.eat(TipoToken.LBRACE)
        comandos = []
        while self.current_token.type != TipoToken.RBRACE and self.current_token.type != TipoToken.EOF:
            comandos.append(self.parse_comando())
        self.eat(TipoToken.RBRACE)
        return NoBloco(comandos)

    def parse_declaracao(self):
        """declaracao -> (INT | FLOAT | CHAR) ID ('=' expressao)? ';'"""
        token_tipo = self.current_token
        self.eat(token_tipo.type) # Come o int, float ou char
        
        token_id = self.current_token
        self.eat(TipoToken.ID)    # Come o nome da variável
        
        inicializacao = None
        # Verifica se há inicialização na mesma linha (ex: int a = 5;)
        if self.current_token.type == TipoToken.ASSIGN:
            self.eat(TipoToken.ASSIGN)
            inicializacao = self.parse_expressao()
            
        self.eat(TipoToken.SEMI)  # Obrigatório ponto-e-vírgula no final
        return NoDeclVariavel(token_tipo.type, token_id.value, inicializacao, token_tipo.line, token_tipo.column)

    def parse_atribuicao(self):
        """atribuicao -> ID '=' expressao ';'"""
        token_id = self.current_token
        self.eat(TipoToken.ID)
        self.eat(TipoToken.ASSIGN)
        
        expr = self.parse_expressao()
        self.eat(TipoToken.SEMI)
        
        return NoAtribuicao(token_id.value, expr, token_id.line, token_id.column)

    def parse_if(self):
        """if_stmt -> IF '(' expressao ')' comando (ELSE comando)?"""
        token_if = self.current_token
        self.eat(TipoToken.IF)
        self.eat(TipoToken.LPAREN)
        condicao = self.parse_expressao()
        self.eat(TipoToken.RPAREN)
        
        bloco_then = self.parse_comando()
        bloco_else = None
        
        if self.current_token.type == TipoToken.ELSE:
            self.eat(TipoToken.ELSE)
            bloco_else = self.parse_comando()
            
        return NoIf(condicao, bloco_then, bloco_else, token_if.line, token_if.column)

    def parse_while(self):
        """while_stmt -> WHILE '(' expressao ')' comando"""
        token_while = self.current_token
        self.eat(TipoToken.WHILE)
        self.eat(TipoToken.LPAREN)
        condicao = self.parse_expressao()
        self.eat(TipoToken.RPAREN)
        
        corpo = self.parse_comando()
        return NoWhile(condicao, corpo, token_while.line, token_while.column)

    # ==========================================
    # Parsing de Expressões (Precedência)
    # ==========================================

    def parse_expressao(self):
        """expressao -> expr_and (OR expr_and)*"""
        no = self.parse_expr_and()
        while self.current_token.type == TipoToken.OR:
            op = self.current_token
            self.eat(TipoToken.OR)
            no = NoOpBinaria(no, op, self.parse_expr_and(), op.line, op.column)
        return no

    def parse_expr_and(self):
        """expr_and -> expr_relacional (AND expr_relacional)*"""
        no = self.parse_expr_relacional()
        while self.current_token.type == TipoToken.AND:
            op = self.current_token
            self.eat(TipoToken.AND)
            no = NoOpBinaria(no, op, self.parse_expr_relacional(), op.line, op.column)
        return no

    def parse_expr_relacional(self):
        """expr_relacional -> expr_soma ( (== | != | < | > | <= | >=) expr_soma )*"""
        no = self.parse_expr_soma()
        
        operadores_relacionais = (
            TipoToken.EQ, TipoToken.NEQ, TipoToken.LT, 
            TipoToken.GT, TipoToken.LE, TipoToken.GE
        )
        
        while self.current_token.type in operadores_relacionais:
            op = self.current_token
            self.eat(op.type)
            no = NoOpBinaria(no, op, self.parse_expr_soma(), op.line, op.column)
        return no

    def parse_expr_soma(self):
        """expr_soma -> expr_mult ( (+ | -) expr_mult )*"""
        no = self.parse_expr_mult()
        while self.current_token.type in (TipoToken.PLUS, TipoToken.MINUS):
            op = self.current_token
            self.eat(op.type)
            no = NoOpBinaria(no, op, self.parse_expr_mult(), op.line, op.column)
        return no

    def parse_expr_mult(self):
        """expr_mult -> fator ( (* | / | %) fator )*"""
        no = self.parse_fator()
        while self.current_token.type in (TipoToken.MUL, TipoToken.DIV, TipoToken.MOD):
            op = self.current_token
            self.eat(op.type)
            no = NoOpBinaria(no, op, self.parse_fator(), op.line, op.column)
        return no

    def parse_fator(self):
        """fator -> NUM_INT | NUM_FLOAT | ID | '(' expressao ')' | (+ | - | !) fator"""
        token = self.current_token
        
        # Operadores unários (ex: -5, !verdadeiro)
        if token.type in (TipoToken.PLUS, TipoToken.MINUS, TipoToken.NOT):
            self.eat(token.type)
            return NoOpUnaria(token, self.parse_fator(), token.line, token.column)
            
        elif token.type == TipoToken.NUM_INT:
            self.eat(TipoToken.NUM_INT)
            return NoLiteralInt(token.value, token.line, token.column)
            
        elif token.type == TipoToken.NUM_FLOAT:
            self.eat(TipoToken.NUM_FLOAT)
            return NoLiteralFloat(token.value, token.line, token.column)
            
        elif token.type == TipoToken.ID:
            self.eat(TipoToken.ID)
            return NoVariavel(token.value, token.line, token.column)
            
        elif token.type == TipoToken.LPAREN:
            self.eat(TipoToken.LPAREN)
            no = self.parse_expressao()
            self.eat(TipoToken.RPAREN)
            return no
            
        else:
            self.error(f"Fator inesperado: {token.value}")