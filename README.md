# 金融经济学

王江《金融经济学》讲义与课后习题，以及熊和平《金融经济学》本章小结、章末习题和参考解答。由 dk431 项目独立迁移，正文与现有排版保留。

## 编译

需要 XeLaTeX、latexmk 和包含文档所需宏包的 TeX Live / MacTeX。中文字体以及定制 exam-zh 运行时随仓库提供。
在仓库根目录执行：

```sh
latexmk -xelatex 金融经济学_王江_讲义及习题.tex
latexmk -xelatex 金融经济学_熊和平_习题.tex
```

PDF 写入 `output/`，中间文件写入 `build/`。

教师版和学生版：

```sh
tools/latex/build-dual.sh 金融经济学_王江_讲义及习题.tex output build/金融经济学_王江_讲义及习题
tools/latex/build-dual.sh 金融经济学_熊和平_习题.tex output build/金融经济学_熊和平_习题
```

王江仅习题版：

```sh
latexmk -xelatex -usepretex -pretex='\def\WJExercisesOnly{}' -jobname=金融经济学_王江_exercises_only 金融经济学_王江_讲义及习题.tex
```

## 目录

- `tex/金融经济学_王江/`：第 2—15 章的讲义和习题，共 28 个文件。
- `tex/金融经济学_熊和平/`：第 1—15 章的小结、习题和布朗运动附录，共 31 个文件。
- `tex/_shared/`：从 431 复制的独立排版主题，保留原有命令与封面。
- `texmf/`：项目定制的 exam-zh 运行时与许可说明。
- `fonts/`：当前排版实际使用的 6 个字体。
- `tools/latex/`：构建脚本，以及历史拆分/编号维护工具。历史工具会写入源码，正常编译无需运行。
- `docs/migration.md`、`docs/migration-manifest.json`：迁移来源和文件哈希。

## 本地参考资料

教材、参考答案 PDF、勘误 Word、熊和平原图和历史参考题库归入本地 `references/`，不纳入 Git。生成 PDF、图片和缓存同样不纳入仓库。
正式文档编译不读取这些参考资料；需要核对题目时再使用本地原件。

旧 Git 历史保留在 dk431；本仓库从迁移基线开始独立维护。迁移只验证文件完整性和编译可复现性，不代表重新核验每道题的内容。
