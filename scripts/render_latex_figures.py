"""Render the audited XeLaTeX figure corpus to theme-aware SVG files."""

from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import tempfile
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"
SOURCES = FIGURES / "latex"
MANIFEST = FIGURES / "manifest.toml"

DOCUMENT = r"""\documentclass[tikz,border=6pt]{standalone}
\usepackage[UTF8,fontset=fandol]{ctex}
\usepackage{amsmath,amssymb}
\usepackage[americanvoltages,americancurrents]{circuitikz}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usetikzlibrary{arrows.meta,calc,decorations.pathreplacing,fit,matrix,patterns,positioning,svg.path}
\ctikzset{resistors/scale=0.86, capacitors/scale=0.86, diodes/scale=0.86}
\definecolor{AEteal}{HTML}{006F78}
\definecolor{AEorange}{HTML}{AD4F16}
\definecolor{AEmuted}{HTML}{59676D}
\tikzset{
  ae arrow/.style={-{Stealth[length=2.2mm]},AEteal,semithick},
  ae orange arrow/.style={-{Stealth[length=2.2mm]},AEorange,semithick},
  ae panel/.style={draw=AEmuted!70,rounded corners=2mm},
  ae block/.style={draw=AEmuted!70,rounded corners=2mm,align=center,minimum height=13mm,inner sep=3mm},
  ae axis/.style={-{Stealth[length=2mm]},semithick},
  ae curve/.style={AEteal,thick},
  ae accent/.style={AEorange,thick}
}
\begin{document}
%s
\end{document}
"""

THEME_STYLE = (
    'svg[data-generator="latex"]{color:#172127;--ae-figure-muted:#46565b;'
    "--ae-figure-panel:#87979a;--ae-figure-bg:#fffaf0;"
    "--ae-figure-teal:#006f78;--ae-figure-orange:#ad4f16}"
    ".bg{fill:var(--ae-figure-bg)}"
    '@media(prefers-color-scheme:dark){svg[data-generator="latex"]{color:#e8eee8;'
    "--ae-figure-muted:#c3cdca;--ae-figure-panel:#607076;"
    "--ae-figure-bg:#121a1d;--ae-figure-teal:#55c4c8;"
    "--ae-figure-orange:#f19962}}"
)


def _require_tool(name: str) -> str:
    executable = shutil.which(name)
    if executable is None:
        raise SystemExit(f"missing required executable: {name}")
    return executable


def _run(command: list[str], *, cwd: Path) -> None:
    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.returncode:
        raise RuntimeError(f"command failed: {' '.join(command)}\n{result.stdout}")


def _theme_svg(svg: str, *, source: str, title: str, description: str) -> str:
    root_match = re.search(r"<svg\b[^>]*>", svg)
    if root_match is None:
        raise ValueError("PDF-to-SVG output has no SVG root")
    viewbox_match = re.search(r'viewBox="([^"]+)"', root_match.group(0))
    if viewbox_match is None:
        raise ValueError("pdftocairo output has no viewBox")
    x, y, width, height = viewbox_match.group(1).split()

    svg = re.sub(r"fill:rgb\(0%,\s*0%,\s*0%\)", "fill:currentColor", svg)
    svg = re.sub(r"stroke:rgb\(0%,\s*0%,\s*0%\)", "stroke:currentColor", svg)
    svg = re.sub(
        r'fill="rgb\(0%,\s*0%,\s*0%\)"', 'fill="currentColor"', svg
    )
    svg = re.sub(
        r'stroke="rgb\(0%,\s*0%,\s*0%\)"', 'stroke="currentColor"', svg
    )
    svg = svg.replace("fill:#000000", "fill:currentColor")
    svg = svg.replace("stroke:#000000", "stroke:currentColor")
    svg = re.sub(
        r"rgb\(34\.899902%,\s*40\.39917%,\s*42\.698669%\)",
        "var(--ae-figure-muted)",
        svg,
    )
    svg = re.sub(
        r"rgb\(54\.432678%,\s*58\.274841%,\s*59\.919739%\)",
        "var(--ae-figure-panel)",
        svg,
    )
    svg = re.sub(
        r"rgb\(50%,\s*50%,\s*50%\)", "var(--ae-figure-panel)", svg
    )
    svg = re.sub(
        r"rgb\(0%,\s*43\.499756%,\s*47\.099304%\)",
        "var(--ae-figure-teal)",
        svg,
    )
    svg = re.sub(
        r"rgb\(67\.799377%,\s*30\.999756%,\s*8\.599854%\)",
        "var(--ae-figure-orange)",
        svg,
    )
    svg = re.sub(
        r"rgb\(100%,\s*100%,\s*100%\)", "var(--ae-figure-bg)", svg
    )

    root = root_match.group(0)[:-1]
    root += (
        ' role="img"'
        f' aria-label="{html.escape(title, quote=True)}"'
        ' data-generator="latex"'
        f' data-source="{html.escape(source, quote=True)}">'
    )
    metadata = (
        f"<desc>{html.escape(description)}</desc>"
        f"<style>{THEME_STYLE}</style>"
        f'<rect class="bg" x="{x}" y="{y}" width="{width}" height="{height}"/>'
    )
    return svg[: root_match.start()] + root + metadata + svg[root_match.end() :]


