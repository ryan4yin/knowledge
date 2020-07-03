# IOS 自动化构建

为了实现自动化构建，需要安装 Python3 环境（ macOS 自带）、OpenJDK8+(给 jenkins-agent 需要)。

此外构建 IOS 程序需要安装 Xcode、cocopods 等工具。不详细说明。


## 常见问题

### 签名失败

构建机需要解锁钥匙串 keychain，否则自动化构建时将无法获取签名密钥。

```
# 解锁钥匙串
security unlock-keychain -p <password> "$HOME/Library/Keychains/login.keychain"

// -k 指定证书导入到登录钥匙串中
// -P 导入证书时，需要的密码（是导出这个p12格式的证书时输入的密码）
// -A 表示允许任何应用程序访问导入的密钥，不提示警告信息（不安全，不推荐！）
security import $basepath/$p12File -k ~/Library/Keychains/login.keychain -P password -A
```

