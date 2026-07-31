"""Generate the composite SVG figures used to replace monospace diagrams."""

from __future__ import annotations

import math
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "assets" / "figures"

STYLE = """
    .bg{fill:#fffaf0}.panel{fill:none;stroke:#87979a;stroke-width:1.5}
    .ink{fill:none;stroke:#172127;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round}
    .axis{fill:none;stroke:#172127;stroke-width:2;stroke-linecap:round}
    .teal{fill:none;stroke:#006f78;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round}
    .orange{fill:none;stroke:#ad4f16;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round}
    .node{fill:#172127}.txt{fill:#172127;font:20px sans-serif}
    .head{fill:#172127;font:bold 21px sans-serif}.small{fill:#59676d;font:16px sans-serif}
    .math{fill:#172127;font:18px monospace}
    @media(prefers-color-scheme:dark){
      .bg{fill:#121a1d}.panel{stroke:#607076}.ink,.axis{stroke:#e8eee8}.node{fill:#e8eee8}
      .txt,.head,.math{fill:#e8eee8}.small{fill:#aebcb9}
    }
"""


def svg(title: str, desc: str, body: str, *, height: int = 440) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 {height}" role="img">
  <title>{title}</title>
  <desc>{desc}</desc>
  <defs>
    <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" fill="#006f78"/></marker>
    <marker id="arrow-orange" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8Z" fill="#ad4f16"/></marker>
  </defs>
  <style>{STYLE}</style>
  <rect class="bg" width="960" height="{height}"/>
{body}
</svg>
"""


def waveform_path(
    x: float,
    y: float,
    width: float,
    amplitude: float,
    *,
    cycles: float = 1.5,
    phase: float = 0.0,
    clip_top: float | None = None,
    clip_bottom: float | None = None,
) -> str:
    """Return a sampled SVG path; clipping limits are expressed in SVG y coordinates."""
    points: list[str] = []
    for index in range(121):
        ratio = index / 120
        py = y - amplitude * math.sin(2 * math.pi * cycles * ratio + phase)
        if clip_top is not None:
            py = max(py, clip_top)
        if clip_bottom is not None:
            py = min(py, clip_bottom)
        command = "M" if index == 0 else "L"
        points.append(f"{command}{x + width * ratio:.1f},{py:.1f}")
    return " ".join(points)


FIGURES = {
    "basic-circuit-laws.svg": svg(
        "电容参考方向、节点电流与串联回路",
        "三幅图依次展示电容的电压电流参考方向、节点的流入流出电流，以及含电压源和两个串联电阻的KVL回路。",
        """
  <rect class="panel" x="20" y="24" width="292" height="382" rx="8"/>
  <rect class="panel" x="334" y="24" width="292" height="382" rx="8"/>
  <rect class="panel" x="648" y="24" width="292" height="382" rx="8"/>
  <text class="head" x="42" y="60">电容参考方向</text>
  <line class="ink" x1="66" y1="198" x2="142" y2="198"/><line class="ink" x1="142" y1="158" x2="142" y2="238"/>
  <line class="ink" x1="170" y1="158" x2="170" y2="238"/><line class="ink" x1="170" y1="198" x2="258" y2="198"/>
  <circle class="node" cx="66" cy="198" r="5"/><circle class="node" cx="258" cy="198" r="5"/>
  <line class="teal" x1="76" y1="126" x2="210" y2="126" marker-end="url(#arrow)"/>
  <text class="txt" x="128" y="110">i<tspan baseline-shift="sub" font-size="13">C</tspan></text>
  <text class="txt" x="72" y="184">+</text><text class="txt" x="242" y="184">−</text>
  <text class="math" x="64" y="284">vC = V+ − V−</text>
  <text class="small" x="42" y="356">正负号与箭头先定义，</text><text class="small" x="42" y="380">计算符号再说明真实方向。</text>

  <text class="head" x="356" y="60">节点电流</text>
  <circle class="node" cx="480" cy="208" r="7"/>
  <line class="teal" x1="480" y1="100" x2="480" y2="184" marker-end="url(#arrow)"/>
  <line class="teal" x1="456" y1="208" x2="374" y2="208" marker-end="url(#arrow)"/>
  <line class="teal" x1="504" y1="208" x2="588" y2="208" marker-end="url(#arrow)"/>
  <text class="txt" x="492" y="128">i₁</text><text class="txt" x="394" y="190">i₂</text><text class="txt" x="548" y="190">i₃</text>
  <text class="math" x="382" y="292">i₁ = i₂ + i₃</text>
  <text class="small" x="356" y="356">理想节点不储存净电荷：</text><text class="small" x="356" y="380">流入之和等于流出之和。</text>

  <text class="head" x="670" y="60">串联回路与 KVL</text>
  <line class="ink" x1="700" y1="126" x2="700" y2="172"/><circle class="ink" cx="700" cy="220" r="26"/>
  <line class="ink" x1="700" y1="246" x2="700" y2="320"/><line class="ink" x1="700" y1="320" x2="894" y2="320"/>
  <line class="ink" x1="894" y1="320" x2="894" y2="126"/>
  <line class="ink" x1="700" y1="126" x2="730" y2="126"/>
  <polyline class="ink" points="730,126 742,112 758,140 774,112 790,140 802,126"/>
  <line class="ink" x1="802" y1="126" x2="820" y2="126"/>
  <polyline class="ink" points="820,126 832,112 848,140 864,112 880,140 894,126"/>
  <text class="small" x="754" y="100">R₁</text><text class="small" x="846" y="100">R₂</text>
  <text class="txt" x="660" y="226">V<tspan baseline-shift="sub" font-size="13">S</tspan></text>
  <text class="txt" x="706" y="202">+</text><text class="txt" x="706" y="248">−</text>
  <path class="orange" d="M748 282C800 306 858 280 860 220" marker-end="url(#arrow-orange)"/>
  <text class="math" x="690" y="366">VS − iR₁ − iR₂ = 0</text>
""",
    ),
    "semiconductor-foundations.svg": svg(
        "能带与掺杂载流子",
        "左图显示导带、禁带和价带，右图比较n型与p型半导体中的固定离子、多数载流子和少数载流子。",
        """
  <rect class="panel" x="24" y="28" width="438" height="374" rx="8"/>
  <rect class="panel" x="490" y="28" width="446" height="374" rx="8"/>
  <text class="head" x="48" y="66">能带示意</text>
  <line class="axis" x1="82" y1="338" x2="82" y2="92" marker-end="url(#arrow)"/>
  <line class="ink" x1="104" y1="142" x2="424" y2="142"/><line class="ink" x1="104" y1="284" x2="424" y2="284"/>
  <text class="math" x="48" y="150">Ec</text><text class="math" x="48" y="292">Ev</text>
  <text class="txt" x="132" y="124">导带</text><text class="txt" x="132" y="316">价带</text>
  <text class="small" x="176" y="216">禁带 Eg = Ec − Ev</text>
  <circle class="node" cx="196" cy="142" r="7"/><line class="teal" x1="208" y1="114" x2="330" y2="114" marker-end="url(#arrow)"/>
  <text class="small" x="214" y="102">电子运动</text>
  <circle cx="302" cy="284" r="8" fill="none" stroke="#ad4f16" stroke-width="2.5"/>
  <line class="orange" x1="288" y1="254" x2="186" y2="254" marker-end="url(#arrow-orange)"/>
  <text class="small" x="196" y="242">空穴等效运动</text>

  <text class="head" x="514" y="66">掺杂与载流子</text>
  <text class="txt" x="520" y="120">n 型</text><text class="small" x="520" y="146">施主释放电子，体区仍近似电中性</text>
  <circle cx="558" cy="188" r="17" fill="none" stroke="#ad4f16" stroke-width="2"/><text class="small" x="549" y="194">D⁺</text>
  <circle class="node" cx="628" cy="188" r="7"/><circle class="node" cx="670" cy="188" r="7"/><circle class="node" cx="712" cy="188" r="7"/>
  <text class="small" x="614" y="220">多数 e⁻</text><circle cx="856" cy="188" r="8" fill="none" stroke="#ad4f16" stroke-width="2"/><text class="small" x="824" y="220">少数 h⁺</text>
  <line class="panel" x1="520" y1="246" x2="908" y2="246"/>
  <text class="txt" x="520" y="286">p 型</text><text class="small" x="520" y="312">受主接受电子，空穴成为多数载流子</text>
  <circle cx="558" cy="354" r="17" fill="none" stroke="#006f78" stroke-width="2"/><text class="small" x="549" y="360">A⁻</text>
  <circle cx="628" cy="354" r="8" fill="none" stroke="#ad4f16" stroke-width="2"/><circle cx="670" cy="354" r="8" fill="none" stroke="#ad4f16" stroke-width="2"/><circle cx="712" cy="354" r="8" fill="none" stroke="#ad4f16" stroke-width="2"/>
  <text class="small" x="614" y="386">多数 h⁺</text><circle class="node" cx="856" cy="354" r="7"/><text class="small" x="824" y="386">少数 e⁻</text>
""",
    ),
    "diode-bias-iv.svg": svg(
        "二极管偏置回路与电流电压特性",
        "左图给出电源、电阻和二极管构成的完整测试回路与参考方向；右图显示正向指数区、反向漏电区和反向击穿区。",
        """
  <rect class="panel" x="24" y="28" width="450" height="374" rx="8"/>
  <rect class="panel" x="498" y="28" width="438" height="374" rx="8"/>
  <text class="head" x="48" y="66">完整偏置回路</text>
  <circle class="ink" cx="92" cy="224" r="30"/><text class="txt" x="102" y="214">+</text><text class="txt" x="102" y="248">−</text>
  <line class="ink" x1="92" y1="194" x2="92" y2="126"/><line class="ink" x1="92" y1="126" x2="164" y2="126"/>
  <polyline class="ink" points="164,126 178,112 196,140 214,112 232,140 246,126"/>
  <line class="ink" x1="246" y1="126" x2="312" y2="126"/>
  <polygon class="ink" points="312,108 340,126 312,144"/><line class="ink" x1="342" y1="106" x2="342" y2="146"/>
  <line class="ink" x1="342" y1="126" x2="414" y2="126"/><line class="ink" x1="414" y1="126" x2="414" y2="318"/>
  <line class="ink" x1="414" y1="318" x2="92" y2="318"/><line class="ink" x1="92" y1="318" x2="92" y2="254"/>
  <line class="teal" x1="182" y1="86" x2="304" y2="86" marker-end="url(#arrow)"/>
  <text class="txt" x="218" y="76">iD</text><text class="small" x="304" y="174">A</text><text class="small" x="340" y="174">K</text>
  <text class="txt" x="46" y="230">VS</text><text class="txt" x="196" y="174">R</text>
  <text class="small" x="48" y="356">VS &gt; 0：正向偏置；反转电源：反向偏置。</text>

  <text class="head" x="522" y="66">定性 iD–vD 特性</text>
  <line class="axis" x1="548" y1="250" x2="904" y2="250" marker-end="url(#arrow)"/>
  <line class="axis" x1="700" y1="354" x2="700" y2="88" marker-end="url(#arrow)"/>
  <path class="teal" d="M700 250C744 250 770 242 792 214C818 180 842 126 884 88"/>
  <path class="teal" d="M700 256C650 256 612 258 584 264C570 270 558 300 548 338"/>
  <line class="orange" x1="574" y1="250" x2="574" y2="338" stroke-dasharray="6 6"/>
  <text class="small" x="794" y="196">正向指数增长</text><text class="small" x="526" y="286">反向漏电</text>
  <text class="small" x="522" y="360">击穿</text><text class="math" x="850" y="276">vD</text><text class="math" x="710" y="102">iD</text>
  <text class="small" x="724" y="328">0.6–0.8 V 不是固定拐点</text>
