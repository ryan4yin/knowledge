# fstab 与自动挂载

我们常用 /etc/fstab 实现自动挂载，这里做个记录。

## 挂载失败时也启动系统

>https://unix.stackexchange.com/questions/53456/what-is-the-difference-between-nobootwait-and-nofail-in-fstab

在 fstab 中，可以使用 `nofail` 选项，使得挂载失败时也启动系统。

**注意这一点非常重要，因为默认情况下如果挂载失败，系统会永远无法启动，你必须通过 U 盘系统或者 rescue 模式来挂载根分区，修复 `/etc/fstab`**。

尤其是你自动挂载的是移动硬盘或者 SMB 分享，这种情况下，如果你的系统启动时，移动硬盘还未连接，或者 SMB 分享无法连接上，那么系统就会永远无法启动！

示例：

```
/dev/sda1 / ext4 defaults,nofail 0 0
```

## 基础语法

挂载一个普通的分区：

```
/dev/sda1 /mnt/sda1 ext4 defaults 0 0
```

挂载一个 CIFS 分享，用户设为 ryan,组也设为 ryan，并且挂载失败时也启动系统：

```
//xx.xx.xx.xx/share-path /mnt/share cifs vers=3.0,uid=1000,gid=1000,dir_mode=0755,file_mode=0755,mfsymlinks,username=xxx,password=xxx,nofail 0 0
```

然后 `sudo mount -a` 测试下挂载是否正常，再将 SMB 主机停机，再次测试，应该也不会报错。



