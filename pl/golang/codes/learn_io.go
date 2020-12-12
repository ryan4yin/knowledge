package main

import (
	"bufio"
	"fmt"
	"io"
	"io/ioutil"
	"os"
	"strings"
)

func learnReader() {
	// 方法一：一次性读完整个文件，适合用于读取一些不方便流式处理的数据（如 json/yaml）。
	bytes1, err := ioutil.ReadFile("learn_slice.go")
	if err != nil {
		panic(err)
	}
	fmt.Println(string(bytes1))

	// 方法二：bufio 流式读取，而且提供 ReadBytes/ReadString 等便捷方法
	// 适合用于读取大文件，或者需要分段处理文本的情况（比如按行处理）。
	file, err := os.Open("learn_slice.go") // 返回一个只读 reader
	if err != nil {
		panic(err)
	}
	defer file.Close()
	bufReader := bufio.NewReader(file)
	for {
		line, err := bufReader.ReadString('\n')
		if err != nil {
			if err == io.EOF {
				return
			}

			panic(err)
		}

		line = strings.TrimSpace(line)
		fmt.Println(line)
	}
}

func learnWriter() {
	// 方法一：一次性地写入（会清空掉原有内容）
	content := "write all content at once"
	// 只接受 []byte，因此要转换下类型
	err := ioutil.WriteFile("write_once.txt", []byte(content), 0644) // 必须指定权限 0644
	if err != nil {
		panic(err)
	}

	// 方法二：流式写入，提供了 WriteString 方法
	// 适合用于需要按分段处理文本的情况。
	file, err := os.OpenFile("write_multiple_times.txt", os.O_RDWR|os.O_CREATE|os.O_TRUNC, 0644) // 返回一个可读可写的 file
	if err != nil {
		panic(err)
	}
	defer file.Close()

	bufWriter := bufio.NewWriter(file) // 使用 bufio 提升性能
	defer bufWriter.Flush()            // 最后需要调用 bufWriter 的 flush 函数！
	// 这里可以分多次写入
	content = "write content multiple times"
	_, err = bufWriter.WriteString(content)
	if err != nil {
		panic(err)
	}
}

func main() {
	learnReader()
	learnWriter()
}
