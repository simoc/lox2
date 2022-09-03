from enum import IntEnum

class ValueType(IntEnum):
	"""Types of values"""
	VAL_BOOL = 0
	VAL_NIL = 1
	VAL_NUMBER = 2
	VAL_OBJ = 3

class Value:
	def __init__(self):
		self.__type = ValueType.VAL_NIL
		self.__boolean = False
		self.__number = 0
		self.__obj = None

	def BOOL_VAL(n):
		value = Value()
		value.__type = ValueType.VAL_BOOL
		value.__boolean = n
		return value

	def NIL_VAL():
		value = Value()
		value.__type = ValueType.VAL_NIL
		return value

	def NUMBER_VAL(n):
		value = Value()
		value.__type = ValueType.VAL_NUMBER
		value.__number = n
		return value

	def OBJ_VAL(n):
		value = Value()
		value.__type = ValueType.VAL_OBJ
		value.__obj = n
		return value

	def IS_BOOL(self):
		return self.__type == ValueType.VAL_BOOL

	def IS_NIL(self):
		return self.__type == ValueType.VAL_NIL

	def IS_NUMBER(self):
		return self.__type == ValueType.VAL_NUMBER

	def IS_OBJ(self):
		return self.__type == ValueType.VAL_OBJ

	def AS_BOOL(self):
		return self.__boolean

	def AS_NUMBER(self):
		return self.__number

	def AS_OBJ(self):
		return self.__obj

	def printValue(value):
		print('{0:g}'.format(value.AS_NUMBER()), end='')

	def valuesEqual(a, b):
		if a.__type != b.__type:
			return False
		if a.__type == ValueType.VAL_BOOL:
			return a.__boolean == b.__boolean
		if a.__type == ValueType.VAL_NIL:
			return True
		if a.__type == ValueType.VAL_NUMBER:
			return a.__number == b.__number
		if a.__type == ValueType.VAL_OBJ:
			aString = a.AS_OBJ().AS_STRING()
			bString = b.AS_OBJ().AS_STRING()
			return aString == bString
		return False

	def isObjType(self, objectType):
		return self.IS_OBJ() and value.AS_OBJ().type == objectType
