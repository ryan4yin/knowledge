# 大型语言模型 LLM

ChatGPT 开启了大型语言模型的新时代，各种开源/闭源 LLM 模型雨后春笋般涌现，这里记录我玩 LLM 的一些心得。

目前开源的 LLM 模型有很多，详情可参考 [Awesome-LLM](https://github.com/Hannibal046/Awesome-LLM)

## 2023-04 目前最好的中文 LLM 模型 - ChatGLM

开源中文 LLM 模型中，效果最好的是清华大学开源的 ChatGLM，它的 6B 版本可以在 16G 显卡上跑，量化后能跑在 8G 显存的卡上（不过跑不了几句话就会 OOM）。而它原版的 130B 模型，至少需要四张 3090，估计效果会好很多。

6B 版本的 ChatGLM 有一些明显的缺点：

1. 有些内容它不太能理解，经常出现人物关系混乱、因果关系混乱的情况。
2. 上下文能力不足，多聊几句它就把前面的内容忘了。



chatglm 可以用 [chatglm-web](https:cc//github.com/NCZkevin/chatglm-web) 来玩耍体验。

## 2023-04 目前最好的英文 LLM 模型 - LLAMA

开源英文模型中效果最好的是 Meta 的 LLAMA 模型，它衍生出了一整个基于 LLAMA 的微调模型生态。

据传目前效果最高的模型是基于 LLAMA 微调的 Vicuna，能在 4090 上跑的 Vicuna-13B 模型下载链接如下：

- [lmsys/vicuna-13b-delta-v1.1](https://huggingface.co/lmsys/vicuna-13b-delta-v1.1/tree/main)
- [decapoda-research/llama-13b-hf](https://huggingface.co/decapoda-research/llama-13b-hf): 根据开源协议，vicuna 只能开源自身的微调权重，其基础模型 llama-13b 项目不能自带。而这个仓库保存了转换格式后的 llama-13b 模型，将其与 vicuna 权重合并，就得到我们需要的模型了。

## (2023-5)DB-GPT - 本地化大模型数据助手

[DB-GPT](https://github.com/csunny/DB-GPT) 是一个基于 LLM 模型的本地化数据助手，提供私域问答与数据处理等功能。

它是一个整合了各种 AI 前沿技术的落地项目，很值得一玩。
