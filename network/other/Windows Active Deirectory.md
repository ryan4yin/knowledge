# Windows AD 域的建立与管理

要想让企业内部成员方便地使用各类内部服务，最好的办法就是组建一个 AD 域/LDAP 域控，
统一使用同一套身份验证系统登录使用各类应用，如 Gitlab、Wiki、NAS、CI/CD、Docker 镜像仓库、APP 包仓库等等。

## AD 域介绍

待续。


## 最佳实践

我目前想到的 AD 域最佳配置：

1. 管理员账户 administrator 设置强密码，保存好密码，然后封存。紧急情况才使用这个账户。
2. 新建一个 ldap-ops 管理员账户，专门用于各类应用、主机加入域控。
3. 将办公 PC 加入域控后，需要将该 PC 用户的域账号加入到【本地用户和组】-【本地管理员组】中！
   1. 【本地管理员组】只拥有对该 PC 的管理权限，域控仍然是安全的。
   2. 如果不将用户加入【本地管理员组】，很多对 C盘/注册表的操作（比如安装软件）都会要求通过管理员账户授权（输入账号密码），导致管理员账户密码半公开，域控安全形同虚设。
   3. 当然如果你们的办公 PC 要求更高的安全性，就是不允许域用户安装额外的软件，那就不需要这样做。
4. CI/CD 自动化使用专用账户访问域内各项服务（Gitlab/FTP服务器等）。
   1. 细分下去，还可以分为 frontend-ops、backend-ops、autotest-ops、operation-ops 等 CI/CD 账户。


## 参考

- [Acitve Directory Domain Service 入门 - 官方文档](https://docs.microsoft.com/zh-cn/windows-server/identity/ad-ds/ad-ds-getting-started)
