from chunk import *

c = Chunk()
constant = c.addConstant(1.2)
c.writeChunk(OpCode.OP_CONSTANT, 123)
c.writeChunk(constant, 123)
c.writeChunk(OpCode.OP_RETURN, 123)
c.disassembleChunk("test chunk")
