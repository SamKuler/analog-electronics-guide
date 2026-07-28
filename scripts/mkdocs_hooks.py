"""MkDocs build hooks for browser-stable course rendering."""

from __future__ import annotations

import html as html_module
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit


TEACHING_FIGURE_RE = re.compile(
    r'<img\b'
    r'(?=[^>]*\bclass="[^"]*\bae-figure\b[^"]*")'
    r'(?=[^>]*\bsrc="(?P<src>[^"]+\.svg)")'
    r"[^>]*/?>"
)
SVG_OPEN_RE = re.compile(r"<svg\b(?P<attributes>[^>]*)>", re.IGNORECASE)
CLASS_RE = re.compile(r'\bclass="(?P<classes>[^"]*)"', re.IGNORECASE)
ID_RE = re.compile(r'\bid="(?P<id>[^"]+)"')


def _prefix_svg_ids(svg: str, prefix: str) -> str:
    """Keep marker and gradient IDs unique after several SVGs are inlined."""

    identifiers = ID_RE.findall(svg)
    for identifier in identifiers:
        replacement = f"{prefix}{identifier}"
        svg = svg.replace(f'id="{identifier}"', f'id="{replacement}"')
        svg = svg.replace(f"url(#{identifier})", f"url(#{replacement})")
        svg = svg.replace(f'href="#{identifier}"', f'href="#{replacement}"')
        svg = svg.replace(f"xlink:href=\"#{identifier}\"", f'xlink:href="#{replacement}"')
    return svg


def _add_figure_class(svg: str) -> str:
    def replace(match: re.Match[str]) -> str:
        attributes = match.group("attributes")
        class_match = CLASS_RE.search(attributes)
        if class_match:
            classes = class_match.group("classes").split()
            if "ae-figure" not in classes:
                classes.append("ae-figure")
            attributes = CLASS_RE.sub(
                f'class="{" ".join(classes)}"',
                attributes,
                count=1,
            )
        else:
            attributes = f' class="ae-figure"{attributes}'
        return f"<svg{attributes}>"

    return SVG_OPEN_RE.sub(replace, svg, count=1)


def on_page_content(html: str, page, config, files) -> str:
    """Inline teaching SVGs so the selected site palette controls their colors."""

    figure_dir = (Path(config.docs_dir) / "assets" / "figures").resolve()

    def replace(match: re.Match[str]) -> str:
        source = html_module.unescape(match.group("src"))
        source_path = unquote(urlsplit(source).path)
        filename = Path(source_path).name
        figure_path = (figure_dir / filename).resolve()

        if figure_path.parent != figure_dir or not figure_path.is_file():
            return match.group(0)

        svg = figure_path.read_text(encoding="utf-8")
        prefix = f"ae-{figure_path.stem}-"
        return _add_figure_class(_prefix_svg_ids(svg, prefix))

    return TEACHING_FIGURE_RE.sub(replace, html)
