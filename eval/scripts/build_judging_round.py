"""Build pairwise-judge and fidelity-grader jobs for any comparison of two conditions.

Example (dev tuning of the v2 candidate against v1 and no skill):
  python scripts/build_judging_round.py --replies results/replies.jsonl results/replies_dev_v2.jsonl \
      --set dev --skill G-skill-v2-candidate --against C-skill-v1 A-none --round dev-v2
"""

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_judging import GRADE_BATCH, GRADE_PROMPT, JUDGES, PAIR_BATCH, PAIR_PROMPT, chunks, read_jsonl  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--replies", nargs="+", required=True)
    ap.add_argument("--set", required=True)
    ap.add_argument("--skill", required=True)
    ap.add_argument("--against", nargs="+", required=True)
    ap.add_argument("--round", required=True)
    ap.add_argument("--rep", type=int, default=1)
    ap.add_argument("--grade", nargs="*", default=None, help="conditions to grade for fidelity/format (default: skill + against)")
    ap.add_argument("--seed", type=int, default=9912)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    out_dir = ROOT / "judgments" / args.round
    prompts = {}
    for name in ("dev", "test1", "test2"):
        for p in read_jsonl(ROOT / "prompts" / f"{name}.jsonl"):
            prompts[p["id"]] = p
    by = {}
    for f in args.replies:
        for r in read_jsonl(f):
            if r["set"] == args.set and r["rep"] == args.rep and r["turn"] is None:
                by[(r["model"], r["cond"], r["prompt_id"])] = r
    jobs, keys = [], {"pairs": {}, "grades": {}}
    per_judge = defaultdict(list)
    rot = 0
    for (model, cond, pid), s in sorted(by.items()):
        if cond != args.skill:
            continue
        for other in args.against:
            o = by.get((model, other, pid))
            if not o:
                continue
            eligible = [m for fam, m in JUDGES.items() if fam != s["family"]]
            chosen = [eligible[(rot + k) % len(eligible)] for k in range(2)]
            rot += 1
            for judge in chosen:
                skill_first = rng.random() < 0.5
                item = f"j{len(keys['pairs']) + 1:05d}"
                keys["pairs"][item] = {"pair_id": f"{model}|{pid}|{args.skill}~{other}", "judge": judge, "model": model, "family": s["family"],
                                       "prompt_id": pid, "category": prompts[pid]["category"], "comparison": f"{args.skill} vs {other}",
                                       "skill_is": "1" if skill_first else "2", "w_skill": s["words"], "w_other": o["words"]}
                r1, r2 = (s, o) if skill_first else (o, s)
                per_judge[judge].append((item, prompts[pid]["text"], r1["text"], r2["text"]))
    for judge, items in per_judge.items():
        rng.shuffle(items)
        for b, chunk in enumerate(chunks(items, PAIR_BATCH), 1):
            out = out_dir / "pairs" / judge / f"batch{b:03d}.jsonl"
            body = "\n".join(f"\n##### item {i} #####\n[Message]\n{m}\n\n[Reply 1]\n{a}\n\n[Reply 2]\n{bb}\n##### end of item {i} #####" for i, m, a, bb in chunk)
            jobs.append({"id": f"{args.round}:pairs:{judge}:b{b:03d}", "kind": "pairs", "model": judge, "out_path": str(out),
                         "expect_ids": [i for i, *_ in chunk], "required_keys": ["item", "prefer", "ai_like"],
                         "prompt": PAIR_PROMPT.format(out_path=out, items=body)})
    grade_conds = args.grade if args.grade is not None else [args.skill] + args.against
    grade_items = defaultdict(list)
    rot = 0
    for (model, cond, pid), r in sorted(by.items()):
        p = prompts[pid]
        if cond not in grade_conds or (not p.get("required_facts") and not p.get("format_request")):
            continue
        eligible = [m for fam, m in JUDGES.items() if fam != r["family"]]
        g = eligible[rot % len(eligible)]
        rot += 1
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
            out = out_dir / "grades" / g / f"batch{b:03d}.jsonl"
            body = "\n".join(f"\n##### item {i} #####\n[Message]\n{m}\n\n[Required facts]\n{f}\n\n[Format request]\n{fr}\n\n[Reply]\n{rep}\n##### end of item {i} #####" for i, m, f, fr, rep in chunk)
            jobs.append({"id": f"{args.round}:grades:{g}:b{b:03d}", "kind": "grades", "model": g, "out_path": str(out),
                         "expect_ids": [i for i, *_ in chunk], "required_keys": ["item", "facts", "invented", "format"],
                         "prompt": GRADE_PROMPT.format(out_path=out, items=body)})
    for j in jobs:
        Path(j["out_path"]).parent.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "keys.json").write_text(json.dumps(keys, ensure_ascii=False))
    (ROOT / f"judge_manifest_{args.round}.json").write_text(json.dumps(jobs, ensure_ascii=False))
    print(f"{args.round}: {len(jobs)} jobs | pair judgments {len(keys['pairs'])} | graded replies {len(keys['grades'])}")


if __name__ == "__main__":
    main()
