# 模拟电子技术 30 天双轨自学指南

一套面向零基础或基础薄弱学习者的公开自学材料：从 KCL/KVL、器件模型与偏置开始，逐步进入放大电路、运算放大器、反馈、频率响应、功放、电源和技术面试表达。

[在线阅读](https://samkuler.github.io/analog-electronics-guide/) · [开始 Day 1](docs/sprint/week-1.md#day-1) · [学习路线](docs/学习路线与使用方法.md)

## 两种学习方式

**网页模式**适合按导航阅读、查公式、做练习和运行七个交互实验。网页是纯静态站点，不保存个人进度。

**Clone + 学习助手**适合对话式学习：

```bash
git clone https://github.com/SamKuler/analog-electronics-guide.git
cd analog-electronics-guide
```

在能够读取仓库说明的对话助手中打开目录，然后使用：

```text
开始第 1 天
只做 P0
批改 E-C-01
开始模拟面试
复盘
查看到期复习
```

助手协议位于 [AGENTS.md](AGENTS.md)，可复制提示词位于 [prompts/学习助手.md](prompts/学习助手.md)。个人状态只写入本机 `.learning/`，该目录默认不会进入 Git。

## 内容

- 30 天冲刺轨：每天 45–60 分钟，合计约 23.4 小时；
- 七章完整教材：概念、模型、推导、例题、边界与口述；
- 分层练习、详细解答、70 个高频问答与两套模拟面试；
- 七个交互实验：RC 阶跃、二极管波形、BJT 负载线、晶体管放大器信号链、运放反馈、Bode 稳定性和隔离低压整流滤波；
- 一页公式表、典型电路速查和可交互的参数实验。

主线材料自包含，不要求购买教材或访问外部课程。

## 本地预览与验证

```bash
uv sync
uv run python -m unittest discover -s tests -v
node --test tests/**/*.test.mjs
uv run python scripts/validate_guide.py .
uv run mkdocs serve
```

生产构建使用：

```bash
uv run mkdocs build --strict
```

## 许可证

- 课程正文、题目、解答、教学图文，以及 `README.md`、`AGENTS.md`、`prompts/` 中的教学文字采用 [CC BY 4.0](LICENSE-CONTENT)；
- HTML/CSS/JavaScript/Python/YAML 实现、脚本、配置、工作流、测试与交互实验程序采用 [MIT License](LICENSE-CODE)；
- 同一文件同时包含教学文字与程序实现时，文字部分采用 CC BY 4.0，程序实现部分采用 MIT License；
- 外部链接指向的材料仍由各自权利人按原许可管理。
