"""plain-voice tell-counting suite.

Counts surface patterns that the plain-voice skill tells a model to avoid, plus
a watch list of substitutes the skill doesn't name (to catch a model swapping
one tell for another) and plain length/readability metrics.

Rules that keep the counts fair:
- Formatting the user explicitly asked for (a table, headers, bold terms,
  numbered options, a TL;DR, emoji) is not counted for that prompt.
- Words and quoted phrases the user used first are not counted ("the user's
  words are fine").
- Hashtags are recorded but not counted, since they're a genre convention.

Pattern matching is approximate. Its precision is measured separately by
labeling a random sample of matches.
"""

import re

SUITE_VERSION = "2.2"

# ---------------------------------------------------------------- helpers

def _norm(text):
    return (text or "").replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')


def _words(text):
    return re.findall(r"[A-Za-z][A-Za-z'\-]*", _norm(text))


def _mask(m):
    """Blank out a match but keep its length and line breaks, so positions still line up."""
    return re.sub(r"[^\n]", " ", m.group(0))


def _strip_code(text):
    return re.sub(r"```.*?```", _mask, text, flags=re.S)


def _prose(text):
    """Text with code blocks and table rows blanked out. Table cells aren't prose."""
    return re.sub(r"(?m)^[ \t]*\|.*\|[ \t]*$", _mask, _strip_code(text))


class _M(str):
    """A matched string that remembers where it sits in the reply."""


def _mk(s, start, end):
    o = _M(s)
    o.pos, o.endpos = start, end
    return o


VOCAB_CLAUDE = [
    "load-bearing", "does a lot of work", "earns its place", "lands", "quietly", "the shape of",
    "lean into", "leaning into", "unpack", "crisp", "landscape", "north star", "the move", "punchy",
    "throat-clearing",
]
VOCAB_AI = [
    "delve", "delves", "delving", "tapestry", "testament", "pivotal", "crucial", "vibrant", "robust",
    "intricate", "meticulous", "meticulously", "multifaceted", "showcase", "showcases", "showcasing",
    "underscore", "underscores", "underscoring", "foster", "fosters", "fostering", "enhance", "enhances",
    "enhancing", "leverage", "leverages", "leveraging",
]
VOCAB_BROCHURE = [
    "nestled", "perched", "bustling", "iconic", "renowned", "steeped in", "boasts", "rich history",
    "sweeping views", "sweeping view", "charm", "charming", "moody",
]
FILLER_ADVERBS = ["genuinely", "honestly", "truly", "deeply", "really", "actually", "basically", "essentially", "literally"]

EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF\u2B50\u2B06\u2B07\u2B05\u2934\u2935\u203C\u2049]")

# Each tell: name -> (section, function(text, ctx) -> list of match strings)
TELLS = {}


def tell(name, section):
    def deco(fn):
        TELLS[name] = (section, fn)
        return fn
    return deco


def _rx_all(pattern, text, flags=0, offset=0):
    return [_mk(m.group(0), m.start() + offset, m.end() + offset) for m in re.finditer(pattern, text, flags)]


def _head(t, n):
    s = t.lstrip()
    return s[:n], len(t) - len(s)


def _tail(t, n):
    s = t.rstrip()
    return s[-n:], max(0, len(s) - n)


# ---------------------------------------------------------------- punctuation and cadence

@tell("em_dash", "punctuation")
def _em_dash(t, c):
    return _rx_all("\u2014", _prose(t))


@tell("answer_label", "punctuation")
def _answer_label(t, c):
    if c["format"] == "tldr":
        return []
    return _rx_all(
        r"(?im)^[\s>*_#-]*(?:short answer|long answer|bottom line|tl;?\s?dr|key takeaways?|my take|my recommendation|"
        r"rule of thumb|the short version|in short|verdict|quick take|the gist|the upshot|my decision rule|next steps|(?:the )?takeaway)\b[*_\s]*:", t)


