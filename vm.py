from enum import IntEnum
from chunk import *
from compiler import *
from value import *

class InterpretResult(IntEnum):
	"""Possible results of interpreting chunk of bytecode"""
	INTERPRET_OK = 1
	INTERPRET_COMPILE_ERROR = 2
	INTERPRET_RUNTIME_ERROR = 3

class VM:
	"""A virtual machine for executing chunks of bytecode"""
	def __init__(self):
		self.initVm()

	def initVm(self):
		"""Setup empty virtual machine"""
		self.chunk = Chunk()
		self.ip = 0
		self.resetStack()
		self.debugTraceExecution = 0

	def resetStack(self):
		self.stack = []

	def runtimeError(self, message):
		print(message, file=sys.stderr)
		instruction = self.ip - 1
		line = self.chunk.lines[instruction]
		print("[line {0}] in script".format(line), file=sys.stderr)
		self.resetStack()

	def freeVm(self):
		"""Free memory used by virtual machine"""
		return

	def interpret(self, source):
		"""Interpret lox source code"""
		chunk = Chunk()
		c = Compiler()
		if c.compile(source, chunk) == False:
			return InterpretResult.INTERPRET_COMPILE_ERROR

		self.chunk = chunk
		self.ip = 0
		result = self.run()
		self.chunk.freeChunk()

		return result

	def checkBinaryOperands(self):
		return self.peek(0).IS_NUMBER() and self.peek(1).IS_NUMBER()

	def run(self):
		while True:
			if self.debugTraceExecution != 0:
					print('        ', end='')
					i = 0
					while i < len(self.stack):
						print('[ ', end='')
						self.chunk.printValue(self.stack[i])
						print(' ]', end='')
						i += 1
					print('')
					self.chunk.disassembleInstruction(self.ip)
			instruction = self.readByte()
			if instruction == OpCode.OP_CONSTANT:
				constant = self.readConstant()
				self.push(constant)

			if instruction == OpCode.OP_NIL:
				self.push(Value.NIL_VAL())

			if instruction == OpCode.OP_TRUE:
				self.push(Value.BOOL_VAL(True))

			if instruction == OpCode.OP_FALSE:
				self.push(Value.BOOL_VAL(False))

			if instruction == OpCode.OP_EQUAL:
				b = self.pop()
				a = self.pop()
				eq = Value.valuesEqual(a, b)
				self.push(Value.BOOL_VAL(eq))

			if instruction == OpCode.OP_GREATER:
				if not self.checkBinaryOperands():
					self.runtimeError("Operands must be numbers.")
					return InterpretResult.INTERPRET_RUNTIME_ERROR
				b = self.pop().AS_NUMBER()
				a = self.pop().AS_NUMBER()
				self.push(Value.BOOL_VAL(a > b))

			if instruction == OpCode.OP_LESS:
				if not self.checkBinaryOperands():
					self.runtimeError("Operands must be numbers.")
					return InterpretResult.INTERPRET_RUNTIME_ERROR
				b = self.pop().AS_NUMBER()
				a = self.pop().AS_NUMBER()
				self.push(Value.BOOL_VAL(a < b))


			if instruction == OpCode.OP_ADD:
				if not self.checkBinaryOperands():
					self.runtimeError("Operands must be numbers.")
					return InterpretResult.INTERPRET_RUNTIME_ERROR
				b = self.pop().AS_NUMBER()
				a = self.pop().AS_NUMBER()
				self.push(Value.NUMBER_VAL(a + b))

			if instruction == OpCode.OP_SUBTRACT:
				if not self.checkBinaryOperands():
					self.runtimeError("Operands must be numbers.")
					return InterpretResult.INTERPRET_RUNTIME_ERROR
				b = self.pop().AS_NUMBER()
				a = self.pop().AS_NUMBER()
				self.push(Value.NUMBER_VAL(a - b))

			if instruction == OpCode.OP_MULTIPLY:
				if not self.checkBinaryOperands():
					self.runtimeError("Operands must be numbers.")
					return InterpretResult.INTERPRET_RUNTIME_ERROR
				b = self.pop().AS_NUMBER()
				a = self.pop().AS_NUMBER()
				self.push(Value.NUMBER_VAL(a * b))

			if instruction == OpCode.OP_DIVIDE:
				if not self.checkBinaryOperands():
					self.runtimeError("Operands must be numbers.")
					return InterpretResult.INTERPRET_RUNTIME_ERROR
				b = self.pop().AS_NUMBER()
				a = self.pop().AS_NUMBER()
				self.push(Value.NUMBER_VAL(a / b))

			if instruction == OpCode.OP_NOT:
				n = self.pop()
				self.push(Value.BOOL_VAL(self.isFalsey(n)))

			if instruction == OpCode.OP_NEGATE:
				if not self.peek(0).IS_NUMBER():
					self.runtimeError("Operand must be a number.")
					return InterpretResult.INTERPRET_RUNTIME_ERROR
				n = self.pop().AS_NUMBER()
				self.push(Value.NUMBER_VAL(-n))
			if instruction == OpCode.OP_RETURN:
				self.chunk.printValue(self.pop())
				return

	def readByte(self):
		b = self.chunk.code[self.ip]
		self.ip += 1
		return b

	def readConstant(self):
		n = self.readByte()
		return self.chunk.constants[n]

	def push(self, value):
		self.stack.append(value)

	def pop(self):
		return self.stack.pop()

	def peek(self, distance):
		return self.stack[-1:][0]

	def isFalsey(self, value):
		if value.IS_NIL():
			return True
		if value.IS_BOOL():
			return value.AS_BOOL() == False
		return False
