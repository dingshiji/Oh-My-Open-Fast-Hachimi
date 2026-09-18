# 测试音频 / Test audio

[demo.wav](demo.wav) 是 4 秒、44.1 kHz、双声道 PCM16 的纯程序合成短音型。
它来自本仓库原有的 [notes.json](notes.json)，使用正弦波及二次谐波生成，
不含下载歌曲、真人录音或 teio/manbo 声库采样。开始时间包含 0.13 秒 synthesis lead。
用途是检查音频读取、提取、路径和基础流程，不代表歌声质量或复杂分轨/转谱效果。

运行 python scripts/generate_demo.py 可重建；仅需 Python 标准库。
其余 mix.demo.json/video.demo.json 是完整歌声及视频流程配置，需要自行取得私有素材。

The 4-second procedural fixture uses the existing notes.json with sine waves and a
second harmonic, including a 0.13-second lead. It contains no downloaded recording
or voicebank samples. Regenerate it with python scripts/generate_demo.py (standard
library only). It tests basic I/O, not singing quality or realistic source separation.
Full vocal/video examples require separately obtained assets.