@tell("fragment_reveal", "punctuation")
def _fragment_reveal(t, c):
    found = _rx_all(
        r"(?:^|(?<=[.!?:]\s)|(?<=\n))(?:the (?:catch|result|trick|kicker|twist|fix|answer|problem|upshot|good news|bad news|real question|short version|honest answer)"
        r"|what would i do|my (?:answer|take|advice|honest take)|why|how|so what)\?(?=\s)", t, re.I)
    found += _rx_all(r"(?i)\bhere's the (?:thing|deal|kicker|catch)\b", t)
    return found


@tell("shorthand", "punctuation")
def _shorthand(t, c):
    body = _prose(t)
    ok = {"and/or", "his/her", "he/she", "km/h", "w/o", "n/a", "input/output", "read/write", "24/7", "client/server", "pros/cons"}
    slashes = [m for m in _rx_all(r"\b[a-z]{3,}/[a-z]{3,}\b", body) if m.lower() not in ok]
    arrows = _rx_all("\u2192|\u21d2|(?<![<-])->(?!>)", body)
    return slashes + arrows


# ---------------------------------------------------------------- phrases

@tell("stock_opener", "phrases")
def _stock_opener(t, c):
    head, off = _head(t, 80)
    return _rx_all(r"(?i)^[\W_]*(?:certainly|of course|absolutely|sure(?: thing)?|happy to help|i'd be happy to|i'd love to|great|hey there|hi there)\b[!,.]?", head, offset=off)


@tell("praise_opener", "phrases")
def _praise_opener(t, c):
    head, off = _head(t, 220)
    return _rx_all(
        r"(?i)\b(?:great question|good question|excellent question|love (?:this|that|it)|what a (?:great|lovely)|"
        r"(?:great|strong|nice|solid|excellent|good|lovely) (?:start|opener|opening|draft|idea|instinct|question|foundation)|"
        r"(?:it's|this is|that's) (?:a |an )?(?:great|strong|solid|excellent|fantastic|good|really good) (?:start|opening|opener|draft|question|idea|hook|place)|"
        r"congrats|congratulations)\b", head, offset=off)


@tell("reframe", "phrases")
def _reframe(t, c):
    return _rx_all(
        r"(?i)\b(?:i'?d|i would|let's|it helps to) (?:treat|frame|think of|look at) (?:this|it) (?:less )?as\b|"
        r"\bthis (?:isn't|is not) (?:really |just )?(?:a|an|about)\b[^.\n]{0,40}(?:question|decision|problem|choice)|"
        r"\bthe real question (?:is|here)\b|\breframe\b", t)


@tell("signpost", "phrases")
def _signpost(t, c):
    return _rx_all(
        r"(?i)\bhere(?:'s| is| are) (?:how|why|what|where|the (?:breakdown|rundown|short version|deal|plan)|"
        r"a (?:quick |simple |clean |short )?(?:breakdown|rundown|overview|framework|way to think))\b|"
        r"\blet me break (?:it|this|that) down\b|\blet's (?:break (?:it|this) down|dig in|dive in|unpack)\b|"
        r"\b(?:a few|some|three|two|four) (?:things|thoughts|notes|tips|suggestions|questions|options) (?:to (?:consider|keep in mind|think about)|worth)\b", _norm(t))


@tell("draft_preamble", "phrases")
def _draft_preamble(t, c):
    head, off = _head(t, 120)
    return _rx_all(r"(?i)^[\W_]*here(?:'s| is) (?:a|an|your|the|my) (?:quick |short |clean |polished |revised |updated |possible |draft |simple )*(?:draft|version|rewrite|revision|update|email|message|post|take|option|summary|breakdown)\b", _norm(head), offset=off)


@tell("filler_adverb", "phrases")
def _filler_adverb(t, c):
    out = []
    for w in FILLER_ADVERBS:
        if w in c["prompt_words"]:
            continue
        out += _rx_all(rf"(?i)\b{w}\b", t)
    return out


