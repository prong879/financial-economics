use Cwd qw(abs_path);
use File::Basename qw(dirname);

# 优先使用项目内定制的 exam-zh 运行时，同时保留系统 TeX 搜索路径。
my $project_dir = dirname(abs_path(__FILE__));
my $project_texmf = "$project_dir/texmf//";
my $existing_texinputs = $ENV{'TEXINPUTS'} // '';
$ENV{'TEXINPUTS'} = "$project_texmf:$existing_texinputs";
