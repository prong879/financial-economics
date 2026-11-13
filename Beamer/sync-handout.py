"""Lay out the complete Chapter 12–14 handouts as Beamer frames."""
from argparse import ArgumentParser
from dataclasses import dataclass
from difflib import unified_diff
from pathlib import Path
import re
import sys


BEAMER = Path(__file__).resolve().parent
HANDOUT = BEAMER.parent / "tex" / "金融经济学_王江"


@dataclass(frozen=True)
class Chapter:
    number: int
    name: str
    label: str
    title: str

    def read(self):
        source = (HANDOUT / f"{self.number}_{self.name}.tex").read_text()
        exercises = (HANDOUT / f"{self.number}_{self.name}_习题.tex").read_text()
        preamble, body = source.split("\\ifdefined\\WJHandoutKnowledge\n", 1)
        body, end = body.rsplit("\n\\WJChapterExercises\n", 1)
        body = body.rstrip()
        if not body.endswith("\n\\fi"):
            raise ValueError(f"Unexpected Chapter {self.number} body ending")
        body = body.removesuffix("\n\\fi")
        if end.splitlines() != [
            f"\\input{{tex/金融经济学_王江/{self.number}_{self.name}_习题.tex}}",
            r"\endgroup",
        ]:
            raise ValueError(f"Unexpected Chapter {self.number} footer")
        declarations = [
            line for line in preamble.splitlines()
            if re.match(r"^\\(?:newcounter|newcommand|renewcommand)\{\\?(?:WJ|thewj|wj)", line)
        ]
        return declarations, body, exercises

    @property
    def review_section(self):
        return (
            r"\section[小结与练习]{本讲小结与课后习题}"
            + rf"\label{{sec:wj-{self.label}-review}}"
        )

    @property
    def output(self):
        return BEAMER / "build" / f"chapter{self.number}-full.tex"


CHAPTERS = (
    Chapter(12, "均值方差偏好", "twelve", "在均值--方差偏好下的投资组合选择"),
    Chapter(13, "CAPM", "thirteen", "资本资产定价模型"),
    Chapter(14, "APT", "fourteen", "套利定价理论"),
)
HEADING = re.compile(
    r"^\\(?P<kind>section|subsection|subsubsection)\{(?P<title>[^{}]+)\}(?P<label>\\label\{[^{}]+\})?$"
)
EXERCISE = re.compile(r"^\\WJ(?:Twelve|Thirteen|Fourteen)Exercise\{exer:wj-\w+-(\d+)\}")
EXERCISE_WRAPPERS = {
    r"\begin{problem}",
    r"\end{problem}",
    r"\par\noindent\begin{minipage}{\linewidth}",
    r"\end{minipage}\par",
}
SLIDE_WRAPPERS = {
    r"\end{frame}",
    r"\framebreak",
    r"\tcbset{break at=.72\textheight/.72\textheight/.72\textheight/.72\textheight}",
    r"\subsection{课后习题}",
}
SHORT_SECTIONS = {
    "均值--方差前沿组合": "前沿组合",
    "均值--方差前沿组合的性质": "前沿性质",
    "存在无风险资产的情形": "无风险资产",
    "CAPM给出的资产定价关系": "贝塔定价",
    "不存在无风险资产的CAPM": "零贝塔 CAPM",
    "作为均衡结果的CAPM": "均衡推导",
    "资产收益风险的因子模型": "因子模型",
    "精确因子模型和套利定价理论": "精确 APT",
    "极限套利和APT": "极限套利",
    "作为均衡结果的APT": "均衡 APT",
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
    "两基金分离与权重空间的直线": (
        r"\WJFigureStart{fig:wj-twelve-basis-mapping}",
        r"\begin{center}",
        r"\end{center}",
        "基准基金在两个平面的对应",
        "两基金分离与权重空间的直线",
    ),
    "Sharpe比与有效前沿": (
        r"\WJTwelveFigureStart{fig:wj-twelve-2}",
        r"\begin{center}",
        r"\end{center}",
        "无风险证券、切点组合与资本市场线",
        "Sharpe比与有效前沿",
    ),
    "前沿几何与最小方差组合": (
        r"\WJTwelveFigureStart{fig:wj-twelve-1}",
        r"\begin{center}",
        r"\end{center}",
        "两种空间中的均值--方差前沿",
        "有效前沿与可行区域",
    ),
}


