package main

import (
	"fmt"
	"math"
	"strings"
)

func primeFilter(prime int, remains chan int) chan int {
	result := make(chan int)
	for i := range remains {
		if i%prime != 0 {
			result <- i
		}
	}

	return result
}

func primeNumbers(max int) chan int {
	isPrime := make([]bool, max+1)
	primeNumChan := make(chan int)

	// calulate all prime numbers
	isPrime[2] = true
	isPrime[3] = true

	// 2 和 3之后的所有素数，都不能被 2 或 3 整除：可推出它们必须满足 6 n ± 1 这个条件。
	for i := 7; i < max; i += 6 {
		isPrime[i-2] = true // 6n-1
		isPrime[i] = true   // 6n+1
	}

	// 上面设为 true 的都还只是候选值，需要进一步筛选.
	// 现在开始将「假」素数设为 false
	for i := 5; i <= int(math.Sqrt(float64(max))); i += 6 {
		for j := i * i; j < max; j += i {
			if isPrime[j] && j%i == 0 {
				isPrime[j] = false
			}
		}
	}

	// output
	go func() {
		for i, ok := range isPrime {
			if !ok {
				continue
			}
			primeNumChan <- i
		}
		close(primeNumChan)
	}()

	return primeNumChan
}

func PrimeFactors(n int) string {
	var result []string
	for p := range primeNumbers(n) {
		if n%p != 0 {
			continue
		}
		for exp := 1; ; exp++ {
			if n%p == 0 {
				n /= p
			} else {
				exp-- // get last valid exponent
				var s string
				if exp == 1 {
					s = fmt.Sprintf("(%d)", p)
				} else {
					s = fmt.Sprintf("(%d**%d)", p, exp)
				}
				result = append(result, s)
				break
			}
		}
	}
	return strings.Join(result, "")
}

func main() {
	fmt.Println(PrimeFactors(7775460))
}
