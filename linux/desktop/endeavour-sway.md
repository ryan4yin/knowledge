# Endeavour Sway 使用记录

sway 是 i3wm 的替代品，区别在于它基于 Wayland 而不是 X11，所以它的性能更好。

目前看到网上的一些说法都表明，sway 要比 i3wm 更流畅，对多显示器不同分辨率的支持也非常好。

>x11 对多显示器的支持一直都不好，不能多屏不同的 scale 比例，这也是促使我想换到 wayland 的主要动力。

另一方面 wayland 开发跟积极，而 x11 早就没啥人维护了，所以 sway 基本可以说是确定的未来。

但尴尬的是我用的是 Nvidia 显卡，而且为了玩 AI 我还装了 Nvidia 闭源驱动，而 sway 官方不支持 Nvidia 闭源驱动，必须添加 `--unsupported-gpu` 参数才能正常启动 sway...

wlroots 0.16 开始，Wayland Vulkan API 比较稳定了，这使得 sway 可以使用 vulkan 来渲染窗口，使用 Nvidia 闭源驱动渲染也成为可能。


TODO

## 参考

- [探索linux桌面全面wayland化（基于swaywm）](https://zhuanlan.zhihu.com/p/462322143)

