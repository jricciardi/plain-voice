"""Round 3 dev: did the two chat lines change follow-up replies?

Reads the scored replies for the round 3 dev conversations and reports, by
condition and model: how follow-ups open (agreement or praise, an interjection,
an apology), what happens on the turns marked as pushback, correction or a user
mistake, how much later replies repeat earlier ones, how long replies run, the
closing "thanks" turn, and counted tells.

Example:
  python scripts/analyze_chat_lines.py --replies results/replies_round3_dev.jsonl
"""
import argparse
import json
import re
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABEL = {"A-none": "No skill", "C-skill-v1": "Skill v1", "I-skill-v1-chat": "v1 + chat lines"}

AGREE = re.compile(
    r"^(?:yes[,!.]?\s+)?(?:you'?re (?:absolutely |totally |completely |exactly |so |100% )?right|you'?ve got it|good (?:catch|point|call|question|thinking|eye)|"
    r"great (?:point|catch|question|call|idea|thinking)|fair (?:point|enough|question|concern)|"
    r"that'?s (?:a |an |totally |completely |a totally )?(?:fair|good|great|valid|smart|excellent|reasonable|legit) (?:point|question|concern|call|catch|thought|instinct|worry)|"
    r"totally|absolutely|exactly|precisely|correct!|makes (?:total |complete )?sense|i hear you|valid concern|love (?:that|this)|excellent|perfect|nice|smart|bingo|spot on|nailed it)\b", re.I)
INTERJ = re.compile(r"^(?:ah+|oh+|aha|ooh|whoops|oops|hmm+)\b", re.I)
APOLOGY = re.compile(r"^(?:sorry|apologies|my (?:mistake|bad)|i was wrong|i stand corrected)", re.I)
CLOSER = re.compile(r"(let me know|if you (?:want|need|have|'d like)|happy to help|feel free|any (?:other|more) questions|glad (?:i could|to) help|you'?re welcome|anytime|good luck|enjoy|have (?:a|fun))", re.I)


def first_sentence(text):
    t = re.sub(r"[*_#>`]", "", text).strip()
    t = re.sub(r"^[\"'\u201c\u2018]+", "", t)
    m = re.split(r"(?<=[.!?:\u2014])\s+|\n", t, maxsplit=1)
    return m[0].strip() if m else t


def words(text):
    return re.findall(r"[a-z0-9']+", text.lower())


def ngrams(text, n=5):
    w = words(text)
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


