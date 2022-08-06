from chunk import *
from vm import *

vm = VM()
vm.initVm()

c = Chunk()
constant = c.addConstant(1.2)
c.writeChunk(OpCode.OP_CONSTANT, 123)
c.writeChunk(constant, 123)

constant = c.addConstant(3.4)
c.writeChunk(OpCode.OP_CONSTANT, 123)
c.writeChunk(constant, 123)

c.writeChunk(OpCode.OP_ADD, 123)

constant = c.addConstant(5.6)
c.writeChunk(OpCode.OP_CONSTANT, 123)
c.writeChunk(constant, 123)

c.writeChunk(OpCode.OP_DIVIDE, 123)

c.writeChunk(OpCode.OP_RETURN, 123)
c.disassembleChunk("test chunk")
vm.interpret(c)
