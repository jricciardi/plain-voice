"""Build the human review tasks (blind pairs plus pattern-match checks) and the answer key."""

import hashlib
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import tells  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "human"
SEED = 41012

TELL_HELP = {
    "em_dash": "An em dash (\u2014) inside a sentence",
    "answer_label": "A label standing in for a sentence: \"Short answer:\", \"Bottom line:\", \"TL;DR:\"",
    "fragment_reveal": "A question fragment answered right away: \"The catch?\", \"Here's the thing.\"",
    "shorthand": "Slash pairs, arrows or ~ used as shorthand in prose",
    "stock_opener": "A stock opener: \"Certainly!\", \"Of course!\", \"Absolutely\"",
    "praise_opener": "Stock praise up front: \"Great question\", \"Strong start\"",
    "reframe": "Recasting the user's question: \"I'd treat this as a risk decision\"",
    "signpost": "Announcing what's coming instead of saying it: \"Here's how to think about it\"",
    "draft_preamble": "A preamble before a draft: \"Here's a draft:\"",
    "filler_adverb": "A filler or sincerity adverb: genuinely, honestly, really, actually, basically",
    "real_intensifier": "\"Real\" as an intensifier: \"the risk is real\", \"a real signal\"",
    "contrast_formula": "A contrast slogan: \"It's not X, it's Y\", \"less X, more Y\", \"X, not Y\"",
    "slogan": "An \"X beats Y\" or \"X over Y\" slogan",
    "significance": "Significance talk: \"this matters because\", \"worth noting\", \"serves as\"",
    "scare_quotes": "Ironic quotes around an ordinary word",
    "unnamed_authority": "An unsourced authority: \"experts say\", \"studies show\"",
    "disclaimer": "A reflexive disclaimer: \"not financial advice\", \"consult a professional\"",
    "padding": "Message padding: \"I appreciate your flexibility\", \"hope this finds you well\"",
    "offer_closer": "An offer at the end: \"If you want, I can\u2026\", \"Let me know if\u2026\"",
    "hope_closer": "A stock closer: \"Hope this helps\", \"Good luck!\"",
    "recap": "A recap opener: \"In summary\", \"Overall\", \"Ultimately\"",
    "listed_vocab": "A word from the skill's stock-vocabulary list (delve, crucial, landscape, charm\u2026)",
    "md_header": "A markdown header in a reply",
    "bold_header_line": "A bold line used as a header",
    "bold_label": "A bold label in a list: \"**Speed:** fast\"",
    "bold_inline": "Bold text inside a sentence",
    "emoji": "An emoji",
    "horizontal_rule": "A horizontal rule (---)",
    "table": "A table the user didn't ask for",
    "option_menu": "\"Option 1, Option 2\" versions the user didn't ask for",
}


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def main():
    rng = random.Random(SEED)
    replies = [r for r in read_jsonl(ROOT / "results" / "replies.jsonl") if r["set"] == "test1"]
    prompts = {p["id"]: p for p in read_jsonl(ROOT / "prompts" / "test1.jsonl")}
    by = {(r["model"], r["cond"], r["rep"], r["prompt_id"]): r for r in replies}
    models = sorted({r["model"] for r in replies})

    # ---- pairs: 4 per model; alternate (3 vs A, 1 vs D) and (2 vs A, 2 vs D)
    eligible_prompts = [pid for pid, p in prompts.items() if p["category"] != "explicit_format"]
    use_count = defaultdict(int)
    pairs = []
    for mi, model in enumerate(models):
        plan = ["A-none"] * 3 + ["D-placebo"] if mi % 2 == 0 else ["A-none"] * 2 + ["D-placebo"] * 2
        cands = eligible_prompts[:]
        rng.shuffle(cands)
        cats_used = set()
        for other in plan:
            for pid in cands:
                c, o = by.get((model, "C-skill-v1", 1, pid)), by.get((model, other, 1, pid))
                if not c or not o or c["words"] > 450 or o["words"] > 450:
                    continue
                if use_count[pid] >= 2 or prompts[pid]["category"] in cats_used:
                    continue
                use_count[pid] += 1
                cats_used.add(prompts[pid]["category"])
                cands.remove(pid)
                pairs.append({"model": model, "family": c["family"], "prompt_id": pid, "category": prompts[pid]["category"],
                              "skill": c, "other": o, "other_cond": other})
                break
    rng.shuffle(pairs)
    # spread families across the sequence so early stopping stays balanced
    seen_fam = defaultdict(int)
    for p in pairs:
        p["_rank"] = seen_fam[p["family"]]
        seen_fam[p["family"]] += 1
    pairs.sort(key=lambda p: (p["_rank"], rng.random()))

    tasks, key = [], {}
    for i, p in enumerate(pairs, 1):
        tid = f"p{i:03d}"
        skill_left = rng.random() < 0.5
        left, right = (p["skill"], p["other"]) if skill_left else (p["other"], p["skill"])
        tasks.append({"id": tid, "prompt": prompts[p["prompt_id"]]["text"], "left": left["text"], "right": right["text"]})
        key[tid] = {"model": p["model"], "family": p["family"], "prompt_id": p["prompt_id"], "category": p["category"],
                    "comparison": f"C-skill-v1 vs {p['other_cond']}", "skill_side": "left" if skill_left else "right",
                    "repeat_of": None}
    # four repeats with sides swapped, placed in the back half
    for k, src in enumerate(rng.sample(range(len(tasks) // 2), 4), 1):
        s = tasks[src]
        tid = f"p{len(pairs) + k:03d}"
        rep = {"id": tid, "prompt": s["prompt"], "left": s["right"], "right": s["left"]}
        pos = rng.randint(len(tasks) * 2 // 3, len(tasks))
        tasks.insert(pos, rep)
        sk = dict(key[s["id"]])
        sk["skill_side"] = "right" if sk["skill_side"] == "left" else "left"
        sk["repeat_of"] = s["id"]
        key[tid] = sk

    # ---- pattern-match checks: 2 per tell for the 16 most frequent tells in test-1
    found = defaultdict(list)
    for r in replies:
        if r["rep"] != 1:
            continue
        for name, m, start, end in tells.matches(r["text"], prompts[r["prompt_id"]]):
            if start >= 0:
                found[name].append((r, m, start, end))
    top = sorted(found, key=lambda n: -len(found[n]))[:16]
    matches = []
    for name in top:
        for r, m, start, end in rng.sample(found[name], min(2, len(found[name]))):
            t = r["text"]
            matches.append({"tell": name, "tell_help": TELL_HELP.get(name, name), "before": t[max(0, start - 140):start],
                            "match": t[start:end], "after": t[end:end + 140],
                            "_key": {"model": r["model"], "cond": r["cond"], "prompt_id": r["prompt_id"], "start": start}})
    rng.shuffle(matches)
    mtasks = []
    for i, m in enumerate(matches, 1):
        tid = f"m{i:03d}"
        key[tid] = m.pop("_key") | {"tell": m["tell"]}
        mtasks.append({"id": tid, **m})

    doc = {
        "title": "plain-voice human review",
        "sections": [
            {"id": "pairs", "kind": "pair", "title": "Compare replies",
             "instructions": "Each screen shows a message someone sent an AI assistant and two replies to it. For each pair, pick the reply you'd rather receive, then the one that sounds more like stock AI. Go with your gut. If you spot a phrase that reads like an AI tell, select it and press T.",
             "tasks": tasks},
            {"id": "matches", "kind": "match", "title": "Check flagged phrases",
             "instructions": "Each screen shows a phrase the counting script flagged, with the pattern it was looking for. Press Y if it's a real example of that pattern, N if it's a false alarm, U if unsure.",
             "tasks": mtasks},
        ],
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "tasks.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1))
    (OUT / "answer_key.json").write_text(json.dumps(key, ensure_ascii=False, indent=1))
    fams = defaultdict(int)
    for p in pairs:
        fams[(p["family"], p["other_cond"])] += 1
    print(f"pairs: {len(tasks)} ({len(pairs)} + 4 repeats) | matches: {len(mtasks)}")
    print("by family and comparison:", dict(fams))
    print("categories:", dict(sorted(defaultdict(int, {c: sum(1 for p in pairs if p['category'] == c) for c in {p['category'] for p in pairs}}).items())))
    print("tasks sha256:", hashlib.sha256((OUT / "tasks.json").read_bytes()).hexdigest()[:16])


if __name__ == "__main__":
    main()