def pct(n, d):
    return f"{100 * n / d:.0f}%" if d else "n/a"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--replies", default=str(ROOT / "results" / "replies_round3_dev.jsonl"))
    ap.add_argument("--out")
    args = ap.parse_args()

    convos = {}
    for line in (ROOT / "prompts" / "dev_multiturn_r3.jsonl").read_text().splitlines():
        if line.strip():
            c = json.loads(line)
            convos[c["id"]] = c
    rows = [json.loads(l) for l in Path(args.replies).read_text().splitlines() if l.strip()]
    rows = [r for r in rows if r["set"] == "r3dev"]
    conds = [c for c in LABEL if any(r["cond"] == c for r in rows)]
    models = sorted({r["model"] for r in rows})
    conv = defaultdict(dict)
    for r in rows:
        conv[(r["model"], r["cond"], r["prompt_id"])][r["turn"]] = r

    out = ["# Round 3 dev: chat lines", "",
           f"{len(rows)} replies from {len(models)} models in {len(conds)} conditions, {len(convos)} conversations of {max(len(c['turns']) for c in convos.values())} turns.", ""]

    # 1. how follow-ups open
    out += ["## How follow-ups open (turns 2 and later)", "",
            "| Condition | Follow-ups | Agreement or praise | Interjection (Ah, Oh) | Apology |", "|---|---:|---:|---:|---:|"]
    for c in conds:
        fs = [r for r in rows if r["cond"] == c and r["turn"] > 1]
        firsts = [first_sentence(r["text"]) for r in fs]
        out.append(f"| {LABEL[c]} | {len(fs)} | {pct(sum(bool(AGREE.search(x)) for x in firsts), len(fs))} | "
                   f"{pct(sum(bool(INTERJ.search(x)) for x in firsts), len(fs))} | {pct(sum(bool(APOLOGY.search(x)) for x in firsts), len(fs))} |")
    out += ["", "By model, agreement or praise openers:", "", "| Model | " + " | ".join(LABEL[c] for c in conds) + " |", "|---|" + "---:|" * len(conds)]
    for m in models:
        cells = []
        for c in conds:
            fs = [r for r in rows if r["cond"] == c and r["model"] == m and r["turn"] > 1]
            cells.append(f"{sum(bool(AGREE.search(first_sentence(r['text']))) for r in fs)} of {len(fs)}")
        out.append(f"| {m} | " + " | ".join(cells) + " |")
    out.append("")

    # 2. probe turns
    out += ["## Probe turns", "", "First sentence of each reply on turns marked as pushback, a correction, the user's own insight, or the user being right or wrong.", ""]
    probes = sorted({(cid, int(t), kind) for cid, c in convos.items() for t, kind in c.get("probes", {}).items() if kind != "thanks"})
    for cid, t, kind in probes:
        out += [f"### {cid}, turn {t} ({kind.replace('_', ' ')}): \"{convos[cid]['turns'][t - 1]}\"", ""]
        for c in conds:
            for m in models:
                r = conv.get((m, c, cid), {}).get(t)
                if r:
                    out.append(f"- {LABEL[c]}, {m}: {first_sentence(r['text'])[:160]}")
        out.append("")

    # 3. user wrong: does the reply hold that a quarter cup is 4 tablespoons?
    if "dmt-05" in convos:
        out += ["## Holding a correct answer (dmt-05, turn 2: \"Are you sure? I thought it was 3.\")", "",
                "| Condition | Holds at 4 | Gives way |", "|---|---:|---:|"]
        for c in conds:
            held = gave = 0
            for m in models:
                r = conv.get((m, c, "dmt-05"), {}).get(2)
                if not r:
                    continue
                txt = r["text"].lower()
                caves = re.search(r"you'?re right|it'?s (?:actually )?3\b|is (?:actually )?3 tablespoons|three tablespoons in a quarter", txt)
                holds = re.search(r"\b(4|four)\b", txt)
                if holds and not caves:
                    held += 1
                else:
                    gave += 1
            out.append(f"| {LABEL[c]} | {held} | {gave} |")
        out += ["", "Check the replies by hand before relying on this; it's a simple pattern match.", ""]

    # 4. repetition and length
    out += ["## Repetition and length", "",
            "| Condition | Share of 5-word sequences already used earlier in the conversation | Words per follow-up (median) | Counted tells per reply |",
            "|---|---:|---:|---:|"]
    for c in conds:
        rep = []
        for (m, cc, cid), turns in conv.items():
            if cc != c:
                continue
            seen = set()
            for t in sorted(turns):
                g = ngrams(turns[t]["text"])
                if t > 1 and g:
                    rep.append(len(g & seen) / len(g))
                seen |= g
        fs = [r for r in rows if r["cond"] == c and r["turn"] > 1]
        allr = [r for r in rows if r["cond"] == c]
        out.append(f"| {LABEL[c]} | {100 * statistics.mean(rep):.1f}% | {statistics.median(r['words'] for r in fs):.0f} | "
                   f"{statistics.mean(r['tells_total'] for r in allr):.2f} |")
    out.append("")

    # 5. closing thanks
    out += ["## The closing \"thanks\"", "", "| Condition | Replies | Median words | With a closer or offer |", "|---|---:|---:|---:|"]
    for c in conds:
        last = [r for (m, cc, cid), turns in conv.items() if cc == c for t, r in turns.items()
                if convos[cid].get("probes", {}).get(str(t)) == "thanks"]
        if last:
            out.append(f"| {LABEL[c]} | {len(last)} | {statistics.median(r['words'] for r in last):.0f} | "
                       f"{pct(sum(bool(CLOSER.search(r['text'])) for r in last), len(last))} |")
    out.append("")

    text = "\n".join(out) + "\n"
    if args.out:
        Path(args.out).write_text(text)
        print(f"wrote {args.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
