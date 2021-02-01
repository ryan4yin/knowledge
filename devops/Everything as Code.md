# Everything as Code

目前 DevOps 领域有一个发展趋势，就是 Everything as Code，具体表现：

- Infrastructure as Code: 如 pulumi/terraform
- Policy as Code: 如 open policy agent
- Diagram as Code: 如 [diagrams](https://github.com/mingrammer/diagrams)、[mermaid.js](https://github.com/mermaid-js/mermaid)
- Workflow as Code: 如 [couler](https://github.com/couler-proj/couler)

但是我们也能看到一些项目的理念与 Everything as Code 刚好相反。比如：

- [airflow-declarative](https://github.com/rambler-digital-solutions/airflow-declarative): 使用 yaml 来声明 airflow 流水线，降低门槛。


## Kubernetes Yaml vs. Everything as Code

目前在 Kubernetes 生态圈，有两种发展趋势：

1. Everything as Code: 这是本文的主题
2. Everything as Kubernetes Yaml: 使用 Kubernetes Yaml 来定义一切。
   - [crossplane](https://github.com/crossplane/crossplane): 通过 kubernetes yaml 来定义基础设施，主要目的是为了更 kubernetes.
   - kubevirt: 通过 kubernetes 来定义与管理虚拟机

上述两种趋势目前表现形式是有些冲突的，一个提倡用通用编程语言，另一个则提倡使用更简单的 Yaml.

但是未来也不是没有合流的可能，毕竟 pulumi 本身就支持使用代码来定义 kubernetes 资源。
