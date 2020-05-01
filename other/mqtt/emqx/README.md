# [EMQ X](https://github.com/emqx/emqx)

EMQ X Broker - Scalable Distributed MQTT Message Broker for IoT in 5G Era

## 部署

可使用 `docker-compose` 进行单机集群部署测试:

```shell
# 需要使用本文件夹中的 docker-compose.yml
docker-compose up 
```

更方便的方法是使用 helm3 部署测试集群到 kuberntes:

```shell
helm repo add emqx https://repos.emqx.io/charts
helm repo update

helm install my-emqx emqx/emqx --set service.type=NodePort
```
