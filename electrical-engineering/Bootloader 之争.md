# Bootloader 之争

UEFI(EDKII) vs LinuxBoot vs U-Boot.

## EDK2 的 ACPI 模式与 DeviceTree 模式

1. ACPI 模式：即 UEFI 标准的硬件描述方式，通过 ACPI 表来描述硬件信息。
   - ACPI 和 UEFI 一样，由微软和 Intel 联合提出。
1. DeviceTree 模式：即源自 Linux 内核的硬件描述方式，使用 DTS 文件来描述硬件信息。

区别：

1. ACPI 不但实现了硬件设备的静态抽象，还实现了硬件行为的动态抽象。
2. ACPI 顾名思义，还提供全面的电源管理功能。
3. ACPI 兼容性更强，用一套抽象模型可以支持全部操作系统。而如果用 DeviceTree，Windows 是不支持的。
4. ACPI 已经是服务器事实标准：随着 x86 服务器占据主流，ACPI 已经占据了服务器生态位，后进的 ARM 要支持既有的配件和生态，采用ACPI是明智之举。
   - 因为同样的原因，ARM 的服务器生态也接纳了传统 x86 体系中的 PCI/PCIe 总线，以融入现有的生态。

以及我目前的一点理解（不保证正确）：

1. ACPI 模式下，ACPI 表等硬件信息是写在 UEFI 固件源码中的，构建出的固件本身就包含了硬件信息。
   - 这使得任何对接了 ACPI 的操作系统都能直接在使用了 UEFI 的硬件上运行，比如我们在网上下载的 Windows/Ubuntu 系统镜像，都可以直接在大多数 UEFI 主板上启动。
2. DeviceTree 模式下，硬件信息是写在 Linux 内核源码中的，跟内核是绑定在一起的。
   - 这使得每一家 ARM 嵌入式设备商、SoC 芯片商，都需要定制自己的 Linux 内核与 U-Boot 引导。我们的操作系统也必须使用这个定制的内核才能在这个设备上正常运行。
   - RISC-V 同样采用了 DeviceTree 模式，只是因为 RISC-V 指令集的开放性，为了避免指令集碎片化带来的驱动实现碎片化，RISC-V 额外引入了一个 OpenSBI 屏蔽底层的指令集差异，向上层 U-Boot 等引导程序提供统一的接口。

总之 UEFI + ACPI 这种模式，对硬件的用户很友好，一个系统镜像就能在大多数 UEFI 主板上启动。但相对的，UEFI 固件要比 U-Boot 复杂得多，厂商需要花费更多的精力定制固件。

而 DeviceTree 这种模式，对 SoC 或嵌入式设备的开发者很友好，直接改 Linux 跟 U-Boot 的源码就行，不需要依赖于第三方的 UEFI 固件，这要简单灵活得多。但相对的，用户需要使用定制的内核和引导程序，不能直接使用通用的系统镜像。


## 参考资料

- https://developer.aliyun.com/article/1411292
- https://tinylab.org/riscv-uefi-part1/



