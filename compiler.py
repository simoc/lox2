from scanner import *
from token import *
from chunk import *
from value import *
from object import *
import sys

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

class Local:
	def __init__(self):
		self.name = Token()
		self.depth = 0
		self.isCaptured = False

class FunctionType(IntEnum):
	TYPE_FUNCTION = 0
	TYPE_INITIALIZER = 1
	TYPE_METHOD = 2
	TYPE_SCRIPT = 3

class CompilerState:
	def __init__(self, type):
		self.function = ObjFunction(None)
		self.type = type
		self.locals = []
		self.scopeDepth = 0

class Compiler:
	"""Compiles source code"""

	DEBUG_PRINT_CODE = 0

	def __init__(self, compiler, type):
		self.enclosing = compiler
		if compiler != None:
			self.currentClass = compiler.currentClass
		else:
			self.currentClass = None
		self.start = ""
		self.line = 1
		self.parser = Parser()
		self.current = CompilerState(type)
		if type != FunctionType.TYPE_SCRIPT:
			self.current.function = ObjFunction(ObjString(compiler.parser.previous.start))

		local = Local()
		local.name = Token()
		local.name.type = TokenType.TOKEN_STRING
		local.depth = 0
		local.isCaptured = False
		if type != FunctionType.TYPE_FUNCTION:
			local.name.start = "this"
		else:
			local.name.start = ""
		self.current.locals.append(local)

		self.scanner = Scanner()

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
		return self.current.function.chunk

	def emitByte(self, byte):
		self.currentChunk().writeChunk(byte, self.parser.previous.line)

	def emitBytes(self, byte1, byte2):
		self.emitByte(byte1)
		self.emitByte(byte2)

	def emitLoop(self, loopStart):
		self.emitByte(OpCode.OP_LOOP)
		offset = len(self.currentChunk().code) - loopStart + 2
		if offset > 65535:
			self.error("Loop body too large.")
		self.emitByte((offset >> 8) & 0xff)
		self.emitByte(offset & 0xff)

	def emitJump(self, instruction):
		self.emitByte(instruction)
		# Add placeholder position that will be replaced after jump location determined
		self.emitByte(0xff)
		self.emitByte(0xff)
		return len(self.currentChunk().code) - 2

	def emitReturn(self):
		if self.current.type == FunctionType.TYPE_INITIALIZER:
			self.emitBytes(OpCode.OP_GET_LOCAL, 0)
		else:
			self.emitByte(OpCode.OP_NIL)
		self.emitByte(OpCode.OP_RETURN)

	def makeConstant(self, value):
		constant = self.currentChunk().addConstant(value)
		if (constant > 255):
			self.error("Too many constants in one chunk.")
			return 0
		return constant

	def emitConstant(self, value):
		self.emitBytes(OpCode.OP_CONSTANT, self.makeConstant(value))

	def patchJump(self, offset):
		# -2 to adjust for the bytecode for the jump offset itself.
		jump = len(self.currentChunk().code) - offset - 2
		if jump > 65535:
			self.error("Too much code to jump over.")
		self.currentChunk().code[offset] = (jump >> 8) & 0xff
		self.currentChunk().code[offset + 1] = jump & 0xff

	def endCompiler(self):
		self.emitReturn()
		function = self.current.function
		if self.DEBUG_PRINT_CODE == 1:
			if not self.parser.hadError:
				if function.getName() != None:
					name = function.getName().AS_STRING()
				else:
					name = "<script>"
				self.currentChunk().disassembleChunk(name)
		return function

	def beginScope(self):
		self.current.scopeDepth += 1

	def endScope(self):
		self.current.scopeDepth -= 1

		while len(self.current.locals) > 0 and self.current.locals[-1].depth > self.current.scopeDepth:
			if self.current.locals[-1].isCaptured:
				self.emitByte(OpCode.OP_CLOSE_UPVALUE)
			else:
				self.emitByte(OpCode.OP_POP)
			self.current.locals.pop()

	def binary(self, canAssign):
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

	def call(self, canAssign):
		argCount = self.argumentList()
		self.emitBytes(OpCode.OP_CALL, argCount)

	def dot(self, canAssign):
		self.consume(TokenType.TOKEN_IDENTIFIER, "Expect property name after '.'.")
		name = self.identifierConstant(self.parser.previous)
		if canAssign and self.match(TokenType.TOKEN_EQUAL):
			self.expression()
			self.emitBytes(OpCode.OP_SET_PROPERTY, name)
		else:
			self.emitBytes(OpCode.OP_GET_PROPERTY, name)

	def literal(self, canAssign):
		operatorType = self.parser.previous.type
		if operatorType == TokenType.TOKEN_FALSE:
			self.emitByte(OpCode.OP_FALSE)
		if operatorType == TokenType.TOKEN_NIL:
			self.emitByte(OpCode.OP_NIL)
		if operatorType == TokenType.TOKEN_TRUE:
			self.emitByte(OpCode.OP_TRUE)

	def grouping(self, canAssign):
		self.expression()
		self.consume(TokenType.TOKEN_RIGHT_PAREN, "Expect ')' after expression.")

	def number(self, canAssign):
		value = float(self.parser.previous.start)
		self.emitConstant(Value.NUMBER_VAL(value))

	def or_(self, canAssign):
		elseJump = self.emitJump(OpCode.OP_JUMP_IF_FALSE)
		endJump = self.emitJump(OpCode.OP_JUMP)
		self.patchJump(elseJump)
		self.emitByte(OpCode.OP_POP)
		self.parsePrecedence(Precedence.PREC_OR)
		self.patchJump(endJump)

	def string(self, canAssign):
		# Take string inside quotes
		s = self.parser.previous.start[1 : -1]
		obj = ObjString(s)
		self.emitConstant(Value.OBJ_VAL(obj))

	def namedVariable(self, name, canAssign):
		arg = self.resolveLocal(name)
		if arg != -1:
			getOp = OpCode.OP_GET_LOCAL
			setOp = OpCode.OP_SET_LOCAL
		else:
			arg = self.resolveUpvalue(name)
			if arg != -1:
				getOp = OpCode.OP_GET_UPVALUE
				setOp = OpCode.OP_SET_UPVALUE
			else:
				arg = self.identifierConstant(name)
				getOp = OpCode.OP_GET_GLOBAL
				setOp = OpCode.OP_SET_GLOBAL

		if canAssign and self.match(TokenType.TOKEN_EQUAL):
			self.expression()
			self.emitBytes(setOp, arg)
		else:
			self.emitBytes(getOp, arg)

	def variable(self, canAssign):
		self.namedVariable(self.parser.previous, canAssign)

	def this_(self, canAssign):
		if self.currentClass == None:
			self.error("Can't use 'this' outside of a class.")
			return
		self.variable(False)

	def unary(self, canAssign):
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
			TokenType.TOKEN_LEFT_PAREN:     ParseRule(self.grouping, self.call, Precedence.PREC_CALL),
			TokenType.TOKEN_RIGHT_PAREN:    ParseRule(None, None, Precedence.PREC_NONE),
			TokenType.TOKEN_LEFT_BRACE:     ParseRule(None, None, Precedence.PREC_NONE),
			TokenType.TOKEN_RIGHT_BRACE:    ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_COMMA:          ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_DOT:            ParseRule(None,     self.dot, Precedence.PREC_CALL),
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
			TokenType.TOKEN_IDENTIFIER:     ParseRule(self.variable,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_STRING:         ParseRule(self.string,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_NUMBER:         ParseRule(self.number,   None,   Precedence.PREC_NONE),
			TokenType.TOKEN_AND:            ParseRule(None,     self.and_,   Precedence.PREC_AND),
			TokenType.TOKEN_CLASS:          ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_ELSE:           ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_FALSE:          ParseRule(self.literal,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_FOR:            ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_FUN:            ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_IF:             ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_NIL:            ParseRule(self.literal,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_OR:             ParseRule(None,     self.or_,   Precedence.PREC_OR),
			TokenType.TOKEN_PRINT:          ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_RETURN:         ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_SUPER:          ParseRule(None,     None,   Precedence.PREC_NONE),
			TokenType.TOKEN_THIS:           ParseRule(self.this_,     None,   Precedence.PREC_NONE),
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
		canAssign = precedence <= Precedence.PREC_ASSIGNMENT
		rule.prefix(canAssign)

		while precedence <= self.getRule(self.parser.current.type).precedence:
			self.advance()
			rule = self.getRule(self.parser.previous.type)
			rule.infix(canAssign)

		if canAssign and self.match(TokenType.TOKEN_EQUAL_EQUAL):
			self.error("Invalid assignment target.")

	def identifierConstant(self, name):
		obj = Value.OBJ_VAL(ObjString(name.start))
		return self.makeConstant(obj)

	def identifiersEqual(self, a, b):
		return a.start == b.start

	def resolveLocal(self, name):
		i = len(self.current.locals) - 1
		while i >= 0:
			local = self.current.locals[i]
			if self.identifiersEqual(name, local.name):
				if local.depth == -1:
					self.error("Can't read local variable in its own initializer")
				return i
			i = i - 1
		return -1

	def addUpvalue(self, index, isLocal):
		i = 0
		while i < len(self.current.function.upvalues):
			if self.current.function.upvalues[i].index == index and self.current.function.upvalues[i].isLocal == isLocal:
				return i
			i += 1

		if len(self.current.function.upvalues) == 256:
			self.error("Too many closure variables in function.")
			return 0

		u = Upvalue()
		u.isLocal = isLocal
		u.index = index
		self.current.function.upvalues.append(u)
		return len(self.current.function.upvalues) - 1

	def resolveUpvalue(self, name):
		if self.enclosing == None:
			return -1

		local = self.enclosing.resolveLocal(name)
		if local != -1:
			self.enclosing.current.locals[local].isCaptured = True
			return self.addUpvalue(local, True)

		upvalue = self.enclosing.resolveUpvalue(name)
		if upvalue != -1:
			return self.addUpvalue(upvalue, False)

		return -1

	def addLocal(self, name):
		if len(self.current.locals) == 256:
			self.error("Too many local variables in function.")
			return
		local = Local()
		local.name = name
		local.depth = -1
		local.isCaptured = False
		self.current.locals.append(local)

	def declareVariable(self):
		if self.current.scopeDepth == 0:
			return
		name = self.parser.previous
		i = len(self.current.locals) - 1
		while i >= 0:
			local = self.current.locals[i]
			if local.depth != -1 and local.depth < self.current.scopeDepth:
				break
			if self.identifiersEqual(name, local.name):
				self.error("Already a variable with this name in this scope.")
			i = i - 1
		self.addLocal(name)

	def parseVariable(self, errorMessage):
		self.consume(TokenType.TOKEN_IDENTIFIER, errorMessage)
		self.declareVariable()
		if self.current.scopeDepth > 0:
			return 0
		return self.identifierConstant(self.parser.previous)

	def markInitialized(self):
		if self.current.scopeDepth == 0:
			return
		self.current.locals[-1].depth = self.current.scopeDepth

	def defineVariable(self, globalVar):
		if self.current.scopeDepth > 0:
			self.markInitialized()
			return 0
		self.emitBytes(OpCode.OP_DEFINE_GLOBAL, globalVar)

	def argumentList(self):
		argCount = 0
		if not self.check(TokenType.TOKEN_RIGHT_PAREN):
			while True:
				self.expression()
				if argCount == 255:
					self.error("Can't have more than 255 arguments.")
				argCount += 1
				if not self.match(TokenType.TOKEN_COMMA):
					break
		self.consume(TokenType.TOKEN_RIGHT_PAREN, "Expect ')' after arguments.")
		return argCount

	def and_(self, canAssign):
		endJump = self.emitJump(OpCode.OP_JUMP_IF_FALSE)
		self.emitByte(OpCode.OP_POP)
		self.parsePrecedence(Precedence.PREC_AND)
		self.patchJump(endJump)

	def expression(self):
		self.parsePrecedence(Precedence.PREC_ASSIGNMENT)

	def block(self):
		while (not self.check(TokenType.TOKEN_RIGHT_BRACE) and
			not self.check(TokenType.TOKEN_EOF)):
			self.declaration()
		self.consume(TokenType.TOKEN_RIGHT_BRACE, "Expect '}' after block.")

	def function(self, type):
		compiler = Compiler(self, type)
		compiler.parser = self.parser
		compiler.scanner = self.scanner
		compiler.beginScope()

		compiler.consume(TokenType.TOKEN_LEFT_PAREN, "Expect '(' after function name.")

		if not compiler.check(TokenType.TOKEN_RIGHT_PAREN):
			while True:
				compiler.current.function.arity += 1
				if compiler.current.function.arity > 255:
					compiler.errorAtCurrent("Can't have more than 255 parameters.")
				constant = compiler.parseVariable("Expect parameter name.")
				compiler.defineVariable(constant)
				if not compiler.match(TokenType.TOKEN_COMMA):
					break

		compiler.consume(TokenType.TOKEN_RIGHT_PAREN, "Expect ')' after parameters.")
		compiler.consume(TokenType.TOKEN_LEFT_BRACE, "Expect '{' before function body.")
		compiler.block()
		function = compiler.endCompiler()
		value = Value.OBJ_VAL(function)
		self.emitBytes(OpCode.OP_CLOSURE, self.makeConstant(value))

		i = 0
		while i < len(function.upvalues):
			if function.upvalues[i].isLocal:
				b = 1
			else:
				b = 0
			self.emitByte(b)
			self.emitByte(function.upvalues[i].index)
			i += 1

	def method(self):
		self.consume(TokenType.TOKEN_IDENTIFIER, "Expect method name.")
		constant = self.identifierConstant(self.parser.previous)
		type = FunctionType.TYPE_METHOD
		if self.parser.previous.start == "init":
			type = FunctionType.TYPE_INITIALIZER
		self.function(type)
		self.emitBytes(OpCode.OP_METHOD, constant)

	def classDeclaration(self):
		self.consume(TokenType.TOKEN_IDENTIFIER, "Expect class name.")
		className = self.parser.previous
		nameConstant = self.identifierConstant(self.parser.previous)
		self.declareVariable()

		self.emitBytes(OpCode.OP_CLASS, nameConstant)
		self.defineVariable(nameConstant)
		enclosingCurrentClass = self.currentClass
		self.currentClass = self
		self.namedVariable(className, False)

		self.consume(TokenType.TOKEN_LEFT_BRACE, "Expect '{' before class body.")
		while (not self.check(TokenType.TOKEN_RIGHT_BRACE) and
			not self.check(TokenType.TOKEN_RIGHT_BRACE)):
			self.method()
		self.consume(TokenType.TOKEN_RIGHT_BRACE, "Expect '}' after class body.")
		self.emitByte(OpCode.OP_POP)
		self.currentClass = enclosingCurrentClass

	def funDeclaration(self):
		globalVar = self.parseVariable("Expect function name.")
		self.markInitialized()
		self.function(FunctionType.TYPE_FUNCTION)
		self.defineVariable(globalVar)

	def expressionStatement(self):
		self.expression()
		self.consume(TokenType.TOKEN_SEMICOLON, "Expect ';' after expression.")
		self.emitByte(OpCode.OP_POP)

	def forStatement(self):
		self.beginScope()
		self.consume(TokenType.TOKEN_LEFT_PAREN, "Expect '(' after 'for'.")
		if self.match(TokenType.TOKEN_SEMICOLON):
			# No initializer.
			pass
		elif self.match(TokenType.TOKEN_VAR):
			self.varDeclaration()
		else:
			self.expressionStatement()
		loopStart = len(self.currentChunk().code)
		exitJump = -1
		if not self.match(TokenType.TOKEN_SEMICOLON):
			self.expression()
			self.consume(TokenType.TOKEN_SEMICOLON, "Expect ';' after loop condition.")
			# Jump out of the loop if the condition is false.
			exitJump = self.emitJump(OpCode.OP_JUMP_IF_FALSE)
			self.emitByte(OpCode.OP_POP) # Condition.

		if not self.match(TokenType.TOKEN_RIGHT_PAREN):
			bodyJump = self.emitJump(OpCode.OP_JUMP)
			incrementStart = len(self.currentChunk().code)
			self.expression()
			self.emitByte(OpCode.OP_POP)
			self.consume(TokenType.TOKEN_RIGHT_PAREN, "Expect ')' after for clauses.")
			self.emitLoop(loopStart)
			loopStart = incrementStart
			self.patchJump(bodyJump)

		self.statement()
		self.emitLoop(loopStart)
		if exitJump != -1:
			self.patchJump(exitJump)
			self.emitByte(OpCode.OP_POP) # Condition.

		self.endScope()

	def ifStatement(self):
		self.consume(TokenType.TOKEN_LEFT_PAREN, "Expect '(' after 'if'.")
		self.expression()
		self.consume(TokenType.TOKEN_RIGHT_PAREN, "Expect ')' after condition.")
		thenJump = self.emitJump(OpCode.OP_JUMP_IF_FALSE)
		self.emitByte(OpCode.OP_POP)
		self.statement()

		elseJump = self.emitJump(OpCode.OP_JUMP)

		self.patchJump(thenJump)
		self.emitByte(OpCode.OP_POP)
		if (self.match(TokenType.TOKEN_ELSE)):
			self.statement()
		self.patchJump(elseJump)

	def varDeclaration(self):
		globalVar = self.parseVariable("Expect variable name.")

		if self.match(TokenType.TOKEN_EQUAL):
			self.expression()
		else:
			self.emitByte(OpCode.OP_NIL)
		self.consume(TokenType.TOKEN_SEMICOLON, "Expect ';' after variable declaration.")
		self.defineVariable(globalVar)

	def printStatement(self):
		self.expression()
		self.consume(TokenType.TOKEN_SEMICOLON, "Expect ';' after value.")
		self.emitByte(OpCode.OP_PRINT)

	def returnStatement(self):
		if self.current.type == FunctionType.TYPE_SCRIPT:
			self.error("Can't return from top-level code.")

		if self.match(TokenType.TOKEN_SEMICOLON):
			self.emitByte(OpCode.OP_RETURN)
		else:
			if self.current.type == FunctionType.TYPE_INITIALIZER:
				self.error("Can't return a value from an initializer.")

			self.expression()
			self.consume(TokenType.TOKEN_SEMICOLON, "Expect ';' after return value.")
			self.emitByte(OpCode.OP_RETURN)

	def whileStatement(self):
		loopStart = len(self.currentChunk().code)
		self.consume(TokenType.TOKEN_LEFT_PAREN, "Expect '(' after 'while'.")
		self.expression()
		self.consume(TokenType.TOKEN_RIGHT_PAREN, "Expect ')' after condition.")
		exitJump = self.emitJump(OpCode.OP_JUMP_IF_FALSE)
		self.emitByte(OpCode.OP_POP)
		self.statement()
		self.emitLoop(loopStart)
		self.patchJump(exitJump)
		self.emitByte(OpCode.OP_POP)

	def synchronize(self):
		self.parser.panicMode = False

		while self.parser.current.type != TokenType.TOKEN_EOF:
			if self.parser.previous.type == TokenType.TOKEN_SEMICOLON:
				return
			if (self.parser.current.type == TokenType.TOKEN_CLASS or
				self.parser.current.type == TokenType.TOKEN_FUN or
				self.parser.current.type == TokenType.TOKEN_VAR or
				self.parser.current.type == TokenType.TOKEN_FOR or
				self.parser.current.type == TokenType.TOKEN_IF or
				self.parser.current.type == TokenType.TOKEN_WHILE or
				self.parser.current.type == TokenType.TOKEN_PRINT or
				self.parser.current.type == TokenType.TOKEN_RETURN):
				return
			self.advance()

	def declaration(self):
		if self.match(TokenType.TOKEN_CLASS):
			self.classDeclaration()
		elif self.match(TokenType.TOKEN_FUN):
			self.funDeclaration()
		elif self.match(TokenType.TOKEN_VAR):
			self.varDeclaration()
		else:
			self.statement()

		if self.parser.panicMode:
			self.synchronize()

	def statement(self):
		if self.match(TokenType.TOKEN_PRINT):
			self.printStatement()
		elif self.match(TokenType.TOKEN_FOR):
			self.forStatement()
		elif self.match(TokenType.TOKEN_IF):
			self.ifStatement()
		elif self.match(TokenType.TOKEN_RETURN):
			self.returnStatement()
		elif self.match(TokenType.TOKEN_WHILE):
			self.whileStatement()
		elif self.match(TokenType.TOKEN_LEFT_BRACE):
			self.beginScope()
			self.block()
			self.endScope()
		else:
			self.expressionStatement()

	def compile(self, source):
		self.scanner = Scanner()
		self.scanner.initScanner(source)
		#self.current.function = ObjFunction(None)
		self.current.type = type

		self.parser.hadError = False
		self.parser.panicMode = False

		self.advance()

		while not self.match(TokenType.TOKEN_EOF):
			self.declaration()

		function = self.endCompiler()
		if self.parser.hadError:
			return None
		else:
			return function
