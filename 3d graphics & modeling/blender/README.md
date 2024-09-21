# Blender

## 学习路线

我的学习目标：

1. 创建、修改些简单的 3D/2D 游戏资产
1. 制作与渲染 MMD 动画

当前制定的学习路线：

1. 花 20 分钟快速了解 Blender 的基础操作与 UI 界面
1. 花几个小时学习桌子椅子杯子、甜甜圈等简单物体的建模、材质到渲染静态图像的全流程
   1. 这个过程中你会逐渐熟悉 Blender 的大部分入门操作与概念，类似点线面的概念、编辑模式（几项高级操
      作：挤出、切割、焊接）、对象模式（平滑、细分）、材质、光照、渲染等。
1. 学习动画与运动
   1. 了解关键帧、动画曲线、动画编辑器、骨骼绑定、衣服绑定等概念
   1. 了解物理模拟、碰撞检测等概念
1. 学习材质与纹理
   1. 了解材质、纹理、UV 映射、法线贴图、置换贴图等概念
   1. 了解 PBR 材质、节点编辑器等概念
1. 探索 AI 与 Python 自动化工作流程
   1. 雕刻：雕刻模式、雕刻笔刷、雕刻纹理等
   1. 2D 动画制作：油蜡笔之类的
   1. 使用 AI 生成 Python 代码
   1. AI 生成 3D 模型：
      - [TripoSR](https://github.com/VAST-AI-Research/TripoSR): 从图片生成 3D 模型
        - 对应的商业服务：<https://www.tripo3d.ai/>，生成的模型能自带 PBR 材质，行业一流水准。
      - [InstantMesh](https://github.com/TencentARC/InstantMesh): 腾讯家的，同样是图生 3D 模型
      - [meshy.ai](https://www.meshy.ai): taichi 胡渊鸣团队整的，主做文生 3D，但也在探索图生 3D、自
        动绑定骨骼等功能。
      - 根据 Youtube 上搜到的一些对比视频，图生 3D 领域 Tripo AI 做得最好，但 2024 年 8 月 Meshy AI
        大更新后它的图生 3D 也有了很大进步。
   1. AI 生成图片、视频（优势是这些插件能跟 Blender 直接交互）：
      - [ComfyUI-BlenderAI-node](https://github.com/AIGODLIKE/ComfyUI-BlenderAI-node): 由国内知名
        Blender 布道师只剩一瓶辣椒酱发起的社区以及插件项目。的插件，辣椒酱 23 年开始做了大量相关的视
        频。辣椒酱还配套录制了一系列教程视频
        [合集·ComfyUI大冒险](https://space.bilibili.com/35723238/channel/collectiondetail?sid=1320931)
        以及插件模型整合包。因为 ComfyUI 原生支持视频，所以这个插件貌似也支持视频。
      - https://github.com/carson-katri/dream-textures
        - 这个视频比较好地介绍了这个插件的功
          能：[Dream Textures is INSANE](https://www.youtube.com/watch?v=4kmdyNavuvs)，缺点是只支持
          图片，搞视频比较麻烦。
1. 很明显未来 3D 建模的主流会是 AI 自动生成，因此这个阶段的目标是熟悉 Blender 的各种概念与用法，会用
   即可，不需要熟练掌握各种艰深的技巧。

> 目前最潮的工作流：使用 Flux 生成图片，再通过 tripo/meshy 生成 3D 模型，再导入 Blender 进行渲染。

学习资料：

- 官方资料索引: https://www.blender.org/support/
- [90 分钟快速上手 Blender](https://www.bilibili.com/video/BV1kX4y1m7G5/)
- [Blender 4.0 Beginner Donut Tutorial (NEW) - Blender Guru](https://www.youtube.com/playlist?list=PLjEaoINr3zgEPv5y--4MKpciLaoQYZB1Z)
- [只剩一瓶辣椒酱](https://space.bilibili.com/35723238): 国内最知名的 Blender 布道师，他的 B 站视频
  被众多人称为 Blender 字典。

## 基础快捷键

> 注意：下列内容中的 Numpad 表示数字小键盘区，主键盘区的这些键有其他功能（譬如 1 2 3 分别在点线面三
> 种编辑模式间进行切换）。但如果你没有数字小键盘，可以通过 `编辑 -> 偏好设置 -> 输入` 中的
> `模拟数字键盘` 选项来将主键盘区的这些键映射到数字小键盘区。

先说明下格式：

- `A - B` 表示按住 A 键不放，然后按 B 键，最后同时松开 A 键和 B 键。
- `A + B` 表示先点击 A 键（并放开），然后点击 B 键。

- 场景视图调整
  - 场景位移：Shift - 按住鼠标中键（滚轮）拖动
  - 场景旋转：按住鼠标中键（滚轮）拖动
  - 场景缩放：滚动鼠标滚轮
- 其他视图调整
  - 视图切换：Numpad 1/3/7
    - 或者也可以通过右上角的 XYZ 轴按钮来切换视图，更直观但不如快捷键方便
  - 透视/正交切换：Numpad 5
  - 最大化显示当前物体：Numpad .（小数点）
  - 单独显示当前物体（隐藏其他所有物体）：/（正斜线）
- 物体操作（不区分大小写）
  - 移动（Grab）：G
    - 向某个轴移动：G + X/Y/Z
    - 未确认操作前，你可以通过 X/Y/Z 切换移动轴进行多次移动，下面的旋转缩放也是一样。
    - 重复按 X/Y/Z 可以从全局坐标系切换到物体坐标系
  - 旋转（Rotate）：R
    - 绕某个轴旋转：R + X/Y/Z
  - 缩放（Scale）：S
    - 沿某个轴缩放：S + X/Y/Z
  - 复制：Shift - D
  - 删除：X
  - 重复上一次操作：Shift - R
  - 重复上一次操作的次数：Ctrl - R

其他功能大都可以在编辑窗口的左侧以及顶部的工具烂中找到，新手可以先直接使用这些工具栏的按钮来操作，等
熟悉了之后再逐渐转向快捷键操作。

### 基础快捷键第二部分

稍微复杂一点的快捷键：

- 在不同模式间切换：Ctrl - Tab，再根据提示按下快捷键或鼠标
- 直接使用 Tab 键可以在对象模式和编辑模式间切换
- 切换透视模式：Alt + Z
- 倒角：Ctrl - B
- 环切并滑移：先确保你未选中任何物体，按 Ctrl - R，然后鼠标选中某个环面，再滑动鼠标选择环切的位置
- 在当前「面」中插入新「面」：I，然后拖动鼠标
- 挤出并移动：E
- 在当前两条边之间生成封闭「面」：F
