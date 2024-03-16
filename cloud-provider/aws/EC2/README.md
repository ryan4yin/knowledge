## AWS EC2 - 虚拟机实例

EC2 实例类型

1. 按需实例 - 临时测试用
2. 预留实例 - 固定的工作，使用预留实例
3. 竞价 Spot 实例，随时可能被终止 - 爬虫、map reduce 的 task 实例

在任一 ec2 实例中调用固定的 http api，就能获取到它自身相关的 user-data/meta-data 以及资源绑定的 Role
相关的 Ak/SK 信息，这两个文件其实和 cloud-init 很类似，甚至就是用 cloud-init 实现的。

### userdata 与 cloudinit

cloudinit: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html#user-data-cloud-init

### 实例类型介绍

> 实例类型：https://aws.amazon.com/cn/ec2/instance-types/

> AWS and AMD https://aws.amazon.com/ec2/amd/

> 实例历史：https://aws.amazon.com/blogs/aws/ec2-instance-history/

> OD 实例价格：https://aws.amazon.com/cn/ec2/pricing/dedicated-instances/

> Spot 实例价
> 格：https://docs.aws.amazon.com/zh_cn/AWSEC2/latest/UserGuide/using-spot-instances-history.html

针对通用计算而言，通常我们的 CPU/MEM 之比为 1:2 或者 1:4，影响服务性能的主要是 CPU/MEM，存储性能对服
务有一定影响，但是不大。

这里主要介绍针对 Web 服务与离线计算常用的实例类型，而且侧重考虑使用 Spot 实例，暂时不考虑「内存优化
型(R/X)」与「存储优化(D/I)」这几个类型。

下面以 us-east-1a 为例，分别介绍下各实例配置及价格，Spot 使用 2021/11/30 号前一周的历史数据进行统
计。

### 1. 通用型 - M 系列 - 1:4

- M4（基于 Xen 虚拟化技术，又贵性能又差，但是资源池目前还算大）
  - CPU: 2.3 GHz Intel Xeon® E5-2686 v4 (Broadwell) 处理器或 2.4 GHz Intel Xeon® E5-2676 v3
    (Haswell) 处理器

|        实例名称         | OD 单价（USD） | Spot 本周平均单价 | Spot 节约成本 |
| :---------------------: | :------------: | :---------------: | :-----------: |
|    m4.xlarge(4c/13g)    |      0.88      |      0.0921       |    53.94%     |
|   m4.2xlarge(8c/26g)    |      0.88      |      0.2388       |    40.30%     |
|  m4.4xlarge(16c/53.5g)  |      0.88      |      0.3350       |    58.12%     |
| m4.10xlarge(40c/124.5g) |      2.00      |      0.8937       |    55.38%     |

- M5（基于 KVM 定制的 Nitro 虚拟化技术，性价比高）
  - CPU: 最高 3.1 GHz Intel Xeon® Platinum 8175M 处理器，支持 AVX512
  - 成本：相比 M4 实例，性价比可提高 14%

|       实例名称        | OD 单价（USD） | Spot 本周平均单价 | Spot 节约成本 |
| :-------------------: | :------------: | :---------------: | :-----------: |
|   m5.xlarge(4c/16g)   |     0.204      |      0.0711       |    62.96%     |
|  m5.2xlarge(8c/32g)   |     0.407      |      0.1804       |    53.02%     |
|  m5.4xlarge(16c/64g)  |     0.815      |      0.3735       |    51.36%     |
| m5.8xlarge(32c/128g)  |     1.629      |      0.7017       |    54.32%     |
| m5.12xlarge(48c/192g) |     2.444      |      1.6180       |    29.77%     |

- M5a
  - CPU: AMD EPYC 7000 系列处理器，全内核睿频时钟速度达 2.5GHz
  - 存储：x/2x/4x 的 EBS 带宽上限只有 2880Mbps，低于 M5 的 4750Mbps
  - 成本: 相比 M5 成本最高降低 10%
