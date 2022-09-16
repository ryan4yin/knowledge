# 路由器


## 小米 AX1800

>https://www.right.com.cn/forum/thread-4032490-1-1.html

```shell
# 启用 SSH
curl "http://192.168.31.1/cgi-bin/luci/;stok=1b09f63d038ea376d2641b1e6c2fe456/api/misystem/set_config_iotdev?bssid=Xiaomi&user_id=longdike&ssid=-h%3B%20nvram%20set%20ssh_en%3D1%3B%20nvram%20commit%3B%20sed%20-i%20's%2Fchannel%3D.*%2Fchannel%3D%5C%22debug%5C%22%2Fg'%20%2Fetc%2Finit.d%2Fdropbear%3B%20%2Fetc%2Finit.d%2Fdropbear%20start%3B"

# 使用命令 `echo 'admmin\nadmin' | passwd root` 修改 SSH 密码
curl "http://192.168.31.1/cgi-bin/luci/;stok=1b09f63d038ea376d2641b1e6c2fe456/api/misystem/set_config_iotdev?bssid=Xiaomi&user_id=longdike&ssid=-h%3B%20echo%20-e%20'xxx123xxx%5Cnxxx123xxx'%20%7C%20passwd%20root%3B"
```

## 安装 Clash

- https://github.com/juewuy/ShellClash

