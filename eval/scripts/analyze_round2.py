"""Round 2: check the pre-registered hypotheses for skill v2 on sealed test-2 and apply the shipping rule."""

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from analyze import boot_ratio, wilson  # noqa: E402
from analyze_round import load  # noqa: E402

ROOT = Path(os.environ.get("PV_EVAL_ROOT") or Path(__file__).resolve().parents[1])
RES = ROOT / "results"
FAMS = ["Claude", "GPT", "Gemini", "Grok", "MAI"]
CN = {"A-none": "No skill", "C-skill-v1": "Skill v1", "H-skill-v2": "Skill v2"}


def ci(t, pct=False):
    p, lo, hi = t
    if p != p:
        return "n/a"
    return f"{100 * p:.0f}% ({100 * lo:.0f}–{100 * hi:.0f})" if pct else f"{p:.2f} ({lo:.2f}–{hi:.2f})"


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    return "\n".join(out + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])


def main():
    df = pd.DataFrame([json.loads(x) for x in (RES / "replies_round2.jsonl").read_text().splitlines() if x.strip()])
    t2 = df[df.set == "test2"]
    out, verdicts = {"n_replies": int(len(df)), "by_set": df.groupby("set").size().to_dict()}, []

    # 1. tells v2 vs no skill, per family
    r1 = {}
    for fam in FAMS + ["All"]:
        sub = t2 if fam == "All" else t2[t2.family == fam]
        r1[fam] = {"H/A": boot_ratio(sub, "H-skill-v2", "A-none"), "C/A": boot_ratio(sub, "C-skill-v1", "A-none"), "H/C": boot_ratio(sub, "H-skill-v2", "C-skill-v1")}
    out["tell_ratios"] = r1
    ok1 = all(r1[f]["H/A"][0] <= 0.5 for f in FAMS)
    verdicts.append(("1. v2 has at most half the tells of no skill, in every family", "pass" if ok1 else "fail",
                     "; ".join(f"{f} {r1[f]['H/A'][0]:.2f}" for f in FAMS)))

    # judges and graders
    pj, gd = load("t2")
    j = {}
    for comp, g in pj.groupby("comparison"):
        dec, dai = g[g.prefer != "tie"], g[g.ai != "same"]
        j[comp] = {"n": int(len(g)),
                   "prefers_v2": wilson(int((dec.prefer == "skill").sum()), len(dec)),
                   "v2_less_ai_like": wilson(int((dai.ai == "other").sum()), len(dai)),
                   "v2_more_ai_like": wilson(int((dai.ai == "skill").sum()), len(dai)),
                   "by_family_less_ai_like": {f: wilson(int((x[x.ai != "same"].ai == "other").sum()), int((x.ai != "same").sum())) for f, x in g.groupby("family")},
                   "by_family_prefers_v2": {f: wilson(int((x[x.prefer != "tie"].prefer == "skill").sum()), int((x.prefer != "tie").sum())) for f, x in g.groupby("family")},
                   "by_category_prefers_v2": {c: wilson(int((x[x.prefer != "tie"].prefer == "skill").sum()), int((x.prefer != "tie").sum())) for c, x in g.groupby("category")}}
    out["judges"] = j
    va = j.get("H-skill-v2 vs A-none")
    if va:
        fam_ok = all(v[0] > 0.60 for v in va["by_family_less_ai_like"].values())
        ok2 = va["v2_less_ai_like"][0] > 0.75 and fam_ok
        verdicts.append(("2. Judges find v2 less AI-like than no skill in over 75% of decisive pairs, and over 60% in every family",
                         "pass" if ok2 else "fail", f"overall {ci(va['v2_less_ai_like'], True)}; " + "; ".join(f"{f} {100 * v[0]:.0f}%" for f, v in va["by_family_less_ai_like"].items())))
    vc = j.get("H-skill-v2 vs C-skill-v1")
    if vc:
        ok3 = vc["v2_more_ai_like"][0] <= 0.55 and r1["All"]["H/C"][0] <= 1.15
        verdicts.append(("3. No regression from v1: judges find v2 more AI-like in at most 55% of decisive pairs, and tells at most 1.15 times v1's",
                         "pass" if ok3 else "fail", f"v2 judged more AI-like {ci(vc['v2_more_ai_like'], True)}; tells v2/v1 {ci(r1['All']['H/C'])}"))
    fid = {}
    for cond, g in gd[gd.n_facts > 0].groupby("cond"):
        tot = g.checked.sum()
        fid[cond] = {"replies": int(len(g)), "facts": int(tot), "missing": float(g.missing.sum() / max(tot, 1)),
                     "wrong": float(g.wrong.sum() / max(tot, 1)), "invented": float(g.invented.mean())}
    out["fidelity"] = fid
    if {"A-none", "C-skill-v1", "H-skill-v2"} <= set(fid):
        h, a, c = fid["H-skill-v2"], fid["A-none"], fid["C-skill-v1"]
        ok4 = h["missing"] <= a["missing"] + 0.01 and h["missing"] <= c["missing"] and h["invented"] <= a["invented"]
        verdicts.append(("4. Fidelity: v2 misses no more than 1 point above no skill and no more than v1, and invents no more than no skill",
                         "pass" if ok4 else "fail", f"missing {100 * h['missing']:.1f}% vs no skill {100 * a['missing']:.1f}% and v1 {100 * c['missing']:.1f}%; invented per reply {h['invented']:.2f} vs {a['invented']:.2f}"))
    fm = {c: wilson(int((g.format_v == "yes").sum()), len(g)) for c, g in gd[gd.format.notna() & gd.format_v.isin(["yes", "partly", "no"])].groupby("cond")}
    out["format"] = fm
    if "H-skill-v2" in fm:
        ok5 = fm["H-skill-v2"][0] >= 0.95
        verdicts.append(("5. v2 follows explicit format requests at least 95% of the time", "pass" if ok5 else "fail", ci(fm["H-skill-v2"], True)))
    res = {v[0][0]: v[1] for v in verdicts}
    ship = all(res.get(k) == "pass" for k in ("1", "3", "4", "5"))
    out["verdicts"] = verdicts
    out["ship_v2"] = ship

    # exploratory
    out["mean_tells"] = t2.groupby(["family", "cond"]).tells_total.mean().unstack().round(2).to_dict()
    out["words"] = t2.groupby("cond").words.mean().round(1).to_dict()
    out["words_by_family"] = t2.groupby(["family", "cond"]).words.mean().unstack().round(0).to_dict()
    tc = [c for c in t2.columns if c.startswith("tell_")]
    pt = t2.groupby("cond")[tc].sum().T
    pt.index = [i.replace("tell_", "") for i in pt.index]
    out["per_tell"] = pt.astype(int).to_dict()
    uw = t2[t2.category == "user_words"]
    out["user_words_reuse"] = uw.assign(r=uw.user_words_reused > 0).groupby("cond").r.mean().round(3).to_dict()
    mt = df[df.set == "multiturn2"]
    if not mt.empty:
        mt = mt.assign(turn=mt.turn.astype(int))
        out["multiturn_by_turn"] = mt.groupby(["turn", "cond"]).tells_total.mean().unstack().round(2).to_dict()
        h = mt[mt.cond == "H-skill-v2"]
        out["multiturn_v2_slope"] = round(float(np.polyfit(h.turn.astype(float), h.tells_total.astype(float), 1)[0]), 3) if len(h) > 5 else None

    (RES / "round2_summary.json").write_text(json.dumps(out, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))

    md = ["# Round 2: skill v2 on sealed test-2", "", f"Replies scored: {len(df)} ({', '.join(f'{k} {v}' for k, v in out['by_set'].items())}). Intervals are 95%.", "",
          "## Pre-registered hypotheses", "", table(["Hypothesis", "Result", "Evidence"], verdicts), "",
          f"Shipping rule (v2 ships if 1, 3, 4 and 5 pass): **{'ship v2' if ship else 'keep v1'}**.", "",
          "## Tells, ratio against no skill (below 1 means fewer)", "",
          table(["Family", "v2 / no skill", "v1 / no skill", "v2 / v1"], [[f, ci(r1[f]["H/A"]), ci(r1[f]["C/A"]), ci(r1[f]["H/C"])] for f in FAMS + ["All"]]), ""]
    for comp, v in j.items():
        md += [f"## Judges: {comp.replace('H-skill-v2', 'v2').replace('A-none', 'no skill').replace('C-skill-v1', 'v1')}", "",
               f"Judgments: {v['n']}. Prefers v2 {ci(v['prefers_v2'], True)}. Finds v2 less AI-like {ci(v['v2_less_ai_like'], True)}.", "",
               table(["Family", "Finds v2 less AI-like", "Prefers v2"], [[f, ci(v["by_family_less_ai_like"][f], True), ci(v["by_family_prefers_v2"][f], True)] for f in v["by_family_less_ai_like"]]), "",
               "Preference by category: " + "; ".join(f"{c} {100 * x[0]:.0f}%" for c, x in sorted(v["by_category_prefers_v2"].items(), key=lambda kv: kv[1][0])), ""]
    md += ["## Fidelity", "", table(["Condition", "Replies", "Facts", "Missing", "Wrong", "Invented per reply"],
                                     [[CN[c], f["replies"], f["facts"], f"{100 * f['missing']:.1f}%", f"{100 * f['wrong']:.1f}%", f"{f['invented']:.2f}"] for c, f in fid.items()]), "",
           "## Format requests", "", table(["Condition", "Followed"], [[CN[c], ci(v, True)] for c, v in fm.items()]), "",
           "## Length and the user's own words", "", table(["Condition", "Words per reply", "Reuses a listed word the user wrote"],
                                                           [[CN[c], f"{out['words'][c]:.0f}", f"{100 * out['user_words_reuse'].get(c, float('nan')):.0f}%"] for c in out["words"]]), ""]
    if "multiturn_by_turn" in out:
        mtt = out["multiturn_by_turn"]
        md += ["## Multi-turn (mean tells per reply by turn)", "", table(["Turn", "No skill", "Skill v2"], [[t, f"{mtt.get('A-none', {}).get(t, float('nan')):.2f}", f"{mtt.get('H-skill-v2', {}).get(t, float('nan')):.2f}"] for t in sorted(mtt.get("A-none", {}))]), ""]
    (RES / "ROUND2.md").write_text("\n".join(md))
    print("\n".join(f"{v[0]} -> {v[1]} | {v[2]}" for v in verdicts))
    print("SHIP v2" if ship else "KEEP v1")


if __name__ == "__main__":
    main()
