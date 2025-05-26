# 权限控制

## 如何充值一个 APP 的权限

在 macOS 运行 APP 时常常会弹出各种询问是否给予 APP 各种权限的弹窗，有时候出于谨慎我选择了拒绝，接着 APP 就无法正常工作了，而且再也不会弹出第二次授权弹窗...

有时候运气好，在 Settings -> Privacy & Security 里就能找到对应的权限选项，重新启用授权就行。

但问题是有的权限（比如 System Events）在 Settings 里找不到，于是 APP 就一直无法正常使用了...

我 Google 也没找到很好的办法，但是问 Gemini 却给出了能 Work 的解决方案，这里记录下：

```bash
# 1. 获取到 APP 的 ID
osascript -e 'id of app "Your APP Name"'

# 2 使用 APP ID 重置该 APP 的所有权限
sudo tccutil reset All you.app.id
```

重置完成后再次重新执行 APP，应该就能再次弹出授权弹窗了。

如果使用完上述方法后仍然没有效果，可以再试试卸载 APP -> 重装 APP.