""",
    ),
    "diode-dc-analysis.svg": svg(
        "恒压降二极管例题与负载线",
        "左图是5伏电源、1千欧电阻和0.7伏恒压降二极管的串联回路；右图用负载线与二极管曲线的交点表示工作点。",
        """
  <rect class="panel" x="24" y="28" width="450" height="340" rx="8"/>
  <rect class="panel" x="498" y="28" width="438" height="340" rx="8"/>
  <text class="head" x="48" y="66">状态假设后的回路</text>
  <circle class="ink" cx="88" cy="220" r="28"/><text class="txt" x="98" y="210">+</text><text class="txt" x="98" y="244">−</text>
  <line class="ink" x1="88" y1="192" x2="88" y2="116"/><line class="ink" x1="88" y1="116" x2="160" y2="116"/>
  <polyline class="ink" points="160,116 174,102 192,130 210,102 228,130 242,116"/>
  <line class="ink" x1="242" y1="116" x2="314" y2="116"/>
  <polygon class="ink" points="314,98 342,116 314,134"/><line class="ink" x1="344" y1="96" x2="344" y2="136"/>
  <line class="ink" x1="344" y1="116" x2="410" y2="116"/><line class="ink" x1="410" y1="116" x2="410" y2="310"/>
  <line class="ink" x1="410" y1="310" x2="88" y2="310"/><line class="ink" x1="88" y1="310" x2="88" y2="248"/>
  <line class="teal" x1="180" y1="78" x2="300" y2="78" marker-end="url(#arrow)"/>
  <text class="txt" x="214" y="68">iD</text><text class="small" x="48" y="226">5.0 V</text>
  <text class="small" x="174" y="164">1.00 kΩ</text><text class="small" x="300" y="164">vD = 0.70 V</text>
  <text class="math" x="98" y="348">iD = (5.0 − 0.70)/1.00k = 4.30 mA</text>

  <text class="head" x="522" y="66">负载线与工作点 Q</text>
  <line class="axis" x1="548" y1="310" x2="902" y2="310" marker-end="url(#arrow)"/>
  <line class="axis" x1="580" y1="330" x2="580" y2="90" marker-end="url(#arrow)"/>
  <line class="orange" x1="580" y1="112" x2="874" y2="310"/>
  <path class="teal" d="M580 310C700 310 744 306 770 280C800 250 824 188 850 108"/>
  <circle cx="784" cy="266" r="7" fill="#ad4f16"/><text class="txt" x="798" y="258">Q</text>
  <text class="small" x="602" y="126">VS/R</text><text class="small" x="830" y="294">VS</text>
  <text class="small" x="620" y="344">每个候选模型都必须回代检查状态条件。</text>
""",
        height=390,
    ),
    "zener-recovery.svg": svg(
        "齐纳反向稳压与二极管反向恢复",
        "左图展示齐纳二极管反向击穿时由串联电阻限流的回路；右图展示换向后出现反向恢复电流并在trr后回到漏电。",
        """
  <rect class="panel" x="24" y="28" width="450" height="374" rx="8"/>
  <rect class="panel" x="498" y="28" width="438" height="374" rx="8"/>
  <text class="head" x="48" y="66">反向稳压回路</text>
  <circle class="ink" cx="88" cy="224" r="30"/><text class="txt" x="98" y="214">+</text><text class="txt" x="98" y="248">−</text>
  <line class="ink" x1="88" y1="194" x2="88" y2="122"/><line class="ink" x1="88" y1="122" x2="156" y2="122"/>
  <polyline class="ink" points="156,122 170,108 188,136 206,108 224,136 238,122"/>
  <line class="ink" x1="238" y1="122" x2="314" y2="122"/>
  <polygon class="ink" points="350,104 322,122 350,140"/><polyline class="ink" points="320,102 326,108 314,136 320,142"/>
  <line class="ink" x1="350" y1="122" x2="414" y2="122"/><line class="ink" x1="414" y1="122" x2="414" y2="318"/>
  <line class="ink" x1="414" y1="318" x2="88" y2="318"/><line class="ink" x1="88" y1="318" x2="88" y2="254"/>
  <line class="teal" x1="286" y1="82" x2="184" y2="82" marker-end="url(#arrow)"/>
  <text class="txt" x="220" y="70">IZ</text><text class="small" x="48" y="230">VS</text><text class="small" x="184" y="166">限流 R</text>
  <text class="small" x="294" y="166">K　Zener　A</text>
  <text class="small" x="48" y="360">先算串联电流，再用 KCL 分给负载与齐纳支路。</text>

  <text class="head" x="522" y="66">换向与反向恢复</text>
  <line class="axis" x1="542" y1="218" x2="906" y2="218" marker-end="url(#arrow)"/>
  <line class="axis" x1="566" y1="346" x2="566" y2="92" marker-end="url(#arrow)"/>
  <path class="teal" d="M566 132L700 132L700 218L720 292L754 300C790 300 808 270 824 232L892 232"/>
  <line class="orange" x1="700" y1="318" x2="824" y2="318"/>
  <line class="orange" x1="700" y1="310" x2="700" y2="326"/><line class="orange" x1="824" y1="310" x2="824" y2="326"/>
  <text class="math" x="742" y="344">trr</text><text class="small" x="588" y="118">正向 IF</text>
  <text class="small" x="708" y="286">反向抽取</text><text class="small" x="824" y="252">回到漏电</text>
  <text class="small" x="550" y="388">反向电流面积的量级对应恢复电荷 Qrr。</text>
""",
    ),
    "diode-solved-waveforms.svg": svg(
        "二极管分段题的三类波形",
        "三幅图分别给出带偏置半波输出、双向限幅传输与时间波形、以及钳位电路首周期到稳态的关键电平。",
        """
  <rect class="panel" x="18" y="24" width="298" height="430" rx="8"/>
  <rect class="panel" x="331" y="24" width="298" height="430" rx="8"/>
  <rect class="panel" x="644" y="24" width="298" height="430" rx="8"/>
  <text class="head" x="38" y="60">带偏置半波</text>
  <line class="axis" x1="46" y1="224" x2="292" y2="224" marker-end="url(#arrow)"/>
  <line class="axis" x1="66" y1="346" x2="66" y2="88" marker-end="url(#arrow)"/>
  <path class="teal" d="M66 224L120 224C150 224 164 310 194 316C224 310 238 224 270 224"/>
  <circle cx="194" cy="316" r="5" fill="#ad4f16"/>
  <text class="small" x="82" y="206">OFF：vo=0</text><text class="small" x="124" y="338">ON：vo=vi+0.65 V</text>
  <text class="math" x="84" y="390">189.35° &lt; θ &lt; 350.65°</text>
  <text class="small" x="38" y="426">先标换区角，再写每段方程。</text>

  <text class="head" x="351" y="60">双向限幅</text>
  <line class="axis" x1="356" y1="218" x2="604" y2="218" marker-end="url(#arrow)"/>
  <line class="axis" x1="480" y1="340" x2="480" y2="88" marker-end="url(#arrow)"/>
  <path class="teal" d="M370 300L420 300L540 136L594 136"/>
  <line class="orange" x1="350" y1="136" x2="606" y2="136" stroke-dasharray="5 5"/>
  <line class="orange" x1="350" y1="300" x2="606" y2="300" stroke-dasharray="5 5"/>
  <text class="small" x="532" y="124">+2.15 V</text><text class="small" x="532" y="324">−2.65 V</text>
  <text class="math" x="360" y="386">vo = clamp(vi, −2.65, +2.15)</text>
  <text class="small" x="351" y="426">中段斜率为 1，越界后进入平台。</text>

  <text class="head" x="664" y="60">钳位：首周期与稳态</text>
  <line class="axis" x1="666" y1="238" x2="920" y2="238" marker-end="url(#arrow)"/>
  <line class="axis" x1="686" y1="354" x2="686" y2="88" marker-end="url(#arrow)"/>
  <path class="teal" d="M686 238C720 238 734 112 768 112C802 112 816 306 850 306C884 306 896 112 918 112"/>
  <line class="orange" x1="684" y1="306" x2="920" y2="306" stroke-dasharray="5 5"/>
  <text class="small" x="700" y="100">首个正峰 +3.00 V</text><text class="small" x="700" y="330">导通钳到 −0.65 V</text>
  <text class="math" x="680" y="388">稳态理想保持：正峰 +5.35 V</text>
  <text class="small" x="664" y="426">有限 RC 时关断段出现约 45 mV 下垂。</text>
""",
        height=480,
    ),
    "bode-solved-examples.svg": svg(
        "一阶RC与多拐点Bode图",
        "三幅图依次展示一阶低通的精确角频率和阶跃时间常数、带通网络的斜率变化、以及零点和极点造成的渐近斜率与相位方向。",
        """
  <rect class="panel" x="18" y="24" width="298" height="430" rx="8"/>
  <rect class="panel" x="331" y="24" width="298" height="430" rx="8"/>
  <rect class="panel" x="644" y="24" width="298" height="430" rx="8"/>
  <text class="head" x="38" y="60">一阶 RC 低通</text>
  <line class="axis" x1="46" y1="310" x2="294" y2="310" marker-end="url(#arrow)"/>
  <line class="axis" x1="66" y1="336" x2="66" y2="88" marker-end="url(#arrow)"/>
  <path class="teal" d="M66 118C140 118 166 120 192 144C220 170 248 226 286 282"/>
  <line class="orange" x1="192" y1="98" x2="192" y2="310" stroke-dasharray="5 5"/>
  <circle cx="192" cy="144" r="6" fill="#ad4f16"/>
  <text class="small" x="198" y="136">fc：−3.010 dB</text><text class="small" x="198" y="330">4.980 kHz</text>
  <text class="math" x="46" y="376">τ = 31.96 μs</text><text class="small" x="38" y="418">t=τ 时阶跃达到终值的 63.2%。</text>

  <text class="head" x="351" y="60">多拐点带通</text>
  <line class="axis" x1="352" y1="310" x2="608" y2="310" marker-end="url(#arrow)"/>
  <line class="axis" x1="372" y1="336" x2="372" y2="88" marker-end="url(#arrow)"/>
  <polyline class="teal" points="372,284 414,230 452,178 532,178 568,232 602,286"/>
  <line class="orange" x1="452" y1="178" x2="532" y2="178"/>
  <text class="small" x="390" y="274">+40</text><text class="small" x="418" y="218">+20</text>
  <text class="small" x="470" y="164">0 dB/dec</text><text class="small" x="548" y="218">−20</text><text class="small" x="576" y="274">−40</text>
  <text class="math" x="356" y="376">fL ≈ 211.5 Hz</text><text class="math" x="474" y="400">fH ≈ 19.80 kHz</text>
  <text class="small" x="351" y="428">每遇一个零点斜率 +20，</text>
  <text class="small" x="351" y="450">每遇一个极点 −20。</text>

  <text class="head" x="664" y="60">零点、极点与相位</text>
  <line class="axis" x1="668" y1="310" x2="918" y2="310" marker-end="url(#arrow)"/>
  <line class="axis" x1="688" y1="336" x2="688" y2="88" marker-end="url(#arrow)"/>
  <polyline class="teal" points="688,270 748,270 794,202 852,202 910,270"/>
  <text class="small" x="716" y="288">0</text><text class="small" x="752" y="236">+20</text><text class="small" x="804" y="190">0</text><text class="small" x="864" y="236">−20</text>
  <text class="math" x="670" y="366">LHP 零点：0° → +90°</text>
  <text class="math" x="670" y="390">RHP 零点：0° → −90°</text>
  <text class="small" x="664" y="420">幅频可以相同；</text>
  <text class="small" x="664" y="442">相位方向决定稳定性含义。</text>
""",
        height=480,
    ),
    "independent-sources.svg": svg(
        "理想独立电压源与电流源",
        "左图规定电压源端电压而电流由外电路决定；右图规定电流源支路电流而端电压由外电路决定。",
        """
  <rect class="panel" x="24" y="28" width="438" height="340" rx="8"/>
  <rect class="panel" x="490" y="28" width="446" height="340" rx="8"/>
  <text class="head" x="48" y="66">理想电压源</text><text class="head" x="514" y="66">理想电流源</text>
  <circle class="node" cx="244" cy="94" r="6"/><circle class="node" cx="244" cy="302" r="6"/>
  <line class="ink" x1="244" y1="94" x2="244" y2="144"/><circle class="ink" cx="244" cy="198" r="38"/><line class="ink" x1="244" y1="236" x2="244" y2="302"/>
  <text class="txt" x="254" y="178">+</text><text class="txt" x="254" y="226">−</text><text class="txt" x="184" y="204">VS</text>
  <line class="teal" x1="308" y1="120" x2="308" y2="250" marker-end="url(#arrow)"/><text class="small" x="320" y="192">iv</text>
  <text class="math" x="76" y="334">vab = Va − Vb = VS；iv 由外电路决定</text>
  <circle class="node" cx="710" cy="94" r="6"/><circle class="node" cx="710" cy="302" r="6"/>
  <line class="ink" x1="710" y1="94" x2="710" y2="144"/><circle class="ink" cx="710" cy="198" r="38"/><line class="ink" x1="710" y1="236" x2="710" y2="302"/>
  <line class="teal" x1="710" y1="162" x2="710" y2="226" marker-end="url(#arrow)"/><text class="txt" x="762" y="204">IS</text>
  <text class="txt" x="728" y="132">+</text><text class="txt" x="728" y="286">−</text>
  <text class="math" x="532" y="334">is(a→b) = IS；vab 由外电路决定</text>
