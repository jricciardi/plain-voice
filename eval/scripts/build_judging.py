"""Build the judging manifest: pairwise judges, fidelity/format graders and pattern-match labelers."""

import json
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import tells  # noqa: E402
from build_human_tasks import TELL_HELP  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
JUDGE_DIR = ROOT / "judgments"
SEED = 7712
JUDGES = {"GPT": "gpt-6.1-sol", "Gemini": "gemini-3.8-flash", "Claude": "claude-opus-5.5", "Grok": "grok-4.7"}
LABELERS = ["gpt-6.1-sol", "gemini-3.8-flash"]
PAIR_BATCH, GRADE_BATCH, LABEL_BATCH = 15, 12, 50

PAIR_PROMPT = """You're evaluating replies written by AI chat assistants. Each item below shows a message someone sent to an assistant, then two replies to it, Reply 1 and Reply 2. Judge each item on its own, and don't let reply order or length alone decide.

Answer two questions for every item:
- prefer: Which reply would you rather receive if you had sent this message? Weigh usefulness, accuracy, completeness and how it reads. Answer "1", "2" or "tie".
- ai_like: Which reply sounds more like stock AI writing, the recognizable house style of chatbots? Use your own judgment of what makes writing read as machine-generated. Answer "1", "2" or "same".
Also give a reason in one short sentence.

Don't use the web or read any files. Write your answers as JSON Lines to this file (create it):
{out_path}

One line per item, with exactly these keys:
{{"item": "<item id>", "prefer": "1" | "2" | "tie", "ai_like": "1" | "2" | "same", "reason": "<one short sentence>"}}

When the file has one line for every item, respond with only: done

Items:
{items}"""

GRADE_PROMPT = """You're checking replies written by AI chat assistants against what the user gave them. Each item shows the user's message, a numbered list of required facts (when the user supplied facts the reply must keep), a format request (when the user explicitly asked for one), and the reply.

For every item:
- facts: one entry per required fact, in order: "present" (the reply states it, in any wording), "missing" (it's absent) or "wrong" (stated incorrectly). Use an empty list when there are no required facts.
- invented: specific details in the reply that the user didn't provide and that a reader could take as fact, such as new names, numbers, dates, deadlines, commitments or events. Don't list general advice, placeholders like [Your Name], or ordinary wording. Use an empty list if there are none.
- format: "yes", "partly" or "no" for whether the reply follows the format request, or "n/a" when there isn't one.

Don't use the web or read any files. Write your answers as JSON Lines to this file (create it):
{out_path}

One line per item, with exactly these keys:
{{"item": "<item id>", "facts": ["present", "..."], "invented": ["..."], "format": "yes" | "partly" | "no" | "n/a"}}

When the file has one line for every item, respond with only: done

Items:
{items}"""

LABEL_PROMPT = """A script flags phrases in AI-written replies that match named writing patterns. For each item, decide whether the text between [[ and ]] is a real example of the named pattern in its context.

Answer "yes" for a real example, "no" for a false alarm (the text matches mechanically but isn't that pattern: for example a quotation of the user's words, a literal meaning, a proper name, or a format the user asked for), or "unsure".

Don't use the web or read any files. Write your answers as JSON Lines to this file (create it):
{out_path}

One line per item, with exactly these keys:
{{"item": "<item id>", "verdict": "yes" | "no" | "unsure"}}

When the file has one line for every item, respond with only: done

Items:
{items}"""


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def chunks(xs, n):
    return [xs[i:i + n] for i in range(0, len(xs), n)]


