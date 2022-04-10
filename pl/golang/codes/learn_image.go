// 学习图片库，struct 结构体
package main

import (
	"image"
	"image/color"
	"image/gif"
	"io"
	"math"
	"math/rand"
	"net/http"
)

var palette = []color.Color{color.White, color.RGBA{0x11, 0x11, 0x11, 0xee}, color.RGBA{0xcc, 0x55, 0xdd, 0x99}, color.RGBA{0x11, 0xbb, 0x88, 0xaa}, color.RGBA{0x99, 0x33, 0x66, 0xaa}, color.RGBA{0x11, 0x32, 0xaa, 0xaa}, color.RGBA{0xee, 0xcc, 0xaa, 0xaa}}

func main() {
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		lissajous(w)
	})
	http.ListenAndServe("0.0.0.0:8000", nil)
}

func lissajous(out io.Writer) {
	const (
		cycles  = 5
		res     = 0.001
		size    = 100
		nframes = 64
		delay   = 8
	)

	freq := rand.Float64() * 3.0
	anim := gif.GIF{LoopCount: nframes}
	phase := 0.0
	for i := 0; i < nframes; i++ {
		rect := image.Rect(0, 0, 2*size+1, 2*size+1)
		img := image.NewPaletted(rect, palette)
		for t := 0.0; t < cycles*2*math.Pi; t += res {
			x := math.Sin(t)
			y := math.Sin(t*freq + phase)
			img.SetColorIndex(size+int(x*size+0.5), size+int(y*size+0.5), uint8(t)%5+1)
		}
		phase += 0.1
		anim.Delay = append(anim.Delay, delay)
		anim.Image = append(anim.Image, img)
	}

	gif.EncodeAll(out, &anim)
}