""",
        height=390,
    ),
    "network-equivalents.svg": svg(
        "节点分析电路与戴维南诺顿等效",
        "左图是十二伏电源、两个电阻和一毫安电流源构成的节点电路；右图比较同一端口的戴维南电压源串联电阻与诺顿电流源并联电阻。",
        """
  <rect class="panel" x="20" y="24" width="520" height="392" rx="8"/>
  <rect class="panel" x="560" y="24" width="380" height="392" rx="8"/>
  <text class="head" x="42" y="60">节点与端口</text>
  <circle class="ink" cx="82" cy="220" r="28"/><text class="small" x="40" y="226">12 V</text>
  <line class="ink" x1="82" y1="192" x2="82" y2="112"/><line class="ink" x1="82" y1="112" x2="154" y2="112"/>
  <polyline class="ink" points="154,112 168,98 186,126 204,98 222,126 236,112"/><line class="ink" x1="236" y1="112" x2="334" y2="112"/>
  <circle class="node" cx="334" cy="112" r="6"/><text class="small" x="344" y="104">a，Va</text>
  <polyline class="ink" points="334,112 320,132 348,154 320,176 348,198 334,218"/><line class="ink" x1="334" y1="218" x2="334" y2="328"/>
  <circle class="ink" cx="438" cy="220" r="26"/><line class="teal" x1="438" y1="242" x2="438" y2="196" marker-end="url(#arrow)"/>
  <line class="ink" x1="438" y1="194" x2="438" y2="112"/><line class="ink" x1="438" y1="112" x2="334" y2="112"/>
  <line class="ink" x1="438" y1="246" x2="438" y2="328"/><line class="ink" x1="438" y1="328" x2="82" y2="328"/><line class="ink" x1="82" y1="328" x2="82" y2="248"/>
  <text class="small" x="166" y="88">R1=2 kΩ</text><text class="small" x="350" y="170">R2=4 kΩ</text><text class="small" x="450" y="226">1 mA</text>
  <text class="math" x="42" y="378">端口电压 v = Va − Vb；参考电流按箭头定义</text>

  <text class="head" x="582" y="60">同一端口的两种等效</text>
  <text class="small" x="584" y="98">戴维南</text><circle class="ink" cx="614" cy="180" r="24"/>
  <line class="ink" x1="614" y1="156" x2="614" y2="126"/><polyline class="ink" points="614,126 630,112 650,140 670,112 690,140 706,126"/>
  <line class="ink" x1="706" y1="126" x2="748" y2="126"/><circle class="node" cx="748" cy="126" r="5"/>
  <line class="ink" x1="748" y1="126" x2="748" y2="236"/><line class="ink" x1="748" y1="236" x2="614" y2="236"/><line class="ink" x1="614" y1="236" x2="614" y2="204"/>
  <text class="small" x="644" y="102">Rth</text><text class="small" x="574" y="186">Vth</text>
  <text class="small" x="780" y="98">诺顿</text><circle class="ink" cx="812" cy="180" r="24"/><line class="teal" x1="812" y1="194" x2="812" y2="164" marker-end="url(#arrow)"/>
  <line class="ink" x1="812" y1="156" x2="812" y2="126"/><line class="ink" x1="812" y1="126" x2="910" y2="126"/>
  <polyline class="ink" points="882,126 868,142 896,162 868,182 896,202 882,220"/><line class="ink" x1="882" y1="220" x2="882" y2="236"/>
  <line class="ink" x1="910" y1="126" x2="910" y2="236"/><line class="ink" x1="910" y1="236" x2="812" y2="236"/><line class="ink" x1="812" y1="236" x2="812" y2="204"/>
  <text class="small" x="824" y="186">IN</text><text class="small" x="892" y="178">Rth</text>
  <text class="math" x="590" y="326">Vth = IN Rth</text><text class="small" x="582" y="366">开路电压相同，短路电流相同。</text>
""",
    ),
    "rc-transient.svg": svg(
        "RC切换回路与一阶响应",
        "左图展示电压源、开关、电阻和电容构成的完整充电回路；右图展示电容电压从V0指数趋近Vf并在一个时间常数达到总变化的63.2%。",
        """
  <rect class="panel" x="24" y="28" width="450" height="374" rx="8"/>
  <rect class="panel" x="498" y="28" width="438" height="374" rx="8"/>
  <text class="head" x="48" y="66">完整 RC 切换回路</text>
  <circle class="ink" cx="86" cy="228" r="28"/><text class="txt" x="96" y="218">+</text><text class="txt" x="96" y="252">−</text>
  <line class="ink" x1="86" y1="200" x2="86" y2="116"/><line class="ink" x1="86" y1="116" x2="146" y2="116"/>
  <circle class="node" cx="146" cy="116" r="4"/><circle class="node" cx="198" cy="116" r="4"/><line class="ink" x1="150" y1="112" x2="190" y2="94"/>
  <line class="ink" x1="198" y1="116" x2="228" y2="116"/><polyline class="ink" points="228,116 242,102 260,130 278,102 296,130 310,116"/>
  <line class="ink" x1="310" y1="116" x2="392" y2="116"/><line class="ink" x1="374" y1="168" x2="410" y2="168"/><line class="ink" x1="374" y1="190" x2="410" y2="190"/>
  <line class="ink" x1="392" y1="116" x2="392" y2="168"/><line class="ink" x1="392" y1="190" x2="392" y2="320"/>
  <line class="ink" x1="392" y1="320" x2="86" y2="320"/><line class="ink" x1="86" y1="320" x2="86" y2="256"/>
  <line class="teal" x1="228" y1="78" x2="346" y2="78" marker-end="url(#arrow)"/>
  <text class="small" x="256" y="68">iC(t)</text><text class="small" x="48" y="234">Vf</text><text class="small" x="258" y="158">R</text><text class="small" x="416" y="184">C</text>
  <text class="math" x="60" y="364">vC(t)=Vf+(V0−Vf)e^(−t/RC)</text>

  <text class="head" x="522" y="66">从 V0 趋近 Vf</text>
  <line class="axis" x1="548" y1="326" x2="906" y2="326" marker-end="url(#arrow)"/>
  <line class="axis" x1="574" y1="348" x2="574" y2="88" marker-end="url(#arrow)"/>
  <line class="orange" x1="574" y1="112" x2="896" y2="112" stroke-dasharray="6 6"/>
  <path class="teal" d="M574 290C626 290 636 210 676 168C724 118 798 114 894 112"/>
  <circle cx="676" cy="168" r="7" fill="#ad4f16"/><line class="orange" x1="676" y1="168" x2="676" y2="326" stroke-dasharray="5 5"/>
  <text class="small" x="584" y="282">V0</text><text class="small" x="834" y="102">Vf</text>
  <text class="small" x="690" y="160">t=τ：完成 63.2%</text><text class="math" x="664" y="350">τ=RC</text>
  <text class="small" x="522" y="386">有限电流下，电容电压在切换瞬间连续。</text>
""",
    ),
}

FIGURES["figure-4-07.svg"] = svg(
    "简单共射极放大器的反相输出与两侧削顶",
    "左侧用同一时间轴对齐基极增量与反相集电极输出；中图显示静态集电极电流过高时的底部削顶；右图显示静态集电极电流过低时的顶部削顶。",
    f"""
  <rect class="panel" x="18" y="24" width="304" height="430" rx="8"/>
  <rect class="panel" x="338" y="24" width="294" height="430" rx="8"/>
  <rect class="panel" x="648" y="24" width="294" height="430" rx="8"/>

  <text class="head" x="38" y="60">线性区：输入与输出反相</text>
  <line class="axis" x1="48" y1="164" x2="298" y2="164" marker-end="url(#arrow)"/>
  <line class="axis" x1="48" y1="344" x2="298" y2="344" marker-end="url(#arrow)"/>
  <line class="ink" x1="48" y1="96" x2="48" y2="212"/>
  <line class="ink" x1="48" y1="264" x2="48" y2="412"/>
  <path class="teal" d="{waveform_path(48, 164, 232, 46)}"/>
  <path class="orange" d="{waveform_path(48, 344, 232, 62, phase=math.pi)}"/>
  <text class="math" x="58" y="108">vb(t)</text>
  <text class="math" x="58" y="278">vc(t)−VCQ</text>
  <line class="teal" x1="138" y1="112" x2="138" y2="136" marker-end="url(#arrow)"/>
  <line class="orange" x1="138" y1="372" x2="138" y2="402" marker-end="url(#arrow-orange)"/>
  <text class="small" x="160" y="122">正输入峰</text>
  <text class="small" x="160" y="410">负输出峰</text>
  <text class="small" x="40" y="442">vb↑ → ic↑ → vC=VCC−icRC↓</text>

  <text class="head" x="358" y="60">ICQ 过高：底部削平</text>
  <line class="axis" x1="366" y1="256" x2="610" y2="256" marker-end="url(#arrow)"/>
  <line class="ink" x1="366" y1="92" x2="366" y2="382"/>
  <line class="orange" x1="366" y1="330" x2="606" y2="330" stroke-dasharray="5 5"/>
  <path class="orange" d="{waveform_path(366, 246, 228, 102, phase=math.pi, clip_bottom=330)}"/>
  <text class="small" x="374" y="352">VCE,sat ≈ 0.2 V</text>
  <text class="small" x="360" y="406">正 vb → ic↑ → vC↓，</text>
  <text class="small" x="360" y="430">先碰饱和边界。</text>

  <text class="head" x="668" y="60">ICQ 过低：顶部削平</text>
  <line class="axis" x1="676" y1="256" x2="920" y2="256" marker-end="url(#arrow)"/>
  <line class="ink" x1="676" y1="92" x2="676" y2="382"/>
  <line class="orange" x1="676" y1="124" x2="916" y2="124" stroke-dasharray="5 5"/>
  <path class="orange" d="{waveform_path(676, 230, 228, 112, phase=math.pi, clip_top=124)}"/>
  <text class="small" x="684" y="116">VCC = 10 V</text>
  <text class="small" x="670" y="406">负 vb → ic↓ → vC↑，</text>
  <text class="small" x="670" y="430">先碰电源上限。</text>
""",
    height=480,
)


def chapter3_semantic_figures() -> dict[str, str]:
    flow = lambda title, desc, labels: svg(
        title,
        desc,
        "".join(
            f'<rect class="panel" x="{40+i*220}" y="120" width="180" height="150" rx="12"/>'
            f'<text class="head" x="{60+i*220}" y="165">{escape(label[0])}</text>'
            f'<text class="small" x="{60+i*220}" y="205">{escape(label[1])}</text>'
            + (
                f'<line class="teal" x1="{220+i*220}" y1="195" x2="{255+i*220}" y2="195" marker-end="url(#arrow)"/>'
                if i < len(labels) - 1
                else ""
            )
            for i, label in enumerate(labels)
        ),
        height=360,
    )
    figures = {
        "figure-3-02.svg": flow(
            "NPN 结构、端子角色与统一参考方向",
            "发射区注入电子，薄基区只有少量复合，集电区借助反偏电场收集大部分电子；传统电流方向与电子运动相反。",
            [("E：n⁺", "高效注入电子"), ("B：薄 p", "少量复合形成 IB"), ("C：n", "反偏收集形成 IC"), ("端口参考", "IB、IC 流入；IE 流出")],
        ),
        "figure-3-03.svg": flow(
            "正向有源区的载流子输运链",
            "电子从发射极经薄基区扩散到集电结，再由电场扫入集电极；少量复合需要基极补充电荷。",
            [("BE 势垒降低", "VBE 正向偏置"), ("发射极注入", "电子进入薄基区"), ("扩散与复合", "少量形成 IB"), ("BC 结收集", "大部分形成 IC")],
        ),
        "figure-3-11.svg": flow(
            "增强型 NMOS 的零栅偏、耗尽与反型序列",
            "栅压升高先排斥表面空穴形成耗尽区，超过阈值后电子反型层把源漏连接成可控沟道。",
            [("VGS = 0", "p 型表面，无 n 沟道"), ("0 < VGS < VTH", "空穴被排斥，形成耗尽"), ("VGS > VTH", "电子反型层形成"), ("继续升高", "沟道电荷增加")],
        ),
        "figure-3-13.svg": flow(
            "沟道渐变与夹断",
            "VDS 增大使漏端沟道电荷逐渐减少；在VDS等于过驱动电压时漏端刚夹断，载流子仍被强电场扫向漏极。",
            [("小 VDS", "连续反型沟道"), ("VDS 增大", "漏端沟道变薄"), ("VDS = VOV", "漏端刚夹断"), ("VDS > VOV", "夹断区延伸，电流不为零")],
        ),
        "figure-3-18.svg": flow(
            "两类晶体管的端口控制表述",
            "BJT与NMOS都以控制端口电压产生增量输出电流，但BJT有有限rπ，理想低频MOS栅端没有电导电流。",
            [("BJT 输入", "vbe 与 rπ"), ("BJT 输出", "ic = gm·vbe"), ("NMOS 输入", "vgs，理想栅流为零"), ("NMOS 输出", "id = gm·vgs")],
        ),
    }
    figures["figure-3-04.svg"] = svg(
        "由 BE、BC 两个结偏置构成的 BJT 工作区地图",
        "二维工作区表按BE结与BC结是否正向偏置区分截止、正向有源、饱和和反向相关状态。",
        """
  <text class="head" x="360" y="52">BC 结偏置</text><text class="head" x="225" y="105">反偏</text><text class="head" x="585" y="105">正偏</text>
  <text class="head" x="34" y="195">BE 未正偏</text><text class="head" x="34" y="330">BE 正偏</text>
  <rect class="panel" x="190" y="120" width="330" height="130" rx="8"/><rect class="panel" x="530" y="120" width="330" height="130" rx="8"/>
  <rect class="panel" x="190" y="260" width="330" height="130" rx="8"/><rect class="panel" x="530" y="260" width="330" height="130" rx="8"/>
  <text class="head" x="290" y="185">截止</text><text class="small" x="250" y="220">通常 IC ≈ 0</text>
  <text class="head" x="620" y="185">反向相关状态</text><text class="small" x="635" y="220">冲刺轨不使用</text>
  <text class="head" x="285" y="325">正向有源</text><text class="small" x="260" y="360">IC ≈ βIB</text>
  <text class="head" x="650" y="325">饱和</text><text class="small" x="600" y="360">两结均正偏</text>
