# Nix Darwin

## 如何测试一个 Darwin 包

以 wechat 为例：

```bash
export NIXPKGS_ALLOW_UNFREE=1
nix build --impure github:NixOS/nixpkgs/xxxxxxxxxxxxxx#wechat
open ./result/Applications/WeChat.app
```

