"""Generate circuit schematics with standard electrical symbols."""

from __future__ import annotations

import re
from pathlib import Path

import schemdraw
import schemdraw.elements as elm


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "assets" / "figures"
INK = "#172127"


def accessible_svg(drawing: schemdraw.Drawing, title: str, desc: str) -> str:
    svg = drawing.get_imagedata("svg").decode("utf-8")
    svg = svg.replace(INK, "currentColor")
    viewbox = re.search(r'viewBox="([^"]+)"', svg)
    if viewbox is None:
        raise ValueError("Schemdraw SVG is missing a viewBox")
    x, y, width, height = map(float, viewbox.group(1).split())
    # Matplotlib/Schemdraw's bounding box does not include the full visual
    # width of every text label.  A small deterministic margin prevents
    # headings and edge annotations from being clipped by the SVG viewBox.
    padding = 12.0
    x -= padding
    y -= padding
    width += 2 * padding
    height += 2 * padding
    padded_viewbox = f"{x:g} {y:g} {width:g} {height:g}"
    svg = svg.replace(viewbox.group(0), f'viewBox="{padded_viewbox}"', 1)
    svg = svg.replace("<svg ", '<svg role="img" ')
    svg = svg.replace(
        ">",
        f"><title>{title}</title><desc>{desc}</desc>"
        "<style>:root{color:#172127}.bg{fill:#fffaf0}"
        "@media(prefers-color-scheme:dark){:root{color:#e8eee8}.bg{fill:#121a1d}}</style>"
        f'<rect class="bg" x="{x}" y="{y}" width="{width}" height="{height}"/>',
        1,
    )
    return svg


def add_box(
    drawing: schemdraw.Drawing,
    corner1: tuple[float, float],
    corner2: tuple[float, float],
) -> None:
    """Draw an absolute rectangular frame without inherited rotation."""
    x1, y1 = corner1
    x2, y2 = corner2
    for start, end in (
        ((x1, y1), (x2, y1)),
        ((x2, y1), (x2, y2)),
        ((x2, y2), (x1, y2)),
        ((x1, y2), (x1, y1)),
    ):
        drawing.add(elm.Line().endpoints(start, end))


def simple_ce_bias() -> str:
    d = schemdraw.Drawing(show=False)
    d.config(unit=2.2, fontsize=14, color=INK, lw=2)

    q1 = d.add(elm.BjtNpn().at((4.2, 1.7)).label("Q1", loc="right"))
    d.add(elm.Line().at((1.2, 4.8)).to((5.2, 4.8)))
    d.add(elm.Dot().at((1.2, 4.8)))
    d.add(elm.Label().at((1.2, 5.15)).label("+10.0 V = VCC"))

    d.add(
        elm.Resistor()
        .at((1.8, 4.8))
        .to((1.8, q1.base.y))
        .label("RB = 390 kΩ", loc="left")
    )
    d.add(elm.Line().at((1.8, q1.base.y)).to(q1.base))
    d.add(elm.Dot().at(q1.base))
    d.add(elm.Label().at((q1.base.x - 0.15, q1.base.y + 0.35)).label("B"))

    d.add(
        elm.Resistor()
        .at((q1.collector.x, 4.8))
        .to(q1.collector)
        .label("RC = 2.00 kΩ", loc="right")
    )
    d.add(elm.Dot().at(q1.collector))
    d.add(elm.Label().at((q1.collector.x - 0.18, q1.collector.y + 0.35)).label("C"))

    d.add(elm.Line().at(q1.collector).right(1.7))
    d.add(elm.Dot())
    d.add(elm.Label().label("vo = VC", loc="right"))

    d.add(elm.Line().at(q1.emitter).down(1.0))
    d.add(elm.Ground())
    d.add(elm.Label().at((q1.emitter.x + 0.18, q1.emitter.y - 0.15)).label("E"))

    d.add(elm.Arrow().at((1.45, 3.8)).down(0.7).label("IB", loc="left"))
    d.add(elm.Arrow().at((q1.collector.x + 0.35, 4.0)).down(0.7).label("IC", loc="right"))
    d.add(elm.Arrow().at((q1.emitter.x + 0.9, 0.9)).down(0.55).label("IE", loc="right"))

    return accessible_svg(
        d,
        "简单共射极放大器的完整直流偏置电路",
        "十伏电源分别通过三百九十千欧基极电阻和二千欧集电电阻连接到NPN晶体管；发射极接地，集电极节点作为对地输出。图中标出了基极、集电极和发射极电流的参考方向。",
    )


def divider_biased_ce() -> str:
    d = schemdraw.Drawing(show=False)
    d.config(unit=2.0, fontsize=11, color=INK, lw=2)

    q1 = d.add(elm.BjtNpn().at((6.0, 2.6)).label("Q1", loc="right"))
    top_y = 5.6
    ground_y = 0.0

    d.add(elm.Line().at((2.8, top_y)).to((q1.collector.x, top_y)))
    d.add(elm.Dot().at((2.8, top_y)))
    d.add(elm.Label().at((2.8, top_y + 0.35)).label("+12 V = VCC"))

    d.add(
        elm.Resistor()
        .at((q1.collector.x, top_y))
        .to(q1.collector)
        .label("RC  2.20 kΩ", loc="right")
    )
    d.add(elm.Dot().at(q1.collector))
    d.add(elm.Label().at((q1.collector.x - 0.15, q1.collector.y + 0.28)).label("C"))

    divider_x = 3.65
    d.add(
        elm.Resistor()
        .at((divider_x, top_y))
        .to((divider_x, q1.base.y))
        .label("R1  82 kΩ", loc="left")
    )
    d.add(elm.Line().at((divider_x, q1.base.y)).to(q1.base))
    d.add(elm.Dot().at(q1.base))
    d.add(elm.Label().at((q1.base.x - 0.12, q1.base.y + 0.3)).label("B"))
    d.add(
        elm.Resistor()
        .at((divider_x, q1.base.y))
        .to((divider_x, ground_y))
        .label("R2  18 kΩ", loc="left")
    )
    d.add(elm.Ground().at((divider_x, ground_y)))

    d.add(
        elm.Resistor()
        .at(q1.emitter)
        .to((q1.emitter.x, ground_y))
        .label("RE  1.00 kΩ", loc="left")
    )
    d.add(elm.Ground().at((q1.emitter.x, ground_y)))
    bypass_x = q1.emitter.x + 1.45
    d.add(elm.Line().at(q1.emitter).to((bypass_x, q1.emitter.y)))
    d.add(
        elm.Capacitor()
        .at((bypass_x, q1.emitter.y))
        .to((bypass_x, ground_y))
        .label("CE", loc="right")
    )
    d.add(elm.Ground().at((bypass_x, ground_y)))
    d.add(elm.Label().at((q1.emitter.x - 0.15, q1.emitter.y - 0.35)).label("E"))

    source = d.add(elm.SourceSin().at((0.4, ground_y)).up(2.6).label("vs", loc="left"))
    d.add(elm.Ground().at(source.start))
    d.add(elm.Resistor().at(source.end).right(1.25).label("Rs  600 Ω"))
    d.add(elm.Capacitor().right(1.1).label("Cin"))
    d.add(elm.Line().to(q1.base))

    d.add(elm.Capacitor().at(q1.collector).right(2.0))
    output = d.add(elm.Dot())
    d.add(elm.Label().at((q1.collector.x + 0.95, q1.collector.y + 0.48)).label("Cout"))
    d.add(elm.Label().at((output.center.x + 0.3, output.center.y + 0.42)).label("vo"))
    load_x = output.center.x
    d.add(
        elm.Resistor()
        .at((load_x, output.center.y))
        .to((load_x, ground_y))
        .label("RL", loc="right")
    )
    d.add(elm.Ground().at((load_x, ground_y)))

    return accessible_svg(
        d,
        "分压偏置、耦合电容和发射极旁路齐全的共射极放大器",
        "十二伏单电源共射极放大器。基极由八十二千欧和十八千欧分压偏置，输入经六百欧源电阻和输入耦合电容接入；集电极经二点二千欧电阻上拉，输出通过耦合电容驱动十千欧负载；发射极的一千欧电阻与旁路电容并联接地。",
    )


def emitter_follower() -> str:
    d = schemdraw.Drawing(show=False)
    d.config(unit=2.0, fontsize=11, color=INK, lw=2)
    q1 = d.add(elm.BjtNpn().at((5.8, 2.8)).label("Q1", loc="right"))
    top_y, ground_y = 5.5, 0.0

    d.add(elm.Line().at((3.4, top_y)).to((q1.collector.x, top_y)))
    d.add(elm.Dot().at((3.4, top_y)))
    d.add(elm.Label().at((3.4, top_y + 0.35)).label("+VCC"))
    d.add(elm.Line().at((q1.collector.x, top_y)).to(q1.collector))

    divider_x = 3.6
    d.add(elm.Resistor().at((divider_x, top_y)).to((divider_x, q1.base.y)).label("R1", loc="left"))
    d.add(elm.Line().at((divider_x, q1.base.y)).to(q1.base))
    d.add(elm.Dot().at(q1.base))
    d.add(elm.Label().at((q1.base.x - 0.15, q1.base.y + 0.3)).label("B"))
    d.add(elm.Resistor().at((divider_x, q1.base.y)).to((divider_x, ground_y)).label("R2", loc="left"))
    d.add(elm.Ground().at((divider_x, ground_y)))

    source = d.add(elm.SourceSin().at((0.4, ground_y)).up(q1.base.y).label("vs", loc="left"))
    d.add(elm.Ground().at(source.start))
    d.add(elm.Resistor().at(source.end).right(1.15).label("Rs"))
    d.add(elm.Capacitor().right(1.05).label("Cin"))
    d.add(elm.Line().to(q1.base))

    d.add(elm.Resistor().at(q1.emitter).to((q1.emitter.x, ground_y)).label("RE", loc="left"))
    d.add(elm.Ground().at((q1.emitter.x, ground_y)))
    d.add(elm.Dot().at(q1.emitter))
    d.add(elm.Label().at((q1.emitter.x - 0.15, q1.emitter.y - 0.35)).label("E"))

    d.add(elm.Capacitor().at(q1.emitter).right(2.0))
    output = d.add(elm.Dot())
    d.add(elm.Label().at((q1.emitter.x + 0.95, q1.emitter.y + 0.45)).label("Cout"))
    d.add(elm.Label().at((output.center.x + 0.3, output.center.y + 0.4)).label("vo"))
    d.add(elm.Resistor().at(output.center).to((output.center.x, ground_y)).label("RL", loc="right"))
    d.add(elm.Ground().at((output.center.x, ground_y)))

    return accessible_svg(
        d,
        "分压偏置射极跟随器的完整电路",
        "NPN射极跟随器。集电极直接连接正电源，基极由分压网络偏置并通过输入耦合电容接收信号；发射极通过电阻接地，并经输出耦合电容驱动负载。",
    )


def common_base_amplifier() -> str:
    d = schemdraw.Drawing(show=False)
    d.config(unit=2.0, fontsize=11, color=INK, lw=2)
    q1 = d.add(elm.BjtNpn().at((5.4, 2.8)).label("Q1", loc="right"))
    top_y, ground_y = 5.6, 0.0

    d.add(elm.Line().at((2.8, top_y)).to((q1.collector.x, top_y)))
    d.add(elm.Dot().at((2.8, top_y)))
    d.add(elm.Label().at((2.8, top_y + 0.35)).label("+VCC"))
    d.add(elm.Resistor().at((q1.collector.x, top_y)).to(q1.collector).label("RC", loc="right"))
    d.add(elm.Dot().at(q1.collector))

    d.add(elm.Capacitor().at(q1.collector).right(3.0))
    output = d.add(elm.Dot())
    d.add(elm.Label().at((q1.collector.x + 1.5, q1.collector.y + 0.45)).label("Cout"))
    d.add(elm.Label().at((output.center.x + 0.25, output.center.y + 0.4)).label("vo"))
    d.add(elm.Resistor().at(output.center).to((output.center.x, ground_y)).label("RL", loc="right"))
    d.add(elm.Ground().at((output.center.x, ground_y)))

    divider_x = 3.45
    d.add(elm.Resistor().at((divider_x, top_y)).to((divider_x, q1.base.y)).label("R1", loc="left"))
    d.add(elm.Line().at((divider_x, q1.base.y)).to(q1.base))
    d.add(elm.Dot().at(q1.base))
    d.add(elm.Resistor().at((divider_x, q1.base.y)).to((divider_x, ground_y)).label("R2", loc="left"))
    d.add(elm.Ground().at((divider_x, ground_y)))
    bypass_x = q1.base.x - 0.65
    d.add(elm.Line().at(q1.base).to((bypass_x, q1.base.y)))
    d.add(elm.Capacitor().at((bypass_x, q1.base.y)).to((bypass_x, ground_y)).label("CB", loc="right"))
    d.add(elm.Ground().at((bypass_x, ground_y)))

    d.add(elm.Resistor().at(q1.emitter).to((q1.emitter.x, ground_y)).label("RE", loc="left"))
    d.add(elm.Ground().at((q1.emitter.x, ground_y)))
    d.add(elm.Dot().at(q1.emitter))
    input_x = q1.emitter.x + 1.15
    d.add(elm.Line().at(q1.emitter).to((input_x, q1.emitter.y)))
    d.add(elm.Capacitor().at((input_x, q1.emitter.y)).down(0.85).label("Cin", loc="right"))
    d.add(elm.Resistor().down(0.85).label("Rs", loc="right"))
    source = d.add(elm.SourceSin().down(1.4).label("vs", loc="right"))
    d.add(elm.Ground().at(source.end))

    return accessible_svg(
        d,
        "单电源共基极放大器的完整电路",
        "NPN共基极放大器。基极由分压网络建立直流偏置并通过旁路电容交流接地；信号经源电阻和输入耦合电容送入发射极，集电极经电阻上拉并通过输出耦合电容驱动负载。",
    )