- M6i
  - CPU: 高达 3.5 GHz 的第 3 代英特尔至强可扩展处理器，支持 AVX512
  - 成本：与 M5 实例相比，性价比提高 15%

|        实例名称        | OD 单价（USD） | Spot 本周平均单价 | Spot 节约成本 |
| :--------------------: | :------------: | :---------------: | :-----------: |
|   m6i.xlarge(4c/16g)   |     0.2112     |      0.0829       |    56.82%     |
|  m6i.2xlarge(8c/32g)   |     0.4224     |      0.2404       |    37.39%     |
|  m6i.4xlarge(16c/64g)  |     0.8448     |      0.3461       |    54.93%     |
| m6i.8xlarge(32c/128g)  |     1.6896     |      0.6193       |    59.68%     |
| m6i.12xlarge(48c/192g) |     2.5344     |      0.9171       |    60.19%     |

- **M6g**（未来希望使用的机型）
  - CPU: 基于 Arm 的 AWS Graviton2 处理器
  - 成本：对比 M5 实例，性价比提升 40%

|       实例名称        | OD 单价（USD） | Spot 本周平均单价 | Spot 节约成本 |
| :-------------------: | :------------: | :---------------: | :-----------: |
|  m6g.xlarge(4c/16g)   |     0.1632     |      0.0714       |    53.64%     |
|  m6g.2xlarge(8c/32g)  |     0.3264     |      0.1464       |    52.47%     |
| m6g.4xlarge(16c/64g)  |     0.6528     |      0.3054       |    50.42%     |
| m6g.8xlarge(32c/128g) |     1.3056     |      0.5713       |    53.63%     |
| m6g.8xlarge(48c/192g) |     1.9584     |      0.8570       |    53.63%     |

- M6a(2021/11/29)
  - CPU: 第三代 AMD EPYC processors, 全核睿频 3.6 GHz
  - 成本：对比 m5a 性价比最高提升 35%

突增性能型，在运行低于基准阈值时累积积分，在需要时能通过消耗积分，在一分钟内突增至一个完整 CPU 核
心：

- T3: 目前主要使用的机型

|     实例名称     | OD 单价（USD） |
| :--------------: | :------------: |
|  t3.small(2c2g)  |     0.0220     |
| t3.medium(2c/4g) |     0.0441     |

- T4g:
  - CPU: 基于 Arm 的 AWS Graviton2 处理器
  - 成本：性价比提升 40%

### 2. 计算优化型 - C 系列 - 1:2

- C4（基于 Xen 虚拟化技术，又贵性能又差，但是资源池目前还算大）
  - CPU: 2.9GHz Intel Xeon E5-2666 v3 (Haswell) 处理器

|      实例名称       | OD 单价（USD） | Spot 本周平均单价 | Spot 节约成本 |
| :-----------------: | :------------: | :---------------: | :-----------: |
| c4.xlarge(4c/7.5g)  |     0.219      |      0.0655       |    67.06%     |
| c4.2xlarge(8c/15g)  |     0.438      |      0.2355       |    40.83%     |
| c4.4xlarge(16c/30g) |     0.876      |      0.3015       |    62.12%     |
| c4.8xlarge(32c/60g) |     1.591      |      0.6448       |    59.47%     |

- C5（基于 KVM 定制的 Nitro 虚拟化技术，性价比高）
  - CPU: 新启动的 C5 实例，都使用定制的 Intel Xeon 可扩展处理器 (Cascade Lake)，具有 3.6GHz 的持续全
    核 Turbo 频率和高达 3.9GHz 的单核 Turbo 频率.
  - 成本：与 C4 实例相比，性能/价格比提高了 49%

|      实例名称       | OD 单价（USD） | Spot 本周平均单价 | Spot 节约成本 |
| :-----------------: | :------------: | :---------------: | :-----------: |
|  c5.xlarge(4c/8g)   |      0.18      |      0.0805       |    52.62%     |
| c5.2xlarge(8c/16g)  |     0.361      |       0.181       |    46.78%     |
| c5.4xlarge(16c/32g) |     0.721      |      0.3259       |    52.07%     |
| c5.9xlarge(36c/72g) |     1.622      |      0.7213       |    52.85%     |

