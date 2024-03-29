# 使用WireShark嗅探并解密TLS数据

要通过 WireShark 解密嗅探到的 TLS 数据，需要：

1. 服务端 TLS 证书的私钥
2. 如果使用了客户端认证，应该还需要客户端 TLS 证书的私钥。（待验证）

有了上述两个证书，WireShark 就能解密一些未使用完美前向保密(PFS)密钥协商算法(ECDHE/DHE)加密的 TLS 数
据。可以先通过 tcpdump 等工具抓包得到 pcap 文件，然后导入 wireshark 解密抓到的 TLS 数据。

而对于使用了 ECDHE/DHE 算法协商密钥的 TLS 数据，上述方法就无能为力了。嗅探者无法获知协商出的对称密钥
的内容，也就无法解密。这时，唯一的办法就是从客户端或服务端获取到对称密钥的内容。

Chorme/Firefox 浏览器均支持设置 `SSLKEYLOGFILE` 环境变量来导出协商好的 pre-master 内容，wireshark 可
以直接使用这份数据解密 TLS 数据。

另一种方式是直接修改底层 OpenSSL 代码，将 ECDHE 相关的内容直接打印出来，然后自己算出 pre-master。

对于手机 App 等客户端，目前貌似没有什么简单的抓包手段。

## 总结

随着 TLS1.3 及 ECDHE 等前向保密算法的普及，通过证书公私钥解密数据的方法肯定很快就会被彻底淘汰。目前
`SSLKEYLOGFILE` 是唯一比较简单的 TLS 抓包方法，但是客户端必须使用浏览器。
