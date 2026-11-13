use Cwd qw(abs_path);
use File::Spec;
use File::Basename qw(basename dirname);
use File::Path qw(make_path);
use File::Compare qw(compare);
use Digest::SHA;
use File::Temp qw(tempfile);
use Encode qw(encode_utf8);
use utf8;

# 优先使用项目内定制的 exam-zh 运行时，同时保留系统 TeX 搜索路径。
my $project_dir = dirname(abs_path(__FILE__));
my $project_texmf = "$project_dir/texmf//";
my $existing_texinputs = $ENV{'TEXINPUTS'} // '';
$ENV{'TEXINPUTS'} = "$project_texmf:$existing_texinputs";

# 按入口设置默认输出位置。显式 -outdir / -auxdir 仍可覆盖。
$out_dir = "$project_dir/output";
$aux_dir = "$project_dir/build";
my $course_slides = encode_utf8('第12—14讲_均值方差偏好_CAPM与APT.tex');
my @sources = grep { !/^-/ && /\.tex\z/ } @ARGV;
if (@sources == 1) {
    my $source = File::Spec->rel2abs($sources[0]);
    my $name = basename($source);
    $name =~ s/\.tex\z//;
    if (dirname($source) eq "$project_dir/Beamer") {
        $out_dir .= "/Beamer";
        $aux_dir .= "/Beamer/$name";
        if (basename($source) eq $course_slides) {
            system('python3', "$project_dir/tools/latex/sync-handout.py") == 0
                or die "Beamer frame generation failed\n";
        }
    } else {
        $aux_dir .= "/$name";
    }
}
make_path($out_dir, $aux_dir);

# 记录独立图的共用样式与字体。图面代码由 Memoize 自己校验。
my $wj_handout = encode_utf8('金融经济学_王江_讲义及习题.tex');
my $is_wj_build = sub {
    my ($source) = @_;
    my $name = basename($source);
    return $name eq $wj_handout || $name =~ /\Awj-ch[0-9]+-preview\.tex\z/;
};

push @generated_exts, 'mmz';

add_hook('compile_begin', sub {
    my %build = @_;
    return 0 unless $is_wj_build->($build{'tex_file'});

    my $digest = Digest::SHA->new(256);
    for my $file (sort "$project_dir/.latexmkrc", "$project_dir/$wj_handout",
                  glob("$project_dir/tex/_shared/*.tex"),
                  glob("$project_dir/fonts/*.ttf"),
                  glob("$project_dir/texmf/tex/latex/*/*")) {
        next unless -f $file;
        open my $input, '<:raw', $file or die "Read $file: $!";
        $digest->add($file, "\0")->addfile($input);
    }

    my $dir = $build{'aux_dir'} || '.';
    make_path($dir);
    my $context = "$dir/wj-figure-cache-context.tex";
    my ($fh, $temp) = tempfile('wj-context-XXXXXX', DIR => $dir, UNLINK => 1);
    print {$fh} "\\def\\WJFigureCacheContext{" . $digest->hexdigest . "}\n";
    close $fh or die "Write $temp: $!";
    if (compare($temp, $context) == 0) {
        unlink $temp;
    } else {
        rename $temp, $context or die "Publish $context: $!";
    }
    return 0;
});

# 从本轮 XDV 提取 Memoize 的附页，最终 PDF 只在重新排版后写出。
# 用 TeX Live 自带的 xdvipdfmx，无需额外的 PDF 处理库。
add_hook('after_xlatex_analysis', sub {
    my %build = @_;
    return 0 unless $is_wj_build->($build{'tex_file'}) && $build{'rule'} eq 'xelatex';
    my $base = $build{'base'};
    my $dir = $build{'aux_dir'} || '.';
    my $mmz = "$dir/$base.mmz";
    return 0 unless -f $mmz && test_gen_file_time($mmz);
    my $xdv = $build{'dest'};
    return 0 unless $xdv =~ /\.xdv\z/ && -f $xdv && test_gen_file_time($xdv);

    open my $record, '<', $mmz or die "Read $mmz: $!";
    my $count = 0;
    while (<$record>) {
        next unless /^\\mmzNewExtern\s/;
        my ($name, $page) = /\A\\mmzNewExtern\s+\{(\Q$base\E\.[[:xdigit:]-]+\.pdf)\}\s*\{([1-9][0-9]*)\}/
            or die "Invalid figure cache record in $mmz: $_";
        my $pdf = "$dir/$name";
        rdb_ensure_files_here($pdf);
        my ($fh, $temp) = tempfile('wj-figure-XXXXXX', DIR => $dir, SUFFIX => '.pdf', UNLINK => 1);
        close $fh or die "Close $temp: $!";
        system('xdvipdfmx', '-q', '-E', '-s', $page, '-o', $temp, $xdv) == 0 && -s $temp
            or die "Extract figure $name from page $page of $xdv";
        rename $temp, $pdf or die "Publish $pdf: $!";
        $count++;
    }
    print "WJ figure cache: generated $count PDF(s)\n" if $count;
    return 0;
});
