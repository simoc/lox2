# lox2

Lox compiler and virtual machine from Chapters 14-30 of the http://www.craftinginterpreters.com web site and book.

This implementation is in Python instead of C, but uses the same function
names and logic.

Currently, Chapters 14-21 are implemented.

## Usage

```
C:\Git_Repos\lox2>type chapter21.1.lox
print 1 + 2;
print 3 * 4;

C:\Git_Repos\lox2>python main.py chapter21.1.lox
=== code ===
0000    1 OP_CONSTANT         0 '1'
0002    | OP_CONSTANT         1 '2'
0004    | OP_ADD
0005    | OP_PRINT
0006    2 OP_CONSTANT         2 '3'
0008    | OP_CONSTANT         3 '4'
0010    | OP_MULTIPLY
0011    | OP_PRINT
3
12

C:\Git_Repos\lox2>type chapter21.4.lox
var breakfast = "beignets";
var beverage = "cafe au lait";
breakfast = "beignets with " + beverage;

print breakfast;

C:\Git_Repos\lox2>python main.py chapter21.4.lox
=== code ===
0000    1 OP_CONSTANT         1 'beignets'
0002    | OP_DEFINE_GLOBAL    0 'breakfast'
0004    2 OP_CONSTANT         3 'cafe au lait'
0006    | OP_DEFINE_GLOBAL    2 'beverage'
0008    3 OP_CONSTANT         5 'beignets with '
0010    | OP_GET_GLOBAL       6 'beverage'
0012    | OP_ADD
0013    | OP_SET_GLOBAL       4 'breakfast'
0015    | OP_POP
0016    5 OP_GET_GLOBAL       7 'breakfast'
0018    | OP_PRINT
beignets with cafe au lait
```
