# nushell 常用命令集锦

将图片批量转换为 webp 格式，同时缩小到 2K 宽度，质量 85:

```nu
ls *.jpg | each {|it| ffmpeg -y -i $it.name -vf scale=2000:-1 -codec libwebp -lossless 0 -quality 85  $"($it.name).webp"}
```
