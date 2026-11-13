# ESG 与碳风险定价 Beamer 汇报

主文件：ESG与碳风险定价_文献综述汇报.tex。

本目录包含课件入口、njust_beamer.sty 和 cover_background.png。字体统一从项目根目录的 `fonts/` 加载。主题和封面来源为高级公司金融项目中的“京东方收购彩虹光电股权_投资决策汇报”。

在项目根目录使用 TeX Live / XeLaTeX 编译：

    latexmk -xelatex -interaction=nonstopmode -halt-on-error Beamer/ESG与碳风险定价_文献综述汇报.tex

根目录的 `.latexmkrc` 将 PDF 放入 `output/Beamer/`，编译中间文件放入 `build/Beamer/<课件名>/`。Cursor 的 XeLaTeX 构建使用相同路径。

共 15 页，按上级目录《课堂汇报_15页逐页文案与版式建议.md》重做，保留原 PPT 的页面顺序：

1. 封面
2. 目录
3. 研究背景与核心问题
4. 收益关联、风险暴露与因子价格
5. Pástor：理论机制
6. Bolton：碳排放与收益
7. Lioui：ESG 因子构造与收益
8. Engle：气候新闻对冲
9. 中国市场：ESG 因子与规模异质性
10. Aswani 与 Zhang：排放测量与信息时点
11. Huij 与 Crosignani：碳 β 定价与企业异质性
12. 文献分歧归因
13. 综合判断
14. 九篇参考文献
15. 结束页

正文采用六项固定导航，依据页面内容高亮。第 9 页高亮“中国”，第 10—11 页回到“实证”。书目编号与原 PPT 及逐页文案一致。讲述提示保存在源文件的 Beamer 备注中。

字体的实际版本、SHA256、版权与嵌入许可记录在 `../fonts/font-manifest.json`，来源说明见 `../fonts/SOURCES.txt`，对应完整许可证随字体保留在 `../fonts/LICENSE-*.txt`。讲义与课件共用这些字体文件。

## 金融经济学第 12—14 讲

在项目根目录编译：

    latexmk -xelatex -interaction=nonstopmode -halt-on-error Beamer/第12—14讲_均值方差偏好_CAPM与APT.tex

编译前由 Python 3 读取第 12—14 讲的讲义正文与习题 TeX，在 `build/Beamer/<课件名>/frames/` 生成课件帧。各讲正文、公式、图源、注释性脚注、习题题面及解答以讲义为准。

用 `build-dual.sh --parallel` 可同时构建教师版和学生留白版。只构建学生留白版：

    tools/latex/build-dual.sh --student-blank Beamer/第12—14讲_均值方差偏好_CAPM与APT.tex output/Beamer build/Beamer/第12—14讲_均值方差偏好_CAPM与APT

学生版以 `_student.pdf` 结尾，显示“证明”或“解答”等标题，标题和书写区的总高度沿用讲义的 `blank-vsep`，未指定时留 `5\baselineskip`。

从项目根目录核对讲义与生成帧的内容差异：

    python3 tools/latex/sync-handout.py --check
