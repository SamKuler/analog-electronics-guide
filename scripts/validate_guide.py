#!/usr/bin/env python3
"""检查模拟电子技术自学指南的结构、链接与关键内容。

Markdown 标题片段采用本项目统一规则：标题转为小写，去掉行内标记与除
字母、数字、汉字、下划线、连字符、空白以外的字符，空白转为连字符并
合并连续连字符；重复标题依次追加 ``-1``、``-2``。HTML ``id`` 或
``name`` 属性提供的显式锚点也有效。
"""

from __future__ import annotations

import argparse
import html
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit


EXPECTED_FILES = (
    "README.md",
    "AGENTS.md",
    "prompts/学习助手.md",
    "docs/index.md",
    "docs/学习路线与使用方法.md",
    "docs/assistant/使用学习助手.md",
    "docs/extensions/agent-systems.md",
    "docs/guide/01-最小电路基础.md",
    "docs/guide/02-二极管与半导体基础.md",
    "docs/guide/03-BJT与MOSFET.md",
    "docs/guide/04-基本放大电路.md",
    "docs/guide/05-运算放大器.md",
    "docs/guide/06-反馈与频率响应.md",
    "docs/guide/07-差分功放与电源.md",
    "docs/sprint/week-1.md",
    "docs/sprint/week-2.md",
    "docs/sprint/week-3.md",
    "docs/sprint/week-4.md",
    "docs/interview/高频问题与追问.md",
    "docs/interview/两套模拟面试.md",
    "docs/interview/评分标准.md",
    "docs/exercises/练习题.md",
    "docs/exercises/详细解答.md",
    "docs/cheatsheets/一页公式表.md",
    "docs/cheatsheets/典型电路速查.md",
    "docs/labs/rc-step-response.html",
    "docs/labs/bjt-load-line.html",
    "docs/labs/opamp-feedback.html",
)

CONTENT_DIRECTORIES = (
    "docs",
    "prompts",
)
FORBIDDEN_MARKERS = ("TODO", "TBD", "待补充", "稍后填写")
PERSONAL_MARKERS = (
    "清华电子系",
    "清华大学电子工程系",
    "直博",
    "推免",
    "软件工程本科",
    "另外四门课程",
    "五门课程",
)
CORE_TERMS = (
    "KCL",
    "KVL",
    "戴维南",
    "RC",
    "二极管",
    "BJT",
    "MOSFET",
    "静态工作点",
    "小信号",
    "运算放大器",
    "负反馈",
    "差分放大",
    "功率放大",
    "稳压",
)
REQUIRED_CHAPTER_MARKERS = (
    "冲刺必会",
    "面试加分",
    "考后深入",
    "适用边界",
    "30 秒回答",
    "90 秒回答",
    "练习",
)

