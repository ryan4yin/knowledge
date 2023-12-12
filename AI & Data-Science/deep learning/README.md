# Deep Learning


近期火热的 Llama / AIGC 相关科普资料：

- [苏洋的相关博客内容](https://soulteary.com/tags/python.html)


比较权威的 Huggingface 开源 LLM 模型评测榜单：

- <https://huggingface.co/open-llm-leaderboard>


## 快速下载 huggingface 模型

使用 [huggingface-cli](https://huggingface.co/docs/huggingface_hub/guides/cli) 要比直接使用 `git clone` 方便很多，可以直接下载模型，而不用下载整个仓库，而且重点是能断点续传！

```
huggingface-cli download --help
```

## 通过 llama.cpp 进行 CPU / GPU 混合推理

llama.cpp 的最初目标是在 CPU 上运行 LLM 模型，但随着项目的迭代，目前已经支持 CPU / GPU 混合推理，可以将任务 offload 到 GPU 上，以提高推理速度。

借助此项目，可以在消费级显卡上运行任何大小的 LLM 模型！不用担心 GPU 显存不够（Out of Memory）的问题，显存的多少只影响推理速度。

借助 llama.cpp + 消费级显卡（比如 RTX 4090），就能以可接受的推理速度来验证 LLM 模型的效果，而不用购买昂贵的商业 GPU 或租用云服务。

相关文章：

- [零一万物模型折腾笔记：官方 Yi-34B 模型基础使用](https://soulteary.com/2023/12/10/notes-on-the-01-ai-model-basic-use-of-the-official-yi-34b.html)
- [CPU 混合推理，非常见大模型量化方案：“二三五六” 位量化](https://soulteary.com/2023/12/12/cpu-hybrid-inference-unusual-large-language-model-quantization-2-3-5-6-bit-quantization.html)

