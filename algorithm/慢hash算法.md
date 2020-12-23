# 密码 Hash 算法 - 慢 Hash 算法

为了增大密码 Hash 的碰撞难度，需要使用慢 Hash 算法限制破解者的计算速度，这可以从如下三个维度入手：

1. 时间复杂度：对应 CPU/GPU 计算资源。
2. 空间复杂度：对应 RAM 资源。
3. 并行维度：使用无法分解的算法，锁定只允许单线程运算。

按照这个思路，目前流行的有如下几种慢 hash 算法：

1. argon2 算法：目前最强的密码 Hash 算法，在 2015 年赢得了密码 Hash 竞赛。
1. scrypt 算法：可以灵活地设定使用的内存大小，在 argon2 不可用时，可使用它。
1. bcrypt 算法：安全性在下降，用得越来越少了。不建议使用。

## 参考

- [Practical Cryptography for Developers](https://cryptobook.nakov.com/)
- [怎样的 Hash 算法能对抗硬件破解](https://www.cnblogs.com/index-html/p/hardware-resistant-hash-algorithm.html)
