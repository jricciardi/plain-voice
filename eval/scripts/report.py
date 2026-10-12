"""Render eval/results/summary.json as markdown tables (eval/results/TABLES.md)."""

import json
import os
from pathlib import Path

ROOT = Path(os.environ.get("PV_EVAL_ROOT") or Path(__file__).resolve().parents[1])
RES = ROOT / "results"
FAMS = ["Claude", "GPT", "Gemini", "Grok", "MAI"]
MAIN = ["A-none", "C-skill-v1", "D-placebo", "E-original"]
CNAME = {"A-none": "No skill", "C-skill-v1": "Skill v1", "D-placebo": "Placebo", "E-original": "Original skill"}


def ci(t, pct=False, digits=2):
    if t is None:
        return "n/a"
    p, lo, hi = t
    if p != p:  # nan
        return "n/a"
    if pct:
        return f"{100 * p:.0f}% ({100 * lo:.0f}–{100 * hi:.0f})"
    return f"{p:.{digits}f} ({lo:.{digits}f}–{hi:.{digits}f})"


def table(header, rows, numeric=True):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" if (i == 0 or not numeric) else "---:" for i in range(len(header))) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def verdicts(s):
    v = []
    ratios = {r["family"]: r for r in s.get("ratios", [])}
    fam_ok = [f for f in FAMS if f in ratios and ratios[f]["C/D"][0] <= 0.5]
    v.append(("H1. Skill has at most half the tells of the placebo, in every family",
              "pass" if len(fam_ok) == sum(f in ratios for f in FAMS) else f"fail ({', '.join(f for f in FAMS if f in ratios and f not in fam_ok)} above 0.5)",
              "; ".join(f"{f} {ratios[f]['C/D'][0]:.2f}" for f in FAMS if f in ratios)))
    h = s.get("human", {})
    hv = h.get("C-skill-v1 vs A-none", {}).get("prefers_skill")
    v.append(("H2. Human prefers the skill reply over no skill in more than 60% of decisive pairs",
              "pending" if not hv else ("pass" if hv[0] > 0.6 else "fail"), ci(hv, pct=True) if hv else "awaiting review"))
    fid = s.get("fidelity", {})
    if "A-none" in fid and "C-skill-v1" in fid:
        d = fid["C-skill-v1"]["missing_rate"] - fid["A-none"]["missing_rate"]
        inv = fid["C-skill-v1"]["invented_per_reply"] - fid["A-none"]["invented_per_reply"]
        v.append(("H3. Skill doesn't miss more required facts (under 2 points) or invent more",
                  "pass" if d < 0.02 and inv <= 0 else "fail",
                  f"missing {100 * fid['C-skill-v1']['missing_rate']:.1f}% vs {100 * fid['A-none']['missing_rate']:.1f}%; invented per reply {fid['C-skill-v1']['invented_per_reply']:.2f} vs {fid['A-none']['invented_per_reply']:.2f}"))
    fm = s.get("format_compliance_graders", {}).get("C-skill-v1")
    if fm:
        v.append(("H4. Skill follows explicit format requests at least 95% of the time", "pass" if fm["yes"][0] >= 0.95 else "fail", ci(fm["yes"], pct=True)))
    a_ok = [f for f in FAMS if f in ratios and ratios[f]["C/A"][2] < 1]
    e_ok = [f for f in FAMS if f in ratios and ratios[f]["C/E"][2] < 1]
    v.append(("H5. Fewer tells than no skill and than the original skill, per family (interval below 1)",
              "pass" if len(a_ok) == len(e_ok) == sum(f in ratios for f in FAMS) else "partial",
              f"vs no skill: {len(a_ok)}/{sum(f in ratios for f in FAMS)} families; vs original: {len(e_ok)}/{sum(f in ratios for f in FAMS)}"))
    hv6 = h.get("C-skill-v1 vs A-none", {}).get("skill_less_ai_like")
    v.append(("H6. Human finds the skill reply less like stock AI in more than 60% of decisive pairs",
              "pending" if not hv6 else ("pass" if hv6[0] > 0.6 else "fail"), ci(hv6, pct=True) if hv6 else "awaiting review"))
    uw = s.get("user_words_reuse_rate", {})
    if "A-none" in uw and "C-skill-v1" in uw:
        v.append(("H7. Skill reuses the user's own listed words about as often as no skill (within 10 points)",
                  "pass" if uw["C-skill-v1"] >= uw["A-none"] - 0.10 else "fail", f"{100 * uw['C-skill-v1']:.0f}% vs {100 * uw['A-none']:.0f}%"))
    ident = s.get("family_identifiability_balanced_accuracy", {})
    if "A-none" in ident and "C-skill-v1" in ident:
        v.append(("H8. Model family is harder to identify with the skill", "pass" if ident["C-skill-v1"] < ident["A-none"] else "fail",
                  f"{ident['C-skill-v1']:.2f} vs {ident['A-none']:.2f} (chance {ident['chance']:.2f})"))
    return v


