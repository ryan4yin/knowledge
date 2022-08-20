# C 语言的 IO 相关标准库与函数

getchar
putchar
fopen
scanf

基于行的字符串

- fgets
- fputs

错误处理：

- `int feof(FILE *fp)`: 如果 fp 已经遇到了 EOF，则返回非 0 值
- `int ferror(FILE *fp)`: 如果 fp 流上出现报错，则返回非 0 值

字符串 <string.h>：

- strlen
- strcpy
- strcat(s,t)

字符串 <ctype.h>

- is 系列，如果为 true 则返回非 0 值
  - islower
  - isupper
  - isalpha
  - isdigit
  - isalnum: 等同于 isalpha 或 isdigit
- to 系列
  - tolower
  - toupper

TODO
