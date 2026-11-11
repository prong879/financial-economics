use Cwd qw(abs_path);
use File::Basename qw(dirname);
use File::Path qw(make_path);

# 保持工程根目录只放源文件：成品进入 output/，中间文件进入 build/。
# 命令行显式传入的 -outdir / -auxdir 仍可覆盖这里。
my $project_dir = dirname(abs_path(__FILE__));
$out_dir = "$project_dir/output";
$aux_dir = "$project_dir/build";
make_path($out_dir, $aux_dir);
