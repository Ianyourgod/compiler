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
				tokens.append(Token("SET"))
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

class Interpreter:
	def __init__(self) -> None:
		self.vars = []
		self.funcs = {}
		self.lines = ["#AS\n"]
		self.addLine("define $COMPILERVAR = 0")
	def addLine(self, line):
		self.lines.append(line + "\n")
	def _createVar(self, name, value):
		self.vars.append(name)
		self.addLine(f"define ${name} = {value}")
	def _setVar(self,name,value):
		if self.vars.__contains__(value):
			self.addLine(f"change ${name} -> ${value}")
		else:
			self.addLine(f"change ${name} = {value}")
	def _addVar(self, name, value):
		if self.vars.__contains__(value):
			self.addLine(f"add ${name} , ${value} -> ${name}")
		else:
			self.addLine(f"change $COMPILERVAR = {value}")
			self.addLine(f"add ${name} , $COMPILERVAR -> ${name}")
	def _subVar(self, name, value):
		if self.vars.__contains__(value):
			self.addLine(f"sub ${name} , ${value} -> ${name}")
		else:
			self.addLine(f"change $COMPILERVAR = {value}")
			self.addLine(f"sub ${name} , $COMPILERVAR -> ${name}")
	def _multVar(self, name, value):
		if self.vars.__contains__(value):
			self.addLine(f"mult ${name} , ${value} -> ${name}")
		else:
			self.addLine(f"change $COMPILERVAR = {value}")
			self.addLine(f"mult ${name} , $COMPILERVAR -> ${name}")
	def _divVar(self, name, value):
		if self.vars.__contains__(value):
			self.addLine(f"div ${name} , ${value} -> ${name}")
		else:
			self.addLine(f"change $COMPILERVAR = {value}")
			self.addLine(f"div ${name} , $COMPILERVAR -> ${name}")
	def _andVar(self,name,value):
		if self.vars.__contains__(value):
			self.addLine(f"and ${name} , ${value} -> ${name}")
		else:
			self.addLine(f"change $COMPILERVAR = {value}")
			self.addLine(f"and ${name} , $COMPILERVAR -> ${name}")
	def _orVar(self,name,value):
		if self.vars.__contains__(value):
			self.addLine(f"or ${name} , ${value} -> ${name}")
		else:
			self.addLine(f"change $COMPILERVAR = {value}")
			self.addLine(f"or ${name} , $COMPILERVAR -> ${name}")
	def _notVar(self,name):
		self.addLine(f"not ${name} -> ${name}")
	def _setPix(self,idx,chr):
		self.addLine(f"change {idx+61294} = {chr}")
	def readLines(self,text):
		lines = []
		line = ""
		for i in text:
			if i == "\n":
				cont = False
				for i in line:
					if  not i in " \t":
						cont = True
				if cont:
					lines.append(line)
				line = ""
			else:
				line += i
		return lines

	def compile(self,text,file_name):
		lines = self.readLines(text)
		if len(lines) > 0:
			idx = 0
			while idx < len(lines):
				line = lines[idx]
				tokens = Lexer(line,file_name,idx+1).tokenize()
				print(tokens)
				idx += 1
		with open(file_name, "w") as f:
			for i in self.lines:
				f.write(i)
	def compAndRun(self, file_name):
		import subprocess
		self.compile(file_name)
		subprocess.run(["astro8", file_name])

inter = Interpreter()
inter._createVar("a", 3)
inter._createVar("b", 2)
inter._addVar("a", "b")
inter._setPix(1,"'h'")
print(inter.vars)
inter.compile("print 'hello world'","test.armstrong")