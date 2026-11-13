"""Lay out the complete Chapter 12 handout as Beamer frames."""
from argparse import ArgumentParser
from difflib import unified_diff
from pathlib import Path
import re
import sys


BEAMER = Path(__file__).resolve().parent
CHAPTER = BEAMER.parent / "tex" / "金融经济学_王江" / "12_均值方差偏好.tex"
EXERCISES = CHAPTER.with_stem(CHAPTER.stem + "_习题")
OUTPUT = BEAMER / "build" / "chapter12-full.tex"
HEADING = re.compile(
    r"^\\(?P<kind>section|subsection)\{(?P<title>[^{}]+)\}(?P<label>\\label\{[^{}]+\})?$"
)
EXERCISE = re.compile(r"^\\WJTwelveExercise\{exer:wj-twelve-(\d+)\}")
EXERCISE_WRAPPERS = {
    r"\begin{problem}",
    r"\end{problem}",
    r"\par\noindent\begin{minipage}{\linewidth}",
    r"\end{minipage}\par",
}
SLIDE_WRAPPERS = {
    r"\end{frame}",
    r"\WJFeasibleDirectionFrame",
    r"\framebreak",
    r"\subsection{课后习题}",
    r"\section[小结与练习]{本讲小结与课后习题}\label{sec:wj-twelve-review}",
}
SHORT_SECTIONS = {
    "均值--方差前沿组合": "前沿组合",
    "均值--方差前沿组合的性质": "前沿性质",
    "存在无风险资产的情形": "无风险资产",
}
FIGURE_SLIDES = {
    "联合正态支付与效用性质": (
        r"\WJFigureStart{fig:wj-twelve-utility-surface}",
        r"\begin{center}",
        r"\end{center}",
        "均值与标准差的效用曲面",
        "联合正态支付与效用性质",
    ),
    "最小方差问题及其解": (
        r" \WJInputFigure{12_正交投影与行列式}",
        r"\noindent\begin{minipage}{\linewidth}",
        r"\end{minipage}",
        "正交投影与行列式",
        "最小方差问题及其解",
    ),
    "前沿几何与最小方差组合": (
        r"\WJTwelveFigureStart{fig:wj-twelve-1}",
        r"\begin{center}",
        r"\end{center}",
        "两种空间中的均值--方差前沿",
        "有效前沿与可行区域",
    ),
}


def chapter_frames(source):
    """Replace document-level headings with frame boundaries."""
    _, body = source.split("\\ifdefined\\WJHandoutKnowledge\n", 1)
    body, end = body.rsplit("\n\\fi\n\n\\WJChapterExercises\n", 1)
    if not re.fullmatch(r"\\input\{[^\n]+\}\n\\endgroup\s*", end):
        raise ValueError("Unexpected Chapter 12 footer")
    headings = {"\\WJChapterSummary": "本讲小结"}
    title = "在均值--方差偏好下的投资组合选择"
    lines = []
    for line in body.splitlines():
        heading = HEADING.fullmatch(line)
        if heading:
            yield title, lines
            title = heading["title"]
            short = SHORT_SECTIONS.get(title)
            option = f"[{short}]" if short else ""
            lines = [f'\\{heading["kind"]}{option}{{{title}}}{heading["label"] or ""}']
        elif line in headings:
            yield title, lines
            title, lines = headings[line], [r"\section[小结与练习]{本讲小结与课后习题}\label{sec:wj-twelve-review}"]
        elif line.startswith(r"\begin{solution}[label-content={},label-indentation=false"):
            yield title, lines
            title, lines = "定理 12.3 的补充证明", [line]
        else:
            lines.append(line)
    yield title, lines


def exercise_frames(source):
    """Keep each full question and solution in a separate group of frames."""
    lines = []
    number = None
    title = "课后习题"
    for line in source.splitlines():
        if line == r"\begin{problem}":
            if number is not None:
                yield title, lines
                lines = []
            title = None
        elif match := EXERCISE.match(line):
            number = match[1]
            title = f"练习 12.{number}"
            lines.append(line)
        elif line == r"\end{problem}":
            if title != f"练习 12.{number}":
                raise ValueError("Exercise question missing its number")
            yield title, lines
            lines = []
            title = f"练习 12.{number} 解答"
        elif line not in EXERCISE_WRAPPERS:
            lines.append(line)
    yield title, lines


