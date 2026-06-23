from enum_tokens import TipoToken, Token
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
        self.current_token = self.lexer.get_next_token()

    def error(self, mensagem):
        raise ErroSintatico(f"Erro Sintático na linha {self.current_token.line}, coluna {self.current_token.column}: {mensagem}")

    def eat(self, tipo_esperado):
        if self.current_token.type == tipo_esperado:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Esperado token {tipo_esperado.name}, mas encontrou {self.current_token.type.name}")

    def parse_programa(self):
        comandos = []
        while self.current_token.type != TipoToken.EOF:
            # Um comando pode retornar uma lista de nós (ex: int a, b;)
            resultado = self.parse_comando()
            if isinstance(resultado, list):
                comandos.extend(resultado)
            else:
                comandos.append(resultado)
        return NoPrograma(comandos)

    def parse_comando(self):
        tipo = self.current_token.type
        
        if tipo in (TipoToken.INT, TipoToken.FLOAT, TipoToken.CHAR):
            return self.parse_declaracao()
            
        elif tipo == TipoToken.ID:
            return self.parse_atribuicao_ou_incremento()
            
        elif tipo == TipoToken.LBRACE:
            return self.parse_bloco()
            
        elif tipo == TipoToken.IF:
            return self.parse_if()
            
        elif tipo == TipoToken.WHILE:
            return self.parse_while()
            
        elif tipo == TipoToken.SEMI:
            return self.parse_comando_vazio()
            
        else:
            self.error(f"Comando inválido ou inesperado. Token atual: {self.current_token.value}")

    def parse_comando_vazio(self):
        token = self.current_token
        self.eat(TipoToken.SEMI)
        return NoComandoVazio(token.line, token.column)

    def parse_bloco(self):
        self.eat(TipoToken.LBRACE)
        comandos = []
        while self.current_token.type != TipoToken.RBRACE and self.current_token.type != TipoToken.EOF:
            resultado = self.parse_comando()
            if isinstance(resultado, list):
                comandos.extend(resultado)
            else:
                comandos.append(resultado)
        self.eat(TipoToken.RBRACE)
        return NoBloco(comandos)

    def parse_declaracao(self):
        token_tipo = self.current_token
        self.eat(token_tipo.type)

        declaracoes = []
        
        while True:
            token_id = self.current_token
            self.eat(TipoToken.ID)
            
            inicializacao = None
            if self.current_token.type == TipoToken.ASSIGN:
                self.eat(TipoToken.ASSIGN)
                inicializacao = self.parse_expressao()
            
            declaracoes.append(NoDeclVariavel(token_tipo.type, token_id.value, inicializacao, token_id.line, token_id.column))

            if self.current_token.type == TipoToken.COMMA:
                self.eat(TipoToken.COMMA)
                continue
            else:
                break

        self.eat(TipoToken.SEMI)
        return declaracoes

    def parse_atribuicao_ou_incremento(self):
        token_id = self.current_token
        self.eat(TipoToken.ID)

        if self.current_token.type == TipoToken.ASSIGN:
            self.eat(TipoToken.ASSIGN)
            expr = self.parse_expressao()
            self.eat(TipoToken.SEMI)
            return NoAtribuicao(token_id.value, expr, token_id.line, token_id.column)
        
        elif self.current_token.type in (TipoToken.INC, TipoToken.DEC):
            op_token = self.current_token
            self.eat(op_token.type)
            self.eat(TipoToken.SEMI)

            op_binaria = TipoToken.PLUS if op_token.type == TipoToken.INC else TipoToken.MINUS
            expressao = NoOpBinaria(NoVariavel(token_id.value), Token(op_binaria, '', op_token.line, op_token.column), NoLiteralInt(1))
            return NoAtribuicao(token_id.value, expressao, token_id.line, token_id.column)
        else:
            self.error(f"Esperado '=', '++' ou '--' após o identificador '{token_id.value}'")

    def parse_atribuicao(self):
        token_id = self.current_token
        self.eat(TipoToken.ID)
        self.eat(TipoToken.ASSIGN)
        
        expr = self.parse_expressao()
        self.eat(TipoToken.SEMI)
        
        return NoAtribuicao(token_id.value, expr, token_id.line, token_id.column)

    def parse_if(self):
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
        token_while = self.current_token
        self.eat(TipoToken.WHILE)
        self.eat(TipoToken.LPAREN)
        condicao = self.parse_expressao()
        self.eat(TipoToken.RPAREN)
        
        corpo = self.parse_comando()
        return NoWhile(condicao, corpo, token_while.line, token_while.column)


    def parse_expressao(self):
        return self.parse_expr_logica_ou()

    def parse_expr_logica_ou(self):
        no = self.parse_expr_logica_e()
        while self.current_token.type == TipoToken.OR:
            op = self.current_token
            self.eat(op.type)
            no = NoOpBinaria(no, op, self.parse_expr_logica_e(), op.line, op.column)
        return no

    def parse_expr_logica_e(self):
        no = self.parse_expr_igualdade()
        while self.current_token.type == TipoToken.AND:
            op = self.current_token
            self.eat(op.type)
            no = NoOpBinaria(no, op, self.parse_expr_igualdade(), op.line, op.column)
        return no

    def parse_expr_igualdade(self):
        no = self.parse_expr_soma()
        
        operadores = (TipoToken.EQ, TipoToken.NEQ, TipoToken.LT, TipoToken.GT, TipoToken.LE, TipoToken.GE)
        
        while self.current_token.type in operadores:
            op = self.current_token
            self.eat(op.type)
            no = NoOpBinaria(no, op, self.parse_expr_soma(), op.line, op.column)
        return no

    def parse_expr_soma(self):
        no = self.parse_expr_mult()
        while self.current_token.type in (TipoToken.PLUS, TipoToken.MINUS):
            op = self.current_token
            self.eat(op.type)
            no = NoOpBinaria(no, op, self.parse_expr_mult(), op.line, op.column)
        return no

    def parse_expr_mult(self):
        no = self.parse_fator()
        while self.current_token.type in (TipoToken.MUL, TipoToken.DIV, TipoToken.MOD):
            op = self.current_token
            self.eat(op.type)
            no = NoOpBinaria(no, op, self.parse_fator(), op.line, op.column)
        return no

    def parse_fator(self):
        token = self.current_token
        
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