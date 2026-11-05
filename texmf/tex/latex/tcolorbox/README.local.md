# Local breakable color-stack compatibility patch

`tcbbreakable.code.tex` is based on the installed tcolorbox 6.10.0
(2026/05/28), TeX Live revision 79191. The installed upstream library was
verified byte-for-byte against upstream commit `057ff62` in
https://github.com/T-F-S/tcolorbox before applying development commit
`8ee0b2d` (https://github.com/T-F-S/tcolorbox/pull/374).
The override retains the matching 6.10.0 version guard and the upstream LPPL
license header. Local development checkout:
`/Users/macbook/Documents/tcolorbox-xetex-color-fix`.

The patch adds an opt-in XeTeX/xdvipdfmx backend for `use color stack`.
It uses private driver stack 0 inside captured box content, preserves local
RGB/CMYK/gray colors and converts HSB colors to RGB. Graphics transformations
and PGF pictures restore the private color afterward. Surrounding document
colors continue to use the standard graphics driver. The option remains off
by default; the Wang Jiang entry point enables it with
`\tcbset{breakable,use color stack}`.

Requires xdvipdfmx with `pdfcolorstack` specials (TeX Live 2021 or newer).
Do not enable this backend in a document that independently reserves stack 0.
Validated locally on TeX Live 2026 with XeLaTeX, pdfLaTeX, LuaLaTeX, and
LuaLaTeX + luacolor, plus the handout's teacher/student builds.

Revalidated after the 2026-11-04 TeX Live package refresh with tcolorbox
6.10.0, pdfcol 1.8, and fontspec 2.9h. Each of the four engine configurations
passed 1,544 color-marker checks. With the option disabled, the nine-page
control had identical text, positions, and colors to the official library.
Full-document checks use a separate build copy to avoid simultaneous editor
builds sharing auxiliary/output files.

The project `.latexmkrc` and dual-build script prioritize this `texmf/` tree.
Only the breakable library is overridden; its version must match the loaded
tcolorbox package. Recheck this override when updating TeX Live/tcolorbox.
To revert, remove this local library override and the `use color stack`
activation in the entry point. No chapter-specific color changes are needed.
