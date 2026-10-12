# Tuning log: v1 to v2

Tuning used the dev set and test-1 (already scored once for v1). Test-2 stays sealed until the final v2 is scored once.

## What test-1 showed about v1

- Tells dropped about 90% against no skill and about 84% against the placebo, and the drop holds with noisy patterns removed. MAI improved least.
- Judges found v1 replies less like stock AI in 93% of pairs against no skill, but preferred them in only 49%.
- Judges preferred v1 on writing tasks (genre traps 61%, status updates 59%, emails 57%) and the no-skill reply on structured ones (summaries 30%, explicit format requests 41%, how-tos 42%). Their reasons: the no-skill reply was more complete, or easier to scan for owners, steps and action items.
- v1 missed slightly more required facts than no skill (10.1% vs 8.3%) and invented fewer details.
- v1 reused listed words the user had written less often (17% vs 39%), mostly on a prompt about "the landscape" and what to "leverage".

## Candidate edits and what happened

| Edit | Aimed at | Result | Kept |
|---|---|---|---|
| "Lists only when the content is a list, and then use one: steps, options, action items, dates." | Structured content losing on completeness and scannability | More bullets in dev summaries and how-tos; small gain against no skill on summaries (30% to 37%) | Yes |
| "...but never a fact, name, date or step the user gave or asked for." | Missing facts | Missing facts on matched test-1 prompts fell from 12.4% (v1) to 9.1%, below no skill (10.3%) | Yes |
| "...phrased as a plain sentence, not an offer." | Offer closers | Explicit offers were already rare (1% of v1 replies); no measurable change | No |
| "When it's the right word, use it; don't swap in a synonym to dodge the list." | User's own words avoided | No change (20% vs 23% for v1, 37% for no skill) | No |

Judges rated the four-edit candidate even with v1 (50% on targeted test-1 prompts, 47% on dev), so v2 aims at fidelity and structure rather than a broad preference gain.

## What the human review added

- Stock-AI judgments: the rater found the v1 reply less like stock AI in 12 of 13 decisive pairs against no skill, and the judges agreed with the rater on 92% of decisive calls. That makes the judges a reasonable stand-in for this question in round 2.
- Preference: no difference (12 skill, 11 other, 17 ties across 40 pairs), and the rater matched his own preference on only 2 of 4 repeated pairs. The judges agreed with the rater's preference on 53% of decisive calls. Preference isn't measured reliably here by the rater or the judges.
- Phrase checks: the rater confirmed the wording tells he was shown (contrast slogans, filler adverbs, listed words, signposts, option menus) and was unsure or said no on formatting ones, including three bolded items in lists.

## Final v2

v1 plus the list edit and the fidelity edit. The bold-label rule stays as written: three phrase checks from a fatigued session weren't enough to override the author's rule, given that the judges treat bold as chatbot style.

## Outcome

v2 didn't ship. On sealed test-2 it failed the tells bar for MAI (as v1 also did on those prompts) and missed more required facts than v1, mostly on one advice prompt. It matched v1 on everything else. v1 stays, unchanged. See [RESULTS.md](RESULTS.md).
