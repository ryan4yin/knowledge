# CentOS 相关


## epel 源与常用软件

设置阿里云 epel 源：
```shell
# https://developer.aliyun.com/mirror/epel
yum -y install epel-release wget
mv /etc/yum.repos.d/epel.repo /etc/yum.repos.d/epel.repo.backup

wget -O /etc/yum.repos.d/epel.repo https://mirrors.aliyun.com/repo/epel-7.repo
```

安装常用软件：

```shell
yum install -y vim curl wget \
  htop ntpdate sysstat iotop fio nethogs \
  socat
```
