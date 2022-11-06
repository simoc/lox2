from enum import IntEnum
from value import *
from chunk import *
from table import *

class ObjType(IntEnum):
	OBJ_BOUND_METHOD = 0
	OBJ_CLASS = 1
	OBJ_CLOSURE = 2
	OBJ_FUNCTION = 3
	OBJ_INSTANCE = 4
	OBJ_NATIVE = 5
	OBJ_STRING = 6
	OBJ_UPVALUE = 7

class Obj:
	def __init__(self, type):
		self.__type = type

	def OBJ_TYPE(self):
		return self.__type

class Upvalue:
	"""A value defined in an outer scope, further up the stack"""
	def __init__(self):
		self.index = 0
		self.isLocal = False

class ObjFunction(Obj):
	def __init__(self, name):
		super().__init__(ObjType.OBJ_FUNCTION)
		self.arity = 0
		self.upvalues = []
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

class ObjNative(Obj):
	def __init__(self, function):
		super().__init__(ObjType.OBJ_NATIVE)
		self.__function = function

	def printObject(self):
		print('<native fn>', end='')

	def IS_NATIVE(self):
		return self.OBJ_TYPE() == ObjType.OBJ_NATIVE

	def AS_NATIVE(self):
		return self.__function

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

class ObjUpvalue(Obj):
	def __init__(self, slot):
		super().__init__(ObjType.OBJ_UPVALUE)
		self.__chars = str
		self.location = slot
		self.closed = Value.NIL_VAL()
		self.next = None

	def printObject(self):
		print('upvalue', end='')

class ObjClosure(Obj):
	def __init__(self, function):
		super().__init__(ObjType.OBJ_CLOSURE)
		self.__function = function
		self.upvalues = []
		i = 0
		while i < len(function.upvalues):
			self.upvalues.append(None)
			i += 1

	def IS_CLOSURE(self):
		return self.OBJ_TYPE() == ObjType.OBJ_CLOSURE

	def AS_CLOSURE(self):
		return self.__function

	def printObject(self):
		self.__function.printObject()

class ObjClass(Obj):
	def __init__(self, name):
		super().__init__(ObjType.OBJ_CLASS)
		self.__name = name
		self.methods = Table()

	def IS_CLASS(self):
		return self.OBJ_TYPE() == ObjType.OBJ_CLASS

	def printObject(self):
		if self.OBJ_TYPE() == ObjType.OBJ_CLASS:
			self.__name.printObject()

class ObjInstance(Obj):
	def __init__(self, klass):
		super().__init__(ObjType.OBJ_INSTANCE)
		self.klass = klass
		self.fields = Table()

	def IS_INSTANCE(self):
		return self.OBJ_TYPE() == ObjType.OBJ_INSTANCE

	def printObject(self):
		if self.OBJ_TYPE() == ObjType.OBJ_INSTANCE:
			self.klass.printObject()
			print(' instance', end='')

class ObjBoundMethod(Obj):
	def __init__(self, receiver, method):
		super().__init__(ObjType.OBJ_BOUND_METHOD)
		self.receiver = receiver
		self.method = method

	def IS_BOUND_METHOD(self):
		return self.OBJ_TYPE() == ObjType.OBJ_BOUND_METHOD

	def printObject(self):
		if self.OBJ_TYPE() == ObjType.OBJ_BOUND_METHOD:
			self.method.printObject()
