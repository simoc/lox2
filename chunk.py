from enum import IntEnum
from valuearray import *
from value import *

class OpCode(IntEnum):
	"""Instruction opcodes"""
	OP_CONSTANT = 1
	OP_NIL = 2
	OP_TRUE = 3
	OP_FALSE = 4
	OP_POP = 5
	OP_GET_LOCAL = 6
	OP_SET_LOCAL = 7
	OP_GET_GLOBAL = 8
	OP_DEFINE_GLOBAL = 9
	OP_SET_GLOBAL = 10
	OP_GET_UPVALUE = 11
	OP_SET_UPVALUE = 12
	OP_GET_PROPERTY = 13
	OP_SET_PROPERTY = 14
	OP_EQUAL = 15
	OP_GREATER = 16
	OP_LESS = 17
	OP_ADD = 18
	OP_SUBTRACT  = 19
	OP_MULTIPLY = 20
	OP_DIVIDE = 21
	OP_NOT = 22
	OP_NEGATE = 23
	OP_PRINT = 24
	OP_JUMP = 25
	OP_JUMP_IF_FALSE = 26
	OP_LOOP = 27
	OP_CALL = 28
	OP_INVOKE = 29
	OP_CLOSURE = 30
	OP_CLOSE_UPVALUE = 31
	OP_RETURN = 32
	OP_CLASS = 33
	OP_METHOD = 34