""",
    )
    figures["figure-3-07.svg"] = svg(
        "固定基极偏置电路的直流负载线",
        "负载线连接VCE等于零时的五毫安截距与IC等于零时的十伏截距，Q点位于六点零四伏和一点九八毫安。",
        """
  <line class="axis" x1="120" y1="370" x2="880" y2="370" marker-end="url(#arrow)"/><line class="axis" x1="120" y1="370" x2="120" y2="60" marker-end="url(#arrow)"/>
  <line class="orange" x1="120" y1="85" x2="820" y2="370"/><circle cx="543" cy="198" r="8" fill="#006f78"/>
  <line class="teal" x1="543" y1="198" x2="543" y2="370" stroke-dasharray="6 6"/><line class="teal" x1="120" y1="198" x2="543" y2="198" stroke-dasharray="6 6"/>
  <text class="head" x="560" y="185">Q (6.04 V, 1.98 mA)</text><text class="txt" x="48" y="90">5.0 mA</text><text class="txt" x="790" y="402">10.0 V</text>
  <text class="math" x="390" y="432">IC = (10.0 V − VCE) / 2.00 kΩ</text>
""",
        height=460,
    )
    figures["figure-3-09.svg"] = local_linearization("BJT 指数特性在 Q 点的局部线性化", quadratic=False)
    figures["figure-3-17.svg"] = local_linearization("NMOS 饱和平方律在 Q 点的局部线性化", quadratic=True)
    figures["figure-3-10.svg"] = svg(
        "增强型 NMOS 的截面直觉与端口参考",
        "绝缘栅位于氧化层上方，源漏为n加区，正栅压形成表面反型沟道；漏电流从D流入并从S流出。",
        """
  <rect class="panel" x="60" y="70" width="840" height="300" rx="12"/><rect x="310" y="95" width="340" height="55" fill="#87979a"/><text class="head" x="420" y="130">G：绝缘栅</text>
  <rect x="180" y="210" width="150" height="95" fill="#006f78" opacity=".25"/><rect x="630" y="210" width="150" height="95" fill="#006f78" opacity=".25"/>
  <text class="head" x="230" y="265">S：n⁺</text><text class="head" x="680" y="265">D：n⁺</text><text class="small" x="405" y="190">SiO₂ 绝缘层</text>
  <path class="teal" d="M330 250C430 215 530 215 630 250" marker-end="url(#arrow)"/><text class="txt" x="405" y="235">反型沟道</text>
  <text class="small" x="360" y="340">p 型体区 B 与 S 相连；VGS=VG−VS，VDS=VD−VS</text>
""",
    )
    figures["figure-3-12.svg"] = svg(
        "长沟道 NMOS 输出特性的区域图",
        "多条输出特性从三极管区弯曲进入饱和区，边界随各条曲线的过驱动电压变化。",
        """
  <line class="axis" x1="100" y1="390" x2="890" y2="390" marker-end="url(#arrow)"/><line class="axis" x1="100" y1="390" x2="100" y2="55" marker-end="url(#arrow)"/>
  <path class="teal" d="M100 390C190 310 250 300 350 300L850 300"/><path class="teal" d="M100 390C210 230 300 210 430 210L850 210"/>
  <path class="teal" d="M100 390C220 150 350 120 520 120L850 120"/><path class="orange" d="M150 350L550 90" stroke-dasharray="7 7"/>
  <text class="head" x="600" y="95">VGS3 &gt; VGS2 &gt; VGS1</text><text class="txt" x="215" y="430">三极管区</text><text class="txt" x="610" y="430">饱和区</text>
  <text class="small" x="450" y="80">边界 VDS = VOV</text>
""",
        height=460,
    )
    return figures


def local_linearization(title: str, *, quadratic: bool) -> str:
    curve = "M120 370C280 360 400 305 540 170C650 85 760 65 850 55" if quadratic else "M120 370C420 365 555 330 650 220C730 125 790 80 850 55"
    return svg(
        title,
        "非线性器件特性在静态工作点Q附近用切线近似，切线斜率为跨导gm；小信号增量必须足够小。",
        f"""
  <line class="axis" x1="100" y1="390" x2="890" y2="390" marker-end="url(#arrow)"/><line class="axis" x1="100" y1="390" x2="100" y2="55" marker-end="url(#arrow)"/>
  <path class="teal" d="{curve}"/><line class="orange" x1="390" y1="330" x2="820" y2="80"/>
  <circle cx="600" cy="208" r="9" fill="#172127"/><text class="head" x="620" y="205">Q</text>
  <line class="panel" x1="600" y1="208" x2="600" y2="390" stroke-dasharray="6 6"/><line class="panel" x1="100" y1="208" x2="600" y2="208" stroke-dasharray="6 6"/>
  <text class="txt" x="650" y="135">局部切线斜率 gm</text><text class="small" x="235" y="435">总量 = Q 点直流量 + 小信号增量</text>
""",
        height=460,
    )


FIGURES.update(chapter3_semantic_figures())


def chapter4_semantic_figures() -> dict[str, str]:
    def chain(title: str, desc: str, steps: list[tuple[str, str]], *, foot: str = "") -> str:
        width = 190
        gap = 38
        start = 35
        body = ""
        for index, (head, detail) in enumerate(steps):
            x = start + index * (width + gap)
            detail_lines = [part.strip() for part in detail.split("；")]
            if len(detail_lines) == 1:
                detail_markup = (
                    f'<text class="small" x="{x + 18}" y="202">'
                    f"{escape(detail_lines[0])}</text>"
                )
            else:
                first_y = 188
                tspans = "".join(
                    f'<tspan x="{x + 18}" y="{first_y + line_index * 24}">'
                    f"{escape(line)}</tspan>"
                    for line_index, line in enumerate(detail_lines)
                )
                detail_markup = f'<text class="small">{tspans}</text>'
            body += (
                f'<rect class="panel" x="{x}" y="115" width="{width}" height="160" rx="12"/>'
                f'<text class="head" x="{x + 18}" y="160">{escape(head)}</text>'
                f"{detail_markup}"
            )
            if index < len(steps) - 1:
                body += f'<line class="teal" x1="{x + width}" y1="195" x2="{x + width + 30}" y2="195" marker-end="url(#arrow)"/>'
        if foot:
            body += f'<text class="small" x="50" y="330">{escape(foot)}</text>'
        return svg(title, desc, body, height=370)

    figures = {
        "figure-4-02.svg": chain(
            "放大器的能量与信号角色",
            "输入信号控制有源器件从直流电源向负载传递能量；负载功率不是由输入源直接提供。",
            [("信号源", "vs、Rs 与输入返回"), ("控制端口", "小信号决定器件电流"), ("直流电源", "提供平均功率"), ("负载", "获得输出信号与功率")],
            foot="参考方向：vi、vo 均为节点对地电压；输出能量来自 VCC/VDD。",
        ),
        "figure-4-04.svg": chain(
            "从源到负载的电压链",
            "总电压传递依次包含输入分压、开路级增益和输出加载，三个因子不得重复计入。",
            [("vs", "理想源电压"), ("vi", "× Rin/(Rs+Rin)"), ("vo,oc", "× Av0，保留符号"), ("vL", "× RL/(Rout+RL)")],
            foot="Gv = vL/vs；每个电压都以同一公共地为参考。",
        ),
        "figure-4-16.svg": chain(
            "CE、CC、CB 的公共端与信号方向",
            "三种BJT基本组态按输入端、交流公共端和输出端区分，公共端仍可承载直流电流。",
            [("CE 共射", "输入 B；公共 E；输出 C 反相"), ("CC 共集", "输入 B；公共 C；输出 E 跟随"), ("CB 共基", "输入 E；公共 B；输出 C 同相")],
            foot="比较条件：中频、小信号、相同参考方向并忽略 ro。",
        ),
        "figure-4-19.svg": chain(
            "MOS 源极退化的局部因果链",
            "源极电阻让漏电流增加抬高源电压，从而减小vgs并抵消一部分原变化，同时漏极输出仍反相。",
            [("vg 上升", "控制端变化"), ("vgs 上升", "id = gm·vgs 增加"), ("vs 上升", "vs = id·RS"), ("局部抵消", "vgs = vg−vs 减小")],
            foot="漏极：id↑ → RD 压降↑ → vo↓；RS 未被旁路。",
        ),
        "figure-4-21.svg": chain(
            "从理想源到负载的幅值账本",
            "输入分压、反相级增益和输出加载依次作用于同一信号，负号表示相位反转而不是负幅值。",
            [("10.0 mVpk", "理想源 vs"), ("7.50 mVpk", "输入分压后 vi"), ("−0.804 Vpk", "开路输出估计"), ("−0.659 Vpk", "负载端 vL")],
            foot="低失真检查还需确认 |vbe| ≪ VT；不能只核对比例。",
        ),
    }
    figures["figure-4-03.svg"] = svg(
        "输入、输出电阻的测试源定义",
        "输入电阻测试在实际输出终端下由输入测试源测vt除以it；输出电阻测试移除负载、将独立信号源置零并保留受控源与反馈。",
        """
  <rect class="panel" x="30" y="65" width="430" height="310" rx="12"/><rect class="panel" x="500" y="65" width="430" height="310" rx="12"/>
  <text class="head" x="55" y="105">(a) 测 Rin：输出保持实际终端</text>
  <circle class="ink" cx="90" cy="225" r="28"/><text class="small" x="66" y="230">vt</text>
  <line class="teal" x1="120" y1="185" x2="205" y2="185" marker-end="url(#arrow)"/><text class="small" x="145" y="173">it</text>
  <rect class="panel" x="205" y="155" width="150" height="90" rx="8"/><text class="txt" x="235" y="207">放大级</text>
  <line class="ink" x1="355" y1="200" x2="405" y2="200"/><text class="txt" x="380" y="180">RL</text>
  <text class="math" x="130" y="330">Rin = vt / it</text>
  <text class="head" x="525" y="105">(b) 测 Rout：RL 移除</text>
  <rect class="panel" x="545" y="155" width="170" height="90" rx="8"/><text class="txt" x="572" y="192">受控源与反馈</text><text class="small" x="590" y="220">全部保留</text>
  <line class="ink" x1="715" y1="200" x2="780" y2="200"/><circle class="ink" cx="820" cy="225" r="28"/><text class="small" x="800" y="230">vt</text>
  <line class="teal" x1="865" y1="185" x2="780" y2="185" marker-end="url(#arrow)"/><text class="small" x="815" y="173">it</text>
  <text class="math" x="625" y="330">Rout = vt / it</text>
""",
    )
    figures["figure-4-06.svg"] = svg(
        "数值负载线与近对称 Q 点",
        "十伏共射极电路的负载线连接零伏五毫安与十伏零毫安，Q点位于五点二三一伏和二点三八五毫安，靠近两侧摆幅余量对称位置。",
        """
  <line class="axis" x1="110" y1="390" x2="890" y2="390" marker-end="url(#arrow)"/><line class="axis" x1="110" y1="390" x2="110" y2="55" marker-end="url(#arrow)"/>
  <line class="orange" x1="110" y1="78" x2="840" y2="390"/><circle cx="492" cy="229" r="9" fill="#006f78"/>
  <line class="teal" x1="492" y1="229" x2="492" y2="390" stroke-dasharray="6 6"/><line class="teal" x1="110" y1="229" x2="492" y2="229" stroke-dasharray="6 6"/>
  <circle cx="125" cy="85" r="6" fill="#ad4f16"/><text class="small" x="145" y="95">饱和边界约 (0.20 V, 4.90 mA)</text>
  <text class="head" x="510" y="220">Q (5.231 V, 2.385 mA)</text><text class="math" x="325" y="440">斜率 = −1/RC = −0.500 mA/V</text>
