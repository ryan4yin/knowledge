# LDTK 关卡编辑器

LDTK 是由 [Dead Cells][Dead Cells] 游戏的开发团队开源的一款关卡编辑器，支持多平台，可以用来制作 2D
关卡。

> [Dead Cells][Dead Cells] 是一款制作精良的像素风格的动作游戏，发行于 2018 年，Steam 上好评如潮。

## 教程

- 官方文档: <https://ldtk.io/docs/general/editor-components/>
- 中文快速入门教程: <https://www.bilibili.com/video/BV1y64y1z7Uw>

## 基本概念

- **World**: 世界，包含多个 Level, World 的 Layout 属性用于控制 Level 在 2D 网格上的排列方式。
- **Level**: 关卡，由多个 Layer 组成。
- **Layer**: 图层，包含 Tiles 和 Entities 以及 Enumerations 三种对象。
  - 图层有多种类型：
    - [**Tile Layer**](https://ldtk.io/docs/general/tile-layers/): 砖块图层，也是默认的图层类型，需
      要手动绘制整个地形。所有砖块都必须关联到一个具体的 Bitmap.
    - [**IntGrid Layers**](https://ldtk.io/docs/general/intgrid-layers/): 整数网格，用于标记碰撞及其
      他地形信息，或者结合 Dynamic Rules 自动生成地形。
    - [**Auto Layer**](https://ldtk.io/docs/general/auto-layers/): 自动图层，用于自动生成地形，区别
      是它只能使用来自其他 IntGrid Layer 中定义的 Dynamic Rules.
- [**Entity**](https://ldtk.io/docs/general/editor-components/entities/): 实体，可以是一个角色、一个
  物品、一个敌人等等。
  - Entity 不必包含 Bitmap 信息，也就是说它可以是无形的抽象事物，用于记录一些元信息。

## 与 Bevy 集成

这个项目使我们可以在 Bevy 中使用 LDTK 编辑的关卡：

- https://github.com/Trouv/bevy_ecs_ldtk

注意，在使用这个项目之前，你最好先了解 Bevy 的 ECS 架构以及 LDTK 的基本概念。

[Dead Cells]: https://store.steampowered.com/app/588650/Dead_Cells/
