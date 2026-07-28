<div class="ae-hero" markdown>
<p class="ae-kicker">Analog Electronics · Field Notes 01–30</p>

# 模拟电子技术 30 天双轨自学指南

<p class="ae-lead">从电路语言与器件模型出发，建立能计算、能解释、能承受追问的模拟电路知识框架。</p>

<div class="ae-hero__actions">
<a class="ae-start" href="sprint/week-1/#day-1">开始 Day 1　→</a>
<a class="ae-route" href="学习路线与使用方法/">先看学习路线</a>
</div>

<div class="ae-metrics" aria-label="课程规模">
<div class="ae-metric"><strong>30 天</strong><span>连续冲刺路线</span></div>
<div class="ae-metric"><strong>23.4 h</strong><span>已计时学习任务</span></div>
<div class="ae-metric"><strong>7 章</strong><span>完整教材与推导</span></div>
</div>
</div>

<div class="ae-path-grid">
<div class="ae-path"><b>01 · 冲刺轨</b><p>每天 45–60 分钟，以 P0、推导、计算、口述和关卡建立连续进度。</p></div>
<div class="ae-path"><b>02 · 深入轨</b><p>从基本方程进入器件模型、频率响应和系统边界，为追问补足依据。</p></div>
<div class="ae-path"><b>03 · 对话学习</b><p>Clone 后让学习助手批改、模拟面试，并把复习记录只保存在本机。</p></div>
</div>

<div class="ae-signal-chain" aria-label="电子系统信号链">
<span>传感器</span><i>→</i><span>模拟前端</span><i>→</i><span>ADC</span><i>→</i><span>数字处理 / 控制</span><i>→</i><span>驱动器</span><i>→</i><span>执行器</span>
</div>

## 现在开始

Day 1 页面已经给出目标、前置、计时和过关题，不需要先挑教材。完成第一天后再读[学习路线与使用方法](学习路线与使用方法.md)。网页阅读者可直接沿导航学习；Clone 仓库后，还可以按[使用学习助手](assistant/使用学习助手.md)中的口令进行对话式学习，让助手在本地维护进度、错题和复习计划。时间紧张时只完成 P0，不以跳过基础换取表面进度。

## 30 天冲刺

- [第 1 周：电路语言、网络定理与 RC](sprint/week-1.md)
- [第 2 周：二极管、BJT 与 MOSFET](sprint/week-2.md)
- [第 3 周：基本放大电路与运算放大器](sprint/week-3.md)
- [第 4 周：反馈、频率响应、功放、电源与面试整合](sprint/week-4.md)

冲刺轨每天给出目标、预计用时、最小知识、推导、例题、面试表达和过关题。先完成当天关卡，再决定是否沿深入轨的教材链接继续深挖。

## 完整教材

- [第 1 章：最小电路基础](guide/01-最小电路基础.md)：参考方向、KCL/KVL、网络等效与 RC 暂态
- [第 2 章：二极管与半导体基础](guide/02-二极管与半导体基础.md)：冲刺轨掌握状态判断、整流/限幅/钳位，深入轨理解 PN 结物理与动态非理想
- [第 3 章：BJT 与 MOSFET](guide/03-BJT与MOSFET.md)：冲刺轨掌握端口方向、工作区、偏置 Q 点与小信号参数，深入轨理解 Early 效应、沟道长度调制和体效应
- [第 4 章：基本放大电路](guide/04-基本放大电路.md)：从 DC 偏置与负载线出发，推导 BJT/MOS 六种基本组态，并把信号源、负载、耦合旁路和削顶诊断接成完整系统增益链
- [第 5 章：运算放大器](guide/05-运算放大器.md)：从差分开环模型与虚短/虚断判据出发，推导基本与功能电路，区分比较器和线性反馈，并用摆幅、共模、电流、GBW、压摆率检查实际边界
- [第 6 章：反馈与频率响应](guide/06-反馈与频率响应.md)：从闭环代数、灵敏度与四种反馈组态出发，推导 RC/Bode、放大器带宽和 Miller 效应，并用环路增益与稳定裕度解释振铃和振荡
- [第 7 章：差分、功放与电源](guide/07-差分功放与电源.md)

完整教材用于补概念、看推导和准备追问。它不是另一套必须线性读完的课程；优先从当天冲刺页给出的链接进入相关小节。

## 面试与练习

- [高频问题与追问](interview/高频问题与追问.md)
- [模拟面试一：20 分钟诊断型](interview/两套模拟面试.md#2-模拟一20-分钟诊断型100-分)
- [模拟面试二：25 分钟压力型](interview/两套模拟面试.md#3-模拟二25-分钟压力型100-分)
- [评分标准](interview/评分标准.md)
- [练习题](exercises/练习题.md)
- [详细解答](exercises/详细解答.md)
- [一页公式表](cheatsheets/一页公式表.md)
- [典型电路速查](cheatsheets/典型电路速查.md)

练习时先独立写出依据和适用条件，再核对解答。模拟面试要出声作答，并用评分标准记录“结论—理由—边界”是否完整。

## 交互实验

- [RC 阶跃响应实验](labs/rc-step-response.html)：建议第 4 天使用；比较 $R$、$C$、初值和终值分别改变曲线的哪一部分。
- [BJT 负载线实验](labs/bjt-load-line.html)：建议第 10 或 15 天使用；由两个截距判断 Q 点何时进入截止或饱和。
- [运算放大器反馈实验](labs/opamp-feedback.html)：建议第 23～25 天使用；对照理想电阻比、有限开环增益和电源轨削顶。

实验用于把公式变成直觉。每次只改变一个参数：先在纸上写出方向预测，再用键盘或输入框修改数值，最后用曲线和读数解释预测是否成立。

## 两种学习方式

- **网页模式：** 沿 30 天路线、完整教材、练习和交互实验自由学习；网页不保存个人进度。
- **Clone + 学习助手：** 在支持仓库指令的编码助手中打开项目，通过“开始第 N 天”“批改 E-C-01”“开始模拟面试”等口令学习；个人记录只保存在本机 `.learning/`，不会进入 Git。

完整命令、状态格式和隐私说明见[使用学习助手](assistant/使用学习助手.md)。

## 拓展应用

[智能系统中的模拟边界](extensions/agent-systems.md)以传感器、模拟前端、数据转换、数字处理、驱动器和执行器为例，说明模电知识如何进入更大的系统。该页是可选拓展，不影响主线学习。

## 依据与可选参考

主线讲义、例题、练习与答案完全自包含，**不要求购买教材或访问外部课程才能完成 30 天计划**。若考后希望交叉学习，可选用 [MIT OCW 6.002 Circuits and Electronics](https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/)、[MIT OCW 6.101 Introductory Analog Electronics Laboratory](https://ocw.mit.edu/courses/6-101-introductory-analog-electronics-laboratory-spring-2007/pages/syllabus/)、[Analog Devices University 教程](https://wiki.analog.com/university/courses/tutorials/index)和 [ADI《Op Amp Applications Handbook》](https://www.analog.com/en/resources/technical-books/op-amp-applications-handbook.html)。这些只用于补充实验直觉和运放应用，不是每日任务的前置依赖。