def main():
    s = json.loads((RES / "summary.json").read_text())
    md = ["# plain-voice stress test, round 1: tables", "",
          f"Generated from `results/summary.json`. Tell suite v{s.get('suite_version')}. Replies scored: {s.get('n_replies')} ({', '.join(f'{k} {v}' for k, v in s.get('replies_by_set', {}).items())}).", "",
          "Intervals are 95%: cluster bootstrap over prompts for ratios, Wilson for rates.", ""]

    md += ["## Pre-registered hypotheses", "", table(["Hypothesis", "Result", "Evidence"], verdicts(s), numeric=False), ""]

    m = s.get("mean_tells_per_reply", {})
    md += ["## Mean counted tells per reply (test-1)", "",
           table(["Family"] + [CNAME[c] for c in MAIN], [[f] + [f"{m.get(c, {}).get(f, float('nan')):.2f}" for c in MAIN] for f in FAMS + ["All"] if f in m.get("A-none", {})]), ""]
    md += ["## Ratio of tells, skill v1 against each comparison", "",
           "Below 1 means fewer tells with the skill. The per-100-words column adjusts for reply length.", "",
           table(["Family", "vs placebo", "vs no skill", "vs original skill", "vs no skill, per 100 words"],
                 [[r["family"], ci(r["C/D"]), ci(r["C/A"]), ci(r["C/E"]), ci(r["C/A per100w"])] for r in s.get("ratios", [])]), ""]
    glm = s.get("poisson_glm")
    if glm:
        md += ["Poisson model with model and prompt effects (rate ratio against skill v1, prompt-clustered intervals): " +
               "; ".join(f"{k.replace(' vs C (rate ratio)', '')} {ci(v)}" for k, v in glm.items()) + ".", ""]
    pm = s.get("per_model_mean", {})
    if pm:
        models = sorted(pm.get("A-none", {}))
        md += ["## By model (mean tells per reply)", "", table(["Model"] + [CNAME[c] for c in MAIN], [[mo] + [f"{pm.get(c, {}).get(mo, float('nan')):.2f}" for c in MAIN] for mo in models]), ""]
    pt = s.get("per_tell_totals", {})
    if pt:
        names = sorted(pt.get("A-none", {}), key=lambda n: -pt["A-none"][n])
        md += ["## Totals by tell (test-1, all repeats)", "", table(["Tell"] + [CNAME[c] for c in MAIN], [[n] + [pt.get(c, {}).get(n, 0) for c in MAIN] for n in names]), ""]
    pc = s.get("per_category_mean", {})
    if pc:
        cats = sorted(pc.get("A-none", {}))
        md += ["## By prompt category (mean tells per reply)", "", table(["Category"] + [CNAME[c] for c in MAIN], [[k] + [f"{pc.get(c, {}).get(k, float('nan')):.2f}" for c in MAIN] for k in cats]), ""]
    w = s.get("watch_mean_per_reply", {})
    if w:
        keys = sorted(w)
        md += ["## Watch list: unscored patterns (mean per reply)", "", "Rises here with the skill would suggest substitution: dropping a listed tell for an unlisted one.", "",
               table(["Pattern"] + [CNAME[c] for c in MAIN], [[k.replace("watch_", "")] + [f"{w[k].get(c, float('nan')):.2f}" for c in MAIN] for k in keys]), ""]
    ps = s.get("per_section_mean", {})
    if ps:
        md += ["## Tells by skill section (mean per reply)", "", table(["Section"] + [CNAME[c] for c in MAIN], [[k.replace("section_", "")] + [f"{ps[k].get(c, float('nan')):.2f}" for c in MAIN] for k in sorted(ps)]), ""]
    ln = s.get("length", {})
    if ln:
        md += ["## Length and style", "", table(["Measure"] + [CNAME[c] for c in MAIN], [[k] + [f"{ln.get(k, {}).get(c, float('nan')):.1f}" for c in MAIN] for k in ln]), ""]
        lf = s.get("length_by_family", {})
        if lf:
            md += ["Words per reply by family:", "", table(["Family"] + [CNAME[c] for c in MAIN], [[f] + [f"{lf.get(c, {}).get(f, float('nan')):.0f}" for c in MAIN] for f in FAMS if f in lf.get("A-none", {})]), ""]
    fc = s.get("format_compliance_pattern", {})
    if fc:
        md += ["## Explicit format requests (pattern check)", "", table(["Condition", "Followed"], [[CNAME.get(c, c), ci(v, pct=True)] for c, v in fc.items()]), ""]
    uw = s.get("user_words_reuse_rate", {})
    if uw:
        md += ["## User's own listed words reused", "", table(["Condition", "Replies reusing a listed word the user wrote"], [[CNAME.get(c, c), f"{100 * v:.0f}%"] for c, v in uw.items()]), ""]
    ab = s.get("ablations", [])
    if ab:
        md += ["## Ablations: removing one section at a time (12-prompt subset, 1 repeat)", "",
               "Ratio above 1 means more tells without that section.", "",
               table(["Variant", "Tells vs full skill", "Words (variant / full)", "Contractions per 100 words"],
                     [[a["variant"], ci(a["ratio_vs_full"]), f"{a['words_variant']:.0f} / {a['words_full']:.0f}", f"{a['contractions_variant']:.1f}"] for a in ab]), ""]
    mt = s.get("multiturn_by_turn", {})
    if mt:
        turns = sorted(mt.get("A-none", mt.get("C-skill-v1", {})), key=lambda x: float(x))
        md += ["## Multi-turn: mean tells per reply by turn", "", table(["Turn"] + [CNAME[c] for c in ("A-none", "C-skill-v1")], [[int(float(t))] + [f"{mt.get(c, {}).get(t, float('nan')):.2f}" for c in ("A-none", "C-skill-v1")] for t in turns]), ""]
        if "multiturn_C_slope_per_turn" in s:
            md += [f"Skill v1 trend: {s['multiturn_C_slope_per_turn']:+.3f} tells per reply per turn.", ""]
    idt = s.get("family_identifiability_balanced_accuracy", {})
    if idt:
        md += ["## Family identifiability", "", "Balanced accuracy of a classifier guessing the model family from reply text (5-fold, prompts grouped). Lower means less house style.", "",
               table(["Condition", "Balanced accuracy"], [[CNAME.get(c, c), f"{v:.2f}"] for c, v in idt.items()]), ""]
    j = s.get("judges", {})
    if j:
        rows = []
        for comp, d in j.items():
            for judge, r in d.items():
                if judge == "by_family":
                    continue
                rows.append([comp.replace("C-skill-v1", "Skill v1").replace("A-none", "no skill").replace("D-placebo", "placebo").replace("E-original", "original skill"), judge, r["n"], ci(r["prefers_skill"], pct=True), f"{100 * r['tie_rate']:.0f}%", ci(r["skill_less_ai_like"], pct=True)])
        md += ["## LLM judges (blind pairwise, never from the writer's family)", "", table(["Comparison", "Judge", "Judgments", "Prefers skill reply", "Ties", "Finds skill reply less AI-like"], rows), ""]
        for comp, d in j.items():
            bf = d.get("by_family", {})
            if bf:
                md += [f"By writer family, {comp}:", "", table(["Family", "Prefers skill reply", "Finds skill reply less AI-like"], [[f, ci(x["prefers_skill"], pct=True), ci(x["skill_less_ai_like"], pct=True)] for f, x in bf.items()]), ""]
    fid = s.get("fidelity", {})
    if fid:
        md += ["## Fidelity (graded replies with required facts)", "", table(["Condition", "Replies", "Facts checked", "Missing", "Wrong", "Invented details per reply"],
               [[CNAME.get(c, c), f["replies"], f["facts_checked"], f"{100 * f['missing_rate']:.1f}%", f"{100 * f['wrong_rate']:.1f}%", f"{f['invented_per_reply']:.2f}"] for c, f in fid.items()]), ""]
    fg = s.get("format_compliance_graders", {})
    if fg:
        md += ["## Explicit format requests (graders)", "", table(["Condition", "Followed fully", "Partly or not"], [[CNAME.get(c, c), ci(f["yes"], pct=True), f["partly_or_no"]] for c, f in fg.items()]), ""]
    pp = s.get("pattern_precision_llm", {})
    rb = s.get("robustness")
    if rb:
        md += ["## Robustness: noisy patterns removed or down-weighted", "",
               f"High-precision tells (labeled precision at least 75%): {', '.join(rb['high_precision_tells'])}.", "",
               table(["Family", "High-precision only: vs placebo", "vs no skill", "Precision-weighted: vs placebo", "vs no skill"],
                     [[f, ci(rb["tells_high_precision"][f]["C/D"]), ci(rb["tells_high_precision"][f]["C/A"]), ci(rb["tells_weighted"][f]["C/D"]), ci(rb["tells_weighted"][f]["C/A"])]
                      for f in FAMS + ["All"] if f in rb["tells_high_precision"]]), ""]
    if pp:
        md += ["## Pattern precision (LLM labelers)", "", f"Labeler agreement: {s.get('labeler_agreement', 'n/a')}.", "",
               table(["Tell", "Precision", "Labels"], [[t, ci(v["precision"], pct=True), v["labels"]] for t, v in sorted(pp.items(), key=lambda x: x[1]["precision"][0])]), ""]
    h = s.get("human", {})
    if h:
        md += ["## Human review", "", f"Pairs answered: {h.get('pairs_answered')}. Phrase checks answered: {h.get('matches_answered')}.", ""]
        rows = [[k, v["n"], ci(v["prefers_skill"], pct=True), v["ties"], ci(v["skill_less_ai_like"], pct=True)] for k, v in h.items() if isinstance(v, dict) and "prefers_skill" in v]
        if rows:
            md += [table(["Comparison", "Pairs", "Prefers skill reply", "Ties", "Finds skill reply less AI-like"], rows), ""]
        if "self_consistency_prefer" in h:
            md += [f"Self-consistency on repeated pairs: preference {100 * h['self_consistency_prefer']:.0f}%, AI-like {100 * h['self_consistency_ai_like']:.0f}%.", ""]
        ja = h.get("judge_agreement_with_human", {})
        if ja:
            pct = lambda x: "n/a" if x is None else f"{100 * x:.0f}%"
            md += ["Judge agreement with the human. Raw agreement counts ties, which the human used on 40% of pairs and the judges almost never did; the decisive columns use only pairs where both picked a side.", "",
                   table(["Judge", "Pairs", "Same preference (raw)", "Same AI-like call (raw)", "Same preference (decisive)", "Same AI-like call (decisive)"],
                         [[k, v["n"], pct(v["prefer_agreement"]), pct(v["ai_like_agreement"]), f"{pct(v.get('prefer_agreement_decisive'))} of {v.get('n_prefer_decisive', 0)}", f"{pct(v.get('ai_like_agreement_decisive'))} of {v.get('n_ai_like_decisive', 0)}"] for k, v in ja.items()]), ""]
        if h.get("pattern_precision_human_overall"):
            md += [f"Human-checked pattern precision overall: {ci(h['pattern_precision_human_overall'], pct=True)}.", ""]
    (RES / "TABLES.md").write_text("\n".join(md))
    print("wrote", RES / "TABLES.md", "|", len(md), "lines")


if __name__ == "__main__":
    main()