@tell("real_intensifier", "phrases")
def _real_intensifier(t, c):
    return _rx_all(
        r"(?i)\b(?:is|are|feels|gets) (?:very |pretty )?real\b(?! estate| world| time| number| name)|"
        r"\ba real (?:signal|risk|cost|win|problem|question|concern|issue|reason|step|difference|upside|downside|payoff|pain|tradeoff|advantage|constraint)\b|"
        r"\bthe real (?:win|work|question|risk|cost|problem|issue|reason|value|answer|test|lesson|job|skill|shift|story)\b", t)


@tell("contrast_formula", "phrases")
def _contrast(t, c):
    t2 = _norm(t)
    pats = [
        r"(?i)\bnot (?:just|only|merely|simply)\b[^.\n]{0,80}?\b(?:but|it's|it is|they're)\b",
        r"(?i)\b(?:it|this|that|which)(?:'s| is| was) not\b[^.!?\n]{0,70}?[,;\u2014:]\s*(?:it|this|that)(?:'s| is| was)\b",
        r"(?i)\b(?:isn't|is not|aren't|are not|wasn't|was not)\b[^.!?\n]{0,70}?[,;\u2014]\s*(?:it|this|that|they)(?:'s| is| are| was)\b",
        r"(?i)\b(?:isn't|is not|aren't|wasn't|doesn't|don't)\b[^.!?\n]{0,80}[.!]\s+(?:it|they|that|this)(?:'s| is| are| was)\b",
        r"(?i)\bless (?:about |of )?[\w-]+(?: [\w-]+){0,4},? (?:and )?more (?:about |of )?\b",
        r"(?i)\bnot because\b[^.\n]{0,80}\bbut because\b",
        r"(?<=[a-z]), not (?:a |an |the )?[a-z][\w-]*(?: [a-z][\w-]*)?[.!](?=\s|$)",
    ]
    out = []
    for p in pats:
        out += _rx_all(p, t2)
    return out


@tell("slogan", "phrases")
def _slogan(t, c):
    t2 = _norm(t)
    beats = _rx_all(r"(?i)\b[\w'-]+(?: [\w'-]+){0,3} beats? (?:a |an |the )?[\w'-]+(?: [\w'-]+){0,3}[.!]", t2)
    over = [m for m in _rx_all(r"(?m)(?:^|(?<=[.!?]\s))(?:[-*\u2022]\s+)?(?:\*\*)?[A-Z][a-z'-]+(?: [a-z'-]+)? over (?!(?:the|a|an|my|your|his|her|their|our|it|there)\b)[a-z'-]+(?: [a-z'-]+)?[.!](?:\*\*)?(?=\s|$)", t2)
            if not re.match(r"(?:[-*\u2022]\s+)?(?:\*\*)?(?:he|she|it|they|we|i|you|this|that|there|then)\b", m, re.I)]
    return beats + over


@tell("significance", "phrases")
def _significance(t, c):
    return _rx_all(
        r"(?i)\bthis matters because\b|\bwhy (?:this|it) matters\b|\bthe key (?:insight|takeaway|point|thing|lesson)\b|"
        r"\bworth noting\b|\bit'?s (?:important|worth|crucial|critical) to (?:note|remember|keep in mind|recognize)\b|"
        r"\bimportantly\b|\bcrucially\b|,\s(?:highlighting|underscoring|emphasizing|showcasing|reflecting|cementing|marking) (?:its|the|their|how|a)\b|"
        r"\b(?:serves|stands) as\b", _norm(t))


@tell("scare_quotes", "phrases")
def _scare_quotes(t, c):
    t2 = _norm(t)
    out = []
    for m in re.finditer(r'(?<![\w"])"([a-z][a-z\'-]*(?: [a-z][a-z\'-]*){0,2})"(?![\w"])', t2):
        inner = m.group(1).lower()
        if inner in c["prompt_lower"]:
            continue
        out.append(_mk(m.group(0), m.start(), m.end()))
    return out