""",
        height=470,
    )
    figures["figure-4-24.svg"] = svg(
        "统一电压参考下的 CE 和 CS 削顶画廊",
        "三幅波形分别表示线性反相输出、截止侧的顶部削平和强导通侧的底部削平，纵轴均为集电极或漏极对地电压。",
        f"""
  <rect class="panel" x="20" y="35" width="290" height="390" rx="10"/><rect class="panel" x="335" y="35" width="290" height="390" rx="10"/><rect class="panel" x="650" y="35" width="290" height="390" rx="10"/>
  <text class="head" x="45" y="78">线性反相输出</text><text class="head" x="360" y="78">截止侧：顶部削平</text><text class="head" x="675" y="78">强导通侧：底部削平</text>
  <line class="axis" x1="50" y1="255" x2="285" y2="255" marker-end="url(#arrow)"/><path class="teal" d="{waveform_path(50,255,220,90,phase=math.pi)}"/>
  <line class="axis" x1="365" y1="255" x2="600" y2="255" marker-end="url(#arrow)"/><path class="orange" d="{waveform_path(365,255,220,115,phase=math.pi,clip_top=145)}"/>
  <line class="axis" x1="680" y1="255" x2="915" y2="255" marker-end="url(#arrow)"/><path class="orange" d="{waveform_path(680,255,220,115,phase=math.pi,clip_bottom=345)}"/>
  <text class="small" x="50" y="390">正输入使 vo 向下</text><text class="small" x="365" y="390">vo ≈ VCC/VDD</text><text class="small" x="680" y="390">vo 接近低压工作区边界</text>
""",
        height=460,
    )
    return figures


FIGURES.update(chapter4_semantic_figures())


def chapter5_semantic_figures() -> dict[str, str]:
    def chain(title: str, desc: str, steps: list[tuple[str, str]], *, loop: bool = False) -> str:
        body = ""
        for index, (head, detail) in enumerate(steps):
            x = 45 + index * 225
            body += (
                f'<rect class="panel" x="{x}" y="115" width="185" height="150" rx="12"/>'
                f'<text class="head" x="{x + 18}" y="157">{escape(head)}</text>'
                f'<text class="small" x="{x + 18}" y="202">{escape(detail)}</text>'
            )
            if index < len(steps) - 1:
                body += f'<line class="teal" x1="{x + 185}" y1="190" x2="{x + 215}" y2="190" marker-end="url(#arrow)"/>'
        if loop:
            body += '<path class="orange" d="M865 285C840 345 135 345 65 285" marker-end="url(#arrow-orange)"/><text class="small" x="350" y="338">返回变化沿闭环抵消或强化原扰动</text>'
        return svg(title, desc, body, height=380)

    figures = {
        "figure-5-04.svg": chain(
            "信号控制与能量路径",
            "运放差分输入只控制输出级，负载电流和功率由正负电源提供。",
            [("差分输入", "vd = v+−v−"), ("开环增益", "控制输出级"), ("±12 V 电源", "提供负载能量"), ("RL = 2 kΩ", "8 V 时为 4 mA")],
        ),
        "figure-5-05.svg": chain(
            "反相端取样的负反馈方向检查",
            "若输出上升使反相输入上升，则差分输入下降，运放驱动输出回落并抵消原扰动。",
            [("vo 上升", "假设一个小扰动"), ("v− 上升", "反馈网络取样"), ("vd 下降", "v+ 暂不变"), ("vo 回落", "抵消原变化")],
            loop=True,
        ),
        "figure-5-06.svg": chain(
            "正反馈的自增强方向",
            "输出回送同相端时，输出上升令差分输入增加，运放进一步推高输出，形成状态翻转而非线性虚短。",
            [("vo 上升", "初始扰动"), ("v+ 上升", "正反馈取样"), ("vd 上升", "v− 暂不变"), ("vo 继续上升", "强化原变化")],
            loop=True,
        ),
        "figure-5-15.svg": chain(
            "求和器的权重与共同饱和边界",
            "三个输入在线性区分别乘负权重后相加；任何一路使总候选输出越轨，整个输出一起饱和。",
            [("v1", "× (−Rf/R1)"), ("v2", "× (−Rf/R2)"), ("v3", "× (−Rf/R3)"), ("Σ → vo", "总和统一检查轨限")],
        ),
        "figure-5-17.svg": chain(
            "差模与共模的分解",
            "两个输入由共同的平均值和相反的半差值组成；理想差分级只放大差模，匹配误差和有限CMRR会让共模泄漏。",
            [("vcm", "(v1+v2)/2"), ("±vd/2", "v1减、v2加"), ("四电阻差分级", "电阻比需匹配"), ("vo", "理想为 k·vd")],
        ),
        "figure-5-29.svg": chain(
            "从输入、开环到输出的非理想检查链",
            "理想闭环公式成立前必须同时检查输入范围、开环动态、稳定性、输出摆幅、电流、压摆率和负载。",
            [("输入端", "共模、差分、IB、VOS"), ("开环 A(jf)", "增益与相位"), ("闭环", "误差与稳定性"), ("输出端", "摆幅、限流、SR、CL")],
        ),
    }
    figures["figure-5-03.svg"] = svg(
        "有限电源下的开环传输",
        "运放开环传输中央只有极窄的线性区，斜率为开环增益A；两端分别饱和在VOH和VOL。",
        """
  <line class="axis" x1="100" y1="240" x2="890" y2="240" marker-end="url(#arrow)"/><line class="axis" x1="480" y1="400" x2="480" y2="55" marker-end="url(#arrow)"/>
  <path class="teal" d="M120 355L455 355L505 120L840 120"/><line class="orange" x1="480" y1="390" x2="480" y2="70" stroke-dasharray="6 6"/>
  <text class="head" x="130" y="345">VOL</text><text class="head" x="760" y="108">VOH</text><text class="txt" x="520" y="215">斜率 A</text>
  <text class="small" x="310" y="435">线性区宽度约为 (VOH−VOL)/A，通常极窄</text>
""",
        height=470,
    )
    figures["figure-5-07.svg"] = svg(
        "虚断与虚短不能望文生义",
        "虚断表示输入引脚电流近似为零而外部电阻电流仍经反馈返回；虚短表示特定负反馈线性状态下两输入电位近似相等，但两端没有导线相连。",
        """
  <rect class="panel" x="35" y="55" width="430" height="330" rx="12"/><rect class="panel" x="495" y="55" width="430" height="330" rx="12"/>
  <text class="head" x="60" y="98">虚断：i+ ≈ i− ≈ 0</text><circle class="node" cx="100" cy="210" r="6"/><polyline class="ink" points="100,210 150,210 165,195 185,225 205,195 225,225 240,210 330,210"/>
  <circle class="node" cx="330" cy="210" r="6"/><line class="orange" x1="345" y1="165" x2="345" y2="250" stroke-dasharray="6 6"/>
  <text class="small" x="75" y="285">电流经外部 R 与 Rf 返回，</text><text class="small" x="75" y="315">不是流入运放输入引脚。</text>
  <text class="head" x="520" y="98">虚短：v+ ≈ v−</text><circle class="node" cx="610" cy="210" r="7"/><circle class="node" cx="810" cy="210" r="7"/>
  <line class="teal" x1="630" y1="180" x2="790" y2="180" marker-end="url(#arrow)"/><text class="txt" x="675" y="165">近似同电位</text>
  <line class="orange" x1="650" y1="220" x2="770" y2="220" stroke-dasharray="8 8"/><text class="small" x="665" y="252">没有物理短接</text>
  <text class="small" x="535" y="315">只在负反馈、线性且未饱和时成立。</text>
""",
    )
    figures["figure-5-09.svg"] = wave_pair("反相输出波形", invert=True, step=False)
    figures["figure-5-12.svg"] = wave_pair("同相放大器的波形方向", invert=False, step=True)
    figures["figure-5-19.svg"] = svg(
        "正恒压输入产生负斜坡",
        "反相积分器在正恒压输入期间以负一除以RC乘输入电压的斜率下降，直到触及负输出极限。",
        """
  <text class="head" x="55" y="70">输入 vi</text><line class="axis" x1="80" y1="165" x2="890" y2="165" marker-end="url(#arrow)"/>
  <path class="teal" d="M80 165L220 165L220 95L700 95L700 165L860 165"/><text class="small" x="245" y="85">+V</text>
  <text class="head" x="55" y="245">输出 vo</text><line class="axis" x1="80" y1="330" x2="890" y2="330" marker-end="url(#arrow)"/>
  <path class="orange" d="M80 250L220 250L690 390L860 390"/><circle cx="220" cy="250" r="7" fill="#006f78"/>
  <text class="small" x="365" y="280">斜率 = −V/(RC)</text><text class="small" x="700" y="380">到达 VOL 后饱和</text>
""",
        height=440,
    )
    figures["figure-5-22.svg"] = triangle_square()
    figures["figure-5-25.svg"] = comparator_wave()
    figures["figure-5-27.svg"] = schmitt_wave()
    figures["figure-5-28.svg"] = hysteresis_plot()
    return figures


def wave_pair(title: str, *, invert: bool, step: bool) -> str:
    if step:
        top = "M80 170L230 170L230 95L560 95L560 170L860 170"
        bottom = "M80 350L230 350L230 250L560 250L560 350L860 350"
        desc = "同相放大器的输入和输出阶跃沿同一方向变化，输出幅值由闭环增益决定，实际边沿受带宽和压摆率限制。"
    else:
        top = waveform_path(80, 150, 760, 58)
        bottom = waveform_path(80, 335, 760, 105, phase=math.pi if invert else 0)
        desc = "输入与输出使用同一时间轴；反相放大器输出相对输入旋转一百八十度，幅值按闭环电阻比放大。"
    return svg(
        title,
        desc,
        f"""
  <text class="head" x="45" y="65">vi</text><line class="axis" x1="80" y1="150" x2="890" y2="150" marker-end="url(#arrow)"/><path class="teal" d="{top}"/>
  <text class="head" x="45" y="255">vo</text><line class="axis" x1="80" y1="335" x2="890" y2="335" marker-end="url(#arrow)"/><path class="orange" d="{bottom}"/>
  <text class="small" x="330" y="425">两幅波形共用同一时间基准与地参考</text>
""",
        height=460,
    )


def triangle_square() -> str:
    return svg(
        "三角波的斜率映射成反相方波",
        "反相微分器把三角波的正斜率映射成负恒定输出，把负斜率映射成正恒定输出；输出幅值由斜率和RfC决定。",
        """
  <text class="head" x="45" y="65">vi：三角波</text><line class="axis" x1="80" y1="160" x2="890" y2="160" marker-end="url(#arrow)"/>
  <path class="teal" d="M80 160L210 90L340 230L470 90L600 230L730 90L860 160"/>
  <text class="head" x="45" y="275">vo = −RfC·dvi/dt</text><line class="axis" x1="80" y1="350" x2="890" y2="350" marker-end="url(#arrow)"/>
  <path class="orange" d="M80 400L210 400L210 300L340 300L340 400L470 400L470 300L600 300L600 400L730 400L730 300L860 300"/>
  <text class="small" x="140" y="435">正斜率 → vo &lt; 0</text><text class="small" x="500" y="285">负斜率 → vo &gt; 0</text>
""",
        height=470,
    )


def comparator_wave() -> str:
    return svg(
        "同相比较器的阈值波形",
        "输入三角波高于固定参考电压时输出为高电平，低于参考时输出为低电平；交越附近的传播延迟和噪声会移动实际边沿。",
        """
  <text class="head" x="45" y="60">vi 与 Vref</text><line class="axis" x1="80" y1="190" x2="890" y2="190" marker-end="url(#arrow)"/>
  <path class="teal" d="M80 250L200 95L320 250L440 95L560 250L680 95L800 250L860 170"/><line class="orange" x1="80" y1="170" x2="860" y2="170" stroke-dasharray="8 7"/>
  <text class="small" x="760" y="160">Vref</text><text class="head" x="45" y="305">vo</text><line class="axis" x1="80" y1="385" x2="890" y2="385" marker-end="url(#arrow)"/>
  <path class="orange" d="M80 420L140 420L140 330L260 330L260 420L380 420L380 330L500 330L500 420L620 420L620 330L740 330L740 420L860 420"/>
""",
        height=460,
    )


def schmitt_wave() -> str:
    return svg(
        "反相施密特触发器的双阈值波形",
        "输入上穿上阈值时输出从高翻为低，输入下穿下阈值时输出从低翻为高；两阈值之间保持历史状态并抑制小噪声翻转。",
        """
  <line class="axis" x1="80" y1="230" x2="890" y2="230" marker-end="url(#arrow)"/><path class="teal" d="M80 245C170 245 190 95 290 95C390 95 420 350 540 350C650 350 690 90 820 90"/>
  <path class="orange" d="M230 115l12 18l12-30l12 22l12-20" />
  <line class="orange" x1="80" y1="155" x2="860" y2="155" stroke-dasharray="7 7"/><line class="orange" x1="80" y1="305" x2="860" y2="305" stroke-dasharray="7 7"/>
  <text class="small" x="750" y="145">VTH</text><text class="small" x="750" y="295">VTL</text>
  <line class="axis" x1="80" y1="420" x2="890" y2="420" marker-end="url(#arrow)"/><path class="orange" d="M80 365L260 365L260 445L560 445L560 365L860 365"/>
