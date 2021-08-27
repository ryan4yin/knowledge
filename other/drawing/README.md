# 程序员如何绘图？

## 一、UML 图介绍

- [UML图 - 百度百科](https://baike.baidu.com/item/UML%E5%9B%BE)
- [UML基础 - 统一建模语言简介](https://www.ibm.com/developerworks/cn/rational/r-uml/index.html)
- [UML 各种图总结](https://www.cnblogs.com/jiangds/p/6596595.html)

## 二、绘图工具与语言

### 1. 制作普通图表

- [在线绘图 - processon](https://www.processon.com/)
- <https://draw.io>: 最流行的网页绘图工具之一，有对应的 vscode 插件。
- [excalidraw](https://github.com/excalidraw/excalidraw): 手绘风格的作图工具，画出来的图很好看。

此外，如果你是一个学过点UI设计的程序员，不妨考虑直接用 [Figma](https://www.figma.com/) 画图，优点就是自定义程度相当高，缺点就是门槛高咯。

### 2. 通过编程自动生成图标

- [Markdown 嵌入绘图语言 - mermaid](https://github.com/mermaid-js/mermaid)：适合自己写文档时，直接通过在 IDE 里绘图。（适合手写）
- [graphviz 的 dot 绘图语言](https://www.graphviz.org/doc/info/lang.html): 这项语言适合通过程序自动生成，比如扫描后端 API Routers 生成 DOT 语言描述，这样就能可视化 API 结构树；又或者扫描生成后端依赖树的 DOT 语言描述。


### 3. 绘制 ASCII 图表

- [asciiflow](https://github.com/lewish/asciiflow): 通过网页在线绘制 ASCII 图表
- [vscode-asciiflow2](https://github.com/zenghongtu/vscode-asciiflow2): 在 vscode 中用鼠标画 ascii 图，非常棒的插件。
- [vim-boxdraw](https://github.com/gyim/vim-boxdraw): 如果你比较喜欢使用 vim，这是 vim 的 ascii 画图插件，不需要使用鼠标。

## 思维导图

XMind 是目前最流行的思维导图工具。

## 专用绘图工具

- [mingrammer/diagrams](https://github.com/mingrammer/diagrams): 通过 python 语言描述云端系统结构。


## 其他

- [slidev](https://github.com/slidevjs/slidev): 程序员的 PPT 工具
