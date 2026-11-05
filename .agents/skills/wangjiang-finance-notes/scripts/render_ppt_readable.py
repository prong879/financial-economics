#!/usr/bin/env python3
"""Render a source PPTX for review with process-local Chinese font fallback."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from xml.sax.saxutils import escape


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    parser.add_argument("--soffice", default="soffice")
    args = parser.parse_args()
    source = args.pptx.resolve(strict=True)
    if source.suffix.lower() != ".pptx":
        parser.error("input must be a PPTX")
    root = next(p for p in Path(__file__).resolve().parents if (p / "fonts/SourceHanSerifCN-Regular.ttf").is_file())
    executable = shutil.which(args.soffice)
    if not executable:
        parser.error("soffice not found; locate workspace dependencies or use --soffice")
    destination = args.outdir.resolve()
    if destination == source.parent:
        parser.error("use a review output directory separate from the source directory")
    destination.mkdir(parents=True, exist_ok=True)
    aliases = {
        "Source Han Serif CN": ["宋体", "SimSun", "新宋体", "仿宋", "FangSong", "隶书", "quote-cjk-patch", "serif"],
        "Source Han Sans CN": ["黑体", "SimHei", "微软雅黑", "Microsoft YaHei", "sans-serif"],
        "AR PL KaitiM GB": ["华文楷体", "楷体", "楷体_GB2312", "KaiTi"],
    }
    with tempfile.TemporaryDirectory(prefix="wj-ppt-review-") as temporary:
        work = Path(temporary)
        directories = [root / "fonts", Path("/System/Library/Fonts"), Path.home() / "Library/Fonts"]
        entries = [f"<dir>{escape(str(p))}</dir>" for p in directories if p.is_dir()]
        entries.append(f"<cachedir>{escape(str(work / 'fontcache'))}</cachedir>")
        for replacement, names in aliases.items():
            for name in names:
                entries.append(f"<alias><family>{escape(name)}</family><prefer><family>{replacement}</family></prefer></alias>")
        config = work / "fonts.conf"
        config.write_text('<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">\n<fontconfig>\n' + "\n".join(entries) + "\n</fontconfig>\n")
        env = dict(os.environ, FONTCONFIG_FILE=str(config))
        subprocess.run([executable, f"-env:UserInstallation={(work / 'profile').as_uri()}", "--headless", "--convert-to", "pdf", "--outdir", str(work), str(source)], env=env, check=True)
        rendered = work / (source.stem + ".pdf")
        if not rendered.is_file() or rendered.stat().st_size == 0:
            raise RuntimeError("conversion produced no PDF")
        target = destination / rendered.name
        shutil.copy2(rendered, target)
    print(target)
    print("Conversion finished. Visually verify Chinese text, formulas and graphics before content review.")


if __name__ == "__main__":
    main()
