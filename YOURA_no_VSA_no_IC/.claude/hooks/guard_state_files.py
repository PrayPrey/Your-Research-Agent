#!/usr/bin/env python3
"""
PreToolUse guard for Read/Edit/Write/MultiEdit/NotebookEdit — VSA-IC ablation
enforcement (ws4 spec R8 hardening).

In shadow mode (--state-mode shadow), the model must never touch the three
VSA target files; state is relayed via prompt context + ```state restate
blocks. The 2026-07-09 dl4c run proved prompt-level instructions alone are
insufficient (a conflicting instruction slipped through and the model wrote
verification_state.yaml to disk). This hook makes the disable physical.

Active ONLY when .cache/active_phase.json exists, is enabled, and carries
state_mode == "shadow" (written by the run_phaseN launchers). Normal-mode
runs and interactive sessions are entirely unaffected.

Blocked in shadow mode:
  - any Read/Edit/Write/MultiEdit/NotebookEdit whose target path basename is
    verification_state.yaml / 04_checkpoint.yaml / 03_tasks.yaml
  - any access under a .ablation_shadow/ directory (harness-private)

NOT blocked: template files (verification_state_template.yaml etc. — schema
templates, not pipeline state) and every other file.

Hook contract (Claude Code PreToolUse):
- Read JSON from stdin: {"tool_name":"...","tool_input":{...}, ...}
- Print {"decision":"block","reason":"..."} to refuse the call.
- On any error / inactive shadow mode, exit 0 silently.
"""

import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
# Env override is for unit tests only.
ACTIVE_PHASE_FILE = Path(os.environ.get(
    "YOURA_ACTIVE_PHASE_FILE", str(SCRIPT_DIR / ".cache" / "active_phase.json")))

TARGET_BASENAMES = {
    "verification_state.yaml",
    "04_checkpoint.yaml",
    "03_tasks.yaml",
}
SHADOW_DIR_NAME = ".ablation_shadow"

FILE_TOOLS = {"Read", "Edit", "Write", "MultiEdit", "NotebookEdit"}

BLOCK_REASON = (
    "ABLATION MODE (VSA-IC): file access to {name} is disabled in this run. "
    "All pipeline state is provided in the 'Current Pipeline State' section of "
    "your prompt — use it instead of reading the file. To record a state "
    "update, restate the updated state in a ```state fenced block at the end "
    "of your message (the harness persists it); a ```state block restatement "
    "counts as the file having been generated/updated. Continue with the next "
    "step of your workflow."
)


def shadow_mode_active() -> bool:
    try:
        with open(ACTIVE_PHASE_FILE, "r", encoding="utf-8") as f:
            info = json.load(f)
        return bool(info.get("enabled")) and info.get("state_mode") == "shadow"
    except Exception:
        return False


def extract_paths(tool_input: dict) -> list:
    paths = []
    for key in ("file_path", "notebook_path", "path"):
        val = tool_input.get(key)
        if isinstance(val, str) and val:
            paths.append(val)
    # MultiEdit variants carry a list of edits with a single file_path at top
    # level (already covered); some clients nest {"edits":[...]} — top-level
    # file_path is authoritative there too.
    return paths


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    if tool_name not in FILE_TOOLS:
        sys.exit(0)

    if not shadow_mode_active():
        sys.exit(0)

    tool_input = data.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        sys.exit(0)

    for raw in extract_paths(tool_input):
        try:
            p = Path(raw)
            basename = p.name
        except Exception:
            continue
        if basename in TARGET_BASENAMES or SHADOW_DIR_NAME in p.parts:
            print(json.dumps({
                "decision": "block",
                "reason": BLOCK_REASON.format(name=basename),
            }))
            sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
