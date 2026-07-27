import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


class RenderingContractTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
