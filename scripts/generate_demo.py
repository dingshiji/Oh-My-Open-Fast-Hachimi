"""Generate the public procedural fixture with Python's standard library."""
import json
import math
import struct
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SR = 44100
DURATION = 4.0
LEAD = 0.13


def main():
    parts = json.loads((ROOT / "examples/notes.json").read_text(encoding="utf-8"))
    samples = [0.0] * round(SR * DURATION)
    for notes in parts:
        for note in notes:
            start = round((note["start"] + LEAD) * SR)
            count = round((note["end"] - note["start"]) * SR)
            frequency = 440 * 2 ** ((note["pitch"] - 69) / 12)
            for i in range(count):
                envelope = min(1, i / (SR * .01), (count - 1 - i) / (SR * .03))
                t = i / SR
                value = .28 * envelope * (math.sin(2 * math.pi * frequency * t)
                                         + .2 * math.sin(4 * math.pi * frequency * t))
                samples[start + i] += value
    assert all(math.isfinite(x) and abs(x) < 1 for x in samples)
    pcm = b"".join(struct.pack("<hh", round(x * 32767), round(x * 32767)) for x in samples)
    target = ROOT / "examples/demo.wav"
    with wave.open(str(target), "wb") as out:
        out.setparams((2, 2, SR, len(samples), "NONE", "not compressed"))
        out.writeframes(pcm)
    print(f"{target.name}: {DURATION}s, {SR} Hz, stereo PCM16, peak {max(map(abs, samples)):.4f}")


if __name__ == "__main__":
    main()