def render_frame(title, lines):
    # Move only sectioning commands outside the frame. The body stays verbatim.
    if lines and lines[0].startswith((r"\section", r"\subsection")):
        heading, *lines = lines
        yield heading
    lines = list(lines)
    while lines and not lines[-1].strip():
        lines.pop()
    if not any(line.strip() and not line.lstrip().startswith("%") for line in lines):
        yield from lines
        return
    # Keep large figures and their captions together on dedicated slides.
    if title in FIGURE_SLIDES:
        label, opening, closing, figure_title, next_title = FIGURE_SLIDES[title]
        anchor = next(i for i, line in enumerate(lines) if line.startswith(label))
        start = max(i for i in range(anchor) if lines[i] == opening)
        end = lines.index(closing, anchor) + 1
        yield from slide(title, lines[:start])
        yield from slide(figure_title, lines[start:end])
        yield from slide(next_title, lines[end:])
    else:
        yield from slide(title, lines)
    if title == "最小方差问题及其解":
        yield r"\WJFeasibleDirectionFrame"


def slide(title, lines):
    yield r"\begin{frame}[allowframebreaks=.91,t]{" + title + "}"
    yield r"\footnotesize" if title == "定理 12.3 的补充证明" else r"\small"
    for index, line in enumerate(lines):
        if line == r"\begin{center}" and (
            r"\WJFigureStart{fig:wj-twelve-quadratic-marginals}%" in lines[index:index + 5]
        ):
            yield r"\framebreak"
        if title == "联合正态支付与效用性质" and line.startswith(
            ("再求一次偏导时", "有了这些偏导，便可逐项判断")
        ):
            yield r"\framebreak"
        yield line
    yield r"\end{frame}"


def build():
    chapter = CHAPTER.read_text()
    exercises = EXERCISES.read_text()
    yield "% Generated from the full Chapter 12 handout by sync-chapter12.py."
    for title, lines in chapter_frames(chapter):
        yield from render_frame(title, lines)
        yield ""
    yield r"\subsection{课后习题}"
    for title, lines in exercise_frames(exercises):
        yield from render_frame(title, lines)
        yield ""


def content_lines(source):
    return [line for line in source.splitlines() if line.strip() and not line.lstrip().startswith("%")]


def content_diff(slides):
    """Compare the frame contents with the source, allowing only layout changes."""
    chapter = CHAPTER.read_text().split("\\ifdefined\\WJHandoutKnowledge\n", 1)[1]
    chapter = chapter.rsplit("\n\\fi\n\n\\WJChapterExercises\n", 1)[0]
    original = [
        line for line in content_lines(chapter + "\n" + EXERCISES.read_text())
        if line not in EXERCISE_WRAPPERS and line != r"\WJChapterSummary"
    ]
    actual = []
    after_frame_start = False
    for line in content_lines(slides):
        frame_start = line.startswith(r"\begin{frame}")
        frame_font = after_frame_start and line in {r"\small", r"\footnotesize"}
        after_frame_start = frame_start
        if frame_start or frame_font or line in SLIDE_WRAPPERS:
            continue
        actual.append(re.sub(r"^(\\section)\[[^\]]+\]", r"\1", line))
    return list(unified_diff(
        [line + "\n" for line in original], [line + "\n" for line in actual],
        fromfile="Chapter 12 body and exercises", tofile="Beamer frame content",
    ))


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="check handout content and the cached frames")
    args = parser.parse_args()
    expected = "\n".join(build())
    differences = content_diff(expected)
    if differences:
        sys.stderr.writelines(differences)
        return 1
    current = OUTPUT.read_text() if OUTPUT.exists() else ""
    if args.check:
        if current != expected:
            sys.stdout.writelines(unified_diff(current.splitlines(True), expected.splitlines(True),
                                               fromfile=str(OUTPUT), tofile="current Chapter 12 TeX"))
            return 1
        print("第 12 讲 Beamer 生成稿与当前讲义同步")
    elif current != expected:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        temporary = OUTPUT.with_suffix(".tmp")
        temporary.write_text(expected)
        temporary.replace(OUTPUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