def mosfet_three_topologies() -> str:
    d = schemdraw.Drawing(show=False)
    d.config(unit=1.8, fontsize=10, color=INK, lw=1.9)
    top_y, ground_y = 5.2, 0.0

    # Common source
    cs = d.add(elm.NFet().at((2.0, 2.6)).label("M1", loc="right"))
    d.add(elm.Line().at((cs.drain.x, top_y)).to((cs.drain.x, top_y - 0.35)))
    d.add(elm.Resistor().at((cs.drain.x, top_y - 0.35)).to(cs.drain).label("RD", loc="right"))
    d.add(elm.Line().at(cs.source).to((cs.source.x, 1.7)))
    d.add(elm.Resistor().at((cs.source.x, 1.7)).to((cs.source.x, ground_y)).label("RS", loc="right"))
    d.add(elm.Ground().at((cs.source.x, ground_y)))
    d.add(elm.Line().at((0.5, cs.gate.y)).to(cs.gate))
    d.add(elm.Label().at((0.5, cs.gate.y + 0.3)).label("vi"))
    d.add(elm.Line().at(cs.drain).right(0.8))
    d.add(elm.Dot())
    d.add(elm.Label().label("vo", loc="right"))
    d.add(elm.Label().at((1.2, 6.45)).label("(a) 共源 CS"))

    # Source follower
    sf = d.add(elm.NFet().at((7.2, 2.6)).label("M2", loc="right"))
    d.add(elm.Line().at((sf.drain.x, top_y)).to(sf.drain))
    d.add(elm.Line().at(sf.source).to((sf.source.x, 1.7)))
    d.add(elm.Resistor().at((sf.source.x, 1.7)).to((sf.source.x, ground_y)).label("RS", loc="right"))
    d.add(elm.Ground().at((sf.source.x, ground_y)))
    d.add(elm.Line().at((5.7, sf.gate.y)).to(sf.gate))
    d.add(elm.Label().at((5.7, sf.gate.y + 0.3)).label("vi"))
    d.add(elm.Line().at(sf.source).right(0.9))
    d.add(elm.Dot())
    d.add(elm.Label().label("vo", loc="right"))
    d.add(elm.Label().at((6.0, 6.45)).label("(b) 源极跟随器 CD"))

    # Common gate
    cg = d.add(elm.NFet().at((12.4, 2.6)).label("M3", loc="right"))
    d.add(elm.Resistor().at((cg.drain.x, top_y)).to(cg.drain).label("RD", loc="right"))
    d.add(elm.Line().at(cg.source).to((cg.source.x, 1.7)))
    d.add(elm.Resistor().at((cg.source.x, 1.7)).to((cg.source.x, ground_y)).label("RS", loc="right"))
    d.add(elm.Ground().at((cg.source.x, ground_y)))
    d.add(elm.Line().at((10.9, cg.gate.y)).to(cg.gate))
    d.add(elm.Ground().at((10.9, cg.gate.y)))
    d.add(elm.Line().at(cg.source).left(0.8))
    d.add(elm.Label().label("vi", loc="left"))
    d.add(elm.Line().at(cg.drain).right(0.8))
    d.add(elm.Dot())
    d.add(elm.Label().label("vo", loc="right"))
    d.add(elm.Label().at((11.3, 6.45)).label("(c) 共栅 CG"))

    for x in (cs.drain.x, sf.drain.x, cg.drain.x):
        d.add(elm.Label().at((x - 0.9, top_y + 0.25)).label("+VDD"))

    return accessible_svg(
        d,
        "共源、源极跟随器与共栅三种MOS放大电路",
        "三幅使用标准NMOS符号的电路图。共源电路从栅极输入、漏极输出；源极跟随器从栅极输入、源极输出；共栅电路的栅极交流接地，从源极输入、漏极输出。",
    )


def opamp_feedback_circuit(kind: str) -> str:
    d = schemdraw.Drawing(show=False)
    d.config(unit=2.0, fontsize=11, color=INK, lw=2)
    op = d.add(elm.Opamp(leads=True).at((4.1, 2.6)).right())
    out = op.out
    sum_node = (op.in1.x - 0.85, op.in1.y)
    d.add(elm.Line().at(sum_node).to(op.in1))
    d.add(elm.Dot().at(sum_node))

    if kind in {"inverting", "integrator", "differentiator"}:
        input_element: elm.Element = (
            elm.Capacitor() if kind == "differentiator" else elm.Resistor()
        )
        input_label = "C1" if kind == "differentiator" else "Rin"
        input_start = (0.8, sum_node[1])
        input_part = d.add(input_element.at(input_start).to(sum_node))
        d.add(
            elm.Label()
            .at((input_part.center.x, input_part.center.y + 0.48))
            .label(input_label)
        )
        d.add(elm.Dot().at(input_start))
        d.add(elm.Label().at((0.6, input_start[1] + 0.35)).label("vi"))
        d.add(elm.Line().at(op.in2).left(0.8))
        d.add(elm.Ground())
    else:
        input_start = (0.8, op.in2.y)
        d.add(elm.Line().at(input_start).to(op.in2))
        d.add(elm.Dot().at(input_start))
        d.add(elm.Label().at((0.6, input_start[1] + 0.35)).label("vi"))

    d.add(elm.Line().at(out).right(1.2))
    output = d.add(elm.Dot())
    d.add(elm.Label().at((output.center.x + 0.55, output.center.y + 0.5)).label("vo"))
    load = d.add(elm.Resistor().at(output.center).down(2.2))
    d.add(elm.Label().at((load.center.x + 0.75, load.center.y)).label("RL"))
    d.add(elm.Ground())

    if kind == "follower":
        d.add(elm.Line().at(out).to((out.x, 4.55)))
        d.add(elm.Line().to((sum_node[0], 4.55)))
        d.add(elm.Line().to(sum_node))
    else:
        feedback = elm.Capacitor() if kind == "integrator" else elm.Resistor()
        feedback_label = "Cf" if kind == "integrator" else "Rf"
        d.add(elm.Line().at(out).to((out.x, 4.55)))
        d.add(
            feedback.at((out.x, 4.55))
            .to((sum_node[0], 4.55))
            .label(feedback_label)
        )
        d.add(elm.Line().to(sum_node))

    if kind == "noninverting":
        # Keep the divider return outside both the feedback rail and the
        # non-inverting input lead.  An explicit endpoint is important here:
        # relying on Schemdraw's current position can silently attach Ground
        # to the preceding Label instead of to Rg.
        ground_resistor = d.add(
            elm.Resistor().at(sum_node).left(2.85)
        )
        d.add(
            elm.Label()
            .at((ground_resistor.center.x, ground_resistor.center.y + 0.48))
            .label("Rg")
        )
        ground_drop = (ground_resistor.end.x, 0.45)
        d.add(elm.Line().at(ground_resistor.end).to(ground_drop))
        d.add(elm.Ground().at(ground_drop))

    titles = {
        "inverting": "反相运算放大器",
        "noninverting": "同相运算放大器",
        "follower": "电压跟随器",
        "integrator": "实际反相积分器的基本连接",
        "differentiator": "实际反相微分器的基本连接",
    }
    descriptions = {
        "inverting": "输入经电阻接到反相端，同相端接地，反馈电阻从输出返回反相端。",
        "noninverting": "输入接同相端，反相端通过接地电阻与输出反馈电阻形成分压网络。",
        "follower": "输入接同相端，输出直接反馈到反相端。",
        "integrator": "输入经电阻接到反相端，电容从输出反馈到反相端，同相端接地。",
        "differentiator": "输入经电容接到反相端，电阻从输出反馈到反相端，同相端接地。",
    }
    return accessible_svg(d, titles[kind], descriptions[kind])


def inverting_output_resistance_test() -> str:
    d = schemdraw.Drawing(show=False)
    d.config(unit=2.0, fontsize=11, color=INK, lw=2)
    op = d.add(elm.Opamp(leads=True).at((4.1, 2.6)).right())
    sum_node = (op.in1.x - 0.85, op.in1.y)
    d.add(elm.Line().at(sum_node).to(op.in1))
    d.add(elm.Dot().at(sum_node))

    input_resistor = d.add(elm.Resistor().at(sum_node).left(1.35))
    d.add(
        elm.Label()
        .at((input_resistor.center.x, input_resistor.center.y + 0.48))
        .label("Rin")
    )
    d.add(elm.Line().at(input_resistor.end).down(0.55))
    d.add(elm.Ground())
    d.add(elm.Line().at(op.in2).left(0.8))
    d.add(elm.Ground())

    d.add(elm.Line().at(op.out).to((op.out.x, 4.55)))
    d.add(
        elm.Resistor()
        .at((op.out.x, 4.55))
        .to((sum_node[0], 4.55))
        .label("Rf")
    )
    d.add(elm.Line().to(sum_node))

    d.add(elm.Line().at(op.out).right(1.2))
    test_node = d.add(elm.Dot())
    d.add(elm.Label().at((test_node.center.x + 0.3, test_node.center.y + 0.35)).label("vt"))
    d.add(elm.SourceI().at(test_node.center).down(2.2).reverse().label("it", loc="right"))
    d.add(elm.Ground())

    return accessible_svg(
        d,
        "反相闭环输出电阻的测试端口",
        "独立输入已置零、负载已移除；反馈电阻和运放受控源保留。在输出端对地接入测试电流源，以测试电压除以注入电流定义闭环输出电阻。",
    )


def practical_integrator() -> str:
    d = schemdraw.Drawing(show=False)
    d.config(unit=2.0, fontsize=11, color=INK, lw=2)
    op = d.add(elm.Opamp(leads=True).at((4.1, 2.6)).right())
    sum_node = (op.in1.x - 0.85, op.in1.y)
    d.add(elm.Line().at(sum_node).to(op.in1))
    d.add(elm.Dot().at(sum_node))
    input_resistor = d.add(
        elm.Resistor().at((0.8, sum_node[1])).to(sum_node)
    )
    d.add(elm.Label().at((input_resistor.center.x, input_resistor.center.y + 0.48)).label("R"))
    d.add(elm.Dot().at((0.8, sum_node[1])))
    d.add(elm.Label().at((0.6, sum_node[1] + 0.35)).label("vi"))
    d.add(elm.Line().at(op.in2).left(0.8))
    d.add(elm.Ground())

    d.add(elm.Line().at(op.out).right(1.2))
    output = d.add(elm.Dot())
    d.add(elm.Label().at((output.center.x + 0.55, output.center.y + 0.5)).label("vo"))
    load = d.add(elm.Resistor().at(output.center).down(2.1))
    d.add(elm.Label().at((load.center.x + 0.75, load.center.y)).label("RL"))
    d.add(elm.Ground())

    for y, element, label in (
        (4.45, elm.Capacitor(), "C"),
        (5.35, elm.Resistor(), "Rf"),
    ):
        d.add(elm.Line().at(op.out).to((op.out.x, y)))
        d.add(
            element.at((op.out.x, y))
            .to((sum_node[0], y))
            .label(label)
        )
        d.add(elm.Line().to(sum_node))

    return accessible_svg(
        d,
        "并联泄放电阻的实用反相积分器",
        "输入电阻接到反相求和节点，反馈电容与泄放电阻并联在输出和反相端之间，同相端接地。泄放电阻限制直流增益，避免失调长期积分至饱和。",
    )


