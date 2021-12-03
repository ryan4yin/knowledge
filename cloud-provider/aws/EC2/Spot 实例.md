# [Spot 实例](https://console.aws.amazon.com/ec2spot)

Spot 实例是一种使用备用 EC2 容量的实例，以低于按需价格提供。
每个可用区中的每种实例类型的 Spot 价格都是动态的，会根据 Spot 实例的长期供求趋势逐步调整。
只要容量可用，并且请求的每小时最高价超过 Spot 价格，Spot 实例就会运行。

Spot 实例的价格通常是对应 OnDemand 实例价格的 30% 到 70%，合理使用 Spot 实例，能节约 30%-60% 的计算成本。

如果能灵活控制应用程序的运行时间并且应用程序可以中断，Spot 实例就是经济实惠之选。
例如，Spot 实例非常适合数据分析、批处理作业、后台处理和可选的任务，因为这类任务中断一会没啥大的影响，最多数据分析延迟一些。

此外，为客户端提供 HTTP API 的服务，做了高可用的话，也可以跑在 Spot 实例上。
比如每个服务设置 3 到 5 个实例，然后资源池配置较高比例的的 Spot 实例、较少比例的 OD 实例，在保证服务稳定性的同时，使用 Spot 实例节约成本。

## Spot 实例历史价格

方法一：https://docs.aws.amazon.com/zh_cn/AWSEC2/latest/UserGuide/using-spot-instances-history.html

方法二：使用 awscli/api，下面简要介绍下：

```yaml
# 如果有使用 EC2 Classic 网络，请使用如下命令
## 可以添加 --instance-types r5.2xlarge 来限定实例类型
aws ec2 describe-spot-price-history --region=us-east-1 --start-time=$(date +%s) --product-descriptions="Linux/UNIX (Amazon VPC)"  > spot-price-now.yaml

# 否则使用如下命令
aws ec2 describe-spot-price-history --region=us-east-1 --start-time=$(date +%s) --product-descriptions="Linux/UNIX" > spot-price-now.yaml
```

## Spot 实例中断

aws Spot 实例的资源池大小，会因为时间不同而出现显著变化。Spot 实例随时可能因为如下原因而中断：

- 价格 - Spot 价格高于你的最高出价
- 容量 - ec2 容量吃紧会导致 aws 回收 Spot 实例，其原因可能是「扩大 OD 实例资源池」、「主机维护或硬件停用」等
- 约束 - 如果您的请求包含约束（如启动组或可用区组），则当不再满足约束时，这些 Spot 实例将成组终止。


### 「Spot 实例中断通知」与「EC2 实例再平衡建议」

当 Amazon EC2 将要中断 Spot 实例时，它在实际中断之前的两分钟发出一个事件（休眠除外，此时会收到中断通知，但不会提前两分钟，因为休眠是立即开始的）。

有两种提前获知此事件的方法：

#### 1. 使用 [Amazon EventBridge](https://console.aws.amazon.com/events/home) 添加事件 hook

在 Amazon EventBridge 中创建一个 Rule，使用 AWS EC2 服务预定义的事件类型。

「Spot 实例中断通知」事件的 Pattern 如下：

```json
{
  "source": ["aws.ec2"],
  "detail-type": ["EC2 Spot Instance Interruption Warning"]
}
```

「EC2 实例再平衡建议」事件的 Pattern 如下：

```json
{
  "source": ["aws.ec2"],
  "detail-type": ["EC2 Instance Rebalance Recommendation"]
}
```

提前写好一个专门处理 Spot 中断事件的 Lambda 函数，然后 Rule 的目标就选择这个函数即可。

Spot 实例中断通知」事件的回调数据示例：

```json
{
  "version": "0",
  "id": "1e5527d7-bb36-4607-3370-4164db56a40e",
  "detail-type": "EC2 Spot Instance Interruption Warning",
  "source": "aws.ec2",
  "account": "123456789012",
  "time": "1970-01-01T00:00:00Z",
  "region": "us-east-1",
  "resources": ["arn:aws:ec2:us-east-1b:instance/i-0b662ef9931388ba0"],
  "detail": {
    "instance-id": "i-0b662ef9931388ba0",
    "instance-action": "terminate"
  }
}
```

#### 2. 通过元数据 API

可以通过轮询的方式，从 API 获取通知。

「Spot 实例中断通知」：

```
TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"`
curl -H "X-aws-ec2-metadata-token: $TOKEN" -s http://169.254.169.254/latest/meta-data/spot/termination-time 
```

如果已存在该通知，示例响应：

```json
{"action": "terminate", "time": "2017-09-18T08:22:00Z"}
```

否则将返回 404


「EC2 实例再平衡建议」:

```
TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"`
curl -H "X-aws-ec2-metadata-token: $TOKEN" –v http://169.254.169.254/latest/meta-data/events/recommendations/rebalance
```

如果存在该建议，会有示例输出：

```json
{"noticeTime": "2020-10-27T08:22:00Z"}
```

否则将返回 404.

###  如何观测 Spot 实例的历史中断概率

#### 1. CloudTrail 的 BidEvictedEvent 事件

在 [CloudTrail](https://console.aws.amazon.com/cloudtrail/home) 中搜索「事件名称」 `BidEvictedEvent`，可以查到 90 天内的所有 Spot 中断事件。

结果可以导出为 csv/json，再丢到 excel 里就能很容易画出每日 Spot 中断数量的趋势图了。

但是这边只能查到 instance_id，具体的 DNS 名称、IP 地址、实例类型等参数，可通过 instance_id 在 [AWS Config](https://console.aws.amazon.com/config/home) 中查询得到。


#### 2. [Spot Instance Advisor](http://aws.amazon.com/ec2/spot/instance-advisor/)

这个页面能看到各种 Spot 实例在过去一个月的中断比例。

## Spot with EKS

>https://new.spotmaxtech.com/

在 EKS 集群中使用 Spot 实例，能在节约大量成本的同时，满足集群动态伸缩的需要，也能通过 EKS 的高可用配置来保证服务稳定性。






