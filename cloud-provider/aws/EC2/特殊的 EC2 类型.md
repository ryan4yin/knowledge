## 特殊的 EC2 类型

### i3 - 高 I/O 计算实例

> https://aws.amazon.com/cn/ec2/instance-types/i3/

Amazon EC2 I3 实例提供基于 NVMe SSD 的临时块存储，可实现低延迟、极高的随机 I/O 性能、高速连续读取吞
吐量，并能以较低的成本提供高 IOPS。I3 实例可提供高达 25Gbps 的网络带宽和高达 14Gbps 的专用 Amazon
Elastic Block Store (Amazon EBS) 带宽。

#### 实例规格

| 型号        | vCPU | 内存 (GiB) | 联网性能  | 存储 (TB)          |
| ----------- | ---- | ---------- | --------- | ------------------ |
| i3.large    | 2    | 15.25      | 最高 10Gb | 1 x 0.475 NVMe SSD |
| i3.xlarge   | 4    | 30.5       | 最高 10Gb | 1 x 0.95 NVMe SSD  |
| i3.2xlarge  | 8    | 61         | 最高 10Gb | 1 x 1.9 NVMe SSD   |
| i3.4xlarge  | 16   | 122        | 最高 10Gb | 2 x 1.9 NVMe SSD   |
| i3.8xlarge  | 32   | 244        | 10GB      | 4 x 1.9 NVMe SSD   |
| i3.16xlarge | 64   | 488        | 25GB      | 8 x 1.9 NVMe SSD   |
| i3.metal    | 72\* | 512        | 25GB      | 8 x 1.9 NVMe SSD   |

#### 注意点

- i3 实例自带基于 NVMe SSD 的临时块存储，随机 I/O 性能极高，但是**重启后会丢失包含文件系统在内的所有
  数据**。
- i3 的 cpu:mem 配比为 1:8

由于每次重启，i3 自带的存储都会被重置，因此每次重启后都需要重新格式化该磁盘并挂载。

i3 硬盘的使用方法如下：

- 将持久化的程序配置放在 `/home/ec2-user` 中
- 将不需要持久化，但需要极高 I/O 性能的数据，存放在 i3 的临时块存储中，该存储挂载到 `/data`

服务器每次重启后，都需要先运行如下命令挂载磁盘：

```
sudo mkfs.ext4 /dev/nvme0n1
sudo mkdir /data
sudo mount /dev/nvme0n1 /data
```

然后再启动应用程序。
