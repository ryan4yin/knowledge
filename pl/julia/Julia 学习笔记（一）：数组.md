>个人向，只会记录一些需要注意的点。

### 前言

学习 Julia 已经有一段时间了，但是进步缓慢。这一方面是最近代码写得少，一方面是 Julia 学习资料少、中文资料更少，但也有我没做笔记的缘故导致学习效率不佳。

最近发现一份很不错的入门教程：[Introducing_Julia](https://zh.wikibooks.org/wiki/Introducing_Julia)，但是它的中文版本仍然有很多不足，就打算给它添加翻译和润色（[zxj5470](https://github.com/zxj5470) 完成了绝大部分翻译工作），顺便总结一份自己的笔记。

**NOTE**：Julia 的主要语言特征在于**类型系统**和**多重派发**，而主要的科学计算特征则是**矩阵**和整个标准库及生态圈。

### 一、数组

在 Julia 中，数组被用作列表（lists）、向量（vectors）、表（tables）和矩阵（matrices）。

#### 1. 数组的创建
这里尤其需要注意的是数组构造的几种方法，以及它们的区别。

#### 1.1 一维数组（vector/list）

```julia
julia> v = [1, 2, 3, 4]  # 逗号分隔的语法用于创建一维数组
4-element Array{Int64,1}:
 1
 2
 3
 4
```
向量，指列向量，Julia 使用的是 Fortran Order，各种操作都是**列优先于行**的。（和 numpy 相反，numpy 是 C Order 的，行优先于列）

#### 1.2. 二维数组（table/matrix）

```julia
julia> mat = [1 2 3 4]  # 空格分隔的语法，用于创建二维数组（或称行向量）
1×4 Array{Int64,2}:
 1  2  3  4

julia> [1 2; 3 4]  # 分号和换行符(\n)，用于分隔数组中不同的行
2×2 Array{Int64,2}:
 1  2
 3  4
```

空格对应函数 `hcat`，表示横向拼接各个矩阵/元素。
分号和换行对应函数 `vcat`，表示垂直拼接各个矩阵/元素。

下面的例子演示了拼接（空格）和单纯分隔各个元素（逗号）的区别：
```julia
julia> [1 2 [3 4] 5] # 用空格做横向拼接（或称水平拼接）
1×5 Array{Int64,2}:
 1  2  3  4  5

julia> [1, 2, [3, 4], 5] # 用逗号分隔
4-element Array{Any,1}:
 1      
 2      
  [3, 4]
 5
```
能看到在拼接操作中，`[3 4]` 被“解开”了，而用逗号时，它的行为和 Python 的 `list` 一样（区别只是 Julia 的 list 列优先）。

使用拼接需要注意的情况举例：
```julia
julia> [1 2 [3, 4] 5]  # 横向拼接要求 items 的行数相同！
ERROR: DimensionMismatch("mismatch in dimension 1 (expected 1 got 2)")
```
因为 `[3, 4]` 有两行，而 数组中的其他项是数值，显然行数不同，所以抛出了 Error.

可以想见，垂直拼接则要求 items 的列数相同。

另外当垂直拼接用于基本元素时，效果等同于逗号。（结果都是单列数组）
```julia
julia> v = [1, 2, 3, 4]
4-element Array{Int64,1}:
 1
 2
 3
 4

julia> h = [1; 2; 3; 4]
4-element Array{Int64,1}:
 1
 2
 3
 4

julia> [[1; 2]; [3, 4]]  # 等价于 [[1, 2]; [3, 4]]
4-element Array{Int64,1}:
 1
 2
 3
 4
```

#### 2. 数组的索引

数组的索引方式和 numpy 很类似。有很多高级索引方式。

这里我想说的是类似“齐次坐标”的索引特性。

首先，单个元素可以看作是零维的向量，数学上零维也可以看作是任意维，因此可以这样玩：
```julia
julia> 2[1]
2

julia> 2[1, 1]  # 被当成二维
2

julia> 2[1][1]  # 2[1] 仍然是整数 2
2

julia> 2[1, 1, 1]  # 三维
2

julia> 3.14[1]
3.14

julia> π[1, 1]
π = 3.1415926535897...

julia> '1'[1]
'1': ASCII/Unicode U+0031 (category Nd: Number, decimal digit)

julia> '1'[1, 1]
'1': ASCII/Unicode U+0031 (category Nd: Number, decimal digit)
```

多维数组也能使用类似“齐次坐标”的索引方式：
```julia
julia> m = [1 2; 3 4]
2×2 Array{Int64,2}:
 1  2
 3  4

julia> m[1][1]  # m[1] 是整数 1，这相当于 1[1]
1

julia> m[1, 1, 1]
1

julia> m[1, 1, 1, 1]
1
```

多维矩阵，在更高的维度上，也能被当成“零维”来看待，前面说过了“零维”也相当于“无限维”，所以多维数组也能用这么索引。

但是拓展的维度索引只能是 1！既然被看作“零维”，就只相当于一个点，自然不可能有更高的索引：
```julia
julia> 1[1, 2]
ERROR: BoundsError

julia> m[1, 1, 2]
ERROR: BoundsError: attempt to access 2×2 Array{Int64,2} at index [1, 1, 2]
...

julia> m[1, 1, 1, 2]
ERROR: BoundsError: attempt to access 2×2 Array{Int64,2} at index [1, 1, 1, 2]
...
```

### 3. 推导式（[comprehension](https://docs.julialang.org/en/v1/manual/arrays/#Comprehensions-1)）与生成器表达式（[generator expression](https://docs.julialang.org/en/v1/manual/arrays/#Generator-Expressions-1)）

和 Python 的列表推导式与生成器表达式很像，但是更强大——Julia 是面向矩阵的。

```julia
julia> [i+j for i in 1:3 for j in 1:3]  # 这个语法和 Python 一致
9-element Array{Int64,1}:
 2
 3
 4
 3
 4
 5
 4
 5
 6

julia> [i+j for i in 1:3, j in 1:3]  # 这个是多维的语法
3×3 Array{Int64,2}:
 2  3  4
 3  4  5
 4  5  6

julia> [i+j for i in 1:3, j in 1:3 if iseven(i+j)]  # 在后面加 guard 的情况下，结果坍缩成一维（这时两种语法结果没有差别）
5-element Array{Int64,1}:
 2
 4
 4
 4
 6

julia> [(iseven(i+j) ? 1 : 2) for i in 1:3, j in 1:3]  # 在前面做判断，因为没有过滤元素，所以仍然保持了原有结构。
3×3 Array{Int64,2}:
 1  2  1
 2  1  2
 1  2  1
```