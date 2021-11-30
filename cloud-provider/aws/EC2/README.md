## AWS EC2 - 虚拟机实例


### 实例类型介绍

> 实例类型：https://aws.amazon.com/cn/ec2/instance-types/

>实例价格：https://aws.amazon.com/cn/ec2/pricing/dedicated-instances/

针对通用计算而言，通常我们的 CPU/MEM 之比为 1:2 或者 1:4，这里主要介绍我用过的这类机器。

下面分别介绍下各实例配置及价格（以 us-east-1a 为例）

### 1. 通用型 - M 系列 - 1:4

- M4（又贵性能又差，但是资源池还算大）
  - CPU: 2.3 GHz Intel Xeon® E5-2686 v4 (Broadwell) 处理器或 2.4 GHz Intel Xeon® E5-2676 v3 (Haswell) 处理器
  - 实例价格：
    - m4.xlarge(4c/13g) - 0.88 USD
    - m4.2xlarge(8c/26g) - 0.88 USD
    - m4.4xlarge(16c/53.5g) - 0.88 USD
    - m4.10xlarge(40c/124.5g) - 2.00 USD
- M5（目前的主力机型）
  - CPU: 最高 3.1 GHz Intel Xeon® Platinum 8175M 处理器，支持 AVX512
  - 实例价格：
    - m5.xlarge(4c/16g) - 0.204 USD
    - m5.2xlarge(8c/32g) - 0.407 USD
    - m5.4xlarge(16c/64g) - 0.815 USD
    - m5.8xlarge(32c/128g) - 1.629 USD
- M5a
  - CPU: AMD EPYC 7000 系列处理器，全内核睿频时钟速度达 2.5GHz
  - 成本: 相比 M5 成本最高降低 10%
- M6i
  - CPU: 高达 3.5 GHz 的第 3 代英特尔至强可扩展处理器，支持 AVX512
  - 成本：与 M5 实例相比，性价比提高 15%
  - 实例价格（每小时）
    - m6i.xlarge(4c/16g) - 0.2112 USD
    - m6i.2xlarge(8c/32g) - 0.4224 USD
    - m6i.4xlarge(16c/64g) - 0.8448 USD
    - m6i.8xlarge(32c/128g) - 1.6896 USD
- **M6g**（未来希望使用的机型）
  - CPU: 基于 Arm 的 AWS Graviton2 处理器
  - 成本：对比 M5 实例，性价比提升 40%
  - 实例价格(每小时)
    - m6g.xlarge(4c/16g) - 0.1632 USD
    - m6g.2xlarge(8c/32g) - 0.3264 USD
    - m6g.4xlarge(16c/64g) - 0.6528 USD
    - m6g.8xlarge(32c/128g) - 1.3056 USD

突增性能型，在运行低于基准阈值时累积积分，在需要时能通过消耗积分，在一分钟内突增至一个完整 CPU 核心：

- T3: 目前主要使用的机型
  - 实例价格（每小时）
    - t3.small(2c2g) - 0.022 USD
    - t3.medium(2c/4g) - 0.0441 USD
- T4g: 
  - CPU: 基于 Arm 的 AWS Graviton2 处理器
  - 成本：性价比提升 40%

### 2. 计算优化型 - C 系列 - 1:2

- C4
  - CPU: 2.9GHz Intel Xeon E5-2666 v3 (Haswell) 处理器
  - 实例价格(每小时)
    - c4.xlarge(4c/7.5g) - 0.219 USD
    - c4.2xlarge(8c/15g) - 0.438 USD
    - c4.4xlarge(16c/30g) - 0.876 USD
    - c4.8xlarge(32c/60g) - 1.591 USD
- C5
  - CPU: 新启动的 C5 实例，都使用定制的 Intel Xeon 可扩展处理器 (Cascade Lake)，具有 3.6GHz 的持续全核 Turbo 频率和高达 3.9GHz 的单核 Turbo 频率.
  - 成本：没有介绍
  - 实例价格(每小时)
    - c5.xlarge(4c/8g) - 0.18 USD
    - c5.2xlarge(8c/16g) - 0.361 USD
    - c5.4xlarge(16c/32g) - 0.721 USD
    - c5.9xlarge(36c/72g) - 1.622 USD
- C5a
  - CPU: 第二代 AMD EPYC 7002 系列处理器，运行频率高达 3.3GHz
  - 存储：EBS 带宽峰值从 c4 的 1000Mbps 提升至 4750Mbps
  - 成本：无介绍，估计没啥性价比？
  - 实例价格(每小时)
    - c5a.xlarge(4c/8g) - 0.169 USD
    - c5a.2xlarge(8c/16g) - 0.339 USD
    - c5a.4xlarge(16c/32g) - 0.678 USD
    - c5a.8xlarge(32c/64g) - 1.355 USD
- C6i
  - CPU: 高达 3.5 GHz 的第 3 代英特尔至强可扩展处理器
  - 存储：EBS 带宽峰值从 c4 的 1000Mbps 提升至 4750Mbps
  - 成本：与 C5 实例相比，计算性价比提高多达 15%
  - 实例价格(每小时)
    - c6i.xlarge(4c/8g) - 0.187 USD
    - c6i.2xlarge(8c/16g) - 0.374 USD
    - c6i.4xlarge(16c/32g) - 0.748 USD
    - c6i.8xlarge(32c/64g) - 1.496 USD
- **C6g**
  - CPU: 定制的 AWS Graviton2 处理器，搭载 64 位 Arm Neoverse 内核
  - 存储：EBS 带宽峰值从 c4 的 1000Mbps 提升至 4750Mbps
  - 成本：性价比最多比当前的 C5 实例高 40%
  - 实例价格(每小时)
    - c6g.xlarge(4c/8g) - 0.1442 USD
    - c6g.2xlarge(8c/16g) - 0.2883 USD
    - c6g.4xlarge(16c/32g) - 0.5766 USD
    - c6g.8xlarge(32c/64g) - 1.1533 USD


