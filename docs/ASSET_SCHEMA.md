# 数据与路径约定

所有脚本从任意 cwd 均以脚本位置找仓库根，但示例命令约定在根执行。JSON 内路径相对 JSON 所在目录（音频混音、视频任务）。config/local.json 中外部工具建议绝对路径，禁止写入公开配置。

## notes.json
两个数组，依次 teio/manbo。按 start 排序，单轨无重叠，时间单位秒；不含 .13 秒 synthesis lead。
`[{start:0,end:0.5,pitch:67,lyric:"man",bar:1,phonemes:["ma","n"]}, ...]`
以上只是字段示意；完整合法 JSON 见 examples/notes.json。pitch 是 MIDI 整数；phonemes 可选。bar 仅用于标注。
未发音延音用元音（例如 a），不是重复原辅音。音符内切分在 configure 中实现。全曲变速需保留秒时间，不把每首歌强制按一个 BPM。

## phonemes 与 mouth_events
合成自动产生 phonemes.json，含每一音素起止、alias、采样位置、目标 pitch。
mouth_events 是两个数组，字段 start/end/vowel（a i u e o closed），时间已经加 lead。曼波使用张口/圆口/闭口三类，帝王使用六类。不要再给 render 里的嘴型重复加 lead。

## captions
数组：`{"start":0.13,"end":1.2,"text":"哈基米"}`。text 是显示的中文/日语，不一定等于音源罗马音。换行用 JSON `\n`。时间来自最终音频。

## mix
`duration` 秒、`fade_out` 秒；tracks 中 file、offset（可负）、trim_start、target_lufs（可省略）、gain（线性倍数）、pan（-1..1，单声道人声有效）。源伴奏裁切、前奏插入和 .13 秒起音余量只应用一次。

## video job
duration、fps、width、height、bpm、lead、frames、audio、mouth_events、subtitles（可选）、background（可选）、color（无背景时）、encoder、fade_out。
原曲去人声伴奏不自动从 13 分钟原片中挑片；由用户选段和 mix 配置负责。帧目录应为新版本独有，避免覆盖。

默认视频角色由程序生成，无外部场景输入。mouth_events 仍为两个声部，允许空数组；事件必须按起点排序、不重叠。duration/fps/bpm 为正数，画面宽高为偶数整数。
