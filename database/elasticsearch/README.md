# 容器方式部署 ElasticSearch

主要使用 [Docker-ELK](https://github.com/deviantony/docker-elk.git)

需要注意的有: 

1. 要在 `docker-compose.yml` 中添加容器日志的大小限制，elk 的日志比较多，不加限制可能会吃光存储空间。
1. 磁盘空间不足时，ElasticSearch 会自动将索引设为 `read only`。
2. ELK 系统启动很慢。（Java 程序的通病）
3. ELK 系统非常吃 CPU 和内存，空载状态下这三件套也要用掉近 2G 的内存。
   1. 建议 ElasticSearch  和 Logstash 的内存上下限都设为 4G-8G。
   2. Logstash 的 pipelines （定时同步）越多，启动就越慢，也越吃性能。要给足 CPU 和 RAM.
4. 设定 ElasticSearch JVM 堆的大小：添加环境变量 `ES_JAVA_OPTS: "-Xmx4g -Xms4g"`
   1. JVM 堆的大量应该低于 50% 物理内存。

## 安装中文分词插件

1. [IK Analyzer](https://github.com/medcl/elasticsearch-analysis-ik): 使用最广泛的中文分词插件
2. [pinyin Analyzer](elasticsearch-analysis-pinyin): 拼音分词插件

如果你有 github 代理，请直接修改 `docker-elk/elasticsearch/Dockerfile`，示例如下：

```dockerfile
ARG ELK_VERSION

# https://www.docker.elastic.co/
FROM docker.elastic.co/elasticsearch/elasticsearch:${ELK_VERSION}

# Add your elasticsearch plugins setup here
# Example: RUN elasticsearch-plugin install analysis-icu
ARG ELK_VERSION  # 这一行不能省略！
RUN elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v6.3.0/elasticsearch-analysis-ik-6.3.0.zip
RUN elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v6.3.0/elasticsearch-analysis-pinyin-6.3.0.zip
```

没有代理，网速慢的话，可以手动下载 zip 包到 ``docker-elk/elasticsearch/` 目录下，然后修改 `docker-elk/elasticsearch/Dockerfile`:

```dockerfile
ARG ELK_VERSION

FROM buildpack-deps:buster
# 下面这行不能省略！
ARG ELK_VERSION
ADD elasticsearch-analysis-ik-${ELK_VERSION}.zip .
# 多阶段构建，第一步解压 zip
RUN unzip elasticsearch-analysis-ik-${ELK_VERSION}.zip -d /ik

# https://github.com/elastic/elasticsearch-docker
FROM docker.elastic.co/elasticsearch/elasticsearch:${ELK_VERSION}

# 从上一阶段的容器中，拷贝解压完成的 elasticsearch 插件
COPY --from=0 /ik /usr/share/elasticsearch/plugins/ik
```


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
    logging: &logging # 限制容器日志大小，也可在 `/etc/docker/daemon.json` 中进行全局配置。
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


1. 创建 ES 数据文件夹 `es_data`，权限设为 777。否则可能航报错 Access Denied。
   1. 这应该是因为 ES 使用的账号有问题，或者是 SELinux 的问题。
2. 构建镜像：`docker-compose build`，如果更新了镜像相关的配置，一定要提前运行这个命令！
3. 通过 `docker-compose up -d` 启动 ELK。



## ELK 监控

ELK 自带监控功能，但是不建议使用，因为比较吃存储。
单机监控，默认保留七天监控日志，大概就要用掉六七个 G。

可以在 Kibana 左边导航栏中的「Monitoring」中查看 ELK 系统的状态。
监控相关的设置可以通过 [ElasticSearch 集群设置更新 API](https://www.elastic.co/guide/en/elasticsearch/reference/current/cluster-update-settings.html) 修改。

监控日志默认保留七天，可通过 API 修改 `xpack.monitoring.history.duration` 来调整保存时间，默认为 `7d`（七天），最小可调整为 `1d`（一天）。

监控的详细设置见 [ES 监控设置](https://www.elastic.co/guide/en/elasticsearch/reference/current/monitoring-settings.html#monitoring-collection-settings)
