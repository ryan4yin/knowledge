# 使用 jsonnet 编写 grafana 配置

jsonnet 是 Google 2014 年开源的一个「数据模板语言」，是专为简化配置而设计的一门 DSL.

grafana 的 json 配置，完整形态下复杂冗长，很适合使用 jsonnet 来编写维护。

## 画外：不断增长的配置复杂性

为了应付配置 config 不断增长的复杂性和维护难题，kubernetes 社区出现了 helm/kustomize，此外还死了一票 ksonnet 之类的前浪。

ansible 则选用了 jinja2 作为自己的 yaml 模板引擎，很多熟悉 ansible 的运维人员也因此青睐 jinja2.

hashicorp 在自家的全家桶(terraform/vault/consul)中选用自研的 hcl 语言编写配置，
而 pulumi 直接选用通用编程语言 python/typescript/c#/go 编写配置。


对于「基础设施即代码」，我使用过 terraform 和 pulumi，个人的感觉是，复杂场景下必须要使用 pulumi+python 才能 hold 住配置的复杂性。
terraform 的 hcl 灵活度太差了，即使算上 module，体验和 pulumi+python 也要差一个档次。

而对于 kubernetes 的 yaml 配置管理，目前感觉 helm 体验是最好的。
helm 多了些包管理器的特性，但是也可以单纯使用 `helm template` 渲染 yaml，体验很好。

而使用 jsonnet 来编写 grafana 配置，说实话我还没研究，待续了。
