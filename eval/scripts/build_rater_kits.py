"""Build blind rating kits for the round 3 human review.

Each kit is one self-contained HTML file (the app in ../rater-kit/app.html with
the kit's data embedded). A kit has several short sessions. Each session uses
one model and has two batches of replies: one batch written without the skill
and one written with it. Raters work in pairs: both get the same prompts in the
same positions, with the conditions swapped, and the order of conditions
alternates between sessions. The answer key, with conditions and the character
span of every tappable sentence, is written separately and never goes into a kit.

Example:
  python scripts/build_rater_kits.py --out ../round3/kits --raters "Jay,Rater 2,Rater 3"
"""
import argparse
import hashlib
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "rater-kit" / "app.html"
PLACEHOLDER = "/*KIT*/null"

FAMILY = {"claude": "Claude", "gpt": "GPT", "gemini": "Gemini", "grok": "Grok", "mai": "MAI"}
DEFAULT_MODELS = ["claude-opus-5.5", "gpt-6.1-sol", "gemini-3.8-flash", "grok-4.7", "mai-code-1.1-flash"]
CONDS = ("A-none", "C-skill-v1")
# The two prompts the round 1 rater flagged as stilted (both real WildChat messages).
DEFAULT_EXCLUDE = {"wc-28", "wc-03"}
LEAK = re.compile(r"(?i)\blogged\b[^\n]{0,40}\btodos?\b")


# ---------------------------------------------------------------- segmenting

