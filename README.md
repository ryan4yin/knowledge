# Everything I Know

>个人知识库，主要供自己查阅使用。并不是教程，也不保证正确！

>为了维护方便，本仓库的内容可能会在完善后，被整理、润色，再发布到我的博客 <https://thiscute.world/> 中。这边将只保留一个链接。

主要内容（大致按内容丰富程度排序）：

1. Kubernetes 生态：部署、配置、组件及使用笔记
2. 网络：Kubernetes 集群网络、Linux 网络（学习中）
3. 云服务：AWS/GCP/Alicloud 使用笔记
4. 编程语言学习笔记：Go/Rust/Python
5. Telemetry：监控（Prometheus+Grafana）、日志（ELK/Loki）、链路追踪
6. 操作系统：Linux 系统、KVM 虚拟化等
7. CI/CD：Jenkins/GitLabCI/ArgoWorkflow 等
8.  Homelab: NAS、路由器/树莓派等硬件玩法、ffmpeg 玩法
9.  音乐：乐理、口琴/竹笛、歌声合成、编曲（Reaper）
10. 区块链、分布式系统及原理
11. 建模与图形学：图形学编程、Blender、Unreal Engine 5
12. 机器学习/深度学习（貌似还没开始...）
13. 其他各种我感兴趣的知识

文件夹结构就是文档目录，这里就不额外列索引了—_—

## 镜像站点与加速

### 1. 国内主流镜像站

由于众所周知的原因，很多时候我们需要为各种系统、应用、包管理器设置镜像源以加速下载。

主要有如下几个镜像站：

1. [阿里云开源镜像站](https://developer.aliyun.com/mirror/): 个人感觉是国内下载速度最快的一个镜像源。
    - 提供了 ubuntu/debian/centos/alpine，以及 pypi/goproxy 等主流 OS/PL 的镜像源。比较全。
2. [清华开源镜像源](https://mirrors.tuna.tsinghua.edu.cn/): 非常全，更新也很及时。
    - 但是速度比不上阿里云，而且有时会停机维护。。
1. [北京外国语大学镜像站](https://mirrors.bfsu.edu.cn): 清华镜像的姊妹站，因为目前用的人少，感觉速度比清华源快很多。
3. [中科大开源镜像源](http://mirrors.ustc.edu.cn/): 这个也很全，更新也很快。但是不够稳定。
    - 比清华源要快一点，但是停机维护的频率更高。而且前段时间因为经费问题还将 pypi 源下线了。
4. [腾讯镜像源](https://mirrors.cloud.tencent.com/): 才推出没多久的镜像源，还没用过。

首推阿里云镜像源，稳定可靠速度快。


### 2. 通过代理加速

有些时候不方便设置镜像源，或者根本不存在镜像源。这时有另外两种方法进行下载加速：

1. 最通用的方法：本机安装代理软件，然后设置环境变量 `HTTP_PROXY`/`HTTPS_PROXY` 加速。
2. 一劳永逸的方法（前提是路由器归你管，而且固件支持）：直接在路由器上安装设置 clash 等代理软件，利用 geoip 进行全局智能加速。

详见 [网络代理与科学上网](/network/other/网络代理与科学上网.md)

## DevOps/SRE 相关

### 1. 工具选型

DevOps/SRE 领域，基本都可以直接参考 CNCF 蓝图：[CNCF Cloud Native Interactive Landscape](https://landscape.cncf.io/)


### 2. IT 资料

CS 全自学指南（汇集全球最牛逼的各种课程）：
  - https://github.com/pkuflyingpig/cs-self-learning/
  - https://github.com/ossu/computer-science

偏底层的个人博客（CSAPP 笔记）：

- [不周山作品集](https://wdxtub.com/work/): 学习知识就像不周山，永远不会有『周全』的一天，是为活到老，学到老。

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

## 技术之外

做一名程序员，并不是只需要技术。

技术之外的能力

- 识别关键问题
  - 目前的关键目标是啥？存在哪些关键问题（实现关键目标最大的阻碍）？我最近做的主要工作，是不是在为关键目标服务？
  - 每件事的重要程度、紧急程度、ROI 投入产出比
  - 思考的层面越高，就越难看清楚什么是关键问题。
- 如果规划项目、推进项目前进？
  - 先把事情看清楚，然后以终推始
- 沟通表达能力
- ownership

### 方法论

- 极客时间《10x 程序员工作法》

### 团队协作 - TeamWork

需要学习如何进行高效地团队协作，提高效率。（加更少的班，还能更高质量地完成任务。）

1. [领域驱动设计](https://book.douban.com/subject/5344973/)
   1. 方法：事件风暴
2. [人月神话：软件项目管理之道](https://book.douban.com/subject/26358448/)
3. [程序员修炼之道](https://book.douban.com/subject/5387402/)
4. [人件](https://book.douban.com/subject/1108725/)
5. [《关键对话》：掌握沟通的方式](https://book.douban.com/subject/27046682/)
   - 时刻注意维护对方的安全感；一定要牢记对话的目的。
6. [重构](https://book.douban.com/subject/4262627/)

### 老一辈程序员的思考

- [MacTalk-池建强的随想录](http://macshuo.com/): 极客时间创始人，45+
- [李凡希的Blog](https://www.freemindworld.com/blog/2016/160918_ten_years_2.shtml): 

## 文章转载利器

- [paste-markdown](https://github.com/github/paste-markdown): github 官方出的小工具，将 sheet/table 直接 copy 进来，自动转换为 markdown
- [domchristie/turndown](https://github.com/domchristie/turndown): 将整个 html 页面转换为 markdown，不过对表格的支持好像有点问题

