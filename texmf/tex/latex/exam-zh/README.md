# exam-zh 运行时

从 dk431 复制的项目定制版本。上游：https://gitee.com/xkwxdyy/exam-zh 。
这些文件采用 LPPL 1.3c，许可全文见 LICENSE。
`.latexmkrc` 与构建脚本将本目录优先加入 TEXINPUTS。

## 本地数学宏包兼容约定（2026-11-04）

`exam-zh-font.sty` 在 `unicode-math` 之前加载 `mathtools`，避免主入口在
文档类之后加载 `mathtools` 时产生顺序警告。保留现有符号选择：方括注采用
`mathtools`，重名的冒号命令采用 `unicode-math`。对应两项兼容性通知定向
改为日志信息，其他警告不受影响。这是本项目的配置选择，不应直接作为
上游模板的默认策略提交。原有中文括号延迟测宽补丁继续保留。
