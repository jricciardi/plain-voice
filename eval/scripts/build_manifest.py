"""Build the generation manifest for the plain-voice stress test.

Every job is one agent call: a model answers a batch of messages (or plays one
multi-turn conversation) under one condition. The full agent prompt is stored
in the manifest so the workflow passes it through unchanged.
"""

import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "prompts"
CONDS = ROOT / "conditions"
RAW = ROOT / "raw"

MODELS = [
    "claude-opus-5.5", "claude-haiku-5.5",
    "gpt-6.1-sol", "gpt-5.5", "gpt-5-mini",
    "gemini-3.8-flash", "gemini-3.7-flash",
    "grok-4.7", "grok-4.5",
    "mai-code-1.1-flash",
]
MAIN_CONDS = ["A-none", "C-skill-v1", "D-placebo", "E-original"]
ABLATIONS = ["F1-no-defaults", "F2-no-punctuation", "F3-no-phrases", "F4-no-vocabulary", "F5-no-structure", "F6-no-framing"]
REPS = 3
BATCHES = 4
ABLATION_CATEGORIES = ["explain", "advice", "email", "feedback", "tech", "howto", "marketing", "factual", "summary", "status_update", "genre_trap", "user_words"]

BATCH_TEMPLATE = """Reply to the {n} messages below and save the replies to one file.

Each message comes from a different person in a separate chat, so treat every message as the start of its own conversation. For each one, write exactly the reply you would send if that person sent you that message in an ordinary chat app, where your reply is shown to them rendered as markdown. Use your natural length, formatting, tone, opening and closing. Rules you have about keeping your own status updates short don't apply to these replies.
{skill_block}
Don't research, don't use the web, and don't read any files. Don't add notes or commentary about the replies.

Create this file: {out_path}

Use exactly this format in the file, with nothing before the first marker:

=== r01 ===
(your reply to message r01)

=== r02 ===
(your reply to message r02)

...and so on through === {last} ===.

When the file is written, respond with only: done

Messages:
{messages}"""

MULTITURN_TEMPLATE = """You're in a chat with one person. Their messages arrive one at a time as files in this folder:
{folder}

For n = 1 to 8, in order:
1. Read turn-n.txt. It holds the person's next message.
2. Write your reply to reply-n.md in the same folder: exactly what you'd send them in an ordinary chat app where replies render as markdown, at your natural length and formatting, responding to the whole conversation so far.

Read turn-(n+1).txt only after reply-n.md is written. Don't list the folder or read ahead: in a real chat the next message doesn't exist yet. Rules you have about keeping your own status updates short don't apply to these replies.
{skill_block}
Don't research or use the web, and don't read any other files. When reply-8.md is written, respond with only: done"""

SKILL_BLOCK = """
The following skill is installed and governs every reply you write. Follow it.

<skill>
{skill}
</skill>
"""


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def skill_block(cond):
    text = (CONDS / f"{cond}.md").read_text().strip()
    return SKILL_BLOCK.format(skill=text) if text else ""


def seeded(*parts):
    return random.Random(int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:12], 16))


def batch_job(set_name, model, cond, rep, b, prompts):
    rids = [f"r{i + 1:02d}" for i in range(len(prompts))]
    out = RAW / set_name / model / cond / f"rep{rep}" / f"batch{b}.txt"
    msgs = "\n".join(f"\n----- message {rid} -----\n{p['text']}\n----- end of message {rid} -----" for rid, p in zip(rids, prompts))
    prompt = BATCH_TEMPLATE.format(n=len(prompts), skill_block=skill_block(cond), out_path=str(out), last=rids[-1], messages=msgs)
    return {
        "id": f"{set_name}:{model}:{cond}:rep{rep}:b{b}", "kind": "batch", "set": set_name, "model": model,
        "cond": cond, "rep": rep, "batch": b, "rids": rids, "prompt_ids": [p["id"] for p in prompts],
        "out_path": str(out), "prompt": prompt,
    }