""",
        height=480,
    )


def hysteresis_plot() -> str:
    return svg(
        "反相施密特触发器的滞回传输",
        "输入上升时沿高电平支路向右并在VTH下跳，输入下降时沿低电平支路向左并在VTL上跳；两阈值间输出取决于历史。",
        """
  <line class="axis" x1="100" y1="390" x2="890" y2="390" marker-end="url(#arrow)"/><line class="axis" x1="480" y1="420" x2="480" y2="55" marker-end="url(#arrow)"/>
  <path class="teal" d="M200 115L720 115L720 350L240 350L240 115" marker-end="url(#arrow)"/>
  <line class="orange" x1="240" y1="100" x2="240" y2="390" stroke-dasharray="6 6"/><line class="orange" x1="720" y1="100" x2="720" y2="390" stroke-dasharray="6 6"/>
  <text class="head" x="120" y="120">VOH</text><text class="head" x="120" y="355">VOL</text><text class="small" x="210" y="420">VTL：上跳</text><text class="small" x="680" y="420">VTH：下跳</text>
  <text class="small" x="390" y="455">滞回宽度 VH = VTH − VTL</text>
""",
        height=480,
    )


FIGURES.update(chapter5_semantic_figures())


def chapter6_semantic_figures() -> dict[str, str]:
    def chain(title: str, desc: str, steps: list[tuple[str, str]], *, return_path: bool = False) -> str:
        body = ""
        count = len(steps)
        width = 175 if count >= 4 else 220
        gap = 45
        total = count * width + (count - 1) * gap
        start = (960 - total) / 2
        for index, (head, detail) in enumerate(steps):
            x = start + index * (width + gap)
            body += (
                f'<rect class="panel" x="{x:.0f}" y="115" width="{width}" height="150" rx="12"/>'
                f'<text class="head" x="{x + 16:.0f}" y="157">{escape(head)}</text>'
                f'<text class="small" x="{x + 16:.0f}" y="202">{escape(detail)}</text>'
            )
            if index < count - 1:
                body += f'<line class="teal" x1="{x + width:.0f}" y1="190" x2="{x + width + 35:.0f}" y2="190" marker-end="url(#arrow)"/>'
        if return_path:
            body += f'<path class="orange" d="M{start + total - 20:.0f} 280C{start + total - 50:.0f} 345 {start + 75:.0f} 345 {start + 20:.0f} 280" marker-end="url(#arrow-orange)"/>'
        return svg(title, desc, body, height=380)

    figures = {
        "figure-6-02.svg": feedback_loop(),
        "figure-6-03.svg": chain(
            "反馈极性的扰动判定",
            "负反馈沿环路返回抵消原变化，正反馈沿环路返回强化原变化；额外一百八十度相移会在某频率反转低频直觉。",
            [("xo ↑", "假设输出扰动"), ("xf ↑", "反馈网络返回"), ("xe 改变", "xs−xf 或 xs+xf"), ("输出响应", "抵消或继续强化")],
            return_path=True,
        ),
        "figure-6-05.svg": chain(
            "负反馈数值例的去敏与端口变化",
            "开环增益增加百分之二十时，闭环增益只变化约百分之一点八九；电压串联反馈同时提高输入电阻并降低输出电阻。",
            [("A: 200→240", "器件变化 +20%"), ("Af: 22.22→22.64", "闭环只变 +1.89%"), ("Rin", "10 kΩ → 90 kΩ"), ("Rout", "900 Ω → 100 Ω")],
        ),
        "figure-6-07.svg": chain(
            "反馈纠错的四个必要环节",
            "扰动必须被取样看见、形成误差、落在有效环路带宽内，且前向通道仍有输出余量，才能由反馈减小。",
            [("扰动进入", "位于取样范围内"), ("输出取样", "反馈能看见误差"), ("形成 xe", "|T(jω)| 足够大"), ("执行纠正", "未碰轨、未限流")],
        ),
        "figure-6-09.svg": feedback_topology("电压串联反馈", "电压取样 βv", "串联比较 xe=vs−vf", "闭环电压增益 vo/vs"),
        "figure-6-10.svg": feedback_topology("电压并联反馈", "输出电压经 Rf 取样", "求和节点作电流 KCL", "跨阻 vo/is"),
        "figure-6-11.svg": feedback_topology("电流串联反馈", "传感器串入输出电流", "串联比较电压", "跨导 io/vs"),
        "figure-6-12.svg": feedback_topology("电流并联反馈", "传感器串入输出支路", "源与反馈电流并联混合", "电流增益 io/is"),
        "figure-6-17.svg": chain(
            "一阶 Bode 手绘与自检流程",
            "先因式分解并标拐点，再累计渐近线斜率、补拐点精确修正和相位，最后检查低高频物理极限与频率单位。",
            [("因式分解", "常数×零点/极点"), ("标拐点", "Hz 与 rad/s 不混用"), ("累计斜率", "零点 +20；极点 −20"), ("精确自检", "±3.01 dB、相位、极限")],
        ),
        "figure-6-19.svg": chain(
            "含低频与高频电容的完整放大器接口",
            "低频由输入输出耦合和发射极或源极旁路电容主导，高频由器件输入、桥接、结电容和负载电容主导。",
            [("源与 Cin", "Rs + 输入网络"), ("有源器件", "Cπ/Cgs 与 Cμ/Cgd"), ("发射/源端", "RE/RS ∥ CE/CS"), ("输出与 Cout", "Rout、结电容、RL")],
        ),
        "figure-6-22.svg": miller_diagram(),
        "figure-6-23.svg": chain(
            "闭环分母与环路增益测试概念",
            "闭环信号沿A和β回到比较点；测环路增益需在保持直流偏置与端口加载的断点注入测试量并测返回量。",
            [("注入 xt", "保持工作点与加载"), ("A(s)", "前向通道"), ("β(s)", "反馈网络"), ("测返回 xr", "T = xr/xt")],
            return_path=True,
        ),
    }
    figures["figure-6-04.svg"] = complex_sum()
    figures["figure-6-06.svg"] = disturbance_positions()
    figures["figure-6-15.svg"] = bode_first_order(lowpass=True)
    figures["figure-6-16.svg"] = bode_first_order(lowpass=False)
    figures["figure-6-18.svg"] = rc_step_responses()
    figures["figure-6-20.svg"] = amplifier_bode_envelope()
    figures["figure-6-21.svg"] = gain_bandwidth_plot()
    figures["figure-6-24.svg"] = margin_plot()
    figures["figure-6-25.svg"] = stability_time_responses()
    return figures


def feedback_loop() -> str:
    return svg(
        "统一负反馈方框图",
        "外加量xs与反馈量xf在比较点相减得到xe，前向通道A把xe变为xo，反馈网络β从输出取样并沿下支路返回。",
        """
  <circle class="ink" cx="190" cy="180" r="35"/><text class="head" x="177" y="173">+</text><text class="head" x="178" y="205">−</text>
  <line class="teal" x1="45" y1="180" x2="150" y2="180" marker-end="url(#arrow)"/><text class="txt" x="70" y="165">xs</text>
  <line class="teal" x1="225" y1="180" x2="355" y2="180" marker-end="url(#arrow)"/><text class="txt" x="270" y="165">xe</text>
  <rect class="panel" x="355" y="125" width="190" height="110" rx="10"/><text class="head" x="415" y="190">A(s)</text>
  <line class="teal" x1="545" y1="180" x2="850" y2="180" marker-end="url(#arrow)"/><text class="txt" x="700" y="165">xo</text>
  <path class="orange" d="M760 180L760 315L500 315" marker-end="url(#arrow-orange)"/><rect class="panel" x="310" y="270" width="190" height="90" rx="10"/><text class="head" x="365" y="325">β(s)</text>
  <path class="orange" d="M310 315L190 315L190 220" marker-end="url(#arrow-orange)"/><text class="small" x="220" y="300">xf = βxo</text>
""",
        height=410,
    )


def feedback_topology(title: str, sample: str, mix: str, result: str) -> str:
    return svg(
        title,
        f"{title}方框图明确区分输出取样方式与输入混合方式，并给出对应闭环量。",
        f"""
  <circle class="ink" cx="190" cy="180" r="34"/><text class="head" x="177" y="172">+</text><text class="head" x="177" y="204">−</text>
  <line class="teal" x1="40" y1="180" x2="150" y2="180" marker-end="url(#arrow)"/><text class="small" x="55" y="160">输入源</text>
  <line class="teal" x1="225" y1="180" x2="350" y2="180" marker-end="url(#arrow)"/>
  <rect class="panel" x="350" y="120" width="210" height="120" rx="10"/><text class="head" x="405" y="175">前向级</text><text class="small" x="390" y="210">{result}</text>
  <line class="teal" x1="560" y1="180" x2="875" y2="180" marker-end="url(#arrow)"/><text class="small" x="720" y="158">输出与负载</text>
  <path class="orange" d="M760 180L760 325L540 325" marker-end="url(#arrow-orange)"/>
  <rect class="panel" x="305" y="280" width="235" height="90" rx="10"/><text class="head" x="335" y="318">{sample}</text><text class="small" x="335" y="347">{mix}</text>
  <path class="orange" d="M305 325L190 325L190 220" marker-end="url(#arrow-orange)"/>
""",
        height=420,
    )


def complex_sum() -> str:
    return svg(
        "一加环路增益的复数几何意义",
        "左图中正实环路增益与一同向相加使分母增大；右图中环路增益接近负一时，一加T接近零并逼近不稳定边界。",
        """
  <rect class="panel" x="25" y="35" width="440" height="360" rx="10"/><rect class="panel" x="495" y="35" width="440" height="360" rx="10"/>
  <line class="axis" x1="70" y1="250" x2="430" y2="250" marker-end="url(#arrow)"/><line class="axis" x1="120" y1="340" x2="120" y2="75" marker-end="url(#arrow)"/>
  <line class="teal" x1="120" y1="250" x2="350" y2="250" marker-end="url(#arrow)"/><text class="head" x="230" y="225">T = 8</text>
  <line class="orange" x1="350" y1="250" x2="390" y2="250" marker-end="url(#arrow-orange)"/><text class="small" x="305" y="285">1+T = 9</text>
  <line class="axis" x1="530" y1="250" x2="900" y2="250" marker-end="url(#arrow)"/><line class="axis" x1="710" y1="340" x2="710" y2="75" marker-end="url(#arrow)"/>
  <circle cx="770" cy="250" r="6" fill="#172127"/><text class="small" x="760" y="225">1</text><line class="teal" x1="770" y1="250" x2="716" y2="250" marker-end="url(#arrow)"/>
  <text class="head" x="620" y="200">T ≈ −0.9</text><text class="small" x="680" y="290">1+T ≈ 0.1</text>
""",
    )


def disturbance_positions() -> str:
    return svg(
        "三种扰动注入位置",
        "环内输出扰动可被反馈看见并压低，输入端噪声会被当作输入一起传递，取样点之后的环外扰动不能由该环路纠正。",
        """
  <rect class="panel" x="20" y="45" width="290" height="335" rx="10"/><rect class="panel" x="335" y="45" width="290" height="335" rx="10"/><rect class="panel" x="650" y="45" width="290" height="335" rx="10"/>
  <text class="head" x="45" y="85">(a) 环内输出扰动</text><text class="head" x="360" y="85">(b) 输入端噪声</text><text class="head" x="675" y="85">(c) 环外扰动</text>
  <path class="teal" d="M45 180L105 180L145 180L205 180L275 180" marker-end="url(#arrow)"/><rect class="panel" x="105" y="145" width="100" height="70" rx="8"/><text class="txt" x="137" y="188">A</text><line class="orange" x1="205" y1="105" x2="205" y2="145" marker-end="url(#arrow-orange)"/><text class="small" x="215" y="120">no</text>
  <path class="teal" d="M360 180L420 180L460 180L550 180L600 180" marker-end="url(#arrow)"/><rect class="panel" x="460" y="145" width="90" height="70" rx="8"/><text class="txt" x="492" y="188">A</text><line class="orange" x1="420" y1="105" x2="420" y2="170" marker-end="url(#arrow-orange)"/><text class="small" x="430" y="120">ns</text>
  <path class="teal" d="M675 180L735 180L795 180L900 180" marker-end="url(#arrow)"/><rect class="panel" x="735" y="145" width="80" height="70" rx="8"/><text class="txt" x="763" y="188">A</text><circle class="node" cx="815" cy="180" r="6"/><line class="orange" x1="865" y1="105" x2="865" y2="170" marker-end="url(#arrow-orange)"/><text class="small" x="875" y="120">n外</text>
  <text class="small" x="45" y="320">反馈能看见并抑制</text><text class="small" x="360" y="320">与有用输入同点相加</text><text class="small" x="675" y="320">取样点在扰动之前</text>
