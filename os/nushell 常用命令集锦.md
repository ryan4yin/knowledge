# nushell 常用命令集锦

将大于 10kib 的 png 图片全部转换为 webp 图片，并执行全文替换：

```nu
# 批量将所有 png 文件转换成 webp 文件以缩小体积，并全文替换 markdown 中的图片名称

let png_paths = (ls **/*.png | each {|it| $it.name})
$png_paths | to md | save --raw ./png_paths.txt

def png_to_webp [png_path: string] {
  let webp_path = ($png_path | split row '.png' | append ".webp" | str collect)
  ffmpeg -y -i $png_path -c:v libwebp $webp_path
  rm $png_path
}

def replace_png_with_webp [png_path: string] {
  let webp_path = ($png_path | split row '.png' | append ".webp" | str collect)
  let png_name = ($png_path | path basename)
  let webp_name = ($webp_path | path basename)
  let cmd = $"gsed -ri 's/($png_name)/($webp_name)/g' `find . -name "*.md"`"
  echo $cmd
  bash -c $cmd
}

$png_paths | each { |it| png_to_webp $it }
$png_paths | each { |it| replace_png_with_webp $it }
```

