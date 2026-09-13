#!/usr/bin/env python3
"""
Phase Auto-Responder Test — Tests each phase's LLM resume prompt pipeline.

For each phase (phase0 ~ phase65):
1. Creates a fake active_phase.json
2. Loads phase config YAML
3. Loads phase-specific prompt from .claude/prompts/{phase}_responder.md
4. Calls OpenRouter LLM with a simulated conversation snippet
5. Parses the response (PHASE_COMPLETE / MUST_STOP / resume prompt)
6. Reports PASS/FAIL

Usage:
  python3 test_phase_responders.py                  # Test all phases
  python3 test_phase_responders.py phase0 phase3    # Test specific phases
  python3 test_phase_responders.py --dry-run         # Skip LLM call, test config loading only
"""

import json
import os
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
CACHE_DIR = SCRIPT_DIR / ".cache"
ACTIVE_PHASE_FILE = CACHE_DIR / "active_phase.json"
PROJECT_DIR = SCRIPT_DIR.parent.parent

# All phases to test
ALL_PHASES = [
    "phase0", "phase1", "phase2a", "phase2b", "phase2c",
    "phase3", "phase4", "phase45", "phase6", "phase65",
]

# Simulated conversation snippets per phase (realistic stop scenarios)
FAKE_CONVERSATIONS = {
    "phase0": """assistant: I've started the brainstorming session and created the initial research question outline.
The research topic has been documented in 00_brainstorm_session.md.

Should I continue with the next step of the brainstorming process?""",

    "phase1": """assistant: I've completed the literature search and found 15 relevant papers.
The research data has been compiled into 01_research_data.md.

I need to organize the findings into categories. Should I proceed?""",

    "phase2a": """assistant: Round 1 of the 4-perspective discussion is complete.
The Novelty perspective has been documented. Moving to Falsifiability next.

Shall I continue with Round 2?""",

    "phase2b": """assistant: I've decomposed the main hypothesis into 3 sub-hypotheses:
- h-m1: Main hypothesis variant 1
- h-e1: Exploratory hypothesis
- h-m2: Main hypothesis variant 2

The verification plan has been saved to 02b_verification_plan.md. Continue?""",

    "phase2c": """assistant: I've completed the Archon KB search and found relevant experiment cases.
Now I need to search Exa for implementation code examples for hypothesis h-e1.

Should I proceed with the Exa search?""",

    "phase3": """assistant: I've generated the PRD and architecture documents for h-e1.
The implementation plan is saved in 03_prd.md and 03_architecture.md.

Next I need to create the task definitions. Continue?""",

    "phase4": """assistant: Task 1 of 5 is complete. The training script has been written and tested.
Current progress: 1/5 tasks done.

Should I proceed to Task 2?""",

    "phase45": """assistant: I've analyzed all hypothesis results from h-m1, h-e1, and h-m2.
The cross-hypothesis comparison is being generated.

Continue with the synthesis?""",

    "phase6": """assistant: I've written the Introduction and Related Work sections of the paper.
Now generating the Methodology section based on experiment results.

Should I continue with the next section?""",

    "phase65": """assistant: Round 1 of the adversarial review is complete.
The Devil's Advocate has raised 3 major concerns about the methodology.

Shall I proceed with addressing these concerns?""",
}


