> 今天打算花时间把 OneNote 和 EverNote 里的笔记整理一下，放到 cnblogs 里。因为我平常遇到解决过的问题
> 都习惯翻自己的博客，但是以前的很多笔记都不在 cnblogs 上，要不是今天找自己的计算机网络笔记，我几乎
> 都忘记这回事了。。。

Git 是目前最流行的分布式版本管理系统，令人痛苦的是它有点复杂，我到现在也就只记住了几个常用命令。。

## 一、配置

和大多数程序一样，Git 有两份配置文件：全局的通用配置 `/etc/gitconifg` 和用户配置 `.gitconfig`，此外
每个仓库还有一个 `.git/config` 配置，越接近仓库的配置优先级就越高。

要使用 Git，首先就需要设置一些初始信息，这些信息会被写入 `.gitconfig` 中，可以直接备份该文件，方便换
机器。

```bash
# global 表示写入用户配置 `.gitconfig` 中。还有 `--local` 表示写入仓库配置 `.git/config`
git config --global user.name "Ryan Yin"
git config --global user.email "xiaoyin_c@qq.com"

# 这样 `git l` 就能打印出清晰漂亮的 log 了
git config --global alias.l 'log --color --graph --decorate -M --pretty=format:"%h - %an, %ar : %s" --abbrev-commit -M'

# 使用 git unstage <filename> 来取消暂存
git config --global alias.unstage 'reset HEAD --'

git config --global core.editor code  # 指定默认编辑器为 vscode
```

## 二、基础

