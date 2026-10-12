import json, re, random
import pyarrow.parquet as pq
random.seed(20261012)

EXCLUDE = re.compile(r"(?i)("
  r"```|\bdef\s+\w+\(|\bfunction\s*\(|console\.log|#include|public\s+static|\bimport\s+\w+|SELECT\s+\*|</?\w+>|\{\s*\"|=>|\bnpm\b|\bpip\s+install|"
  r"midjourney|prompt\s+generator|\bDAN\b|jailbreak|ignore\s+(all\s+)?previous|pretend\s+(to\s+be|you)|act\s+as\b|you\s+are\s+now|roleplay|role-play|role\s+play|"
  r"fanfic|fan\s*fiction|\bstory\b|\bstories\b|\bchapter\b|\bnovel\b|\bpoem\b|\blyrics?\b|\brap\b|\bscript\b|\bepisode\b|anime|naruto|sonic|freedom\s+planet|monika|doki|minecraft|"
  r"\bsex|\bnsfw|\bfetish|\berotic|\bkiss|\bboobs?\b|\bnaked|\bhentai|"
  r"translate|translation|paraphrase\s+in|in\s+(chinese|spanish|french|german|russian|arabic)|"
  r"\bgpt-?\d|chatgpt|openai|are\s+you\s+(an?\s+)?(ai|bot|human)|who\s+(made|created)\s+you|your\s+(name|model)|"
  r"https?://|www\.|@\w+\.\w+|\+?\d[\d\s\-()]{8,}\d|"
  r"\bmcq\b|multiple\s+choice|\bquiz\b|answer\s+the\s+following|true\s+or\s+false|fill\s+in\s+the\s+blank|"
  r"\bessay\b|\b\d{3,}\s*words\b|seo|keywords?|"
  r"stable\s+diffusion|dall-?e|image\s+prompt"
r")")
LISTY = re.compile(r"(\n\s*[-*•]\s|\n\s*\d+[.)]\s)")

def first_user(conv):
    for t in conv:
        if t["role"] == "user":
            return t
    return None

cands, seen = [], set()
for shard in ["wildchat/train-00001.parquet", "wildchat/train-00009.parquet"]:
    pf = pq.ParquetFile(shard)
    for rg in range(pf.num_row_groups):
        df = pf.read_row_group(rg, columns=["conversation_hash", "model", "timestamp", "language", "toxic", "redacted", "conversation"]).to_pandas()
        df = df[(df.language == "English") & (~df.toxic) & (~df.redacted)]
        for _, r in df.iterrows():
            u = first_user(r["conversation"])
            if u is None or u["toxic"] or u["redacted"]:
                continue
            text = (u["content"] or "").strip()
            n = len(text.split())
            if n < 8 or n > 260 or EXCLUDE.search(text):
                continue
            alpha = sum(ch.isalpha() for ch in text) / max(1, len(text))
            if alpha < 0.72 or text.count("\n") > 25 or len(LISTY.findall(text)) > 8:
                continue
            key = re.sub(r"\W+", " ", text.lower())[:120]
            if key in seen:
                continue
            seen.add(key)
            cands.append({"hash": r["conversation_hash"], "shard": shard.split("/")[-1], "model": r["model"], "date": str(r["timestamp"])[:10], "text": text, "words": n})
print("candidates after filters:", len(cands))

CATS = {
  "explain": r"(?i)^(why|how\s+(does|do|is|are|can)|what\s+(is|are|causes|happens)|explain|can\s+you\s+explain|what's\s+the\s+difference)",
  "advice": r"(?i)\b(should\s+i|what\s+should\s+i|advice|my\s+(boss|wife|husband|girlfriend|boyfriend|friend|mom|dad|manager|landlord|roommate)|i'?m\s+(thinking|trying|struggling|worried|not\s+sure)|help\s+me\s+decide|is\s+it\s+(worth|ok|okay|normal))",
  "email": r"(?i)\b(write|draft|compose|reply|respond)\b.{0,40}\b(email|e-mail|mail|letter|message|note|text)\b",
  "feedback": r"(?i)\b(improve|feedback|proofread|rewrite|polish|edit|make\s+(it|this)\s+(sound|better|more)|check\s+(my|this)|correct\s+(my|this|the)\s+(grammar|english))\b",
  "tech": r"(?i)\b(which\s+is\s+better|vs\.?|versus|should\s+i\s+use|recommend|best\s+(way|laptop|phone|language|framework|database|tool)|pros\s+and\s+cons|compare)\b",
  "howto": r"(?i)^(how\s+(do|can|to|should)\s+i|how\s+to|steps\s+to|what\s+are\s+the\s+steps|give\s+me\s+(a\s+)?(plan|steps|guide))",
  "marketing": r"(?i)\b(product\s+description|ad\s+copy|slogan|tagline|bio|about\s+us|caption|instagram|linkedin|marketing|promote|sales\s+pitch|cover\s+letter)\b",
  "factual": r"(?i)^(what|when|where|who|which|is|are|does|do|can|how\s+many|how\s+much)\b.{0,140}\?$",
}
for c in cands:
    c["cats"] = [k for k, p in CATS.items() if re.search(p, c["text"])]
pool = []
for k in CATS:
    items = [c for c in cands if k in c["cats"]]
    random.shuffle(items)
    pick = items[:45]
    pool += [{**p, "bucket": k} for p in pick]
    print(f"{k:10s} matches={len(items):5d} sampled={len(pick)}")
seen_h, final = set(), []
for p in pool:
    if p["hash"] not in seen_h:
        seen_h.add(p["hash"]); final.append(p)
random.shuffle(final)
with open("prompt-drafts/wildchat_candidates.jsonl", "w") as f:
    for i, p in enumerate(final):
        p["cid"] = f"wc-cand-{i:03d}"
        f.write(json.dumps(p) + "\n")
print("candidate pool written:", len(final))