DAY_HEADING_RE = re.compile(r"^### Day (\d+)\b", re.MULTILINE)
MINUTES_RE = re.compile(r"预计用时：(\d+) 分钟")
LINK_START_RE = re.compile(r"(?<!!)\[[^\]]*\]\(")
HEADING_RE = re.compile(r"^ {0,3}#{1,6}\s+(.+?)\s*$", re.MULTILINE)
EXPLICIT_ANCHOR_RE = re.compile(
    r"(?:\bid|\bname)\s*=\s*(?:\"([^\"]+)\"|'([^']+)'|([^\s>]+))",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ScheduleEntry:
    """一个 Day 标题及其用时和来源位置。"""

    day: int
    minutes: int | None
    source: str
    line: int


def expected_files() -> list[str]:
    """返回最终交付给学习者的文件清单。"""

    return list(EXPECTED_FILES)


def content_files(root: Path) -> list[Path]:
    """返回需要做正文检查的用户可见 Markdown 文件。"""

    root = Path(root)
    files = list(root.glob("*.md"))
    for directory in CONTENT_DIRECTORIES:
        location = root / directory
        if location.is_dir():
            files.extend(location.rglob("*.md"))
    return sorted((path for path in files if path.is_file()), key=lambda path: path.as_posix())


def public_files(root: Path) -> list[Path]:
    """返回会进入公开仓库或站点的文本文件。"""

    root = Path(root)
    files = [root / "README.md", root / "AGENTS.md"]
    for directory in ("prompts", "docs"):
        location = root / directory
        if location.is_dir():
            files.extend(location.rglob("*"))
    return sorted(
        (path for path in files if path.is_file()),
        key=lambda path: path.as_posix(),
    )


def find_personal_markers(root: Path) -> list[str]:
    """查找公开内容中的个人院校、背景与升学目标表述。"""

    root = Path(root)
    errors: list[str] = []
    for path in public_files(root):
        relative = path.relative_to(root).as_posix()
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for line_number, line in enumerate(lines, 1):
            for marker in PERSONAL_MARKERS:
                if marker in line:
                    errors.append(
                        f"{relative}:{line_number}: 公开内容含个性化表述“{marker}”"
                    )
    return errors


def find_missing_files(root: Path) -> list[str]:
    """返回相对于根目录缺失的计划交付文件。"""

    root = Path(root)
    return [relative for relative in EXPECTED_FILES if not (root / relative).is_file()]


def find_forbidden_markers(root: Path) -> list[str]:
    """查找用户可见正文中的未完成标记。"""

    root = Path(root)
    errors: list[str] = []
    for path in content_files(root):
        relative = path.relative_to(root).as_posix()
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for marker in FORBIDDEN_MARKERS:
                if marker in line:
                    errors.append(f"{relative}:{line_number}: 未完成标记“{marker}”")
    return errors


def _link_destination(raw_destination: str) -> str:
    destination = raw_destination.strip()
    if destination.startswith("<") and ">" in destination:
        destination = destination[1 : destination.index(">")]
    else:
        destination = destination.split(maxsplit=1)[0]
    return re.sub(r"\\([\\() ])", r"\1", destination)


def _link_destinations(line: str) -> list[str]:
    """提取一行中的行内链接目标，并支持目标中的成对括号。"""

    destinations: list[str] = []
    for match in LINK_START_RE.finditer(line):
        start = match.end()
        depth = 1
        escaped = False
        for index in range(start, len(line)):
            character = line[index]
            if escaped:
                escaped = False
                continue
            if character == "\\":
                escaped = True
            elif character == "(":
                depth += 1
            elif character == ")":
                depth -= 1
                if depth == 0:
                    destinations.append(line[start:index])
                    break
    return destinations


def _heading_slug(title: str) -> str:
    title = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", title)
    title = re.sub(r"<[^>]+>", "", title)
    title = html.unescape(title).strip().rstrip("#").strip().casefold()
    characters = [
        character
        for character in title
        if character.isalnum() or character in "_-" or character.isspace()
    ]
    slug = re.sub(r"\s+", "-", "".join(characters))
    return re.sub(r"-+", "-", slug).strip("-")


def _document_anchors(path: Path) -> set[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return set()

    anchors = {
        next(group for group in match.groups() if group is not None)
        for match in EXPLICIT_ANCHOR_RE.finditer(text)
    }
    slug_counts: dict[str, int] = {}
    for match in HEADING_RE.finditer(text):
        base_slug = _heading_slug(match.group(1))
        if not base_slug:
            continue
        duplicate_index = slug_counts.get(base_slug, 0)
        slug_counts[base_slug] = duplicate_index + 1
        slug = base_slug if duplicate_index == 0 else f"{base_slug}-{duplicate_index}"
        anchors.add(slug)
    return anchors


def find_broken_local_links(root: Path) -> list[str]:
    """查找正文 Markdown 中指向不存在文件的相对链接。"""

    root = Path(root)
    errors: list[str] = []
    anchor_cache: dict[Path, set[str]] = {}
    for path in content_files(root):
        relative = path.relative_to(root).as_posix()
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for raw_destination in _link_destinations(line):
                destination = _link_destination(raw_destination)
                if not destination or destination.startswith("#"):
                    continue
                try:
                    parsed = urlsplit(destination)
                except ValueError:
                    parsed = urlsplit("")
                if parsed.scheme or parsed.netloc:
                    continue

                file_part = unquote(parsed.path)
                fragment = unquote(parsed.fragment)
                target = path if not file_part else (path.parent / file_part).resolve()
                if not target.exists():
                    errors.append(
                        f"{relative}:{line_number}: 本地链接不存在：{destination}"
                    )
                    continue
                if fragment:
                    anchors = anchor_cache.setdefault(target, _document_anchors(target))
                    if fragment not in anchors:
                        errors.append(
                            f"{relative}:{line_number}: 本地链接片段不存在：{destination}"
                        )
    return errors


def collect_schedule_minutes(root: Path) -> list[ScheduleEntry]:
    """收集每个 Day 标题的用时、相对文件路径和标题行号。"""

    root = Path(root)
    schedule: list[ScheduleEntry] = []
    sprint_directory = root / "docs" / "sprint"
    if not sprint_directory.is_dir():
        return schedule

    for path in sorted(sprint_directory.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        source = path.relative_to(root).as_posix()
        headings = list(DAY_HEADING_RE.finditer(text))
        for index, heading in enumerate(headings):
            section_end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
            section = text[heading.end() : section_end]
            minutes_match = MINUTES_RE.search(section)
            schedule.append(
                ScheduleEntry(
                    day=int(heading.group(1)),
                    minutes=int(minutes_match.group(1)) if minutes_match else None,
                    source=source,
                    line=text.count("\n", 0, heading.start()) + 1,
                )
            )
    return schedule


def find_missing_core_terms(root: Path) -> list[str]:
    """返回七章完整教材中尚未出现的核心术语。"""

    root = Path(root)
    guide_directory = root / "docs" / "guide"
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(guide_directory.glob("*.md"))
        if path.is_file()
    ) if guide_directory.is_dir() else ""
    return [term for term in CORE_TERMS if term not in text]


def find_missing_chapter_markers(root: Path) -> list[str]:
    """返回七章教材中缺失的双轨、面试与练习结构标记。"""

    root = Path(root)
    errors: list[str] = []
    for path in sorted((root / "docs" / "guide").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for marker in REQUIRED_CHAPTER_MARKERS:
            if marker not in text:
                errors.append(f"{path.relative_to(root)}: {marker}")
    return errors


def validate(root: Path) -> list[str]:
    """运行全部检查并返回适合直接打印的错误列表。"""

    root = Path(root)
    errors = [f"缺少文件：{path}" for path in find_missing_files(root)]
    errors.extend(find_forbidden_markers(root))
    errors.extend(find_personal_markers(root))
    errors.extend(find_broken_local_links(root))

    schedule = collect_schedule_minutes(root)
    entries_by_day: dict[int, list[ScheduleEntry]] = {}
    for entry in schedule:
        entries_by_day.setdefault(entry.day, []).append(entry)

    duplicate_days = {
        day: entries for day, entries in entries_by_day.items() if len(entries) > 1
    }
    for day in sorted(duplicate_days):
        locations = "、".join(
            f"{entry.source}:{entry.line}" for entry in duplicate_days[day]
        )
        errors.append(f"冲刺日程 Day {day} 重复：{locations}")

    expected_days = set(range(1, 31))
    actual_days = set(entries_by_day)
    if actual_days != expected_days:
        missing_days = sorted(expected_days - actual_days)
        extra_days = sorted(actual_days - expected_days)
        detail: list[str] = []
        if missing_days:
            detail.append(f"缺少 {missing_days}")
        if extra_days:
            detail.append(f"超出范围 {extra_days}")
        errors.append(f"冲刺日程必须包含 30 个唯一 Day；{'；'.join(detail)}")

    missing_minutes = [entry for entry in schedule if entry.minutes is None]
    for entry in missing_minutes:
        errors.append(f"冲刺日程缺少预计用时：{entry.source}:{entry.line}")

    if not duplicate_days and not missing_minutes:
        total_minutes = sum(entry.minutes for entry in schedule if entry.minutes is not None)
        if not 1320 <= total_minutes <= 1560:
            errors.append(
                f"30 天预计用时总计应为 1320–1560 分钟，当前为 {total_minutes} 分钟"
            )

    for term in find_missing_core_terms(root):
        errors.append(f"完整教材缺少核心术语：{term}")
    errors += [
        f"missing chapter marker: {item}"
        for item in find_missing_chapter_markers(root)
    ]
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="验证模拟电子技术自学指南")
    parser.add_argument("root", nargs="?", default=".", help="指南根目录，默认为当前目录")
    args = parser.parse_args()

    errors = validate(Path(args.root).resolve())
    if errors:
        print(f"FAIL：发现 {len(errors)} 个问题")
        for error in errors:
            print(f"- {error}")
        return 1

    schedule = collect_schedule_minutes(Path(args.root).resolve())
    total_minutes = sum(
        entry.minutes for entry in schedule if entry.minutes is not None
    )
    print(
        f"PASS: {len(schedule)} days, {total_minutes} minutes, "
        f"{len(find_broken_local_links(Path(args.root).resolve()))} broken links, "
        f"{len(find_forbidden_markers(Path(args.root).resolve()))} forbidden markers, "
        f"{len(find_personal_markers(Path(args.root).resolve()))} personal markers."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
