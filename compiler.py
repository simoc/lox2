from scanner import *
from token import *
from chunk import *
from value import *
from object import *
import sys

DEBUG_PRINT_CODE = 1

class Parser:
	def __init__(self):
		self.current = Token()
		self.previous = Token()
		self.hadError = False
		self.panicMode = False

class Precedence(IntEnum):
	"""Precedence of each operator"""
	PREC_NONE = 0
	PREC_ASSIGNMENT = 1 # =
	PREC_OR = 2 # or
	PREC_AND = 3 # and
	PREC_EQUALITY = 4 # == !=
	PREC_COMPARISON = 5 # < > <= >=
	PREC_TERM = 6 # + -
	PREC_FACTOR = 7 # * /
	PREC_UNARY = 8 # ! -
	PREC_CALL = 9 # . ()
	PREC_PRIMARY = 10

class ParseRule:
	def __init__(self):
		self.prefix = ParseFn()
		self.infix = ParseFn()
		self.precedence = Predence()

	def __init__(self, rulePrefix, ruleInfix, rulePrecedence):
		self.prefix = rulePrefix
		self.infix = ruleInfix
		self.precedence = rulePrecedence

class Compiler:
	"""Compiles source code"""

	def __init__(self):
		self.start = ""
		self.currentIndex = 0
		self.line = 1
		self.parser = Parser()
		self.scanner = Scanner()
		self.compilingChunk = Chunk()

	def errorAt3(self, token, message):
		if self.parser.panicMode:
			return
		self.parser.panicMode = True
		print("[line {0}] Error".format(token.line), end='', file=sys.stderr)
		if token.type == TokenType.TOKEN_EOF:
			print(" at end", end='', file=sys.stderr)
		elif token.type == TokenType.TOKEN_ERROR:
			# Nothing
			pass
		else:
			print(" at '{0}'".format(token.start), end='', file=sys.stderr)

		print(": {0}".format(message), file=sys.stderr)
		self.parser.hadError = True

	def errorAt(self, message):
		self.errorAt3(self.parser.current, message)

	def error(self, message):
		self.errorAt3(self.parser.previous, message)

	def errorAtCurrent(self, message):
		self.errorAt3(self.parser.current, message)

	def advance(self):
		self.parser.previous = self.parser.current

		while True:
			self.parser.current = self.scanner.scanToken()
			if self.parser.current.type != TokenType.TOKEN_ERROR:
				break

			self.errorAt(self.parser.current.start)

	def consume(self, type, message):
		if self.parser.current.type == type:
			self.advance()
			return
		self.errorAtCurrent(message)

	def check(self, type):
		return self.parser.current.type == type

	def match(self, type):
		if not self.check(type):
			return False
		self.advance()
		return True

	def currentChunk(self):
		return self.compilingChunk

	def emitByte(self, byte):
		self.currentChunk().writeChunk(byte, self.parser.previous.line)

	def emitBytes(self, byte1, byte2):
		self.emitByte(byte1)
		self.emitByte(byte2)

	def emitReturn(self):
		self.emitByte(OpCode.OP_RETURN)

	def makeConstant(self, value):
		constant = self.currentChunk().addConstant(value)
		if (constant > 255):
			self.error("Too many constants in one chunk.")
			return 0
		return constant

	def emitConstant(self, value):
		self.emitBytes(OpCode.OP_CONSTANT, self.makeConstant(value))

	def endCompiler(self):
		if DEBUG_PRINT_CODE == 1:
			if not self.parser.hadError:
				self.currentChunk().disassembleChunk("code")
		self.emitReturn()

	def binary(self):
		operatorType = self.parser.previous.type
		rule = self.getRule(operatorType)
		self.parsePrecedence(rule.precedence + 1)

		if operatorType == TokenType.TOKEN_BANG_EQUAL:
			self.emitBytes(OpCode.OP_EQUAL, OpCode.OP_NOT)
		elif operatorType == TokenType.TOKEN_EQUAL_EQUAL:
			self.emitByte(OpCode.OP_EQUAL)
		elif operatorType == TokenType.TOKEN_GREATER:
			self.emitByte(OpCode.OP_GREATER)
		elif operatorType == TokenType.TOKEN_GREATER_EQUAL:
			self.emitBytes(OpCode.OP_LESS, OpCode.OP_NOT)
		elif operatorType == TokenType.TOKEN_LESS:
			self.emitByte(OpCode.OP_LESS)
		elif operatorType == TokenType.TOKEN_LESS_EQUAL:
			self.emitBytes(OpCode.OP_GREATER, OpCode.OP_NOT)
		elif operatorType == TokenType.TOKEN_PLUS:
			self.emitByte(OpCode.OP_ADD)
		elif operatorType == TokenType.TOKEN_MINUS:
			self.emitByte(OpCode.OP_SUBTRACT)
		elif operatorType == TokenType.TOKEN_STAR:
			self.emitByte(OpCode.OP_MULTIPLY)
		elif operatorType == TokenType.TOKEN_SLASH:
			self.emitByte(OpCode.OP_DIVIDE)
		else:
			# Unreachable
			return

	def literal(self):
		operatorType = self.parser.previous.type
		if operatorType == TokenType.TOKEN_FALSE:
			self.emitByte(OpCode.OP_FALSE)
		if operatorType == TokenType.TOKEN_NIL:
			self.emitByte(OpCode.OP_NIL)
		if operatorType == TokenType.TOKEN_TRUE:
			self.emitByte(OpCode.OP_TRUE)

	def grouping(self):
		self.expression()
		self.consume(TokenType.TOKEN_RIGHT_PAREN, "Expect ')' after expression.")

	def number(self):
		value = float(self.parser.previous.start)
		self.emitConstant(Value.NUMBER_VAL(value))

	def string(self):
		# Take string inside quotes
		s = self.parser.previous.start[1 : -1]
		obj = ObjString(s)
		self.emitConstant(Value.OBJ_VAL(obj))

	def unary(self):
		operatorType = self.parser.previous.type

		# Compile the operand.
		self.parsePrecedence(Precedence.PREC_UNARY)

		# Emit the operator instruction.
		if operatorType == TokenType.TOKEN_BANG:
			self.emitByte(OpCode.OP_NOT)
		if operatorType == TokenType.TOKEN_MINUS:
			self.emitByte(OpCode.OP_NEGATE)

		# Unreachable
		return

	def getRule(self, type):
		rules = {
			TokenType.TOKEN_LEFT_PAREN:     ParseRule(self.grouping, None, Precedence.PREC_NONE),
			TokenType.TOKEN_RIGHT_PAREN:    ParseRule(None, None, Precedence.PREC_NONE),
			TokenType.TOKEN_LEFT_BRACE:     ParseRule(None, None, Precedence.PREC_NONE),
			TokenType.TOKEN_RIGHT_BRACE:    ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_COMMA:          ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_DOT:            ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_MINUS:          ParseRule(self.unary, self.binary, Precedence.PREC_TERM),
			TokenType.TOKEN_PLUS:           ParseRule(None,     self.binary, Precedence.PREC_TERM),
			TokenType.TOKEN_SEMICOLON:      ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_SLASH:          ParseRule(None,     self.binary, Precedence.PREC_FACTOR),
			TokenType.TOKEN_STAR:           ParseRule(None,     self.binary, Precedence.PREC_FACTOR),
			TokenType.TOKEN_BANG:           ParseRule(self.unary,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_BANG_EQUAL:     ParseRule(None,     self.binary,   Precedence.PREC_EQUALITY),
			TokenType.TOKEN_EQUAL:          ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_EQUAL_EQUAL:    ParseRule(None,     self.binary,   Precedence.PREC_EQUALITY),
			TokenType.TOKEN_GREATER:        ParseRule(None,     self.binary,   Precedence.PREC_COMPARISON),
			TokenType.TOKEN_GREATER_EQUAL:  ParseRule(None,     self.binary,   Precedence.PREC_COMPARISON),
			TokenType.TOKEN_LESS:           ParseRule(None,     self.binary,   Precedence.PREC_COMPARISON),
			TokenType.TOKEN_LESS_EQUAL:     ParseRule(None,     self.binary,   Precedence.PREC_COMPARISON),
			TokenType.TOKEN_IDENTIFIER:     ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_STRING:         ParseRule(self.string,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_NUMBER:         ParseRule(self.number,   None,   Precedence.PREC_NONE),
			TokenType.TOKEN_AND:            ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_CLASS:          ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_ELSE:           ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_FALSE:          ParseRule(self.literal,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_FOR:            ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_FUN:            ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_IF:             ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_NIL:            ParseRule(self.literal,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_OR:             ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_PRINT:          ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_RETURN:         ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_SUPER:          ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_THIS:           ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_TRUE:           ParseRule(self.literal,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_VAR:            ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_WHILE:          ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_ERROR:          ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_EOF:            ParseRule(None,     None,   Precedence.PREC_NONE)
			}
		return rules[type]

	def parsePrecedence(self, precedence):
		self.advance()
		rule = self.getRule(self.parser.previous.type)
		if (rule.prefix == None):
			self.error("Expect expression.")
			return
		rule.prefix()

		while precedence <= self.getRule(self.parser.current.type).precedence:
			self.advance()
			rule = self.getRule(self.parser.previous.type)
			rule.infix()

	def expression(self):
		self.parsePrecedence(Precedence.PREC_ASSIGNMENT)

	def printStatement(self):
		self.expression()
		self.consume(TokenType.TOKEN_SEMICOLON, "Expect ';' after value.")
		self.emitByte(OpCode.OP_PRINT)

	def declaration(self):
		self.statement()

	def statement(self):
		if self.match(TokenType.TOKEN_PRINT):
			self.printStatement()

	def compile(self, source, chunk):
		self.scanner = Scanner()
		self.scanner.initScanner(source)
		self.compilingChunk = chunk

		self.parser.hadError = False
		self.parser.panicMode = False

		self.advance()

		while not self.match(TokenType.TOKEN_EOF):
			self.declaration()

		self.endCompiler()
		return not self.parser.hadError


