import sys

##########
# CONSTS #
##########

DIGITS = "1234567890"
CHARS = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"

##########
# ERRORS #
##########

class Error:
    def __init__(self,name:str,info:str,file_name:str,ln:int,char_n:int) -> None:
        self.name = name
        self.info = info
        self.fn = file_name
        self.ln = ln
        self.chr = char_n
    def __repr__(self) -> str:
        return f'{self.name}: {self.info}\nat line: {self.ln}, {self.chr}\nin file: {self.fn}'

class IllegalCharError(Error):
    def __init__(self, info: str, file_name: str, ln: int, char_n: int) -> None:
        super().__init__("IllegalCharError", info, file_name, ln, char_n)

class SyntaxError(Error):
    def __init__(self, info: str, file_name: str, ln: int, char_n: int) -> None:
        super().__init__("SyntaxError", info, file_name, ln, char_n)

#########
# TOKEN #
#########

class Token:
    def __init__(self,name,data=None) -> None:
        self.name = name
        self.data = data
    def __repr__(self) -> str:
        if self.data: return f'[{self.name}: {self.data}]'
        return f'[{self.name}]'

# TYPES:
# PLUSEQ
# PLUS
# MINEQ
# MINUS
# MULEQ
# MULT
# DIVEQ
# DIV
# LPAREN
# RPAREN
# IDENT
# INT
# FLOAT

############
# KEYWORDS #
############

KEYWORDS = ["func","if","elif","else","for","while"]

#########
# LEXER #
#########

class Lexer:
    def __init__(self,text,fn,ln) -> None:
        self.text = text
        self.pos = -1
        self.cur_char = None
        self.fn = fn
        self.ln = ln
        self.advance()
    def advance(self):
        self.pos += 1
        self.cur_char = self.text[self.pos] if self.pos < len(self.text) else None
    def tokenize(self):
        tokens = []

        while self.cur_char != None:
            if self.cur_char in " \t":
                self.advance()
            elif self.cur_char == "+":
                self.advance()
                if self.cur_char == "=":
                    tokens.append(Token("PLUSEQ"))
                    self.advance()
                else: tokens.append(Token("PLUS"))
            elif self.cur_char == "-":
                self.advance()
                if self.cur_char == "=":
                    tokens.append(Token("MINEQ"))
                    self.advance()
                else: tokens.append(Token("MINUS"))
            elif self.cur_char == "*":
                self.advance()
                if self.cur_char == "=":
                    tokens.append(Token("MULEQ"))
                    self.advance()
                else: tokens.append(Token("MULT"))
            elif self.cur_char == "/":
                self.advance()
                if self.cur_char == "=":
                    tokens.append(Token("DIVEQ"))
                    self.advance()
                else: tokens.append(Token("DIV"))
            elif self.cur_char == "(":
                tokens.append(Token("LPAREN"))
                self.advance()
            elif self.cur_char == ")":
                tokens.append(Token("RPAREN"))
                self.advance()
            elif self.cur_char in CHARS:
                name = ""
                while self.cur_char != None and self.cur_char in CHARS:
                    name += self.cur_char
                    self.advance()
                if name in KEYWORDS:
                    tokens.append(Token("KEYWORD",name))
                else:
                    tokens.append(Token("IDENT",name))
            elif self.cur_char in DIGITS:
                dots = 0
                n_str = ""
                while self.cur_char != None and self.cur_char in DIGITS + ".":
                    if self.cur_char == ".":
                        if dots == 1:break
                        dots += 1
                    n_str += self.cur_char
                    self.advance()
                if dots == 0:
                    tokens.append(Token("INT",int(n_str)))
                else:
                    tokens.append(Token("FLOAT",float(n_str)))
            else:
                return [],IllegalCharError(f"'{self.cur_char}'",self.fn,self.ln,self.pos+1)
        return tokens,None

#########
# NODES #
#########

class NumberNode:
    def __init__(self,token) -> None:
        self.token = token
    def __repr__(self) -> str:
        return f'{self.token}'

class BinOpNode:
    def __init__(self,left_node,op,right_node) -> None:
        self.l_node = left_node
        self.op = op
        self.r_node = right_node
    def __repr__(self) -> str:
        return f'({self.l_node}, {self.op}, {self.r_node})'

class UnaryOpNode:
    def __init__(self,op_tok,node) -> None:
        self.op_tok = op_tok
        self.node = node
    def __repr__(self) -> str:
        return f'({self.op_tok}, {self.node})'

################
# PARSE RESULT #
################

class ParseResult:
    def __init__(self) -> None:
        self.error = None
        self.node = None
    def register(self,res):
        if isinstance(res,ParseResult):
            if res.error: self.error = res.error
            return res.node

        return res
    def success(self,node):
        self.node = node
        return self
    def failure(self,error):
        self.error = error
        return self

##########
# PARSER #
##########

class Parser:
    def __init__(self,tokens,fn,ln) -> None:
        self.tokens = tokens
        self.t_idx = -1
        self.fn=fn
        self.ln=ln
        self.advance()
    def advance(self):
        self.t_idx += 1
        if self.t_idx < len(self.tokens):
            self.cur_tok = self.tokens[self.t_idx]
        return self.cur_tok
    def parse(self):
        res = self.expr()
        return res
    def factor(self):
        res = ParseResult()
        tok = self.cur_tok

        if tok.name in ("PLUS","MINUS"):
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok,factor))

        elif tok.name in ("INT","FLOAT"):
            res.register(self.advance())
            return res.success(NumberNode(tok))

        elif tok.name == "LPAREN":
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error: return res
            if self.cur_tok.name == "RPAREN":
                res.register(self.advance())
                return res.success(expr)
            else: return res.failure(SyntaxError("Expected ')'",self.fn,self.ln,0))

        return res.failure(SyntaxError("Expected int or float",self.fn,self.ln,0))
    def term(self):
        return self.bin_op(self.factor,("MULT","DIV"))
    def expr(self):
        return self.bin_op(self.term,("PLUS","MINUS"))
    def bin_op(self,func,ops):
        res = ParseResult()
        left = res.register(func())
        if res.error: return res

        while self.cur_tok.name in ops:
            op_tok = self.cur_tok
            res.register(self.advance())
            right = res.register(func())
            if res.error: return res
            left = BinOpNode(left,op_tok,right)
        return res.success(left)
############
# COMPILER #
############

class Compiler:
    def __init__(self) -> None:
        pass

########
# MAIN #
########

def main(fn,text,ln):
    lex = Lexer(text,fn,ln)
    tokens,error = lex.tokenize()
    if error: return None,error

    par = Parser(tokens,fn,ln)
    ast = par.parse()

    return ast.node,ast.error
if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "-c":
        with open(sys.argv[2]) as f:
            pass
