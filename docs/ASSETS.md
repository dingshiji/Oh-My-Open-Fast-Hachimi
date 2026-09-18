# 素材恢复 / Restoring assets

仓库仅包含代码、说明和一个纯程序生成的测试 WAV。实际声库、3D 模型、贴图、头像和权重不分发。

- [声库、角色来源与目录结构](../assets/DOWNLOAD.txt)
- [神经声码器与 Demucs 权重](../models/DOWNLOAD.txt)
- [软件要求](../tools/REQUIREMENTS.txt)与[本地软件目录](../tools/local/README.txt)
- [第三方来源与边界](../THIRD_PARTY.md)

取得原始声库后运行 python scripts/index_voicebanks.py，再运行 python scripts/doctor.py。
缺少 teio/manbo 声库或已整理场景时无法完整复现歌声/视频；不能用其他素材悄悄替换并宣称相同效果。

A clone does not include voicebanks, characters or weights. Follow the linked download
instructions. The voicebank source video is listed in assets/DOWNLOAD.txt; its attachments were not verified.
There is no public prepared-scene download.
Raw character downloads require additional rigging and mouth UV setup. The included
procedural audio fixture works without those private assets.
