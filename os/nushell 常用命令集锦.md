# nushell 常用命令集锦

将大于 10kib 的 png 图片全部转换为 webp 图片，并执行全文替换：

```nu
# 批量将所有 png 文件转换成 webp 文件以缩小体积，并全文替换 markdown 中的图片名称

let old_format = ".jpeg"

let old_paths = (ls $"**/*($old_format)" | each {|it| $it.name})
$old_paths | to md | save --raw ./old_paths.txt

def to_webp [old_path: string, old_format: string] {
  let webp_path = ($old_path | split row $old_format | append ".webp" | str collect)
  ffmpeg -y -i $old_path -c:v libwebp $webp_path
  rm $old_path
}

def replace_with_webp [old_path: string, old_format: string] {
  let webp_path = ($old_path | split row $old_format | append ".webp" | str collect)
  let old_name = ($old_path | path basename)
  let webp_name = ($webp_path | path basename)
  let cmd = $"gsed -ri 's/($old_name)/($webp_name)/g' `find . -name "*.md"`"
  echo $cmd
  bash -c $cmd
}

$old_paths | each { |it| to_webp $it $old_format }
$old_paths | each { |it| replace_with_webp $it $old_format }
```