def load_api_key() -> str:
    """Load OpenRouter API key from .env file."""
    env_file = PROJECT_DIR / ".env"
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("OPENROUTER_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return os.environ.get("OPENROUTER_API_KEY", "")


def test_phase(phase: str, dry_run: bool = False) -> dict:
    """Test a single phase's auto-responder pipeline."""
    result = {
        "phase": phase,
        "config_loaded": False,
        "prompt_loaded": False,
        "prompt_file": "",
        "prompt_length": 0,
        "llm_called": False,
        "llm_response_type": "",
        "llm_response_preview": "",
        "passed": False,
        "error": "",
    }

    # Step 1: Check phase config exists
    config_file = SCRIPT_DIR / f"{phase}_auto_config.yaml"
    if not config_file.exists():
        result["error"] = f"Config file not found: {config_file.name}"
        return result

    try:
        import yaml
        with open(config_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
        result["config_loaded"] = True
    except Exception as e:
        result["error"] = f"Config load failed: {e}"
        return result

    # Verify phase field matches
    config_phase = config.get("phase", "")
    if config_phase != phase:
        result["error"] = f"Config phase mismatch: expected '{phase}', got '{config_phase}'"
        return result

    # Step 2: Resolve prompt file
    prompt_file = config.get("prompt_file", "")
    if not prompt_file:
        # Fallback: read from auto_responder_config.yaml
        global_config_path = SCRIPT_DIR / "auto_responder_config.yaml"
        try:
            with open(global_config_path, "r", encoding="utf-8") as f:
                global_config = yaml.safe_load(f) or {}
            prompts_dir = global_config.get("prompts_dir", "")
            if prompts_dir:
                prompt_file = str(Path(prompts_dir) / f"{phase}_responder.md")
        except Exception as e:
            result["error"] = f"Global config load failed: {e}"
            return result

    if not prompt_file:
        result["error"] = "Could not resolve prompt_file path"
        return result

    result["prompt_file"] = prompt_file

    # Step 3: Load prompt content
    prompt_path = Path(prompt_file)
    if not prompt_path.exists():
        result["error"] = f"Prompt file not found: {prompt_file}"
        return result

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_content = f.read()
        result["prompt_loaded"] = True
        result["prompt_length"] = len(prompt_content)
    except Exception as e:
        result["error"] = f"Prompt read failed: {e}"
        return result

    if not prompt_content.strip():
        result["error"] = "Prompt file is empty"
        return result

    # Step 4: Dry run stops here
    if dry_run:
        result["passed"] = True
        result["llm_response_type"] = "(dry-run: skipped)"
        return result

    # Step 5: Call LLM
    api_key = load_api_key()
    if not api_key:
        result["error"] = "No OPENROUTER_API_KEY found"
        return result

    conversation_text = FAKE_CONVERSATIONS.get(phase, "assistant: Phase is in progress. Continue?")
    file_diff_summary = "Files changed since last check:\n  + 00_brainstorm_session.md (new, 2048 bytes)\n  ~ verification_state.yaml (size: 1024 → 1280 bytes)"

    user_message = f"""## Recent Conversation (Last {len(conversation_text)} chars)
```
{conversation_text}
```

## File Changes
{file_diff_summary}

---

Based on the conversation above and the phase workflow instructions, determine what to do next.
Respond with one of:
1. PHASE_COMPLETE — if the phase is done.
2. MUST_STOP: <reason> — if human intervention is truly needed.
3. A resume prompt — plain text to send to Claude to continue.
"""

    openrouter = config.get("openrouter", {})
    model = openrouter.get("model", "openai/gpt-5.2")

    try:
        import requests
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "X-Title": "YouRA Phase Responder Test",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": prompt_content},
                    {"role": "user", "content": user_message},
                ],
                "max_tokens": 1000,
            },
            timeout=120,
        )

        if response.status_code != 200:
            result["error"] = f"LLM API error: {response.status_code} - {response.text[:200]}"
            return result

        llm_response = (
            response.json()
            .get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )

        result["llm_called"] = True

        # Parse response type
        stripped = llm_response.strip()
        if stripped.upper().startswith("PHASE_COMPLETE"):
            result["llm_response_type"] = "PHASE_COMPLETE"
        elif stripped.upper().startswith("MUST_STOP"):
            result["llm_response_type"] = "MUST_STOP"
        else:
            result["llm_response_type"] = "RESUME_PROMPT"

        result["llm_response_preview"] = stripped[:200]
        result["passed"] = True

    except Exception as e:
        result["error"] = f"LLM call failed: {e}"

    return result


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    if dry_run:
        args.remove("--dry-run")

    phases = args if args else ALL_PHASES
    invalid = [p for p in phases if p not in ALL_PHASES]
    if invalid:
        print(f"ERROR: Unknown phases: {invalid}")
        print(f"Valid phases: {ALL_PHASES}")
        sys.exit(1)

    print("=" * 70)
    print(f"Phase Auto-Responder Test {'(DRY RUN)' if dry_run else '(LIVE LLM)'}")
    print(f"Testing {len(phases)} phases: {', '.join(phases)}")
    print("=" * 70)

    results = []
    for phase in phases:
        print(f"\n{'─' * 50}")
        print(f"Testing {phase}...")

        r = test_phase(phase, dry_run=dry_run)
        results.append(r)

        status = "PASS ✓" if r["passed"] else "FAIL ✗"
        print(f"  Config loaded:  {'Yes' if r['config_loaded'] else 'No'}")
        print(f"  Prompt file:    {r['prompt_file']}")
        print(f"  Prompt loaded:  {'Yes' if r['prompt_loaded'] else 'No'} ({r['prompt_length']} chars)")

        if not dry_run and r["llm_called"]:
            print(f"  LLM response:   {r['llm_response_type']}")
            print(f"  Preview:        {r['llm_response_preview'][:100]}...")

        if r["error"]:
            print(f"  Error:          {r['error']}")

        print(f"  Result:         {status}")

    # Summary
    passed = sum(1 for r in results if r["passed"])
    failed = sum(1 for r in results if not r["passed"])

    print(f"\n{'=' * 70}")
    print(f"SUMMARY: {passed}/{len(results)} passed, {failed} failed")

    if failed:
        print("\nFailed phases:")
        for r in results:
            if not r["passed"]:
                print(f"  - {r['phase']}: {r['error']}")

    print("=" * 70)

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
