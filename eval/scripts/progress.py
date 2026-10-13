"""Report generation progress and clear output paths that agents created as directories."""

import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _resolve(path):
    """Committed manifests write the eval folder as <eval>; map it to this checkout."""
    return str(path).replace("<eval>", str(ROOT))


def done(j):
    if j["kind"] == "multiturn":
        return all(os.path.isfile(os.path.join(_resolve(j["dir"]), f"reply-{n}.md")) for n in range(1, j["turns"] + 1))
    p = _resolve(j["out_path"])
    if not os.path.isfile(p):
        return False
    got = set(int(x) for x in re.findall(r"^===\s*r0*(\d+)\s*===\s*$", open(p, errors="replace").read(), flags=re.M))
    return all(int(r[1:]) in got for r in j["rids"])


def main():
    manifest = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "manifest.json")
    jobs = json.load(open(manifest))
    for j in jobs:
        paths = [_resolve(j["out_path"])] if j["kind"] == "batch" else [os.path.join(_resolve(j["dir"]), f"reply-{n}.md") for n in range(1, j["turns"] + 1)]
        for p in paths:
            if os.path.isdir(p) and not os.listdir(p):
                os.rmdir(p)
                print("removed empty directory at output path:", p)
            elif os.path.isdir(p):
                print("WARNING: non-empty directory at output path:", p)
    d = [j for j in jobs if done(j)]
    sets = Counter(j["set"] for j in jobs)
    dsets = Counter(j["set"] for j in d)
    print(f"done {len(d)}/{len(jobs)} | " + " | ".join(f"{s} {dsets[s]}/{n}" for s, n in sets.items()))
    tier1 = [j for j in jobs if j["set"] == "test1" and j["rep"] == 1]
    if tier1:
        print(f"test-1 repeat 1: {sum(done(j) for j in tier1)}/{len(tier1)}; remaining by model: {dict(Counter(j['model'] for j in tier1 if not done(j)))}")
    left = Counter(j["model"] for j in jobs if not done(j))
    print("all remaining by model:", dict(left.most_common()))


if __name__ == "__main__":
    main()
