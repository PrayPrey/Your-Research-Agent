"""Generate the 200-word research ideas (idea.md) from the bundled YouRA originals.

For every task folder under results/generations/idea_and_proposal/youra/<lane>/
(lanes: sonnet45, opus45), this script assembles the idea-conversion prompt
from the bundled source artifacts and sends it to an LLM via OpenRouter:

    task.md                      original MLR-Bench task description
    02_hypothesis_generation.md  YouRA Phase 2A Extended hypothesis (bundled
                                 copy of the pipeline's 02a_extended_hypothesis.md,
                                 the summary variant, not the _full variant)
                        |
                        v  (prompt template below)
    idea_prompt.txt              the assembled prompt (verbatim record)
    idea.md                      the generated 200-word research idea

The original pipeline recorded this prompt verbatim for one task (sonnet45
iclr2023_bands, bundled as idea_prompt.txt); the rebuilt prompt is
byte-identical to that record. The remaining tasks did not save their idea
prompt, so their bundled idea.md cannot be byte-verified; regenerating them
uses the same template. Run with --verify for the offline comparison.

Usage:
    export OPENROUTER_API_KEY=...       # or put it in .env
    python generate_research_ideas.py            # fill missing idea.md
    python generate_research_ideas.py --verify   # offline prompt check
    python generate_research_ideas.py --lane opus45 --force --task icml2023_tom
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

IDEA_TEMPLATE = """You are an excellent machine learning researcher. Below is an original research task description and a scientifically clarified hypothesis that has been rigorously formalized through Extended workflow.

The extended hypothesis includes:
- Formal hypothesis statement with causal claims
- Operationalized variables (independent, dependent, controlled)
- Evidence-backed causal mechanism
- Testable predictions and falsification criteria
- Theoretical and practical contributions

Your job is to synthesize these into a concise, compelling research idea in exactly 200 words or less.

The research idea should include the following three sections:

1. Title: A concise and descriptive title for the research idea (based on the clarified hypothesis).

2. Motivation: A brief explanation of why this research is important and what problems it aims to solve (synthesize from the original task context, identified research gap, and the hypothesis's rationale).

3. Main Idea: A clear and detailed description of the proposed research idea, including:
   - The core hypothesis and causal mechanism
   - Key methodology approach (how variables will be tested)
   - Expected outcomes and potential impact
   - Write concisely for general understanding while maintaining scientific accuracy

IMPORTANT:
- Do NOT invent new ideas or approaches. Faithfully represent the extended hypothesis.
- Focus on the CORE INNOVATION: What is the key insight/mechanism that makes this hypothesis novel?
- Synthesize the technical details into an accessible yet accurate summary.
- Emphasize the causal mechanism and testable predictions.
- The total output should be approximately 200 words."""

IDEA_CLOSING = (
    "Please provide the research idea directly in the specified format "
    "(Title, Motivation, Main Idea)."
)


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
                return line.split("=", 1)[1].strip().strip("\"\'")
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


def build_idea_prompt(task_text: str, hypothesis_text: str) -> str:
    return (
        IDEA_TEMPLATE
        + "\n\n=== ORIGINAL TASK DESCRIPTION ===\n"
        + task_text
        + "\n\n=== SCIENTIFICALLY CLARIFIED HYPOTHESIS (Extended) ===\n"
        + hypothesis_text
        + "\n\n"
        + IDEA_CLOSING
    )


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
    parser.add_argument("--force", action="store_true", help="Regenerate idea.md even if it exists")
    parser.add_argument("--verify", action="store_true",
                        help="No API calls: rebuild every prompt and compare with the bundled idea_prompt.txt")
    parser.add_argument("--sleep", type=float, default=1.0, help="Seconds between API calls")
    args = parser.parse_args()
    args.root = args.root or DEFAULT_ROOT / args.lane

    if not args.root.is_dir():
        raise SystemExit(f"Task root not found: {args.root}")

    if args.verify:
        same = diff = missing = unsaved = 0
        for d in iter_task_dirs(args.root, args.task):
            src_task, src_hyp = d / "task.md", d / "02_hypothesis_generation.md"
            saved = d / "idea_prompt.txt"
            if not (src_task.exists() and src_hyp.exists()):
                missing += 1
                print(f"[MISSING] {d.name}")
                continue
            if not saved.exists():
                unsaved += 1
                continue
            rebuilt = build_idea_prompt(read_text(src_task), read_text(src_hyp))
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
    for d in iter_task_dirs(args.root, args.task):
        src_task, src_hyp = d / "task.md", d / "02_hypothesis_generation.md"
        if not (src_task.exists() and src_hyp.exists()):
            print(f"[SKIP] {d.name}: missing source files")
            skipped += 1
            continue
        out = d / "idea.md"
        if out.exists() and not args.force:
            skipped += 1
            continue
        prompt = build_idea_prompt(read_text(src_task), read_text(src_hyp))
        prompt_file = d / "idea_prompt.txt"
        if not prompt_file.exists():
            prompt_file.write_text(prompt, encoding="utf-8")
        print(f"[GEN] {d.name}")
        idea = call_openrouter(prompt, api_key, args.model, max_tokens=1000)
        if idea:
            out.write_text(idea, encoding="utf-8")
            done += 1
        else:
            failed += 1
        time.sleep(args.sleep)
    print(f"generated={done} skipped={skipped} failed={failed}")


if __name__ == "__main__":
    main()
