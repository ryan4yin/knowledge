内网 DNS，某种意义上说，很类似内网 IP 网段。但是 IP 网段的选择主要看网段的大小，而内网 DNS 的选择主要考虑的是可读性、长短等。


1. `internal.xxx.com`/`lan.xxx.com`：就是用公网域名的子域。是使用最广泛的用法，配置也简单。
    - 但是要小心私有 DNS 服务器和公网 DNS 冲突的问题。
    - 也有人抱怨这样的域名太长了。
1. `xxx.local`/`xxx.lan`/`xxx.srv`: 纯粹的私有域，不会和公网冲突。
    - 这样能确保不存在 DNS 冲突，但是 Chorme 在浏览器中输入 xxx.local/xxx.lan/xxx.srv 会默认进行搜索。。Firefox 倒是能正常进入页面。
    - srv 是 `service` 的缩写。
1. `xxx.zone`/`xxx.int`: 看起来像私有域。**但其实是公共顶级域，该域有可能会被别人注册使用！！！**

也需要考虑到内网的应用未来是否有可能放到公网上，如果考虑这种可能性，方案一是最佳选择，因为切换最方便。

另外还有 SSL 证书的问题，大部分 SSL Provider 都不给 .local .lan .corp 等私有顶级域提供 SSL 证书。因此这些域将只能使用非权威证书。
虽然说内网使用非权威证书也不是个大问题，每台机器加个私有证书就行。

## 总结

可以将企业公网域名的一个子域如 `lan.xxx.com` 用做内部域名，也可以用 `xxx.local`/`xxx.lan`/`xxx.srv` 之类的纯私有域。
如果希望共用 ssl 泛域名证书，可以用 `lan.xxx.com`，如果不需要考虑证书等问题，用 `xxx.local` 之类的域名更方便。


## 参考

- 公网根域查询：IANA Root Zone Database: https://www.iana.org/domains/root/db