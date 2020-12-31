# Kubernetes 配置（YAML）管理

目前 kubernetes 配置有如下几种流行的编写方法：

1. helm: 基于 go-templates 的模板化、参数化配置。
2. jsonnet: 基于专有 DSL jsonnet 的配置。
3. pulumi/cdk8s: 基于通用编程语言 python/go/typescript/c# 的配置。
4. kustomize: overlay 模式的配置，把变化的配置抽出来做成补丁 patch，剩下的配置就可以复用了。


## 画外：不断增长的配置复杂性

为了应付配置 config 不断增长的复杂性和维护难题，kubernetes 社区出现了 helm/kustomize，此外还死了一票 ksonnet 之类的前浪。

ansible 则选用了 jinja2 作为自己的 yaml 模板引擎，很多熟悉 ansible 的运维人员也因此青睐 jinja2.

hashicorp 在自家的全家桶(terraform/vault/consul)中选用自研的 hcl 语言编写配置，
而 pulumi 直接选用通用编程语言 python/typescript/c#/go 编写配置。


对于「基础设施即代码」，我使用过 terraform 和 pulumi，个人的感觉是，复杂场景下必须要使用 pulumi+python 才能 hold 住配置的复杂性。
terraform 的 hcl 灵活度太差了，即使算上 module，体验和 pulumi+python 也要差一个档次。

而对于 kubernetes 的 yaml 配置管理，目前感觉 helm 体验是最好的。
helm 多了些包管理器的特性，但是也可以单纯使用 `helm template` 渲染 yaml，体验很好。

## 画外：文本渲染的几种思路 - 通用模板 vs DSL 专有模板

在文本渲染领域，有三类不同思路的渲染工具，都很受欢迎：

1. 通用模板：如 jinja2/mustache/go-templates，这类模板语言很「通用」，可用于各类文本渲染场景，因此应用非常广泛。
   - 「通用模板」和 DSL 语法通常都难以兼容，未渲染的模板不能直接被解析使用。
2. DSL 专有模板：如 thymeleaf(xml)，特点是模板本身就是一份完备的 DSL 文本，可以被正确解析，甚至可以直接使用。
3. DSL 语法增强：如 jsonnet/yaml，这两个 DSL 都是 json 的超集，针对 json 冗长、不支持注释等缺点做了优化。

两类模板各有千秋，不过总的来说，「通用模板」是最流行的，毕竟它可以「learn once, use anywhere.」而「DSL 专有模板」也有自己的应用场景。

目前我个人更喜欢使用「通用模板」- helm/jinja2。
DSL 专有模板需要慎重考虑，毕竟会引入额外的复杂度，会增加维护成本。


## 相关文档

- [Eating Your Vegetables: How to Manage 2.5 Million Lines of YAML - Daniel Thomson & Jesse Suen](https://www.youtube.com/watch?v=BGiCRyUDIPg)
