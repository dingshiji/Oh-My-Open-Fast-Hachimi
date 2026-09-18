# Agent entry point

Read README.md, docs/WORKFLOW.md, docs/ASSET_SCHEMA.md, and docs/LESSONS.md before work. These instructions are harness-independent. CLAUDE.md/GEMINI.md point here; do not maintain conflicting policies.

## Scope
- Make teio + manbo music from a user-provided local song, score, or MIDI. Default is a flat, fixed front camera video. No spherical stage or spatial-audio workflow is included.
- Use original Japanese VCV voicebanks and the neural vocoder. Voice conversion is deliberately outside this repository's scope.
- Reuse external applications first; optional portable copies may live in ignored tools/local/. Read tools/REQUIREMENTS.txt and tools/local/README.txt; configure absolute paths in config/local.json. Never commit software installations.
- No existing wallpaper/background is supplied. Default preview is solid white. Obtain a task-specific user image or create a new background only when requested. Never look for old project backgrounds outside this repository.

## Autonomy and checkpoints
- Treat requests as instructions to do the work; check available files and tools first. Give concise progress reports during long tasks.
- Do not ask repeated permission for already authorized local actions. Uploading audio is opt-in per task: document exact files and destination; previous tasks' permissions do not automatically apply.
- Default pipeline checkpoints: stems preview -> two-staff piano/MuseScore draft -> user corrections -> voice sample -> final mix/video. Follow explicit user requests to go directly to full output; never invent an extra approval gate.
- Never overwrite user-edited scores. Snapshot/hash latest saved MSCZ; each new version goes in a new numbered output folder. Check for autosave discrepancies when relevant.
- If asked for a preview, make the preview first. Do not spend hours making an unreviewed full video.

## Musical requirements
- A=teio lead, B=manbo countermelody/answer by default; duet allocation may use complete phrases/sections, not mechanical line alternation.
- A tied equal-pitch group is one lyric attack. Preserve high notes that carry melody; move a phrase an octave only when musically justified. Do not flatten every note into an artificial range.
- A four-character lyric on one sustained note needs explicit split syllables or note edits. Never silently discard words, notes, tuplets, rests, or user corrections.
- Report inference limits: polyphonic melody transcription may confuse bass/harmonics, F0 confidence is not proof of correctness. Do not claim to have listened when only numerical checks were possible.
- Chinese pronounced using Japanese phonemes has an accent. Explain this honestly. Do not call this a native Chinese singing model.

## Timeline and video
- Canonical note times are seconds excluding the configurable synthesis lead (default .13 s). Mouth/subtitle/mix times are final output seconds. Apply source trims and lead once, explicitly.
- Sustain words across barlines; split quick captions at meaningful phrase boundaries, not arbitrary measure boundaries. Do not prepend singer names unless requested.
- Default 1920x1080/30fps. Use the supplied planar character scene, existing mouth UV controls, and grounded feet. Do not move the mouth mesh away from the face.
- Optional video-sample intros must be separated to vocals when the user excludes their background music.
- Match dance beat and interpolate body movement; don't render every frame by repeating a tiny pose cache without acknowledging motion limitations.
- Check audio finite/peak/duration, both channel timing, video full decode, sample frames, and source/user edits unchanged. Numerical checks are not listening tests.

## Repository hygiene
- No secrets, personal paths, downloaded songs, rendered frames, outputs, or private assets in Git. The sole public WAV exception is the procedural examples/demo.wav fixture. Do not add ignored files with `git add -f`.
- assets/private and model weights are not distributed. Restore using assets/DOWNLOAD.txt and models/DOWNLOAD.txt; never assume they exist locally.
- Update docs/STATE.md for reusable findings only; keep per-song state in ignored projects/<song>/STATE.md.
- At completion give artifact links, what changed, verification, and material limitations. Do not publish/upload/create a GitHub repository unless requested.
