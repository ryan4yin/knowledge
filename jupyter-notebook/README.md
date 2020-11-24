# My Jupyter Notebooks

[View Through NBViewer](https://nbviewer.jupyter.org/github/ryan4yin/knowledge/tree/master/notebook)

## Book/Notebook Reference

1. linear algebra
    - Book: [线性代数及其应用](https://book.douban.com/subject/2128777/)
    - Course: [Linear Algebra - Gilbert Strang](https://www.youtube.com/playlist?list=PL221E2BBF13BECF6C)
    - Lecture: [MIT 18.06: Linear Algebra Lectures](https://github.com/stevengj/1806)
    - Notes: [线性代数笔记 - 子实（Python）](https://github.com/zlotus/notes-linear-algebra)
2. AI learning
    - machine learning
      - [Hands-on Machine Learning with Scikit-Learn and TensorFlow](https://github.com/ageron/handson-ml)
      - [100-Days-Of-ML-Code](https://github.com/Avik-Jain/100-Days-Of-ML-Code)
      - [Implement basic ML models in TensorFlow 2.0 + Keras or PyTorch.](https://github.com/madewithml/basics)
    - deep learning
      - [fastai book](https://github.com/fastai/fastbook)
      - [动手学深度学习（Dive into Deep Learning，D2L）](https://github.com/d2l-ai/d2l-zh)
2. mathematical methods for physics
    - Book: [数学物理方法 - 顾樵](https://book.douban.com/subject/10517521/)
    - Course: [数学物理方法 - 吴崇试](https://www.bilibili.com/video/av6292055)
3. signal and systems
    - Book: [信号与系统 - 奥本海姆](https://book.douban.com/subject/21359219/)
    - Course: [信号与系统分析](https://www.bilibili.com/video/av14481798)
    - Lecture: [signals-and-systems-lecture（Python）](https://github.com/spatialaudio/signals-and-systems-lecture)
4. digital signal processing(preview)
    - Book: [Think DSP（Python）](https://book.douban.com/subject/30150911/)
    - Lecture: [digital-signal-processing-lecture（Python）](https://github.com/spatialaudio/digital-signal-processing-lecture)


## Work Environment

### 1. Install Environment Manually

set up and use work environment:

```shell
pip install poetry

# init env and install all python dependencies
poetry install

# enable python env
poetry shell

# integrate julia into jupyterlab
julia --eval 'using Pkg; Pkg.add("IJulia")'

# start jupytelab
jupyter lab
```

jupyterlab should contains 2 kernels: python & julia

usage after setup:

```shell
poetry run jupyter lab
```

Other related materials can be put in folder: `playgound`, which will be ingored by git.


### 2. Use Docker Image Provided by Jupyter

Jupyter provide a set of docker image: [jupyter-docker-stacks](https://jupyter-docker-stacks.readthedocs.io/en/latest/using/selecting.html)

datascience-notebook and tensorflow-notebook may be useful in this project.