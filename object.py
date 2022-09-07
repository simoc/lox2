from enum import IntEnum
from value import *

class ObjType(IntEnum):
	OBJ_STRING = 0

class Obj:
	def __init__(self):
		self.type = ObjType.OBJ_STRING

	def OBJ_TYPE(self):
		return self.type

class ObjString(Obj):
	def __init__(self):
		super().__init__()
		self.__chars = ""

	def __init__(self, str):
		super().__init__()
		self.__chars = str

	def IS_STRING(self):
		return self.OBJ_TYPE() == ObjType.OBJ_STRING

	def AS_CSTRING(self):
		return self.__chars

	def AS_STRING(self):
		return self.__chars

	def printObject(self):
		if self.OBJ_TYPE() == ObjType.OBJ_STRING:
			print(self.AS_CSTRING(), end='')
