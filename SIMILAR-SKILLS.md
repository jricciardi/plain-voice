# Similar skills

Plenty of other public skills target AI writing tells. A GitHub search on October 13, 2026 found nearly 300 skill files and about 240 repositories, many of them copies or ports of a few originals. For the 47 with the most stars or the most distinct approach, the main skill file and README were read and sorted by aim, size, when the skill runs and what evidence it publishes. AI agents did the first pass, and every claim below was checked against the project's own files.

Use whichever fits. No head-to-head test between plain-voice and any of these has been run, so this page compares aims and methods. It can't say which one works best.

## At a glance

plain-voice is in the first row for reference. The other rows are sorted by the testing they publish, then by size. Size is the main skill file in tokens (OpenAI's o200k tokenizer), and a plus sign means that file also points the agent to reference files or scripts. "No" in the testing columns means nothing was found in the skill file or README. Stars are for the whole hosting repository on October 13, 2026.

| Skill | Size | Aim | Tested its own output | Human judges | When it runs | Tells by model family | Stars |
|---|---:|---|---|---|---|---|---:|
| plain-voice | 1,321 | Fewer tells in everyday replies | Yes: 10 models, against no skill and a placebo | Yes: the author, 40 blind pairs | Every reply | Claude, GPT, Gemini, Grok | new |
| [theclaymethod/unslop] | 1,649+ | Fewer tells, or writing in your voice | Yes: a GPT judge; latest result was "no-ship" | No | On a draft | General list | 529 |
| [MohamedAbdallah-14/unslop] | 3,747 | Read as human, with an anti-detector mode | Yes: an LLM judge and a detector | No | Every reply | General list | 158 |
| [blader/humanizer] | 7,056 | Make AI text sound like a person wrote it | An outside study with model judges | No | On a draft | General list | 56,490 |
| [ilien-dev/quiron] | 7,235+ | Read as human, checked by measurement | Yes: Claude judges | No | Writing or rewriting | General, some Claude | 58 |
| [conorbronsdon/avoid-ai-writing] | 6,703+ | Find and fix tells, with a scoring engine | Only its scorer | No | On a draft | General list | 4,989 |
| [hardikpandya/stop-slop] | 615+ | Fewer tells | No | No | Drafting or editing | General list | 17,977 |
| [realrossmanngroup/no_ai_slop_writing_rules] | 1,318+ | Fewer tells | No | No | Before writing prose | General list | 699 |
| [Avinashricky211/writ] | 1,331 | Fewer tells | No | No | Silent final pass | General list | 28 |
| [pstack's unslop][pstack unslop] | 1,400 | Fewer tells | No | No | Only when called by name | General list | 1,742 |
| [jalaalrd/anti-ai-slop-writing] | 1,666+ | Avoid detectable AI patterns | No | No | Every writing task | General list | 532 |
| [Nanako0129/sepia] | 3,197+ | Fewer tells in fiction and professional prose | No | No | On request | Claude, GPT, Gemini, DeepSeek, Kimi | 3,151 |
| [ama-zingco/anti-ai-writing-skill] | 3,428 | Fewer tells in copy | No; built on two studies | No | While writing copy | Claude, GPT, Gemini, Grok | 35 |

## How plain-voice compares

### Aim

plain-voice is meant to make an assistant's replies less tiring to read. It isn't meant to pass AI writing off as a person's, and the README asks people not to use it that way.

The most-starred skill, blader/humanizer, "makes AI-written text sound like a person wrote it, without changing what it says," and its README adds that getting past AI detectors is not a goal. A few others do aim at detectors. [drpedapati/sciclaw]'s humanizer lists "bypass AI detection" among its triggers and labels each rewrite with a detection risk. jalaalrd's skill "avoids detectable AI writing patterns." [numen-tech/slopornot] pairs a humanizer with an on-device AI detector. [lynote-ai/humanize-text], the open version of a paid service, keeps an older pipeline that passes text through Japanese and Finnish translations, and its README reports the paid version's "detector-bypass rate." MohamedAbdallah-14/unslop has an anti-detector mode, but its README reports that surface rewriting moved a detector's score by 0.0 to 0.2 percentage points.

Projects that checked found that surface fixes don't hide AI writing from readers either. quiron had four Claude Opus judges estimate how likely each post was to be AI-written, and all 12 posts rewritten with the skill were judged AI, at an average of 82%. Adding the writer's own notes ("what happened, names, links, opinions") helped more, though across three rounds 18 of 32 of those posts were still judged AI. [asavvin-pixel/unslop]'s launch post, written with the skill, was "identified as AI within the hour" on r/ClaudeAI.

### Size and cost

plain-voice is one file of 1,321 tokens with no reference files, scripts or extra model calls. Because it's always on, every conversation loads it, so it was kept small. [COST.md](COST.md) has what that costs.

The biggest are five to seven times its size: blader/humanizer is 7,056 tokens, avoid-ai-writing is 6,703 plus a scoring engine, quiron is 7,235 plus measurement scripts, and [Aboudjem/humanizer-skill] is 9,377. [epoko77-ai/im-not-ai] sends harder Korean texts through three or more model calls. Most of these are passes you call on a draft, where size matters less. Some are smaller than plain-voice: stop-slop's main file is 615 tokens and [glaforge/deslopify]'s is 243, and both can load longer reference files. Among skills used while writing, plain-voice is about the size of realrossmanngroup's rules (1,318) and writ (1,331), and smaller than MohamedAbdallah-14/unslop (3,747) and [FeedHive/ai-slop-detector]'s list of 120 patterns (5,678).

### When it runs

plain-voice applies to every everyday reply as it's written. Most others are passes over finished text: blader/humanizer, avoid-ai-writing and theclaymethod/unslop take a draft and return a rewrite or an audit. pstack's unslop can only run when called by name. [michaelshimeles/skills] copied that skill and removed the setting, so the agent can apply it to anything written for a person, chat replies included. [jssblck's stop-slop] takes the opposite position to plain-voice: it covers docs, commit messages and PR text, and says to "skip ordinary chat replies." MohamedAbdallah-14/unslop ("ACTIVE EVERY RESPONSE") and jalaalrd's skill are meant to apply all the time, like plain-voice, and writ runs as a silent final pass on longer prose.

### Which models

plain-voice names tells from Claude, GPT, Gemini and Grok, found by sampling 13 models side by side (see [How the list was built](README.md#how-the-list-was-built)). Most other skills use one general list, often drawn from Wikipedia's Signs of AI writing guide. Two cover several families by name. ama-zingco/anti-ai-writing-skill names all four and notes where they differ, based on two published studies; by 2026, for example, ChatGPT used fewer em dashes than human writers and only Claude still used more. sepia loads separate tables for Claude, GPT, Gemini, DeepSeek and Kimi when it knows which model wrote the text. [makoMakoGo/fish-claude] targets one model, GPT-5.4.

### Voice and structure

plain-voice doesn't imitate anyone's voice, and its description says to use a voice-matching skill instead when one is installed. It also leaves the structure and order of ideas alone.

Several skills take on one or the other. [jzOcb/writing-style-skill] learns rules from the differences between the AI's draft and your edited version. theclaymethod/unslop builds a profile of your voice and then writes in it. Aboudjem/humanizer-skill rewrites into one of five voice profiles. realrossmanngroup pairs its rules with a profile of Louis Rossmann's voice built from 513,683 words of his writing. Any of these could run alongside plain-voice. On structure, sepia repairs the "narrative architecture" of fiction, [NulightJens/humanizer-stack] adds a structural pass after the word-level one, and [mizchi's natural-writing-en] asks one question of every sentence: does it update the situation or the document?

### Evidence

plain-voice was tested before release on 10 models from 5 families, against no skill and against a placebo, with the hypotheses written down first and the failures published ([eval/RESULTS.md](eval/RESULTS.md)). It's also the only skill in the table whose test included a human rater. Its author rated 40 pairs of replies blind, and when both picked a side, the model judges agreed with him 92% of the time on which reply sounded more like stock AI. That's a single rater who also wrote the skill, a limit the README's [Limitations](README.md#limitations-and-opportunities) section covers.

Most of the skills reviewed publish no test of their own output. Of those that do, theclaymethod/unslop runs a benchmark with separate scoreboards, scored by a GPT judge, and published its latest result as a "no-ship." MohamedAbdallah-14/unslop reports that a blind LLM judge preferred its rewrite in 21 of 21 runs, along with the detector result above. blader/humanizer's README cites an outside study in which judges, all language models from one family, preferred its rewrite 16 times out of 16. [MrGeDiao/shuorenhua] keeps a 123-case benchmark and reports how often it changed text that was already fine. im-not-ai fixed false positives that an outside review found, then measured again on 532 human-written texts. mizchi's natural-writing-en measured four widely cited tells and says not to build on them.

theclaymethod/unslop is the only other one found that tests against something like a placebo: the same model given neutral editing instructions. In plain-voice's test, a one-line placebo cut counted tells by a third on its own, so a test against no skill alone would have overstated the effect.

### License

Most are MIT. quiron and [alexgreensh/attention-span] use AGPL-3.0. GitHub detects no license for 10 of them, including realrossmanngroup's rules, jalaalrd's skill and theclaymethod/unslop; without one, reuse needs the author's permission. plain-voice is MIT with one exception: no AI training.

## Other approaches

For other languages there's [op7418/Humanizer-zh] (Chinese, a port of blader/humanizer), MrGeDiao/shuorenhua (Chinese and English), im-not-ai (Korean) and [iKora128/stop-ai-slop-jp] (Japanese, a port of stop-slop). plain-voice was only tested in English.

For particular kinds of writing, [AIScientists-Dev/academic-humanizer] handles papers and NSF and NIH proposals, [sergebulaev/linkedin-skills] has a LinkedIn humanizer, sepia covers fiction, and [ninehills's deslop-en] has separate guidance for blogs, science writing, release notes and social posts.

Some tools work outside the prompt. [eric-tramel/slop-guard] is a rule-based linter that scores text from 0 to 100 without calling a model, and it also runs as an MCP server. [DanRWilloughby/snifftest] checks drafts against your own house rules and sends text to a model only with consent. [sam-paech/antislop-sampler] blocks listed phrases during generation on locally run models, and was published at ICLR 2026. [mshumer/unslop] samples a model many times in a domain you name, then writes a new skill against the defaults it repeats.

alexgreensh/attention-span takes a different route to shorter replies. Its output styles make Claude Code answer first, in a form that's easy to scan, and on 12 coding tasks they cut output by about 43% with the same test pass rate.

## Finding and judging others

These commands find most of them:

```sh
gh skill search humanizer --limit 100
gh skill search slop --limit 100
gh skill search "ai writing" --limit 100
gh search repos "ai slop" --sort stars --limit 50
```

Many results are copies, and READMEs usually say so with "ported from," "vendored" or "based on." Star counts cover the whole repository, which may hold dozens of unrelated skills. [coreyhaines31/marketingskills], for example, has 54,523 stars and one copywriting skill with an AI-tells checklist.

Questions that separate them:

- What is it for: fewer tells for the reader's sake, passing as human, getting past detectors, matching a voice, or one kind of writing?
- When does it run: on every reply, or on a draft when asked?
- How much does it load? A skill that's always on is read in every conversation, so count its main file, reference files, scripts and extra model calls.
- Whose tells does it cover? Lists built from older ChatGPT output can miss newer models and other families.
- Was it tested against no skill and a placebo, on more than one model, with failures reported?
- Does it overcorrect? Quotas and forced variety make a new pattern. As sepia puts it, "Inverting every AI tell creates a new fingerprint."
- What does the license allow?

[blader/humanizer]: https://github.com/blader/humanizer
[hardikpandya/stop-slop]: https://github.com/hardikpandya/stop-slop
[conorbronsdon/avoid-ai-writing]: https://github.com/conorbronsdon/avoid-ai-writing
[Nanako0129/sepia]: https://github.com/Nanako0129/sepia
[pstack unslop]: https://github.com/backnotprop/pstack/tree/main/skills/unslop
[realrossmanngroup/no_ai_slop_writing_rules]: https://github.com/realrossmanngroup/no_ai_slop_writing_rules
[jalaalrd/anti-ai-slop-writing]: https://github.com/jalaalrd/anti-ai-slop-writing
[theclaymethod/unslop]: https://github.com/theclaymethod/unslop
[MohamedAbdallah-14/unslop]: https://github.com/MohamedAbdallah-14/unslop
[ilien-dev/quiron]: https://github.com/ilien-dev/quiron
[ama-zingco/anti-ai-writing-skill]: https://github.com/ama-zingco/anti-ai-writing-skill
[Avinashricky211/writ]: https://github.com/Avinashricky211/writ
[drpedapati/sciclaw]: https://github.com/drpedapati/sciclaw/tree/main/skills/humanize-text
[numen-tech/slopornot]: https://github.com/numen-tech/slopornot
[lynote-ai/humanize-text]: https://github.com/lynote-ai/humanize-text
[asavvin-pixel/unslop]: https://github.com/asavvin-pixel/unslop
[Aboudjem/humanizer-skill]: https://github.com/Aboudjem/humanizer-skill
[epoko77-ai/im-not-ai]: https://github.com/epoko77-ai/im-not-ai
[glaforge/deslopify]: https://github.com/glaforge/deslopify
[FeedHive/ai-slop-detector]: https://github.com/FeedHive/ai-slop-detector
[michaelshimeles/skills]: https://github.com/michaelshimeles/skills/tree/main/unslop
[jssblck's stop-slop]: https://github.com/aiskillstore/marketplace/tree/main/skills/jssblck/stop-slop
[makoMakoGo/fish-claude]: https://github.com/makoMakoGo/fish-claude/tree/main/skills/gpt-isms-stamp-out
[jzOcb/writing-style-skill]: https://github.com/jzOcb/writing-style-skill
[NulightJens/humanizer-stack]: https://github.com/NulightJens/humanizer-stack
[mizchi's natural-writing-en]: https://github.com/mizchi/skills/tree/main/natural-writing-en
[MrGeDiao/shuorenhua]: https://github.com/MrGeDiao/shuorenhua
[op7418/Humanizer-zh]: https://github.com/op7418/Humanizer-zh
[iKora128/stop-ai-slop-jp]: https://github.com/iKora128/stop-ai-slop-jp
[AIScientists-Dev/academic-humanizer]: https://github.com/AIScientists-Dev/academic-humanizer
[sergebulaev/linkedin-skills]: https://github.com/sergebulaev/linkedin-skills/tree/main/skills/linkedin-humanizer
[ninehills's deslop-en]: https://github.com/ninehills/skills/tree/main/deslop-en
[eric-tramel/slop-guard]: https://github.com/eric-tramel/slop-guard
[DanRWilloughby/snifftest]: https://github.com/DanRWilloughby/snifftest
[sam-paech/antislop-sampler]: https://github.com/sam-paech/antislop-sampler
[mshumer/unslop]: https://github.com/mshumer/unslop
[alexgreensh/attention-span]: https://github.com/alexgreensh/attention-span
[coreyhaines31/marketingskills]: https://github.com/coreyhaines31/marketingskills/tree/main/skills/copywriting
