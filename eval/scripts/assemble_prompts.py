"""Assemble the plain-voice evaluation prompt sets.

Sources: real first messages from WildChat-1M (ODC-BY), prompts drafted by
four different model families, and the eight prompts from the first test.
Splits are stratified by category with a fixed seed, before any replies exist.

  dev    : used to tune the skill
  test1  : scored once for skill v1 (this run)
  test2  : sealed; scored once for the revised skill
"""

import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path

SEED = 20261012
ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT.parents[2] / "prompt-drafts"
OUT = ROOT / "prompts"

ORIGINAL = [
    ("orig-1", "explain", "Why do planes leave white trails in the sky, and why do some disappear right away while others stick around for ages?", []),
    ("orig-2", "advice", "I've been at my job for 3 years. I'm good at it but bored. A startup offered me a bigger role with 20% less salary plus equity. I'm 34 and have a mortgage. What would you do?", []),
    ("orig-3", "email", "Write a short email to my team: our weekly sync is moving from Monday 10am to Thursday 2pm starting next week, and the first Thursday session will run long because we'll use it for Q3 planning.",
     ["Sync moves from Monday 10am", "New time is Thursday 2pm", "Change starts next week", "First Thursday session runs long", "The extra time is for Q3 planning"]),
    ("orig-4", "social_post", "Write a LinkedIn post about what I learned in my first year as an engineering manager.", []),
    ("orig-5", "feedback", "Can you give me feedback on the opening of my blog post? \"Every team says they value documentation. Few actually write it. In this post I want to talk about why, and what we did about it on my team.\"", []),
    ("orig-6", "tech", "We're a 5-person startup building a B2B SaaS app. Monolith or microservices?", []),
    ("orig-7", "status_update", "Turn my notes into a quick status update for my manager: migration 70% done, blocked on vendor API rate limits, asked vendor for an increase, eta friday. new hire starts monday. dashboard v2 shipped tuesday, 3 bugs reported, 2 fixed.",
     ["Migration is 70% done", "Blocked on vendor API rate limits", "Asked the vendor for an increase", "ETA is Friday", "New hire starts Monday", "Dashboard v2 shipped Tuesday", "3 bugs reported", "2 bugs fixed"]),
    ("orig-8", "descriptive", "Write about 150 words describing Astoria, Oregon for a travel blog.", []),
]


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def split_counts(items, key, n_test1, n_test2, rng):
    """Stratified split by key with largest-remainder allocation."""
    groups = defaultdict(list)
    for it in items:
        groups[key(it)].append(it)
    for g in groups.values():
        rng.shuffle(g)
    total = len(items)
    targets = {"test1": n_test1, "test2": n_test2, "dev": total - n_test1 - n_test2}
    out = {"test1": [], "test2": [], "dev": []}
    for name in ("test1", "test2"):
        want = targets[name]
        pool = {k: v for k, v in groups.items() if v}
        remaining = sum(len(v) for v in pool.values())
        if remaining == 0:
            continue
        shares = {k: want * len(v) / remaining for k, v in pool.items()}
        alloc = {k: int(s) for k, s in shares.items()}
        short = want - sum(alloc.values())
        for k in sorted(shares, key=lambda k: (shares[k] - alloc[k], len(pool[k])), reverse=True)[:short]:
            alloc[k] += 1
        for k, n in alloc.items():
            n = min(n, len(groups[k]))
            out[name] += groups[k][:n]
            groups[k] = groups[k][n:]
    for g in groups.values():
        out["dev"] += g
    return out


def main():
    rng = random.Random(SEED)
    sets = {"dev": [], "test1": [], "test2": []}

    wc = read_jsonl(DRAFTS / "wildchat_selected.jsonl")
    for r in wc:
        rec = {"id": r["id"], "source": "wildchat", "category": r["category"], "text": r["text"].strip(),
               "required_facts": r.get("required_facts", []), "format_request": r.get("format_request"),
               "meta": {"wildchat_hash": r["hash"], "asks_format": r.get("asks_format", False)}}
        r["_rec"] = rec
    parts = split_counts(wc, lambda r: r["category"], 26, 16, rng)
    for k, v in parts.items():
        sets[k] += [r["_rec"] for r in v]

    def add_drafted(path, n1, n2, make, key):
        rows = read_jsonl(DRAFTS / path)
        parts = split_counts(rows, key, n1, n2, rng)
        for k, v in parts.items():
            sets[k] += [make(r) for r in v]

    add_drafted("summaries.jsonl", 4, 3, lambda r: {"id": r["id"], "source": "drafted-gpt", "category": "summary", "text": r["text"], "required_facts": r["required_facts"], "meta": {"doc_type": r.get("doc_type")}}, lambda r: "all")
    add_drafted("status_updates.jsonl", 4, 3, lambda r: {"id": r["id"], "source": "drafted-gemini", "category": "status_update", "text": r["text"], "required_facts": r["required_facts"], "meta": {"audience": r.get("audience")}}, lambda r: "all")
    sg = read_jsonl(DRAFTS / "stress_genre_words.jsonl")
    for st, n1, n2 in (("genre_trap", 6, 4), ("user_words", 6, 4)):
        rows = [r for r in sg if r["stress_type"] == st]
        parts = split_counts(rows, lambda r: "all", n1, n2, rng)
        for k, v in parts.items():
            sets[k] += [{"id": r["id"], "source": "drafted-grok", "category": st, "stress_type": st, "text": r["text"],
                         "listed_words": r.get("listed_words", []), "required_facts": []} for r in v]
    add_drafted("stress_format.jsonl", 7, 5, lambda r: {"id": r["id"], "source": "drafted-claude", "category": "explicit_format", "stress_type": "explicit_format", "text": r["text"], "format_request": r["format_request"], "required_facts": []}, lambda r: r["format_request"]["type"])

    for pid, cat, text, facts in ORIGINAL:
        sets["dev"].append({"id": pid, "source": "first-test", "category": cat, "text": text, "required_facts": facts})

    mt = read_jsonl(DRAFTS / "multiturn.jsonl")
    rng.shuffle(mt)
    multiturn = {"test1": mt[:4], "test2": mt[4:]}

    OUT.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for name, rows in sets.items():
        rows.sort(key=lambda r: r["id"])
        body = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
        (OUT / f"{name}.jsonl").write_text(body)
        hashes[f"{name}.jsonl"] = hashlib.sha256(body.encode()).hexdigest()
    for name, rows in multiturn.items():
        body = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
        (OUT / f"multiturn_{name}.jsonl").write_text(body)
        hashes[f"multiturn_{name}.jsonl"] = hashlib.sha256(body.encode()).hexdigest()
    (OUT / "SHA256SUMS").write_text("".join(f"{h}  {n}\n" for n, h in sorted(hashes.items())))
    for name, rows in sets.items():
        cats = defaultdict(int)
        for r in rows:
            cats[r["category"]] += 1
        print(f"{name:6s} {len(rows):3d}  {dict(sorted(cats.items()))}")
    print("multiturn", {k: [r["id"] for r in v] for k, v in multiturn.items()})
    print((OUT / "SHA256SUMS").read_text())


if __name__ == "__main__":
    main()
