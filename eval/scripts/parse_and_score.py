"""Parse raw generation outputs into one table of replies, scored with the tell suite."""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import tells  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def _resolve(path):
    """Committed manifests write the eval folder as <eval>; map it to this checkout."""
    return str(path).replace("<eval>", str(ROOT))
FAMILY = {"claude": "Claude", "gpt": "GPT", "gemini": "Gemini", "grok": "Grok", "mai": "MAI"}


def family(model):
    for k, v in FAMILY.items():
        if model.startswith(k):
            return v
    return "Other"


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def parse_batch(path, rids):
    txt = Path(path).read_text()
    parts = re.split(r"^===\s*r0*(\d+)\s*===\s*$", txt, flags=re.M)
    bodies = {int(parts[i]): parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}
    return {rid: bodies.get(int(rid[1:])) for rid in rids}


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=str(ROOT / "manifest.json"))
    ap.add_argument("--out", default=str(ROOT / "results" / "replies.jsonl"))
    args = ap.parse_args()
    prompts = {}
    for name in ("test1", "dev", "test2"):
        for p in read_jsonl(ROOT / "prompts" / f"{name}.jsonl"):
            prompts[p["id"]] = p
    convos = {}
    for name in ("multiturn_test1", "multiturn_test2"):
        convos.update({c["id"]: c for c in read_jsonl(ROOT / "prompts" / f"{name}.jsonl")})
    jobs = json.loads(Path(args.manifest).read_text())
    rows, missing = [], []
    for j in jobs:
        if j["kind"] == "batch":
            if not Path(_resolve(j["out_path"])).exists():
                missing.append(j["id"])
                continue
            got = parse_batch(_resolve(j["out_path"]), j["rids"])
            for pos, (rid, pid) in enumerate(zip(j["rids"], j["prompt_ids"])):
                text = got.get(rid)
                if not text:
                    missing.append(f"{j['id']}#{rid}")
                    continue
                p = prompts[pid]
                rows.append({"set": j["set"], "model": j["model"], "family": family(j["model"]), "cond": j["cond"],
                             "rep": j["rep"], "batch": j["batch"], "position": pos + 1, "prompt_id": pid,
                             "category": p["category"], "source": p["source"], "turn": None, "text": text,
                             **tells.score(text, p)})
        else:
            convo = convos[j["convo"]]
            fr_turn = convo.get("format_request_turn")
            for n in range(1, j["turns"] + 1):
                f = Path(_resolve(j["dir"])) / f"reply-{n}.md"
                if not f.exists() or not f.read_text().strip():
                    missing.append(f"{j['id']}#turn{n}")
                    continue
                text = f.read_text().strip()
                ptxt = convo["turns"][n - 1]
                fmt = {"type": "table"} if fr_turn == n and re.search(r"(?i)table", ptxt) else ({"type": "headers_bullets"} if fr_turn == n else None)
                p = {"text": ptxt, "format_request": fmt}
                rows.append({"set": j["set"], "model": j["model"], "family": family(j["model"]), "cond": j["cond"],
                             "rep": 1, "batch": None, "position": None, "prompt_id": j["convo"], "category": "multiturn",
                             "source": "drafted-gpt", "turn": n, "text": text, **tells.score(text, p)})
    Path(args.out).parent.mkdir(exist_ok=True)
    with open(args.out, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"replies: {len(rows)} | missing: {len(missing)}")
    if missing:
        print("first missing:", missing[:10])


if __name__ == "__main__":
    main()
