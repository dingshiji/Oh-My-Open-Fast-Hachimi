# 示例文件 / Example fixtures

本目录只放可公开提交的最小示例，用于跑通流程和验证脚本，不含软件、声库、模型或历史歌曲。
This directory only holds minimal publishable fixtures for pipeline and I/O checks; no software,
voicebanks, weights or downloaded songs.

## demo.wav

[demo.wav](demo.wav) 是 4 秒、44.1 kHz、双声道 PCM16 的纯程序合成短音型。
它来自本仓库原有的 [notes.json](notes.json)，使用正弦波及二次谐波生成，
不含下载歌曲、真人录音或 teio/manbo 声库采样。开始时间包含 0.13 秒 synthesis lead。
用途是检查音频读取、提取、路径和基础流程，不代表歌声质量或复杂分轨/转谱效果。

运行 python scripts/generate_demo.py 可重建；仅需 Python 标准库。

## marry-has-a-little-lamb.wav

19 秒、44.1 kHz、双声道 PCM16 的示例源音频，与 `projects/mary-had-a-little-lamb/source.wav`
相同，用于演示「源音频 → 分轨 → 转谱」路径。旋律为公版童谣，无 vocals、无歌词。
示例音频的来源与再分发授权由提交者确认；本仓库不因此授予第三方素材的再分发权。

## 钟_哈基米双人带填词.mscz

MuseScore 4 双谱表示例乐谱（李斯特《钟 / La Campanella》双人阿卡贝拉节选改编，含填词）。
A 谱表 = teio 主旋律，B 谱表 = manbo 应答，均单声部、无和弦重叠，可直接用
`python scripts/score.py extract` 解析。用于示意「用户修订乐谱 → 合成」流程，非最终成品。

## 其余配置

mix.demo.json / video.demo.json / captions.json 是完整歌声及视频流程配置，需要自行取得私有素材。

---

The 4-second procedural fixture uses the existing notes.json with sine waves and a
second harmonic, including a 0.13-second lead. It contains no downloaded recording
or voicebank samples. Regenerate it with `python scripts/generate_demo.py` (standard
library only). It tests basic I/O, not singing quality or realistic source separation.

Additional fixtures: `marry-has-a-little-lamb.wav` is the example 19-second source
melody, and `钟_哈基米双人带填词.mscz` is a two-staff example score with lyrics.
Full vocal/video examples require separately obtained assets.
