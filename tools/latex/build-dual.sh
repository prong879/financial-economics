#!/bin/zsh

# 为 exam-zh 讲义显式生成教师版和学生版。
# 不使用 -shell-escape，避免文档类内部再次递归调用 latexmk。

set -eu

if (( $# != 3 )); then
    print -u2 "用法: build-dual.sh <主文档.tex> <输出目录> <辅助目录>"
    exit 2
fi

doc_path=$1
out_dir=$2
aux_dir=$3
doc_name=${doc_path:t:r}
student_aux_dir="$aux_dir/student"
latexmk_bin=/Library/TeX/texbin/latexmk
project_root=${0:A:h:h:h}

# 直接运行脚本时也优先加载项目内的定制 exam-zh。
export TEXINPUTS="$project_root/texmf//:${TEXINPUTS:-}"

mkdir -p "$out_dir" "$aux_dir" "$student_aux_dir"

common_args=(
    -synctex=1
    -interaction=nonstopmode
    -file-line-error
    -xelatex
)

"$latexmk_bin" \
    $common_args \
    "-outdir=$out_dir" \
    "-auxdir=$aux_dir" \
    "$doc_path"

student_hook='\AddToHook{env/document/before}{\ExamPrintAnswer}'

"$latexmk_bin" \
    $common_args \
    "-pretex=$student_hook" \
    -usepretex \
    "-jobname=${doc_name}_student_version" \
    "-outdir=$out_dir" \
    "-auxdir=$student_aux_dir" \
    "$doc_path"
