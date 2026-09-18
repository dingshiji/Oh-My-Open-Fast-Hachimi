"""Audit worktree candidates, index blobs and reachable history without printing secrets."""
import argparse
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESCRIPTIONS = {"models/readme.md", "models/download.txt", "tools/local/readme.txt"}
EXAMPLE_MEDIA = {
    "examples/demo.wav",
    "examples/marry-has-a-little-lamb.wav",
    "examples/钟_哈基米双人带填词.mscz",
}
PRIVATE = ("assets/private/", "models/", "projects/", "output/", "work/", "cache/",
           "logs/", "tools/local/", ".codex/", ".claude/", ".agents/")
BLOCKED = set("""
.exe .dll .msi .msix .appx .dmg .appimage .so .dylib .key .pem .p12 .pfx
.ckpt .pth .pt .th .onnx .safetensors .npz .wav .mp3 .flac .ogg .m4a .aac .wma
.aiff .mp4 .mkv .mov .webm .avi .zip .rar .7z .tar .gz .glb .gltf .fbx .max
.blend .obj .pmx .pmd .vrm .stl .sf2 .sfz .vmd .bvh .mid .midi .mscz .mscx
""".split())
PATTERNS = [
    ("private key", re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("GitHub token", re.compile(rb"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})")),
    ("API token", re.compile(rb"\bsk-[A-Za-z0-9_-]{24,}")),
    ("AWS access key", re.compile(rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("credential assignment", re.compile(
        rb"""(?i)["']?(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|client[_-]?secret)["']?\s*[:=]\s*["'][^"'\r\n]{8,}["']""")),
    ("URL credentials", re.compile(rb"https?://[^/\s:@]+:[^/\s@]+@")),
    ("personal home path", re.compile(rb"(?:[A-Za-z]:[\\/]+Users[\\/]+|/(?:home|Users)/)[A-Za-z0-9_.-]+")),
]
MAX_BYTES = 20 * 1024 * 1024


def git(root, *args):
    # Per-command trust only for the explicitly selected repository, no global config change.
    return subprocess.check_output(["git", "-c", f"safe.directory={root.as_posix()}",
                                    "-c", f"core.excludesFile={os.devnull}", *args], cwd=root)


def path_issues(name):
    name = name.replace("\\", "/").lower()
    leaf = name.rsplit("/", 1)[-1]
    result = []
    if name not in DESCRIPTIONS and name.startswith(PRIVATE):
        result.append("private directory")
    if name == "config/local.json" or (name.startswith("config/") and name.endswith(".local.txt")):
        result.append("local configuration")
    if (leaf == ".env" or leaf.startswith(".env.")) and leaf != ".env.example":
        result.append("environment file")
    if leaf.startswith(("credentials", "secrets")) and leaf.endswith(".json"):
        result.append("credential file")
    if Path(name).suffix in BLOCKED and name not in EXAMPLE_MEDIA:
        result.append("software/media/model/credential binary")
    return result


def content_issues(data):
    # Scan all candidate bytes, including binary strings; report category only.
    return [label for label, regex in PATTERNS if regex.search(data)]


def audit(root):
    failures = set()
    total = 0
    names = sorted(set(filter(None, git(root, "ls-files", "--cached", "--others",
                                        "--exclude-standard", "-z").decode("utf-8").split("\0"))))

    def inspect(label, name, data, mode=""):
        for reason in path_issues(name):
            failures.add(f"{label}: {name} ({reason})")
        if mode in ("120000", "160000"):
            failures.add(f"{label}: {name} (symlink or submodule requires review)")
        if len(data) > MAX_BYTES:
            failures.add(f"{label}: {name} (over 20 MiB)")
        for reason in content_issues(data):
            failures.add(f"{label}: {name} ({reason})")

    for name in names:
        path = root / name
        if path.is_symlink():
            failures.add(f"worktree: {name} (symlink requires review)")
        elif path.is_file():
            data = path.read_bytes()
            total += len(data)
            inspect("worktree", name, data)

    # Index blobs can differ from the worktree; .gitignore does not untrack them.
    for record in filter(None, git(root, "ls-files", "--stage", "-z").split(b"\0")):
        metadata, raw_name = record.split(b"\t", 1)
        mode, oid, stage = metadata.decode().split()
        name = raw_name.decode("utf-8")
        if stage != "0":
            failures.add(f"index: {name} (unmerged)")
        if mode == "160000":
            inspect("index", name, b"", mode)
        else:
            inspect("index", name, git(root, "cat-file", "blob", oid), mode)

    commits = git(root, "rev-list", "--all").decode().splitlines()
    seen = set()
    for commit in commits:
        # Commit metadata may also reveal personal paths or credential-like strings.
        for reason in content_issues(git(root, "cat-file", "commit", commit)):
            failures.add(f"history commit {commit[:12]} ({reason})")
        for record in filter(None, git(root, "ls-tree", "-r", "-z", commit).split(b"\0")):
            metadata, raw_name = record.split(b"\t", 1)
            mode, kind, oid = metadata.decode().split()
            name = raw_name.decode("utf-8")
            key = (name, oid, mode)
            if key in seen:
                continue
            seen.add(key)
            inspect("history", name, git(root, "cat-file", "blob", oid) if kind == "blob" else b"", mode)
    print(f"Public candidates: {len(names)}; bytes: {total}; reachable commits: {len(commits)}")
    if failures:
        for item in sorted(failures):
            print("FAIL:", item)
        return 1
    print("PASS: no rule matches in candidates, index or reachable history.")
    print("Heuristic scan only; review file provenance and commit author/email before publishing.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    raise SystemExit(audit(args.root.resolve()))
