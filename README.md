# lox2

Lox compiler and virtual machine from Chapters 14-30 of the http://www.craftinginterpreters.com web site and book.

This implementation is in Python instead of C, but uses the same function
names and logic.

## Usage

```
C:\Git_Repos\lox2>type chapter17.lox
(-1 + 2) * 3 - -4

C:\Git_Repos\lox2>python main.py chapter17.lox
=== code ===
0000    1 OP_CONSTANT         0 '1'
0002    | OP_NEGATE
0003    | OP_CONSTANT         1 '2'
0005    | OP_ADD
0006    | OP_CONSTANT         2 '3'
0008    | OP_MULTIPLY
0009    | OP_CONSTANT         3 '4'
0011    | OP_NEGATE
0012    | OP_SUBTRACT
7
```
