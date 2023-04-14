# 大型语言模型 LLM

ChatGPT 开启了大型语言模型的新时代，各种开源/闭源 LLM 模型雨后春笋般涌现，这里记录我玩 LLM 的一些心得。

目前开源的 LLM 模型有很多，详情可参考 [Awesome-LLM](https://github.com/Hannibal046/Awesome-LLM)

## 2023-04 目前最好的 LLM 模型

开源中文 LLM 模型中，效果最好的是清华大学开源的 ChatGLM，它的 6B 版本可以在 16G 显卡上跑，量化后能跑在 8G 显存的卡上（不过跑不了几句话就会 OOM）。而它原版的 130B 模型，至少需要四张 3090，估计效果会好很多。

开源英文模型中效果最好的是 Meta 的 LLAMA 模型，它衍生出了一整个基于 LLAMA 的微调模型生态。


chatglm 可以用 [chatglm-web](https://github.com/NCZkevin/chatglm-web) 来玩耍体验。
