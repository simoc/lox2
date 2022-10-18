# lox2

Lox compiler and virtual machine from Chapters 14-30 of the http://www.craftinginterpreters.com web site and book.

This implementation is in Python instead of C, but uses the same function
names and logic.

Currently, Chapters 14-24 are implemented.

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

$ python3 main.py chapter23.lox
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

$ cat chapter24.5.1.lox
fun sum(a, b, c) {
  return a + b + c;
}

print 4 + sum(5, 6, 7);

$ python3 main.py chapter24.5.1.lox
=== sum ===
0000    2 OP_GET_LOCAL        1
0002    | OP_GET_LOCAL        2
0004    | OP_ADD
0005    | OP_GET_LOCAL        3
0007    | OP_ADD
0008    | OP_RETURN
0009    3 OP_NIL
0010    | OP_RETURN
=== <script> ===
0000    3 OP_CONSTANT         1 '<fn sum>'
0002    | OP_DEFINE_GLOBAL    0 'sum'
0004    5 OP_CONSTANT         2 '4'
0006    | OP_GET_GLOBAL       3 'sum'
0008    | OP_CONSTANT         4 '5'
0010    | OP_CONSTANT         5 '6'
0012    | OP_CONSTANT         6 '7'
0014    | OP_CALL             3
0016    | OP_ADD
0017    | OP_PRINT
0018    6 OP_NIL
0019    | OP_RETURN
22
```
