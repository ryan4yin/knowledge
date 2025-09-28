# Nushell

## 目前踩过的坑

- [Nushell is printing (or asking to print) escape sequences](https://github.com/nushell/nushell/issues/11950)
  - 偶尔会突然打印一堆乱码，很烦
- [Make it possible to run nushell printing each executed command](https://github.com/nushell/nushell/issues/10037)
  - 没有类似 bash `set -x` 的调试模式，调用外部命令时无法打印出执行的命令。这个在调试的时候非常头疼
- rm 的实现跟系统的 rm 也有细微的区别，偶尔会遇到 rm 报错但是用 `^rm` 就正常的情况。
  - 可能相关的 issue
    - https://github.com/nushell/nushell/issues/10447

## nushell 常用命令集锦

将图片批量转换为 webp 格式，同时缩小到 2K 宽度，质量 85:

```nu
ls *.jpg | each {|it| ffmpeg -y -i $it.name -vf scale=2000:-1 -codec libwebp -lossless 0 -quality 85  $"($it.name).webp"}
```