- C5a
  - CPU: 第二代 AMD EPYC 7002 系列处理器，运行频率高达 3.3GHz
  - 存储：EBS 带宽峰值从 c4 的 1000Mbps 提升至 4750Mbps
  - 成本：性价比大概提升 10%

|        实例名称        | OD 单价（USD） | Spot 本周平均单价 | Spot 节约成本 |
| :--------------------: | :------------: | :---------------: | :-----------: |
|   c5a.xlarge(4c/8g)    |     0.169      |      0.0698       |    54.65%     |
|  c5a.2xlarge(8c/16g)   |     0.339      |      0.1853       |    39.85%     |
|  c5a.4xlarge(16c/32g)  |     0.678      |      0.3996       |    35.13%     |
|  c5a.8xlarge(32c/64g)  |     1.355      |      0.7268       |    41.01%     |
| c5a.12xlarge(64c/128g) |     2.033      |      1.1135       |    39.75%     |

- C6i
  - CPU: 高达 3.5 GHz 的第 3 代英特尔至强可扩展处理器
  - 存储：EBS 带宽峰值从 c4 的 1000Mbps 提升至 4750Mbps
  - 成本：与 C5 实例相比，计算性价比提高多达 15%

|       实例名称        | OD 单价（USD） | Spot 本周平均单价 | Spot 节约成本 |
| :-------------------: | :------------: | :---------------: | :-----------: |
|   c6i.xlarge(4c/8g)   |     0.187      |       0.068       |    60.00%     |
|  c6i.2xlarge(8c/16g)  |     0.374      |       0.136       |    60.00%     |
| c6i.4xlarge(16c/32g)  |     0.748      |      0.3121       |    54.10%     |
| c6i.8xlarge(32c/64g)  |     1.496      |      0.5441       |    59.99%     |
| c6i.12xlarge(48c/96g) |     2.244      |      0.8382       |    58.91%     |

- **C6g**
  - CPU: 定制的 AWS Graviton2 处理器，搭载 64 位 Arm Neoverse 内核
  - 存储：EBS 带宽峰值从 c4 的 1000Mbps 提升至 4750Mbps
  - 成本：性价比最多比当前的 C5 实例高 40%

|       实例名称        | OD 单价（USD） | Spot 本周平均单价 | Spot 节约成本 |
| :-------------------: | :------------: | :---------------: | :-----------: |
|   c6g.xlarge(4c/8g)   |     0.1442     |       0.068       |    50.00%     |
|  c6g.2xlarge(8c/16g)  |     0.2883     |      0.1361       |    49.97%     |
| c6g.4xlarge(16c/32g)  |     0.5766     |      0.3051       |    43.91%     |
| c6g.8xlarge(32c/64g)  |     1.1533     |      0.5441       |    49.99%     |
| c6g.12xlarge(48c/96g) |     1.7299     |      0.8162       |    49.99%     |

### EC2 与 AMI 的对应关系

注意新的实例类型通常都需要新的 AMI 镜像才会支持，如果 EC2 类型与 AMI 不匹配，可能会造成实例无法启动
等故障。

EKS 的 AMI 对各机型的支持可以参考
[amazon-eks-ami/files/eni-max-pods.txt](https://github.com/awslabs/amazon-eks-ami/blob/v20211109/files/eni-max-pods.txt)
与仓库 tag.

## EC2 启动速度研究

2023 年最新的非官方启动速度测试： https://www.martysweet.co.uk/ec2-launch-times/

总结中的几个点：

1. EBS encryption currently increases the time spent in the pending state for freshly launched
   instances.
2. Unencrypted gp2, gp3 or io1 result in the lowest time spent in the pending instance state for
   freshly launched instances.
3. Use Amazon Linux 2023 or Amazon Linux 2 EKS for the fastest general-purpose AMI to boot for
   launches and stop/starts.
