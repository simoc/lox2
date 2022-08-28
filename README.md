# lox2

Lox compiler and virtual machine from Chapters 14-30 of the http://www.craftinginterpreters.com web site and book.

This implementation is in Python instead of C, but uses the same function
names and logic.

## Usage

```
C:\Git_Repos\lox2>type chapter18.lox
!(5 - 4 > 3 * 2 == !nil)

C:\Git_Repos\lox2>python main.py chapter18.lox
=== code ===
0000    1 OP_CONSTANT         0 '5'
0002    | OP_CONSTANT         1 '4'
0004    | OP_SUBTRACT
0005    | OP_CONSTANT         2 '3'
0007    | OP_CONSTANT         3 '2'
0009    | OP_MULTIPLY
0010    | OP_GREATER
0011    | OP_NIL
0012    | OP_NOT
0013    | OP_EQUAL
0014    | OP_NOT
true

C:\Git_Repos\lox2>type chapter19.lox
"st" + "ri" + "ng"

C:\Git_Repos\lox2>python main.py chapter19.lox
=== code ===
0000    1 OP_CONSTANT         0 'st'
0002    | OP_CONSTANT         1 'ri'
0004    | OP_ADD
0005    | OP_CONSTANT         2 'ng'
0007    | OP_ADD
string
```