""",
    )


def bode_first_order(*, lowpass: bool) -> str:
    if lowpass:
        exact = "M110 105C340 105 445 110 515 165C610 245 700 330 860 395"
        asym = "M110 105L500 105L860 395"
        phase = "0° → −45° → −90°"
        title = "低通精确幅频与相位标记"
    else:
        exact = "M110 395C260 330 355 245 445 165C515 110 620 105 860 105"
        asym = "M110 395L470 105L860 105"
        phase = "+90° → +45° → 0°"
        title = "高通精确幅频与相位标记"
    return svg(
        title,
        f"{title}使用对数频率轴，精确曲线在截止频率处为负三点零一分贝，相位跨三个典型频点平滑变化。",
        f"""
  <line class="axis" x1="90" y1="410" x2="900" y2="410" marker-end="url(#arrow)"/><line class="axis" x1="90" y1="410" x2="90" y2="55" marker-end="url(#arrow)"/>
  <path class="teal" d="{exact}"/><path class="orange" d="{asym}" stroke-dasharray="8 7"/>
  <line class="panel" x1="490" y1="55" x2="490" y2="410" stroke-dasharray="6 6"/><circle cx="490" cy="150" r="8" fill="#006f78"/>
  <text class="head" x="505" y="145">fc：−3.01 dB</text><text class="small" x="170" y="445">0.1fc</text><text class="small" x="475" y="445">fc</text><text class="small" x="790" y="445">10fc</text>
  <text class="small" x="570" y="70">相位 {phase}</text>
""",
        height=480,
    )


def rc_step_responses() -> str:
    return svg(
        "RC 阶跃与截止频率的同一极点",
        "低通电容电压从零指数上升至V，高通电阻电压从V指数衰减至零；两者具有相同时间常数τ和频域拐点一除以τ。",
        """
  <rect class="panel" x="20" y="45" width="290" height="340" rx="10"/><rect class="panel" x="335" y="45" width="290" height="340" rx="10"/><rect class="panel" x="650" y="45" width="290" height="340" rx="10"/>
  <text class="head" x="45" y="85">输入阶跃</text><text class="head" x="360" y="85">低通：电容充电</text><text class="head" x="675" y="85">高通：电阻瞬态</text>
  <path class="teal" d="M50 285L120 285L120 125L285 125"/><path class="teal" d="M360 285C390 285 410 165 600 130"/><line class="orange" x1="360" y1="125" x2="600" y2="125" stroke-dasharray="6 6"/>
  <path class="teal" d="M675 125C720 130 760 275 915 285"/><line class="axis" x1="50" y1="285" x2="290" y2="285" marker-end="url(#arrow)"/><line class="axis" x1="360" y1="285" x2="605" y2="285" marker-end="url(#arrow)"/><line class="axis" x1="675" y1="285" x2="920" y2="285" marker-end="url(#arrow)"/>
  <text class="small" x="360" y="330">t=τ：达到 63.2%</text><text class="small" x="675" y="330">t=τ：剩余 36.8%</text><text class="math" x="355" y="370">sp = −1/τ，ωc = 1/τ</text>
""",
    )


def amplifier_bode_envelope() -> str:
    return svg(
        "多低频、多高频转折的放大器 Bode 包络",
        "总幅频曲线在多个低频转折后进入中频平台，再在多个高频极点后以更陡斜率下降；总负三分贝点不一定等于任一单独拐点。",
        """
  <line class="axis" x1="90" y1="410" x2="900" y2="410" marker-end="url(#arrow)"/><line class="axis" x1="90" y1="410" x2="90" y2="55" marker-end="url(#arrow)"/>
  <path class="teal" d="M105 365L220 235L330 120L650 120L760 210L860 385"/>
  <line class="orange" x1="220" y1="70" x2="220" y2="410" stroke-dasharray="6 6"/><line class="orange" x1="330" y1="70" x2="330" y2="410" stroke-dasharray="6 6"/><line class="orange" x1="650" y1="70" x2="650" y2="410" stroke-dasharray="6 6"/><line class="orange" x1="760" y1="70" x2="760" y2="410" stroke-dasharray="6 6"/>
  <text class="small" x="195" y="440">fL1</text><text class="small" x="305" y="440">fL2</text><text class="small" x="625" y="440">fH1</text><text class="small" x="735" y="440">fH2</text>
  <text class="head" x="430" y="105">中频增益 AM</text><text class="small" x="110" y="330">+40 → +20 dB/dec</text><text class="small" x="690" y="330">−20 → −40 dB/dec</text>
""",
        height=470,
    )


def gain_bandwidth_plot() -> str:
    return svg(
        "单主极点负反馈的增益—带宽交换",
        "负反馈把低频增益除以一加T0，同时把闭环极点提高相同倍数；仅在单主极点和常数反馈系数模型中增益带宽乘积近似不变。",
        """
  <line class="axis" x1="90" y1="410" x2="900" y2="410" marker-end="url(#arrow)"/><line class="axis" x1="90" y1="410" x2="90" y2="55" marker-end="url(#arrow)"/>
  <path class="teal" d="M110 90L330 90L850 390"/><path class="orange" d="M110 235L625 235L850 390"/>
  <line class="panel" x1="330" y1="90" x2="330" y2="410" stroke-dasharray="6 6"/><line class="panel" x1="625" y1="235" x2="625" y2="410" stroke-dasharray="6 6"/>
  <text class="head" x="125" y="78">开环 A0</text><text class="head" x="125" y="222">闭环 Af0</text><text class="small" x="305" y="440">fp</text><text class="small" x="600" y="440">fHf</text>
  <line class="teal" x1="350" y1="370" x2="605" y2="370" marker-end="url(#arrow)"/><text class="small" x="405" y="355">×(1+T0)</text>
""",
        height=470,
    )


def miller_diagram() -> str:
    return svg(
        "桥接阻抗的 Miller 两端等效",
        "原桥接阻抗连接输入和输出；在给定电压增益Av下可等效为输入对地阻抗和输出对地阻抗，但建立Av的受控放大通道仍必须保留。",
        """
  <rect class="panel" x="25" y="45" width="440" height="330" rx="10"/><rect class="panel" x="495" y="45" width="440" height="330" rx="10"/>
  <text class="head" x="50" y="85">原桥接网络</text><circle class="node" cx="100" cy="210" r="6"/><circle class="node" cx="390" cy="210" r="6"/><rect class="panel" x="200" y="165" width="100" height="90" rx="8"/><text class="head" x="235" y="217">Z</text><line class="ink" x1="100" y1="210" x2="200" y2="210"/><line class="ink" x1="300" y1="210" x2="390" y2="210"/><text class="small" x="70" y="195">vi</text><text class="small" x="395" y="195">vo=Av·vi</text>
  <text class="head" x="520" y="85">Miller 两端等效</text>
  <circle class="node" cx="550" cy="140" r="6"/><text class="small" x="520" y="125">vi</text>
  <line class="teal" x1="550" y1="140" x2="650" y2="140" marker-end="url(#arrow)"/>
  <rect class="panel" x="650" y="105" width="120" height="70" rx="8"/>
  <text class="head" x="690" y="148">Av</text>
  <line class="teal" x1="770" y1="140" x2="880" y2="140" marker-end="url(#arrow)"/>
  <circle class="node" cx="880" cy="140" r="6"/><text class="small" x="850" y="125">vo</text>
  <text class="small" x="660" y="198">vo = Av·vi</text>

  <line class="ink" x1="550" y1="140" x2="550" y2="215"/>
  <rect class="panel" x="505" y="215" width="90" height="58" rx="8"/>
  <text class="small" x="515" y="250">Zin,M</text>
  <line class="ink" x1="550" y1="273" x2="550" y2="315"/>

  <line class="ink" x1="880" y1="140" x2="880" y2="215"/>
  <rect class="panel" x="835" y="215" width="90" height="58" rx="8"/>
  <text class="small" x="841" y="250">Zout,M</text>
  <line class="ink" x1="880" y1="273" x2="880" y2="315"/>

  <line class="ink" x1="550" y1="315" x2="880" y2="315"/>
  <line class="ink" x1="715" y1="315" x2="715" y2="332"/>
  <line class="ink" x1="685" y1="332" x2="745" y2="332"/>
  <line class="ink" x1="694" y1="341" x2="736" y2="341"/>
  <line class="ink" x1="704" y1="350" x2="726" y2="350"/>
""",
    )


def margin_plot() -> str:
    return svg(
        "同一环路的相位裕度与增益裕度读图",
        "幅值图在二十千赫兹穿越零分贝，对应相位负一百三十五度并给出四十五度相位裕度；相位在八十千赫兹到负一百八十度时幅值为负十三点九八分贝。",
        """
  <text class="head" x="45" y="55">环路幅值 / dB</text><line class="axis" x1="90" y1="185" x2="900" y2="185" marker-end="url(#arrow)"/><path class="teal" d="M100 95C330 105 500 180 850 300"/>
  <circle cx="420" cy="185" r="7" fill="#006f78"/><circle cx="760" cy="285" r="7" fill="#ad4f16"/><text class="small" x="390" y="170">gc: 20 kHz</text><text class="small" x="730" y="315">pc: −13.98 dB</text>
  <text class="head" x="45" y="350">环路相位 / °</text><line class="axis" x1="90" y1="455" x2="900" y2="455" marker-end="url(#arrow)"/><path class="orange" d="M100 350C350 350 520 400 850 450"/>
  <line class="panel" x1="90" y1="430" x2="900" y2="430" stroke-dasharray="6 6"/><circle cx="420" cy="375" r="7" fill="#006f78"/><circle cx="760" cy="430" r="7" fill="#ad4f16"/>
  <text class="small" x="430" y="370">−135°，PM=45°</text><text class="small" x="765" y="420">−180°，GM=13.98 dB</text>
""",
        height=500,
    )


def stability_time_responses() -> str:
    return svg(
        "稳定、超调、振铃和振荡的时域联系",
        "四幅阶跃响应依次表示阻尼良好、欠阻尼但收敛、稳定边界附近的等幅振铃和振幅增长的不稳定响应。",
        """
  <rect class="panel" x="25" y="35" width="440" height="190" rx="10"/><rect class="panel" x="495" y="35" width="440" height="190" rx="10"/><rect class="panel" x="25" y="245" width="440" height="190" rx="10"/><rect class="panel" x="495" y="245" width="440" height="190" rx="10"/>
  <text class="head" x="50" y="75">(a) 阻尼良好</text><path class="teal" d="M50 190C90 190 100 100 175 100L430 100"/>
  <text class="head" x="520" y="75">(b) 欠阻尼但稳定</text><path class="teal" d="M520 190C570 190 575 65 630 90C680 115 700 90 740 100C790 108 820 100 910 100"/>
  <text class="head" x="50" y="285">(c) 稳定边界附近</text><path class="orange" d="M50 365C90 300 130 430 170 365C210 300 250 430 290 365C330 300 370 430 430 365"/>
  <text class="head" x="520" y="285">(d) 不稳定</text><path class="orange" d="M520 365C550 340 580 390 615 350C650 305 690 430 735 320C780 245 830 455 910 275"/>
