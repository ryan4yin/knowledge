# Anycast IP Address

>https://en.wikipedia.org/wiki/Anycast

Anycast 是一种 IP 寻址与路由的方法，它使分布在不同地域的不同服务器能共享同一个 IP 地址，而路由器会将数据包路由到离得最近的服务器，由 [RFC1546](https://datatracker.ietf.org/doc/html/rfc1546) 标准化。

Anycast 被广泛应用在 CDN 内容分发网络中，比如 Vercel 的 `76.76.21.21`，AWS 的 Global Accalarator 等等。

TODO