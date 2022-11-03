DIGITS = "1234567890"
CHARS = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"


class Token:
	def __init__(self,type,value=None) -> None:
		self.type = type
		self.value = value
	def __repr__(self) -> str:
		if self.value: return f'[{self.type}: {self.value}]'
		return f'[{self.type}]'

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
			elif self.cur_char == "=":
				tokens.append(Token("EQUALS"))
				self.advance()
			elif self.cur_char == "+":
				self.advance()
				if self.cur_char == "=":
					tokens.append(Token("PLUSEQ"))
					self.advance()
				else:
					tokens.append(Token("PLUS"))
			elif self.cur_char == "-":
				self.advance()
				if self.cur_char == "=":
					tokens.append(Token("MINEQ"))
					self.advance()
				else:
					tokens.append(Token("MINUS"))
			elif self.cur_char == "*":
				self.advance()
				if self.cur_char == "=":
					tokens.append(Token("MULEQ"))
					self.advance()
				else:
					tokens.append(Token("MULT"))
			elif self.cur_char == "/":
				self.advance()
				if self.cur_char == "=":
					tokens.append(Token("DIVEQ"))
					self.advance()
				else:
					tokens.append(Token("DIV"))
			elif self.cur_char == "(":
				tokens.append(Token("LPAREN"))
				self.advance()
			elif self.cur_char == ")":
				tokens.append(Token("RPAREN"))
				self.advance()
			elif self.cur_char == "{":
				tokens.append(Token("LBRACE"))
				self.advance()
			elif self.cur_char == "}":
				tokens.append(Token("RBRACE"))
				self.advance()
			elif self.cur_char == "[":
				tokens.append(Token("LBRACKET"))
				self.advance()
			elif self.cur_char == "]":
				tokens.append(Token("RBRACKET"))
				self.advance()
			elif self.cur_char == ",":
				tokens.append(Token("COMMA"))
				self.advance()
			elif self.cur_char == ".":
				tokens.append(Token("DOT"))
				self.advance()
			elif self.cur_char == ":":
				tokens.append(Token("COLON"))
				self.advance()
			elif self.cur_char == ";":
				tokens.append(Token("SEMICOLON"))
				self.advance()
			elif self.cur_char == '"':
				tokens.append(self.make_string('"'))
			elif self.cur_char == "'":
				tokens.append(self.make_string("'"))
			elif self.cur_char in DIGITS:
				tokens.append(self.make_number())
			elif self.cur_char in CHARS:
				word = ""
				while self.cur_char != None and self.cur_char in CHARS + DIGITS:
					word += self.cur_char
					self.advance()
				if word == "let":
					tokens.append(Token("LET"))
				elif word == "if":
					tokens.append(Token("IF"))
				elif word == "else":
					tokens.append(Token("ELSE"))
				elif word == "while":
					tokens.append(Token("WHILE"))
				elif word == "for":
					tokens.append(Token("FOR"))
				elif word == "in":
					tokens.append(Token("IN"))
				elif word == "def":
					tokens.append(Token("MAKEFUNC"))
				elif word == "return":
					tokens.append(Token("RETURN"))
				elif word == "true":
					tokens.append(Token("TRUE"))
				elif word == "false":
					tokens.append(Token("FALSE"))
				elif word == "null":
					tokens.append(Token("NULL"))
				elif word == "and":
					tokens.append(Token("AND"))
				elif word == "or":
					tokens.append(Token("OR"))
				elif word == "not":
					tokens.append(Token("NOT"))
				else:
					tokens.append(Token("IDENTIFIER",word))
		return tokens
	def make_string(self,opener):
		string = ""
		self.advance()
		while self.cur_char != opener and self.cur_char != None:
			string += self.cur_char
			self.advance()
		if self.cur_char == None:
			raise Exception("Unexpected EOF")
		self.advance()
		return Token("STRING",string)
	def make_number(self):
		num = ""
		while self.cur_char != None and self.cur_char in DIGITS:
			num += self.cur_char
			self.advance()
		if self.cur_char == ".":
			num += self.cur_char
			self.advance()
			while self.cur_char != None and self.cur_char in DIGITS:
				num += self.cur_char
				self.advance()
			return Token("FLOAT",float(num))
		return Token("INT",int(num))

class node:
    def __init__(self,token):
        self.token = token
        self.children = []
    def __repr__(self):
        return f"{self.token} {self.children}"
    def __str__(self):
        return f"{self.token} {self.children}"

class Parser:
    def __init__(self,tokens):
        self.tokens = tokens
        self.cur_token = self.tokens.pop(0)
        self.cur_index = 0
    def advance(self):
        self.cur_index += 1
        if self.cur_index < len(self.tokens):
            self.cur_token = self.tokens[self.cur_index]
        else:
            self.cur_token = None
    def parse(self):
        return self.expr()
    def expr(self):
        node = self.term()
        while self.cur_token != None and self.cur_token.type in ["PLUS","MINUS"]:
            token = self.cur_token
            if token.type == "PLUS":
                self.advance()
                node = node("PLUS",[node,self.term()])
            elif token.type == "MINUS":
                self.advance()
                node = node("MINUS",[node,self.term()])
        return node
    def term(self):
        node = self.factor()
        while self.cur_token != None and self.cur_token.type in ["MUL","DIV"]:
            token = self.cur_token
            if token.type == "MUL":
                self.advance()
                node = node("MUL",[node,self.factor()])
            elif token.type == "DIV":
                self.advance()
                node = node("DIV",[node,self.factor()])
        return node
    def factor(self):
        token = self.cur_token
        if token.type == "LPAREN":
            self.advance()
            node = self.expr()
            if self.cur_token.type == "RPAREN":
                self.advance()
                return node
        elif token.type == "INT":
            self.advance()
            return node("INT",token.value)
        elif token.type == "FLOAT":
            self.advance()
            return node("FLOAT",token.value)
        elif token.type == "IDENTIFIER":
            self.advance()
            return node("IDENTIFIER",token.value)