def inverting_summer() -> str:
    d = schemdraw.Drawing(show=False)
    d.config(unit=1.9, fontsize=10, color=INK, lw=2)
    op = d.add(elm.Opamp(leads=True).at((5.0, 2.8)))
    sum_x = 3.35
    for y, name, resistor in ((4.1, "v1", "R1"), (2.8, "v2", "R2"), (1.5, "v3", "R3")):
        d.add(elm.Dot().at((0.6, y)))
        d.add(elm.Label().at((0.45, y + 0.3)).label(name))
        d.add(elm.Resistor().at((0.6, y)).to((sum_x, y)).label(resistor))
        d.add(elm.Line().at((sum_x, y)).to((sum_x, op.in1.y)))
    d.add(elm.Line().at((sum_x, op.in1.y)).to(op.in1))
    d.add(elm.Dot().at((sum_x, op.in1.y)))
    d.add(elm.Line().at(op.in2).left(0.75))
    d.add(elm.Ground())

    d.add(elm.Line().at(op.out).to((op.out.x, 5.1)))
    d.add(elm.Resistor().at((op.out.x, 5.1)).to((sum_x, 5.1)).label("Rf"))
    d.add(elm.Line().to((sum_x, op.in1.y)))
    d.add(elm.Line().at(op.out).right(1.0))
    out = d.add(elm.Dot())
    d.add(elm.Label().at((out.center.x + 0.55, out.center.y + 0.5)).label("vo"))
    load = d.add(elm.Resistor().at(out.center).down(2.0))
    d.add(elm.Label().at((load.center.x + 0.75, load.center.y)).label("RL"))
    d.add(elm.Ground())
    return accessible_svg(
        d,
        "三个输入的反相加权求和器",
        "三个输入分别经R1、R2和R3汇入反相求和节点，反馈电阻Rf从输出返回该节点，同相端接地。",
    )


def four_resistor_difference_amplifier() -> str:
    d = schemdraw.Drawing(show=False)
    d.config(unit=2.0, fontsize=10, color=INK, lw=2)
    op = d.add(elm.Opamp(leads=True).at((5.0, 2.8)))

    node_x = 3.0
    inverting_node = (node_x, op.in1.y)
    noninverting_node = (node_x, op.in2.y)
    d.add(elm.Dot().at((0.7, op.in1.y)))
    d.add(elm.Label().at((0.5, op.in1.y + 0.32)).label("v1"))
    d.add(elm.Resistor().at((0.7, op.in1.y)).to(inverting_node).label("R1"))
    d.add(elm.Dot().at(inverting_node))
    d.add(elm.Line().at(inverting_node).to(op.in1))
    d.add(elm.Line().at(op.out).to((op.out.x, 5.0)))
    d.add(elm.Resistor().at((op.out.x, 5.0)).to((node_x, 5.0)).label("R2"))
    d.add(elm.Line().to(inverting_node))

    d.add(elm.Dot().at((0.7, op.in2.y)))
    d.add(elm.Label().at((0.5, op.in2.y + 0.32)).label("v2"))
    d.add(elm.Resistor().at((0.7, op.in2.y)).to(noninverting_node).label("R3"))
    d.add(elm.Dot().at(noninverting_node))
    d.add(elm.Line().at(noninverting_node).to(op.in2))
    d.add(elm.Resistor().at(noninverting_node).down(0.85).label("R4", loc="left"))
    d.add(elm.Ground())

    d.add(elm.Line().at(op.out).right(1.0))
    out = d.add(elm.Dot())
    d.add(elm.Label().at((out.center.x + 0.55, out.center.y + 0.5)).label("vo"))
    load = d.add(elm.Resistor().at(out.center).down(2.0))
    d.add(elm.Label().at((load.center.x + 0.75, load.center.y)).label("RL"))
    d.add(elm.Ground())
    return accessible_svg(
        d,
        "四电阻差分放大器的指定拓扑",
        "v1经R1连接反相端，R2从输出反馈到反相端；v2经R3连接同相端，R4从同相端接地。",
    )


def bjt_dc_case(
    *,
    title: str,
    vcc: str,
    rc: str,
    vbase: str,
    rb: str,
    emitter: str = "0 V",
) -> str:
    """Draw the complete two-supply-reference BJT state-test circuit."""
    d = schemdraw.Drawing(show=False)
    d.config(unit=2.0, fontsize=11, color=INK, lw=2)
    q = d.add(elm.BjtNpn().at((4.8, 2.4)).label("Q (NPN)", loc="right"))
    top_y = 5.0
    d.add(elm.Dot().at((q.collector.x, top_y)))
    d.add(elm.Label().at((q.collector.x - 1.2, top_y + 0.12)).label(vcc))
    d.add(elm.Resistor().at((q.collector.x, top_y)).to(q.collector))
    d.add(elm.Label().at((q.collector.x + 1.35, (top_y + q.collector.y) / 2)).label(rc))
    d.add(elm.Dot().at(q.collector))
    d.add(elm.Label().at((q.collector.x + 0.25, q.collector.y + 0.28)).label("C"))
    d.add(elm.Dot().at((0.5, q.base.y)))
    d.add(elm.Label().at((0.05, q.base.y + 0.42)).label(vbase))
    d.add(elm.Resistor().at((0.5, q.base.y)).to((3.2, q.base.y)).label(rb))
    d.add(elm.Line().to(q.base))
    d.add(elm.Dot().at(q.base))
    d.add(elm.Label().at((q.base.x - 0.2, q.base.y + 0.3)).label("B"))
    if emitter == "0 V":
        d.add(elm.Line().at(q.emitter).down(0.9))
        d.add(elm.Ground())
    else:
        source = d.add(elm.SourceV().at(q.emitter).down(1.45).reverse())
        d.add(elm.Label().at((source.center.x + 0.85, source.center.y)).label(emitter))
        d.add(elm.Ground())
    d.add(elm.Label().at((q.emitter.x + 0.22, q.emitter.y - 0.2)).label("E"))
    d.add(elm.Arrow().at((q.collector.x + 0.45, 4.35)).down(0.7).label("IC", loc="right"))
    return accessible_svg(
        d,
        title,
        f"NPN晶体管状态判断电路。集电极经{rc}接{vcc}，基极经{rb}接{vbase}，发射极参考为{emitter}；所有电源共用地参考。",
    )


def nmos_dc_case(
    *,
    title: str,
    vdd: str,
    rd: str,
    vgate: str,
    source: str = "0 V",
) -> str:
    """Draw the complete resistor-loaded NMOS state-test circuit."""
    d = schemdraw.Drawing(show=False)
    d.config(unit=2.0, fontsize=11, color=INK, lw=2)
    m = d.add(elm.NFet().at((4.8, 2.4)).label("M (NMOS)", loc="right"))
    top_y = 5.0
    d.add(elm.Dot().at((m.drain.x, top_y)))
    d.add(elm.Label().at((m.drain.x - 1.15, top_y + 0.12)).label(vdd))
    d.add(elm.Resistor().at((m.drain.x, top_y)).to(m.drain))
    d.add(elm.Label().at((m.drain.x + 1.35, (top_y + m.drain.y) / 2)).label(rd))
    d.add(elm.Dot().at(m.drain))
    d.add(elm.Label().at((m.drain.x + 0.24, m.drain.y + 0.3)).label("D"))
    d.add(elm.Dot().at((0.7, m.gate.y)))
    d.add(elm.Label().at((0.55, m.gate.y + 0.35)).label(vgate))
    d.add(elm.Line().at((0.7, m.gate.y)).to(m.gate))
    d.add(elm.Label().at((m.gate.x - 0.22, m.gate.y + 0.3)).label("G"))
    if source == "0 V":
        d.add(elm.Line().at(m.source).down(0.9))
        d.add(elm.Ground())
    else:
        source_element = d.add(
            elm.SourceV().at(m.source).down(1.45).reverse()
        )
        d.add(elm.Label().at((source_element.center.x + 0.85, source_element.center.y)).label(source))
        d.add(elm.Ground())
    d.add(elm.Label().at((m.source.x + 0.24, m.source.y - 0.2)).label("S, B"))
    d.add(elm.Arrow().at((m.drain.x + 0.45, 4.35)).down(0.7).label("ID", loc="right"))
    return accessible_svg(
        d,
        title,
        f"电阻负载NMOS状态判断电路。漏极经{rd}接{vdd}，栅极由共地理想源设为{vgate}，源极和体端参考为{source}。",
    )


def bjt_divider_bias() -> str:
    d = schemdraw.Drawing(show=False)
    d.config(unit=2.0, fontsize=11, color=INK, lw=2)
    q = d.add(elm.BjtNpn().at((5.0, 2.5)).label("Q1", loc="right"))
    top, bottom, xdiv = 5.2, 0.0, 2.7
    d.add(elm.Line().at((xdiv, top)).to((q.collector.x, top)))
    d.add(elm.Dot().at((xdiv, top)))
    d.add(elm.Label().at((xdiv, top + 0.34)).label("+12.0 V"))
    d.add(elm.Resistor().at((q.collector.x, top)).to(q.collector))
    d.add(elm.Label().at((q.collector.x + 1.45, (top + q.collector.y) / 2)).label("RC  2.20 kΩ"))
    d.add(elm.Resistor().at((xdiv, top)).to((xdiv, q.base.y)))
    d.add(elm.Label().at((xdiv - 1.4, (top + q.base.y) / 2)).label("R1  82.0 kΩ"))
    d.add(elm.Line().at((xdiv, q.base.y)).to(q.base))
    d.add(elm.Dot().at((xdiv, q.base.y)))
    d.add(elm.Resistor().at((xdiv, q.base.y)).to((xdiv, bottom)))
    d.add(elm.Label().at((xdiv - 1.4, q.base.y / 2)).label("R2  18.0 kΩ"))
    d.add(elm.Ground().at((xdiv, bottom)))
    d.add(elm.Resistor().at(q.emitter).to((q.emitter.x, bottom)))
    d.add(elm.Label().at((q.emitter.x + 1.4, q.emitter.y / 2)).label("RE  1.00 kΩ"))
    d.add(elm.Ground().at((q.emitter.x, bottom)))
    return accessible_svg(
        d,
        "分压—发射极电阻偏置完整电路",
        "十二伏单电源NPN偏置电路。R1和R2构成基极分压器，集电极经RC接电源，发射极经RE接公共地。",
    )


def nmos_fixed_bias(*, divider: bool) -> str:
    d = schemdraw.Drawing(show=False)
    d.config(unit=2.0, fontsize=11, color=INK, lw=2)
    m = d.add(elm.NFet().at((5.0, 2.5)).label("M1", loc="right"))
    top, bottom = 5.2, 0.0
    d.add(elm.Dot().at((m.drain.x, top)))
    d.add(elm.Label().at((m.drain.x - 1.1, top + 0.12)).label("+12.0 V" if divider else "+10.0 V"))
    d.add(elm.Resistor().at((m.drain.x, top)).to(m.drain))
    d.add(elm.Label().at((m.drain.x + 1.45, (top + m.drain.y) / 2)).label("RD  2.00 kΩ"))
    if divider:
        x = 2.7
        d.add(elm.Line().at((x, top)).to((m.drain.x, top)))
        d.add(elm.Resistor().at((x, top)).to((x, m.gate.y)))
        d.add(elm.Label().at((x - 1.45, (top + m.gate.y) / 2)).label("R1  1.00 MΩ"))
        d.add(elm.Resistor().at((x, m.gate.y)).to((x, bottom)))
        d.add(elm.Label().at((x - 1.45, m.gate.y / 2)).label("R2  500 kΩ"))
        d.add(elm.Ground().at((x, bottom)))
        d.add(elm.Line().at((x, m.gate.y)).to(m.gate))
        d.add(elm.Resistor().at(m.source).to((m.source.x, bottom)))
        d.add(elm.Label().at((m.source.x + 1.4, m.source.y / 2)).label("RS  1.00 kΩ"))
        d.add(elm.Ground().at((m.source.x, bottom)))
        title = "栅分压—源极电阻偏置完整电路"
        desc = "十二伏NMOS偏置电路。栅极由一兆欧和五百千欧分压，漏极经两千欧接电源，源极经一千欧接地，体端与源端相连。"
    else:
        d.add(elm.Dot().at((0.8, m.gate.y)))
        d.add(elm.Label().at((0.6, m.gate.y + 0.35)).label("+3.00 V"))
        d.add(elm.Line().at((0.8, m.gate.y)).to(m.gate))
        d.add(elm.Line().at(m.source).down(0.9))
        d.add(elm.Ground())
        title = "固定栅压的电阻负载 NMOS 完整电路"
        desc = "十伏电源通过两千欧漏极电阻驱动NMOS，栅极由共地三伏理想源偏置，源极和体端接公共地。"
    return accessible_svg(d, title, desc)


