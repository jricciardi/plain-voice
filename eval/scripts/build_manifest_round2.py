"""Build the round-2 generation manifest: skill v2 against v1 and no skill on sealed test-2."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_manifest as bm  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CONDS = ["A-none", "C-skill-v1", "H-skill-v2"]
MT_CONDS = ["A-none", "H-skill-v2"]
REPS = 2
BATCHES = 3


def main():
    test2 = bm.read_jsonl(bm.PROMPTS / "test2.jsonl")
    convos = bm.read_jsonl(bm.PROMPTS / "multiturn_test2.jsonl")
    jobs = []
    for model in bm.MODELS:
        for rep in range(1, REPS + 1):
            order = test2[:]
            bm.seeded("round2", model, rep).shuffle(order)
            size = -(-len(order) // BATCHES)
            batches = [order[i:i + size] for i in range(0, len(order), size)]
            for cond in CONDS:
                for b, chunk in enumerate(batches, 1):
                    jobs.append(bm.batch_job("test2", model, cond, rep, b, chunk))
    for model in bm.MODELS:
        for cond in MT_CONDS:
            for convo in convos:
                folder = bm.RAW / "multiturn2" / model / cond / convo["id"]
                folder.mkdir(parents=True, exist_ok=True)
                for n, turn in enumerate(convo["turns"], 1):
                    (folder / f"turn-{n}.txt").write_text(turn)
                jobs.append({"id": f"multiturn2:{model}:{cond}:{convo['id']}", "kind": "multiturn", "set": "multiturn2",
                             "model": model, "cond": cond, "rep": 1, "convo": convo["id"], "turns": len(convo["turns"]),
                             "dir": str(folder), "prompt": bm.MULTITURN_TEMPLATE.format(folder=str(folder), skill_block=bm.skill_block(cond))})
    for j in jobs:
        if j["kind"] == "batch":
            Path(j["out_path"]).parent.mkdir(parents=True, exist_ok=True)
    speed = {"claude-opus-5.5": 12, "gpt-6.1-sol": 6, "claude-haiku-5.5": 5, "grok-4.7": 3, "gemini-3.8-flash": 2,
             "gemini-3.7-flash": 2, "grok-4.5": 1.7, "mai-code-1.1-flash": 1, "gpt-5.5": 1, "gpt-5-mini": 1}
    jobs.sort(key=lambda j: (j["rep"], -speed[j["model"]] * (1.5 if j["kind"] == "multiturn" else 1), j["id"]))
    (ROOT / "manifest_round2.json").write_text(json.dumps(jobs, ensure_ascii=False))
    kinds = {}
    for j in jobs:
        kinds[j["set"]] = kinds.get(j["set"], 0) + 1
    print("round-2 jobs:", len(jobs), kinds)


if __name__ == "__main__":
    main()
