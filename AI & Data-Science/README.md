# 数据科学

[View Through NBViewer](https://nbviewer.jupyter.org/github/ryan4yin/knowledge/tree/master/data-science/)


## AI / ML / DL  / Data Mining 的关系

![](./_img/AI%20ML%20DL%20DataMining.jpg)

## 资料

- ML/DL
  - [Machine Learning for Beginners - MicroSoft](https://github.com/microsoft/ML-For-Beginners): 比较有意思的 ML 入门课
  - [100-Days-Of-ML-Code](https://github.com/Avik-Jain/100-Days-Of-ML-Code) - 100 天从 ML 到 DL，比较全的学习路线
  - [动手学深度学习（Dive into Deep Learning，D2L）](https://github.com/d2l-ai/d2l-zh)
  - [transformers](https://github.com/huggingface/transformers): 超多的 ML 预训练模型，可用于各个领域
  - [Learn how to responsibly deliver value with ML.](https://github.com/GokuMohandas/MadeWithML): 如何将 ML 应用到具体的场景中，产生出价值。
  - [Probabilistic-Programming-and-Bayesian-Methods-for-Hackers](https://github.com/CamDavidsonPilon/Probabilistic-Programming-and-Bayesian-Methods-for-Hackers): 深度讲解 ML 中的贝叶斯统计方法
  - [ML-From-Scratch](https://github.com/eriklindernoren/ML-From-Scratch): ML 算法的各种 Python 实现，旨在学习其底层原理
  - [applied-ml](https://github.com/eugeneyan/applied-ml): ML 生产环境相关的各种文章、论文、博客

AI 是如此火爆，网络上有如此多的资料（最经典的吴恩达的 Cousera 课程、Github 上的各种入门教程）、学院派的书籍、等等），以至于想学 AI 却不知从何下手。

先确定下我学习 AI 的目的：「为了兴趣，能够使用 AI 来做一些有意思的事情」。

从这个角度出发，能最快出成果的学习资料应该是：

- [动手学深度学习（Dive into Deep Learning，D2L）](https://github.com/d2l-ai/d2l-zh)

所以我应该通过这本书入门。

在入门后，如果希望更系统地学习 AI 的原理，可以再考虑其他学习资料。

### 运行环境

Jupyter provide a set of docker image: [jupyter-docker-stacks](https://jupyter-docker-stacks.readthedocs.io/en/latest/using/selecting.html)

datascience-notebook and tensorflow-notebook may be useful in this project.

## 其他

Python 分布式运行框架：

- https://github.com/ray-project/ray: 将可拆分的分布式分派到远程主机上执行，用法跟分布式压测工具 locust 很类似，非常简单。
- https://github.com/apache/superset: 最流行的数据分析面板


## 硬件

再有就是炼丹设备，去年开始 AI 大火，我也是挺感兴趣的。
现在（2023-02-17）闲鱼上 2016 年的 P4/P40 矿卡相当便宜，一张 8G 的 P4 只要 400 多，一张 24G 的 P40 只要 750，整几张搞个主机专门跑 AI，感觉会很有意思。多 GPU 炼丹相关的教程：

- [Deep Learning with Multiple GPUs - run:ai](https://www.run.ai/guides/multi-gpu)
- [Fundamentals of Deep Learning for Multi-GPUs - Nvidia](https://www.nvidia.com/en-us/training/instructor-led-workshops/fundamentals-of-deep-learning-for-multi-gpus/)

不过我手上一块 RTX3070 MAX-Q 用来跑模型好像也够用了，想了想感觉自己还是冲动了，等有需要再考虑吧（但是这么便宜的二手卡再等几个月可能就卖没了，还是得尽快学学 AI 啊）。

## 参考

- [Distinction between AI, ML, Neural Networks, Deep learning and Data mining](https://softwareengineering.stackexchange.com/questions/366996/distinction-between-ai-ml-neural-networks-deep-learning-and-data-mining)
