#!/usr/bin/env python3
"""Renumber 熊和平 exercises to Wang-Jiang-style chapter.seq and drop section headers."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIR = ROOT / "tex/金融经济学_熊和平"

CHAPTER_NUM = {
    "01_基本框架及分析模式_习题.tex": 1,
    "02_期望效用理论_习题.tex": 2,
    "03_风险厌恶及典型的效用函数_习题.tex": 3,
    "04_Arrow-Debreu经济_习题.tex": 4,
    "05_套利定价的理论基础_习题.tex": 5,
    "06_无套利原理在衍生证券定价中的应用_习题.tex": 6,
    "07_基于消费的投资组合理论_习题.tex": 7,
    "08_马科维茨投资组合理论_习题.tex": 8,
    "09_资本资产定价模型_习题.tex": 9,
    "10_因子模型与套利定价理论_习题.tex": 10,
    "11_完全市场下的资源配置与资产定价_习题.tex": 11,
    "12_基于消费的资产定价模型_习题.tex": 12,
    "13_生产性经济与资源配置_习题.tex": 13,
    "14_异质性投资者_习题.tex": 14,
    "15_家庭金融_习题.tex": 15,
}


def renumber(path: Path, chapter: int) -> None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    seq = 0
    for line in lines:
        if line.strip() in ("\\xhpthoughts", "\\xhpexercises"):
            continue
        m = re.match(r"^\\problemno\{\d+\}(.*)$", line)
        if m:
            seq += 1
            line = f"\\problemno{{{chapter}.{seq}}}{m.group(1)}\n"
        out.append(line)
    path.write_text("".join(out), encoding="utf-8")


def main() -> None:
    for name, ch in CHAPTER_NUM.items():
        renumber(DIR / name, ch)
        print(f"renumbered {name} -> chapter {ch}")


if __name__ == "__main__":
    main()
