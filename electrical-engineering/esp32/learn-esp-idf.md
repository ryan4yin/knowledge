# ESP-IDF 学习

## 代码结构：

1. 主程序代码放在 main 文件夹中，特殊函数有这几个：

1. `void app_main()`: 程序的入口，它在 FreeROTS 内核初始化完成后，被 fork 出的应用线程调用
1. printf(), strlen(), time() 等 C 标准库的常用函数在 ESP-IDF 中也可以直接使用
1. ESP-IDF 默认使用 FreeRTOS 作为底层系统，最常用的 FreeRTOS 函数有
   1. `vTaskDelay` 看名字就知道了，延时函数
   2. `xTaskGetTickCount`:
