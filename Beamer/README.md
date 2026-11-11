# ESG 与碳风险定价 Beamer 汇报

主文件：ESG与碳风险定价_文献综述汇报.tex。

本目录包含复制的 njust_beamer.sty、cover_background.png 和 fonts/ 字体，编译时请保留这些相对路径。主题和封面来源为高级公司金融项目中的“京东方收购彩虹光电股权_投资决策汇报”。

在本目录使用 TeX Live / XeLaTeX 编译：

    latexmk -xelatex -interaction=nonstopmode -halt-on-error ESG与碳风险定价_文献综述汇报.tex

.latexmkrc 将 PDF 放入 output/，编译中间文件放入 build/。

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

字体的实际版本、SHA256、版权与嵌入许可记录在 `fonts/font-manifest.json`，来源说明见 `fonts/SOURCES.txt`，对应完整许可证随字体保留在 `fonts/LICENSE-*.txt`。这些是模板实际加载的相对路径依赖，不能单独忽略 fonts/；本轮没有更改字体二进制。
