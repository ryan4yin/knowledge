package main

import (
	"fmt"
	"reflect"
	"unsafe"
)

func main() {
	var a1 [3]int // 数组，自动分配空间
	var s1 []int  // 切片，自动分配空间（长度0，容量 0）

	fmt.Println(a1, len(a1))
	fmt.Println(s1, len(s1), cap(s1))

	var a2 = [3]int{1, 2, 3} // 通过字面量初始化数组
	var s2 = []int{1, 2, 3}  // 通过字面量初始化切片

	// make 的参数：类型，长度，容量
	var s3 = make([]int, 5, 10) // 预先分配好内存的切片
	fmt.Println("a2(predefined):", a2, reflect.ValueOf(a2).Kind(), len(a2), cap(a2))
	fmt.Println("s2(predefined, len==cap):", s2, reflect.ValueOf(s2).Kind(), len(s2), cap(s2))
	fmt.Println("s3(created by `make`):", s3, reflect.ValueOf(s3).Kind(), len(s3), cap(s3))

	// 通过 append 将一个切片合并到另一个上
	// 如果底层容量超过限制，会自动创建一个新切片，并且**拷贝**旧切片的所有元素！(所以最好先通过 make 预分配足够容量)
	var s4 = append(s3, s2...)
	hdr := (*reflect.SliceHeader)(unsafe.Pointer(&s3))
	data := *(*[10]int)(unsafe.Pointer(hdr.Data))
	fmt.Println("s3(after append):", s3, "underlying array:", data) // 底层数组后面的元素变了，但是 s3 本身没变。
	fmt.Println("s4(after append):", s4)

	var s5 = append(s3, 7, 8) // 第二次 append 会导致 s4 被修改！！！
	fmt.Println(s5)
	fmt.Println("s4(after append 2nd):", s4)
}