def render(entry: dict[str, str], *, audit_dir: Path | None = None) -> str:
    xelatex = _require_tool("xelatex")
    pdftocairo = _require_tool("pdftocairo")
    source_path = FIGURES / entry["source"]
    body = source_path.read_text(encoding="utf-8")

    with tempfile.TemporaryDirectory(prefix="latex-figure-") as temp_name:
        temp = Path(temp_name)
        tex_path = temp / "figure.tex"
        tex_path.write_text(DOCUMENT % body, encoding="utf-8")
        _run(
            [
                xelatex,
                "-interaction=nonstopmode",
                "-halt-on-error",
                f"-output-directory={temp}",
                str(tex_path),
            ],
            cwd=SOURCES,
        )
        if audit_dir is not None:
            audit_dir.mkdir(parents=True, exist_ok=True)
            audit_base = audit_dir / Path(entry["output"]).stem
            _run(
                [
                    pdftocairo,
                    "-png",
                    "-singlefile",
                    "-r",
                    "120",
                    str(temp / "figure.pdf"),
                    str(audit_base),
                ],
                cwd=temp,
            )
        svg_path = temp / "figure.svg"
        _run(
            [pdftocairo, "-svg", str(temp / "figure.pdf"), str(svg_path)],
            cwd=temp,
        )
        svg = svg_path.read_text(encoding="utf-8")

    return _theme_svg(
        svg,
        source=entry["source"],
        title=entry["title"],
        description=entry["description"],
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("figures", nargs="*", help="output basenames to render")
    parser.add_argument("--check", action="store_true", help="fail if generated SVGs differ")
    parser.add_argument(
        "--audit-dir",
        type=Path,
        help="also write PNG previews compiled from the same LaTeX source",
    )
    args = parser.parse_args()

    entries = tomllib.loads(MANIFEST.read_text(encoding="utf-8"))["figures"]
    requested = set(args.figures)
    selected = [
        entry
        for entry in entries
        if not requested or Path(entry["output"]).name in requested
    ]
    found = {Path(entry["output"]).name for entry in selected}
    missing = requested - found
    if missing:
        raise SystemExit(f"unknown figure(s): {', '.join(sorted(missing))}")

    stale: list[str] = []
    for entry in selected:
        generated = render(entry, audit_dir=args.audit_dir)
        output = ROOT / entry["output"]
        if args.check:
            if not output.exists() or output.read_text(encoding="utf-8") != generated:
                stale.append(entry["output"])
        else:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(generated, encoding="utf-8")
            print(f"rendered {output.relative_to(ROOT)}")

    if stale:
        raise SystemExit("stale LaTeX figure outputs:\n" + "\n".join(stale))


if __name__ == "__main__":
    main()
