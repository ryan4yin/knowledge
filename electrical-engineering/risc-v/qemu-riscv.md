# QEMU riscv 模拟

QEMU 提供了 qemu-system-riscv64 跟 qemu-system-riscv32 这两个命令，分别模拟 64 位跟 32 位的 riscv 架构。

riscv 基本上每块开发版都需要定制的 OS 或者固件，同一套固件与 OS 只能在特定开发版上运行，不像 x86_64 机器那样，一套系统可以运行在任何同架构的机器上。

必须指定正确的 `--machine`，你制作的镜像才能正常地在 QEMU 中被引导启动。

如果你不关注特定的硬件，只想测试 RISCV 本身的能力，那最好的选择是使用 `virt` 这个虚拟的 machine，这是一块完全虚拟的开发版，专为 QEMU 虚拟机设计。为了将你的 Linux 系统运行在这块 virt 板子上，你需要在编译时设置好合适的内核参数。virt 提供了 PCI、virtio、近期的各种 CPU 型号，以及 RAM，它也支持 riscv64.

可以通过如下命令查看 QEMU 默认支持的所有 machine 类型：

```shell
› qemu-system-riscv64 --machine help
Supported machines are:
microchip-icicle-kit Microchip PolarFire SoC Icicle Kit
none                 empty machine
shakti_c             RISC-V Board compatible with Shakti SDK
sifive_e             RISC-V Board compatible with SiFive E SDK
sifive_u             RISC-V Board compatible with SiFive U SDK
spike                RISC-V Spike board (default)
virt                 RISC-V VirtIO board

› qemu-system-riscv32 --machine help
Supported machines are:
none                 empty machine
opentitan            RISC-V Board compatible with OpenTitan
sifive_e             RISC-V Board compatible with SiFive E SDK
sifive_u             RISC-V Board compatible with SiFive U SDK
spike                RISC-V Spike board (default)
virt                 RISC-V VirtIO board
```

## CPU 固件
