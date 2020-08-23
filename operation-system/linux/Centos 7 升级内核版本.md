
升级 Centos7 内核到 4.18 稳定版：

```shell
# 载入公钥
rpm --import https://www.elrepo.org/RPM-GPG-KEY-elrepo.org
# 安装最新版 elrepo
yum install -y https://www.elrepo.org/elrepo-release-7.el7.elrepo.noarch.rpm
# 列出可使用的 kernel 版本（lt - 长期支持版，ml - 最新稳定版）
yum list available --disablerepo=* --enablerepo=elrepo-kernel
yum install -y --enablerepo=elrepo-kernel kernel-ml-5.8.3-1.el7.elrepo
```

设置启动时使用的默认内核：

```
## 查看系统可用内核
$ cat /boot/grub2/grub.cfg | grep menuentry

...
menuentry 'CentOS Linux (5.8.3-1.el7.elrepo.x86_64) 7 (Core)' --class centos ...x86_64-advanced-fd58a3db-cad3-4c64-ae69-3ac9e2bbc327' {
menuentry 'CentOS Linux (3.10.0-1127.18.2.el7.x86_64) 7 (Core)' --class centos ...


## 设置开机从新内核启动
$ grub2-set-default 'CentOS Linux (5.8.3-1.el7.elrepo.x86_64) 7 (Core)'

## 查看内核启动项
$ grub2-editenv list

saved_entry=CentOS Linux (5.8.3-1.el7.elrepo.x86_64) 7 (Core)
```


## 参考

- [CentOS7 升级内核版本](http://www.mydlq.club/article/79/)
