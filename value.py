from enum import IntEnum

class ValueType(IntEnum):
	"""Types of values"""
	VAL_BOOL = 0
	VAL_NIL = 1
	VAL_NUMBER = 2
	VAL_OBJ = 3

class Value:
	def __init__(self):
		self.type = ValueType.VAL_NIL
		self.boolean = False
		self.number = 0
		self.obj = None

	def BOOL_VAL(n):
		value = Value()
		value.type = ValueType.VAL_BOOL
		value.boolean = n
		return value

	def NIL_VAL():
		value = Value()
		value.type = ValueType.VAL_NIL
		return value

	def NUMBER_VAL(n):
		value = Value()
		value.type = ValueType.VAL_NUMBER
		value.number = n
		return value

	def OBJ_VAL(n):
		value = Value()
		value.type = ValueType.VAL_OBJ
		value.obj = n
		return value

	def IS_BOOL(self):
		return self.type == ValueType.VAL_BOOL

	def IS_NIL(self):
		return self.type == ValueType.VAL_NIL

	def IS_NUMBER(self):
		return self.type == ValueType.VAL_NUMBER

	def IS_OBJ(self):
		return self.type == ValueType.VAL_OBJ

	def AS_BOOL(self):
		return self.boolean

	def AS_NUMBER(self):
		return self.number

	def AS_OBJ(self):
		return self.obj

	def printValue(value):
		print('{0:g}'.format(value.AS_NUMBER()), end='')

	def valuesEqual(a, b):
		if a.type != b.type:
			return False
		if a.type == ValueType.VAL_BOOL:
			return a.boolean == b.boolean
		if a.type == ValueType.VAL_NIL:
			return True
		if a.type == ValueType.VAL_NUMBER:
			return a.number == b.number
		if a.type == ValueType.VAL_OBJ:
			aString = a.AS_OBJ().AS_STRING()
			bString = b.AS_OBJ().AS_STRING()
			return aString == bString
		return False

	def isObjType(self, objectType):
		return self.IS_OBJ() and value.AS_OBJ().type == objectType
