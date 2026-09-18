本目录供 code agent 按需放置便携软件；Git 只保留本说明。
优先复用已安装软件或统一外部工具目录；不要重复下载，不要提交安装包。
软件、官方来源及已测版本见 ../REQUIREMENTS.txt。
示例结构（均不随 Git 分发，下载包实际层级可能不同）：
  tools/local/blender/blender.exe
  tools/local/musescore/bin/MuseScore4.exe
  tools/local/ffmpeg/bin/ffmpeg.exe
  tools/local/ffmpeg/bin/ffprobe.exe
  tools/local/hifisampler/util/nsf_hifigan.py
  tools/local/hifisampler/util/wav2mel.py
复制 config/tools.example.json 为 config/local.json，填实际程序的绝对路径；
hifisampler 指向包含 util/ 的目录。不要使用 git add -f。

Local portable applications may be placed here by a code agent. Only this file is public.
Reuse existing installations first. See ../REQUIREMENTS.txt for upstream sources.
Configure absolute executable paths in config/local.json; hifisampler points to the
code directory containing util/. Package layouts vary. Never force-add local tools.
