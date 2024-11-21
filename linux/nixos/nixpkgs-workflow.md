# Nixpkgs 工作流

## 为什么 nixos-unstable 有时候会有包构建失败?

如果是 CI 构建成功, 但本地使用有问题, 那还比较好理解: 可能是本地使用的文件系统或别的环境区别导致的问
题.

但如果 CI 本身就失败了, 为什么还会进到 unstable 呢?

在 NixOS 中文群跟几位维护者讨论了一下, nixpkgs 的工作流大概是这样:

1. 针对普通的 PR, 一般都会要求相关的所有包都能正常编译, 并且测试都能通过, 才会合并.
2. 但在升级一些比较核心的包(比如 gcc/llm/rust, libc, kernel, etc)时, 因为可能会涉及到非常多依赖它们
   的包, 要求PR 作者修复所有构建失败的包常常是不现实的. 这时候, 会有两种方式:
   1. 如果构建失败的包比较老, 而且数量不多, 可能会先合并 PR, 然后等待相关的 maintainer 提 PR 修复.
      - 一些比较老的包可能会经常因为构建失败而阻塞各种其依赖项的更新 PR, 因此甚至有些极端的想法是,
        如果一个包在 unstable 上两三周没人修, 就直接标记为 borken, 进而删除.
      - 目前如果一个包因为依赖更新而构建失败, 对应的 maintainer 是收不到提醒的, 他需要自己主动更新
        nixpkgs 并修复问题.
   1. 如果构建失败的包太多, 或者涉及比较核心的依赖, 会先合并到 staging-next 分支, 然后等待其他
      maintainer 一起修复问题, 等修复了大部分问题后, 才会合并到 unstable 分支.

在自动工作流中, 会阻塞 master 分支被自动合并到 unstable 分支的包只有这个页面中所列的这些, 只有几十个
包: [nixpkgs:trunk:unstable](https://hydra.nixos.org/job/nixpkgs/trunk/unstable#tabs-constituents)

除了自动工作流的阻塞外, 有时候一些 PR 在人工判断为不适合立即合并到 unstable 时, 也会先被合并到
staging-next. 注意为了保证这几个分支的一致性, 当用到 staging-next 修复大量构建问题时, 常常也会同时阻
塞 unstable 分支的更新. 这个阻塞时间可能持续数天到好几周.

## 为什么 arch / fedora 这类滚动发行版很少出现类似 nixos 这种构建失败的问题?

> https://wiki.archlinux.org/title/Official_repositories

目前看到的一些可能的原因:

1. arch 的核心包数量相对较少, 那维护团队就有余力去保证所有包都能正常构建.
2. arch 的包仓库分级更细致, 有 core, extra, community, multilib 等等, 这样可以按照重要性来保证构建的
   稳定性, 从而保证了系统的稳定性.
3. arch 官方维护的包数量， 跟 nixpkgs 中的包数量不是一个数量级的.
4. arch 的包仓库都还有一个 testing 分支, 用于测试新的包, 这进一步保证了问题在进入正式仓库前就能被发
   现并解决.

而 AUR 的包, 其稳定性则依赖于相关的社区维护者.

总的来看, nixpkgs 的 unstable 分支在设计上就是允许非核心包构建失败的, nixpkgs 也期待 package
maintainer 在在 unstable 上主动发现自己的包有问题, 并且主动提 PR 修复. 这个 unstable 分支的功能介于
arch 的 xxx-testing 与正式仓库之间.

而 arch 应该总是能确保所有 core 与 extra 包都能正常构建(问题都应该在 xxx-testing 仓库解决), 因此其稳
定性会比 nixpkgs 的 unstable 分支更高.


为了兼顾稳定性与版本够新, 一般推荐默认使用 stable 分支, 对需要新版本的软件, 再单独从 unstable 分支引入.

这样做的缺点是, 相比 arch linux, 系统的各软件版本可能会比较滞后.



## 吐槽 - 经常有人提 PR 把 unstable 搞坏, 而且还不愿意修复?

nixpkgs 现在这个局面就是它的架构跟工作流设计导致的，跟某个个人没有关系。

nixpkgs 感觉相当于 arch + AUR，导致很多 maintainer 对一些比较老的包不感冒，毕竟都不知道还有没有人在用。

打个比较, python maintainer 就只想维护 python 自身，并希望被破坏掉的其他依赖，由相关的 maintainer 自己修。

如果是在 arch 上, 那至少 python 的更新在相关的其他 core/extra 包都能正常构建后才会被合并到正式仓库。
但在 NixOS 上, 它就直接被自动 merge 到 unstable 分支了, 导致稳定性欠佳.

之前也有人提过为什么 nixpkgs 不像 arch 那样多加个 extra 维护级别跟 testing 分支呢?
不这么干的主要原因可能是: 人手与资源都不够, 多加一个分支就意味着多维护一个分支、多一堆 CI 构建、多一分 s3 cache 存储.

另外当前的 monorepo + git 工作流可能会成为瓶颈, 拖慢了一个包的更新 PR 从合并到 master 到进入 unstable 的时间.