@tell("unnamed_authority", "phrases")
def _unnamed_authority(t, c):
    return _rx_all(
        r"(?i)\b(?:experts|economists|researchers|psychologists|analysts) (?:say|agree|suggest|recommend|argue|warn)\b|"
        r"\bstudies (?:show|suggest|have shown|find|found)\b|\bresearch (?:shows|suggests|has shown)\b|\bindustry reports\b|"
        r"\baccording to (?:experts|studies|research)\b|\bmany (?:experts|people) (?:say|believe|agree)\b", t)


@tell("disclaimer", "phrases")
def _disclaimer(t, c):
    return _rx_all(
        r"(?i)\bnot (?:financial|legal|medical|tax|professional) advice\b|"
        r"\b(?:consult|talk to|speak with|check with) (?:a|an|your|with a) (?:qualified |licensed |certified )?(?:professional|financial (?:advisor|planner)|advisor|lawyer|attorney|doctor|accountant|tax professional)\b|"
        r"\bas an ai\b|\bi'?m (?:just )?an ai\b|\bi (?:can't|cannot) (?:provide|give) (?:financial|legal|medical) advice\b", t)


@tell("padding", "phrases")
def _padding(t, c):
    return _rx_all(
        r"(?i)\b(?:thanks|thank you|i appreciate) (?:everyone |all )?(?:for )?(?:your |everyone's )?(?:flexibility|patience|understanding|cooperation)\b|"
        r"\bi hope this (?:email|message|note) finds you well\b|\bhope you're (?:doing )?well\b|"
        r"\bplease (?:don't hesitate|feel free) to (?:reach out|contact|let me know)\b", t)


@tell("offer_closer", "phrases")
def _offer_closer(t, c):
    tail, off = _tail(t, 380)
    return _rx_all(
        r"(?i)\bif you(?:'d| would)? (?:want|like)\b|\bwant me to\b|\bwould you like\b|\bdo you want me to\b|"
        r"\blet me know if\b|\bhappy to (?:help|adjust|tweak|expand|dig|go|walk|draft|write|refine|rework|share|put)\b|"
        r"\bi can also\b|\bfeel free to\b|\bshall i\b|\bjust say the word\b|\bif (?:it|that) helps, i can\b", _norm(tail), offset=off)


@tell("hope_closer", "phrases")
def _hope_closer(t, c):
    tail, off = _tail(t, 220)
    return _rx_all(r"(?i)\bhope (?:this|that) helps\b|\bgood luck\b|\bbest of luck\b|\byou(?:'ve)? got this\b|\bhappy (?:writing|planning|travels|traveling|coding|budgeting)\b|\bcheers\b", _norm(tail), offset=off)


@tell("recap", "phrases")
def _recap(t, c):
    return _rx_all(r"(?im)^[\s*_#>-]*(?:in summary|in conclusion|to sum up|to summarize|overall|in short|all in all|ultimately)\b[,:]", t)


# ---------------------------------------------------------------- vocabulary

@tell("listed_vocab", "vocabulary")
def _listed_vocab(t, c):
    out = []
    low = _norm(t).lower()
    for w in VOCAB_CLAUDE + VOCAB_AI + VOCAB_BROCHURE:
        if w in c["prompt_lower"]:
            continue
        out += [_mk(t[m.start():m.end()], m.start(), m.end()) for m in re.finditer(rf"(?<![\w-]){re.escape(w)}(?![\w-])", low)]
    out += _rx_all(r"(?m)(?:^|(?<=[.!?]\s))Additionally,", t)
    return out


# ---------------------------------------------------------------- structure

@tell("md_header", "structure")
def _md_header(t, c):
    if c["format"] in ("headers_bullets", "outline", "schedule"):
        return []
    return _rx_all(r"(?m)^#{1,6}\s+\S.*$", _strip_code(t))


