
1. container/ring: 循环链表
    - 优势：
        1. 任何节点都可以做为 header，可以从任何节点开始进行链表的遍历。当指针又回到 header 时，说明遍历已经完成。
        2. 不需要为队列维护两个指针，也不存在 NULL 指针，不需要通过 NULL 判空来确定链表结束。
1. heap: 可用于实现高效定时器 - 通过最小堆对所有 cronjob 进行存储、排序，这样每次都只需要遍历最少的 cronjob 就能触发所有到了时间的 job.