def powered_opamp_symbol() -> str:
    d = schemdraw.Drawing(show=False)
    d.config(unit=2.0, fontsize=11, color=INK, lw=2)
    op = d.add(elm.Opamp(leads=True).at((4.2, 2.6)))
    d.add(elm.Dot().at((0.7, op.in2.y)))
    d.add(elm.Label().at((0.5, op.in2.y + 0.35)).label("v+"))
    d.add(elm.Line().to(op.in2))
    d.add(elm.Dot().at((0.7, op.in1.y)))
    d.add(elm.Label().at((0.5, op.in1.y + 0.35)).label("v−"))
    d.add(elm.Line().to(op.in1))
    d.add(elm.Line().at(op.out).right(1.2))
    out = d.add(elm.Dot())
    d.add(elm.Label().at((out.center.x + 0.55, out.center.y + 0.5)).label("vo"))
    load = d.add(elm.Resistor().at(out.center).down(1.8))
    d.add(elm.Label().at((load.center.x + 0.72, load.center.y)).label("RL"))
    d.add(elm.Ground())
    d.add(elm.Line().at(op.vd).up(0.7))
    d.add(elm.Label().label("+VCC", loc="top"))
    d.add(elm.Line().at(op.vs).down(0.7))
    d.add(elm.Label().label("−VEE", loc="bottom"))
    return accessible_svg(
        d,
        "带供电、输入符号和负载返回的运放符号",
        "运算放大器的同相端、反相端、正负供电、输出端和对地负载均完整画出。差分输入定义为v+减v−。",
    )


def practical_differentiator() -> str:
    d = schemdraw.Drawing(show=False)
    d.config(unit=2.0, fontsize=10, color=INK, lw=2)
    op = d.add(elm.Opamp(leads=True).at((5.1, 2.5)))
    d.add(elm.Dot().at((0.4, op.in1.y)))
    d.add(elm.Label().at((0.3, op.in1.y + 0.35)).label("vi"))
    d.add(elm.Capacitor().at((0.4, op.in1.y)).right(1.25).label("C"))
    d.add(elm.Resistor().right(1.5).label("Rin"))
    node = d.add(elm.Dot())
    d.add(elm.Line().to(op.in1))
    d.add(elm.Line().at(op.in2).left(0.8))
    d.add(elm.Ground())
    d.add(elm.Line().at(op.out).right(1.0))
    out = d.add(elm.Dot())
    d.add(elm.Label().at((out.center.x + 0.55, out.center.y + 0.5)).label("vo"))
    for y, element, label, label_dx in (
        (4.1, elm.Resistor(), "Rf", -0.75),
        (4.9, elm.Capacitor(), "Cf", 0.75),
    ):
        d.add(elm.Line().at(op.out).to((op.out.x, y)))
        branch = d.add(element.at((op.out.x, y)).to((node.center.x, y)))
        d.add(
            elm.Label()
            .at((branch.center.x + label_dx, branch.center.y + 0.35))
            .label(label)
        )
        d.add(elm.Line().to(node.center))
    return accessible_svg(
        d,
        "输入串联电阻、反馈并联电容的实用带限微分器",
        "输入电容与Rin串联后进入反相端，输出通过Rf与Cf并联反馈，同相端接地。Rin限制高频输入电流，Cf降低高频反馈阻抗。",
    )


def schmitt_trigger() -> str:
    d = schemdraw.Drawing(show=False)
    d.config(unit=2.0, fontsize=10, color=INK, lw=2)
    op = d.add(elm.Opamp(leads=True).at((5.0, 2.7)))
    d.add(elm.Dot().at((0.6, op.in1.y)))
    d.add(elm.Label().at((0.45, op.in1.y + 0.34)).label("vi"))
    d.add(elm.Line().to(op.in1))
    plus_node = (3.15, op.in2.y)
    d.add(elm.Dot().at(plus_node))
    d.add(elm.Line().at(plus_node).to(op.in2))
    d.add(elm.Resistor().at((0.6, op.in2.y)).to(plus_node).label("R2"))
    d.add(elm.Dot().at((0.6, op.in2.y)))
    d.add(elm.Label().at((0.35, op.in2.y + 0.34)).label("Vref"))
    d.add(elm.Line().at(op.out).right(1.0))
    out = d.add(elm.Dot())
    d.add(elm.Label().at((out.center.x + 0.55, out.center.y + 0.5)).label("vo"))
    feedback_y = 0.45
    d.add(elm.Line().at(op.out).to((op.out.x, feedback_y)))
    feedback = d.add(
        elm.Resistor()
        .at((op.out.x, feedback_y))
        .to((plus_node[0], feedback_y))
    )
    d.add(elm.Label().at((feedback.center.x, feedback.center.y - 0.35)).label("R1"))
    d.add(elm.Line().to(plus_node))
    load = d.add(elm.Resistor().at(out.center).down(1.8))
    d.add(elm.Label().at((load.center.x + 0.72, load.center.y)).label("RL"))
    d.add(elm.Ground())
    return accessible_svg(
        d,
        "指定的反相施密特触发器",
        "输入vi只接反相端。输出经R1回送同相端，同相端再经R2连接参考Vref，构成正反馈和双阈值。",
    )


def comparator_variants() -> str:
    d = schemdraw.Drawing(show=False)
    d.config(unit=1.55, fontsize=8.5, color=INK, lw=1.8)
    for x, open_collector in ((3.0, False), (11.0, True)):
        # Set orientation explicitly: the first branch ends downward at ground,
        # so relying on Schemdraw's inherited direction rotates the second op-amp.
        op = d.add(elm.Opamp(leads=True).at((x, 2.6)).right())
        d.add(elm.Dot().at((x - 2.5, op.in2.y)))
        d.add(elm.Label().at((x - 2.65, op.in2.y + 0.3)).label("vi"))
        d.add(elm.Line().to(op.in2))
        d.add(elm.Dot().at((x - 2.5, op.in1.y)))
        d.add(elm.Label().at((x - 2.8, op.in1.y + 0.3)).label("Vref"))
        d.add(elm.Line().to(op.in1))
        d.add(elm.Line().at(op.out).right(1.0))
        out = d.add(elm.Dot())
        d.add(elm.Label().at((out.center.x + 0.5, out.center.y + 0.45)).label("vo"))
        if open_collector:
            pullup = d.add(
                elm.Resistor().at(out.center).up(1.55).label("RPU", loc="right")
            )
            d.add(
                elm.Label()
                .at((pullup.end.x - 0.75, pullup.end.y + 0.28))
                .label("+VPU")
            )
            d.add(elm.Label().at((x - 1.25, 5.35)).label("(b) 开集/开漏输出"))
        else:
            load = d.add(elm.Resistor().at(out.center).down(1.55))
            d.add(elm.Label().at((load.center.x + 0.62, load.center.y)).label("RL"))
            d.add(elm.Ground())
            d.add(elm.Label().at((x - 1.0, 5.35)).label("(a) 推挽输出"))
    return accessible_svg(
        d,
        "同相比较器的两种输出拓扑",
        "两幅比较器均以vi接同相端、Vref接反相端且没有反馈。左图为推挽输出驱动负载，右图为开集或开漏输出并使用外部上拉电阻。",
    )


def rc_filter(*, highpass: bool) -> str:
    d = schemdraw.Drawing(show=False)
    d.config(unit=2.2, fontsize=12, color=INK, lw=2)
    source = d.add(elm.SourceSin().at((0.5, 0.0)).up(2.5).label("vs", loc="left"))
    d.add(elm.Ground().at(source.start))
    if highpass:
        d.add(elm.Capacitor().at(source.end).right(2.4).label("C"))
        shunt = elm.Resistor()
        title = "一阶 RC 高通完整电路"
        desc = "交流电压源经串联电容到输出节点，电阻由输出节点接公共地，输出取电阻两端。"
    else:
        d.add(elm.Resistor().at(source.end).right(2.4).label("R"))
        shunt = elm.Capacitor()
        title = "一阶 RC 低通完整电路"
        desc = "交流电压源经串联电阻到输出节点，电容由输出节点接公共地，输出取电容两端。"
    out = d.add(elm.Dot())
    d.add(elm.Label().at((out.center.x + 0.62, out.center.y + 0.52)).label("vo"))
    shunt_element = d.add(shunt.at(out.center).down(2.5))
    d.add(
        elm.Label()
        .at((shunt_element.center.x + 0.82, shunt_element.center.y))
        .label("R" if highpass else "C")
    )
    d.add(elm.Ground())
    return accessible_svg(d, title, desc)


def bjt_small_signal(kind: str) -> str:
    """Draw complete midband hybrid-pi networks with explicit returns."""
    d = schemdraw.Drawing(show=False)
    d.config(unit=1.8, fontsize=10, color=INK, lw=1.9)
    ground_y = 0.0
    b = (3.2, 2.4)
    if kind == "ce_bypassed":
        e, c = (5.0, ground_y), (7.0, 2.8)
        title = "共射极中频混合-π小信号图"
        desc = "信号源经Rs驱动基极，偏置等效电阻接交流地，rπ从基极接交流地；集电极节点并联RC、RL和由集电极指向发射极的gmvπ受控电流源。"
    elif kind == "ce_degenerated":
        e, c = (5.0, 1.25), (7.0, 3.0)
        title = "有发射极退化的共射极小信号回路"
        desc = "rπ连接基极与发射极，发射极经RE接交流地；受控电流源gmvπ从集电极流向发射极，集电极经等效负载接地。"
    elif kind == "cc":
        e, c = (6.0, 2.0), (6.0, 4.4)
        title = "射极跟随器的完整中频小信号图"
        desc = "基极由信号源和源电阻驱动并经偏置电阻接地，rπ连接基极与输出发射极；发射极经RE和RL并联接地，受控电流源从交流接地的集电极流向发射极。"
    elif kind == "cb":
        e, c = (4.5, 2.0), (6.8, 3.5)
        b = (3.0, ground_y)
        title = "共基极的中频混合-π小信号图"
        desc = "基极由旁路电容作用成为交流地；输入经源电阻送入发射极，rπ从发射极接基极交流地，gmvπ受控源跨接集电极和发射极，集电极经RC与RL等效负载接地。"
    else:
        raise ValueError(kind)

    if kind == "cb":
        src = d.add(elm.SourceSin().at((0.4, ground_y)).up(e[1]).label("vs", loc="left"))
        d.add(elm.Ground().at(src.start))
        d.add(elm.Resistor().at(src.end).to(e).label("Rs"))
        d.add(elm.Dot().at(e))
        d.add(elm.Resistor().at(e).down(e[1]).label("RE", loc="left"))
        d.add(elm.Ground())
        d.add(elm.Resistor().at(e).to(b).label("rπ"))
        d.add(elm.Ground().at(b))
    else:
        src = d.add(elm.SourceSin().at((0.4, ground_y)).up(b[1]).label("vs", loc="left"))
        d.add(elm.Ground().at(src.start))
        d.add(elm.Resistor().at(src.end).to(b).label("Rs"))
        d.add(elm.Dot().at(b))
        d.add(elm.Resistor().at(b).down(b[1]).label("RB", loc="left"))
        d.add(elm.Ground())
        d.add(elm.Resistor().at(b).to(e).label("rπ"))
        d.add(elm.Dot().at(e))

    if kind == "ce_degenerated":
        d.add(elm.Resistor().at(e).down(e[1]).label("RE", loc="left"))
        d.add(elm.Ground())
    elif kind == "ce_bypassed":
        d.add(elm.Ground().at(e))
    elif kind == "cc":
        for dx in (0.0, 1.25):
            d.add(elm.Line().at(e).to((e[0] + dx, e[1])))
            d.add(elm.Resistor().at((e[0] + dx, e[1])).down(e[1]))
            d.add(elm.Ground())
        d.add(elm.Label().at((e[0] - 0.7, e[1] - 0.9)).label("RE"))
        d.add(elm.Label().at((e[0] + 1.75, e[1] - 0.9)).label("RL"))
        d.add(elm.Label().at((e[0] + 0.35, e[1] + 0.38)).label("vo"))
        d.add(elm.Line().at(c).left(1.0))
        d.add(elm.Ground())

    gm_source = d.add(
        elm.SourceControlledI()
        .endpoints(c, e)
    )
    gm_label_offset = (0.75, 0.0) if kind == "cc" else (0.0, 0.55)
    d.add(
        elm.Label()
        .at(
            (
                gm_source.center.x + gm_label_offset[0],
                gm_source.center.y + gm_label_offset[1],
            )
        )
        .label("gm vπ")
    )
    if kind != "cc":
        for dx in (0.0, 1.3):
            node = (c[0] + dx, c[1])
            d.add(elm.Line().at(c).to(node))
            d.add(elm.Resistor().at(node).down(c[1]))
            d.add(elm.Ground())
        d.add(elm.Dot().at(c))
        d.add(elm.Label().at((c[0] - 0.55, c[1] - 1.35)).label("RC"))
        d.add(elm.Label().at((c[0] + 1.8, c[1] - 1.35)).label("RL"))
        d.add(elm.Label().at((c[0] + 0.35, c[1] + 0.38)).label("vo"))
    return accessible_svg(d, title, desc)