![git 文件的变化周期](https://img2018.cnblogs.com/blog/968138/201901/968138-20190122120215626-1182395661.png)

### 1. 差异比较

安装 icdiff，文档比较更清晰。

```bash
yay -S icdiff  # aur 仓库（其它 linux 可能需要手动将 `git icdiff` 添加到 PATH）
```

相关命令：

```bash
git icdiff [filename] # 查看尚未暂存的文件修改(对比 modified 与 staged)

git icdiff --staged [filename] # 查看已暂存的修改（对比 staged 与 最新的 commit）

git icdiff hash1 hash2  [filename] # 查看两个 commit 之间的差异

# 也可省略 filename 参数，这样会列出所有文件的修改
```

### 2. 标签

1. 打标签：`git tag -a v1.4 -m "version 1.4" [hash]`，在最后写上 hash 可以为过去的 comiit 打标签。
1. 删除标签：`git tag -d <tagName>`

## 三、分支

1. 创建分支：`git checkout -b <branch-name>`，这在当前 commit 上新建了一个分支，并立即切换到该新分支
   上。
1. 切换分支：`git checkout <branch-name>`
1. 合并分支：`git merge <branch-name>`：将指定分支合并到当前分支，没有冲突时会自动合并。
   - 如果有冲突，git 会在冲突文件中添加冲突内容标记，你可以通过 `git status` 查看冲突文件，解决冲突
     然后暂存提交，这个提交就会变成 merge 提交。
1. 删除分支：`git branch -d <branch-name>`

### 变基（[rebase](https://git-scm.com/book/zh/v2/Git-%E5%88%86%E6%94%AF-%E5%8F%98%E5%9F%BA)）

变基是将当前分支的一系列提交按照原有次序依次应用到另一分支上，而合并是把最终结果合在一起。两个方法整
合的最终结果所指向的快照始终是一样的，只不过提交历史不同罢了。变基主要用于得到更干净的提交历史。

假设你的仓库现在有两个分支：
![](https://img2018.cnblogs.com/blog/968138/201901/968138-20190122192832777-1038446345.png) 将
experiment merge 到 master 得到的结果如下：
![](https://img2018.cnblogs.com/blog/968138/201901/968138-20190122192927926-698975726.png) 可以看到
历史记录不是线性的，而用 `git rebase master` 将当前分支 experiment 变基到 master 得到的历史是这样
的： ![](https://img2018.cnblogs.com/blog/968138/201901/968138-20190122193228716-1645582950.png)

结果变成了线性的，虽然 c4 的修改是和 c3 同时进行的，可在历史记录上看，我们是先做了 c3 的工作，然后再
做了 c4 的工作。

推荐用法：

1. **在个人分支上，推荐只使用 rebase 而不是 merge **，因为 rebase 可以让你的提交看起来意义明确，并且
   没有无意义的 merge 其他分支的 commit。

1. 而**在主分支上， 只允许 merge 操作**，从而保证主分支的 commit 历史的完整性。**在多人开发的主分支
   上进行 rebase 操作是一件很危险的行为**，可能会把主仓库的提交历史搞得一团糟，人民群众会仇恨你，你
   的朋友和家人也会嘲笑你，唾弃你。hhh

总的原则是，只对尚未推送或分享给别人的本地修改执行变基操作清理历史，从不对已推送至别处的提交执行变基
操作，这样，你才能享受到两种方式带来的便利。

## 四、远程仓库

### 1. 配置远程仓库

如果在 Github 上参与开源项目，那你一般会有两个远程仓库：一个是你的 fork repo，一个是该开源项目本身的
repo。

从远程服务器 `clone` 下来的 repo 会自带一个名叫 `origin` 的远程仓库，`origin` 是默认的远程仓库名字，
就像 `master` 是默认的分支名称一样。但是它们并没有其他特殊意义，可以随便更改。

现在假设你 clone 你自己的 fork repo 到本地，但是很显然为了获取该开源项目的最新更新，还需要把上游的
repo 添加进来，一般给它取名叫 `upstream`

```bash
git remote add upstream git@github.com:JuliaCN/JuliaZH.jl.git
```

接下来使用 `git remote -v` 可以查看远程仓库的详细信息：

```shell
$ git remote -v
origin  git@github.com:ryan4yin/JuliaZH.jl.git (fetch)
origin  git@github.com:ryan4yin/JuliaZH.jl.git (push)
upstream        git@github.com:JuliaCN/JuliaZH.jl.git (fetch)
upstream        git@github.com:JuliaCN/JuliaZH.jl.git (push)
```

这样你的本地 repo 就有了两个远程 repo，需要的时候可以通过 `fetch` 来拉取远程 repo 的更新。

如果更换了仓库，可以用 `reset` 更改 url，也可以用 `rm` 移除某远程 repo。详情见 `git remote --help`

### 2. 与远程仓库交互

1. 拉取更新：
   1. `git fetch origin master` 从远程仓库 origin 的 master 分支获取更新（这会在本地新建更新分支
      `origin/master`）
   1. `git fetch --all`：一次从所有远程仓库的所有分支拉取更新
   1. `git pull origin master`：将远程仓库 origin 的 mater 分支 **merge** 到当前分支，是 `git fetch`
      和 `git merge` 的缩写。
   1. `git pull --rebase origin master`：将远程仓库 origin 的 master 分支 **rebase** 到当前分
      支，`git fetch` 和 `git rebase` 的缩写。
1. 推送到远程 repo：
   1. `git push origin master`: 将本地的 master 分支推送到 origin 仓库
   1. `git push origin v1.4`：将 v1.4 标签推送到 origin 仓库
   1. `git push origin --tags`：推送所有标签到 origin 仓库
1. 删除远程分支、标签
   1. `git push origin --delete <branchName>`
   1. `git push <remote> :refs/tags/<tagname>`

Note：远程分支的名字为 `仓库名/分支名`，如 `origin/master` 就是 origin 仓库的 master 分支名。可以直
接 `checkout` 出远程分支，但是这会使仓库处于“分离头指针”状态。（该状态下所有提交都不会属于任何分
支。。）

## 五、.gitignore

gitignore 使用标准的 glob 模式匹配，也就是 shell 所使用的简化正则表达式。

```gitignore
# 忽略任何 .a 或 .o 结尾的文件（因为默认是递归在所有目录内匹配！）
# * 匹配任意个字符，包括空格
*.[ao]

# 叹号开头表示不要忽略这个文件！
# 因为上面忽略了 所有 .a 文件，需要使用这个更 specific 的定义来跟踪 lib.a
!lib.a

# 使用 / 开头防止递归匹配，这是只忽略当前目录下的 TODO 文件
/TODO

# 使用 xxx/ 表示该路径是一个目录
# 忽略任何 build/ 目录
build/

# 忽略 doc 文件夹内的任何 txt 文件
# 但是不递归匹配内层目录中的 txt 文件！
doc/*.txt

# 忽略 doc 目录下的所有 pdf 文件
# 使用 ** 表示任意层中间目录，因此这会递归忽略子目录内的 pdf
doc/**/*.pdf
```

可以在 [github/gitignore](https://github.com/github/gitignore/blob/master/C.gitignore) 上找到各语言/
工具的 gitignore 模板，另外在 github 上新建 repo 时也可以直接选择 gitignore 模板。

## 六、Git 的各种撤销姿势

1. 取消跟踪：不小心 `add` 了不需要的文件或文件夹到暂存区，可以使用 `git rm --cached <filename>` 来取
   消跟踪（`--cached` 表示不要删除原文件）。
1. 修改上一次提交的 commit message：先 `add` 上次提交的修正版本，然后运行
   `git commit --amend`。amend 是“修正”的意思，表示这个 commit 是上一次的修正，它应该覆盖上一个
   commit。（也可用于修改上一次提交的 message）
1. 修改多条提交的 commit message:
   1. `git rebase --interactive $parent_of_flawed_commit`: 交互式修改自 parent commit 依赖的所有提
      交。会弹出一个 vim 界面。
   1. 在 vim 中将需要修改的 commits 行首的 `pick` 修改成 `reword`，表示要修改它的 commit message，通
      过 `:wq` 保存。
   1. 接下来 git 会依次弹出 commit 消息的修改界面（vim），并且下方的注释中还带有文件变动消息。修改
      commit message 后保存。
   1. 全部修改完成后，修改结束。
1. 取消暂存：有时我们会想将已经暂存的文件分多次提交以得到更清晰的提交历史，这需要先取消暂存其中的一
   部分文件。`git reset HEAD <file>` 就是用来干这个事的。（看不懂没关系，有用就行。。。）
1. 撤销未暂存的修改：`git checkout -- <filename>`，直接签出最新一次 commit 里的该文件。当前文件会直
   接被覆盖掉！
1. 回滚/还原某个文件/文件夹：`git checkout [<branch> / <commit id>] [<file path>]`，从指定的 commit
   中签出文件，当前文件会被覆盖掉。
1. 使整个仓库切换到某个提交（只能用于查看历史数据）：`git reset --hard <commit-hash>`
1. 将仓库的所有内容退回到某个提交，但是不回退提交记录：`git checkout <commit-hash> -- .`
   1. 然后重新 `git add . && git commit -m "revert: revert back to old version"`

### Git Revert cherry-pick

待续

## 七、最佳实践

### 1. git commit 的注释

简单的提交可以直接用 `git commit -m "该 commit 的信息"`，而需要详细说明的 commit（比如完成了阶段性的
任务时），建议直接 `git commit`，然后在打开的文本编辑器中书写。

此外，最好使用统一的格式书写 commit 信息，例如 "[模块名]:动词 操作对象"，更详细的信息换行后再写。

1. 常用的动词：add、update、fix、change、remove/delete、finish 等
1. 操作对象：某文件、feature、bug、todo、api、doc 等

### 2. 用远程分支覆盖本地记录

也就是清除本地的所有修改

```bash
git fetch --all
git reset --hard origin/master  # 这里换成你的远程分支
git pull origin master  # 将远程仓库 origin 的 mater 分支 **merge** 到当前分支（fast-forward）
```

## 八、Git 的错误使用方式及补救方法

1. **存放大文件**：代码库中最好不要添加大文件，这会使仓库大小剧增。而且一旦提交，删除起来还很麻烦。

## 核武器级提交历史改写工具 - filter-branch

> 以及一个辅助工具： https://github.com/rtyley/bfg-repo-cleaner

它可以修改历史中的大量 commits，包括 commit 的文件、提交者、提交信息！危险且强大。

最好只在个人分支上干这件事，否则你的合作者尝试提交时，会出现大量的冲突。。。

### 从每一个提交移除一个文件

这经常发生。 有人粗心地通过 git add . 提交了一个巨大的二进制文件，你想要从所有地方删除它。 可能偶然
地提交了一个包括一个密码的文件，然而你想要开源项目。 filter-branch 是一个可能会用来擦洗整个提交历史
的工具。 为了从整个提交历史（当前分支）中移除一个叫做 passwords.txt 的文件，可以使用 --tree-filter
选项给 filter-branch：

```shell
$ git filter-branch --tree-filter 'rm -f passwords.txt' HEAD --prune-empty
Rewrite 6b9b3cf04e7c5686a9cb838c3f36a8cb6a0fc2bd (21/21)
Ref 'refs/heads/master' was rewritten
```

`--tree-filter` 选项在检出项目的每一个提交后，在文件树根目录运行指定的命令然后重新提交结果。 在本例
中，你从每一个快照中移除了一个叫作 passwords.txt 的文件，无论它是否存在。

也可以使用 `--index-filter`，它以 Git 索引为操作对象（而不是文件树），它比 `--tree-filter` 快很多。
经常与 `git rm -rf --cached --ignore-unmatch` 一起用：

```bash
git filter-branch --force --index-filter 'git rm -rf --cached --ignore-unmatch <要删除的文件>' --prune-empty --tag-name-filter cat --
```

通常一个好的想法是在一个测试分支中运行 filter-branch，然后当你决定最终结果是真正想要的，再硬重置
master 分支。 为了让 `filter-branch` 在所有分支上运行，可以给命令传递 `--all` 选项。

### 从每一个提交中删除掉的特定字符串

假如你在某次提交中不小心把密码等敏感信息写到了某文件里，格式如下：

```python
username = "ryan"
password="56224"
```

你可以通过 filter-branch 将这些敏感信息替换掉：

```bash
git filter-branch --tree-filter "sed -i 's/56224//g' <filename>"  # 将 56224 替换为空（删除）
```

如果多个py文件都存在该密码，可以使用：

```bash
git filter-branch --tree-filter "find . -name '*.py' -exec sed -i -e \
    's/56224//g' {} \;"
```

更复杂的操作，用 [bfg-repo-cleaner](https://github.com/rtyley/bfg-repo-cleaner) 是更好的选择。

**需要注意的是，上述操作完成之后，被修改的那些数据只是“隐形”了，但没有被物理删除！！！要彻底清除，请
继续看下一小节**

## 九、彻底的删除掉某些提交

假如你在某次提交中不小心把密码等敏感信息写到了代码文件里，现在你需要撤销该提交。

只使用 `git reset --hard` 或者 `git commit --amend` 是不行的，因为“使用 git 你总有后悔药可吃”，仍然
可以通过 `git reflog` 看到被丢弃的 commit，然后通过 `git reset --hard <commit-hash>` 来切换到该提
交，从而得到相关的敏感信息。

在 `reset` 或者 `--amend` 后，你还需要清除掉 reflog 中相关的记录。方法如下：

```
git reflog expire --expire-unreachable=now --all  # 删除所有没有被当前分支引用的 reflog
git gc --prune=now  # 立即 gc 掉所有没有被引用的 commits
```

HEAD 是当前分支引用的指针，它总是指向该分支上的最后一次提交。 这表示 HEAD 将是下一次提交的父结点。通
常，理解 HEAD 的最简方式，就是将它看做 你的上一次提交 的快照。

如果你 `git reset --hard <commit-hash>` 到以前的提交，那该提交之后的所有内容都会被丢弃。（它们将只能
在 reflog 中找到了）

而 reflog 会记录 HEAD 的所有更改历史，只要某 commit 仍然被 reflog 引用，它就不会丢失，而且随时可以还
原。

## 十、子模块（据说很难用）

有时候，我们需要使用到一些包，而这些包可能并没有上传到语言的中央仓库（比如 Python 的 pypi，Rust 的
crate.io，Java 的 maven central 等）。或者这个包在中央仓库里有，但是我们需要对它做一些定制。

从中央仓库下载的依赖的话，我们基本无法对它做什么修改。而如果直接把包的内容拷贝过来，上游代码更新了的
话，我们就必须手动从上游 copy 代码，必须重新对新代码做第二遍修改——相信我，这相当痛苦。

Git 提供了子模块的功能来解决这个问题。

假设你现在要把一个项目添加到你的依赖中，而且你既想保持你自己的变更，又要延续上游的变更。首先你要把外
部的仓库克隆到你的子目录中。你通过 `git submodule add` 将外部项目加为子模块：

```shell
$ git submodule add git@github.com:coding-and-typing/xhup-club-api.git
正克隆到 '/home/ryan/Codes/testt/xhup-club-api'...
remote: Enumerating objects: 114, done.
remote: Counting objects: 100% (114/114), done.
remote: Compressing objects: 100% (76/76), done.
remote: Total 800 (delta 53), reused 90 (delta 38), pack-reused 686
接收对象中: 100% (800/800), 257.03 KiB | 87.00 KiB/s, 完成.
处理 delta 中: 100% (439/439), 完成.

# 然后用 git status 就会发现，多了个 .gitmodules 配置文件
$ git status
位于分支 master
要提交的变更：
  （使用 "git reset HEAD <文件>..." 以取消暂存）

        新文件：   .gitmodules
        新文件：   xhup-club-api
```

子模块在 Github 上会显示为一个类似引用的文件夹，它链接到对应的 git 地址。

其他常用的子模块命令：

```shell
# 等同于在所有子模块文件夹中先跑 git init 再跑 git update
git submodule update --init --recursive
# 在每个子模块文件夹中执行一段 shell 脚本，这里的命令是用于重置子模块状态
git submodule foreach 'git fetch origin; git checkout $(git rev-parse --abbrev-ref HEAD); git reset --hard origin/$(git rev-parse --abbrev-ref HEAD); git submodule update --recursive; git clean -dfx'
```

详见 [子模块](https://git-scm.com/book/zh/v1/Git-%E5%B7%A5%E5%85%B7-%E5%AD%90%E6%A8%A1%E5%9D%97)

## 十一、Git Hooks

和其它版本控制系统一样，Git 能在特定的重要动作发生时触发自定义脚本。 有两组这样的钩子：客户端的和服
务器端的。 客户端钩子由诸如提交和合并这样的操作所调用，而服务器端钩子作用于诸如接收被推送的提交这样
的联网操作。 你可以随心所欲地运用这些钩子。

服务端的钩子，如果你使用过 Github App，Travis-CI、Codacy 就都是通过服务端钩子，来获取最新的 commit
的。常用于持续集成、自动部署。而客户端钩子，同样也能用于持续集成、自动部署。如果是一个个人项目，直接
通过客户端钩子来自动测试部署，更方便。

详见
[Git 钩子](https://git-scm.com/book/zh/v2/%E8%87%AA%E5%AE%9A%E4%B9%89-Git-Git-%E9%92%A9%E5%AD%90)

## 十二、Git 旧分支清理

在日常使用时，我们可能会创建很多分支，而且有些分支可能已经不再使用了。

对于较少的分支，我们可以直接使用如下命令来删除：

```bash
# 查询有哪些本地分支
git branch
# 删除本地已合并到当前 HEAD 的分支
git branch -d <branch-name>
# 删除本地未合并到当前 HEAD 的分支
git branch -D <branch-name>

# 查询有哪些远程分支
git branch -r

# 删除远程分支
git push origin --delete <branch-name>
```

而如果本地或者远程已经有了很多遗留分支，就需要查询分析下哪些分支是可以删除的。

```bash
# 列出所有已经合并到当前 HEAD 主线分支的其他分支
git branch --merged

# 删除所有已经合并到当前 HEAD 主线分支的其他分支（master 和 dev 分支除外）
git branch --merged | egrep -v "(^\*|master|dev)" | xargs git branch -d

# 列出所有没有合并到当前 HEAD 主线分支的其他分支
git branch --no-merged

# 未合并的分支直接删除有风险，建议一个个手动删除
git branch -D <branch-name>
```

以及一些跟踪远程分支的本地分支处理：

```bash
# 列出所有对应的远程分支已经不存在的本地分支（也可将 origin 换成别的 remote 名称）
git remote prune origin --dry-run

# 去掉 --dry-run 参数，真正删除对应的本地分支
git remote prune origin
```

再有是一些远程分支的处理（这个也可以直接在 GitLab/GitHub 提供的 Web 页面上做）：

```bash
# 删除掉远程已经被合并到当前 HEAD 主线分支的其他分支（master 和 dev 分支除外）
git branch -r --merged | egrep -v "(^\*|master|dev)" | sed 's/origin\///' | xargs -n 1 git push origin --delete
```

## 其他可能用到的 Git 命令

```
# 查看某文件（不论当前是否还存在）的所有提交记录
git log -- <file-path>

# 查看某文件的最新一次提交记录，并显示该 commit 的具体 status
# 如果文件已经不存在，那就是被删除的 git commit
git log -1 --stat -- <file-path>
```

## 参考

- [Pro Git](https://git-scm.com/book/zh/v2)
- [Git-工具-重写历史 - Pro Git](https://git-scm.com/book/zh/v2/Git-工具-重写历史)
- [Git-工具- reset 揭密](https://git-scm.com/book/zh/v2/Git-%E5%B7%A5%E5%85%B7-%E9%87%8D%E7%BD%AE%E6%8F%AD%E5%AF%86)
- [Git工作流的最佳实践](https://zhuanlan.zhihu.com/p/26216630)
- [Commit message 和 Change log 编写指南 - 阮一峰](http://www.ruanyifeng.com/blog/2016/01/commit_message_change_log.html)
- [How to substitute text from files in git history?](https://stackoverflow.com/questions/4110652/how-to-substitute-text-from-files-in-git-history)
