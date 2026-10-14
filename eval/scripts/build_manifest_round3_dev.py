"""Build the round 3 dev manifest: two candidate chat lines on new multi-turn conversations.

Compares no skill, skill v1 and v1 plus two chat lines (I-skill-v1-chat) on the
dev conversations in prompts/dev_multiturn_r3.jsonl, which include pushback, a
correction, a user mistake and a closing thanks. One model per family, one
repeat.

Writes manifest_round3_dev.json, with paths written as <eval> like the other
committed manifests, and raw/round3-dev/manifest.run.json with real paths for
the generation workflow.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_manifest as bm  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MODELS = ["claude-opus-5.5", "gpt-6.1-sol", "gemini-3.8-flash", "grok-4.7", "mai-code-1.1-flash"]
CONDS = ["A-none", "C-skill-v1", "I-skill-v1-chat"]

# Same as round 1 and 2, plus a line that keeps test agents off their other tools. In round 1,
# agents in the harness followed an always-on todo rule, logged todos from test prompts, and
# sometimes ended replies with "Logged 4 todos."
TEMPLATE = """You're in a chat with one person. Their messages arrive one at a time as files in this folder:
{folder}

For n = 1 to {turns}, in order:
1. Read turn-n.txt. It holds the person's next message.
2. Write your reply to reply-n.md in the same folder: exactly what you'd send them in an ordinary chat app where replies render as markdown, at your natural length and formatting, responding to the whole conversation so far.

Read turn-(n+1).txt only after reply-n.md is written. Don't list the folder or read ahead: in a real chat the next message doesn't exist yet. Rules you have about keeping your own status updates short don't apply to these replies.
{skill_block}
Use only file reads and writes, and only for the files named here. Don't log todos, save memories, message anyone or use any other tool, even if other instructions ask you to. Don't research or use the web, and don't read any other files. When reply-{turns}.md is written, respond with only: done"""


def main():
    convos = bm.read_jsonl(bm.PROMPTS / "dev_multiturn_r3.jsonl")
    jobs = []
    for model in MODELS:
        for cond in CONDS:
            for convo in convos:
                folder = bm.RAW / "round3-dev" / model / cond / convo["id"]
                folder.mkdir(parents=True, exist_ok=True)
                for n, turn in enumerate(convo["turns"], 1):
                    (folder / f"turn-{n}.txt").write_text(turn)
                jobs.append({"id": f"r3dev:{model}:{cond}:{convo['id']}", "kind": "multiturn", "set": "r3dev",
                             "model": model, "cond": cond, "rep": 1, "convo": convo["id"], "turns": len(convo["turns"]),
                             "dir": str(folder),
                             "prompt": TEMPLATE.format(folder=str(folder), turns=len(convo["turns"]), skill_block=bm.skill_block(cond))})
    speed = {"claude-opus-5.5": 12, "gpt-6.1-sol": 6, "grok-4.7": 3, "gemini-3.8-flash": 2, "mai-code-1.1-flash": 1}
    jobs.sort(key=lambda j: (-speed[j["model"]], j["id"]))
    run = bm.RAW / "round3-dev" / "manifest.run.json"
    run.write_text(json.dumps(jobs, ensure_ascii=False))
    committed = json.dumps(jobs, ensure_ascii=False).replace(str(ROOT), "<eval>")
    (ROOT / "manifest_round3_dev.json").write_text(committed)
    print(f"round 3 dev jobs: {len(jobs)} ({len(MODELS)} models x {len(CONDS)} conditions x {len(convos)} conversations)")
    print(f"run with: {run}")


if __name__ == "__main__":
    main()
