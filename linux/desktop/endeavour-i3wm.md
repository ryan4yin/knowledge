# Endeavour I3wm 使用记录

## 配置调整

### 1. 修改默认文件编辑器

默认使用的是超难用的 nano 编辑器，添加配置文件 `/etc/profile.d/editor.sh`，内容为:

```
export EDITOR=vim
```

然后重启系统，即可将默认编辑器改为 vim