class Chunk:
	"""A chunk of bytecode that was compiled and is executed by VM"""

	def __init__(self):
		self.code = []
		self.lines = []
		self.constants = ValueArray()

	def writeChunk(self, b, line):
		"""Add a single byte to chunk"""
		self.code.append(b)
		self.lines.append(line)

	def freeChunk(self):
		"""Throw away memory used by chunk"""
		self.code.clear()
		self.lines.clear()
		self.constants.clear()

	def addConstant(self, value):
		"""Add a constant value to the chunk"""
		self.constants.writeValueArray(value)
		return self.constants.len() - 1
		
	def disassembleChunk(self, name):
		"""Print human readable representation of chunk"""
		print("===", name, "===")
		offset = 0
		while offset < len(self.code):
			offset = self.disassembleInstruction(offset)

	def disassembleInstruction(self, offset):
		print('{0:04d} '.format(offset), end='')
		if offset > 0 and self.lines[offset] == self.lines[offset - 1]:
			print('   | ', end='')
		else:
			print('{0:4d} '.format(self.lines[offset]), end='')
		op = self.code[offset]
		if op == OpCode.OP_CONSTANT:
			return self.constantInstruction("OP_CONSTANT", offset)

		if op == OpCode.OP_NIL:
			return self.simpleInstruction("OP_NIL", offset)

		if op == OpCode.OP_TRUE:
			return self.simpleInstruction("OP_TRUE", offset)

		if op == OpCode.OP_FALSE:
			return self.simpleInstruction("OP_FALSE", offset)

		if op == OpCode.OP_POP:
			return self.simpleInstruction("OP_POP", offset)

		if op == OpCode.OP_GET_LOCAL:
			return self.byteInstruction("OP_GET_LOCAL", offset)

		if op == OpCode.OP_SET_LOCAL:
			return self.byteInstruction("OP_SET_LOCAL", offset)

		if op == OpCode.OP_GET_GLOBAL:
			return self.constantInstruction("OP_GET_GLOBAL", offset)

		if op == OpCode.OP_DEFINE_GLOBAL:
			return self.constantInstruction("OP_DEFINE_GLOBAL", offset)

		if op == OpCode.OP_SET_GLOBAL:
			return self.constantInstruction("OP_SET_GLOBAL", offset)

		if op == OpCode.OP_GET_UPVALUE:
			return self.byteInstruction("OP_GET_UPVALUE", offset)

		if op == OpCode.OP_SET_UPVALUE:
			return self.byteInstruction("OP_SET_UPVALUE", offset)

		if op == OpCode.OP_GET_PROPERTY:
			return self.constantInstruction("OP_GET_PROPERTY", offset)

		if op == OpCode.OP_SET_PROPERTY:
			return self.constantInstruction("OP_SET_PROPERTY", offset)

		if op == OpCode.OP_EQUAL:
			return self.simpleInstruction("OP_EQUAL", offset)

		if op == OpCode.OP_GREATER:
			return self.simpleInstruction("OP_GREATER", offset)

		if op == OpCode.OP_LESS:
			return self.simpleInstruction("OP_LESS", offset)

		if op == OpCode.OP_ADD:
			return self.simpleInstruction("OP_ADD", offset)

		if op == OpCode.OP_SUBTRACT:
			return self.simpleInstruction("OP_SUBTRACT", offset)

		if op == OpCode.OP_MULTIPLY:
			return self.simpleInstruction("OP_MULTIPLY", offset)

		if op == OpCode.OP_DIVIDE:
			return self.simpleInstruction("OP_DIVIDE", offset)

		if op == OpCode.OP_NOT:
			return self.simpleInstruction("OP_NOT", offset)

		if op == OpCode.OP_NEGATE:
			return self.simpleInstruction("OP_NEGATE", offset)

		if op == OpCode.OP_PRINT:
			return self.simpleInstruction("OP_PRINT", offset)

		if op == OpCode.OP_JUMP:
			return self.jumpInstruction("OP_JUMP", 1, offset)

		if op == OpCode.OP_JUMP_IF_FALSE:
			return self.jumpInstruction("OP_JUMP_IF_FALSE", 1, offset)

		if op == OpCode.OP_LOOP:
			return self.jumpInstruction("OP_LOOP", -1, offset)

		if op == OpCode.OP_CALL:
			return self.byteInstruction("OP_CALL", offset)

		if op == OpCode.OP_INVOKE:
			return self.invokeInstruction("OP_INVOKE", offset)

		if op == OpCode.OP_CLOSURE:
			offset += 1
			constant = self.code[offset]
			offset += 1
			print("{0:<16} {1:4d} '".format("OP_CLOSURE", constant), end='')
			self.printValue(self.constants[constant])
			print("'")
			function = self.constants[constant].AS_OBJ()
			j = 0
			while j < len(function.upvalues):
				isLocal = self.code[offset]
				if isLocal == 1:
					type = "local"
				else:
					type = "upvalue"
				offset += 1
				index = self.code[offset]
				offset += 1
				print("{0:04d}    | {1:>27} {2:d} '".format(offset - 2, type, index))
				j += 1
			return offset

		if op == OpCode.OP_CLOSE_UPVALUE:
			return self.simpleInstruction("OP_CLOSE_UPVALUE", offset)

		if op == OpCode.OP_RETURN:
			return self.simpleInstruction("OP_RETURN", offset)

		if op == OpCode.OP_CLASS:
			return self.constantInstruction("OP_CLASS", offset)

		if op == OpCode.OP_METHOD:
			return self.constantInstruction("OP_METHOD", offset)

		print("Unknown opcode {0}".format(self.code[offset]))
		return offset + 1

	def constantInstruction(self, name, offset):
		constant = self.code[offset + 1]
		print("{0:<16} {1:4d} '".format(name, constant), end='')
		self.printValue(self.constants[constant])
		print("'")
		return offset + 2

	def invokeInstruction(self, name, offset):
		constant = self.code[offset + 1]
		argCount = self.code[offset + 2]
		print("{0:<16} ({1:d} args) {2:4d} '".format(name, argCount, constant), end='')
		self.printValue(self.constants[constant])
		print("'")
		return offset + 3

	def printValue(self, value):
		if value.IS_BOOL():
			if value.AS_BOOL() == True:
				print('true', end='')
			else:
				print('false', end='')

		if value.IS_NIL():
			print('nil', end='')

		if value.IS_NUMBER():
			print('{0:g}'.format(value.AS_NUMBER()), end='')

		if value.IS_OBJ():
			value.AS_OBJ().printObject()

	def simpleInstruction(self, name, offset):
		print(name)
		return offset + 1

	def byteInstruction(self, name, offset):
		slot = self.code[offset + 1]
		print('{0:<16} {1:4d}'.format(name, slot))
		return offset + 2

	def jumpInstruction(self, name, sign, offset):
		jump = self.code[offset + 1] << 8
		jump = jump | (self.code[offset + 2])
		print('{0:<16} {1:4d} -> {2}'.format(name, offset, offset + 3 + sign * jump))
		return offset + 3
