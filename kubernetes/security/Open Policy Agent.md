## Open Policy Agent - 安全策略即代码

Open Policy Agent 被设计为一个通用的策略引擎，除了替代掉 Kubernetes 的 PSP，它还可以被用在 HTTP API
鉴权、Envoy 权限策略等多种场景下，因此它显然要比 kyverno 更复杂。

其中门槛最高的一点，是 Open Policy Agent 要求使用它的 DSL - Rego 编写权限策略。

这是一个新的发展趋势——安全策略即代码，不过目前看来，大部分人都不太想用 DSL 写安全策略，很多人抱怨说
讨厌 Rego。

## 参考

- [Handling Container Vulnerabilities with Open Policy Agent - Teppei Fukuda, Aqua Security](https://www.youtube.com/watch?v=WKE2XNZ2zr4&list=PLj6h78yzYM2O1wlsM-Ma-RYhfT5LKq0XC&index=17)
