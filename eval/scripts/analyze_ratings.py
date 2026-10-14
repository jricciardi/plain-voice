"""Summarize round 3 human ratings from the rating app.

Reads the answer key written by build_rater_kits.py and any number of results
files (the JSON the app copies or downloads; extra text around it is fine).
Prints a markdown report.

Example:
  python scripts/analyze_ratings.py --key ../round3/kits/key.json ../round3/results/
"""
import argparse
import json
import random
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tells  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LABEL = {"A-none": "No skill", "C-skill-v1": "Skill v1"}


def read_results(paths):
    latest = {}
    files = []
    for p in paths:
        p = Path(p)
        files.extend(sorted(p.glob("*.json")) + sorted(p.glob("*.txt")) if p.is_dir() else [p])
    for f in files:
        text = f.read_text(encoding="utf-8", errors="replace")
        a, b = text.find("{"), text.rfind("}")
        if a < 0 or b < a:
            continue
        try:
            r = json.loads(text[a:b + 1])
        except json.JSONDecodeError:
            print(f"skipped {f}: not valid JSON", file=sys.stderr)
            continue
        if r.get("app") != "plain-voice-rating":
            continue
        kit = r["kit_id"]
        if kit not in latest or r.get("exported_at", "") > latest[kit].get("exported_at", ""):
            latest[kit] = r
    return latest


def boot_mean_ci(values, groups=None, n=2000, seed=7):
    """Percentile bootstrap of the mean, resampling groups (e.g. raters) when given."""
    if not values:
        return None, None, None
    rng = random.Random(seed)
    if groups is None:
        groups = list(range(len(values)))
    by = defaultdict(list)
    for v, g in zip(values, groups):
        by[g].append(v)
    keys = list(by)
    means = []
    for _ in range(n):
        sample = []
        for _ in keys:
            sample.extend(by[rng.choice(keys)])
        means.append(sum(sample) / len(sample))
    means.sort()
    return sum(values) / len(values), means[int(0.025 * n)], means[int(0.975 * n) - 1]


def fmt_ci(m, lo, hi, digits=2):
    if m is None:
        return "n/a"
    return f"{m:.{digits}f} ({lo:.{digits}f} to {hi:.{digits}f})"


def pct(n, d):
    return f"{100 * n / d:.0f}%" if d else "n/a"


def load_rows(key, results, prompts, exclude):
    items, blocks, sessions = [], [], []
    for kit_id, r in results.items():
        kk = key["kits"].get(kit_id)
        if not kk:
            print(f"results for unknown kit {kit_id} skipped", file=sys.stderr)
            continue
        rater = kk["rater"]
        if rater in exclude:
            continue
        for skey in kk["sessions"]:
            sres = r["sessions"].get(skey["id"])
            if not sres:
                continue
            conds = {}
            for bkey in skey["blocks"]:
                conds[bkey["id"]] = bkey["cond"]
                bres = (sres.get("blocks") or {}).get(bkey["id"]) or {}
                if bres.get("w") is not None:
                    blocks.append({"rater": rater, "session": skey["id"], "model": skey["model"], "family": skey["family"],
                                   "block": bkey["id"], "cond": bkey["cond"], "worn": bres["w"]})
                for pos, it in enumerate(bkey["items"]):
                    ires = (sres.get("items") or {}).get(it["id"])
                    if not ires or ires.get("t") is None or ires.get("j") is None:
                        continue
                    flags = set(ires.get("f") or [])
                    items.append(dict(it, rater=rater, pair=kk.get("pair"), session=skey["id"], block=bkey["id"],
                                      tiring=ires["t"], job=ires["j"], ms=ires.get("ms") or 0, flags=flags,
                                      prompt_rec=prompts.get(it["prompt_id"], {"text": ""})))
            if sres.get("end") and sres.get("p"):
                p = sres["p"]
                choice = conds.get(p, p)
                sessions.append({"rater": rater, "session": skey["id"], "model": skey["model"], "family": skey["family"],
                                 "choice": choice, "note": sres.get("n") or ""})
    return items, blocks, sessions