def mos_small_signal_triptych() -> str:
    d = schemdraw.Drawing(show=False)
    d.config(unit=1.4, fontsize=8.5, color=INK, lw=1.8)
    ground_y = 0.0
    for index, kind in enumerate(("CS", "SF", "CG")):
        x0 = index * 5.0
        if kind == "CS":
            g = (x0 + 0.7, 2.2)
            s, drain, load_x = (
                (x0 + 2.7, ground_y),
                (x0 + 2.7, 3.2),
                x0 + 4.0,
            )
            d.add(elm.Dot().at(g))
            d.add(elm.Label().at((g[0] - 0.25, g[1] + 0.3)).label("vi"))
            d.add(elm.Resistor().at(g).down(g[1]).label("RG", loc="left"))
            d.add(elm.Ground())
            gm_source = d.add(elm.SourceControlledI().endpoints(drain, s))
            d.add(
                elm.Label()
                .at((gm_source.center.x - 0.72, gm_source.center.y))
                .label("gmvgs")
            )
            d.add(elm.Ground().at(s))
            d.add(elm.Line().at(drain).to((load_x, drain[1])))
            load = d.add(
                elm.Resistor().at((load_x, drain[1])).down(drain[1])
            )
            d.add(
                elm.Label()
                .at((load.center.x + 0.58, load.center.y))
                .label("RD∥RL")
            )
            d.add(elm.Ground())
            d.add(elm.Dot().at(drain))
            d.add(
                elm.Label().at((drain[0] - 0.35, drain[1] + 0.35)).label("vo")
            )
        elif kind == "SF":
            g = (x0 + 0.7, 2.2)
            s, drain, load_x = (
                (x0 + 2.7, 1.6),
                (x0 + 2.7, 4.2),
                x0 + 4.0,
            )
            d.add(elm.Dot().at(g))
            d.add(elm.Label().at((g[0] - 0.25, g[1] + 0.3)).label("vi"))
            d.add(elm.Resistor().at(g).down(g[1]).label("RG", loc="left"))
            d.add(elm.Ground())
            gm_source = d.add(elm.SourceControlledI().endpoints(drain, s))
            d.add(
                elm.Label()
                .at((gm_source.center.x + 0.72, gm_source.center.y))
                .label("gmvgs")
            )
            # Draw the AC-ground symbol in its conventional downward
            # orientation on a short side branch.
            ac_ground = (x0 + 1.7, drain[1])
            ground_drop = (ac_ground[0], drain[1] - 0.55)
            d.add(elm.Line().at(drain).to(ac_ground))
            d.add(elm.Line().at(ac_ground).to(ground_drop))
            d.add(elm.Ground().at(ground_drop))
            d.add(elm.Line().at(s).to((load_x, s[1])))
            load = d.add(elm.Resistor().at((load_x, s[1])).down(s[1]))
            d.add(
                elm.Label()
                .at((load.center.x - 0.82, load.center.y))
                .label("RS∥RL")
            )
            d.add(elm.Ground())
            d.add(elm.Dot().at(s))
            d.add(elm.Label().at((s[0] - 0.35, s[1] + 0.35)).label("vo"))
        else:
            s, drain, load_x = (
                (x0 + 2.4, 1.6),
                (x0 + 2.4, 3.6),
                x0 + 4.0,
            )
            src = d.add(
                elm.SourceSin()
                .at((x0 + 0.1, ground_y))
                .up(s[1])
                .label("vs", loc="left")
            )
            d.add(elm.Ground().at(src.start))
            d.add(elm.Resistor().at(src.end).to(s).label("Rs"))
            d.add(elm.Dot().at(s))
            d.add(elm.Resistor().at(s).down(s[1]).label("RS", loc="left"))
            d.add(elm.Ground())
            gm_source = d.add(elm.SourceControlledI().endpoints(drain, s))
            d.add(
                elm.Label()
                .at((gm_source.center.x - 0.72, gm_source.center.y))
                .label("gmvgs")
            )
            d.add(elm.Line().at(drain).to((load_x, drain[1])))
            load = d.add(
                elm.Resistor().at((load_x, drain[1])).down(drain[1])
            )
            d.add(
                elm.Label()
                .at((load.center.x + 0.58, load.center.y))
                .label("RD∥RL")
            )
            d.add(elm.Ground())
            d.add(elm.Dot().at(drain))
            d.add(
                elm.Label().at((drain[0] - 0.35, drain[1] + 0.35)).label("vo")
            )
            gate_ground = (x0 + 0.7, 3.6)
            d.add(elm.Dot().at(gate_ground))
            d.add(
                elm.Label()
                .at((gate_ground[0] + 0.45, gate_ground[1] + 0.25))
                .label("g=交流地")
            )
            d.add(elm.Ground().at(gate_ground))
        d.add(elm.Label().at((x0 + 1.5, 5.1)).label(f"({chr(97 + index)}) {kind}"))
    return accessible_svg(
        d,
        "三种 MOS 组态的中频小信号图",
        "共源、源极跟随器和共栅三个小信号网络均画出栅极偏置返回、gmvgs受控电流源、源漏负载和交流地。MOS栅极没有rπ支路。",
    )


def input_coupling_highpass() -> str:
    d = schemdraw.Drawing(show=False)
    d.config(unit=2.0, fontsize=11, color=INK, lw=2)
    src = d.add(elm.SourceSin().at((0.4, 0)).up(2.4).label("vs", loc="left"))
    d.add(elm.Ground().at(src.start))
    d.add(elm.Resistor().at(src.end).right(1.8).label("Rs"))
    d.add(elm.Capacitor().right(1.5).label("Cin"))
    out = d.add(elm.Dot())
    d.add(elm.Label().at((out.center.x + 0.25, out.center.y + 0.7)).label("vi"))
    d.add(elm.Resistor().at(out.center).down(2.4))
    d.add(elm.Label().at((out.center.x + 0.95, out.center.y - 1.2)).label("Rin"))
    d.add(elm.Ground())
    return accessible_svg(
        d,
        "单个输入耦合电容形成的一阶高通",
        "共地交流源经源电阻Rs和串联耦合电容Cin驱动输入节点，输入等效电阻Rin由该节点接交流地；电容看到的总电阻为Rs加Rin。",
    )


def dc_ac_pair() -> str:
    d = schemdraw.Drawing(show=False)
    d.config(unit=1.55, fontsize=8.5, color=INK, lw=1.8)
    q = d.add(elm.BjtNpn().at((3.0, 2.1)).label("Q1", loc="right"))
    d.add(elm.Resistor().at((q.collector.x, 5.0)).to(q.collector).label("RC", loc="right"))
    d.add(elm.Label().at((q.collector.x - 0.75, 5.35)).label("+VCC"))
    d.add(elm.Line().at((0.5, q.base.y)).to(q.base).label("偏置"))
    d.add(elm.Line().at(q.emitter).down(0.8))
    d.add(elm.Ground())
    d.add(elm.Label().at((1.3, 5.7)).label("(a) 直流图：电容开路"))

    xoff = 7.0
    b, e, c = (xoff + 1.0, 2.2), (xoff + 3.0, 0), (xoff + 4.8, 3.0)
    d.add(elm.Dot().at(b))
    d.add(elm.Label().at((b[0] - 0.25, b[1] + 0.3)).label("vi"))
    d.add(elm.Resistor().at(b).to(e).label("rπ"))
    d.add(elm.Ground().at(e))
    gm_source = d.add(
        elm.SourceControlledI()
        .endpoints(c, e)
    )
    d.add(
        elm.Label()
        .at((gm_source.center.x, gm_source.center.y + 0.55))
        .label("gmvπ")
    )
    d.add(elm.Resistor().at(c).down(3.0).label("RC", loc="left"))
    d.add(elm.Ground())
    d.add(elm.Label().at((c[0] + 0.2, c[1] + 0.3)).label("vo"))
    d.add(elm.Label().at((xoff + 1.2, 5.7)).label("(b) 中频增量图：电源为交流地"))
    return accessible_svg(
        d,
        "同一放大器的直流图与中频小信号图",
        "左侧保留直流电源和晶体管以求静态工作点；右侧把直流电源置为交流地，用rπ与gmvπ受控源描述Q点附近的中频增量。",
    )


def differential_pair(*, active_load: bool = False) -> str:
    d = schemdraw.Drawing(show=False)
    d.config(unit=1.7, fontsize=9, color=INK, lw=1.8)
    q1 = d.add(elm.BjtNpn().at((4.2, 2.2)).label("Q1", loc="left"))
    q2 = d.add(elm.BjtNpn().at((8.0, 2.2)).label("Q2", loc="right"))
    d.add(elm.Dot().at((0.7, q1.base.y)))
    d.add(elm.Label().at((0.5, q1.base.y + 0.3)).label("v1"))
    d.add(elm.Line().to(q1.base))
    d.add(elm.Dot().at((11.2, q2.base.y)))
    d.add(elm.Label().at((11.2, q2.base.y + 0.3)).label("v2"))
    d.add(elm.Line().at((11.2, q2.base.y)).to(q2.base))
    common = ((q1.emitter.x + q2.emitter.x) / 2, 0.8)
    d.add(elm.Line().at(q1.emitter).to(common))
    d.add(elm.Line().at(q2.emitter).to(common))
    d.add(elm.Dot().at(common))
    tail = d.add(elm.SourceI().at(common).down(1.7).label("IT", loc="right"))
    d.add(elm.Label().at((tail.end.x, tail.end.y - 0.25)).label("−VEE"))

    if not active_load:
        top = 5.5
        d.add(elm.Line().at((q1.collector.x, top)).to((q2.collector.x, top)))
        d.add(elm.Label().at(((q1.collector.x + q2.collector.x) / 2, top + 0.3)).label("+VCC"))
        for q, name in ((q1, "vo1"), (q2, "vo2")):
            d.add(elm.Resistor().at((q.collector.x, top)).to(q.collector).label("RC", loc="right"))
            d.add(elm.Dot().at(q.collector))
            d.add(elm.Label().at((q.collector.x + 0.2, q.collector.y + 0.25)).label(name))
        return accessible_svg(
            d,
            "带双电阻负载的对称 NPN 差分对",
            "匹配NPN差分对由两个集电电阻接正电源，发射极汇合后由理想尾电流源接负电源；v1和v2分别驱动两基极，vo1和vo2取自两集电极。",
        )

    # The preceding tail source points downward; reset orientation so the PNP
    # pair is not rotated by Schemdraw's inherited drawing direction.
    p1 = d.add(elm.BjtPnp().at((4.2, 5.0)).right().label("Q3", loc="left"))
    p2 = d.add(elm.BjtPnp().at((8.0, 5.0)).right().label("Q4", loc="right"))
    top = 7.0
    d.add(elm.Line().at(p1.emitter).to((p1.emitter.x, top)))
    d.add(elm.Line().at(p2.emitter).to((p2.emitter.x, top)))
    d.add(elm.Line().at((p1.emitter.x, top)).to((p2.emitter.x, top)))
    d.add(elm.Label().at(((p1.emitter.x + p2.emitter.x) / 2, top + 0.3)).label("+VCC"))
    d.add(elm.Line().at(p1.base).to(p2.base))
    d.add(elm.Line().at(p1.collector).to(p1.base))
    d.add(elm.Line().at(p1.collector).to(q1.collector))
    d.add(elm.Line().at(p2.collector).to(q2.collector))
    d.add(elm.Dot().at(q2.collector))
    d.add(elm.Label().at((q2.collector.x + 0.25, q2.collector.y + 0.3)).label("vo"))
    return accessible_svg(
        d,
        "带 PNP 电流镜有源负载的 NPN 差分级",
        "下方NPN差分对共用尾电流源，上方匹配PNP管构成电流镜有源负载。Q3集电极与基极相连并与Q4基极共接，Q4集电极和Q2集电极汇合成单端高阻输出。",
    )


def bjt_current_mirror() -> str:
    d = schemdraw.Drawing(show=False)
    d.config(unit=1.8, fontsize=10, color=INK, lw=1.9)
    q1 = d.add(elm.BjtNpn().at((4.0, 2.1)).label("Q1", loc="left"))
    q2 = d.add(elm.BjtNpn().at((8.0, 2.1)).label("Q2", loc="right"))
    d.add(elm.Line().at(q1.emitter).to((q1.emitter.x, 0)))
    d.add(elm.Line().at(q2.emitter).to((q2.emitter.x, 0)))
    d.add(elm.Line().at((q1.emitter.x, 0)).to((q2.emitter.x, 0)))
    d.add(elm.Ground().at(((q1.emitter.x + q2.emitter.x) / 2, 0)))
    d.add(elm.Line().at(q1.base).to(q2.base))
    d.add(elm.Line().at(q1.collector).to(q1.base))
    d.add(elm.Dot().at(q1.collector))
    reference = d.add(elm.Resistor().at(q1.collector).up(2.3))
    d.add(elm.Label().at((reference.center.x - 0.85, reference.center.y)).label("Rref"))
    d.add(elm.Label().at((reference.end.x - 0.8, reference.end.y + 0.15)).label("+VCC"))
    load = d.add(elm.Resistor().at(q2.collector).up(2.3))
    d.add(elm.Label().at((load.center.x + 0.75, load.center.y)).label("RL"))
    d.add(elm.Label().at((load.end.x - 0.75, load.end.y + 0.15)).label("+VLOAD"))
    d.add(elm.Dot().at(q2.collector))
    d.add(elm.Label().at((q2.collector.x + 0.2, q2.collector.y + 0.28)).label("vout"))
    return accessible_svg(
        d,
        "基本 NPN 电流镜的参考与输出回路",
        "Q1集电极与基极短接并经Rref接VCC，Q1和Q2基极相连、发射极共地；Q2集电极作为输出并经负载接VLOAD。",
    )


