from enum import IntEnum
from value import *
from chunk import *

class ObjType(IntEnum):
	OBJ_FUNCTION = 0
	OBJ_STRING = 1

class Obj:
	def __init__(self, type):
		self.__type = type

	def OBJ_TYPE(self):
		return self.__type

class ObjFunction(Obj):
	def __init__(self, name):
		super().__init__(ObjType.OBJ_FUNCTION)
		self.arity = 0
		self.chunk = Chunk()
		self.__name = name

	def __eq__(self, other):
		if isinstance(other, ObjFunction):
			return self.__name == other.__name
		return False

	def __hash__(self):
		return hash(self.__name)

	def getName(self):
		return self.__name

	def IS_FUNCTION(self):
		return self.OBJ_TYPE() == ObjType.OBJ_FUNCTION

	def printObject(self):
		if self.OBJ_TYPE() == ObjType.OBJ_FUNCTION:
			if self.__name == None:
				print('<script>', end='')
				return
			print('<fn ', end='')
			self.__name.printObject()
			print('>', end='')

class ObjString(Obj):
	def __init__(self, str):
		super().__init__(ObjType.OBJ_STRING)
		self.__chars = str

	def __eq__(self, other):
		if isinstance(other, ObjString):
			return self.__chars == other.__chars
		return False

	def __hash__(self):
		return hash(self.__chars)

	def IS_STRING(self):
		return self.OBJ_TYPE() == ObjType.OBJ_STRING

	def AS_CSTRING(self):
		return self.__chars

	def AS_STRING(self):
		return self.__chars

	def printObject(self):
		if self.OBJ_TYPE() == ObjType.OBJ_STRING:
			print(self.AS_CSTRING(), end='')
