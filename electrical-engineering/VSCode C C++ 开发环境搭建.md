# VSCode C/C++ 开发环境搭建

VSCode 的 C/C++ 插件功能虽然全但是速度比较拉，跳转个定义卡半天，而且还经常给出一堆莫名的引用，体验极其糟糕。而 llvm 项目推出的 clangd 应用广泛，体验丝滑，直接吊打 VSCode C/C++ 插件（举个例子 Clion 就是基于 clangd 开发的）。

这里就简单介绍下如何用 clangd 搭建开发环境，其实挺简单的。

需要的工具：

- VSCode 插件
  - clangd
  - codelldb
- 依赖（直接包管理器安装就行）
  - clang
  - cmake
  - lldb
  - clangd: 这个组件可以使用系统包管理器安装，也可以由 vscode 插件自行下载安装。

环境装好后还需要一点点工作—— clang 借助 `compile_commands.json` 进行语法提示，但这个配置可不是让你手写的，有很多工具可以自动生成它：

1. 对于使用 make 的项目，可以直接使用 [rizsotto/Bear](https://github.com/rizsotto/Bear) 自动生成此文件
2. 对于使用 cmake 的项目就更简单了，cmake 原生就支持，只需要在根目录的配置文件中添加 `set(CMAKE_EXPORT_COMPILE_COMMANDS True)`
3. 其他工具的配置方法请自行搜索。

对于自定义程度较高的大型项目就得具体情况具体分析了，比如 Linux 内核其实本身就提供了生成 `compile_commands.json` 的脚本：[scripts/clang-tools/gen_compile_commands.py](https://github.com/torvalds/linux/blob/master/scripts/clang-tools/gen_compile_commands.py)


## 参考

- [几乎无痛的VSCode+clangd+lldb+cmake配置C/C++开发环境指南](https://zhuanlan.zhihu.com/p/566365173)
- [使用Clangd提升C++代码编写体验](https://zhuanlan.zhihu.com/p/566506467)

