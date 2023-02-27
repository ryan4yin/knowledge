# Stable Diffuion - 文字生成图片

这是一个非常火的图片转文字模型，效果非常惊艳：

- [StableDiffusionBook](https://github.com/sudoskys/StableDiffusionBook): Stable Diffusion 小书，适合入门看。
- [stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui): 应该是目前最火的图片生成工具了，提供了易用的 AI 来与模型进行交互。
- [sd-webui-controlnet](https://github.com/Mikubill/sd-webui-controlnet): 整合了 controlnet 的 stable-diffusion-webui，controlnet 是 2023-02 的一项突破性进展，使我们能够使用线稿、骨骼结构来控制模型效果。
- [stablediffusion](https://github.com/Stability-AI/stablediffusion)

其他资源站：

- [civitai](https://civitai.com): 模型分享网站，大量高质量模型（注意有大量 NFSW）
  - 比如目前（2023-02-23）比较火的有
    - [chilloutmix](https://civitai.com/models/6424/chilloutmix) 小姐姐模型
- [prompthero](https://prompthero.com/stable-diffusion-prompts): 提示词分享站点，可用于学习如何编写调试你的「图片咒语」。

一些教程：

- [低成本体验生成 AI 小姐姐照片](https://medium.com/@croath/%E4%BD%8E%E6%88%90%E6%9C%AC%E4%BD%93%E9%AA%8C%E7%94%9F%E6%88%90-ai-%E5%B0%8F%E5%A7%90%E5%A7%90%E7%85%A7%E7%89%87-85ffa7c13cd7)
- [基于我擅长的编程、绘画、写作展开的 AI 探索和总结 - phodal](https://github.com/phodal/ai-research)


## 我的玩法

首先为了方便环境搭建，我选择使用 Docker 来跑深度学习环境。

我的系统是 Arch，显卡是 RTX 3070 Max-Q，找到 Nvidia Docker 的安装方法 [Run GPU accelerated Docker containers with NVIDIA GPUs](https://wiki.archlinux.org/title/Docker#Run_GPU_accelerated_Docker_containers_with_NVIDIA_GPUs：

1. 首先 `yay -S docker` 安装好 docker
2. 确认本机安装了 nvidia 驱动，可通过本机运行 `nvidia-smi` 查看输出，如果各驱动版本号输出正常，也有输出你的显卡型号、功率、内存大小、利用率等参数，就说明没问题。
   1. 主机不需要安装 cuda，容器里装好就行。
3. 然后用 `yay -S nvidia-container-toolkit` 安装好 nvidia 容器支持。
4. `sudo systemctl restart docker` 重启 docker 运行时

上述流程走完后就搞定了，接着可以跑个 cuda 容器测一下，如果同样能识别到 GPU 那就说明没毛病。比如:

```shell
docker run --rm --gpus all nvidia/cuda:11.7.1-base-ubuntu22.04 nvidia-smi
```

注意 cuda 容器比较大，建议直接拉取你打算使用的版本来进行测试，这样后面就不需要拉取第二次镜像。

比如我打算跑的 [stable-diffusion-webui-docker](https://github.com/camenduru/stable-diffusion-webui-docker/blob/main/Dockerfile) 的基础镜像是 `nvidia/cuda:11.7.1-base-ubuntu22.04`，那我就直接拉了这个镜像来测试，后面就不需要拉第二次了。


前面的流程跑通后，就可以跑我们的容器了，首先进入 [stable-diffusion-webui-docker](https://github.com/camenduru/stable-diffusion-webui-docker/blob/main/Dockerfile) 构建好容器：

```shell
docker build -t sd-webui .
```

>为了节约时间，我建议改下 Dockerfile，模型手动单独下载，这样就可以分开更新，会方便一些。

然后运行容器，再登录进去跑项目：

```shell
# 直接命令行起容器
## 当然想也可以写个 docker-compose.yaml 会更方便些，后面再整吧。
docker run --gpus all --network host --name sd-webui --entrypoint /bin/bash -d stable-diffusion-webui -c 'while true; do sleep 1000; done'
docker exec -it sd-webui bash
```

然后在容器中直接运行启动命令：

```shell
python webui.py --xformers --listen --enable-insecure-extension-access
```

等待启动完成就可以访问 <http://127.0.0.1:7860> 开始玩耍了。

## 更换模型

如果你下载了新的模型要怎么使用呢？

首先模型下载到本地，可以考虑直接用 docker 文件夹映射的方式来把模型弄进容器中，也可以 copy，示例:

```shell
docker cp chilloutmix_NiPrunedFp32Fix.safetensors sd-webui:/content/stable-diffusion-webui/models/Stable-diffusion/
```

模型弄进去后重启启动 webui，就能在左上角的 checkpoints 那里选用新模型了。


## sd-webui-controlnet

按照 [sd-webui-controlnet](https://github.com/Mikubill/sd-webui-controlnet) 的 README 操作就行，需要注意的是，ControlNet 模型需要放在 `stable-diffusion-webui/extensions/sd-webui-controlnet/models/ControlNet` 文件夹中才能找到它（而不是 `stable-diffusion-webui/models/ControlNet`）。

插件安装好，模型也放置好后，启动 sd-webui，就能在 txt2img/img2img 的最下方找到默认收起来的 ControlNet 面板，使用流程：

1. 在 ControlNET 中选择好模型，如果模型中未列出选项，说明说明没放对地方
2. Preprocesser 选择需要跟模型对应：
   1. canay 边缘检测：用户输入一张动漫图片作为参考，程序会对这个图片预加载出线稿图，之后再由AI对线稿进行精准绘制（细节复原能力强）
   2. Hed： 相比Canny自由发挥程度更高
   3. Scribble 模型: 涂鸦成图，比Canny自由发挥程度更高
   4. Seg模型:区块标注，适合潦草草图上色 
   5. Mlsd 模型：建筑物线段识别，适合画建筑
   6. Normal模型：适用于 3 维制图，用于法线贴图，立体效果
   7. Depth模型：该模型可以较好的掌握图片内的复杂3维结构层次，并将其复现
3. 在 ControlNet 面板中添加参考图片，插件会使用选择的 preprocesser 先处理图片，再将结果作为 ControlNet 的输入。
4. 最后就是在前面的正常面板中写提示词、调整生成参数进行生成了（txt2img 模式下）。