@tell("bold_header_line", "structure")
def _bold_header_line(t, c):
    if c["format"] in ("headers_bullets", "outline", "bold_terms", "schedule"):
        return []
    return _rx_all(r"(?m)^\s*(?:\d+[.)]\s*)?\*\*[^*\n]{2,80}\*\*:?\s*$", _prose(t))


@tell("bold_label", "structure")
def _bold_label(t, c):
    if c["format"] in ("bold_terms", "schedule"):
        return []
    return _rx_all(r"(?m)^\s*(?:[-*\u2022]|\d+[.)])?\s*\*\*[^*\n]{1,60}?(?::\*\*|\*\*\s*:)", _prose(t))


@tell("bold_inline", "structure")
def _bold_inline(t, c):
    if c["format"] in ("bold_terms", "headers_bullets", "outline"):
        return []
    body = _prose(t)
    spans = _rx_all(r"\*\*[^*\n]{1,120}\*\*", body)
    raw = dict(c, format=None)
    heads = _bold_header_line(body, raw) + _bold_label(body, raw)
    n = max(0, len(spans) - len(heads))
    inline = [s for s in spans if not any(h.pos < s.endpos and s.pos < h.endpos for h in heads)]
    return (inline + [s for s in spans if s not in inline])[:n] if n else []


@tell("emoji", "structure")
def _emoji(t, c):
    if c["format"] == "checklist_emoji":
        return []
    return [_mk(m.group(0), m.start(), m.end()) for m in EMOJI.finditer(t)]


@tell("horizontal_rule", "structure")
def _hr(t, c):
    return _rx_all(r"(?m)^\s*(?:-{3,}|\*{3,}|_{3,})\s*$", _strip_code(t))


@tell("table", "structure")
def _table(t, c):
    if c["format"] in ("table", "schedule"):
        return []
    return _rx_all(r"(?m)^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$", t)


@tell("option_menu", "structure")
def _option_menu(t, c):
    if c["format"] == "n_options":
        return []
    return _rx_all(r"(?im)^[\s>#*_-]*(?:option|version|variant|alternative)\s*(?:\d+|[a-c]\b|one|two|three)\b", t)


# ---------------------------------------------------------------- watch list (not scored)

WATCH = {
    "en_dash_spaced": r" \u2013 ",
    "spaced_hyphen_dash": r"(?<=\w) - (?=\w)",
    "double_hyphen": r"(?<=\w) ?-- ?(?=\w)",
    "semicolon": r";",
    "parenthetical": r"\([^)\n]{3,}\)",
    "ellipsis": r"\u2026|\.\.\.",
    "connective_adverb": r"(?i)(?:^|(?<=[.!?]\s))(?:notably|moreover|furthermore|ultimately|in essence|that said|in fact|indeed)\b",
    "hedge": r"(?i)\b(?:might|may|could|perhaps|possibly|probably|generally|typically|often|usually)\b",
    "hashtag": r"(?<![\w#])#[A-Za-z][\w]+",
    "tilde_approx": r"(?<![\w~])~\s?\$?\d",
}


def context_for(prompt):
    text = _norm(prompt.get("text", ""))
    fr = prompt.get("format_request") or {}
    return {
        "prompt_lower": text.lower(),
        "prompt_words": set(w.lower() for w in _words(text)),
        "format": fr.get("type") if isinstance(fr, dict) else None,
    }


def contraction_rate(text):
    ws = _words(text)
    if not ws:
        return 0.0
    n = len(re.findall(r"(?i)\b\w+'(?:s|t|re|ve|ll|d|m)\b", _norm(text)))
    return 100.0 * n / len(ws)


