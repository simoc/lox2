# lox2

Lox compiler and virtual machine from Chapters 14-30 of the http://www.craftinginterpreters.com web site and book.

This implementation is in Python instead of C, but uses the same function
names and logic.

Currently, Chapters 14-23 are implemented.

## Usage

```
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

C:\Git_Repos\lox2>type chapter23.lox
print "begin";
for (var i = 0; i < 5; i = i + 1)
{
	print(i);
}
print "end";

C:\Git_Repos\lox2>python main.py chapter23.lox
=== code ===
0000    1 OP_CONSTANT         0 'begin'
0002    | OP_PRINT
0003    2 OP_CONSTANT         1 '0'
0005    | OP_GET_LOCAL        0
0007    | OP_CONSTANT         2 '5'
0009    | OP_LESS
0010    | OP_JUMP_IF_FALSE   10 -> 34
0013    | OP_POP
0014    | OP_JUMP            14 -> 28
0017    | OP_GET_LOCAL        0
0019    | OP_CONSTANT         3 '1'
0021    | OP_ADD
0022    | OP_SET_LOCAL        0
0024    | OP_POP
0025    | OP_LOOP            25 -> 5
0028    4 OP_GET_LOCAL        0
0030    | OP_PRINT
0031    5 OP_LOOP            31 -> 17
0034    | OP_POP
0035    | OP_POP
0036    6 OP_CONSTANT         4 'end'
0038    | OP_PRINT
begin
0
1
2
3
4
end
```
