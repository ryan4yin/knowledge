# System call monitoring

1. strace
2. ltrace
3. lsof

## using strace

examples:

```shell
# Track file related syscalls
strace -e trace=file ls
```

Useful options and examples

- `c` – See what time is spend and where (combine with -S for sorting)
- `f` – Track process including forked child processes
- `o` my-process-trace.txt – Log strace output to a file
- `p 1234` – Track a process by PID
- `P /tmp` – Track a process when interacting with a path
- `T` – Display syscall duration in the output

Track by specific system call group

- `e trace=ipc` – Track communication between processes (IPC)
- `e trace=memory` – Track memory syscalls
- `e trace=network` – Track memory syscalls
- `e trace=process` – Track process calls (like fork, exec)
- `e trace=signal` – Track process signal handling (like HUP, exit)
- `e trace=file` – Track file related syscalls

Trace multiple syscalls

```shell
strace -e open,close <path/to/app>
```
