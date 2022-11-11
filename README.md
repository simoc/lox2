# lox2

Lox compiler and virtual machine from Chapters 14-30 of the http://www.craftinginterpreters.com web site and book.

This implementation is in Python instead of C, but uses the same function
names and logic.

Currently, Chapters 14-29 are implemented.

Chapter 30 is not implemented, because these optimizations
are specific to the C language.

Hash Tables for Chapter 20 and Garbage Collection
for Chapter 26 are also not implemented and
Python dictionaries are used instead.

## Usage

```
$ cat chapter23.lox
print "begin";
var i = 0;
while (i < 5)
{
        print(i);
        i = i + 1;
}
print "end";

$ python3 main.py --debug-print-code chapter23.lox
=== <script> ===
0000    1 OP_CONSTANT         0 'begin'
0002    | OP_PRINT
0003    2 OP_CONSTANT         2 '0'
0005    | OP_DEFINE_GLOBAL    1 'i'
0007    3 OP_GET_GLOBAL       3 'i'
0009    | OP_CONSTANT         4 '5'
0011    | OP_LESS
0012    | OP_JUMP_IF_FALSE   12 -> 30
0015    | OP_POP
0016    5 OP_GET_GLOBAL       5 'i'
0018    | OP_PRINT
0019    6 OP_GET_GLOBAL       7 'i'
0021    | OP_CONSTANT         8 '1'
0023    | OP_ADD
0024    | OP_SET_GLOBAL       6 'i'
0026    | OP_POP
0027    7 OP_LOOP            27 -> 7
0030    | OP_POP
0031    8 OP_CONSTANT         9 'end'
0033    | OP_PRINT
0034    9 OP_NIL
0035    | OP_RETURN
begin
0
1
2
3
4
end

$ cat fib.lox
fun fib(n) {
 if (n < 2) return n;
 return fib(n - 2) + fib(n - 1);
}

var start = clock();
print fib(25);
var elapsed = clock() - start;
print "elapsed seconds:";
print elapsed;

$ python3 main.py fib.lox
75025
elapsed seconds:
19.4062
```