def nmos_current_mirror() -> str:
    d = schemdraw.Drawing(show=False)
    d.config(unit=1.8, fontsize=10, color=INK, lw=1.9)
    m1 = d.add(elm.NFet().at((4.0, 2.2)).label("M1", loc="left"))
    m2 = d.add(elm.NFet().at((8.0, 2.2)).label("M2", loc="right"))
    d.add(elm.Line().at(m1.source).to((m1.source.x, 0)))
    d.add(elm.Line().at(m2.source).to((m2.source.x, 0)))
    d.add(elm.Line().at((m1.source.x, 0)).to((m2.source.x, 0)))
    d.add(elm.Ground().at(((m1.source.x + m2.source.x) / 2, 0)))
    d.add(elm.Line().at(m1.gate).to(m2.gate))
    d.add(elm.Line().at(m1.drain).to(m1.gate))
    d.add(elm.Dot().at(m1.drain))
    reference = d.add(elm.Resistor().at(m1.drain).up(2.3))
    d.add(elm.Label().at((reference.center.x - 0.85, reference.center.y)).label("Rref"))
    d.add(elm.Label().at((reference.end.x - 0.8, reference.end.y + 0.15)).label("+VDD"))
    load = d.add(elm.Resistor().at(m2.drain).up(2.3))
    d.add(elm.Label().at((load.center.x + 0.75, load.center.y)).label("RL"))
    d.add(elm.Label().at((load.end.x - 0.75, load.end.y + 0.15)).label("+VLOAD"))
    d.add(elm.Dot().at(m2.drain))
    d.add(elm.Label().at((m2.drain.x + 0.2, m2.drain.y + 0.28)).label("vout"))
    return accessible_svg(
        d,
        "基本 NMOS 电流镜的完整连接",
        "M1漏极与栅极短接并经Rref接VDD，两管栅极相连、源极和体端共地；M2漏极作为输出并经负载接VLOAD。",
    )


def current_mirrors_pair() -> str:
    """Standard-symbol comparison of BJT and NMOS sink current mirrors."""
    d = schemdraw.Drawing(show=False)
    d.config(unit=1.35, fontsize=8.3, color=INK, lw=1.8)

    # (a) NPN current sink: Q1 is diode connected, bases and emitters are
    # common, and Q2's collector is the output port.
    q1 = d.add(elm.BjtNpn().at((3.0, 2.0)).right())
    q2 = d.add(elm.BjtNpn().at((6.2, 2.0)).right())
    bjt_ground_y = 0.0
    d.add(elm.Line().at(q1.emitter).to((q1.emitter.x, bjt_ground_y)))
    d.add(elm.Line().at(q2.emitter).to((q2.emitter.x, bjt_ground_y)))
    d.add(
        elm.Line()
        .at((q1.emitter.x, bjt_ground_y))
        .to((q2.emitter.x, bjt_ground_y))
    )
    d.add(
        elm.Ground().at(
            ((q1.emitter.x + q2.emitter.x) / 2, bjt_ground_y)
        )
    )
    d.add(elm.Line().at(q1.base).to(q2.base))
    d.add(elm.Line().at(q1.collector).to(q1.base))
    d.add(elm.Dot().at(q1.collector))
    bjt_ref = d.add(elm.Resistor().at(q1.collector).up(2.2))
    d.add(elm.Label().at((bjt_ref.center.x - 0.7, bjt_ref.center.y)).label("Rref"))
    d.add(elm.Label().at((bjt_ref.end.x - 0.5, bjt_ref.end.y + 0.25)).label("+VCC"))
    bjt_load = d.add(elm.Resistor().at(q2.collector).up(2.2))
    d.add(elm.Label().at((bjt_load.center.x + 0.6, bjt_load.center.y)).label("RL"))
    d.add(elm.Label().at((bjt_load.end.x - 0.6, bjt_load.end.y + 0.25)).label("+VLOAD"))
    d.add(elm.Dot().at(q2.collector))
    d.add(elm.Label().at((q1.base.x - 0.45, q1.base.y + 0.4)).label("Q1"))
    d.add(elm.Label().at((q2.base.x - 0.15, q2.base.y + 0.4)).label("Q2"))
    d.add(elm.Label().at((q1.collector.x - 0.6, q1.collector.y + 0.35)).label("Iref"))
    d.add(elm.Label().at((q2.collector.x + 0.35, q2.collector.y + 0.35)).label("Iout"))
    d.add(elm.Label().at((2.2, 5.55)).label("(a) NPN 下拉电流镜"))

    # (b) NMOS current sink: M1 is diode connected, gates and sources are
    # common, and both sources return to the same explicit ground.
    xoff = 8.6
    m1 = d.add(elm.NFet().at((xoff + 3.0, 2.0)).right())
    m2 = d.add(elm.NFet().at((xoff + 6.2, 2.0)).right())
    mos_ground_y = 0.0
    d.add(elm.Line().at(m1.source).to((m1.source.x, mos_ground_y)))
    d.add(elm.Line().at(m2.source).to((m2.source.x, mos_ground_y)))
    d.add(
        elm.Line()
        .at((m1.source.x, mos_ground_y))
        .to((m2.source.x, mos_ground_y))
    )
    d.add(
        elm.Ground().at(
            ((m1.source.x + m2.source.x) / 2, mos_ground_y)
        )
    )
    d.add(elm.Line().at(m1.gate).to(m2.gate))
    d.add(elm.Line().at(m1.drain).to(m1.gate))
    d.add(elm.Dot().at(m1.drain))
    mos_ref = d.add(elm.Resistor().at(m1.drain).up(2.2))
    d.add(elm.Label().at((mos_ref.center.x - 0.7, mos_ref.center.y)).label("Rref"))
    d.add(elm.Label().at((mos_ref.end.x - 0.5, mos_ref.end.y + 0.25)).label("+VDD"))
    mos_load = d.add(elm.Resistor().at(m2.drain).up(2.2))
    d.add(elm.Label().at((mos_load.center.x + 0.6, mos_load.center.y)).label("RL"))
    d.add(elm.Label().at((mos_load.end.x - 0.6, mos_load.end.y + 0.25)).label("+VLOAD"))
    d.add(elm.Dot().at(m2.drain))
    d.add(elm.Label().at((m1.gate.x - 0.35, m1.gate.y + 0.45)).label("M1"))
    d.add(elm.Label().at((m2.gate.x - 0.05, m2.gate.y + 0.45)).label("M2"))
    d.add(elm.Label().at((m1.drain.x - 0.6, m1.drain.y + 0.35)).label("Iref"))
    d.add(elm.Label().at((m2.drain.x + 0.35, m2.drain.y + 0.35)).label("Iout"))
    d.add(elm.Label().at((xoff + 2.2, 5.55)).label("(b) NMOS 下拉电流镜"))

    return accessible_svg(
        d,
        "BJT 与 NMOS 下拉电流镜",
        "左图使用标准NPN符号，Q1集电极与基极短接，两管基极相连且发射极共地；右图使用标准NMOS符号，M1漏极与栅极短接，两管栅极相连且源极共地。两个输出支路均经负载接正电源。",
    )


def bjt_regions_overview() -> str:
    """NPN reference directions plus the two-junction region table."""
    d = schemdraw.Drawing(show=False)
    d.config(unit=1.25, fontsize=8.5, color=INK, lw=1.8)

    add_box(d, (0.0, 0.0), (4.8, 5.6))
    d.add(elm.Label().at((1.0, 5.25)).label("NPN 端子与传统电流"))
    q = d.add(elm.BjtNpn().at((2.3, 2.7)).right())
    d.add(elm.Label().at((q.base.x - 0.35, q.base.y + 0.35)).label("B"))
    d.add(elm.Label().at((q.collector.x + 0.3, q.collector.y + 0.25)).label("C"))
    d.add(elm.Label().at((q.emitter.x + 0.3, q.emitter.y - 0.25)).label("E"))
    d.add(elm.Arrow().at((0.35, q.base.y)).to(q.base))
    d.add(elm.Label().at((0.65, q.base.y + 0.35)).label("IB"))
    d.add(
        elm.Arrow()
        .at((q.collector.x, 4.65))
        .to(q.collector)
    )
    d.add(elm.Label().at((q.collector.x + 0.55, 4.2)).label("IC"))
    d.add(
        elm.Arrow()
        .at(q.emitter)
        .to((q.emitter.x, 0.65))
    )
    d.add(elm.Label().at((q.emitter.x + 0.55, 1.0)).label("IE"))
    d.add(elm.Label().at((2.35, 0.35)).label("电子主运动：E → C"))

    left, mid, right = 6.0, 9.0, 12.0
    bottom, split, top = 0.0, 2.8, 5.6
    d.add(elm.Label().at((7.5, 5.25)).label("BC 反偏"))
    d.add(elm.Label().at((10.5, 5.25)).label("BC 正偏"))
    d.add(elm.Label().at((5.35, 4.05)).label("BE 反偏"))
    d.add(elm.Label().at((5.35, 1.45)).label("BE 正偏"))
    for x1, x2, y1, y2 in (
        (left, mid, split, top - 0.65),
        (mid, right, split, top - 0.65),
        (left, mid, bottom, split),
        (mid, right, bottom, split),
    ):
        add_box(d, (x1, y1), (x2, y2))
    d.add(elm.Label().at((7.5, 4.05)).label("截止"))
    d.add(elm.Label().at((7.5, 3.45)).label("两结反偏；IC≈0"))
    d.add(elm.Label().at((10.5, 4.05)).label("反向有源"))
    d.add(elm.Label().at((10.5, 3.45)).label("角色近似互换"))
    d.add(elm.Label().at((7.5, 1.85)).label("前向有源"))
    d.add(elm.Label().at((7.5, 1.2)).label("BE 正偏；BC 反偏"))
    d.add(elm.Label().at((7.5, 0.55)).label("IC≈βIB"))
    d.add(elm.Label().at((10.5, 1.85)).label("饱和"))
    d.add(elm.Label().at((10.5, 1.2)).label("BE、BC 均正偏"))
    d.add(elm.Label().at((10.5, 0.55)).label("VCE 很小"))
    return accessible_svg(
        d,
        "NPN 端子电流、结偏置与工作区",
        "左侧使用带发射极箭头的标准NPN符号标出基极、集电极和发射极传统电流方向；右侧按BE结与BC结的正反偏组合列出截止、前向有源、反向有源和饱和四个工作区。",
    )


