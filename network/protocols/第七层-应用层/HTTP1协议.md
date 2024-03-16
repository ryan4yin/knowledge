# HTTP/1 协议

HTTP/1 有两个广泛使用的版本：HTTP/1.0 和 HTTP/1.1，

## 注意事项

1. http/1 的标准中没有定义 header 字段的大小写，通常大小写都是可以使用的。不过通常使用首字母大写的形
   式。
2. http/1.1 唯一的变化就是添加了 `Keep-Alive: connection` 这个头部字段。
