# Everything I Know

> 个人知识库，主要供自己查阅使用。并不是教程，也不保证正确！

> 为了维护方便，本仓库的内容可能会在完善后，被整理、润色，再发布到我的博客 <https://thiscute.world/>
> 中。这边将只保留一个链接。

主要内容（大致按内容丰富程度排序）：

1. 云原生运维相关内容
   1. Kubernetes 生态：部署、配置、组件及使用笔记
   2. 网络：Kubernetes 集群网络、Linux 网络（学习中）
   3. 云服务：AWS/GCP/阿里云/... 使用笔记
   4. Telemetry：监控（Prometheus+Grafana）、日志（ELK/Loki）、链路追踪
   5. CI/CD：Jenkins/GitLabCI/ArgoWorkflow 等
2. 电子工程（最近兴趣很强，正在爬科技树中）
   1. 各种芯片/板子的玩法：树莓派、RK3588、STM32、ESP32
   2. 各种好玩的项目：无人机、智能小车、智能机械臂，甚至机器人
3. 操作系统: Linux、NixOS、KVM 虚拟化等
4. Homelab: 记录我的 Homelab 玩法
   1. 硬件配置、网络拓扑、购置时间、购置渠道与价格
   2. PVE 集群的玩法
   3. 这些高算力可以用来干啥：K3s 集群、分布式监控、HomeAssistant、NAS、测试云原生领域的各种新项
      目...
   4. openwrt 路由器玩法
5. 编程语言学习笔记：Go/Python/C/Rust/...
6. 音乐：乐理、口琴/竹笛、歌声合成、编曲（Reaper）
7. 区块链、分布式系统及原理
8. 机器学习/深度学习（貌似还没开始...）
9. 其他各种我有所涉猎的知识

文件夹结构就是文档目录，这里就不额外列索引了—\_—

## 镜像站点与加速

### 1. 国内主流镜像站

由于众所周知的原因，很多时候我们需要为各种系统、应用、包管理器设置镜像源以加速下载。

主要有如下几个镜像站：

1. [阿里云开源镜像站](https://developer.aliyun.com/mirror/): 个人感觉是国内下载速度最快的一个镜像
   源。
   - 提供了 ubuntu/debian/centos/alpine，以及 pypi/goproxy 等主流 OS/PL 的镜像源。比较全。
2. [清华开源镜像源](https://mirrors.tuna.tsinghua.edu.cn/): 非常全，更新也很及时。
   - 但是速度比不上阿里云，而且有时会停机维护。。
3. [北京外国语大学镜像站](https://mirrors.bfsu.edu.cn): 清华镜像的姊妹站，因为目前用的人少，感觉速度
   比清华源快很多。
4. [中科大开源镜像源](http://mirrors.ustc.edu.cn/): 这个也很全，更新也很快。但是不够稳定。
   - 比清华源要快一点，但是停机维护的频率更高。而且前段时间因为经费问题还将 pypi 源下线了。
5. [腾讯镜像源](https://mirrors.cloud.tencent.com/): 才推出没多久的镜像源，还没用过。

首推北京外国语大学镜像站镜像源，稳定可靠速度快。

## DevOps/SRE 相关

### 1. 工具选型

DevOps/SRE 领域，基本都可以直接参考 CNCF 蓝
图：[CNCF Cloud Native Interactive Landscape](https://landscape.cncf.io/)

### 2. IT 资料

CS 全自学指南（汇集全球最牛逼的各种课程）：

- https://github.com/pkuflyingpig/cs-self-learning/
- https://github.com/ossu/computer-science

偏底层的个人博客（CSAPP 笔记）：

- [不周山作品集](https://wdxtub.com/work/): 学习知识就像不周山，永远不会有『周全』的一天，是为活到
  老，学到老。

系统化的 SRE/DevOps 文档：

- [school-of-sre](https://github.com/linkedin/school-of-sre)
- [devops-exercises](https://github.com/bregman-arie/devops-exercises)
- [test-your-sysadmin-skills](https://github.com/trimstray/test-your-sysadmin-skills)
- [sdn-handbook](https://github.com/feiskyer/sdn-handbook)
- [docker_practice](https://github.com/yeasy/docker_practice)

SRE/DevOps 文章集锦：

- [StabilityGuide - 打造国内稳定性领域知识库](https://github.com/StabilityMan/StabilityGuide)
- [awesome-scalability](https://github.com/binhnguyennus/awesome-scalability)
- [awesome-sre](https://github.com/dastergon/awesome-sre)
- [阿里云容器服务 - DevOps 收藏夹](https://github.com/AliyunContainerService/DevOps)

分布式系统设计：

- https://github.com/binhnguyennus/awesome-scalability
- https://github.com/Vonng/ddia
- https://github.com/donnemartin/system-design-primer

企业/团队博客，各个方向的内容都有：

- [阿里云智能基础软件部](https://kernel.taobao.org/)
- [美团技术团队](https://tech.meituan.com/)

## 工作方法

- 极客时间《10x 程序员工作法》

## 团队协作 - TeamWork

需要学习如何进行高效地团队协作，提高效率。（加更少的班，还能更高质量地完成任务。）

1. [领域驱动设计](https://book.douban.com/subject/5344973/)
   1. 方法：事件风暴
2. [人月神话：软件项目管理之道](https://book.douban.com/subject/26358448/)
3. [程序员修炼之道](https://book.douban.com/subject/5387402/)
4. [人件](https://book.douban.com/subject/1108725/)
5. [《关键对话》：掌握沟通的方式](https://book.douban.com/subject/27046682/)
   - 时刻注意维护对方的安全感；一定要牢记对话的目的。
6. [重构](https://book.douban.com/subject/4262627/)

## 老一辈程序员的思考

- [MacTalk-池建强的随想录](http://macshuo.com/): 极客时间创始人，45+
- [李凡希的 Blog](https://www.freemindworld.com/blog/2016/160918_ten_years_2.shtml):

## 文章转载利器

- [paste-markdown](https://github.com/github/paste-markdown): github 官方出的小工具，将 sheet/table
  直接 copy 进来，自动转换为 markdown
- [domchristie/turndown](https://github.com/domchristie/turndown): 将整个 html 页面转换为 markdown，
  不过对表格的支持好像有点问题

## License

[Ryan Yin's Knowledge](https://github.com/ryan4yin/knowledge) © by Ryan Yin is licensed under
[CC BY-SA 4.0](./LICENSE.md)