def report(items, blocks, sessions, title):
    out = [f"## {title}", ""]
    raters = sorted({i["rater"] for i in items})
    out.append(f"Raters: {len(raters)} ({', '.join(raters)}). Replies rated: {len(items)}. Batches rated: {len(blocks)}. Sessions finished: {len(sessions)}.")
    out.append("")
    if not items:
        return out

    out += ["### Each reply", "",
            "| Condition | Replies | Tiring, 1 to 5 (95% interval) | Does the job: yes / mostly / no | Flags per reply | Flags per 100 words | Median seconds |",
            "|---|---:|---|---|---:|---:|---:|"]
    for cond in ("A-none", "C-skill-v1"):
        rows = [i for i in items if i["cond"] == cond]
        if not rows:
            continue
        m, lo, hi = boot_mean_ci([i["tiring"] for i in rows], [i["rater"] for i in rows] if len(raters) >= 3 else None)
        job = Counter(i["job"] for i in rows)
        nflags = sum(len(i["flags"]) for i in rows)
        words = sum(i["words"] for i in rows)
        secs = statistics.median(i["ms"] / 1000 for i in rows)
        out.append(f"| {LABEL[cond]} | {len(rows)} | {fmt_ci(m, lo, hi)} | {pct(job['yes'], len(rows))} / {pct(job['mostly'], len(rows))} / {pct(job['no'], len(rows))} | "
                   f"{nflags / len(rows):.2f} | {100 * nflags / words:.2f} | {secs:.0f} |")
    out.append("")

    # matched: same model and prompt read both ways (by the two raters in a pair)
    by = defaultdict(dict)
    for i in items:
        by[(i["model"], i["prompt_id"])].setdefault(i["cond"], []).append(i)
    diffs, job_diffs = [], []
    for k, d in by.items():
        if "A-none" in d and "C-skill-v1" in d:
            a = statistics.mean(x["tiring"] for x in d["A-none"])
            c = statistics.mean(x["tiring"] for x in d["C-skill-v1"])
            diffs.append(c - a)
            score = {"yes": 2, "mostly": 1, "no": 0}
            job_diffs.append(statistics.mean(score[x["job"]] for x in d["C-skill-v1"]) - statistics.mean(score[x["job"]] for x in d["A-none"]))
    if diffs:
        m, lo, hi = boot_mean_ci(diffs)
        jm, jlo, jhi = boot_mean_ci(job_diffs)
        out += ["### Same prompt, read both ways", "",
                f"{len(diffs)} prompt and model combinations were read with and without the skill (by different raters). Below zero means the skill's reply was rated less tiring.",
                "",
                f"- Tiring, skill minus no skill: {fmt_ci(m, lo, hi)}. Skill less tiring on {sum(d < 0 for d in diffs)}, same on {sum(d == 0 for d in diffs)}, more tiring on {sum(d > 0 for d in diffs)}.",
                f"- Does the job (yes 2, mostly 1, no 0), skill minus no skill: {fmt_ci(jm, jlo, jhi)}. Above zero means the skill's reply did the job better.",
                ""]

    if blocks:
        out += ["### Batches", "", "| Condition | Batches | Worn out, 1 to 5 |", "|---|---:|---|"]
        for cond in ("A-none", "C-skill-v1"):
            rows = [b for b in blocks if b["cond"] == cond]
            if rows:
                m, lo, hi = boot_mean_ci([b["worn"] for b in rows])
                out.append(f"| {LABEL[cond]} | {len(rows)} | {fmt_ci(m, lo, hi)} |")
        paired = defaultdict(dict)
        for b in blocks:
            paired[(b["rater"], b["session"])][b["cond"]] = b["worn"]
        d = [v["C-skill-v1"] - v["A-none"] for v in paired.values() if len(v) == 2]
        if d:
            m, lo, hi = boot_mean_ci(d)
            out += ["", f"Within a session, skill batch minus no-skill batch: {fmt_ci(m, lo, hi)} over {len(d)} sessions (skill batch less wearing in {sum(x < 0 for x in d)}, same in {sum(x == 0 for x in d)}, more in {sum(x > 0 for x in d)})."]
        out.append("")

    if sessions:
        c = Counter(s["choice"] for s in sessions)
        n = len(sessions)
        out += ["### Which batch they'd rather keep getting", "",
                f"Skill batch {c['C-skill-v1']} ({pct(c['C-skill-v1'], n)}), no-skill batch {c['A-none']} ({pct(c['A-none'], n)}), both fine {c['both_fine']} ({pct(c['both_fine'], n)}), both bad {c['both_bad']} ({pct(c['both_bad'], n)}), out of {n} sessions.",
                ""]

    out += ["### By model family (tiring, mean)", "", "| Family | No skill | Skill v1 | Replies |", "|---|---:|---:|---:|"]
    for fam in sorted({i["family"] for i in items}):
        vals = {cond: [i["tiring"] for i in items if i["family"] == fam and i["cond"] == cond] for cond in ("A-none", "C-skill-v1")}
        out.append(f"| {fam} | {statistics.mean(vals['A-none']):.2f} | {statistics.mean(vals['C-skill-v1']):.2f} | {sum(len(v) for v in vals.values())} |"
                   if all(vals.values()) else f"| {fam} | n/a | n/a | {sum(len(v) for v in vals.values())} |")
    out += ["", "### By rater (tiring, mean)", "", "| Rater | No skill | Skill v1 | Replies |", "|---|---:|---:|---:|"]
    for r in raters:
        vals = {cond: [i["tiring"] for i in items if i["rater"] == r and i["cond"] == cond] for cond in ("A-none", "C-skill-v1")}
        cells = [f"{statistics.mean(v):.2f}" if v else "n/a" for v in vals.values()]
        out.append(f"| {r} | {cells[0]} | {cells[1]} | {sum(len(v) for v in vals.values())} |")
    out.append("")

    # what people noticed: counted tells and whether a flagged sentence overlaps them
    occ = defaultdict(lambda: {"A-none": [0, 0], "C-skill-v1": [0, 0]})
    flagged_units, flagged_with_tell, residual = 0, 0, []
    for i in items:
        spans = {k: (s, e) for k, s, e in i["units"]}
        found = tells.matches(i["reply"], i["prompt_rec"])
        for name, text, s, e in found:
            if s < 0:
                continue
            hit = any(spans[k][0] < e and s < spans[k][1] for k in i["flags"] if k in spans)
            occ[name][i["cond"]][0] += 1
            occ[name][i["cond"]][1] += int(hit)
        for k in i["flags"]:
            if k not in spans:
                continue
            flagged_units += 1
            s0, e0 = spans[k]
            if any(s < e0 and s0 < e for _, _, s, e in found if s >= 0):
                flagged_with_tell += 1
            else:
                residual.append((i["cond"], i["model"], i["reply"][s0:e0]))
    if occ:
        out += ["### Which counted tells readers flagged", "",
                "How often a sentence containing each tell was tapped, most common tells first. A high share means readers notice that tell; a low one suggests the list could drop it.", "",
                "| Tell | Seen without skill | Flagged | Seen with skill | Flagged |", "|---|---:|---:|---:|---:|"]
        for name, v in sorted(occ.items(), key=lambda kv: (-(kv[1]["A-none"][0] + kv[1]["C-skill-v1"][0]), kv[0])):
            a, c = v["A-none"], v["C-skill-v1"]
            out.append(f"| {name} | {a[0]} | {pct(a[1], a[0])} | {c[0]} | {pct(c[1], c[0])} |")
        out.append("")
    out += [f"Flagged sentences: {flagged_units}. Containing a counted tell: {pct(flagged_with_tell, flagged_units)}.", ""]
    if residual:
        out += ["### Flagged sentences with no counted tell", "", "Candidates for new list entries, or signs of something other than tells (length, tone, wrong facts).", ""]
        for cond, model, text in residual[:60]:
            out.append(f"- ({LABEL[cond]}, {model}) {text.strip()[:220]}")
        out.append("")
    notes = [s for s in sessions if s["note"].strip()]
    if notes:
        out += ["### Session notes", ""] + [f"- {s['rater']}, {s['session']}: {s['note'].strip()}" for s in notes] + [""]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--key", required=True)
    ap.add_argument("--author", default="Jay", help="Rater who wrote the skill; a second report leaves them out. Use '' to skip.")
    ap.add_argument("--out", help="Write the report here instead of printing it.")
    ap.add_argument("results", nargs="+", help="Results files or folders.")
    args = ap.parse_args()

    key = json.loads(Path(args.key).read_text(encoding="utf-8"))
    prompts = {}
    for name in ("test1", "test2"):
        for line in (ROOT / "prompts" / f"{name}.jsonl").read_text(encoding="utf-8").splitlines():
            if line.strip():
                p = json.loads(line)
                prompts[p["id"]] = p
    results = read_results(args.results)
    lines = ["# Round 3 human ratings", "", f"Results files: {len(results)} kits."]
    items, blocks, sessions = load_rows(key, results, prompts, set())
    lines += [""] + report(items, blocks, sessions, "All raters")
    if args.author and any(i["rater"] == args.author for i in items):
        lines += report(*load_rows(key, results, prompts, {args.author}), f"Without {args.author}, who wrote the skill")
    text = "\n".join(lines) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
