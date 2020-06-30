
需要提前安装好 JDK 环境，可参考 [java 环境安装说明](/programming-language/java/README.md)。

## KeyStore

>如果你使用的是 windows 10 utf-8 编码，使用 keytool 前需要先通过 `chcp 936` 临时切换回 gbk 编码，否则中文会乱码。

生成 KeyStore 密钥+密钥库：

```shell
keytool -genkey -v -keyalg RSA -keysize 2048 -validity 3650 -alias my-app-key -keystore my-keystore.jks

# 然后在交互式地输入名称、城市省份等信息，以及密钥库密码、密钥本身的密码，就生成成功了。
```

查看证书信息，获得证书指纹（应用市场和某些第三方 API 需要验证这个 APP 的密钥签名）。

```shell
keytool -list -v -keystore my-keystore.jks  
Enter keystore password: //输入密码，回车
```

一般需要记录下证书的 SHA1 信息，提供给应用市场/第三方API提供商。


## 参考

- [Android平台签名证书(.keystore)生成指南 ](https://ask.dcloud.net.cn/article/id-35777__page-2)
