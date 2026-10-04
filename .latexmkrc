use Cwd qw(abs_path);
use File::Basename qw(dirname);
use File::Path qw(make_path);

# 优先使用项目内定制的 exam-zh 运行时，同时保留系统 TeX 搜索路径。
my $project_dir = dirname(abs_path(__FILE__));
my $project_texmf = "$project_dir/texmf//";
my $existing_texinputs = $ENV{'TEXINPUTS'} // '';
$ENV{'TEXINPUTS'} = "$project_texmf:$existing_texinputs";

# 普通 latexmk 构建也必须保持项目根目录整洁：成品进入 output/，
# 中间文件进入 build/。命令行显式传入的 -outdir/-auxdir 仍可覆盖这里，
# 供 tools/latex/build-dual.sh 和临时校验构建使用。
$out_dir = "$project_dir/output";
$aux_dir = "$project_dir/build";
make_path($out_dir, $aux_dir);
