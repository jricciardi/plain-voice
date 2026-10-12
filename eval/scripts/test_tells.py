import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import tells  # noqa: E402

P = {"text": "Can you help me with my plan?"}


def s(reply, prompt=P):
    return tells.score(reply, prompt)


def test_em_dash_and_shorthand():
    r = s("It works \u2014 mostly. Costs ~20% more, tight/stressful, and IC \u2192 EM. Use and/or.")
    assert r["tell_em_dash"] == 1
    assert r["tell_shorthand"] == 2  # tight/stressful and the arrow (and/or allowed; ~ is watch-only)
    assert r["watch_tilde_approx"] == 1


def test_openers_and_closers():
    r = s("Great question! Here's how I'd think about it.\n\nDo the thing.\n\nIf you want, I can draft it. Hope this helps!")
    assert r["tell_praise_opener"] == 1
    assert r["tell_stock_opener"] == 1
    assert r["tell_signpost"] == 1
    assert r["tell_offer_closer"] == 1
    assert r["tell_hope_closer"] == 1


def test_offer_only_counts_in_tail():
    body = "If you want speed, pick Postgres. " + ("Filler sentence here. " * 40)
    assert s(body)["tell_offer_closer"] == 0


def test_contrast_variants():
    for txt in [
        "It's not a tooling problem, it's a habit problem.",
        "This isn't about speed. It's about trust.",
        "The job is less about answers and more about questions.",
        "Ship a calculated risk, not a leap.",
        "Not because they're lazy, but because nobody owns it.",
        "It's not just fast, it's cheap.",
    ]:
        assert s(txt)["tell_contrast_formula"] >= 1, txt
    assert s("It is not raining today.")["tell_contrast_formula"] == 0


def test_slogans():
    assert s("Clarity beats heroics.")["tell_slogan"] == 1
    assert s("- Clarity over cleverness.\n- Ship it.")["tell_slogan"] == 1
    assert s("He jumped over the fence.")["tell_slogan"] == 0


def test_user_words_are_fine():
    p = {"text": "What's a good north star metric for a newsletter?", "listed_words": ["north star"]}
    r = s("A good north star is weekly engaged readers.", p)
    assert r["tell_listed_vocab"] == 0
    assert r["user_words_reused"] == 1
    assert s("Your north star is retention.")["tell_listed_vocab"] == 1


def test_scare_quotes_skip_user_phrases():
    p = {"text": "They offered me a bigger role at a startup."}
    assert s('Ask what "bigger role" means in practice.', p)["tell_scare_quotes"] == 0
    assert s('Leaving a "safe" job is a gamble.', p)["tell_scare_quotes"] == 1


def test_requested_formats_not_counted():
    reply = "## Options\n\n| Bank | APY |\n|---|---|\n| A | 4% |\n\n**Pick A.**"
    plain = s(reply)
    assert plain["tell_md_header"] == 1 and plain["tell_table"] == 1
    asked_table = s(reply, {"text": "put it in a table", "format_request": {"type": "table"}})
    assert asked_table["tell_table"] == 0 and asked_table["tell_md_header"] == 1
    asked_heads = s(reply, {"text": "use headers", "format_request": {"type": "headers_bullets"}})
    assert asked_heads["tell_md_header"] == 0


def test_bold_kinds_do_not_double_count():
    reply = "**Why it works**\n\n- **Speed:** fast\n- **Cost:** low\n\nThis is **really** cheap."
    r = s(reply)
    assert r["tell_bold_header_line"] == 1
    assert r["tell_bold_label"] == 2
    assert r["tell_bold_inline"] == 1


def test_option_menu_and_emoji():
    r = s("Option 1: formal\n\nOption 2: casual \u2705")
    assert r["tell_option_menu"] == 2 and r["tell_emoji"] == 1
    r2 = s("Option 1: formal\n\nOption 2: casual", {"text": "give me two versions", "format_request": {"type": "n_options", "count": 2}})
    assert r2["tell_option_menu"] == 0


def test_table_cells_are_not_prose():
    reply = "| Option | Cost |\n|---|---|\n| **Cabin** | ~$900 \u2014 cheap/easy |\n\nPick the **cabin** \u2014 it's 20 \u2192 22 min closer."
    r = s(reply, {"text": "put it in a table", "format_request": {"type": "table"}})
    assert r["tell_bold_inline"] == 1 and r["tell_em_dash"] == 1 and r["tell_shorthand"] == 1 and r["tell_table"] == 0


def test_takeaway_label():
    assert s("**Takeaway:** the demo moves.")["tell_answer_label"] == 1


def test_metrics():
    r = s("I'd go with it. It's fine; don't worry.")
    assert r["words"] == 8 and r["contractions_per_100w"] > 30 and r["watch_semicolon"] == 1


def test_format_compliance():
    t = "| a | b |\n|---|---|\n| 1 | 2 |"
    assert tells.format_compliance(t, {"format_request": {"type": "table"}}) is True
    assert tells.format_compliance("no table", {"format_request": {"type": "table"}}) is False
    assert tells.format_compliance("x", {}) is None
    three = "1. one\n2. two\n3. three"
    assert tells.format_compliance(three, {"format_request": {"type": "n_options", "count": 3}}) is True


def test_matches_have_positions():
    found = tells.matches("Great question \u2014 truly.", P)
    names = [f[0] for f in found]
    assert "em_dash" in names and "filler_adverb" in names and "praise_opener" in names
    assert all(f[2] >= 0 for f in found)


if __name__ == "__main__":
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("pass", name)
            except AssertionError as e:
                fails += 1
                print("FAIL", name, e)
    sys.exit(1 if fails else 0)
