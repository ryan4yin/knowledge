# IOS 自动化构建

>本文写于 2020-03-03，其中内容可能已经失效，请谨慎参考。

为了实现自动化构建，需要安装 Python3 环境（ macOS 自带）、OpenJDK8+(给 jenkins-agent 需要)。

此外构建 IOS 程序需要安装 Xcode、cocopods 等工具。详见参考。。。

## 常见问题

### 1. 签名失败

构建机需要解锁钥匙串 keychain，否则自动化构建时将无法获取签名密钥。

```
# 解锁「登录」钥匙串
security unlock-keychain -p <password> "$HOME/Library/Keychains/login.keychain"
```

默认情况下，xcode 会自动管理证书及密钥。
但对 devops 而言，就希望能手动管理这些数据，这样可以方便地在任意机器上打包。

为此需要提前手动生成好签名证书等数据，方法：

- [iOS证书(.p12)和描述文件(.mobileprovision)申请 ](https://ask.dcloud.net.cn/article/152)

然后将生成好的 p12 证书及 mobileprovision 导入打包服务器中：

```shell
# 将提前生成好的 p12 签名证书导入到「登录」钥匙串中
# -k 指定证书导入到「登录」钥匙串中
# -P 导入证书时，需要的密码（是导出这个p12格式的证书时输入的密码）
# -A 表示允许任何应用程序访问导入的密钥，不提示警告信息（不安全，不推荐！）
security import $basepath/$p12File -k ~/Library/Keychains/login.keychain -P password -A
```

## 参考

- [ios app真机测试到上架App Store详细教程-必看](http://blog.applicationloader.net/blog/zh/88.html)
- [iOS 各种证书的作用、有效期、过期的后果和解决办法](https://www.jianshu.com/p/95ca850e7ece)
- [在macOS上搭建Flutter开发环境](https://flutterchina.club/setup-macos/)
- [通过命令行安装Xcode](https://apple.stackovernet.com/cn/q/23219)
- [Install Developer Command Line Tools with SSH](https://apple.stackexchange.com/questions/75684/installing-xcode-via-command-line)
- [Create IPA from CLI](https://github.com/flutter/flutter/issues/13065)

## 可能遇到的问题

- [warning: 'sqlite3_wal_checkpoint_v2' is only available on iOS 5.0 or newer](https://stackoverflow.com/questions/55594435/failed-to-build-ios-app-after-upgrading-my-flutter-version)
- [xcodebuild command failing on codesign but logs show incorrect profile uuid being used](https://stackoverflow.com/questions/30089572/xcodebuild-command-failing-on-codesign-but-logs-show-incorrect-profile-uuid-bein)
- [Invalid Podfile file: invalid byte sequence in US-ASCII](https://github.com/CocoaPods/CocoaPods/issues/639)
- [Xcode, Codesign Error from Jenkins / SSH](https://stackoverflow.com/questions/26475404/xcode-codesign-error-from-jenkins-ssh-user-interaction-is-not-allowed)
