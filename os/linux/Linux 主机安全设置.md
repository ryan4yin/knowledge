开启了新的 Linux 服务器后，首要任务是做安全配置。

### 1. 添加新用户

建议不要使用 root 账号，而是创建一个新的个人账号：

```shell
adduser username  # 比 useradd 更友好，会进入交互模式设置家目录、密码等

# 给予 user sudo 权限
usermod -aG wheel username  # CentOS 的 wheel 用户组自动获得 sudo 权限
usermod -aG sudo username   # Ubuntu 的 sudo 用户组拥有 sudo 权限

# 如果 adduser 不能使用，或者没有进入交互模式，就改用下面的方法
useradd username
passwd username  # 进交互模式，设置用户密码
```

在需要提权时再 `sudo xxx` 或者 `sudo su`，提升安全性。


### 2. 使用 ssh-key 登录

先在本地机器生成密钥对：
```shell
# 方法一：会进入交互模式，可以指定密钥对保存位置与密钥名称。
## 会使用默认算法 ssh-rsa(RSA/SHA1)，此算法目前已经不够安全！
ssh-keygen
# 或者直接命令行指定密钥算法类型(-t)、名称与路径(-f)、注释(-C)、密钥的保护密码(-P)。
## 当密钥较多时，注释可用于区分密钥的用途。
## 算法推荐使用 ed25519/ecdsa，默认的 rsa 算法目前已不推荐使用（需要很长的密钥和签名才能保证安全）。
ssh-keygen -t ed25519 -f id_rsa_for_xxx -C "ssh key for xxx" -P ''
```

接下来需要把公钥追加到远程主机的 `$HOME/.ssh/authorized_keys` 文件的末尾（`$HOME` 是 user 的家目录，不是 root 的家目录，看清楚了）：

```shell
# 方法一：使用 `ssh-copy-id` 自动完成公钥添加，默认公钥路径 ~/.ssh/id_rsa.pub
 ssh-copy-id  -i path/to/key_name.pub user@host

# 方法二，手动将公钥添加到 ~/.ssh/authorized_keys 中
# 然后手动将  ~/.ssh/authorized_keys 的权限设为 600
chmod 600 ~/.ssh/authorized_keys
```

这样你就可以使用秘钥登录了：
```shell
ssh <username>@<server-ip> -i <rsa_private_key>  # 私钥默认使用 ~/.ssh/id_rsa

# 举例
ssh ubuntu@111.222.333.444 -i ~/.ssh/id_rsa_for_server
```

如果无法登录，可以继续下一步。（在下一步会允许使用秘钥方式登录）

### 3. 禁止密码登录，禁止 root 用户远程登录

编辑 ssh 配置文件 `/etc/ssh/sshd_config`，修改如下：
```config
PermitRootLogin no  # 禁止 root 登录
PasswordAuthentication no  # 禁止密码认证

RSAAuthentication yes  # 允许 RSA 秘钥认证
PubkeyAuthentication yes  # 允许使用公钥认证登录
```

然后重启 ssh 服务：`sudo systemctl sshd restart`

### 4. 打开防火墙，只开启需要使用的端口

旧版的 linux 基本都使用 iptables 做防火墙，但是它配置特别麻烦。而新版的 linux 发行版底层都换成了 eftables，并且提供了更高层的封装，简化上手难度：

1. ubuntu 使用 ufw
2. centos 使用 firewall

**注意**：Docker 的端口映射，ufw 和 firewall 都管不到！这涉及到底层的 iptables 原理，建议网上搜索。。。
总之不要试图通过 ufw/firewall/iptables 去简单地禁用 Docker 映射的端口，没有用的。

#### 4.1 ufw

```bash
$ sudo apt-get install -y ufw  # 新版 ubuntu 自带
$ sudo ufw default deny  # 默认禁用端口
$ sudo ufw allow ssh   # 允许 ssh，这使用了 /etc/services 内的配置，该配置中 ssh 对应端口 22
$ sudo ufw allow http  # /etc/services 中 http 对应 80 端口
$ sudo ufw allow 443/tcp  # 允许 443 的 tcp 连接
$ sudo ufw --force enable  # 开启防火墙
$ sudo ufw status verbose
```

现在只开启了 22 80 和 443 端口，其他所有端口都会被禁用。

#### 4.2 firewall

```bash
systemctl start  firewalld # 启动
systemctl status firewalld # 或者 firewall-cmd --state 查看状态
systemctl disable firewalld # 停止
systemctl stop firewalld  # 禁用

# 显示服务列表  
## Amanda, FTP, Samba和TFTP等最重要的服务已经被FirewallD提供相应的服务，可以使用如下命令查看：
firewall-cmd --get-services

# 允许SSH服务通过
sudo firewall-cmd --zone=public --add-port=22/tcp --permanent

# 禁止SSH服务通过
firewall-cmd --zone=public --remove-port=22/tcp --permanent

sudo firewall-cmd --zone=public --add-port=6379/tcp --permanent

# 修改防火墙规则后需要重载配置
sudo firewall-cmd --reload
```

## 注意事项

1. **上述操作防不了 docker 的端口映射！！！**因为 docker 端口映射的 iptables 链，和防火墙的 iptables 链层级相同！
1. 客户端的公钥文件，权限必须是 600，即仅 owner 可读写。
    - 如果客户端是 windows，必须在公钥文件的「属性」-「安全」中删除掉所有的用户（可能还需要先在「高级」中禁用权限「继承」），只保留自己的读写权限！

## 参考

- [How To Create a Sudo User on CentOS?](https://www.digitalocean.com/community/tutorials/how-to-create-a-sudo-user-on-centos-quickstart)
- [Ubuntu的防火墙配置-ufw](https://www.cnblogs.com/ylan2009/articles/2321136.html)
- [CentOS7 防火墙（firewall）的操作命令](https://www.cnblogs.com/leoxuan/p/8275343.html)