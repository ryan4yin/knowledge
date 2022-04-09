# 图形学

>暂时不考虑 2D，因为目前没兴趣...

说是图形学，其实主要还是业余玩玩啦，会首先从简单的引擎使用学起，需要的时候才会深入学习引擎的原理。

最知名的两个图形学引擎，尤其是 3D 图形学引擎，目前来说就两个：

- Unreal Engine 5: 顶级画质与体验，但是更复杂
    - 游戏开发、建筑可视化、影视制作，都是 Unreal 的目标场景
    - 主要只支持两种编程手段：C++ 与蓝图
    - C++ 语言本身就比较复杂，同时 UE5 还引入了非常多它自定义的宏，学习难度较高
    - 蓝图是一个通过拖拽实现的开发工具，底层会编译成 C++ 因此性能很高，但问题是它是二进制格式，无法使用 Git 仓库存储，而且编程步骤会比直接用 C++ 繁琐很多。
    - 开源引擎
- Unity3D: 简单易学，可以快速上手，画面跟 3A 相比一般，但是用于制作一些写意的 3D 动画或游戏是完全够用的。
    - 主要支持使用 C#/lua 两种语言
    - 闭源，不过个人版有免费授权

此外就是建模、材质工具、布料解算、骨骼模拟等专用工具了，其中最出名的是开源工具 Blender.

>2022-04-10最近突然想学学游戏引擎，原因是手边有台 Quest 2 VR 头显吃灰有一阵了，想拿来搞搞 VR 开发，另外还想自己制作些超高画质（4k/6k/8k）的 MMD 动画放 VR 里看。


## 业余爱好者的 VR 开发与 VR 动画制作学习路线

先罗列下我的需求：

- 需要支持 Quest 2 跟 SteamVR
    - Unreal 跟 Unity3D 都支持
- 画质一定要高，就是想体验下极致的画质
    - 如果是纪念碑谷这类写意风格的话，Unity3D 就完全足够了
    - 如果是 3A 游戏或者 MMD 布料解算这类写实风格的话，就需要 Unreal/Blender 才能提供足够的画质
- 学习难度不能太高
    - 淘汰 Unreal C++ 编程，只有蓝图可选了
- 快糙狠，需要能快速出成果
    - Unity3D 跟 Unreal 蓝图应该都能达成这个目标

综合来看，感觉学一学 Unreal Engine 的蓝图是最优的选项，画质够高，学习难度也低，应该也能快速出成果。

学习方法的话，一是直接看官方文档，二是找找官方及社区的 Youtube 视频教程吧。

后面技能提升了，有兴趣或者有需要，再深入学习计算机图形学以及 3D 引擎的原理（着色器、）吧。

那么总结一下学习路线：

1. 学习 UE5 基础知识
    - 官方文档：<https://docs.unrealengine.com/5.0/zh-CN/>
    - 社区视频教程：
        - Youtube 上最火的 UE5 视频 [Unreal Engine 5 Beginner Tutorial - UE5 Starter Course!](https://www.youtube.com/watch?v=gQmiqmxJMtA): 长达 5 个小时的 UE5 教学视频，手把手教学。
        - 其他看着还不错的教学视频
            - https://www.youtube.com/watch?v=ptCN4cysDig
            - https://www.youtube.com/watch?v=e-nENnVVtJA
    - [UE5 的 VR 编辑模式](https://docs.unrealengine.com/5.0/zh-CN/vr-mode-in-unreal-editor/): 直接带上头盔，在 VR 世界进行游戏/动画的制作
    - 交互式 XR 场景动画：好处是可以实时交互，甚至可以移动
        - 可以对接 SteamVR 或者 Oculus，借助 UE5 可实现高质量的实时渲染
    - VR 视频制作：不可交互，但好处是可以通过长时间渲染达成极高画质，比如使用 1h 来渲染一个 3mins 的视频
        - [Unreal Engine for 360° VR & ArchViz Virtual Tour Video In-depth Tutorial | Oculus TV + YouTube VR](https://www.youtube.com/watch?v=TLHyMwQ0bo0)
2. blender 基础
    - [Blender 2.9-3.1黑铁骑士Ⅱ系统零基础入门教程](https://www.bilibili.com/video/BV1zh411Y7LX)
3. MMD 二次元老婆模型、动作、场景资源
    - [模型屋 - 大量正版二次元老婆模型、动作](https://www.aplaybox.com/)
    - [永昼UE】免费UE教程#01 PMX模型导入虚幻引擎5教程以及为什么这么做](https://www.bilibili.com/video/BV1uL411c7HH)

学这么多目的是啥？当然是用 VR 看二次元老婆跳舞啊，而且要最好的素材跟渲染画质，自己动手丰衣足食。

## 参考

- [虚幻引擎 5 现已正式推出，是否是使用新版引擎开发游戏的好时机呢？ - 知乎](https://www.zhihu.com/question/526248363/answer/2426839028)