FENCE = re.compile(r"^\s*```")
TABLE_ROW = re.compile(r"^\s*\|.+\|\s*$")
TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$")
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
HR = re.compile(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$")
QUOTE = re.compile(r"^\s*>\s?")
LIST = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+")
SENT = re.compile(r"([.!?\u2026]+(?:\*\*|__|\*|_|~~|[\"'\u201d\u2019)\]])*)(\s+)(?=(?:\*\*|__|\*|_|[\"'\u201c\u2018(\[])*[A-Z0-9])")
ABBR = re.compile(r"(?i)(?:\b(?:e\.g|i\.e|vs|etc|approx|dr|mr|mrs|ms|st|no|jr|sr|u\.s|a\.m|p\.m)|(?:^|\s)[A-Z])\.$")


class Doc:
    """Turns one reply into render blocks for the app and unit spans for the key."""

    def __init__(self, text):
        self.text = text
        self.units = []  # (k, start, end)

    def unit(self, start, end, render):
        k = len(self.units)
        self.units.append((k, start, end))
        return {"k": k, "r": render}

    # inline: sentence units with balanced emphasis markers
    @staticmethod
    def _code_spans(s):
        spans, i = [], 0
        while True:
            a = s.find("`", i)
            if a < 0:
                return spans
            j = a
            while j < len(s) and s[j] == "`":
                j += 1
            b = s.find(s[a:j], j)
            if b < 0:
                return spans
            spans.append((a, b + (j - a)))
            i = b + (j - a)

    @staticmethod
    def _toggles(s, code):
        def in_code(p):
            return any(a <= p < b for a, b in code)
        toks, i = [], 0
        while i < len(s):
            if in_code(i):
                i += 1
                continue
            two = s[i:i + 2]
            if two in ("**", "__", "~~"):
                toks.append((i, 2, "s" if two == "~~" else "b", two))
                i += 2
                continue
            c = s[i]
            if c in "*_":
                prev = s[i - 1] if i else " "
                nxt = s[i + 1] if i + 1 < len(s) else " "
                if not (c == "_" and prev.isalnum() and nxt.isalnum()) and not (prev.isspace() and nxt.isspace()):
                    toks.append((i, 1, "i", c))
            i += 1
        active, open_at = [], {}
        for p, ln, kind, mark in toks:
            prev = s[p - 1] if p else " "
            nxt = s[p + ln] if p + ln < len(s) else " "
            if kind in open_at:
                if not prev.isspace():
                    active.append((p, ln, kind, mark, "close"))
                    del open_at[kind]
            elif not nxt.isspace():
                open_at[kind] = len(active)
                active.append((p, ln, kind, mark, "open"))
        drop = set(open_at.values())
        return [a for n, a in enumerate(active) if n not in drop]

    def sentences(self, s, offset):
        code = self._code_spans(s)
        toggles = self._toggles(s, code)
        cuts = []
        for m in SENT.finditer(s):
            end_prev, start_next = m.end(1), m.end(2)
            if any(a <= m.start(1) < b for a, b in code):
                continue
            if ABBR.search(s[max(0, m.start(1) - 6):m.start(1) + 1]):
                continue
            cuts.append((end_prev, start_next))
        pieces, start = [], 0
        for end_prev, start_next in cuts:
            pieces.append((start, end_prev))
            start = start_next
        pieces.append((start, len(s)))

        def open_marks(x):
            # emphasis markers still open at position x, in the order they were opened
            st = {}
            for p, ln, kind, mark, act in toggles:
                if act == "open":
                    if p >= x:
                        break
                    st[kind] = (p, mark)
                else:
                    if p + ln > x:
                        break
                    st.pop(kind, None)
            return [mark for _, mark in sorted(st.values())]

        out = []
        for a, b in pieces:
            while a < b and s[a].isspace():
                a += 1
            while b > a and s[b - 1].isspace():
                b -= 1
            if not re.sub(r"[*_~`\s]", "", s[a:b]):
                continue
            pre = open_marks(a)
            post = open_marks(b)
            render = "".join(pre) + s[a:b] + "".join(reversed(post))
            out.append(self.unit(offset + a, offset + b, render))
        return out

    # blocks
    def parse(self):
        lines, pos = [], 0
        for line in self.text.split("\n"):
            lines.append((line, pos))
            pos += len(line) + 1
        return self._blocks(lines)

    def _blocks(self, lines):
        out, i = [], 0
        while i < len(lines):
            line, off = lines[i]
            if not line.strip():
                i += 1
                continue
            if FENCE.match(line):
                j = i + 1
                while j < len(lines) and not FENCE.match(lines[j][0]):
                    j += 1
                end_line = lines[min(j, len(lines) - 1)]
                body = "\n".join(l for l, _ in lines[i + 1:j])
                out.append({"t": "code", "u": self.unit(off, end_line[1] + len(end_line[0]), body)})
                i = j + 1
                continue
            if TABLE_ROW.match(line) and i + 1 < len(lines) and TABLE_SEP.match(lines[i + 1][0]):
                head = self.unit(off, off + len(line), "")
                head["cells"] = self._cells(line)
                rows, j = [], i + 2
                while j < len(lines) and TABLE_ROW.match(lines[j][0]):
                    u = self.unit(lines[j][1], lines[j][1] + len(lines[j][0]), "")
                    u["cells"] = self._cells(lines[j][0])
                    rows.append(u)
                    j += 1
                out.append({"t": "table", "head": head, "rows": rows})
                i = j
                continue
            hm = HEADING.match(line)
            if hm:
                out.append({"t": "h", "level": len(hm.group(1)), "u": self.unit(off, off + len(line), hm.group(2))})
                i += 1
                continue
            if HR.match(line):
                out.append({"t": "hr", "u": self.unit(off, off + len(line), "")})
                i += 1
                continue
            if QUOTE.match(line):
                inner, j = [], i
                while j < len(lines) and QUOTE.match(lines[j][0]):
                    m = QUOTE.match(lines[j][0])
                    inner.append((lines[j][0][m.end():], lines[j][1] + m.end()))
                    j += 1
                out.append({"t": "quote", "c": self._blocks(inner)})
                i = j
                continue
            if LIST.match(line):
                block, i = self._list(lines, i, len(LIST.match(line).group(1)))
                out.append(block)
                continue
            para, j = [], i
            while j < len(lines):
                l2 = lines[j][0]
                if not l2.strip() or FENCE.match(l2) or HEADING.match(l2) or HR.match(l2) or QUOTE.match(l2) or LIST.match(l2):
                    break
                if TABLE_ROW.match(l2) and j + 1 < len(lines) and TABLE_SEP.match(lines[j + 1][0]):
                    break
                para.append(lines[j])
                j += 1
            out.append({"t": "p", "lines": [u for u in (self.sentences(l, o) for l, o in para) if u]})
            i = j
        return out

    def _list(self, lines, i, indent):
        first = LIST.match(lines[i][0])
        ordered = first.group(2)[0].isdigit()
        block = {"t": "list", "ordered": ordered, "items": []}
        if ordered:
            block["start"] = int(re.match(r"\d+", first.group(2)).group(0))
        while i < len(lines):
            line, off = lines[i]
            m = LIST.match(line)
            if not line.strip():
                nxt = lines[i + 1][0] if i + 1 < len(lines) else ""
                nm = LIST.match(nxt)
                if nm and len(nm.group(1)) >= indent:
                    i += 1
                    continue
                break
            if m and len(m.group(1)) == indent:
                body = line[m.end():]
                block["items"].append({"lines": [self.sentences(body, off + m.end())], "c": []})
                i += 1
                continue
            if m and len(m.group(1)) > indent and block["items"]:
                sub, i = self._list(lines, i, len(m.group(1)))
                block["items"][-1]["c"].append(sub)
                continue
            if not m and len(line) - len(line.lstrip()) > indent and block["items"]:
                stripped = len(line) - len(line.lstrip())
                block["items"][-1]["lines"].append(self.sentences(line[stripped:], off + stripped))
                i += 1
                continue
            break
        return block, i

    @staticmethod
    def _cells(line):
        row = line.strip()
        if row.startswith("|"):
            row = row[1:]
        if row.endswith("|"):
            row = row[:-1]
        return [c.strip() for c in row.split("|")]


def segment(text):
    doc = Doc(text)
    blocks = doc.parse()
    return blocks, doc.units


# ---------------------------------------------------------------- selection

def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def family(model):
    return FAMILY.get(model.split("-")[0], model)


def load_pool(models, exclude, max_reply_words, max_prompt_words):
    prompts = {}
    for name in ("test1", "test2"):
        for p in read_jsonl(ROOT / "prompts" / f"{name}.jsonl"):
            prompts[p["id"]] = dict(p, set=name)
    replies = {}
    for name in ("replies.jsonl", "replies_round2.jsonl"):
        for r in read_jsonl(ROOT / "results" / name):
            if r["set"] in ("test1", "test2") and r["rep"] == 1 and r.get("turn") is None and r["cond"] in CONDS and r["model"] in models:
                replies[(r["model"], r["prompt_id"], r["cond"])] = r
    pool = {m: [] for m in models}
    for pid, p in sorted(prompts.items()):
        if pid in exclude or len(p["text"].split()) > max_prompt_words:
            continue
        for m in models:
            pair = [replies.get((m, pid, c)) for c in CONDS]
            if all(pair) and all(len(r["text"].split()) <= max_reply_words and not LEAK.search(r["text"]) for r in pair):
                pool[m].append(pid)
    return prompts, replies, pool


def item_id(rng, taken):
    while True:
        iid = "".join(rng.choice("abcdefghjkmnpqrstuvwxyz23456789") for _ in range(6))
        if iid not in taken:
            taken.add(iid)
            return iid


def build(args):
    models = args.models
    prompts, replies, pool = load_pool(models, set(args.exclude), args.max_reply_words, args.max_prompt_words)
    order = {}
    for m in models:
        ids = list(pool[m])
        random.Random(f"{args.seed}|{m}").shuffle(ids)
        order[m] = ids
    raters = [r.strip() for r in args.raters.split(",") if r.strip()]
    kits, key = [], {"built_with": "build_rater_kits.py", "seed": args.seed, "models": models, "kits": {}}
    for r_idx, rater in enumerate(raters):
        # Raters work in pairs: both members of a pair get the same models and prompts in the
        # same positions, with conditions swapped, so every prompt is read both ways.
        pair, member = divmod(r_idx, 2)
        rng = random.Random(f"{args.seed}|kit|{r_idx}|{rater}")
        kit_id = hashlib.sha256(f"{args.seed}|{r_idx}|{rater}".encode()).hexdigest()[:10]
        used = set()
        taken = set()
        kit = {"kit_id": kit_id, "rater": "" if args.blank_names else rater, "contact": args.contact, "sessions": []}
        kkey = {"rater": rater, "pair": pair, "member": member, "sessions": []}
        for s in range(args.sessions):
            m = models[(pair + s) % len(models)]
            free = [p for p in order[m] if p not in used]
            if len(free) < 2 * args.per_block:
                raise SystemExit(f"not enough prompts for {m} (rater {rater}, session {s + 1})")
            shift = (pair * (2 * args.per_block + 1)) % len(free)
            chosen = (free[shift:] + free[:shift])[:2 * args.per_block]
            used.update(chosen)
            halves = [chosen[:args.per_block], chosen[args.per_block:]]
            first = CONDS[(member + s) % 2]
            conds = [first, CONDS[1] if first == CONDS[0] else CONDS[0]]
            sess = {"id": f"s{s + 1}", "blocks": []}
            skey = {"id": f"s{s + 1}", "model": m, "family": family(m), "blocks": []}
            for b, (cond, pids) in enumerate(zip(conds, halves), 1):
                pids = list(pids)
                rng.shuffle(pids)
                block = {"id": f"s{s + 1}b{b}", "items": []}
                bkey = {"id": f"s{s + 1}b{b}", "cond": cond, "items": []}
                for pid in pids:
                    r = replies[(m, pid, cond)]
                    blocks, units = segment(r["text"])
                    iid = item_id(rng, taken)
                    block["items"].append({"id": iid, "prompt": prompts[pid]["text"], "doc": blocks})
                    bkey["items"].append({"id": iid, "set": prompts[pid]["set"], "prompt_id": pid,
                                          "category": prompts[pid]["category"], "source": prompts[pid]["source"],
                                          "model": m, "family": family(m), "cond": cond,
                                          "words": len(r["text"].split()), "reply": r["text"],
                                          "units": [list(u) for u in units]})
                sess["blocks"].append(block)
                skey["blocks"].append(bkey)
            kit["sessions"].append(sess)
            kkey["sessions"].append(skey)
        kits.append((rater, kit))
        key["kits"][kit_id] = kkey
    return kits, key, pool


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, help="Output folder for kits and key.json. Keep it outside the repo if kits hold private prompts.")
    ap.add_argument("--raters", required=True, help="Comma-separated rater names, one kit each.")
    ap.add_argument("--blank-names", action="store_true", help="Leave the name empty in kits so raters type it.")
    ap.add_argument("--contact", default="Jay", help="Who raters send results to, shown in the app.")
    ap.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    ap.add_argument("--sessions", type=int, default=4)
    ap.add_argument("--per-block", type=int, default=4)
    ap.add_argument("--max-reply-words", type=int, default=400)
    ap.add_argument("--max-prompt-words", type=int, default=120)
    ap.add_argument("--exclude", nargs="*", default=sorted(DEFAULT_EXCLUDE))
    ap.add_argument("--seed", default="round3-shared-v1")
    args = ap.parse_args()

    kits, key, pool = build(args)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    template = APP.read_text(encoding="utf-8")
    if PLACEHOLDER not in template:
        raise SystemExit(f"placeholder {PLACEHOLDER} not found in {APP}")
    for rater, kit in kits:
        data = json.dumps(kit, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        slug = re.sub(r"[^a-z0-9]+", "-", rater.lower()).strip("-") or kit["kit_id"]
        (out / f"plain-voice-rating-{slug}.html").write_text(template.replace(PLACEHOLDER, data), encoding="utf-8")
    (out / "key.json").write_text(json.dumps(key, ensure_ascii=False, indent=1), encoding="utf-8")
    print("eligible prompts per model:", {m: len(v) for m, v in pool.items()})
    print(f"wrote {len(kits)} kits and key.json to {out}")


if __name__ == "__main__":
    main()
