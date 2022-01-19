## [常用 grafana 面板](https://grafana.com/grafana/dashboards)

- kubernetes 官方插件：https://grafana.com/grafana/plugins/grafana-kubernetes-app
- node 节点监控: https://grafana.com/grafana/dashboards/8919
- istio: https://grafana.com/orgs/istio
- 容器监控: 请使用 [potainer](https://github.com/portainer/portainer) 或者 [scope](https://github.com/weaveworks/scope)


## 自定义 Grafana 面板

使用程序自动生成 Grafana 面板：
- https://github.com/weaveworks/grafanalib

或者直接在页面上拖拽、编写 PromQL，需要花点时间学习的是右侧的各种设置。

## 如何简单快捷地导入导出 Grafana 模板？

Grafana 模板如果经常变动，我们希望能时常备份。
而新建集群时，也希望可以有便捷的方法导入模板，最好是一键导入。

- [Grafana 备份恢复教程](https://fuckcloudnative.io/posts/how-to-back-up-all-of-your-grafana-dashboards/)
