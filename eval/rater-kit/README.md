# Rater kit

Tools for round 3, which asks people instead of models whether the skill makes everyday AI replies less tiring to read. Raters are friends and coworkers of the skill's author, working in short sessions on a laptop or phone.

- `app.html` is the reading test. The kit builder fills it with one rater's replies and writes it out as a single file that works offline.
- `intake.html` is a form for sending in 5 to 10 real prompts.
- `../scripts/build_rater_kits.py` builds the kits and an answer key.
- `../scripts/analyze_ratings.py` turns returned results into a report.

## A session

Each session has two batches of four replies from one model: one batch written without the skill and one written with it. The rater isn't told which is which. For each reply, the rater taps any sentence that bugs them, rates how tiring it was to read from 1 to 5, and says whether it would do the job (yes, mostly or no). After each batch they rate how worn out it left them, and at the end they pick the batch they'd rather keep getting, with "both fine" and "both bad" as separate choices. A session takes about 10 minutes, and a kit has four.

Raters work in pairs. Both people in a pair get the same prompts in the same positions with the conditions swapped, so every prompt is read both ways, and the order of conditions alternates between sessions. Put the skill's author last in the list of raters, so everyone else forms complete pairs and the analysis can leave the author out cleanly.

The shared set uses public replies from the stress test (test-1 and test-2, repeat 1) by Claude Opus 5.5, GPT-6.1 Sol, Gemini 3.8 Flash, Grok 4.7 and MAI-Code-1.1-Flash. Prompts are under 120 words and replies under 400. It leaves out the two prompts the round 1 rater found stilted (wc-03 and wc-28) and any reply where the test agent leaked its own lines. Because the replies are public, a rater could look one up in this repo and see which condition wrote it, so the rater message doesn't point to the repo.

## Build kits

From the `eval` folder:

```sh
python scripts/build_rater_kits.py --out rater-kit/out --blank-names \
  --raters "Rater 1,Rater 2,Rater 3,Rater 4,Rater 5,Rater 6,Jay"
```

This writes one HTML file per rater and `key.json`. The key says which batch is which, so it never goes to raters. `rater-kit/out` is ignored by git. With `--blank-names`, each rater types their own name; reports use the labels from `--raters`.

## Send kits

On a laptop, the HTML file opens in any browser and needs no internet. Phones don't run scripts in attached HTML files, so phone users need a link to the file on a website instead; any static host works, such as GitHub Pages. Progress saves in the browser, so a rater can stop and pick up later.

At the end of each session the app shows the results as a block of text to copy into a message, or a file to download. Each export includes everything so far, and the analysis keeps the latest one per kit.

## Analyze

```sh
python scripts/analyze_ratings.py --key rater-kit/out/key.json path/to/results/
```

The report covers how tiring each reply was, whether it did the job, the same prompt read both ways, how worn out each batch left people, which batch they'd keep, and results by model family and by rater. It also shows how often readers flagged sentences containing each tell the skill lists, and the flagged sentences that contain none, which are candidates for new entries. A second report leaves out the skill's author (`--author`, default Jay).

## Real prompts

`intake.html` collects prompts with an "OK to publish" box for each one, unticked by default. Prompts without that box ticked, and any replies generated from them, stay out of this repo; keep them in a folder outside it, and publish only totals. Add `?to=Name` to the form's link to change who it tells people to send their prompts to.
