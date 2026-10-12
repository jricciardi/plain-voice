# plain-voice

An agent skill that keeps an AI assistant's everyday replies from reading like stock AI. It covers the house-style tells of Claude, GPT, Gemini and Grok: em dashes, "It's not X, it's Y," "Great question," "Here is why:" lead-ins, bolded slogans in bullet lists, "If you want, I can…" closers, and the rest.

It's meant for routine replies and working docs. It doesn't imitate your voice, so pair it with a voice-matching skill for anything that should sound like you.

## Install

With the GitHub CLI, which asks which agent to install it for:

```sh
gh skill install jricciardi/plain-voice plain-voice --scope user
```

Or copy the `plain-voice` folder into your agent's personal skills folder:

- Claude Code: `~/.claude/skills/`
- GitHub Copilot CLI: `~/.copilot/skills/`
- Other agents that support [Agent Skills](https://agentskills.io): see their docs for the skills folder.

The skill applies to routine replies on its own. In Claude Code you can also call it with `/plain-voice`.

## How the list was built

The first version came from watching Claude's habits. Extending it to other model families drew on two kinds of evidence: published research, and a side-by-side test of 13 models.

### Published research

The research pass covered Wikipedia's [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) guide, corpus studies of words that AI overuses, xAI's published Grok system prompts, and detector write-ups that name model-specific patterns. Everything used is listed under [Sources](#sources).

### Side-by-side test

Thirteen models answered the same eight prompts: six from OpenAI (GPT-5 mini, GPT-5.3-Codex, GPT-5.5, GPT-5.6 Sol, GPT-6 Luna and GPT-6.1 Sol), two from Google (Gemini 3.7 Flash and 3.8 Flash), three from xAI (Grok 4.5, 4.6 and 4.7), Microsoft's MAI-Code-1.1-Flash, and Anthropic's Claude Sonnet 5.5 as a baseline. That came to 104 replies and about 16,500 words, collected in October 2026.

The prompts cover the kinds of writing where tells tend to cluster: an explainer, personal advice, a team email, a LinkedIn post, feedback on someone's draft, a technical recommendation, a status update built from rough notes, and a short travel description.

Every model ran in the same agent harness (GitHub Copilot) with identical instructions: reply the way it would in an ordinary chat app, at its natural length and formatting, with no web access. The instructions didn't mention writing style or say what the replies were for, so the models had no reason to adjust. Each prompt got one reply per model.

<details>
<summary>Exact instructions and prompts</summary>

Instructions given to every model:

> For each message, write the reply you would send if a user sent you that message in an ordinary chat app: your natural length, formatting, tone, opening and closing. Write it as you normally would; don't adapt it for this task.

Prompts:

1. Why do planes leave white trails in the sky, and why do some disappear right away while others stick around for ages?
2. I've been at my job for 3 years. I'm good at it but bored. A startup offered me a bigger role with 20% less salary plus equity. I'm 34 and have a mortgage. What would you do?
3. Write a short email to my team: our weekly sync is moving from Monday 10am to Thursday 2pm starting next week, and the first Thursday session will run long because we'll use it for Q3 planning.
4. Write a LinkedIn post about what I learned in my first year as an engineering manager.
5. Can you give me feedback on the opening of my blog post? "Every team says they value documentation. Few actually write it. In this post I want to talk about why, and what we did about it on my team."
6. We're a 5-person startup building a B2B SaaS app. Monolith or microservices?
7. Turn my notes into a quick status update for my manager: migration 70% done, blocked on vendor API rate limits, asked vendor for an increase, eta friday. new hire starts monday. dashboard v2 shipped tuesday, 3 bugs reported, 2 fixed.
8. Write about 150 words describing Astoria, Oregon for a travel blog.

</details>

Scoring had two passes. A script counted 16 kinds of tells with pattern matching (em dashes, headers, bold text, contrast constructions such as "It's not X, it's Y", answer labels, offer closers, a candidate word list and others). It also pulled out every opener and closer and ranked the phrases each family used far more often than the rest. Then every reply was read in full to catch what pattern matching misses, such as reframing the user's question or "Come for X, stay for Y" taglines.

A pattern made the list if published research documents it or if it appeared in replies from at least two model families. One-model quirks were left out, such as GPT-5 mini signing off chat replies with "Cheers".

Most tells showed up across several families, so the skill keeps one list instead of a section per model. A few lean toward one family:

- GPT reframes the question ("I'd treat this as a risk decision"), labels answers ("Short answer:"), and writes in slash and arrow shorthand.
- Gemini puts headers on short answers, leads lists with "Here is why:", and offers "Option 1, 2, 3" when you asked for one draft.
- Grok uses em dashes, quips and scare quotes, and staccato slogans ("Default to the monolith. Earn the split.").
- Claude has its own vocabulary: load-bearing, quietly, the shape of, lean into.

### Validation

Five of the models then answered the same prompts with a draft of the skill applied: GPT-6.1 Sol (the newest GPT), GPT-5 mini (the heaviest em dash user), Gemini 3.8 Flash, Grok 4.5 and MAI-Code-1.1-Flash. Counted tells fell from 277 to 16, and replies got 42% shorter on average (166 words down to 97).

<details>
<summary>Counts by tell, five models, 40 replies each way</summary>

| Tell | Without skill | With skill |
| --- | ---: | ---: |
| Em dashes | 55 | 5 |
| Markdown headers | 12 | 0 |
| Bold spans | 88 | 0 |
| Bold lines used as headers | 17 | 0 |
| Answer labels ("Short answer:") | 4 | 0 |
| Reframing the question | 1 | 0 |
| Signposts ("Here's how/why") | 14 | 0 |
| Praise openers | 2 | 0 |
| Contrast formula | 15 | 3 |
| "X beats Y" slogans | 2 | 0 |
| Offer closers | 7 | 0 |
| Scare quotes | 6 | 1 |
| Slash and arrow shorthand | 15 | 0 |
| Option menus | 2 | 0 |
| Filler and sincerity adverbs | 25 | 3 |
| Listed vocabulary | 12 | 4 |
| Total | 277 | 16 |

</details>

Every email and status update kept all the facts from its prompt. Four of the five models added promises the user never made (for example, "I'll send the agenda before the meeting"), and two dropped contractions and read stiffly. Those findings led to a last round of additions: contractions, padding in drafts, "real" as an intensifier, and a few more words. Those additions haven't been retested yet.

GPT-6.1 Sol, Gemini and Grok followed the skill closely. GPT-5 mini kept five em dashes, and MAI kept some "It's not X, it's Y" lines.

### Limits

- One reply per prompt per model. Eight replies per model make for noisy rates, and there are no confidence intervals.
- The same eight prompts were used to find tells and to check the skill, so the drop from 277 to 16 probably overstates how well it generalizes.
- The models ran in an agent harness, not their own chat apps. The harness holds back some chat-app habits such as emoji, so the entries for those rest on the published research.
- The counters look for the listed patterns. Fewer counted tells shows the models complied; it doesn't show that readers prefer the result. Pattern matching also misses paraphrases and sometimes counts the user's own words quoted back.
- The reading and pattern-finding were done with an AI model (Claude Opus 5.5). No human raters have checked the results yet.
- Model versions are as of October 2026, and house styles shift with each release.

## Sources

- [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
- Kobak et al., [Delving into LLM-assisted writing in biomedical publications through excess vocabulary](https://arxiv.org/abs/2406.07016)
- Juzek and Ward, [Why does ChatGPT "delve" so much?](https://arxiv.org/abs/2412.11385)
- Sun et al., [Idiosyncrasies in large language models](https://arxiv.org/abs/2502.12150)
- [xAI's published Grok system prompts](https://github.com/xai-org/grok-prompts)
- GPTZero, [10 AI patterns](https://gptzero.me/news/ai-patterns/)
- Sean Goedecke, [The OpenAI house style is exhausting](https://www.seangoedecke.com/chatgpt-house-style/)
- [EQ-Bench creative writing leaderboard](https://eqbench.com/creative_writing.html), which tracks a slop score per model

## Contributing

Spotted a tell that isn't listed? Open an issue with an example and the model that wrote it. Samples from chat apps, rather than agent tools, are especially useful.

## License

The license follows MIT terms with one exception: no AI training. You can use, copy, modify and share the skill, and load it into any AI agent or system prompt. You can't use it to train, fine-tune or distill a model, or include it in a training dataset. It also reserves text-and-data-mining rights under EU law.

Because of that exception, the skill is source-available rather than open source as the Open Source Initiative defines it. The full terms are in [LICENSE](LICENSE), and a copy ships inside the skill folder so it travels with every install.
