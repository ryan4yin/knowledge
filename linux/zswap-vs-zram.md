# zswap vs zram

> https://askubuntu.com/questions/471912/zram-vs-zswap-vs-zcache-ultimate-guide-when-to-use-which-one/472227#472227

- zswap: 将内存用做 Swap 设备的缓存，提升 Swap 的性能。需要配合 SSD/HDD 的 Swap 分区使用。
  - 好处： Swap 空间大小不受内存限制，可以使用更大的 Swap 空间。
  - 坏处：需要额外的 Swap 分区，Swap 的性能也会受到 SSD/HDD 的影响。
- zram: 将内存直接用作 Swap 设备，不需要额外的 Swap 分区。
  - 好处：不需要额外的 Swap 分区，配置简单，性能更好。
  - 坏处：Swap 空间的大小受内存限制，它无法将数据 offload 到硬盘，因此内存不足时可能会导致系统崩溃。
