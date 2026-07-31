import re
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


class RenderingContractTests(unittest.TestCase):
    NEW_LABS = (
        "diode-waveforms.html",
        "transistor-amplifier.html",
        "bode-stability.html",
        "rectifier-filter.html",
    )
    TEACHING_FIGURES = (
        "reference-directions.svg",
        "pn-junction.svg",
        "diode-models-loadline.svg",
        "diode-waveforms.svg",
        "bjt-regions.svg",
        "mosfet-regions.svg",
        "small-signal-models.svg",
        "amplifier-topologies.svg",
        "opamp-feedback.svg",
        "bode-stability.svg",
        "differential-power.svg",
        "rectifier-filter.svg",
    )

    def markdown_sources(self):
        return sorted(DOCS.rglob("*.md"))

    def test_material_admonitions_do_not_use_github_alert_syntax(self):
        offenders = []
        pattern = re.compile(r"^> \[![A-Z]+\]", re.MULTILINE)

        for path in self.markdown_sources():
            if pattern.search(path.read_text(encoding="utf-8")):
                offenders.append(path.relative_to(ROOT).as_posix())

        self.assertEqual([], offenders)

    def test_native_details_enable_markdown_for_answers_and_math(self):
        offenders = []
        pattern = re.compile(r"<details[^>]*>")

        for path in self.markdown_sources():
            text = path.read_text(encoding="utf-8")
            for tag in pattern.findall(text):
                if 'markdown="1"' not in tag and "markdown='1'" not in tag:
                    offenders.append(path.relative_to(ROOT).as_posix())
                    break

        self.assertEqual([], offenders)

    def test_navigation_uses_a_dedicated_high_contrast_palette(self):
        css = (DOCS / "assets" / "stylesheets" / "extra.css").read_text(
            encoding="utf-8"
        )

        self.assertGreaterEqual(css.count("--ae-nav-bg:"), 2)
        self.assertGreaterEqual(css.count("--ae-nav-fg:"), 2)
        self.assertIn("background-color: var(--ae-nav-bg);", css)
        self.assertIn("color: var(--ae-nav-fg);", css)

    def test_mermaid_fences_use_material_native_renderer(self):
        config = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

        self.assertIn("- pymdownx.superfences:", config)
        self.assertIn("custom_fences:", config)
        self.assertIn("- name: mermaid", config)
        self.assertIn("class: mermaid", config)
        self.assertIn(
            "format: !!python/name:pymdownx.superfences.fence_code_format",
            config,
        )

    def test_header_links_the_public_github_repository(self):
        config = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

        self.assertIn(
            "repo_url: https://github.com/SamKuler/analog-electronics-guide",
            config,
        )
        self.assertIn("repo: fontawesome/brands/github", config)

    def test_homepage_hero_separates_actions_from_metrics(self):
        index = (DOCS / "index.md").read_text(encoding="utf-8")
        css = (DOCS / "assets" / "stylesheets" / "extra.css").read_text(
            encoding="utf-8"
        )

        self.assertIn('class="ae-hero__actions"', index)
        self.assertIn('class="ae-route"', index)
        self.assertIn("先看学习路线", index)
        self.assertNotIn('class="ae-hero__panel"', index)
        self.assertLess(index.index("ae-hero__actions"), index.index("ae-metrics"))
        self.assertIn(".ae-hero__actions", css)
        self.assertIn(".ae-route", css)
        self.assertIn("border-top: 1px solid var(--ae-line);", css)
        self.assertIn("border-bottom: 1px solid var(--ae-line);", css)

    def test_public_navigation_has_no_agent_course_page(self):
        config = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
        index = (DOCS / "index.md").read_text(encoding="utf-8")

        self.assertNotIn("agent-systems.md", config)
        self.assertNotIn("智能系统中的模拟边界", config)
        self.assertNotIn("agent-systems.md", index)
        self.assertNotIn("智能系统中的模拟边界", index)

    def test_homepage_signal_chain_stays_inside_analog_scope(self):
        index = (DOCS / "index.md").read_text(encoding="utf-8")

        for stage in ("信号源 / 传感器", "偏置与保护", "模拟放大 / 滤波", "负载与驱动", "电源与接地"):
            with self.subTest(stage=stage):
                self.assertIn(stage, index)
        self.assertNotIn("数字处理 / 控制", index)

    def test_new_labs_expose_accessible_interactive_contract(self):
        for filename in self.NEW_LABS:
            with self.subTest(filename=filename):
                html = (DOCS / "labs" / filename).read_text(encoding="utf-8")
                self.assertIn('type="module"', html)
                self.assertIn('aria-live="polite"', html)
                self.assertIn('role="img"', html)
                self.assertIn("<title", html)
                self.assertIn("<desc", html)
                self.assertIn("@media (prefers-color-scheme:", html)
                self.assertIn("@media (prefers-reduced-motion:", html)
                self.assertIn("先预测", html)
                self.assertIn("一次只改一个参数", html)
                self.assertIn("模型限制", html)

    def test_new_labs_are_linked_from_navigation_and_curriculum(self):
        config = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
        curriculum = "\n".join(
            (DOCS / path).read_text(encoding="utf-8")
            for path in (
                "index.md",
                "sprint/week-2.md",
                "sprint/week-3.md",
                "sprint/week-4.md",
                "guide/02-二极管与半导体基础.md",
                "guide/04-基本放大电路.md",
                "guide/06-反馈与频率响应.md",
                "guide/07-差分功放与电源.md",
            )
        )

        for filename in self.NEW_LABS:
            with self.subTest(filename=filename):
                self.assertIn(f"labs/{filename}", config)
                self.assertIn(filename, curriculum)

    def test_teaching_svgs_are_accessible_and_self_contained(self):
        figure_paths = sorted((DOCS / "assets" / "figures").glob("*.svg"))
        self.assertTrue(figure_paths)

        for path in figure_paths:
            filename = path.name
            with self.subTest(filename=filename):
                root = ET.parse(path).getroot()
                local_name = root.tag.rsplit("}", 1)[-1]
                children = {
                    child.tag.rsplit("}", 1)[-1]: (child.text or "").strip()
                    for child in root
                }
                all_elements = list(root.iter())

                self.assertEqual("svg", local_name)
                self.assertTrue(root.attrib.get("viewBox"))
                self.assertTrue(children.get("title"))
                self.assertTrue(children.get("desc"))
                self.assertFalse(
                    any(element.tag.rsplit("}", 1)[-1] == "image" for element in all_elements)
                )
                self.assertFalse(
                    any(
                        str(value).startswith(("http://", "https://"))
                        for element in all_elements
                        for value in element.attrib.values()
                    )
                )
                self.assertTrue(
                    any(element.attrib.get("class") == "bg" for element in all_elements),
                    f"{filename} 必须自带背景，避免站点主题与系统主题不一致时失去对比度",
                )

    def test_physics_figures_keep_key_semantic_roles(self):
        expected_roles = {
            "pn-junction.svg": {"hole-drift", "electron-drift"},
            "diode-models-loadline.svg": {"load-line-q", "small-signal-q"},
            "small-signal-models.svg": {
                "curve-q",
                "bjt-gm-source",
                "mos-gm-source",
                "mos-ro",
            },
            "rectifier-filter.svg": {"filter-capacitor", "load-resistor"},
        }

        for filename, roles in expected_roles.items():
            with self.subTest(filename=filename):
                root = ET.parse(DOCS / "assets" / "figures" / filename).getroot()
                actual = {
                    element.attrib["data-role"]
                    for element in root.iter()
                    if "data-role" in element.attrib
                }
                self.assertTrue(roles <= actual)

    def test_transistor_lab_calls_its_limits_an_abstract_output_window(self):
        html = (DOCS / "labs" / "transistor-amplifier.html").read_text(
            encoding="utf-8"
        )

        self.assertIn("抽象输出窗口", html)
        self.assertNotIn("截止/饱和或三极管区被截断", html)

    def test_pages_ci_runs_browser_model_tests(self):
        workflow = (ROOT / ".github" / "workflows" / "pages.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("node --test tests/**/*.test.mjs", workflow)

    def test_lab_plots_scroll_locally_at_narrow_widths(self):
        css = (DOCS / "assets" / "stylesheets" / "lab.css").read_text(
            encoding="utf-8"
        )

        self.assertRegex(css, r"figure\s*\{[^}]*overflow-x:\s*auto;")
        self.assertRegex(
            css,
            r"@media \(max-width: 760px\)[\s\S]*?\.lab-plot\s*\{[^}]*min-width: 60rem;",
        )
        self.assertRegex(css, r"#stepPlot\s*\{[^}]*min-width: 42rem;")
        self.assertNotIn("min-height: 330px;", css)

    def test_diode_clamper_uses_recharge_event_not_a_conduction_percentage(self):
        html = (DOCS / "labs" / "diode-waveforms.html").read_text(
            encoding="utf-8"
        )

        self.assertIn('id="dutyLabel"', html)
        self.assertIn('"重充标记"', html)
        self.assertIn('"负峰附近"', html)

    def test_rectifier_lab_disambiguates_center_tap_rms_and_line_styles(self):
        html = (DOCS / "labs" / "rectifier-filter.html").read_text(
            encoding="utf-8"
        )

        self.assertIn("每半绕组 RMS", html)
        self.assertGreaterEqual(html.count('"stroke-dasharray"'), 2)

    def test_teaching_figure_css_is_responsive(self):
        css = (DOCS / "assets" / "stylesheets" / "extra.css").read_text(
            encoding="utf-8"
        )

        self.assertIn(".ae-figure", css)
        self.assertIn("width: 100%;", css)
        self.assertIn("height: auto;", css)
        self.assertIn("overflow-x: auto;", css)
        self.assertRegex(
            css,
            r"\.md-typeset \.ae-figure-frame\s*\{[^}]*width: 100%;",
        )
        self.assertIn(".ae-figure-frame > p", css)
        self.assertRegex(
            css,
            r"@media \(max-width: 52rem\)[\s\S]*?"
            r"\.md-typeset \.ae-figure\s*\{[^}]*min-width: 38rem;",
        )

    def test_math_scrolls_instead_of_expanding_the_page(self):
        css = (DOCS / "assets" / "stylesheets" / "extra.css").read_text(
            encoding="utf-8"
        )

        self.assertIn('mjx-container[jax="CHTML"][display="true"]', css)
        self.assertIn(".md-typeset span.arithmatex", css)
        self.assertIn("overflow-x: auto;", css)
        self.assertIn("max-width: 100%;", css)

    def test_teaching_figures_are_embedded_in_guides_with_alt_text(self):
        guides = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted((DOCS / "guide").glob("*.md"))
        )

        for filename in self.TEACHING_FIGURES:
            with self.subTest(filename=filename):
                figure = re.compile(
                    rf"!\[([^\]\n]+)\]\(\.\./assets/figures/{re.escape(filename)}\)"
                    r"\{\s*\.ae-figure\s*\}"
                )
                match = figure.search(guides)
                self.assertIsNotNone(match)
                self.assertTrue(match.group(1).strip())


class BuiltSiteRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._temporary_site = tempfile.TemporaryDirectory()
        cls.site_dir = Path(cls._temporary_site.name)
        subprocess.run(
            [
                sys.executable,
                "-m",
                "mkdocs",
                "build",
                "--strict",
                "--site-dir",
                str(cls.site_dir),
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

    @classmethod
    def tearDownClass(cls):
        cls._temporary_site.cleanup()

    def test_teaching_figures_are_inlined_for_site_theme_control(self):
        html = (
            self.site_dir / "guide" / "03-BJT与MOSFET" / "index.html"
        ).read_text(encoding="utf-8")

        self.assertRegex(
            html,
            r'<svg\b[^>]*class="[^"]*\bae-figure\b[^"]*"',
        )
        self.assertIn('id="ae-mosfet-regions-a"', html)
        self.assertIn("url(#ae-mosfet-regions-a)", html)
        self.assertNotRegex(
            html,
            r'<img\b[^>]*\bsrc="[^"]*/assets/figures/[^"]+\.svg"',
        )

    def test_absolute_value_math_survives_markdown_table_parsing(self):
        html = (
            self.site_dir / "guide" / "03-BJT与MOSFET" / "index.html"
        ).read_text(encoding="utf-8")

        self.assertIn(
            r'<span class="arithmatex">\(\lvert\tilde v_{be}\rvert\ll V_T\)</span>',
            html,
        )
        self.assertNotIn("<td>边界：正向有源、低频、(</td>", html)


if __name__ == "__main__":
    unittest.main()
