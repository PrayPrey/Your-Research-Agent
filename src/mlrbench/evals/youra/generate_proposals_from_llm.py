"""Generate the research proposals (proposal.md) from the bundled YouRA originals.

For every task folder under results/generations/idea_and_proposal/youra/<lane>/
(lanes: sonnet45, opus45), this script assembles the proposal-writing prompt
and sends it to an LLM via OpenRouter:

    task.md                      original MLR-Bench task description
    idea.md                      the research idea (see generate_research_ideas.py)
    02_hypothesis_generation.md  YouRA Phase 2A Extended hypothesis, embedded
                                 in full (bundled copy of the pipeline's
                                 02a_extended_hypothesis.md, the summary
                                 variant, not the _full variant)
                        |
                        v  (prompt template below)
    prompt.txt                   the assembled prompt (verbatim record)
    proposal.md                  the generated proposal

By default the bundled prompt.txt is replayed verbatim when present, so the
API sees exactly the prompt that produced the released proposal.md. With
--rebuild-prompt the prompt is rebuilt from the three source files instead;
the rebuild is byte-identical to every bundled prompt.txt (401 tasks across
both lanes; sonnet45 iclr2023_bands did not record its proposal prompt).
Run --verify for the comparison without calling any API.

The prompt does not ask for a References list; each lane's related_work.md is
a final artifact of the original pipeline (see generate_related_work.py) and
is not touched by proposal regeneration.

Usage:
    export OPENROUTER_API_KEY=...       # or put it in .env
    python generate_proposals_from_llm.py             # fill missing proposal.md
    python generate_proposals_from_llm.py --verify    # offline prompt check
    python generate_proposals_from_llm.py --lane opus45 --verify
    python generate_proposals_from_llm.py --lane opus45 --force --task iclr2023_bands
"""

import argparse
import json
import os
import time
from pathlib import Path
from typing import Optional

import requests

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_ROOT = REPO_ROOT / "results" / "generations" / "idea_and_proposal" / "youra"
LANES = ("sonnet45", "opus45")
# The conversion adapter reported in the paper: Claude Opus 4.5 at temperature 0,
# independent of the lane backbone that produced the hypothesis.
DEFAULT_MODEL = "anthropic/claude-opus-4.5"

PROPOSAL_TEMPLATE = """You are an excellent machine learning researcher!
Please generate a detailed research proposal based on a given task description, a research idea and their hypothesis.
The proposal should be about 2000 words and include the following four sections:
1. Title: a concise and descriptive title for the research proposal.
2. Introduction: background, research objectives and significance.
3. Methodology: detailed and precise research design (including data collection, full algorithmic steps and/or mathematical formulas where appropriate, and full details about experimental design to validate the method, with evaluation metrics).
4. Expected Outcomes & Impact.
The proposal should be well-structured and clearly articulate the research plan.
When writing mathematical formulas, you should use LaTeX syntax. For inline formulas, use single dollar signs, for example: $x^2$ to represent x squared. For block equations, use double dollar signs at the beginning and end, for example: $$x^2$$.
Please directly respond to the proposal."""


def read_text(path: Path) -> str:
    """Read a bundled artifact, tolerating legacy encodings and CRLF line endings."""
    data = path.read_bytes()
    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            text = data.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = data.decode("utf-8", errors="replace")
    return text.replace("\r\n", "\n")


def load_api_key() -> Optional[str]:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if api_key:
        return api_key
    env_file = Path(".env")
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line.startswith("OPENROUTER_API_KEY="):
                return line.split("=", 1)[1].strip().strip("\"'")
    return None


def call_openrouter(prompt: str, api_key: str, model: str, max_tokens: int) -> Optional[str]:
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
            "max_tokens": max_tokens,
        },
        timeout=300,
    )
    response.raise_for_status()
    result = response.json()
    choices = result.get("choices")
    if not choices:
        print(f"    [API] Unexpected response: {json.dumps(result)[:500]}")
        return None
    return choices[0]["message"]["content"]


def build_proposal_prompt(task_text: str, idea_text: str, hypothesis_text: str) -> str:
    """Assemble the prompt exactly as the original pipeline did.

    Each source document is embedded verbatim (trailing newlines included)
    inside a code fence; the rebuild is byte-identical to the bundled
    prompt.txt records.
    """
    return (
        PROPOSAL_TEMPLATE
        + "\nHere is the task:\n```\n" + task_text
        + "\n```\nHere is the idea:\n```\n" + idea_text
        + "\n```\nHere is the hypothesis:\n```\n" + hypothesis_text
        + "\n```"
    )


SOURCES = ("task.md", "idea.md", "02_hypothesis_generation.md")


def rebuild_from_sources(d: Path) -> Optional[str]:
    paths = [d / name for name in SOURCES]
    if not all(p.exists() for p in paths):
        return None
    return build_proposal_prompt(*(read_text(p) for p in paths))


def iter_task_dirs(root: Path, only):
    for d in sorted(p for p in root.iterdir() if p.is_dir()):
        if only and d.name not in only:
            continue
        yield d


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--lane", choices=LANES, default="sonnet45")
    parser.add_argument("--root", type=Path, default=None,
                        help="Folder holding one subfolder per task (default: bundled <lane> folder)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="OpenRouter model id")
    parser.add_argument("--task", action="append", help="Only process this task (repeatable)")
    parser.add_argument("--force", action="store_true", help="Regenerate proposal.md even if it exists")
    parser.add_argument("--rebuild-prompt", action="store_true",
                        help="Rebuild the prompt from the source files even when prompt.txt exists")
    parser.add_argument("--verify", action="store_true",
                        help="No API calls: rebuild every prompt and compare with the bundled prompt.txt")
    parser.add_argument("--sleep", type=float, default=1.0, help="Seconds between API calls")
    args = parser.parse_args()

    root = args.root or DEFAULT_ROOT / args.lane
    if not root.is_dir():
        raise SystemExit(f"Task root not found: {root}")

    if args.verify:
        same = diff = missing = unsaved = 0
        for d in iter_task_dirs(root, args.task):
            saved = d / "prompt.txt"
            rebuilt = rebuild_from_sources(d)
            if rebuilt is None:
                missing += 1
                print(f"[MISSING] {d.name}")
                continue
            if not saved.exists():
                unsaved += 1
                continue
            if rebuilt == read_text(saved):
                same += 1
            else:
                diff += 1
                print(f"[DIFF] {d.name}")
        print(f"verify: identical={same} different={diff} no-saved-prompt={unsaved} missing-inputs={missing}")
        return

    api_key = load_api_key()
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY not set (env var or .env)")

    done = skipped = failed = 0
    for d in iter_task_dirs(root, args.task):
        out = d / "proposal.md"
        if out.exists() and not args.force:
            skipped += 1
            continue
        saved = d / "prompt.txt"
        if saved.exists() and not args.rebuild_prompt:
            prompt = read_text(saved)
        else:
            prompt = rebuild_from_sources(d)
            if prompt is None:
                print(f"[SKIP] {d.name}: no prompt.txt and missing source files")
                skipped += 1
                continue
            if not saved.exists():
                saved.write_text(prompt, encoding="utf-8")
        print(f"[GEN] {d.name}")
        proposal = call_openrouter(prompt, api_key, model=args.model, max_tokens=16384)
        if proposal:
            out.write_text(proposal, encoding="utf-8")
            done += 1
        else:
            failed += 1
        time.sleep(args.sleep)
    print(f"generated={done} skipped={skipped} failed={failed}")


if __name__ == "__main__":
    main()
