#!/usr/bin/env python3
"""从当前王江习题源码导出分章精选解答；无参数时导出第6、7章约定题目。"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT / "金融经济学_王江_讲义及习题.tex"
CHAPTER_DIR = ROOT / "tex/金融经济学_王江"
BUILD_DIR = ROOT / "build/作业精选"
OUTPUT_DIR = ROOT / "output/pdf"
DEFAULT_SELECTIONS = ["6:1,2,3", "7:1,4,5"]
BLOCK = re.compile(
    r"^[ \t]*\\begin\{problem\}\s*\\problemno\{([^}]+)\}"
    r".*?\\end\{problem\}\s*\\begin\{solution\}.*?\\end\{solution\}",
    re.MULTILINE | re.DOTALL,
)


def parse_selection(value: str) -> tuple[int, list[int]]:
    if not re.fullmatch(r"[1-9]\d*:[1-9]\d*(?:,[1-9]\d*)*", value):
        raise ValueError(f"选题格式应为 6:1,2,3，收到：{value}")
    chapter_text, numbers_text = value.split(":")
    numbers = [int(number) for number in numbers_text.split(",")]
    if len(set(numbers)) != len(numbers):
        raise ValueError(f"题号重复：{value}")
    return int(chapter_text), numbers


def make_document(chapter: int, numbers: list[int], preamble: str) -> tuple[str, str]:
    sources = list(CHAPTER_DIR.glob(f"{chapter:02d}_*_习题.tex"))
    if len(sources) != 1:
        raise ValueError(f"第 {chapter} 章习题文件应恰有一个，找到 {len(sources)} 个")
    source = sources[0]
    chapter_source = source.with_name(source.name.replace("_习题.tex", ".tex"))
    heading = re.search(
        r"^\\(?:lecture|zhchapter)\{([^{}]+)\}",
        chapter_source.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    if heading is None:
        raise ValueError(f"未找到章节标题：{chapter_source}")

    blocks: dict[str, str] = {}
    for match in BLOCK.finditer(source.read_text(encoding="utf-8")):
        label = match[1].rstrip("*")
        if label in blocks:
            raise ValueError(f"题号重复：{label}（{source.name}）")
        blocks[label] = match[0].strip()
    labels = [f"{chapter}.{number}" for number in numbers]
    missing = [label for label in labels if label not in blocks]
    if missing:
        raise ValueError(f"{source.name} 缺少题目或完整解答：{', '.join(missing)}")

    name = f"王江_第{chapter}章_作业解答_{'-'.join(map(str, numbers))}"
    # 复用正式入口的宏包、字体和事件树定义；正文只放选定题目与解答。
    document = (
        "% 自动生成；请修改章节源码后重新运行 tools/latex/export-wj-homework.py。\n"
        + preamble
        + "\n\\begin{document}\n\\fancyhead{}\n"
        + rf"\begin{{center}}\LARGE\bfseries 第{chapter}章　{heading[1]}\end{{center}}"
        + "\n\n"
        + "\n\n".join(blocks[label] for label in labels)
        + "\n\\end{document}\n"
    )
    return name, document


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "selections", nargs="*", metavar="章:题号,题号",
        help="例如 6:1,2,3 7:1,4,5；每章输出一份 PDF",
    )
    parser.add_argument(
        "--prepare-only", action="store_true", help="仅生成编译入口，不调用 latexmk",
    )
    args = parser.parse_args()
    try:
        selections = [parse_selection(value) for value in args.selections or DEFAULT_SELECTIONS]
        chapters = [chapter for chapter, _ in selections]
        if len(set(chapters)) != len(chapters):
            raise ValueError("每章请合并到同一个选题参数中")
        main_source = MAIN.read_text(encoding="utf-8")
        preamble, separator, _ = main_source.partition(r"\begin{document}")
        if not separator:
            raise ValueError(f"正式入口缺少 document 环境：{MAIN}")
        # 先验证全部选题，避免参数有误时只生成一部分入口。
        documents = [
            (chapter, *make_document(chapter, numbers, preamble))
            for chapter, numbers in selections
        ]
    except (ValueError, OSError) as error:
        parser.error(str(error))

    latexmk = shutil.which("latexmk")
    if not args.prepare_only and latexmk is None:
        parser.error("未找到 latexmk，请先安装 TeX Live / MacTeX 并加入 PATH")

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    for chapter, name, document in documents:
        entry = BUILD_DIR / f"{name}.tex"
        entry.write_text(document, encoding="utf-8")
        if args.prepare_only:
            print(entry, flush=True)
            continue
        command = [
            latexmk, "-xelatex", "-interaction=nonstopmode", "-halt-on-error",
            "-file-line-error", f"-outdir={OUTPUT_DIR.relative_to(ROOT)}",
            f"-auxdir={BUILD_DIR.relative_to(ROOT)}/ch{chapter}",
            str(entry.relative_to(ROOT)),
        ]
        try:
            subprocess.run(command, cwd=ROOT, check=True)
        except subprocess.CalledProcessError as error:
            raise SystemExit(error.returncode) from error
        print(f"已导出：{OUTPUT_DIR / (name + '.pdf')}", flush=True)


if __name__ == "__main__":
    main()
