# [AWS Node Termination Handler](https://github.com/aws/aws-node-termination-handler)

AWS Node Termination Handler 是一个专门用于处理节点终止的 Kubernetes 组件，它会持续监听 AWS EC2 的各
种事件（如
[EC2 维护事件](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/monitoring-instances-status-check_sched.html)、[EC2 Spot 实例中断](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-interruptions.html)、[ASG 可用区重平衡](https://docs.aws.amazon.com/autoscaling/ec2/userguide/auto-scaling-benefits.html#AutoScalingBehavior.InstanceUsage)等
等），并确保 Kubernetes 控制面及时作出恰当的回应。