def bjt_amplifier_topologies() -> str:
    """Three common BJT amplifier configurations using standard symbols."""
    d = schemdraw.Drawing(show=False)
    d.config(unit=1.2, fontsize=7.8, color=INK, lw=1.7)
    panel_width = 4.5
    for index, kind in enumerate(("CE", "CC", "CB")):
        x0 = index * 4.9
        add_box(d, (x0, 0.0), (x0 + panel_width, 5.8))
        q = d.add(elm.BjtNpn().at((x0 + 2.15, 2.7)).right())
        d.add(elm.Label().at((x0 + 1.05, 5.4)).label(
            {"CE": "(a) 共射极 CE", "CC": "(b) 射极跟随器 CC", "CB": "(c) 共基极 CB"}[kind]
        ))

        if kind in {"CE", "CC"}:
            d.add(elm.Dot().at((x0 + 0.4, q.base.y)))
            d.add(elm.Label().at((x0 + 0.25, q.base.y + 0.35)).label("vi"))
            d.add(elm.Line().at((x0 + 0.4, q.base.y)).to(q.base))
        if kind == "CE":
            d.add(elm.Line().at(q.collector).to((x0 + 4.0, q.collector.y)))
            d.add(elm.Dot().at((x0 + 4.0, q.collector.y)))
            d.add(elm.Label().at((x0 + 3.65, q.collector.y + 0.4)).label("vo"))
            d.add(elm.Line().at(q.emitter).down(0.85))
            d.add(elm.Ground())
            d.add(elm.Label().at((x0 + 1.45, 1.15)).label("Av<0；电压增益大"))
            d.add(elm.Label().at((x0 + 1.2, 0.35)).label("公共端：E"))
        elif kind == "CC":
            d.add(elm.Line().at(q.collector).up(0.75))
            d.add(elm.Label().at((q.collector.x - 0.55, q.collector.y + 1.05)).label("C: 交流地"))
            d.add(elm.Line().at(q.emitter).to((x0 + 4.0, q.emitter.y)))
            d.add(elm.Dot().at((x0 + 4.0, q.emitter.y)))
            d.add(elm.Label().at((x0 + 3.65, q.emitter.y + 0.4)).label("vo"))
            d.add(elm.Label().at((x0 + 2.25, 0.65)).label("Av≈+1；低 Zout"))
            d.add(elm.Label().at((x0 + 2.25, 0.25)).label("公共端：C"))
        else:
            d.add(elm.Line().at(q.base).to((x0 + 0.75, q.base.y)))
            d.add(elm.Line().at((x0 + 0.75, q.base.y)).down(0.8))
            d.add(elm.Ground())
            d.add(elm.Label().at((x0 + 1.0, q.base.y + 0.35)).label("B: 交流地"))
            d.add(elm.Dot().at((x0 + 4.0, q.emitter.y)))
            d.add(elm.Line().at((x0 + 4.0, q.emitter.y)).to(q.emitter))
            d.add(elm.Label().at((x0 + 3.65, q.emitter.y - 0.4)).label("vi"))
            d.add(elm.Line().at(q.collector).to((x0 + 4.0, q.collector.y)))
            d.add(elm.Dot().at((x0 + 4.0, q.collector.y)))
            d.add(elm.Label().at((x0 + 3.65, q.collector.y + 0.4)).label("vo"))
            d.add(elm.Label().at((x0 + 2.25, 0.65)).label("Av>0；低 Zin"))
            d.add(elm.Label().at((x0 + 2.25, 0.25)).label("公共端：B"))
    return accessible_svg(
        d,
        "三种基本 BJT 放大组态",
        "三幅均使用标准NPN符号。共射极从基极输入、集电极输出且发射极为交流公共端；射极跟随器从基极输入、发射极输出且集电极为交流公共端；共基极从发射极输入、集电极输出且基极交流接地。",
    )


def differential_power_pair() -> str:
    """Standard-symbol overview of a differential input and AB output stage."""
    d = schemdraw.Drawing(show=False)
    d.config(unit=1.15, fontsize=7.5, color=INK, lw=1.7)

    add_box(d, (0.0, -0.8), (7.2, 6.4))
    d.add(elm.Label().at((1.45, 6.05)).label("(a) NPN 差分输入级"))
    q1 = d.add(elm.BjtNpn().at((2.5, 2.75)).right())
    q2 = d.add(elm.BjtNpn().at((5.3, 2.75)).right())
    d.add(elm.Label().at((q1.base.x - 0.2, q1.base.y + 0.4)).label("Q1"))
    d.add(elm.Label().at((q2.base.x - 0.2, q2.base.y + 0.4)).label("Q2"))
    d.add(elm.Dot().at((0.45, q1.base.y)))
    d.add(elm.Label().at((0.25, q1.base.y + 0.35)).label("v1"))
    d.add(elm.Line().at((0.45, q1.base.y)).to(q1.base))
    d.add(elm.Dot().at((6.75, q2.base.y)))
    d.add(elm.Label().at((6.5, q2.base.y + 0.35)).label("v2"))
    d.add(elm.Line().at((6.75, q2.base.y)).to(q2.base))
    common = ((q1.emitter.x + q2.emitter.x) / 2, 1.0)
    d.add(elm.Line().at(q1.emitter).to(common))
    d.add(elm.Line().at(q2.emitter).to(common))
    d.add(elm.Dot().at(common))
    tail = d.add(elm.SourceI().at(common).down(0.9))
    d.add(elm.Label().at((tail.center.x + 0.5, tail.center.y)).label("IT"))
    d.add(elm.Label().at((tail.end.x + 0.15, tail.end.y - 0.25)).label("−VEE"))
    top = 5.25
    d.add(elm.Line().at((q1.collector.x, top)).to((q2.collector.x, top)))
    d.add(elm.Label().at((3.45, top + 0.35)).label("+VCC"))
    for transistor, output_label in ((q1, "vo1"), (q2, "vo2")):
        d.add(elm.Resistor().at((transistor.collector.x, top)).to(transistor.collector))
        d.add(elm.Dot().at(transistor.collector))
        d.add(elm.Label().at((transistor.collector.x + 0.25, transistor.collector.y + 0.35)).label(output_label))

    xoff = 8.0
    add_box(d, (xoff, -0.8), (15.2, 6.4))
    d.add(elm.Label().at((xoff + 1.1, 6.05)).label("(b) 互补 AB 推挽输出级"))
    qn = d.add(elm.BjtNpn().at((xoff + 3.5, 4.4)).right())
    qp = d.add(elm.BjtPnp().at((xoff + 3.5, 1.9)).right())
    d.add(elm.Label().at((qn.base.x - 0.5, qn.base.y + 0.4)).label("QN"))
    d.add(elm.Label().at((qp.base.x - 0.5, qp.base.y - 0.4)).label("QP"))
    d.add(elm.Line().at(qn.collector).up(0.8))
    d.add(elm.Label().at((qn.collector.x - 0.35, 6.0)).label("+VCC"))
    d.add(elm.Line().at(qp.collector).down(0.8))
    d.add(elm.Label().at((qp.collector.x - 0.35, qp.collector.y - 1.05)).label("−VEE"))
    out = (xoff + 6.1, 3.15)
    d.add(elm.Line().at(qn.emitter).to(out))
    d.add(elm.Line().at(qp.emitter).to(out))
    d.add(elm.Dot().at(out))
    d.add(elm.Label().at((out[0] + 0.25, out[1] + 0.35)).label("vo"))
    load = d.add(elm.Resistor().at(out).down(1.6))
    d.add(elm.Label().at((load.center.x + 0.6, load.center.y)).label("RL"))
    d.add(elm.Ground())
    upper_diode = d.add(elm.Diode().at((xoff + 1.2, 4.35)).down(1.1))
    lower_diode = d.add(elm.Diode().down(1.1))
    d.add(elm.Line().at(upper_diode.start).to(qn.base))
    d.add(elm.Line().at(lower_diode.end).to(qp.base))
    d.add(elm.Dot().at((xoff + 0.45, 3.25)))
    d.add(elm.Label().at((xoff + 0.25, 3.6)).label("vin"))
    d.add(elm.Line().at((xoff + 0.45, 3.25)).to((xoff + 1.2, 3.25)))
    return accessible_svg(
        d,
        "差分输入级与互补推挽输出级",
        "左侧用标准NPN符号画出带双电阻负载和尾电流源的差分对；右侧用标准NPN、PNP与二极管符号画出互补AB推挽级，两个发射极汇合为输出并驱动接地负载。",
    )


def class_a_stage() -> str:
    d = schemdraw.Drawing(show=False)
    d.config(unit=1.8, fontsize=10, color=INK, lw=1.9)
    q = d.add(elm.BjtNpn().at((5.0, 2.4)).label("Q1", loc="right"))
    top, bottom, xdiv = 5.5, 0.0, 2.8
    collector_resistor = d.add(elm.Resistor().at((q.collector.x, top)).to(q.collector))
    d.add(elm.Label().at((collector_resistor.center.x + 0.7, collector_resistor.center.y)).label("RC"))
    d.add(elm.Line().at((xdiv, top)).to((q.collector.x, top)))
    d.add(elm.Dot().at((q.collector.x, top)))
    d.add(elm.Label().at(((xdiv + q.collector.x) / 2 - 0.25, top + 0.3)).label("+VCC"))
    d.add(elm.Dot().at(q.collector))
    d.add(elm.Label().at((q.collector.x + 0.2, q.collector.y + 0.3)).label("vo"))
    emitter_resistor = d.add(
        elm.Resistor().at(q.emitter).to((q.emitter.x, bottom))
    )
    d.add(
        elm.Label()
        .at((emitter_resistor.center.x + 0.9, emitter_resistor.center.y))
        .label("RE")
    )
    d.add(elm.Ground().at((q.emitter.x, bottom)))
    upper_divider = d.add(
        elm.Resistor().at((xdiv, top)).to((xdiv, q.base.y))
    )
    lower_divider = d.add(
        elm.Resistor().at((xdiv, q.base.y)).to((xdiv, bottom))
    )
    d.add(
        elm.Label()
        .at((upper_divider.center.x - 0.8, upper_divider.center.y))
        .label("R1")
    )
    d.add(
        elm.Label()
        .at((lower_divider.center.x - 0.8, lower_divider.center.y))
        .label("R2")
    )
    d.add(elm.Ground().at((xdiv, bottom)))
    d.add(elm.Line().at((xdiv, q.base.y)).to(q.base))
    src = d.add(elm.SourceSin().at((0.3, bottom)).up(q.base.y).label("vi", loc="left"))
    d.add(elm.Ground().at(src.start))
    d.add(elm.Capacitor().at(src.end).to((xdiv, q.base.y)).label("Cin"))
    return accessible_svg(
        d,
        "电阻负载串馈的 A 类概念级",
        "NPN共射极A类级由R1和R2分压偏置，输入经Cin耦合到基极，集电极经RC接VCC，发射极经RE接地，输出取集电极。晶体管在完整信号周期保持导通。",
    )


def complementary_output(*, ab: bool) -> str:
    d = schemdraw.Drawing(show=False)
    d.config(unit=1.7, fontsize=9, color=INK, lw=1.8)
    qn = d.add(elm.BjtNpn().at((6.0, 4.2)).right())
    qp = d.add(elm.BjtPnp().at((6.0, 1.8)).right())
    d.add(elm.Label().at((qn.base.x - 0.65, qn.base.y + 0.45)).label("QN"))
    d.add(elm.Label().at((qp.base.x - 0.65, qp.base.y - 0.45)).label("QP"))
    d.add(elm.Line().at(qn.collector).up(1.4))
    d.add(elm.Label().label("+VCC", loc="top"))
    d.add(elm.Line().at(qp.collector).down(1.4))
    d.add(elm.Label().label("−VEE", loc="bottom"))
    out = (8.0, 3.0)
    if ab:
        upper_re = d.add(elm.Resistor().at(qn.emitter).to((7.2, 3.6)))
        lower_re = d.add(elm.Resistor().at(qp.emitter).to((7.2, 2.4)))
        d.add(
            elm.Label()
            .at((upper_re.center.x + 0.45, upper_re.center.y + 0.75))
            .label("RE")
        )
        d.add(
            elm.Label()
            .at((lower_re.center.x - 0.45, lower_re.center.y - 0.75))
            .label("RE")
        )
        d.add(elm.Line().at((7.2, 3.6)).to(out))
        d.add(elm.Line().at((7.2, 2.4)).to(out))
        upper_diode = d.add(elm.Diode().at((2.0, 4.1)).down(1.1))
        lower_diode = d.add(elm.Diode().down(1.1))
        d.add(elm.Label().at((upper_diode.center.x - 0.55, upper_diode.center.y)).label("D1"))
        d.add(elm.Label().at((lower_diode.center.x - 0.55, lower_diode.center.y)).label("D2"))
        d.add(elm.Line().at((2.0, 4.1)).to(qn.base))
        d.add(elm.Line().at((2.0, 1.9)).to(qp.base))
        d.add(elm.Dot().at((0.6, 3.0)))
        d.add(elm.Label().at((0.4, 3.3)).label("vin"))
        d.add(elm.Line().at((0.6, 3.0)).to((2.0, 3.0)))
        title = "带预偏置和发射极电阻的互补 AB 类核心"
        desc = "两个串联二极管在上下功率管基极间建立约二VBE预偏置，NPN和PNP发射极分别经小电阻汇合为输出，负载接地并由双电源供能。"
    else:
        d.add(elm.Line().at(qn.emitter).to(out))
        d.add(elm.Line().at(qp.emitter).to(out))
        d.add(elm.Dot().at((0.6, 3.0)))
        d.add(elm.Label().at((0.4, 3.3)).label("vin"))
        d.add(elm.Line().at((0.6, 3.0)).to(qn.base))
        d.add(elm.Line().at((0.6, 3.0)).to(qp.base))
        title = "互补 B 类推挽射极跟随器"
        desc = "NPN和PNP基极由同一输入驱动，两个发射极汇合成输出；NPN集电极接正电源，PNP集电极接负电源，负载从输出接地。"
    d.add(elm.Dot().at(out))
    d.add(elm.Label().at((out[0] + 0.2, out[1] + 0.3)).label("vo"))
    load = d.add(elm.Resistor().at(out).down(1.7))
    d.add(elm.Label().at((load.center.x + 0.65, load.center.y)).label("RL"))
    d.add(elm.Ground())
    return accessible_svg(d, title, desc)