""",
        height=470,
    )


FIGURES.update(chapter6_semantic_figures())


def chapter7_semantic_figures() -> dict[str, str]:
    def chain(title: str, desc: str, steps: list[tuple[str, str]]) -> str:
        body = ""
        for index, (head, detail) in enumerate(steps):
            x = 45 + index * 225
            detail_lines = [part.strip() for part in detail.split("；")]
            if len(detail_lines) == 1:
                detail_markup = (
                    f'<text class="small" x="{x + 16}" y="202">'
                    f"{escape(detail_lines[0])}</text>"
                )
            else:
                tspans = "".join(
                    f'<tspan x="{x + 16}" y="{190 + line_index * 24}">'
                    f"{escape(line)}</tspan>"
                    for line_index, line in enumerate(detail_lines)
                )
                detail_markup = f'<text class="small">{tspans}</text>'
            body += (
                f'<rect class="panel" x="{x}" y="115" width="185" height="150" rx="12"/>'
                f'<text class="head" x="{x + 16}" y="157">{escape(head)}</text>'
                f"{detail_markup}"
            )
            if index < len(steps) - 1:
                body += f'<line class="teal" x1="{x + 185}" y1="190" x2="{x + 215}" y2="190" marker-end="url(#arrow)"/>'
        return svg(title, desc, body, height=380)

    figures = {
        "figure-7-02.svg": chain(
            "输入坐标的分解与重构",
            "两个对地输入可唯一变换为差模与共模坐标，并由平均值加减半差值重构。",
            [("v1、v2", "共同地参考"), ("vid = v1−v2", "差模坐标"), ("vcm=(v1+v2)/2", "共模坐标"), ("重构", "v1=vcm+vid/2；v2=vcm−vid/2")],
        ),
        "figure-7-03.svg": chain(
            "CMRR 的两次小信号测量",
            "差模测量保持平均值固定并让两输入反向等量变化；共模测量令两输入同相等幅，供电、频率、负载和偏置必须相同。",
            [("差模激励", "vcm±vt/2"), ("测 Ad", "vo/vid"), ("共模激励", "v1=v2=vt"), ("测 Ac 与 CMRR", "Ad/Ac")],
        ),
        "figure-7-06.svg": chain(
            "差模小信号的完整符号链",
            "纯差模时两输入分别为正负半个差模电压，理想尾源令增量尾电流为零，因此两支集电极电流增量等大反向。",
            [("+vid/2", "驱动 Q1"), ("Δic1 > 0", "gm(v1−ve)"), ("Δit = 0", "理想尾阻无穷"), ("Δic2 < 0", "与左支等大反向")],
        ),
        "figure-7-07.svg": chain(
            "差分对的输出极性与增益倍数",
            "正差模输入使左支电流增加、左输出降低，同时右支电流减少、右输出升高；差分读出幅值为单端读出的两倍。",
            [("vid > 0", "v1 高于 v2"), ("ic1↑、vo1↓", "左 RC 压降增加"), ("ic2↓、vo2↑", "右 RC 压降减少"), ("vod=vo1−vo2", "为负，幅值 gmRC")],
        ),
        "figure-7-08.svg": chain(
            "理想与有限尾电流源的共模路径",
            "共模上升时理想尾源让发射节点近似同升并保持总电流；有限尾阻会调制总电流，对称单端输出共同移动，失配才泄漏到差分输出。",
            [("v1、v2 同升", "纯共模"), ("尾源有限 ro", "Δit ≠ 0"), ("完全对称", "vo1、vo2 同向移动"), ("存在失配", "差分输出也出现 Ac")],
        ),
        "figure-7-19.svg": chain(
            "功率级的能量与热路径",
            "电源输入功率分为负载平均功率和输出管损耗，器件热量再沿结、壳、界面、散热器到环境；平均热估算不能替代SOA检查。",
            [("电源输入", "示例 9.55 W"), ("负载功率", "示例 6.25 W"), ("输出管热", "示例 3.30 W"), ("散热与安全", "TJ、SOA、峰值I/V")],
        ),
        "figure-7-26.svg": chain(
            "串联型线性稳压器的核心闭环",
            "误差放大器比较反馈采样与基准，驱动串联调整管改变压降，使输出回到设定值；调整管同时承担负载电流与功耗。",
            [("Vref 与 vfb", "形成误差信号"), ("误差放大器", "提供环路增益"), ("串联调整管", "控制 Vraw−vo"), ("RL 与 β", "交付电流并反馈取样")],
        ),
        "figure-7-27.svg": chain(
            "线调整率、负载调整率与滤波稳压分工",
            "线调整测试固定负载只改变输入，负载调整测试固定输入只改变负载；滤波电容负责储能，稳压器靠参考与反馈校正。",
            [("线调整", "固定 IL，改变 Vin"), ("ΔVo/ΔVin", "报告输入范围"), ("负载调整", "固定 Vin，改变 IL"), ("ΔVo/ΔIL", "报告负载与温度条件")],
        ),
    }
    figures["figure-7-05.svg"] = current_steering()
    figures["figure-7-11.svg"] = compliance_plot()
    figures["figure-7-13.svg"] = conduction_angles()
    figures["figure-7-16.svg"] = crossover_wave()
    figures["figure-7-18.svg"] = class_b_efficiency_wave()
    figures["figure-7-23.svg"] = rectifier_waveforms()
    figures["figure-7-24.svg"] = ripple_discharge()
    return figures


def current_steering() -> str:
    return svg(
        "差分对的大信号电流转向",
        "差模输入从负到正时，固定尾电流从Q2支路逐渐转向Q1支路；两支电流之和近似为IT，中点各为一半。",
        """
  <text class="head" x="90" y="70">vid 很负</text><text class="head" x="390" y="70">vid = 0</text><text class="head" x="705" y="70">vid 很正</text>
  <rect class="panel" x="80" y="100" width="190" height="280" rx="10"/><rect class="panel" x="385" y="100" width="190" height="280" rx="10"/><rect class="panel" x="690" y="100" width="190" height="280" rx="10"/>
  <rect x="115" y="320" width="45" height="10" fill="#006f78"/><rect x="185" y="140" width="45" height="190" fill="#ad4f16"/><text class="small" x="100" y="355">ic1≈0</text><text class="small" x="175" y="355">ic2≈IT</text>
  <rect x="420" y="235" width="45" height="95" fill="#006f78"/><rect x="490" y="235" width="45" height="95" fill="#ad4f16"/><text class="small" x="405" y="355">IT/2</text><text class="small" x="485" y="355">IT/2</text>
  <rect x="725" y="140" width="45" height="190" fill="#006f78"/><rect x="795" y="320" width="45" height="10" fill="#ad4f16"/><text class="small" x="710" y="355">ic1≈IT</text><text class="small" x="790" y="355">ic2≈0</text>
  <text class="math" x="300" y="425">ic1 + ic2 ≈ IT</text>
""",
        height=455,
    )


def compliance_plot() -> str:
    return svg(
        "电流源的顺从区和有限斜率",
        "实际电流源在最低顺从电压之前不能维持设定电流，进入工作区后仍因有限输出电阻略有斜率，过高电压又受耐压和功耗限制。",
        """
  <line class="axis" x1="100" y1="390" x2="890" y2="390" marker-end="url(#arrow)"/><line class="axis" x1="100" y1="390" x2="100" y2="55" marker-end="url(#arrow)"/>
  <line class="orange" x1="100" y1="130" x2="850" y2="130" stroke-dasharray="8 7"/><text class="small" x="720" y="115">理想 Iset</text>
  <path class="teal" d="M100 390C160 385 210 250 280 165L760 125"/><line class="panel" x1="280" y1="80" x2="280" y2="390" stroke-dasharray="6 6"/><line class="panel" x1="760" y1="80" x2="760" y2="390" stroke-dasharray="6 6"/>
  <text class="small" x="225" y="425">Vcompliance,min</text><text class="small" x="700" y="425">耐压/功耗上限</text><text class="small" x="430" y="160">斜率约 1/ro</text>
""",
        height=460,
    )


def conduction_angles() -> str:
    return svg(
        "A、B、AB 类的导通角波形",
        "同一零到三百六十度周期中，A类器件全周期导通，B类上下管各导通一百八十度，AB类每只超过一百八十度并在过零附近重叠。",
        """
  <path class="teal" d="M100 150C190 60 280 60 370 150C460 240 550 240 640 150C730 60 820 60 880 135"/>
  <line class="axis" x1="80" y1="150" x2="900" y2="150" marker-end="url(#arrow)"/>
  <text class="head" x="45" y="285">A 类</text><rect x="150" y="255" width="700" height="35" rx="8" fill="#006f78" opacity=".7"/>
  <text class="head" x="45" y="345">B 上管</text><rect x="150" y="315" width="350" height="35" rx="8" fill="#ad4f16" opacity=".75"/>
  <text class="head" x="45" y="405">B 下管</text><rect x="500" y="375" width="350" height="35" rx="8" fill="#ad4f16" opacity=".75"/>
  <text class="small" x="150" y="445">AB：上下导通窗口在 0° 与 180° 附近重叠，每只 &gt;180° 且通常 &lt;360°</text>
""",
        height=480,
    )


def crossover_wave() -> str:
    return svg(
        "B 类交越失真的时域机制",
        "理想输出是平滑正弦；实际B类互补跟随器在每次过零附近两管均截止，输出出现平段和尖锐误差。",
        f"""
  <text class="head" x="45" y="65">理想 vo</text><line class="axis" x1="80" y1="155" x2="890" y2="155" marker-end="url(#arrow)"/><path class="teal" d="{waveform_path(80,155,760,75)}"/>
  <text class="head" x="45" y="285">B 类实际 vo</text><line class="axis" x1="80" y1="365" x2="890" y2="365" marker-end="url(#arrow)"/>
  <path class="orange" d="M80 365C135 365 155 295 215 295C270 295 285 345 330 355L380 365L430 375C475 385 490 435 545 435C605 435 625 365 680 365C735 365 755 295 815 295L860 315"/>
  <rect x="350" y="335" width="110" height="60" fill="none" stroke="#ad4f16" stroke-width="2" stroke-dasharray="6 6"/><text class="small" x="335" y="425">两管近似截止的零点缺口</text>
""",
        height=460,
    )


def class_b_efficiency_wave() -> str:
    return svg(
        "理想 B 类效率推导的波形与积分区间",
        "负载电压是完整正弦，正轨与负轨电流各为半波；每条电源轨的整周期平均电流为Ip除以π，最大理想效率只在输出峰值等于电源电压时达到π除以四。",
        f"""
  <line class="orange" x1="80" y1="90" x2="880" y2="90"/><line class="orange" x1="80" y1="390" x2="880" y2="390"/><text class="small" x="95" y="80">+VCC</text><text class="small" x="95" y="415">−VCC</text>
  <line class="axis" x1="80" y1="240" x2="900" y2="240" marker-end="url(#arrow)"/><path class="teal" d="{waveform_path(80,240,780,135,cycles=1)}"/>
  <path class="orange" d="M80 240C180 105 280 105 380 240L480 240"/><path class="orange" d="M480 240C580 375 680 375 780 240L860 240"/>
  <text class="small" x="180" y="120">正轨电流区间 0&lt;θ&lt;π</text><text class="small" x="560" y="365">负轨电流区间 π&lt;θ&lt;2π</text>
""",
        height=450,
    )


def rectifier_waveforms() -> str:
    return svg(
        "桥式整流、滤波电压与二极管脉冲电流",
        "四幅同轴波形依次为交流次级电压、全波整流电压、电容负载上的充放电纹波和峰值附近的窄二极管充电脉冲。",
        f"""
  <text class="small" x="30" y="70">vab</text><line class="axis" x1="80" y1="75" x2="900" y2="75" marker-end="url(#arrow)"/><path class="teal" d="{waveform_path(80,75,780,45,cycles=2)}"/>
  <text class="small" x="25" y="180">|vab|</text><line class="axis" x1="80" y1="185" x2="900" y2="185" marker-end="url(#arrow)"/><path class="teal" d="M80 185C125 115 170 115 215 185C260 115 305 115 350 185C395 115 440 115 485 185C530 115 575 115 620 185C665 115 710 115 755 185C800 115 845 115 880 170"/>
  <text class="small" x="20" y="300">vraw</text><line class="axis" x1="80" y1="305" x2="900" y2="305" marker-end="url(#arrow)"/><path class="orange" d="M80 255L190 285L215 250L325 282L350 250L460 282L485 250L595 282L620 250L730 282L755 250L860 280"/>
  <text class="small" x="35" y="420">iD</text><line class="axis" x1="80" y1="425" x2="900" y2="425" marker-end="url(#arrow)"/><path class="orange" d="M80 425L190 425L200 360L215 425L325 425L335 360L350 425L460 425L470 360L485 425L595 425L605 360L620 425L730 425L740 360L755 425L860 425"/>
""",
        height=470,
    )


def ripple_discharge() -> str:
    return svg(
        "小纹波常流负载下的电容放电近似",
        "电容在峰值附近快速充到Vmax，随后以近似负IL除以C的斜率向负载放电到Vmin；峰峰纹波约为IL除以C再乘一除以纹波频率。",
        """
  <line class="axis" x1="90" y1="390" x2="900" y2="390" marker-end="url(#arrow)"/><line class="axis" x1="90" y1="390" x2="90" y2="55" marker-end="url(#arrow)"/>
  <path class="teal" d="M120 100L390 275L420 100L690 275L720 100L860 190"/><circle cx="120" cy="100" r="7" fill="#006f78"/><circle cx="390" cy="275" r="7" fill="#ad4f16"/>
  <line class="orange" x1="120" y1="100" x2="860" y2="100" stroke-dasharray="6 6"/><line class="orange" x1="120" y1="275" x2="860" y2="275" stroke-dasharray="6 6"/>
  <text class="head" x="135" y="90">Vmax</text><text class="head" x="405" y="270">Vmin</text><text class="small" x="205" y="180">dv/dt ≈ −IL/C</text><text class="math" x="290" y="430">ΔVpp ≈ IL /(C·fripple)</text>
""",
        height=460,
    )


FIGURES.update(chapter7_semantic_figures())


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for filename, content in FIGURES.items():
        (OUTPUT / filename).write_text(content, encoding="utf-8")
    print(f"generated {len(FIGURES)} teaching figures")


if __name__ == "__main__":
    main()
