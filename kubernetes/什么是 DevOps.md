
## 关于 DevOps

要理解 DevOps 开发+运维的含义，需要先从传统的「瀑布开发模式」讲起。

传统的「瀑布开发模式」，产品可能半年才部署一次，在半年内依次走完「需求分析」-「设计」- 「开发」-「测试」-「部署与维护」。
这种模式下，开发人员与运维人员基本只有在产品出了问题或者要更新了的时候会有些交互，基本没有其他的什么交流。
这导致运维人员需要的技能少，工作闲，也就每半年肝一次版本更新，基本都是靠开发人员提供的文档，一步步手工操作。

而 DevOps，则强调快速迭代（类似敏捷开发），要求产品能**快速地、高效地、稳定地不断迭代**。
传统的运维人员基本不会 shell 脚本之外的编程技能，而且部署都靠脚本+产品部署文档，对基础设施可能也不够了解，与开发人员交流又少。
完全实现不了「快速地、高效地、稳定地不断迭代」产品。

DevOps 是一种新兴的开发思想，它要求开发团队与运维团队之间要建立起更具协作性、更高效的关系。
DevOps 模式下的运维人员，要兼顾「快速地、高效地迭代」与「稳定」这两点，相应的技能点有：

1. Everything as Code（GitOps）: 所有代码/流程/基础设施/文档/规范都通过 Git 做版本控制。保证任何操作的可重复性。
   1. 基础设施即代码
   2. 文档即代码：任何事件的处理流程都应该有对应的文档及规范。
2. 持续集成/持续交付: 自动化。加快产品迭代速度，也减少人为操作引入的错误。
   1. Everything on Containers.
   2. Automate what can be automated.
3. 容器化、微服务化：这是后端在 DevOps 模式下需要做的改造。但是运维人员也需要了解其中关窍。


## 参考

- [DevOps 和敏捷：究竟有什么区别？](https://zhuanlan.zhihu.com/p/115611598)
- [敏捷开发入门教程 - 阮一峰](https://www.ruanyifeng.com/blog/2019/03/agile-development.html)
- [Ledge —— DevOps knowledge learning platform](https://github.com/phodal/ledge)
- [Everything as code architecture design patten and rules](https://github.com/phodal/ascode.ink)