def chapter_frames(chapter, body):
    """Replace document-level headings with frame boundaries."""
    title = chapter.title
    lines = []
    for line in body.splitlines():
        heading = HEADING.fullmatch(line)
        if heading:
            yield title, lines
            title = heading["title"]
            short = SHORT_SECTIONS.get(title)
            option = f"[{short}]" if short else ""
            lines = [f'\\{heading["kind"]}{option}{{{title}}}{heading["label"] or ""}']
        elif line == r"\WJChapterSummary":
            yield title, lines
            title, lines = "本讲小结", [chapter.review_section]
        elif line.startswith(r"\begin{solution}[label-content={},label-indentation=false"):
            yield title, lines
            title, lines = "定理 12.3 的补充证明", [line]
        else:
            lines.append(line)
    yield title, lines


def exercise_frames(chapter, source):
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
            title = f"练习 {chapter.number}.{number}"
            lines.append(line)
        elif line == r"\end{problem}":
            if title != f"练习 {chapter.number}.{number}":
                raise ValueError("Exercise question missing its number")
            yield title, lines
            lines = []
            title = f"练习 {chapter.number}.{number} 解答"
        elif line not in EXERCISE_WRAPPERS:
            lines.append(line)
    yield title, lines


def render_frame(title, lines):
    # Move only sectioning commands outside the frame. The body stays verbatim.
    if lines and lines[0].startswith((r"\section", r"\subsection", r"\subsubsection")):
        heading, *lines = lines
        heading = heading.replace(r"\label{", r"\WJSectionLabel{")
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


def slide(title, lines):
    yield r"\begin{frame}[allowframebreaks=.91,t]{" + title + "}"
    yield r"\footnotesize" if title == "定理 12.3 的补充证明" else r"\small"
    if title == "极限套利和均衡":
        yield r"\tcbset{break at=.72\textheight/.72\textheight/.72\textheight/.72\textheight}"
    for index, line in enumerate(lines):
        if line == r"\begin{center}" and (
            r"\WJFigureStart{fig:wj-twelve-quadratic-marginals}%" in lines[index:index + 5]
        ):
            yield r"\framebreak"
        if title == "联合正态支付与效用性质" and line.startswith(
            ("再求一次偏导时", "有了这些偏导，便可逐项判断")
        ):
            yield r"\framebreak"
        if line in {r"\WJInputFigure{13_CML与SML}", r"\WJInputFigure{14_风险分散}"}:
            yield r"\framebreak"
        if title == "练习 13.5 解答" and line.startswith(("记 $\\widetilde q$", "由两只基金的定义")):
            yield r"\framebreak"
        yield line
    yield r"\end{frame}"


def build(chapter, declarations, body, exercises):
    yield f"% Generated from the full Chapter {chapter.number} handout."
    yield from declarations
    for title, lines in chapter_frames(chapter, body):
        yield from render_frame(title, lines)
        yield ""
    yield r"\subsection{课后习题}"
    for title, lines in exercise_frames(chapter, exercises):
        yield from render_frame(title, lines)
        yield ""


def content_lines(source):
    return [line for line in source.splitlines() if line.strip() and not line.lstrip().startswith("%")]


def content_diff(chapter, declarations, body, exercises, slides):
    """Compare the frame contents with the source, allowing only layout changes."""
    original = [
        line for line in content_lines(body + "\n" + exercises)
        if line not in EXERCISE_WRAPPERS and line != r"\WJChapterSummary"
    ]
    actual = []
    after_frame_start = False
    for line in content_lines(slides):
        frame_start = line.startswith(r"\begin{frame}")
        frame_font = after_frame_start and line in {r"\small", r"\footnotesize"}
        after_frame_start = frame_start
        if frame_start or frame_font or line in SLIDE_WRAPPERS or line in declarations:
            continue
        line = line.replace(r"\WJSectionLabel{", r"\label{")
        if line == chapter.review_section:
            continue
        actual.append(re.sub(r"^(\\section)\[[^\]]+\]", r"\1", line))
    return list(unified_diff(
        [line + "\n" for line in original], [line + "\n" for line in actual],
        fromfile=f"Chapter {chapter.number} body and exercises", tofile="Beamer frame content",
    ))


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="check handout content and the cached frames")
    args = parser.parse_args()
    failed = False
    for chapter in CHAPTERS:
        source = chapter.read()
        expected = "\n".join(build(chapter, *source))
        differences = content_diff(chapter, *source, expected)
        if differences:
            sys.stderr.writelines(differences)
            failed = True
            continue

        output = chapter.output
        current = output.read_text() if output.exists() else ""
        if args.check:
            if current != expected:
                sys.stdout.writelines(unified_diff(
                    current.splitlines(True), expected.splitlines(True),
                    fromfile=str(output), tofile=f"current Chapter {chapter.number} TeX",
                ))
                failed = True
            else:
                print(f"第 {chapter.number} 讲 Beamer 生成稿与当前讲义同步")
        elif current != expected:
            output.parent.mkdir(parents=True, exist_ok=True)
            temporary = output.with_suffix(".tmp")
            temporary.write_text(expected)
            temporary.replace(output)
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
