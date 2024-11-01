# 爬虫/DDoS 攻击与防御

## TLS 指纹识别

指纹识别技术不仅可以用于反爬虫、防 DDoS 攻击，也被一些站点用于识别用户身份。

1. <https://tls.peet.ws/>: 检测你的 TLS JA3/JA4/... 指纹。
   - Chrome 会通过 GREASE 技术随机排列 TLS 扩展，使 JA3 随机化，但 JA4 不会随机化。
   - Firefox/Safari 实测 JA3 和 JA4 都不会随机化。
1. [JA3/JA4 Fingerprint - Cloudflare Docs](https://developers.cloudflare.com/bots/concepts/ja3-ja4-fingerprint/)
   - [JA4+ Technical Details](https://github.com/FoxIO-LLC/ja4/blob/main/technical_details/README.md)
   - 客户端规避手段：基本上通过随机化 TLS Cipher Suites /Extenstions 等方式，就能生成不同的 JA3/JA4
     指纹。
