package main

import (
	"fmt"
)

func main() {
	for i, char := range "春天到了，hhhh" {
		fmt.Println(i, string(char), char)
	}
}
