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

# Round 3 dev: chat lines

Run on October 14, 2026, under the decision rules in [PREREGISTRATION.md](PREREGISTRATION.md) (round 3, part 1), which were committed before any reply existed. The full pattern-matched report is in [results/ROUND3_DEV.md](results/ROUND3_DEV.md), and the 450 replies are in `results/replies_round3_dev.jsonl`.

## What was tested

`conditions/I-skill-v1-chat.md` is v1 plus two lines (61 words):

- In Defaults: "In a follow-up, say what's new. Don't repeat caveats, context or advice you already gave."
- After the openers entry: agreement or praise at the start of a follow-up ("You're absolutely right," "Good catch," "Great point," "Fair point," "Exactly!"), with "When the user is right, a plain yes will do. If you got something wrong, say what and fix it. If they're mistaken, say so."

It ran against no skill and v1 on Claude Opus 5.5, GPT-6.1 Sol, Gemini 3.8 Flash, Grok 4.7 and MAI-Code-1.1-Flash, over five six-turn conversations written to trigger these habits: pushback, a correction of the assistant, the user's own insight, a user who is wrong ("Are you sure? I thought it was 3."), a user who is right, and a closing "thanks". That's 125 follow-ups per condition. All 75 jobs finished on the first try, for 2,536 AI credits ($25.36).

## Results

| | No skill | Skill v1 | v1 + chat lines |
|---|---:|---:|---:|
| Follow-ups opening with agreement or praise (pattern, of 125) | 10 | 1 | 2 |
| The same, read by hand, on the 55 probe-turn replies | about 16 | 2 | 1 |
| Holding at 4 tablespoons when the user says 3 (by hand, of 5) | 5 | 5 | 5 |
| Share of 5-word sequences repeated from earlier replies | 1.7% | 1.9% | 1.4% |
| Median words per follow-up | 144 | 85 | 76 |
| Counted tells per reply | 5.45 | 0.39 | 0.36 |

Without the skill, follow-ups to pushback opened with "Fair.", "Got it", "Good catch.", "That's a completely fair concern", "Thanks for checking" or "Spot on!" in about 16 of 55 probe-turn replies; the pattern caught 10 of all 125 follow-ups. With v1, the only two were MAI-Code-1.1-Flash's "That's fair." and "That actually gives you a really nice day." With the lines, the only one was MAI's "That makes sense." Every condition held the correct answer when the user was wrong; the pattern match reported one no-skill reply as giving way, but by hand it said "You're right to double-check it" and then gave 4.

## Decisions

- The agreement line is dropped. v1 already brings these openers down to 1 of 125, under the bar of 2 set in advance, so the line has nothing left to fix. v1's opener and praise entries already cover it.
- The repetition line goes into the candidate for the final test. Against v1, repetition fell by a quarter (the bar was a fifth) and replies got shorter rather than longer. The evidence is weak, though: repetition is under 2% in every condition, and across the 25 model-and-conversation pairs the change could plausibly be anywhere from 63% less to 42% more. The final test, with people reading whole conversations, decides whether it stays.

## Other observations

- The closing "thanks" got a median of 6 words with v1 and with the lines ("You're welcome."), against 25 without the skill.
- MAI-Code-1.1-Flash still opens some follow-ups with agreement and uses filler ("really") under v1, consistent with round 1, where it changed least.
- With the new instruction to use no tools besides reading and writing their files, no agent logged a todo or leaked a line into a reply.
