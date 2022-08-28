from enum import IntEnum
from valuearray import *
from value import *

class OpCode(IntEnum):
	"""Instruction opcodes"""
	OP_CONSTANT = 1
	OP_NIL = 2
	OP_TRUE = 3
	OP_FALSE = 4
	OP_EQUAL = 5
	OP_GREATER = 6
	OP_LESS = 7
	OP_ADD = 8
	OP_SUBTRACT  = 9
	OP_MULTIPLY = 10
	OP_DIVIDE = 11
	OP_NOT = 12
	OP_NEGATE = 13
	OP_RETURN = 14


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
		offset = 0;
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

		if op == OpCode.OP_RETURN:
				return self.simpleInstruction("OP_RETURN", offset)

		print("Unknown opcode {0}".format(self.code[offset]))
		return offset + 1

	def constantInstruction(self, name, offset):
		constant = self.code[offset + 1]
		print("{0:<16} {1:4d} '".format(name, constant), end='')
		self.printValue(self.constants[constant])
		print("'")
		return offset + 2

	def printValue(self, value):
		if value.type == ValueType.VAL_BOOL:
			if value.AS_BOOL() == True:
				print('true', end='')
			else:
				print('false', end='')

		if value.type == ValueType.VAL_NIL:
			print('nil', end='')

		if value.type == ValueType.VAL_NUMBER:
			print('{0:g}'.format(value.AS_NUMBER()), end='')

		if value.type == ValueType.VAL_OBJ:
			value.AS_OBJ().printObject()

	def simpleInstruction(self, name, offset):
		print(name)
		return offset + 1
