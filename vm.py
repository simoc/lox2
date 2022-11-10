from enum import IntEnum
from chunk import *
from compiler import *
from value import *
from table import *
from object import *
import time

class CallFrame:
	"""A CallFrame represents a single ongoing function call"""
	def __init__(self):
		self.closure = ObjClosure(ObjFunction(None))
		self.ip = 0
		self.stack = []
		# index of first slot in self.stack for this call frame
		self.firstSlotInStack = 0

	def getSlot(self, index):
		return self.stack[self.firstSlotInStack + index]

	def setSlot(self, index, value):
		self.stack[self.firstSlotInStack + index] = value

class InterpretResult(IntEnum):
	"""Possible results of interpreting chunk of bytecode"""
	INTERPRET_OK = 1
	INTERPRET_COMPILE_ERROR = 2
	INTERPRET_RUNTIME_ERROR = 3

class VM:
	"""A virtual machine for executing chunks of bytecode"""

	debugTraceExecution = 0

	def __init__(self):
		self.initVm()

	def clockNative(self, argCount, args):
		"""Return elapsed processor time in seconds"""
		return Value.NUMBER_VAL(time.process_time())

	def initVm(self):
		"""Setup empty virtual machine"""
		self.resetStack()
		self.globals = Table()
		self.initString = "init"
		self.defineNative("clock", self.clockNative)

	def resetStack(self):
		self.stack = []
		self.frames = []

	def runtimeError(self, message):
		print(message, file=sys.stderr)
		frame = self.frames[-1]
		instruction = frame.ip - 1
		line = frame.closure.AS_CLOSURE().chunk.lines[instruction]
		print("[line {0}] in script".format(line), file=sys.stderr)

		i = len(self.frames) - 1
		while i >= 0:
			frame = self.frames[i]
			closure = frame.closure
			instruction = frame.ip
			print("[line {0}] in ".format(closure.AS_CLOSURE().chunk.lines[instruction]), file=sys.stderr, end='')
			if closure.AS_CLOSURE().getName() == None:
				print("script", file=sys.stderr)
			else:
				print("{0}()".format(closure.AS_CLOSURE().getName().AS_STRING()), file=sys.stderr)
			i -= 1
		self.resetStack()

	def defineNative(self, name, function):
		self.push(ObjString(name))
		self.push(Value.OBJ_VAL(ObjNative(function)))
		self.globals.set(self.peek(1), self.peek(0))
		self.pop()
		self.pop()

	def freeVm(self):
		"""Free memory used by virtual machine"""
		return

	def interpret(self, source):
		"""Interpret lox source code"""
		c = Compiler(None, FunctionType.TYPE_SCRIPT)
		function = c.compile(source)
		if function == None:
			return InterpretResult.INTERPRET_COMPILE_ERROR

		self.push(Value.OBJ_VAL(function))
		frame = CallFrame()
		closure = ObjClosure(function)
		self.pop()
		self.push(Value.OBJ_VAL(closure))
		frame.closure = closure
		frame.ip = 0
		frame.stack = self.stack
		frame.firstSlotInStack = 0
		self.frames.append(frame)

		return self.run()

	def checkNumberBinaryOperands(self):
		return self.peek(0).IS_NUMBER() and self.peek(1).IS_NUMBER()

	def checkStringBinaryOperands(self):
		if self.peek(0).IS_OBJ() and self.peek(1).IS_OBJ():
			return self.peek(0).AS_OBJ().IS_STRING() and self.peek(1).AS_OBJ().IS_STRING()

	def run(self):
		frame = self.frames[-1]
		while True:
			if self.debugTraceExecution != 0:
					print('        ', end='')
					i = 0
					while i < len(self.stack):
						print('[ ', end='')
						frame.closure.AS_CLOSURE().chunk.printValue(self.stack[i])
						print(' ]', end='')
						i += 1
					print('')
					frame.closure.AS_CLOSURE().chunk.disassembleInstruction(frame.ip)
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

			if instruction == OpCode.OP_POP:
				self.pop()

			if instruction == OpCode.OP_GET_LOCAL:
				slot = self.readByte()
				self.push(frame.getSlot(slot))

			if instruction == OpCode.OP_SET_LOCAL:
				slot = self.readByte()
				frame.setSlot(slot, self.peek(0))

			if instruction == OpCode.OP_GET_GLOBAL:
				constant = self.readConstant()
				name = constant.AS_OBJ()
				value = self.globals.get(name)
				if value == None:
					self.runtimeError("Undefined variable '{0}'".format(name.AS_STRING()))
					return InterpretResult.INTERPRET_RUNTIME_ERROR
				self.push(value)

			if instruction == OpCode.OP_DEFINE_GLOBAL:
				constant = self.readConstant()
				name = constant.AS_OBJ()
				self.globals.set(name, self.peek(0))
				self.pop()

			if instruction == OpCode.OP_SET_GLOBAL:
				constant = self.readConstant()
				name = constant.AS_OBJ()
				if self.globals.set(name, self.peek(0)):
					self.globals.delete(name)
					self.runtimeError("Undefined variable '{0}'".format(name.AS_STRING()))
					return InterpretResult.INTERPRET_RUNTIME_ERROR

			if instruction == OpCode.OP_GET_UPVALUE:
				slot = self.readByte()
				frame = self.frames[-1]
				self.push(frame.closure.upvalues[slot].location)

			if instruction == OpCode.OP_SET_UPVALUE:
				slot = self.readByte()
				frame = self.frames[-1]
				frame.closure.upvalues[slot].location = self.peek(0)

			if instruction == OpCode.OP_GET_PROPERTY:
				if self.peek(0).AS_OBJ().OBJ_TYPE() != ObjType.OBJ_INSTANCE:
					self.runtimeError("Only instances have properties.")
					return InterpretResult.INTERPRET_RUNTIME_ERROR

				instance = self.peek(0).AS_OBJ()
				name = self.readString()
				value = instance.fields.get(name)
				if value != None:
					self.pop()
					self.push(value)
				elif not self.bindMethod(instance.klass, name):
					return InterpretResult.INTERPRET_RUNTIME_ERROR

			if instruction == OpCode.OP_SET_PROPERTY:
				if self.peek(1).AS_OBJ().OBJ_TYPE() != ObjType.OBJ_INSTANCE:
					self.runtimeError("Only instances have fields.")
					return InterpretResult.INTERPRET_RUNTIME_ERROR

				instance = self.peek(1).AS_OBJ()
				key = self.readString()
				value = self.peek(0)
				instance.fields.set(key, value)
				self.pop()
				self.pop()
				self.push(value)

			if instruction == OpCode.OP_EQUAL:
				b = self.pop()
				a = self.pop()
				eq = Value.valuesEqual(a, b)
				self.push(Value.BOOL_VAL(eq))

			if instruction == OpCode.OP_GREATER:
				if not self.checkNumberBinaryOperands():
					self.runtimeError("Operands must be numbers.")
					return InterpretResult.INTERPRET_RUNTIME_ERROR
				b = self.pop().AS_NUMBER()
				a = self.pop().AS_NUMBER()
				self.push(Value.BOOL_VAL(a > b))

			if instruction == OpCode.OP_LESS:
				if not self.checkNumberBinaryOperands():
					self.runtimeError("Operands must be numbers.")
					return InterpretResult.INTERPRET_RUNTIME_ERROR
				b = self.pop().AS_NUMBER()
				a = self.pop().AS_NUMBER()
				self.push(Value.BOOL_VAL(a < b))

			if instruction == OpCode.OP_ADD:
				if self.checkStringBinaryOperands():
					self.concatenate()
				elif self.checkNumberBinaryOperands():
					b = self.pop().AS_NUMBER()
					a = self.pop().AS_NUMBER()
					self.push(Value.NUMBER_VAL(a + b))
				else:
					self.runtimeError("Operands must be numbers.")
					return InterpretResult.INTERPRET_RUNTIME_ERROR

			if instruction == OpCode.OP_SUBTRACT:
				if not self.checkNumberBinaryOperands():
					self.runtimeError("Operands must be numbers.")
					return InterpretResult.INTERPRET_RUNTIME_ERROR
				b = self.pop().AS_NUMBER()
				a = self.pop().AS_NUMBER()
				self.push(Value.NUMBER_VAL(a - b))

			if instruction == OpCode.OP_MULTIPLY:
				if not self.checkNumberBinaryOperands():
					self.runtimeError("Operands must be numbers.")
					return InterpretResult.INTERPRET_RUNTIME_ERROR
				b = self.pop().AS_NUMBER()
				a = self.pop().AS_NUMBER()
				self.push(Value.NUMBER_VAL(a * b))

			if instruction == OpCode.OP_DIVIDE:
				if not self.checkNumberBinaryOperands():
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

			if instruction == OpCode.OP_PRINT:
				frame.closure.AS_CLOSURE().chunk.printValue(self.pop())
				print()

			if instruction == OpCode.OP_JUMP_IF_FALSE:
				offset = self.readShort()
				if (self.isFalsey(self.peek(0))):
					frame.ip += offset

			if instruction == OpCode.OP_JUMP:
				offset = self.readShort()
				frame.ip += offset

			if instruction == OpCode.OP_LOOP:
				offset = self.readShort()
				frame.ip -= offset

			if instruction == OpCode.OP_CALL:
				argCount = self.readByte()
				if not self.callValue(self.peek(argCount), argCount):
					return InterpretResult.INTERPRET_RUNTIME_ERROR
				frame = self.frames[-1]

			if instruction == OpCode.OP_INVOKE:
				method = self.readString()
				argCount = self.readByte()
				if not self.invoke(method, argCount):
					return InterpretResult.INTERPRET_RUNTIME_ERROR
				frame = self.frames[-1]

			if instruction == OpCode.OP_CLOSURE:
				constant = self.readConstant()
				function = constant.AS_OBJ()
				closure = ObjClosure(function)
				self.push(Value.OBJ_VAL(closure))
				i = 0
				while i < len(closure.upvalues):
					isLocal = self.readByte()
					index = self.readByte()
					if isLocal == 1:
						closure.upvalues[i] = self.captureUpvalue(self.frames[-1].getSlot(index))
					else:
						closure.upvalues[i] = self.frames[-1].closure.upvalues[index]
					i += 1

			if instruction == OpCode.OP_CLOSE_UPVALUE:
				self.closeUpvalues(0)
				self.pop()

			if instruction == OpCode.OP_RETURN:
				result = self.pop()
				self.closeUpvalues(0)
				firstSlotInStack = self.frames[-1].firstSlotInStack
				self.frames.pop()
				if len(self.frames) == 0:
					self.pop()
					return InterpretResult.INTERPRET_OK

				# pop the arguments passed to the function, so it
				# returns to the state before the function was called.
				while len(self.stack) > firstSlotInStack:
					self.pop()

				self.push(result)
				frame = self.frames[-1]

			if instruction == OpCode.OP_CLASS:
				name = self.readString()
				self.push(Value.OBJ_VAL(ObjClass(name)))

			if instruction == OpCode.OP_INHERIT:
				superclass = self.peek(1).AS_OBJ()

				if superclass.OBJ_TYPE() != ObjType.OBJ_CLASS:
					self.runtimeError("Superclass must be a class.")
					return InterpretResult.INTERPRET_RUNTIME_ERROR

				subclass = self.peek(0).AS_OBJ()
				subclass.methods.addAll(superclass.methods)
				self.pop() # Subclass.

			if instruction == OpCode.OP_METHOD:
				name = self.readString()
				self.defineMethod(name)

	def readByte(self):
		frame = self.frames[-1]
		b = frame.closure.AS_CLOSURE().chunk.code[frame.ip]
		frame.ip += 1
		return b

	def readShort(self):
		frame = self.frames[-1]
		b1 = frame.closure.AS_CLOSURE().chunk.code[frame.ip]
		b2 = frame.closure.AS_CLOSURE().chunk.code[frame.ip + 1]
		frame.ip += 2
		return (b1 << 8) | b2

	def readConstant(self):
		n = self.readByte()
		frame = self.frames[-1]
		return frame.closure.AS_CLOSURE().chunk.constants[n]

	def readString(self):
		return self.readConstant().AS_OBJ()

	def push(self, value):
		self.stack.append(value)

	def pop(self):
		return self.stack.pop()

	def peek(self, distance):
		"""Peek value that is distance elements from top of stack without modifying stack"""
		return self.stack[len(self.stack) - 1 - distance]

	def call(self, closure, argCount):
		if argCount != closure.AS_CLOSURE().arity:
			self.runtimeError("Expected {0} arguments but got {1}.".format(closure.AS_CLOSURE().arity, argCount))
			return False
		if len(self.frames) == 64:
			self.runtimeError("Stack overflow.")
			return False
		frame = CallFrame()
		frame.closure = closure
		frame.ip = 0
		frame.stack = self.stack
		# Set index of first slot in stack for this call.
		frame.firstSlotInStack = len(self.stack) - (argCount + 1)
		self.frames.append(frame)
		return True

	def callValue(self, callee, argCount):
		if callee.IS_OBJ():
			if callee.AS_OBJ().OBJ_TYPE() == ObjType.OBJ_BOUND_METHOD:
				bound = callee.AS_OBJ()
				frame = self.frames[-1]
				frame.setSlot(-(argCount + 1), Value.OBJ_VAL(bound.receiver))
				return self.call(bound.method, argCount)
			if callee.AS_OBJ().OBJ_TYPE() == ObjType.OBJ_CLASS:
				klass = callee.AS_OBJ()
				frame = self.frames[-1]
				frame.setSlot(-(argCount + 1), Value.OBJ_VAL(ObjInstance(klass)))
				initializer = klass.methods.get(ObjString(self.initString))
				if initializer != None:
					return self.call(initializer, argCount)
				elif argCount != 0:
					self.runtimeError("Expected 0 arguments but got {0}.".format(argCount))
					return False
				return True
			if callee.AS_OBJ().OBJ_TYPE() == ObjType.OBJ_CLOSURE:
				return self.call(callee.AS_OBJ(), argCount)
			if callee.AS_OBJ().OBJ_TYPE() == ObjType.OBJ_NATIVE:
				native = callee.AS_OBJ().AS_NATIVE()
				result = native(argCount, self.stack[-argCount:])
				i = argCount + 1
				while i > 0:
					self.stack.pop()
					i -= 1
				self.push(result)
				return True
		self.runtimeError("Can only call functions and classes.")
		return False

	def invokeFromClass(self, klass, name, argCount):
		method = klass.methods.get(name)
		if method == None:
			self.runtimeError("Undefined property '{0}'.".format(name.AS_STRING()))
			return False
		return self.call(method, argCount)

	def invoke(self, name, argCount):
		receiver = self.peek(argCount)
		if not receiver.AS_OBJ().IS_INSTANCE():
			self.runtimeError("Only instances have methods.")
			return False

		instance = receiver.AS_OBJ()
		value = instance.fields.get(name)
		if value != None:
			frame.setSlot(-(argCount + 1), value)
			return self.callValue(value, argCount)

		return self.invokeFromClass(instance.klass, name, argCount)

	def bindMethod(self, klass, name):
		method = klass.methods.get(name)
		if method == None:
			self.runtimeError("Undefined property '{0}'.".format(name.AS_STRING()))
			return False
		bound = ObjBoundMethod(self.peek(0).AS_OBJ(), method)
		self.pop()
		self.push(Value.OBJ_VAL(bound))
		return True

	def captureUpvalue(self, local):
		return ObjUpvalue(local)

	def closeUpvalues(self, last):
		#TODO understand and implement 25.4.3 and 25.4.4 logic
		pass

	def defineMethod(self, name):
		method = self.peek(0).AS_OBJ()
		klass = self.peek(1).AS_OBJ()
		klass.methods.set(name, method)
		self.pop()

	def isFalsey(self, value):
		if value.IS_NIL():
			return True
		if value.IS_BOOL():
			return value.AS_BOOL() == False
		return False

	def concatenate(self):
		b = self.pop().AS_OBJ().AS_STRING()
		a = self.pop().AS_OBJ().AS_STRING()
		s = ObjString(a + b)
		self.push(Value.OBJ_VAL(s))
