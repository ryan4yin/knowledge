# 区块链钱包的原理


TO BE DONE

- 以太坊地址（账户 ID 以及合约 ID）: 使用 Keccak-256 哈希函数从账户公钥或合约内容派生的唯一标识符。
- 以太坊名称注册中心：功能与当前中心化的全球 DNS 系统一致，但是是去中心化的。此外这玩意儿的进展比较缓慢，目前应用好像还不多？

- Inter exchange Client Address Protocol (ICAP): 一种以太坊地址编码，跟目前国际银行通用的 International Bank Account Number (IBAN) 编码比较类似。
  - 比如 `0x001d3f1ef827552ae1114027bd3ecf1f086ba0f9` 使用 ICAP 编码得到 `XE60 HAMI CDXS V5QX VJA7 TJW4 7Q9C HWKJ D`
- 带有大写校验和的十六进制编码 (EIP-55): 它通过把地址中的部分字符转为大写来提供一定的地址校验能力，同时与以太坊地址兼容。
  - `0x001d3f1ef827552ae1114027bd3ecf1f086ba0f9` 使用 EIP-55 得到： 
  - `0x001d3F1ef827552Ae1114027BD3ECF1f086bA0F9`，可以看到只有部分字符变成了大写，其他与以太坊地址完全一致。



## 参考

- [基于 BIP-32 和 BIP-39 规范生成 HD 钱包（分层确定性钱包） ](https://stevenocean.github.io/2018/09/23/generate-hd-wallet-by-bip39.html)

