from scanner import *
from token import *

class Compiler:
	"""Compiles source code"""

	def initScanner(self, source):
		self.start = source;
		self.currentIndex = 0;
		self.line = 1;

	def ScanToken(self):
		return Token()

	def compile(self, source):
		s = Scanner()
		s.initScanner(source)
		line = -1
		while True:
			token = s.scanToken()
			if token.line != line:
				print('{0:04d} '.format(token.line), end='')
				line = token.line
			else:
				print('   | ', end='')
			print("{0:2d} '{1}'".format(int(token.type), token.start))

			if token.type == TokenType.TOKEN_EOF:
				break


