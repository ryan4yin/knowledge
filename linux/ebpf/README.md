# eBPF

- ebpf.io
- https://github.com/iovisor/bcc: ebpf's go/lua bindings(you still need to write the ebpf program in
  C)
- https://github.com/bpftrace/bpftrace
- https://github.com/cilium/ebpf: ebpf's go bindings(you still need to write the ebpf program in C))
- https://github.com/aya-rs/aya: ebpf's rust bindings, note that you can write ebpf programs in rust
  using this library.
- https://www.brendangregg.com/bpf-performance-tools-book.html

## 学习目标

1. 可观测性：我们用 ebpf 来分析什么东西？解决什么问题？
2. 网络：ebpf 如何做到拦截处理流量，同时更新 ebpf 程序还不会中断连接？
3. 安全性：基于 ebpf 的安全技术有哪些，跟 apparmor 想比有什么区别、优势？
