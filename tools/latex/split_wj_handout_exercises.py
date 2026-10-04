#!/usr/bin/env python3
"""Split 金融经济学_王江 chapter files into chapter shell + _习题.tex."""

from __future__ import annotations

import re
from pathlib import Path

CHAPTER_DIR = Path(__file__).resolve().parents[2] / "tex/金融经济学_王江"

CHAPTERS = [
    "02_基本框架.tex",
    "03_Arrow-Debreu经济.tex",
    "04_套利和资产定价.tex",
    "05_期权.tex",
    "06_期望效用函数.tex",
    "07_风险厌恶.tex",
    "08_组合选择一.tex",
    "09_组合选择二.tex",
    "10_完全市场.tex",
    "11_不完全市场.tex",
    "12_均值方差偏好.tex",
    "13_CAPM.tex",
    "14_APT.tex",
    "15_完全市场下的公司财务.tex",
]

BEGIN_PROBLEM = re.compile(r"^\s*\\begin\{problem\}\s*$")
END_PROBLEM = re.compile(r"^\s*\\end\{problem\}\s*$")
BEGIN_SOLUTION = re.compile(r"^\s*\\begin\{solution\}\s*$")
END_SOLUTION = re.compile(r"^\s*\\end\{solution\}\s*$")
ZHCHAPTER = re.compile(r"^\\zhchapter\{.*\}\s*$")


def extract_problem_solution_blocks(lines: list[str]) -> tuple[list[str], list[str]]:
    """Return (body_without_blocks, concatenated exercise blocks in order)."""
    exercises: list[str] = []
    body: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        if BEGIN_PROBLEM.match(lines[i]):
            block: list[str] = []
            while i < n:
                block.append(lines[i])
                if END_PROBLEM.match(lines[i]):
                    i += 1
                    break
                i += 1
            else:
                raise ValueError("Unclosed problem environment")
            if i >= n or not BEGIN_SOLUTION.match(lines[i]):
                raise ValueError(f"Expected \\begin{{solution}} after problem, got line {i + 1}")
            while i < n:
                block.append(lines[i])
                if END_SOLUTION.match(lines[i]):
                    i += 1
                    break
                i += 1
            else:
                raise ValueError("Unclosed solution environment")
            exercises.extend(block)
            if exercises and not exercises[-1].endswith("\n"):
                exercises.append("\n")
            exercises.append("\n")
            continue
        body.append(lines[i])
        i += 1
    return body, exercises


def split_chapter(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    header: list[str] = []
    rest_start = 0
    for idx, line in enumerate(lines):
        if ZHCHAPTER.match(line.rstrip("\n")):
            rest_start = idx
            break
        header.append(line)
    else:
        raise ValueError(f"No \\zhchapter in {path}")

    zhchapter_line = lines[rest_start]
    after_chapter = lines[rest_start + 1 :]

    body, exercise_lines = extract_problem_solution_blocks(after_chapter)

    # Trim trailing blank lines from body before \fi
    while body and body[-1].strip() == "":
        body.pop()

    stem = path.stem
    exercise_name = f"{stem}_习题.tex"
    exercise_path = path.parent / exercise_name
    input_line = f"\\input{{tex/金融经济学_王江/{exercise_name}}}\n"

    exercise_header = (
        f"% !TeX root = ../../金融经济学_王江_讲义及习题.tex\n"
        f"% {stem} 课后习题（由章节文件拆分）\n\n"
    )
    exercise_path.write_text(exercise_header + "".join(exercise_lines), encoding="utf-8")

    shell_parts: list[str] = []
    shell_parts.extend(header)
    shell_parts.append(zhchapter_line)
    shell_parts.append("\n")
    shell_parts.append("\\ifdefined\\WJHandoutKnowledge\n")
    shell_parts.extend(body)
    if body and not body[-1].endswith("\n"):
        shell_parts.append("\n")
    shell_parts.append("\\fi\n\n")
    shell_parts.append(input_line)

    path.write_text("".join(shell_parts), encoding="utf-8")
    print(f"OK {path.name} -> {exercise_name} ({len(exercise_lines)} lines exercises)")


def main() -> None:
    for name in CHAPTERS:
        split_chapter(CHAPTER_DIR / name)


if __name__ == "__main__":
    main()
