"""Build one Wang Jiang chapter with the formal handout's preamble."""

import argparse
import re
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="生成王江讲义的单章预览。")
    parser.add_argument("chapter", type=int, help="章节号，如 3")
    parser.add_argument("--dual", action="store_true", help="并行预览教师版和学生版")
    parser.add_argument("--work-dir", type=Path, help="使用独立的预览目录")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    handout = (root / "金融经济学_王江_讲义及习题.tex").read_text(encoding="utf-8")
    preamble, marker, body = handout.partition("\n\\begin{document}\n")
    if not marker:
        parser.error("找不到讲义主文件的 \\begin{document}，请检查主文件结构。")

    chapter_number = f"{args.chapter:02d}"
    chapter_inputs = re.findall(
        rf"(?m)^[ \t]*\\input\{{(tex/金融经济学_王江/{chapter_number}_[^/}}\n]+\.tex)\}}",
        body,
    )
    if args.chapter < 1 or len(chapter_inputs) != 1 or not (root / chapter_inputs[0]).is_file():
        parser.error(f"主文件中找不到唯一可读的第 {args.chapter} 章入口。")

    name = f"wj-ch{chapter_number}-preview"
    if args.work_dir is None:
        aux_dir = root / "build" / "wj-preview" / name
        out_dir = root / "output" / "wj-preview" / name
    else:
        work_dir = args.work_dir.resolve()
        aux_dir = work_dir / "aux" / name
        out_dir = work_dir / "output" / name

    aux_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    wrapper = aux_dir / f"{name}.tex"
    source = (
        preamble + marker
        + f"\\setcounter{{chapter}}{{{args.chapter - 1}}}\n"
        + f"\\input{{{chapter_inputs[0]}}}\n"
        + "\\end{document}\n"
    )
    if not wrapper.exists() or wrapper.read_text(encoding="utf-8") != source:
        wrapper.write_text(source, encoding="utf-8")

    mode = "--parallel" if args.dual else "--teacher"
    command = [root / "tools" / "latex" / "build-dual.sh", mode, wrapper, out_dir, aux_dir]
    result = subprocess.run(command, cwd=root)
    if result.returncode == 0 and not args.dual:
        print(f"单章预览 {out_dir / (name + '.pdf')}")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