def rectifier_topologies() -> str:
    d = schemdraw.Drawing(show=False)
    d.config(unit=1.2, fontsize=7.5, color=INK, lw=1.7)
    # (a) Half-wave: a -> D -> RL -> b.
    a, b, output = (0.3, 3.2), (0.3, 0.8), (2.5, 3.2)
    d.add(elm.Dot().at(a))
    d.add(elm.Label().at((a[0] - 0.15, a[1] + 0.28)).label("a~"))
    d.add(elm.Diode().at(a).to(output).label("D"))
    d.add(elm.Dot().at(output))
    d.add(elm.Resistor().at(output).to((output[0], b[1])).label("RL", loc="right"))
    d.add(elm.Line().to(b))
    d.add(elm.Dot().at(b))
    d.add(elm.Label().at((b[0] - 0.15, b[1] - 0.22)).label("b~ / 0 V"))
    d.add(elm.Label().at((0.45, 5.4)).label("(a) 半波"))

    # (b) Center-tap full wave: a/b alternately feed p, RL returns to CT.
    a, b, ct, p = (4.0, 4.0), (4.0, 2.2), (4.0, 0.6), (6.8, 3.1)
    for source, label in ((a, "D1"), (b, "D2")):
        d.add(elm.Dot().at(source))
        d.add(elm.Diode().at(source).right(1.35).label(label))
        d.add(elm.Line().to(p))
    d.add(elm.Dot().at(p))
    d.add(elm.Label().at((p[0] - 0.65, p[1] + 0.38)).label("+vo"))
    d.add(elm.Resistor().at(p).to((p[0], ct[1])).label("RL", loc="right"))
    d.add(elm.Line().to(ct))
    d.add(elm.Dot().at(ct))
    d.add(elm.Label().at((ct[0] - 0.2, ct[1] - 0.22)).label("CT / 0 V"))
    d.add(elm.Label().at((4.45, 5.4)).label("(b) 中心抽头全波"))

    # (c) Four-diode bridge with explicit AC and DC ports.
    left, right, top, bottom = (9.0, 3.0), (13.0, 3.0), (11.0, 5.0), (11.0, 1.0)
    d.add(elm.Diode().at(left).to(top).label("D1"))
    d.add(elm.Diode().at(right).to(top).label("D2"))
    d.add(elm.Diode().at(bottom).to(left).label("D3"))
    d.add(elm.Diode().at(bottom).to(right).label("D4"))
    d.add(elm.Dot().at(left))
    d.add(elm.Label().at((left[0] - 0.25, left[1] + 0.25)).label("a~"))
    d.add(elm.Dot().at(right))
    d.add(elm.Label().at((right[0] + 0.1, right[1] + 0.25)).label("~b"))
    d.add(elm.Dot().at(top))
    d.add(elm.Label().at((top[0] + 0.15, top[1] + 0.25)).label("p"))
    d.add(elm.Dot().at(bottom))
    d.add(elm.Label().at((bottom[0] + 0.15, bottom[1] - 0.2)).label("n"))
    d.add(elm.Line().at(top).to((14.2, top[1])))
    d.add(elm.Resistor().at((14.2, top[1])).to((14.2, bottom[1])).label("RL", loc="right"))
    d.add(elm.Line().to(bottom))
    d.add(elm.Label().at((9.65, 5.75)).label("(c) 四二极管桥式"))
    return accessible_svg(
        d,
        "三种整流拓扑的次级侧连接",
        "图中依次给出单二极管半波、中心抽头双二极管全波和四二极管桥式整流。前两种每次导通一只二极管，桥式每次导通两只并使用完整次级。",
    )


def bridge_rectifier_filter() -> str:
    d = schemdraw.Drawing(show=False)
    d.config(unit=1.5, fontsize=9, color=INK, lw=1.8)
    left, right, top, bottom = (1.0, 3.0), (7.0, 3.0), (4.0, 5.2), (4.0, 0.8)
    d.add(elm.Diode().at(left).to(top).label("D1"))
    d.add(elm.Diode().at(right).to(top).label("D2"))
    d.add(elm.Diode().at(bottom).to(left).label("D3"))
    d.add(elm.Diode().at(bottom).to(right).label("D4"))
    d.add(elm.Dot().at(left))
    d.add(elm.Label().at((left[0] - 0.4, left[1] + 0.3)).label("a~"))
    d.add(elm.Dot().at(right))
    d.add(elm.Label().at((right[0] + 0.1, right[1] + 0.3)).label("~b"))
    d.add(elm.Dot().at(top))
    d.add(elm.Label().at((top[0] + 0.2, top[1] + 0.3)).label("+raw"))
    d.add(elm.Dot().at(bottom))
    d.add(elm.Label().at((bottom[0] + 0.2, bottom[1] - 0.2)).label("0 V"))
    for x, element, label in ((8.5, elm.Capacitor(), "C"), (10.2, elm.Resistor(), "RL")):
        d.add(elm.Line().at(top).to((x, top[1])))
        d.add(element.at((x, top[1])).to((x, bottom[1])).label(label, loc="right"))
        d.add(elm.Line().to(bottom))
    return accessible_svg(
        d,
        "桥式整流加并联电容滤波的完整网络",
        "四只二极管构成桥式整流，交流端为a和b，正输出p接电容与负载上端，负输出n作为零伏回流；每半周有两只二极管串联导通。",
    )


def zener_regulator() -> str:
    d = schemdraw.Drawing(show=False)
    d.config(unit=1.9, fontsize=10, color=INK, lw=1.9)
    d.add(elm.Dot().at((0.5, 3.0)))
    d.add(elm.Label().at((1.25, 3.72)).label("安全低压 Vin"))
    series = d.add(elm.Resistor().at((0.5, 3.0)).right(2.4))
    d.add(elm.Label().at((series.center.x, series.center.y - 0.42)).label("Rs"))
    node = d.add(elm.Dot())
    d.add(elm.Label().at((node.center.x + 0.7, node.center.y + 0.6)).label("vo ≈ VZ"))
    for dx, element in ((0.0, elm.Resistor()), (2.0, elm.Zener().reverse())):
        d.add(elm.Line().at(node.center).to((node.center.x + dx, node.center.y)))
        d.add(element.at((node.center.x + dx, node.center.y)).down(2.3))
        d.add(elm.Ground())
    d.add(elm.Label().at((node.center.x - 0.65, node.center.y - 1.15)).label("RL"))
    d.add(elm.Label().at((node.center.x + 2.7, node.center.y - 1.15)).label("ZD"))
    return accessible_svg(
        d,
        "齐纳并联稳压器的完整电流路径",
        "安全低压输入经串联电阻到输出节点，负载和反向齐纳二极管并联接地；齐纳阴极接输出、阳极接地，串联电流分成负载电流和齐纳电流。",
    )


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    figures = {
        "figure-4-05.svg": simple_ce_bias(),
        "figure-4-09.svg": divider_biased_ce(),
        "figure-4-12.svg": emitter_follower(),
        "figure-4-14.svg": common_base_amplifier(),
        "figure-4-17.svg": mosfet_three_topologies(),
        "figure-5-08.svg": opamp_feedback_circuit("inverting"),
        "figure-5-10.svg": inverting_output_resistance_test(),
        "figure-5-11.svg": opamp_feedback_circuit("noninverting"),
        "figure-5-13.svg": opamp_feedback_circuit("follower"),
        "figure-5-14.svg": inverting_summer(),
        "figure-5-16.svg": four_resistor_difference_amplifier(),
        "figure-5-18.svg": opamp_feedback_circuit("integrator"),
        "figure-5-20.svg": practical_integrator(),
        "figure-5-21.svg": opamp_feedback_circuit("differentiator"),
        "figure-3-06.svg": bjt_dc_case(
            title="固定基极偏置完整电路",
            vcc="+10.0 V",
            rc="RC  2.00 kΩ",
            vbase="+10.0 V",
            rb="RB  470 kΩ",
        ),
        "figure-3-08.svg": bjt_divider_bias(),
        "figure-3-15.svg": nmos_fixed_bias(divider=False),
        "figure-3-16.svg": nmos_fixed_bias(divider=True),
        "figure-3-19.svg": bjt_dc_case(title="BJT 状态案例 B-1", vcc="+5 V", rc="RC  1 kΩ", vbase="0 V", rb="RB  100 kΩ"),
        "figure-3-20.svg": bjt_dc_case(title="BJT 状态案例 B-2", vcc="+5 V", rc="RC  1 kΩ", vbase="+1.0 V", rb="RB  100 kΩ"),
        "figure-3-21.svg": bjt_dc_case(title="BJT 状态案例 B-3", vcc="+5 V", rc="RC  1 kΩ", vbase="+3.0 V", rb="RB  10 kΩ"),
        "figure-3-22.svg": bjt_dc_case(title="BJT 状态案例 B-4", vcc="+5 V", rc="RC  1 kΩ", vbase="+1.2 V", rb="RB  100 kΩ", emitter="+1.0 V"),
        "figure-3-23.svg": bjt_dc_case(title="BJT 状态案例 B-5", vcc="+6 V", rc="RC  2 kΩ", vbase="+2.0 V", rb="RB  100 kΩ", emitter="+1.0 V"),
        "figure-3-24.svg": bjt_dc_case(title="BJT 状态案例 B-6", vcc="+0.5 V", rc="RC  1 kΩ", vbase="+1.7 V", rb="RB  100 kΩ"),
        "figure-3-25.svg": nmos_dc_case(title="NMOS 状态案例 M-1", vdd="+5 V", rd="RD  1 kΩ", vgate="+0.5 V"),
        "figure-3-26.svg": nmos_dc_case(title="NMOS 状态案例 M-2", vdd="+5 V", rd="RD  1 kΩ", vgate="+2.0 V"),
        "figure-3-27.svg": nmos_dc_case(title="NMOS 状态案例 M-3", vdd="+5 V", rd="RD  1 kΩ", vgate="+4.0 V"),
        "figure-3-28.svg": nmos_dc_case(title="NMOS 状态案例 M-4", vdd="+5 V", rd="RD  1 kΩ", vgate="+1.8 V", source="+1.0 V"),
        "figure-3-29.svg": nmos_dc_case(title="NMOS 状态案例 M-5", vdd="+6 V", rd="RD  2 kΩ", vgate="+3.0 V", source="+1.0 V"),
        "figure-3-30.svg": nmos_dc_case(title="NMOS 状态案例 M-6", vdd="+2 V", rd="RD  1 kΩ", vgate="+3.0 V"),
        "figure-5-02.svg": powered_opamp_symbol(),
        "figure-5-23.svg": practical_differentiator(),
        "figure-5-24.svg": comparator_variants(),
        "figure-5-26.svg": schmitt_trigger(),
        "figure-6-13.svg": rc_filter(highpass=False),
        "figure-6-14.svg": rc_filter(highpass=True),
        "figure-4-08.svg": dc_ac_pair(),
        "figure-4-10.svg": bjt_small_signal("ce_bypassed"),
        "figure-4-11.svg": bjt_small_signal("ce_degenerated"),
        "figure-4-13.svg": bjt_small_signal("cc"),
        "figure-4-15.svg": bjt_small_signal("cb"),
        "figure-4-18.svg": mos_small_signal_triptych(),
        "figure-4-20.svg": divider_biased_ce().replace(
            "分压偏置、耦合电容和发射极旁路齐全的共射极放大器",
            "耦合、旁路、源内阻与负载齐全的放大器接口",
        ),
        "figure-4-22.svg": input_coupling_highpass(),
        "figure-4-23.svg": dc_ac_pair().replace(
            "同一放大器的直流图与中频小信号图",
            "用于故障定位的完整 DC 与 AC 测量基准",
        ),
        "figure-7-04.svg": differential_pair(active_load=False),
        "figure-7-09.svg": bjt_current_mirror(),
        "figure-7-10.svg": nmos_current_mirror(),
        "current-mirrors.svg": current_mirrors_pair(),
        "bjt-regions.svg": bjt_regions_overview(),
        "amplifier-topologies.svg": bjt_amplifier_topologies(),
        "differential-power.svg": differential_power_pair(),
        "figure-7-12.svg": differential_pair(active_load=True),
        "figure-7-14.svg": class_a_stage(),
        "figure-7-15.svg": complementary_output(ab=False),
        "figure-7-17.svg": complementary_output(ab=True),
        "figure-7-21.svg": rectifier_topologies(),
        "figure-7-22.svg": bridge_rectifier_filter(),
        "figure-7-25.svg": zener_regulator(),
    }
    for filename, content in figures.items():
        (OUTPUT / filename).write_text(content, encoding="utf-8")
    print(f"generated {len(figures)} circuit figures")


if __name__ == "__main__":
    main()
