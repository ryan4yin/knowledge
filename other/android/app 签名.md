
需要提前安装好 JDK8，可参考 [java 环境安装说明](/programming-language/java/README.md)。
**注意一定要使用 JDK8，不要用其他版本的 JDK!!!**

## KeyStore

>如果你使用的是 windows 10 utf-8 编码，使用 keytool 前需要先通过 `chcp 936` 临时切换回 gbk 编码，否则中文会乱码。

生成 KeyStore 密钥对+密钥库：

```shell
keytool -genkeypair -v -keyalg RSA -keysize 2048 -validity 3650 -alias my-app-key -keystore my-keystore.jks

# 然后在交互式地输入名称、城市省份等信息，以及密钥库密码、密钥本身的密码，就生成成功了。
```

查看密钥对信息，获得证书指纹（应用市场和某些第三方 API 需要验证这个 APP 的证书签名）。

```shell
keytool -list -v -keystore my-keystore.jks  
Enter keystore password: //输入密码，回车
```

一般需要记录下证书的 SHA1 信息，提供给应用市场/第三方API提供商。

**注：**部分 API 提供商要求使用证书的 MD5 指纹！比如微信分享API。


## 查看 APK 签名证书的指纹

```shell
# 需要使用此文件夹下的 jar 包
cd /<path-to-android>/Android/Sdk/build-tools/30.0.1/lib
java -jar apksigner.jar verify -v xxx.apk
```

上述命令中用到的 `apksigner.jar` 来自 Android build-tools，Android Studio 会自动安装该组件，你也可以尝试手动下载。

如果你使用的 build-tools 版本 >= `30.0.1`，那么你可能需要 JDK11 才能正常执行上述命令。


## 应用签名

在第三方平台进行了应用加固后，需要重新对 APK 进行签名，方法如下：

```shell
# 需要使用此文件夹下的 jar 包
cd /<path-to-android>/Android/Sdk/build-tools/30.0.1/lib
# 1. 方法一，交互式地输入密钥库密码、密钥密码
java -jar apksigner.jar sign \
    --ks <my-app>.jks \
    --ks-key-alias <my-app> \
    --out <my-app>-shield-signed.apk \
    <my-app>-shield.apk
# 2. 方法二，通过环境变量指定密码，适合自动化 CI/CD 时使用。
java -jar apksigner.jar sign \
    --ks <my-app>.jks --ks-pass env:KEYSTORE_PASSWORD\
    --ks-key-alias <my-app> --key-pass env:KEY_PASSWORD\
    --out <my-app>-shield-signed.apk \
    <my-app>-shield.apk
```

## 签名相关的敏感信息

个人开发，可以使用被 git 忽略的 `key.properties` 存放密钥库密码等敏感信息。

做自动化构建时，使用环境变量传递敏感信息更方便，`build.gradle` 里通过 `System.getenv("XXX")` 就能读取环境变量。


## 参考

- [Android平台签名证书(.keystore)生成指南 ](https://ask.dcloud.net.cn/article/id-35777__page-2)
- [关于gradle打包keystore密码的安全问题](https://www.cnblogs.com/liming-saki/p/5016330.html)
