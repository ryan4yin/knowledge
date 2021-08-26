// 参考项目：https://github.com/containers/youki
// 参考文档：https://creaink.github.io/post/Computer/Linux/Linux-namespace.html
use std::env;
use std::process::{Command};

use nix::{
    sched::CloneFlags, 
    sched::unshare,
    unistd,
    mount::mount as nix_mount,
    mount::MsFlags
};

fn main() {
    let args: Vec<String> = env::args().collect();

    match &args[1][..] {
        "run" => run(args),
        "child" => child(args),
        _ => println!("do nothing, exit!")
    }
}

fn run(args: Vec<String>) {
    println!("running: {:?} as pid {}", args, unistd::getpid());

    let mut new_args = vec!("child");
    let args_str: Vec<&str> = args[2..].iter().map(|s| s as &str).collect();
    new_args.extend_from_slice(&args_str);

    // 创建新的名字空间
    unshare(CloneFlags::CLONE_NEWUTS | CloneFlags::CLONE_NEWPID | CloneFlags::CLONE_NEWNS).unwrap();

    // `/proc/self/exe` 代表当前程序
    // 这里实现 隔一层 进程完成预设命令的指向，方便观察结果
    let mut process = Command::new("/proc/self/exe")
        .args(new_args)
        .spawn().unwrap();
    process.wait().unwrap();
}


fn child(args: Vec<String>) {
    println!("running: {:?} as pid {}", args, unistd::getpid());

    // 容器使用测试用的 hostname
    unistd::sethostname("test-in-namespace").unwrap();
    // 以 private 的方式 mount 一遍根目录，实现 mount namespace 的隔离哿
    nix_mount(None::<&str>, "/", None::<&str>, MsFlags::MS_PRIVATE | MsFlags::MS_REC, None::<&str>).unwrap();
    // 使用 alpine 作为容器的根目录，并 cd 到该根目录
    unistd::chroot("/data/lib/alpine").unwrap();
    unistd::chdir("/").unwrap();

    // 将 proc 文件夹挂载到 /proc 这个位置，挂载类型为 proc 进程文件系统
    nix_mount(Some("proc"), "/proc", Some("proc"), MsFlags::empty(), None::<&str>).unwrap();

    // 运行预设命令
    let mut process = Command::new(&args[2])
    .args(&args[3..])
    .spawn().unwrap();
    process.wait().expect("failed to `child`...");
}