def main():
    rng = random.Random(SEED)
    replies = [r for r in read_jsonl(ROOT / "results" / "replies.jsonl") if r["set"] == "test1"]
    prompts = {p["id"]: p for p in read_jsonl(ROOT / "prompts" / "test1.jsonl")}
    by = {(r["model"], r["cond"], r["rep"], r["prompt_id"]): r for r in replies}
    human_key = json.loads((ROOT / "human" / "answer_key.json").read_text())
    human_pairs = {(k["model"], k["prompt_id"], k["comparison"].split(" vs ")[1]) for k in human_key.values() if "comparison" in k}
    jobs, keys = [], {"pairs": {}, "grades": {}, "labels": {}}

    # ---- pairwise judges
    per_judge = defaultdict(list)
    rot = 0
    for (model, cond, rep, pid), c in sorted(by.items()):
        if cond != "C-skill-v1" or rep != 1:
            continue
        for other in ("A-none", "D-placebo", "E-original"):
            o = by.get((model, other, 1, pid))
            if not o:
                continue
            eligible = [m for fam, m in JUDGES.items() if fam != c["family"]]
            if (model, pid, other) in human_pairs:
                chosen = eligible
            else:
                chosen = [eligible[(rot + k) % len(eligible)] for k in range(2)]
                rot += 1
            pair_id = f"{model}|{pid}|C-skill-v1~{other}"
            for judge in chosen:
                skill_first = rng.random() < 0.5
                item = f"j{len(keys['pairs']) + 1:05d}"
                keys["pairs"][item] = {"pair_id": pair_id, "judge": judge, "model": model, "family": c["family"], "prompt_id": pid,
                                       "comparison": f"C-skill-v1 vs {other}", "skill_is": "1" if skill_first else "2",
                                       "human_overlap": (model, pid, other) in human_pairs}
                r1, r2 = (c, o) if skill_first else (o, c)
                per_judge[judge].append((item, prompts[pid]["text"], r1["text"], r2["text"]))
    for judge, items in per_judge.items():
        rng.shuffle(items)
        for b, chunk in enumerate(chunks(items, PAIR_BATCH), 1):
            out = JUDGE_DIR / "pairs" / judge / f"batch{b:03d}.jsonl"
            body = "\n".join(f"\n##### item {i} #####\n[Message]\n{m}\n\n[Reply 1]\n{a}\n\n[Reply 2]\n{bb}\n##### end of item {i} #####" for i, m, a, bb in chunk)
            jobs.append({"id": f"pairs:{judge}:b{b:03d}", "kind": "pairs", "model": judge, "out_path": str(out),
                         "expect_ids": [i for i, *_ in chunk], "required_keys": ["item", "prefer", "ai_like"],
                         "prompt": PAIR_PROMPT.format(out_path=out, items=body)})

    # ---- fidelity and format graders (repeat 1, four main conditions); 15% double-graded
    grade_items = defaultdict(list)
    rot = 0
    for (model, cond, rep, pid), r in sorted(by.items()):
        p = prompts[pid]
        if rep != 1 or cond not in ("A-none", "C-skill-v1", "D-placebo", "E-original"):
            continue
        if not p.get("required_facts") and not p.get("format_request"):
            continue
        eligible = [m for fam, m in JUDGES.items() if fam != r["family"]]
        graders = [eligible[rot % len(eligible)]]
        if rng.random() < 0.15:
            graders.append(eligible[(rot + 1) % len(eligible)])
        rot += 1
        for g in graders:
            item = f"g{len(keys['grades']) + 1:05d}"
            keys["grades"][item] = {"model": model, "family": r["family"], "cond": cond, "prompt_id": pid, "grader": g,
                                    "n_facts": len(p.get("required_facts") or []), "format": (p.get("format_request") or {}).get("type")}
            facts = "\n".join(f"{n}. {f}" for n, f in enumerate(p.get("required_facts") or [], 1)) or "(none)"
            fr = p.get("format_request")
            fr_txt = "(none)" if not fr else f"{fr.get('type')}" + (f", {fr.get('count')} requested" if fr.get("count") else "")
            grade_items[g].append((item, p["text"], facts, fr_txt, r["text"]))
    for g, items in grade_items.items():
        rng.shuffle(items)
        for b, chunk in enumerate(chunks(items, GRADE_BATCH), 1):
            out = JUDGE_DIR / "grades" / g / f"batch{b:03d}.jsonl"
            body = "\n".join(f"\n##### item {i} #####\n[Message]\n{m}\n\n[Required facts]\n{f}\n\n[Format request]\n{fr}\n\n[Reply]\n{rep}\n##### end of item {i} #####" for i, m, f, fr, rep in chunk)
            jobs.append({"id": f"grades:{g}:b{b:03d}", "kind": "grades", "model": g, "out_path": str(out),
                         "expect_ids": [i for i, *_ in chunk], "required_keys": ["item", "facts", "invented", "format"],
                         "prompt": GRADE_PROMPT.format(out_path=out, items=body)})

    # ---- pattern-match labelers: up to 14 per tell from all test-1 replies, plus the human-checked matches
    found = defaultdict(list)
    for r in replies:
        for name, m, start, end in tells.matches(r["text"], prompts[r["prompt_id"]]):
            if start >= 0:
                found[name].append((r, start, end))
    sample = []
    for name, lst in found.items():
        for r, s, e in rng.sample(lst, min(14, len(lst))):
            sample.append((name, r, s, e))
    hk = {(k["model"], k["cond"], k["prompt_id"], k["start"], k["tell"]) for k in human_key.values() if "tell" in k}
    have = {(r["model"], r["cond"], r["prompt_id"], s, n) for n, r, s, e in sample}
    for (model, cond, pid, start, name) in hk - have:
        r = by.get((model, cond, 1, pid))
        if r:
            m = next((x for x in tells.matches(r["text"], prompts[pid]) if x[0] == name and x[2] == start), None)
            if m:
                sample.append((name, r, m[2], m[3]))
    rng.shuffle(sample)
    label_items = []
    for name, r, s, e in sample:
        item = f"l{len(keys['labels']) + 1:05d}"
        t = r["text"]
        keys["labels"][item] = {"tell": name, "model": r["model"], "cond": r["cond"], "rep": r["rep"], "prompt_id": r["prompt_id"], "start": s,
                                "human_overlap": (r["model"], r["cond"], r["prompt_id"], s, name) in hk}
        label_items.append((item, TELL_HELP.get(name, name), t[max(0, s - 140):s], t[s:e], t[e:e + 140]))
    for labeler in LABELERS:
        for b, chunk in enumerate(chunks(label_items, LABEL_BATCH), 1):
            out = JUDGE_DIR / "labels" / labeler / f"batch{b:03d}.jsonl"
            body = "\n".join(f"\n##### item {i} #####\nPattern: {h}\nContext: ...{bf}[[{m}]]{af}...\n##### end of item {i} #####" for i, h, bf, m, af in chunk)
            jobs.append({"id": f"labels:{labeler}:b{b:03d}", "kind": "labels", "model": labeler, "out_path": str(out),
                         "expect_ids": [i for i, *_ in chunk], "required_keys": ["item", "verdict"],
                         "prompt": LABEL_PROMPT.format(out_path=out, items=body)})

    for j in jobs:
        Path(j["out_path"]).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / "judge_manifest.json").write_text(json.dumps(jobs, ensure_ascii=False))
    (JUDGE_DIR / "keys.json").write_text(json.dumps(keys, ensure_ascii=False))
    kinds = defaultdict(int)
    for j in jobs:
        kinds[j["kind"]] += 1
    print("judge jobs:", len(jobs), dict(kinds))
    print("pair judgments:", len(keys["pairs"]), "| graded replies:", len(keys["grades"]), "| labeled matches:", len(keys["labels"]))
    print("max prompt chars:", max(len(j["prompt"]) for j in jobs))


if __name__ == "__main__":
    main()
