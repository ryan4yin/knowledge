# EBS 与 EBS 快照


## 从 EBS 快照 / AMI 创建卷

首次从 EBS 快照创建的卷，其读性能会差到离谱！
而 AMI 镜像实质就是一个 EBS 快照，所以首次从 AMI 创建的 EC2 实例，其读性能也会差到离谱！

根据官方文档 [初始化 Amazon EBS 卷](https://docs.aws.amazon.com/zh_cn/AWSEC2/latest/UserGuide/ebs-initialize.html)，需要通过手动预热的方式来解决这个性能问题。

但我实测对于数据较大的卷，用这种方式进行预热，需要的时间太长了（读速度不到 8M/s），不太现实。

所以我的建议是：不要在 AMI 镜像中放太多数据，尽量在启动实例后再通过其他方式从 S3 或其他节点上拉取数据。

