import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "validate_guide.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_guide", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


validator = load_validator()


def build_valid_root(root: Path) -> None:
    """生成一棵满足全部验证条件的最小指南目录。"""

    chapter_markers = "冲刺必会 面试加分 考后深入 适用边界 30 秒回答 90 秒回答 练习"
    for relative in validator.expected_files():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".md":
            content = "# 有效内容\n"
            if path.parent.name == "guide":
                content += f"\n{chapter_markers}\n"
            path.write_text(content, encoding="utf-8")
        else:
            path.write_text("<!doctype html><title>有效实验</title>\n", encoding="utf-8")

    (root / "docs" / "guide" / "01-最小电路基础.md").write_text(
        "# 核心术语\n\n"
        + "、".join(validator.CORE_TERMS)
        + f"\n\n{chapter_markers}\n",
        encoding="utf-8",
    )
    days_by_week = {week: [] for week in range(1, 5)}
    for day in range(1, 31):
        week = min((day - 1) // 8 + 1, 4)
        minutes = 100 if day == 30 else 45
        days_by_week[week].append(f"### Day {day}\n\n预计用时：{minutes} 分钟\n")
    for week, sections in days_by_week.items():
        (root / "docs" / "sprint" / f"week-{week}.md").write_text(
            "\n".join(sections), encoding="utf-8"
        )


class ValidateGuideTests(unittest.TestCase):
    def test_expected_files_lists_only_final_user_artifacts(self):
        files = validator.expected_files()

        self.assertIn("README.md", files)
        self.assertIn("docs/guide/01-最小电路基础.md", files)
        self.assertIn("docs/labs/opamp-feedback.html", files)
        self.assertIn("AGENTS.md", files)
        self.assertIn("prompts/学习助手.md", files)
        self.assertNotIn("scripts/validate_guide.py", files)
        self.assertNotIn("tests/test_validate_guide.py", files)
        self.assertFalse(any(path.startswith(".internal/") for path in files))

    def test_expected_files_include_all_interactive_lab_artifacts(self):
        files = set(validator.expected_files())
        lab_names = (
            "diode-waveforms",
            "transistor-amplifier",
            "bode-stability",
            "rectifier-filter",
        )

        for name in lab_names:
            with self.subTest(name=name):
                self.assertIn(f"docs/labs/{name}.html", files)
                self.assertIn(f"docs/assets/javascripts/labs/{name}.mjs", files)
        self.assertIn("docs/assets/stylesheets/lab.css", files)

    def test_empty_root_reports_readme_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = validator.find_missing_files(Path(directory))

        self.assertIn("README.md", missing)

    def test_content_files_only_returns_user_facing_markdown(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("首页", encoding="utf-8")
            (root / "docs").mkdir()
            (root / "docs" / "chapter.md").write_text("正文", encoding="utf-8")
            (root / ".internal").mkdir()
            (root / ".internal" / "plan.md").write_text("内部计划", encoding="utf-8")
            (root / "scripts").mkdir()
            (root / "scripts" / "notes.md").write_text("内部说明", encoding="utf-8")

            files = validator.content_files(root)

        self.assertEqual(
            ["README.md", "docs/chapter.md"],
            [path.relative_to(root).as_posix() for path in files],
        )

    def test_unfinished_marker_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("这一节待补充。", encoding="utf-8")

            errors = validator.find_forbidden_markers(root)

        self.assertTrue(any("README.md" in error and "待补充" in error for error in errors))

    def test_personal_marker_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs").mkdir()
            (root / "docs" / "index.md").write_text(
                "面向清华电子系的个人备考材料。\n",
                encoding="utf-8",
            )

            errors = validator.find_personal_markers(root)

        self.assertEqual(
            ["docs/index.md:1: 公开内容含个性化表述“清华电子系”"],
            errors,
        )

    def test_cross_course_teaching_marker_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sprint = root / "docs" / "sprint"
            sprint.mkdir(parents=True)
            (sprint / "week-1.md").write_text(
                "## 本周跨课程负载\n\n结束即切换信号与系统等课程。\n",
                encoding="utf-8",
            )

            errors = validator.find_course_scope_markers(root)

        self.assertEqual(
            [
                "docs/sprint/week-1.md:1: 课程范围外表述“本周跨课程负载”",
                "docs/sprint/week-1.md:3: 课程范围外表述“结束即切换信号与系统”",
            ],
            errors,
        )

    def test_learning_assistant_agent_word_is_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "prompts").mkdir()
            (root / "docs" / "assistant").mkdir(parents=True)
            (root / "AGENTS.md").write_text(
                "Agent 只担任模拟电子技术学习助手。\n",
                encoding="utf-8",
            )
            (root / "prompts" / "学习助手.md").write_text(
                "让 Agent 按教材批改。\n",
                encoding="utf-8",
            )
            (root / "docs" / "assistant" / "使用学习助手.md").write_text(
                "Clone 后可与 Agent 对话学习。\n",
                encoding="utf-8",
            )

            errors = validator.find_course_scope_markers(root)

        self.assertEqual([], errors)

    def test_tutor_contract_lists_supported_commands(self):
        commands = (
            "开始第 N 天",
            "只做 P0",
            "批改 <题号>",
            "开始模拟面试",
            "复盘",
            "查看到期复习",
        )
        agents_text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

        for command in commands:
            with self.subTest(command=command):
                self.assertIn(command, agents_text)

    def test_private_learning_state_is_ignored(self):
        ignore_text = (ROOT / ".gitignore").read_text(encoding="utf-8")

        self.assertIn(".learning/", ignore_text.splitlines())

    def test_day_headings_and_minutes_are_collected_and_sum(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs" / "sprint").mkdir(parents=True)
            (root / "docs" / "sprint" / "week-1.md").write_text(
                """### Day 1：电路语言

预计用时：45 分钟

### Day 2：两种定律

预计用时：50 分钟
""",
                encoding="utf-8",
            )

            schedule = validator.collect_schedule_minutes(root)

        self.assertEqual(
            [
                (1, 45, "docs/sprint/week-1.md", 1),
                (2, 50, "docs/sprint/week-1.md", 5),
            ],
            [
                (entry.day, entry.minutes, entry.source, entry.line)
                for entry in schedule
            ],
        )
        self.assertEqual(95, sum(entry.minutes for entry in schedule))

    def test_duplicate_day_in_same_file_reports_both_locations_and_skips_total(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs" / "sprint").mkdir(parents=True)
            (root / "docs" / "sprint" / "week-1.md").write_text(
                """### Day 1

预计用时：45 分钟

### Day 1

预计用时：50 分钟
""",
                encoding="utf-8",
            )

            errors = validator.validate(root)

        duplicate_errors = [error for error in errors if "重复" in error]
        self.assertEqual(
            ["冲刺日程 Day 1 重复：docs/sprint/week-1.md:1、docs/sprint/week-1.md:5"],
            duplicate_errors,
        )
        self.assertFalse(any("预计用时总计" in error for error in errors))

    def test_duplicate_day_across_files_reports_both_locations(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs" / "sprint").mkdir(parents=True)
            for filename, minutes in (("week-1.md", 45), ("week-2.md", 50)):
                (root / "docs" / "sprint" / filename).write_text(
                    f"### Day 8\n\n预计用时：{minutes} 分钟\n",
                    encoding="utf-8",
                )

            errors = validator.validate(root)

        duplicate_errors = [error for error in errors if "重复" in error]
        self.assertEqual(
            ["冲刺日程 Day 8 重复：docs/sprint/week-1.md:1、docs/sprint/week-2.md:1"],
            duplicate_errors,
        )

    def test_broken_relative_link_is_reported_but_images_and_remote_links_are_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text(
                "# 现在开始\n\n" + "\n".join(
                    [
                        "[缺失章节](guide/missing.md)",
                        "![缺失图片](images/missing.png)",
                        "[网页](https://example.com)",
                        "[页内](#现在开始)",
                        "[邮件](mailto:student@example.com)",
                    ]
                ),
                encoding="utf-8",
            )

            errors = validator.find_broken_local_links(root)

        self.assertEqual(1, len(errors))
        self.assertIn("guide/missing.md", errors[0])

    def test_existing_relative_link_with_anchor_is_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs" / "guide").mkdir(parents=True)
            (root / "docs" / "guide" / "chapter.md").write_text("# 标题", encoding="utf-8")
            (root / "README.md").write_text(
                "[进入章节](docs/guide/chapter.md#标题)", encoding="utf-8"
            )

            errors = validator.find_broken_local_links(root)

        self.assertEqual([], errors)

    def test_missing_local_html_resource_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            labs = root / "docs" / "labs"
            labs.mkdir(parents=True)
            (labs / "demo.html").write_text(
                '<link rel="stylesheet" href="../assets/missing.css">\n'
                '<script type="module" src="../assets/missing.mjs"></script>\n',
                encoding="utf-8",
            )

            errors = validator.find_broken_html_resources(root)

        self.assertEqual(
            [
                "docs/labs/demo.html:1: 本地 HTML 资源不存在：../assets/missing.css",
                "docs/labs/demo.html:2: 本地 HTML 资源不存在：../assets/missing.mjs",
            ],
            errors,
        )

    def test_existing_and_remote_html_resources_are_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            assets = root / "docs" / "assets"
            labs = root / "docs" / "labs"
            assets.mkdir(parents=True)
            labs.mkdir(parents=True)
            (assets / "lab.css").write_text("body {}", encoding="utf-8")
            (labs / "demo.html").write_text(
                '<link rel="stylesheet" href="../assets/lab.css">\n'
                '<script src="https://example.com/demo.js"></script>\n'
                '<a href="#controls">参数</a>\n',
                encoding="utf-8",
            )

            errors = validator.find_broken_html_resources(root)

        self.assertEqual([], errors)

    def test_missing_inline_module_import_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            labs = root / "docs" / "labs"
            labs.mkdir(parents=True)
            (labs / "demo.html").write_text(
                '<script type="module">\n'
                '  import { model } from "../assets/missing.mjs";\n'
                "</script>\n",
                encoding="utf-8",
            )

            errors = validator.find_broken_html_resources(root)

        self.assertEqual(
            [
                "docs/labs/demo.html:2: "
                "本地 HTML 资源不存在：../assets/missing.mjs"
            ],
            errors,
        )

    def test_pure_fragment_link_is_ignored_even_when_heading_is_absent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text(
                "[页内占位](#不存在)", encoding="utf-8"
            )

            errors = validator.find_broken_local_links(root)

        self.assertEqual([], errors)

    def test_missing_fragment_in_existing_markdown_file_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs" / "guide").mkdir(parents=True)
            (root / "docs" / "guide" / "chapter.md").write_text("# 已有标题", encoding="utf-8")
            (root / "README.md").write_text(
                "[进入章节](docs/guide/chapter.md#不存在)", encoding="utf-8"
            )

            errors = validator.find_broken_local_links(root)

        self.assertEqual(
            ["README.md:1: 本地链接片段不存在：docs/guide/chapter.md#不存在"],
            errors,
        )

    def test_heading_slug_and_explicit_anchor_are_valid_fragments(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs" / "guide").mkdir(parents=True)
            (root / "docs" / "guide" / "chapter.md").write_text(
                "# 标题：一、二！\n\n<a id=\"day-1\"></a>\n",
                encoding="utf-8",
            )
            (root / "README.md").write_text(
                "[标题](docs/guide/chapter.md#标题一二)\n"
                "[显式锚点](docs/guide/chapter.md#day-1)\n",
                encoding="utf-8",
            )

            errors = validator.find_broken_local_links(root)

        self.assertEqual([], errors)

    def test_encoded_spaces_queries_parentheses_and_generic_uri_schemes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs" / "guide").mkdir(parents=True)
            (root / "docs" / "guide" / "有 空格.md").write_text("# 小节", encoding="utf-8")
            (root / "docs" / "guide" / "器件(进阶).md").write_text("# 内容", encoding="utf-8")
            (root / "README.md").write_text(
                "\n".join(
                    [
                        "[编码路径](docs/guide/%E6%9C%89%20%E7%A9%BA%E6%A0%BC.md?mode=fast#小节)",
                        "[括号路径](docs/guide/器件(进阶).md)",
                        "[文件传输](ftp://example.com/chapter.md)",
                        "[电话](tel:+861234567890)",
                        "[笔记应用](obsidian://open?vault=模拟电路)",
                    ]
                ),
                encoding="utf-8",
            )

            errors = validator.find_broken_local_links(root)

        self.assertEqual([], errors)

    def test_missing_core_terms_only_reports_absent_terms(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs" / "guide").mkdir(parents=True)
            (root / "docs" / "guide" / "chapter.md").write_text(
                "KCL、KVL 与戴维南是电路基础。", encoding="utf-8"
            )

            missing = validator.find_missing_core_terms(root)

        self.assertNotIn("KCL", missing)
        self.assertNotIn("KVL", missing)
        self.assertNotIn("戴维南", missing)
        self.assertIn("BJT", missing)

    def test_reports_missing_chapter_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            guide = root / "docs" / "guide"
            guide.mkdir(parents=True)
            (guide / "01.md").write_text(
                "冲刺必会 面试加分 考后深入 适用边界 30 秒回答 练习",
                encoding="utf-8",
            )
            self.assertEqual(
                ["docs/guide/01.md: 90 秒回答"],
                validator.find_missing_chapter_markers(root),
            )

    def test_validate_combines_structural_and_content_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text(
                "待补充：[断链](missing.md)", encoding="utf-8"
            )

            errors = validator.validate(root)

        joined = "\n".join(errors)
        self.assertIn("缺少文件", joined)
        self.assertIn("未完成标记", joined)
        self.assertIn("本地链接不存在", joined)
        self.assertIn("30", joined)
        self.assertIn("核心术语", joined)

    def test_main_returns_nonzero_and_prints_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            output = io.StringIO()
            original_argv = sys.argv
            try:
                sys.argv = [str(MODULE_PATH), directory]
                with contextlib.redirect_stdout(output):
                    result = validator.main()
            finally:
                sys.argv = original_argv

        self.assertEqual(1, result)
        self.assertIn("FAIL", output.getvalue())

    def test_complete_valid_root_passes_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            build_valid_root(root)

            errors = validator.validate(root)

        self.assertEqual([], errors)

    def test_main_returns_zero_and_prints_exact_pass_diagnostic(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            build_valid_root(root)
            output = io.StringIO()
            original_argv = sys.argv
            try:
                sys.argv = [str(MODULE_PATH), directory]
                with contextlib.redirect_stdout(output):
                    result = validator.main()
            finally:
                sys.argv = original_argv

        self.assertEqual(0, result)
        self.assertEqual(
            "PASS: 30 days, 1405 minutes, 0 broken links, "
            "0 forbidden markers, 0 personal markers.\n",
            output.getvalue(),
        )


if __name__ == "__main__":
    unittest.main()