def score(reply, prompt):
    """Score one reply. prompt: dict with text and optional format_request, listed_words."""
    t = reply or ""
    c = context_for(prompt)
    out = {"suite_version": SUITE_VERSION}
    total = 0
    by_section = {}
    for name, (section, fn) in TELLS.items():
        n = len(fn(t, c))
        out[f"tell_{name}"] = n
        total += n
        by_section[section] = by_section.get(section, 0) + n
    out["tells_total"] = total
    for s, n in by_section.items():
        out[f"section_{s}"] = n
    for name, pat in WATCH.items():
        out[f"watch_{name}"] = len(re.findall(pat, t))
    ws = _words(t)
    out["words"] = len(ws)
    sents = [s for s in re.split(r"(?<=[.!?])\s+|\n+", t) if len(_words(s)) >= 2]
    out["sentences"] = len(sents)
    out["mean_sentence_words"] = (sum(len(_words(s)) for s in sents) / len(sents)) if sents else 0.0
    out["contractions_per_100w"] = contraction_rate(t)
    out["bullet_lines"] = len(re.findall(r"(?m)^\s*[-*\u2022]\s+\S", t))
    out["numbered_lines"] = len(re.findall(r"(?m)^\s*\d+[.)]\s+\S", t))
    out["tells_per_100w"] = (100.0 * total / len(ws)) if ws else 0.0
    lw = [w.lower() for w in (prompt.get("listed_words") or [])]
    if lw:
        low = _norm(t).lower()
        out["user_words_reused"] = sum(1 for w in lw if re.search(rf"(?<![\w-]){re.escape(w)}(?![\w-])", low))
        out["user_words_listed"] = len(lw)
    return out


def matches(reply, prompt):
    """Return (tell, matched_text, start, end) for every scored match, for precision labeling."""
    t = reply or ""
    c = context_for(prompt)
    found = []
    for name, (section, fn) in TELLS.items():
        for m in fn(t, c):
            start, end = getattr(m, "pos", -1), getattr(m, "endpos", -1)
            found.append((name, t[start:end] if start >= 0 else str(m), start, end))
    return found


def format_compliance(reply, prompt):
    """Rough check that an explicitly requested format is present. None when no format was requested."""
    fr = prompt.get("format_request") or {}
    kind = fr.get("type") if isinstance(fr, dict) else None
    if not kind:
        return None
    t = reply or ""
    if kind == "table":
        return bool(re.search(r"(?m)^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$", t))
    if kind == "headers_bullets":
        heads = re.findall(r"(?m)^#{1,6}\s+\S|^\s*\*\*[^*\n]{2,80}\*\*:?\s*$", t)
        return len(heads) >= 1 and len(re.findall(r"(?m)^\s*[-*\u2022]\s+\S", t)) >= 2
    if kind == "numbered_steps":
        return len(re.findall(r"(?m)^\s*\d+[.)]\s+\S", t)) >= 3
    if kind == "outline":
        return len(re.findall(r"(?m)^#{1,6}\s+\S|^\s*\d+[.)]\s+\S|^\s*\*\*[^*\n]{2,80}\*\*:?\s*$|^\s*[IVX]+\.\s+\S", t)) >= 3
    if kind == "bold_terms":
        return len(re.findall(r"\*\*[^*\n]{1,80}\*\*", t)) >= 3
    if kind == "tldr":
        head = "\n".join(t.strip().splitlines()[:3])
        return bool(re.search(r"(?i)tl;?\s?dr", head))
    if kind == "checklist_emoji":
        return len(EMOJI.findall(t)) >= 3 or len(re.findall(r"(?m)^\s*(?:[-*]\s*)?\[[ xX]\]", t)) >= 3
    if kind == "n_options":
        want = fr.get("count") or 2
        labeled = len(re.findall(r"(?im)^[\s>#*_-]*(?:option|version|subject(?: line)?|variant|draft)\s*(?:\d+|[a-e]\b|one|two|three|four|five)", t))
        numbered = len(re.findall(r"(?m)^\s*\d+[.)]\s+\S", t))
        bullets = len(re.findall(r"(?m)^\s*[-*\u2022]\s+\S", t))
        return max(labeled, numbered, bullets) >= want
    return None
