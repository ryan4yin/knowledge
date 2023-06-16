# 远程构建

- https://github.com/NixOS/nix/blob/713836112/tests/nixos/remote-builds.nix#L46
- https://sgt.hootr.club/molten-matter/nix-distributed-builds/

多机远程构建是以 derivation 为单位的，在构建的 packages 较多时可以轻松将所有主机的 CPU 都用上，非常爽。

## 画外

其他发行版也可以用 distcc/ccache 来构建，不过我没试过，不清楚体验如何。
