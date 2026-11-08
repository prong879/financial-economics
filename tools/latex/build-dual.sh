#!/bin/zsh

# 为 exam-zh 讲义构建教师版，或同时生成学生版。
# 不使用 -shell-escape，避免文档类内部再次递归调用 latexmk。

set -eu

mode=serial
case ${1:-} in
    --teacher|--parallel)
        mode=${1#--}
        shift
        ;;
esac

if (( $# != 3 )); then
    print -u2 "用法: build-dual.sh [--teacher|--parallel] <主文档.tex> <输出目录> <辅助目录>"
    exit 2
fi

doc_path=$1
out_dir=$2
aux_dir=$3
doc_name=${doc_path:t:r}
student_aux_dir="$aux_dir/student"
latexmk_bin=/Library/TeX/texbin/latexmk
[[ -x $latexmk_bin ]] || latexmk_bin=latexmk
project_root=${0:A:h:h:h}

# 直接运行脚本时也优先加载项目内的定制 exam-zh。
export TEXINPUTS="$project_root/texmf//:${TEXINPUTS:-}"

mkdir -p "$out_dir" "$aux_dir"

# Cursor 和终端共用辅助目录。等上一轮写完再让 latexmk 判断是否需要重编。
zmodload zsh/system
lock_path="$aux_dir/.build.lock"
: >> "$lock_path"
if ! zsystem flock -t 0 "$lock_path"; then
    print -r -- "等待当前构建完成 $aux_dir"
    zsystem flock "$lock_path"
fi

common_args=(
    -synctex=1
    -interaction=nonstopmode
    -file-line-error
    -xelatex
)

teacher_args=(
    "${common_args[@]}"
    "-outdir=$out_dir"
    "-auxdir=$aux_dir"
    "$doc_path"
)

if [[ $mode == teacher ]]; then
    "$latexmk_bin" "${teacher_args[@]}"
    exit
fi

mkdir -p "$student_aux_dir"
student_hook='\AddToHook{env/document/before}{\ExamPrintAnswer}'
student_args=(
    "${common_args[@]}"
    "-pretex=$student_hook"
    -usepretex
    "-jobname=${doc_name}_student_version"
    "-outdir=$out_dir"
    "-auxdir=$student_aux_dir"
    "$doc_path"
)

if [[ $mode == serial ]]; then
    "$latexmk_bin" "${teacher_args[@]}"
    "$latexmk_bin" "${student_args[@]}"
    exit
fi

teacher_log="$aux_dir/build-teacher.log"
student_log="$student_aux_dir/build-student.log"
print -r -- "教师版日志 $teacher_log"
print -r -- "学生版日志 $student_log"

"$latexmk_bin" "${teacher_args[@]}" > "$teacher_log" 2>&1 &
teacher_pid=$!
"$latexmk_bin" "${student_args[@]}" > "$student_log" 2>&1 &
student_pid=$!

teacher_status=0
student_status=0
wait "$teacher_pid" || teacher_status=$?
wait "$student_pid" || student_status=$?
if (( teacher_status || student_status )); then
    print -u2 "双版构建失败（教师版 $teacher_status，学生版 $student_status），请查看对应日志。"
    exit 1
fi

print -r -- "教师版 $out_dir/$doc_name.pdf"
print -r -- "学生版 $out_dir/${doc_name}_student_version.pdf"
