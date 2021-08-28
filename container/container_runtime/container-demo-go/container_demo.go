package main

import (
	"fmt"
	"os"
	"os/exec"
	"syscall"
)

func main() {
	switch os.Args[1] {
	case "run":
		run()
	case "child":
		child()
	default:
		fmt.Println("do nothing, exit!")
	}
}

func run() {
	fmt.Printf("running: %v as pid %v\n", os.Args[2:], os.Getpid())
	// `/proc/self/exe` 代表当前程序
	// 这里实现 隔一层 进程完成预设命令的指向，方便观察结果
	cmd := exec.Command("/proc/self/exe", append([]string{"child"}, os.Args[2:]...)...)
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	// 为 command 创建新的名字空间，再运行
	cmd.SysProcAttr = &syscall.SysProcAttr{
		Cloneflags: syscall.CLONE_NEWUTS | syscall.CLONE_NEWPID | syscall.CLONE_NEWNS,
	}
	must(cmd.Run())

}

func child() {
	fmt.Printf("child running: %v as pid %v\n", os.Args[2:], os.Getpid())
	cmd := exec.Command(os.Args[2], os.Args[3:]...)
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	// 变更 hostname
	must(syscall.Sethostname([]byte("test-in-namespace")))

	// 以 private 的方式 mount 一遍根目录，实现 mount namespace 的隔离哿
	must(syscall.Mount("", "/", "", uintptr(syscall.MS_PRIVATE|syscall.MS_REC), ""))
	// 使用 alpine 作为容器的根目录，并 cd 到该根目录
	must(syscall.Chroot("/data/lib/alpine"))
	must(os.Chdir("/"))

	// 将 proc 文件夹挂载到 /proc 这个位置，挂载类型为 proc 进程文件系统. 0 表示使用空的 flags
	must(syscall.Mount("proc", "/proc", "proc", 0, ""))

	// 运行预设命令
	must(cmd.Run())
}

func must(err error) {
	if err != nil {
		panic(err)
	}
}
