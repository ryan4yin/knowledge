# file-sharing - 文件共享服务器

我们常用的文件共享协议有：

1. http: 毫无疑问，http 是应用最广泛的网络协议。
2. smb/nfs: windows/linux 上应用最广泛的文件共享协议，使用体验和本地文件夹基本没有区别。
3. WebDAV: 其全称为 Web-based Distributed Authoring and Versionin, 它扩展了HTTP 1.1，在GET、POST、HEAD等几个HTTP标准方法以外添加了一些新的方法，使应用程序可对Web Server直接读写，并支持写文件锁定(Locking)及解锁(Unlock)，还可以支持文件的版本控制。
    - WebDav 就是 Web 云盘协议/NAS协议。


## 方案一

使用 NAS 做文件共享服务器，如 [OpenMediaVault](https://github.com/openmediavault/openmediavault)，原生就支持 SMB/NFS/FTP 协议。

然后再使用 caddy 做静态文件服务器，提供 HTTP 协议支持，通过 HTTP 提供文件夹形式的索引页。

但是 caddy 作为一个通用服务器，本身不支持太多的文件共享特性：权限策略、文件上传等，它原生都不支持，需要自行实现。

## 方案二

使用 [nextcloud](https://github.com/nextcloud/server) 或者 [cloudreve](https://github.com/cloudreve/Cloudreve)

caddy 只能支持简单的文件浏览与下载，而 nexcloud/cloudreve 是真正的私有云盘，支持：

1. 文件上传、同步
2. 权限策略
3. 接入 s3/smb/ftp 远程存储


## 方案三

[minio](https://github.com/minio/minio) 作为一个兼容 s3 协议的分布式对象存储系统，也提供一个简单的 Web UI 浏览其中的数据，支持 HTTP 协议。

可以使用 minio 做分布式存储，用 nextcloud/cloudreve 做文件共享。



## Web 客户端

我们日常能接触到各种各样的文件共享协议，其中很多如 FTP/WebDAV/Git/S3，可能我们本地都没有一个方便的 GUI 客户端支持它。

这里有一个解决方案：[filestash](https://github.com/mickael-kerjean/filestash)，它是一个 Web 版的文件管理器，
几乎支持常见的所有文件共享协议/云盘。
而且就算支持，像音频视频，你本地也不一定能够正确播放它（没有解码器）。

把它部署在内网，你的所有设备就都能访问这些协议了！
