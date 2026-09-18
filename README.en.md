# Oh My Open Fast Hachimi

[中文](README.md) | **English**

A local workspace for AI coding agents to create duet music videos:
**stem separation → two-part score → teio/manbo Japanese VCV singing → mix → planar character video**.
You can also start from a user-corrected MuseScore score.

This is not an automatic transcription product. Melody selection, lyrics, the second
part and final sound require human review. Defaults: white background, fixed front
camera, 1920×1080 at 30 fps. Voice conversion and spherical/spatial-audio workflows
are outside the scope.

## What is included

Scripts, documentation, configuration templates and one [test WAV](examples/demo.wav).
Applications, voicebanks, 3D assets, neural weights and previous songs are not bundled.

Full singing requires Japanese teio/manbo VCV banks, HifiSampler and PC-NSF-HiFiGAN.
The current synthesis code requires CUDA. Chinese approximated with Japanese phonemes
has an accent; this is not a native Chinese singing model.

Voicebank source: [Bilibili video](https://www.bilibili.com/video/BV1E2J9zJE8c/)
(user-provided; follow the description/author instructions for downloads).
**There is no public download for the prepared duo_stage.blend scene.** Original character models require rigging and mouth UV setup.
A fresh clone cannot reproduce the full video without restoring/rebuilding these assets.
See [asset instructions](assets/DOWNLOAD.txt) and [model downloads](models/DOWNLOAD.txt).

## For coding agents

Read [AGENTS.md](AGENTS.md) and its referenced workflow/schema documents first.
Other harnesses can use [prompts/START_HERE.md](prompts/START_HERE.md).
Claude and Gemini entry points share these same instructions.

Do not upload task audio without consent naming the files and destination.
Do not overwrite user-edited scores.

## Quick test without private assets

[examples/demo.wav](examples/demo.wav) is a 4-second procedural fixture made from the
repository's short note example. It contains no voicebank samples or downloaded recordings.
See [provenance and regeneration](examples/README.md).

Run from the repository root with Python and FFmpeg:

```powershell
python scripts/new_project.py demo-test
python scripts/audio.py extract examples/demo.wav projects/demo-test/00_reference.wav
```

Regenerate the fixture and audit publication candidates using only Python's standard library:

```powershell
python scripts/generate_demo.py
python scripts/audit_release.py
```

This tests basic I/O, not realistic separation or singing quality.

## Set up the full pipeline

1. Follow [software requirements](tools/REQUIREMENTS.txt). Reuse existing installations,
   or put portable copies in ignored [tools/local/](tools/local/README.txt).
   Install requirements.txt and requirements-audio.txt in suitable environments;
   match PyTorch/torchaudio to your GPU.
2. Copy config/tools.example.json to config/local.json and configure absolute executable
   paths. The hifisampler value must point to the code directory containing util/.
3. Obtain voicebanks/characters via [assets/DOWNLOAD.txt](assets/DOWNLOAD.txt) and
   weights via [models/DOWNLOAD.txt](models/DOWNLOAD.txt).
4. Run python scripts/index_voicebanks.py, then python scripts/doctor.py.
   Missing-asset reports are expected before restoration.

With the dependencies and private assets available, run this short example from the root:

```powershell
New-Item -ItemType Directory -Force output/demo01
python scripts/score.py build examples/notes.json output/demo01/demo.mscz --bpm 120
python scripts/synthesize.py examples/notes.json output/demo01/vocals
python scripts/video.py mouths output/demo01/vocals/work/phonemes.json output/demo01/mouths.json
python scripts/audio.py mix examples/mix.demo.json output/demo01/mix.wav
python scripts/video.py captions examples/captions.json output/demo01/captions.ass
python scripts/video.py render examples/video.demo.json output/demo01/preview.mp4
```

JSON paths are relative to the JSON file. The directory-creation command uses PowerShell.
Use the Python interpreter containing the relevant dependencies.

## Start from a song or score

```powershell
python scripts/new_project.py my-song
python scripts/audio.py extract projects/my-song/source.mp4 projects/my-song/00_reference.wav --start 30 --duration 60
python scripts/audio.py separate projects/my-song/00_reference.wav projects/my-song/stems
```

The first separation run may download Demucs weights. Default checkpoints:
stems preview → piano/MuseScore draft → user corrections → voice sample → final mix/video.
Follow an explicit request to go directly to full output.

For an existing corrected score:

```powershell
python scripts/score.py extract projects/my-song/user-edited.mscz projects/my-song/notes.json
python scripts/synthesize.py projects/my-song/notes.json output/my-song/01_vocals
```

A defaults to teio lead; B to manbo answers/countermelody. Note lyrics use pronounceable
Japanese romanization; Chinese captions are separate.
See [workflow](docs/WORKFLOW.md), [schema](docs/ASSET_SCHEMA.md) and [lessons](docs/LESSONS.md)
(these detailed documents are currently in Chinese).

## Layout and publishing

| Path | Purpose | Git |
|---|---|---|
| scripts / docs / prompts | Tools and agent instructions | Included |
| examples | JSON examples and procedural demo.wav | Included |
| tools/REQUIREMENTS.txt, tools/local/README.txt | Software instructions | Included |
| tools/local applications | Optional portable tools | Ignored |
| assets/DOWNLOAD.txt, models/DOWNLOAD.txt | Sources and layout | Included |
| assets/private, model weights | Banks, characters, textures, weights | Ignored |
| config/local.json, config/*.local.txt | Machine configuration | Ignored |
| projects / output | Songs, scores and generated media | Ignored |

Run python scripts/audit_release.py and review git status and the staging area before
publishing. It checks candidates, staged contents and reachable Git history; pattern
scanning cannot guarantee discovery of every secret. **Do not upload an archive of the
entire working directory**, which may contain ignored private projects. Never force-add assets.

See [THIRD_PARTY.md](THIRD_PARTY.md) for sources. No redistribution rights to third-party
assets are granted. A repository code license has not yet been selected; public access
does not itself grant an open-source license. The offline cover editor is
scripts/cover_editor.html; obtain its avatar input separately.
