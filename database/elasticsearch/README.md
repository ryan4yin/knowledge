# 容器方式部署 ElasticSearch

主要使用 [Docker-ELK](https://github.com/deviantony/docker-elk.git)

需要注意的，主要是防止磁盘使用率过高，导致 ElasticSearch 自动将索引设为 `read only`。

## 修改宿主机的内核参数

elasticsearch 6.8 及以上的版本，需要设置 max_map_count 为 262144，否则不能启动。
docker 的这项内核参数会继承宿主机，因此可以直接修改宿主机的内核参数：
```shell
sudo sysctl -w vm.max_map_count=262144  # 临时生效，重启后需要重新设置
echo "vm.max_map_count=262144" >> /etc/sysctl.conf  # 重启后生效
```

此外，es 还需要修改 ulimit 参数，这可以通过  docker-compose.yml 配置，在下一步进行处理。

详细的系统配置说明见[ElasticSearch Docs - Important System Configuration](https://www.elastic.co/guide/en/elasticsearch/reference/current/system-config.html)

## 修改 `docker-compose.yaml`

1. 添加容器日志限制。否则容器日志可能会吃光整个磁盘。。
1. 修改 ulimit 参数限制

```docker-compose
# ...省略...
services:
  elasticsearch:
    # ...省略...
    logging: &logging # 限制容器服务的日志大小
      options:
        max-size: "10m"
        max-file: "1"
    ulimits:  # 放开 ulimit 限制
      memlock:
        soft: -1
        hard: -1
      nproc: 8096
      nofile:
        soft: 65535
        hard: 65535
    # ...省略...
```

好现在可以通过 `docker-compose up -d` 启动了。

## ELK 监控

ELK 自带监控功能，但是不建议使用，因为比较吃存储。
单机监控，默认保留七天监控日志，大概就要用掉六七个 G。

可以在 Kibana 左边导航栏中的「Monitoring」中查看 ELK 系统的状态。
监控相关的设置可以通过 [ElasticSearch 集群设置更新 API](https://www.elastic.co/guide/en/elasticsearch/reference/current/cluster-update-settings.html) 修改。

监控日志默认保留七天，可通过 API 修改 `xpack.monitoring.history.duration` 来调整保存时间，默认为 `7d`（七天），最小可调整为 `1d`（一天）。

监控的详细设置见 [ES 监控设置](https://www.elastic.co/guide/en/elasticsearch/reference/current/monitoring-settings.html#monitoring-collection-settings)
