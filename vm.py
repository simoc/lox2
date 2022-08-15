from enum import IntEnum
from chunk import *
from compiler import *

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

	def freeVm(self):
		"""Free memory used by virtual machine"""
		return

	def interpret(self, source):
		"""Interpret lox source code"""
		c = Compiler()
		c.compile(source)
		return InterpretResult.INTERPRET_OK

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
			if instruction == OpCode.OP_ADD:
				b = self.pop()
				a = self.pop()
				self.push(a + b)
			if instruction == OpCode.OP_SUBTRACT:
				b = self.pop()
				a = self.pop()
				self.push(a - b)
			if instruction == OpCode.OP_MULTIPLY:
				b = self.pop()
				a = self.pop()
				self.push(a * b)
			if instruction == OpCode.OP_DIVIDE:
				b = self.pop()
				a = self.pop()
				self.push(a / b)
			if instruction == OpCode.OP_NEGATE:
				n = self.pop()
				self.push(-n)
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
