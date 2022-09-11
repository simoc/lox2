from token import *

class Scanner:
	def initScanner(self, source):
		self.start = source;
		self.currentIndex = 0;
		self.startIndex = 0;
		self.line = 1;

	def isAtEnd(self):
		flag = self.currentIndex >= len(self.start)
		return flag

	def makeToken(self, type):
		token = Token()
		token.type = type
		token.start = self.start[self.startIndex :  self.currentIndex]
		token.line = self.line
		return token

	def errorToken(self, message):
		token = Token()
		token.type = TokenType.TOKEN_ERROR
		token.start = message
		token.line = self.line
		return token

	def string(self):
		while self.peek() != '"' and not self.isAtEnd():
			if self.peek() == '\n':
				self.line += 1
			self.advance()
		if self.isAtEnd():
			return errorToken("Unterminated string.")

		# The closing quote.
		self.advance()
		return self.makeToken(TokenType.TOKEN_STRING)

	def advance(self):
		c = self.start[self.currentIndex]
		self.currentIndex += 1
		return c

	def match(self, expected):
		if self.isAtEnd():
			return False
		if self.start[self.currentIndex] != expected:
			return False
		self.currentIndex += 1
		return True

	def peek(self):
		return self.start[self.currentIndex]

	def peekNext(self):
		if self.isAtEnd():
			return '\0'
		return self.start[self.currentIndex + 1]

	def skipWhitespace(self):
		if self.isAtEnd():
			return

		while True:
			c = self.peek()
			if c == ' ' or c == '\r' or c == '\t':
				self.advance()
			if c == '\n':
				self.line += 1
				self.advance()
			if c == '/':
				if self.peekNext() == '/':
					# A comment goes until the end of the line.
					while self.peek() != '\n' and not self.isAtEnd():
						self.advance()
				else:
					return
			else:
				return

	def isAlpha(self, c):
		if c >= 'a' and c <= 'z':
			return True
		if c >= 'A' and c <= 'Z':
			return True
		if c == '_':
			return True
		return False

	def checkKeyword(self, start, length, rest, type):
		s = self.start[self.startIndex + start : self.currentIndex]
		if s == rest:
			return type
		return TokenType.TOKEN_IDENTIFIER

	def identifierType(self):
		c = self.start[self.startIndex]
		if c == 'a':
			return self.checkKeyword(1, 2, "nd", TokenType.TOKEN_AND)
		if c == 'c':
			return self.checkKeyword(1, 4, "lass", TokenType.TOKEN_CLASS)
		if c == 'e':
			return self.checkKeyword(1, 3, "lse", TokenType.TOKEN_ELSE)
		if c == 'f':
			c2 = self.start[self.startIndex + 1]
			if c2 == 'a':
				return self.checkKeyword(2, 3, "lse", TokenType.TOKEN_FALSE)
			if c2 == 'o':
				return self.checkKeyword(2, 1, "r", TokenType.TOKEN_FOR)
			if c2 == 'u':
				return self.checkKeyword(2, 1, "n", TokenType.TOKEN_FUN)
		if c == 'i':
			return self.checkKeyword(1, 1, "f", TokenType.TOKEN_IF)
		if c == 'n':
			return self.checkKeyword(1, 2, "il", TokenType.TOKEN_NIL)
		if c == 'o':
			return self.checkKeyword(1, 1, "r", TokenType.TOKEN_OR)
		if c == 'p':
			return self.checkKeyword(1, 4, "rint", TokenType.TOKEN_PRINT)
		if c == 'r':
			return self.checkKeyword(1, 5, "eturn", TokenType.TOKEN_RETURN)
		if c == 's':
			return self.checkKeyword(1, 4, "uper", TokenType.TOKEN_SUPER)
		if c == 't':
			c2 = self.start[self.startIndex + 1]
			if c2 == 'h':
				return self.checkKeyword(2, 2, "is", TokenType.TOKEN_THIS)
			if c2 == 'r':
				return self.checkKeyword(2, 2, "ue", TokenType.TOKEN_TRUE)
		if c == 'v':
			return self.checkKeyword(1, 3, "ar", TokenType.TOKEN_VAR)
		if c == 'w':
			return self.checkKeyword(1, 4, "hile", TokenType.TOKEN_WHILE)

		return TokenType.TOKEN_IDENTIFIER

	def identifier(self):
		while self.isAlpha(self.peek()) or self.isDigit(self.peek()):
			self.advance()
		return self.makeToken(self.identifierType())

	def isDigit(self, c):
		return c >= '0' and c <= '9'

	def number(self):
		while self.isDigit(self.peek()):
			self.advance()

		# Look for a fractional part.
		if self.peek() == '.' and self.isDigit(self.peekNext()):
			# Consume the ".".
			self.advance()

		while self.isDigit(self.peek()):
			self.advance()

		return self.makeToken(TokenType.TOKEN_NUMBER)

	def scanToken(self):
		self.skipWhitespace()
		self.startIndex = self.currentIndex
		if self.isAtEnd():
			return self.makeToken(TokenType.TOKEN_EOF)
		c = self.advance()
		if self.isAlpha(c):
			return self.identifier()
		if self.isDigit(c):
			return self.number()
		if c == '(':
			return self.makeToken(TokenType.TOKEN_LEFT_PAREN)
		if c == ')':
			return self.makeToken(TokenType.TOKEN_RIGHT_PAREN)
		if c == '{':
			return self.makeToken(TokenType.TOKEN_LEFT_BRACE)
		if c == '}':
			return self.makeToken(TokenType.TOKEN_RIGHT_BRACE)
		if c == ';':
			return self.makeToken(TokenType.TOKEN_SEMICOLON)
		if c == ',':
			return self.makeToken(TokenType.TOKEN_COMMA)
		if c == '.':
			return self.makeToken(TokenType.TOKEN_DOT)
		if c == '-':
			return self.makeToken(TokenType.TOKEN_MINUS)
		if c == '+':
			return self.makeToken(TokenType.TOKEN_PLUS)
		if c == '/':
			return self.makeToken(TokenType.TOKEN_SLASH)
		if c == '*':
			return self.makeToken(TokenType.TOKEN_STAR)
		if c == '!':
			if self.match('='):
				return self.makeToken(TokenType.TOKEN_BANG_EQUAL)
			else:
				return self.makeToken(TokenType.TOKEN_BANG)
		if c == '=':
			if self.match('='):
				return self.makeToken(TokenType.TOKEN_EQUAL_EQUAL)
			else:
				return self.makeToken(TokenType.TOKEN_EQUAL)
		if c == '<':
			if self.match('='):
				return self.makeToken(TokenType.TOKEN_LESS_EQUAL)
			else:
				return self.makeToken(TokenType.TOKEN_LESS)
		if c == '>':
			if self.match('='):
				return self.makeToken(TokenType.TOKEN_GREATER_EQUAL)
			else:
				return self.makeToken(TokenType.TOKEN_GREATER)
		if c == '"':
			return self.string()

		return self.errorToken("Unexpected character '{0}'.".format(c))
