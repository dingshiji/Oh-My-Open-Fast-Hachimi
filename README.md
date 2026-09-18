# Oh My Open Fast Hachimi

**中文** | [English](README.en.md)

给 AI 编程代理使用的本地双人哈基米音乐视频工作台：**分轨 → 双声部乐谱 → teio/manbo 日语 VCV 歌声 → 混音 → 平面角色视频**。也支持直接使用用户修订后的 MuseScore 乐谱。

这不是无需判断的一键转谱工具。旋律识别、歌词对齐、B 声部编配和最终听感仍需人工试听确认。默认白底、固定正面镜头、1920×1080 / 30 fps；不包含换声或球面/空间音频流程。

## TLDR

-   用 Codex / Claude Code / OpenCode 或者任何类似的东西打开这个项目，让 AI 配好环境
-   用一个音频制作出 mscz 文件，这是 Musescore 的乐谱格式; 你可以手动修改，或者在任何你想改的地方旁边加上文本描述。
-   音频听起来不错之后就可以让 AI 自动制作出视频了

## 先知道这些

- 仓库只分发脚本、文档、配置模板和 [examples](examples/) 下少量示例文件（程序合成测试音频、示例源音频、用户改编的双人乐谱）；不含软件本体、声库、3D 模型、模型权重或历史歌曲。
- 完整歌声需要 teio/manbo 日语 VCV 声库、HifiSampler 和 PC-NSF-HiFiGAN；当前合成代码需要 CUDA。日语音素近似中文会有口音，并非原生中文歌声模型。
- 声库来源见[作者视频](https://www.bilibili.com/video/BV1E2J9zJE8c/)（用户提供，下载入口以简介/作者说明为准）。**整理后的 duo_stage.blend 无公开下载。** 原始模型仍需绑定和嘴型设置，因此下载本仓库不能直接复现完整视频。见[素材说明](assets/DOWNLOAD.txt)。
- 软件可复用已有安装，也可放在被忽略的 [tools/local/](tools/local/README.txt)。首次使用先读 [tools/REQUIREMENTS.txt](tools/REQUIREMENTS.txt)。

## 给 code agent 的入口

先读 [AGENTS.md](AGENTS.md)，再读其列出的工作流与格式约定。其他 harness 可使用 [prompts/START_HERE.md](prompts/START_HERE.md)。Claude/Gemini 的入口也指向同一套约定。

不要自动上传任务音频；远程转谱需要用户对具体文件与目的站点的授权。不要覆盖用户修订的乐谱。

## 快速测试：无需声库或角色

内附 [examples/demo.wav](examples/demo.wav)：4 秒原创短音型的程序合成音频，不含声库或下载录音。来源与重建方法见 [examples/README.md](examples/README.md)。

在仓库根目录运行（Python + FFmpeg）：

```powershell
python scripts/new_project.py demo-test
python scripts/audio.py extract examples/demo.wav projects/demo-test/00_reference.wav
```

只用 Python 标准库即可重建示例并检查发布候选文件：

```powershell
python scripts/generate_demo.py
python scripts/audit_release.py
```

该音频适合基础读写与流程测试，不代表真实歌声或复杂分轨质量。

## 配置完整流程

1. 按[软件清单](tools/REQUIREMENTS.txt)安装 Python、FFmpeg/ffprobe、Blender、MuseScore 和相应 Python 依赖。基础依赖见 requirements.txt；音频依赖见 requirements-audio.txt。PyTorch/torchaudio 需匹配显卡环境。
2. 复制 config/tools.example.json 为 config/local.json；填入实际程序的绝对路径。hifisampler 指向含 util/ 的代码目录。
3. 按[声库与角色说明](assets/DOWNLOAD.txt)和[权重说明](models/DOWNLOAD.txt)取得素材并还原目录。
4. 运行 python scripts/index_voicebanks.py 重建声库索引，再运行 python scripts/doctor.py 检查环境。缺少素材时报告缺失是正常的。

使用具有所需依赖的 Python，在根目录运行完整短例：

```powershell
New-Item -ItemType Directory -Force output/demo01
python scripts/score.py build examples/notes.json output/demo01/demo.mscz --bpm 120
python scripts/synthesize.py examples/notes.json output/demo01/vocals
python scripts/video.py mouths output/demo01/vocals/work/phonemes.json output/demo01/mouths.json
python scripts/audio.py mix examples/mix.demo.json output/demo01/mix.wav
python scripts/video.py captions examples/captions.json output/demo01/captions.ass
python scripts/video.py render examples/video.demo.json output/demo01/preview.mp4
```

示例 JSON 的路径相对其自身目录；不要随意挪动。上面的目录创建命令适用于 PowerShell。

## 从歌曲或乐谱开始

```powershell
python scripts/new_project.py my-song
python scripts/audio.py extract projects/my-song/source.mp4 projects/my-song/00_reference.wav --start 30 --duration 60
python scripts/audio.py separate projects/my-song/00_reference.wav projects/my-song/stems
```

分轨首次运行可能下载 Demucs 权重。默认检查点：分轨试听 → 双谱表钢琴/MuseScore 草稿 → 用户修订 → 歌声短例 → 最终混音/视频。用户明确要求直出整片时按其要求执行。

已有修订乐谱：

```powershell
python scripts/score.py extract projects/my-song/user-edited.mscz projects/my-song/notes.json
python scripts/synthesize.py projects/my-song/notes.json output/my-song/01_vocals
```

A 默认 teio 主旋律，B 默认 manbo 对答。音符 lyric 使用可发音的日语罗马音，中文字幕单独存储。完整说明见[工作流](docs/WORKFLOW.md)、[数据格式](docs/ASSET_SCHEMA.md)与[经验](docs/LESSONS.md)。

## 目录与发布

| 目录/文件 | 内容 | Git |
|---|---|---|
| scripts / docs / prompts | 工具与代理约定 | 提交 |
| examples | JSON 示例、程序生成的 demo.wav | 提交 |
| tools/REQUIREMENTS.txt、tools/local/README.txt | 软件说明 | 提交 |
| tools/local 下的软件 | 可选便携工具 | 忽略 |
| assets/DOWNLOAD.txt、models/DOWNLOAD.txt | 来源和恢复目录 | 提交 |
| assets/private、模型权重 | 声库、角色、贴图、权重 | 忽略 |
| config/local.json、config/*.local.txt | 本机路径与配置 | 忽略 |
| projects / output | 歌曲、乐谱、渲染产出 | 忽略 |

发布前运行 python scripts/audit_release.py，再核对 git status 与暂存区。检查包含候选文件、暂存内容和可达 Git 历史；规则扫描无法保证发现所有秘密。**不要把整个工作目录打包上传**，其中可能还有被忽略的个人项目。不要 git add -f 私有素材。

第三方来源见 [THIRD_PARTY.md](THIRD_PARTY.md)。仓库不授予第三方素材的再分发权；目前未选择仓库代码许可证，公开可读不等于获得开源许可。离线封面工具见 scripts/cover_editor.html，头像需自行取得。
