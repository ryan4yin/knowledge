# SSH 协议

- [SSH原理与运用（一）：远程登录](http://www.ruanyifeng.com/blog/2011/12/ssh_remote_login.html)
- [SSH原理与运用（二）：远程操作与端口转发](http://www.ruanyifeng.com/blog/2011/12/ssh_port_forwarding.html)


## 注意事项

`.ssh` 文件夹的权限问题：该文件夹的权限必须符合要求，否则 ssh 的秘钥登录将不能使用。
在恢复备份的 .ssh 文件夹时，可能会出现权限问题，你需要把权限改成如下形式：

- `.ssh` 文件夹：`700 (drwx------)`
- 公钥，即`.pub` 文件：`644 (-rw-r--r--)`
- 私钥，`id_rsa` 等：`600 (-rw-------)`
- 远程主机的 `authorized_keys`：`600 (-rw-------)`