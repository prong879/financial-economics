#!/bin/zsh

# 构建 Beamer，或为 exam-zh 讲义构建教师版与学生版。
# 不使用 -shell-escape，避免文档类内部再次递归调用 latexmk。

set -eu

mode=serial
case ${1:-} in
    --teacher|--parallel|--student-blank)
        mode=${1#--}
        shift
        ;;
esac

if (( $# != 3 )); then
    print -u2 "用法: build-dual.sh [--teacher|--parallel|--student-blank] <主文档.tex> <输出目录> <辅助目录>"
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

# 王江讲义、单章预览和配套课件共用学生留白版。
is_beamer=false
[[ ${doc_path:A:h} != "$project_root/Beamer" ]] || is_beamer=true
student_suffix=student_version
case ${doc_path:A} in
    "$project_root/金融经济学_王江_讲义及习题.tex"|"$project_root/Beamer/第12—14讲_均值方差偏好_CAPM与APT.tex"|*/wj-ch[0-9][0-9]-preview.tex)
        student_suffix=student
        student_aux_dir="$aux_dir/student-blank"
        ;;
esac
if [[ $mode == student-blank && $student_suffix != student ]]; then
    print -u2 "--student-blank 仅支持王江讲义、单章预览和第 12—14 讲 Beamer。"
    exit 2
elif [[ $is_beamer == true && $student_suffix != student ]]; then
    mode=teacher
fi

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

student_hook=''
if [[ $student_suffix == student ]]; then
    student_hook='\def\WJStudentBlank{}'
fi
if [[ $is_beamer == false ]]; then
    student_hook+='\AddToHook{env/document/before}{\ExamPrintAnswer}'
fi

mkdir -p "$student_aux_dir"
student_args=(
    "${common_args[@]}"
    "-pretex=$student_hook"
    -usepretex
    "-jobname=${doc_name}_${student_suffix}"
    "-outdir=$out_dir"
    "-auxdir=$student_aux_dir"
    "$doc_path"
)

if [[ $mode == student-blank ]]; then
    "$latexmk_bin" "${student_args[@]}"
    exit
fi

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
print -r -- "学生版 $out_dir/${doc_name}_${student_suffix}.pdf"