def main():
    test1 = read_jsonl(PROMPTS / "test1.jsonl")
    dev = read_jsonl(PROMPTS / "dev.jsonl")
    mt = read_jsonl(PROMPTS / "multiturn_test1.jsonl")
    jobs = []

    # Main comparison: same order and batching for every condition within a model and repeat.
    for model in MODELS:
        for rep in range(1, REPS + 1):
            order = test1[:]
            seeded("main", model, rep).shuffle(order)
            size = -(-len(order) // BATCHES)
            batches = [order[i:i + size] for i in range(0, len(order), size)]
            for cond in MAIN_CONDS:
                for b, chunk in enumerate(batches, 1):
                    jobs.append(batch_job("test1", model, cond, rep, b, chunk))

    # Ablations: a fixed 12-prompt subset, one per category, each section removed in turn, plus the full skill on the same batch.
    rng = seeded("ablation-subset")
    subset = []
    for cat in ABLATION_CATEGORIES:
        pool = [p for p in test1 if p["category"] == cat]
        if pool:
            subset.append(rng.choice(pool))
    for model in MODELS:
        order = subset[:]
        seeded("ablation", model).shuffle(order)
        for cond in ["C-skill-v1"] + ABLATIONS:
            jobs.append(batch_job("ablation", model, cond, 1, 1, order))

    # Dev set: baseline and v1, one repeat, for comparison when tuning v2.
    for model in MODELS:
        order = dev[:]
        seeded("dev", model).shuffle(order)
        half = -(-len(order) // 2)
        for cond in ["A-none", "C-skill-v1"]:
            for b, chunk in enumerate([order[:half], order[half:]], 1):
                jobs.append(batch_job("dev", model, cond, 1, b, chunk))

    # Multi-turn conversations, revealed one turn at a time.
    for model in MODELS:
        for cond in ["A-none", "C-skill-v1"]:
            for convo in mt:
                folder = RAW / "multiturn" / model / cond / convo["id"]
                folder.mkdir(parents=True, exist_ok=True)
                for n, turn in enumerate(convo["turns"], 1):
                    (folder / f"turn-{n}.txt").write_text(turn)
                jobs.append({
                    "id": f"multiturn:{model}:{cond}:{convo['id']}", "kind": "multiturn", "set": "multiturn",
                    "model": model, "cond": cond, "rep": 1, "convo": convo["id"], "turns": len(convo["turns"]),
                    "dir": str(folder), "prompt": MULTITURN_TEMPLATE.format(folder=str(folder), skill_block=skill_block(cond)),
                })

    for j in jobs:
        if j["kind"] == "batch":
            Path(j["out_path"]).parent.mkdir(parents=True, exist_ok=True)

    # Run order (doesn't change any job). Tier 1 is everything the human review and the judges
    # need (test-1 repeat 1, main conditions), slowest models first, so review can start early.
    # Tier 2 interleaves models, weighting slow ones toward the front so all models finish together.
    speed = {"claude-opus-5.5": 12, "gpt-6.1-sol": 6, "claude-haiku-5.5": 5, "grok-4.7": 3, "gemini-3.8-flash": 2,
             "gemini-3.7-flash": 2, "grok-4.5": 1.7, "mai-code-1.1-flash": 1, "gpt-5.5": 1, "gpt-5-mini": 1}
    tier1 = [j for j in jobs if j["set"] == "test1" and j["rep"] == 1]
    tier1.sort(key=lambda j: (-speed[j["model"]], MAIN_CONDS.index(j["cond"]), j["batch"]))
    rest = [j for j in jobs if not (j["set"] == "test1" and j["rep"] == 1)]
    seen = {}
    keyed = []
    for j in rest:
        k = seen.get(j["model"], 0)
        seen[j["model"]] = k + 1
        weight = speed[j["model"]] ** 0.5 * (1.5 if j["kind"] == "multiturn" else 1.0)
        keyed.append((k / weight, j["id"], j))
    jobs = tier1 + [j for _, _, j in sorted(keyed, key=lambda x: (x[0], x[1]))]
    (ROOT / "manifest.json").write_text(json.dumps(jobs, ensure_ascii=False))
    (ROOT / "ablation_subset.json").write_text(json.dumps([p["id"] for p in subset]))
    kinds = {}
    for j in jobs:
        kinds[j["set"]] = kinds.get(j["set"], 0) + 1
    print("jobs:", len(jobs), kinds)
    print("ablation subset:", [p["id"] for p in subset])
    sizes = sorted({len(j.get("rids", [])) for j in jobs if j["kind"] == "batch"})
    print("batch sizes:", sizes, "| max prompt chars:", max(len(j["prompt"]) for j in jobs))


if __name__ == "__main__":
    main()
