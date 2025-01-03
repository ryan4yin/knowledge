# [taichi](https://github.com/taichi-dev/taichi)

一个使用 Python DSL 设计的编程语言，可运行在 GPU/CPU 上.

- 语法简单
- 无缝集成 Python 的生态，包括 numpy/pytorch
- 超简单的并行编程、可微分编程

taichi 的主要特点是性能够好，代码简单，易于编写与理解。因此主要应用场景还是物理模拟上，从
awesome-taichi 中各领域的项目数量也能很明显的看出，粗略按项目数量排序如下：

- Simlulation 的项目数量最多，包括了各种物理模拟，如流体、沙体、弹性体、布料、破碎等
- Voxel Art（体素艺术）的项目数量排第二，
  - 体素（英语：Voxel，或立体像素），是体积像素（Volume Pixel）的简称。 概念上类似二维空间的最小单
    位——像素，像素用在二维电脑图像的影像资料上。

目前感觉 taichi 更像是一个科学计算的模拟工具，也适合用来学习与实现各种物理模拟算法。简单说就是在学术
界比较有潜力，但它在产业界（如游戏、动画、工业）的应用不多见。

> 2024-09-20 更新：今天翻了一圈 taichi 的 GitHub、Blog、Zhihu、Bilibili 等各种官方渠道，发现 Taichi
> 从去年 8 月开始开发与各种其他动态全部停滞了，也没看到任何其他信息，感觉这个项目有些难以为继了...
> 然后进一步在 Zhihu 上看到胡渊鸣在 2024 年发的唯一一个帖子，是宣传 meshy.ai 图生 3D 模型的，感觉
> taichi 项目可能被放弃了，他们公司或者胡博士个人转向了 AIGC 领域。我之后也通过「胡渊鸣 meshy ai」关
> 键字搜索到了许多相关信息，基本确认 taichi 暂时不推进了（未来或许还有复活可能？毕竟还没官宣），他搞了家新公司弄 3D AIGC。

- https://www.jazzyear.com/article_info.html?id=1142
- https://x.com/YuanmingH
