# 大型语言模型 LLM

ChatGPT 开启了大型语言模型的新时代，各种开源/闭源 LLM 模型雨后春笋般涌现，这里记录我玩 LLM 的一些心得。

目前开源的 LLM 模型有很多，这里主要考虑中英双语模型：

- [Awesome-Chinese-LLM](https://github.com/HqWu-HITCS/Awesome-Chinese-LLM): 整理开源的中文大语言模型，以规模较小、可私有化部署、训练成本较低的模型为主，包括底座模型，垂直领域微调及应用，数据集与教程等。 
- 垂直领域模型：[Awesome-Domain-LLM](https://github.com/luban-agi/Awesome-Domain-LLM)

## 2024-01 目前最好的商业 LLM 模型

- OpenAI ChatGPT-4: <https://chat.openai.com/> 这个应该不用介绍了。
- Google Gemini Ultra: <https://deepmind.google/technologies/gemini/> 官方宣称其在大多数任务上的测试性能都领先 GPT-4，而且支持多模态（文字、音频、图片、视频、甚至 xlsx/pdf 等格式的文档）
  - Ultra 在跨多个数据中心的一个大型 TPUv4 集群上进行训练，完全使用了 Google 自家的硬件。此外它的多模态能力也都来自 Google Deepmind 团队的技术积累。Deepmind 这波又有点展现出当年 AlphaGo 击败柯洁的风采了。
  - 使用：<https://bard.google.com/chat>
- GLM-4: <https://open.bigmodel.cn/trialcenter>，官方宣称性能比 GPT-4 差得不多了，开放 API 调用，价格看着还不错。说是也支持多模态，但相关 API 当前状态好像还是「敬请期待」


我的初步测试结果：

1. 翻译我的 NixOS 小书：我对 ChatGPT3.5 跟智谱的 GLM-4 比较满意，Bard with Gemini Pro 有个别细节的翻译与原有语义不一致，但 Gemini 也是出结果速度最快的一个，甚至是一次性输出所有内容。
  1. 所以目前看 Bard 是最快，ChatGPT3.5 跟 GLM-4 的结果跟性能则都相差不大。
1. 尝试让 Bard/GLM-4/ChatGPT3.5 编写 nushell 脚本，可能因为太新、数据量太少，只能说全都傻得可以...十多轮对话下来，没一个输出的代码是能跑的。
   1. Bard 总是以为它在写 Python，GLM-4 老是搞混 Nushell 跟其他 Linux 工具的参数语法，ChatGPT 老是混入些奇怪的 rust 语法，三个都教不会。
1. 让它们写些 Python 脚本，倒是都能完成，虽说各有瑕疵，但都很好解决。
1. 写 Guile，也各有错误，不好修。知识量可能不够吧。
1. 待补充


## 2024-01 目前最好的中文 LLM 模型

### 1. ChatGLM3-6B

> 2023/11/27 目前 ChatGLM 已经更新到了 ChatGLM3，还未测试效果。

> 2024-01-19 目前已经推出了 GLM-4 并可通过 API 试用，ChatGLM 还未更新。

开源中文 LLM 模型中，效果最好的是清华大学开源的 ChatGLM，它的 6B 版本可以在 16G 显卡上跑，量化后能跑在 8G 显存的卡上（不过跑不了几句话就会 OOM）。而它原版的 130B 模型，至少需要四张 3090，估计效果会好很多。

6B 版本的 ChatGLM 有一些明显的缺点：

1. 有些内容它不太能理解，经常出现人物关系混乱、因果关系混乱的情况。
2. 上下文能力不足，多聊几句它就把前面的内容忘了。

chatglm 可以用 [chatglm-web](https:cc//github.com/NCZkevin/chatglm-web) 来玩耍体验。

### 2. Baichaun2-13B

https://github.com/baichuan-inc/Baichuan2

### 3. Yi-34B

李开复团队开源的中文 LLM 模型，目前最大的版本是 34B，通过 llama.cpp 可以在 CPU 上运行，也可借助常见消费级显卡（RTX4060 - RTX4090 都可）加速推理。

效果很好，性能堪比 Llama2-70B 与阿里的 Qwen-70B！目前 Huggingface 榜单靠前的模型中，Yi-34B 及其变体占据了相当多的名额。

在借助 llama.cpp + 整型量化的前提下，能 self-hosted 的中英双语模型中，Yi-34B 应该是目前最好的选择。

## 2023-11 目前最好的英文 LLM 模型 - LLAMA2

> 2023/07 发布了 LLAMA2 开源模型： <https://github.com/facebookresearch/llama.git>

开源英文模型中效果最好的是 Meta 的 LLAMA 模型，它衍生出了一整个基于 LLAMA 的微调模型生态。

据传目前效果最高的模型是基于 LLAMA 微调的 Vicuna，能在 4090 上跑的 Vicuna-13B 模型下载链接如下：

- [lmsys/vicuna-13b-v1.5](https://huggingface.co/lmsys/vicuna-13b-v1.5): 发布于 2023/08/02.
- [lmsys/vicuna-13b-v1.5-16k](https://huggingface.co/lmsys/vicuna-13b-v1.5-16k): 发布于 2023/08/02，支持 16k token 输入。

## (2023-5)DB-GPT - 本地化大模型数据助手

[DB-GPT](https://github.com/csunny/DB-GPT) 是一个基于 LLM 模型的本地化数据助手，提供私域问答与数据处理等功能。

它是一个整合了各种 AI 前沿技术的落地项目，很值得一玩。
