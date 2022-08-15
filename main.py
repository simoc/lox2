from vm import *
import sys

vm = VM()
vm.initVm()

def repl():
	print("> ", end='', flush=True)
	for line in sys.stdin:
		vm.interpret(line)
		print("> ", end='', flush=True)

def readFile(path):
	try:
		f = open(path, "r")
		all_lines = f.readlines()
		buffer = ""
		for line in all_lines:
			buffer += line
		f.close()
		return buffer
	except IOError as e:
		print("Could not open file: {}".format(path), file=sys.stderr)
		exit(74)

def runFile(path):
	source = readFile(path)
	result = vm.interpret(source)
	if (result == InterpretResult.INTERPRET_COMPILE_ERROR):
		return(65)
	if (result == InterpretResult.INTERPRET_RUNTIME_ERROR):
		return(70)

if len(sys.argv) == 1:
	repl()
elif len(sys.argv) == 2:
	runFile(sys.argv[1])
else:
	print("Usage: clox [path]", file=sys.stderr)
	exit(64)

exit(0)

