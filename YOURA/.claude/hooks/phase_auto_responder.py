#!/usr/bin/env python3
"""
Phase-Specific Auto-Responder

LLM-driven orchestrator for Phase 0~6.5.
Two-stage hook design: self-check first, then LLM decision.

Flow (two-stage):
  1st Stop (self-check not done):
    → block + send self-check prompt to main Claude session
    → save selfcheck flag with current transcript length
  2nd Stop (self-check done):
    → read transcript up to the saved length (pre-selfcheck context)
    → call GPT-5.2 with that context + file diff
    → parse response: PHASE_COMPLETE / MUST_STOP / resume prompt
    → delete selfcheck flag (so next Stop starts fresh)

Steps:
1. Load active_phase.json → get phase config
1.5. PHASE_COMPLETE lock check
2. Load phase config YAML
3. Read transcript
4. Fast-path completion check
5. Rate limit check
5.5. Two-stage routing (selfcheck flag check)
6. Load API key (2nd stage only)
7. Load phase prompt (2nd stage only)
8. Snapshot-based file diff (2nd stage only)
9. Call OpenRouter LLM (2nd stage only)
10. Parse LLM response (2nd stage only)

Author: Anonymous
"""

import json
import os
import sys
import time
import glob
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# ============================================================
# Path Configuration
# ============================================================
SCRIPT_DIR = Path(__file__).parent
CACHE_DIR = SCRIPT_DIR / ".cache"
ACTIVE_PHASE_FILE = CACHE_DIR / "active_phase.json"
PROJECT_DIR = SCRIPT_DIR.parent.parent  # project root

# Import shared utilities from auto_responder_full
sys.path.insert(0, str(SCRIPT_DIR))
from auto_responder_full import (
    read_transcript,
    extract_conversation_text,
    output_decision,
    Logger,
    load_api_key,
)


# Global logger
logger: Optional[Logger] = None


def log(message: str):
    """Log helper."""
    if logger:
        logger.info(message)
    else:
        print(f"[PHASE-RESPONDER] {message}", file=sys.stderr)


# ============================================================
# Active Phase Management
# ============================================================
def load_active_phase() -> Optional[Dict[str, Any]]:
    """
    Read .cache/active_phase.json to determine which phase is active.

    Returns:
        Dict with phase info, or None if no active phase.
    """
    if not ACTIVE_PHASE_FILE.exists():
        return None

    try:
        with open(ACTIVE_PHASE_FILE, "r", encoding="utf-8") as f:
            phase_info = json.load(f)

        if not phase_info.get("enabled", False):
            return None

        return phase_info
    except Exception as e:
        log(f"Failed to load active_phase.json: {e}")
        return None


# ============================================================
# Phase Config Loading
# ============================================================
def load_phase_config(config_path: str) -> Optional[Dict[str, Any]]:
    """
    Load phase-specific YAML config file.
    """
    try:
        import yaml
    except ImportError:
        log("PyYAML not installed")
        return None

    config_file = Path(config_path)
    if not config_file.exists():
        log(f"Phase config not found: {config_path}")
        return None

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        if config is None:
            log("Phase config file is empty")
            return None

        return config
    except Exception as e:
        log(f"Failed to load phase config: {e}")
        return None


# ============================================================
# Rate Limiting (Phase-specific)
# ============================================================
def check_phase_rate_limit(phase: str, config: Dict[str, Any]) -> bool:
    """
    Check if phase hook has been triggered too many times.

    Returns True if rate limit exceeded (should stop), False otherwise.
    """
    rate_config = config.get("rate_limit", {})
    max_triggers = rate_config.get("max_triggers", 4)
    time_window = rate_config.get("time_window_seconds", 180)

    history_file = CACHE_DIR / f"{phase}_trigger_history.json"
    current_time = time.time()
    history = []

    if history_file.exists():
        try:
            with open(history_file, "r") as f:
                history = json.load(f)
        except Exception:
            history = []

    # Filter to recent triggers only
    history = [t for t in history if current_time - t < time_window]

    # Add current trigger
    history.append(current_time)

    # Save updated history
    try:
        with open(history_file, "w") as f:
            json.dump(history, f)
    except Exception as e:
        log(f"Failed to save trigger history: {e}")

    # Check if exceeded
    if len(history) >= max_triggers:
        log(f"Phase {phase} rate limit exceeded: {len(history)} triggers in {time_window}s")
        return True

    log(f"Phase {phase} trigger count: {len(history)}/{max_triggers} in last {time_window}s")
    return False


# ============================================================
# Snapshot-Based File Diff
# ============================================================

def _collect_folder_snapshot(research_folder: str) -> Dict[str, int]:
    """
    Walk the research folder and return a dict of {relative_path: file_size_bytes}.
    Hidden directories and _archive/ are skipped.
    """
    snapshot: Dict[str, int] = {}
    if not research_folder or not os.path.isdir(research_folder):
        return snapshot

    try:
        for root, dirs, files in os.walk(research_folder):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "_archive"]
            for fname in files:
                fpath = os.path.join(root, fname)
                try:
                    rel = os.path.relpath(fpath, research_folder)
                    snapshot[rel] = os.path.getsize(fpath)
                except Exception:
                    continue
    except Exception:
        pass

    return snapshot


def _snapshot_path(phase: str) -> Path:
    """Return the per-phase snapshot file path in .cache/."""
    return CACHE_DIR / f"{phase}_file_snapshot.json"


def _load_snapshot(phase: str) -> Dict[str, int]:
    """Load previous snapshot for this phase. Returns empty dict if none exists."""
    path = _snapshot_path(phase)
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("files", {})
    except Exception:
        return {}


def _save_snapshot(phase: str, snapshot: Dict[str, int]) -> None:
    """Save current snapshot for this phase to .cache/."""
    path = _snapshot_path(phase)
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "files": snapshot,
                },
                f,
                indent=2,
            )
    except Exception:
        pass


def build_file_diff_summary(phase: str, research_folder: str) -> str:
    """
    Compare the current research folder state against the previous per-phase snapshot.
    Saves the new snapshot for the next hook call.
    """
    if not research_folder or not os.path.isdir(research_folder):
        return "No research folder detected."

    prev = _load_snapshot(phase)
    curr = _collect_folder_snapshot(research_folder)

    # Save snapshot immediately so the next hook call sees this state
    _save_snapshot(phase, curr)

    prev_keys = set(prev.keys())
    curr_keys = set(curr.keys())

    new_files = sorted(curr_keys - prev_keys)
    removed_files = sorted(prev_keys - curr_keys)
    modified_files = sorted(
        f for f in curr_keys & prev_keys
        if curr[f] != prev[f]
    )
    unchanged_count = len(curr_keys & prev_keys) - len(modified_files)

    lines = []

    if not prev:
        lines.append(f"File snapshot (first check — no previous baseline):")
        lines.append(f"  Total files: {len(curr)}")
        for rel in sorted(curr.keys())[:30]:
            lines.append(f"  + {rel} ({curr[rel]} bytes)")
        if len(curr) > 30:
            lines.append(f"  ... and {len(curr) - 30} more files")
        return "\n".join(lines)

    lines.append(f"File diff since last hook call (snapshot-based):")
    lines.append(f"  Unchanged: {unchanged_count} files")

    if new_files:
        lines.append(f"  New ({len(new_files)}):")
        for f in new_files[:20]:
            lines.append(f"    + {f} ({curr[f]} bytes)")
        if len(new_files) > 20:
            lines.append(f"    ... and {len(new_files) - 20} more")

    if removed_files:
        lines.append(f"  Removed ({len(removed_files)}):")
        for f in removed_files[:10]:
            lines.append(f"    - {f}")
        if len(removed_files) > 10:
            lines.append(f"    ... and {len(removed_files) - 10} more")

    if modified_files:
        lines.append(f"  Modified ({len(modified_files)}):")
        for f in modified_files[:10]:
            lines.append(f"    ~ {f} ({prev[f]} → {curr[f]} bytes)")
        if len(modified_files) > 10:
            lines.append(f"    ... and {len(modified_files) - 10} more")

    if not new_files and not removed_files and not modified_files:
        lines.append("  No file changes detected since last hook call.")

    return "\n".join(lines)


# ============================================================
# Two-Stage Self-Check Flag Management
# ============================================================

def _selfcheck_flag_path(phase: str) -> Path:
    """Return path for the selfcheck flag file."""
    return CACHE_DIR / f"{phase}_selfcheck.json"


def _load_selfcheck_flag(phase: str, session_key: str) -> Optional[Dict[str, Any]]:
    """Load selfcheck flag if it exists and matches current session.

    Returns:
        Dict with {"transcript_len": int, "session": str, "timestamp": str}
        or None if no valid flag exists.
    """
    path = _selfcheck_flag_path(phase)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Only valid if same session
        if data.get("session") != session_key:
            return None
        return data
    except Exception:
        return None


def _save_selfcheck_flag(phase: str, session_key: str, transcript_len: int) -> None:
    """Save selfcheck flag with transcript length at self-check time."""
    path = _selfcheck_flag_path(phase)
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "session": session_key,
                "transcript_len": transcript_len,
                "timestamp": datetime.now().isoformat(),
            }, f, indent=2)
    except Exception as e:
        log(f"Failed to save selfcheck flag: {e}")


def _delete_selfcheck_flag(phase: str) -> None:
    """Delete selfcheck flag (reset for next cycle)."""
    path = _selfcheck_flag_path(phase)
    try:
        if path.exists():
            path.unlink()
    except Exception:
        pass


def _build_selfcheck_prompt(phase: str, research_folder: str, hypothesis: str = None) -> str:
    """Build the self-check prompt sent to the MAIN Claude session.

    This prompt tells Claude to verify its own tracking files are up to date
    for the current step progress, and fix any missing updates.
    """
    h_line = f" for hypothesis {hypothesis}" if hypothesis else ""
    return (
        f"Perform a self-check{h_line}:\n\n"
        f"1. Read the current checkpoint/state files in the research folder:\n"
        f"   {research_folder}\n"
        f"2. Based on the steps you have completed so far, verify that all expected output files\n"
        f"   exist and are properly filled in.\n"
        f"3. If any files are MISSING or INCOMPLETE, generate/fix them now.\n"
        f"4. If everything is already complete, confirm.\n\n"
        f"Do NOT run experiments or generate new code — only verify and fix output files.\n"
        f"After this self-check, stop and wait. Do NOT continue the phase workflow."
    )


# ============================================================
# Prompt Template Loading + Variable Substitution
# ============================================================
def load_and_prepare_prompt(prompt_file: str, config: Dict[str, Any]) -> Optional[str]:
    """
    Load the phase-specific prompt file and substitute variables.
    """
    prompt_path = Path(prompt_file)
    if not prompt_path.exists():
        log(f"Prompt file not found: {prompt_file}")
        return None

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_content = f.read()
    except Exception as e:
        log(f"Failed to read prompt file: {e}")
        return None

    # Substitute research_inputs variables
    research_inputs = config.get("research_inputs", {})
    if research_inputs:
        for key, value in research_inputs.items():
            placeholder = "{" + key + "}"
            if isinstance(value, list):
                value_str = ", ".join(str(v) for v in value) if value else "None"
            else:
                value_str = str(value) if value else "None"
            prompt_content = prompt_content.replace(placeholder, value_str)

    return prompt_content


# ============================================================
# LLM Call (Phase-Specific)
# ============================================================
def call_phase_llm(
    conversation_text: str,
    file_diff_summary: str,
    prompt_content: str,
    config: Dict[str, Any],
    api_key: str,
) -> Optional[str]:
    """
    Call OpenRouter LLM with the phase-specific prompt and conversation context.
    """
    import requests

    openrouter = config.get("openrouter", {})

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

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "X-Title": "YouRA Phase Auto-Responder",
            },
            json={
                "model": openrouter.get("model", "openai/gpt-5.2"),
                "messages": [
                    {"role": "system", "content": prompt_content},
                    {"role": "user", "content": user_message},
                ],
                "max_tokens": openrouter.get("max_tokens", 3000),
            },
            timeout=openrouter.get("timeout_seconds", 180),
        )

        if response.status_code == 200:
            result = response.json()
            llm_response = (
                result.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )

            log(f"LLM response length: {len(llm_response)}")

            # Log full response if debug enabled
            debug_config = config.get("debug", {})
            if debug_config.get("log_llm_interactions", False):
                log("=" * 60)
                log("PHASE LLM FULL RESPONSE:")
                log(llm_response)
                log("=" * 60)

            return llm_response
        else:
            log(f"LLM API error: {response.status_code} - {response.text[:200]}")
            return None

    except Exception as e:
        log(f"LLM API call failed: {e}")
        return None


# ============================================================
# Main Entry Point
# ============================================================
def main(hook_info: Dict[str, Any] = None):
    """
    Main entry point — called by hook_router.py when active_phase.json exists.

    Two-stage design:
      1st Stop: selfcheck flag absent → send self-check prompt to main Claude, set flag
      2nd Stop: selfcheck flag present → call GPT-5.2 for resume/complete decision, clear flag
    """
    global logger

    # ========================================
    # Step 1: Load active phase
    # ========================================
    phase_info = load_active_phase()
    if phase_info is None:
        output_decision("approve", "[PHASE-RESPONDER] No active phase")
        return

    phase = phase_info.get("phase", "unknown")
    config_path = phase_info.get("config_file", "")
    session_key = phase_info.get("started_at", "")

    # ========================================
    # Step 1.5: PHASE_COMPLETE lock check
    # ========================================
    phase_complete_lock = CACHE_DIR / f"{phase}_complete.lock"
    if phase_complete_lock.exists() and session_key:
        try:
            lock_session = phase_complete_lock.read_text().strip()
            if lock_session == session_key:
                output_decision("approve", f"[PHASE-RESPONDER] Phase {phase} already completed (lock)")
                return
        except Exception:
            pass

    # ========================================
    # Step 2: Load phase config
    # ========================================
    config = load_phase_config(config_path)
    if config is None:
        output_decision("approve", f"[PHASE-RESPONDER] Failed to load config: {config_path}")
        return

    if not config.get("enabled", True):
        output_decision("approve", f"[PHASE-RESPONDER] Phase {phase} disabled in config")
        return

    # Initialize logger
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    debug_config = config.get("debug", {})
    log_file = CACHE_DIR / debug_config.get("log_file", f"{phase}_auto_responder.log")
    logger = Logger(log_file, debug_config.get("verbose", True))

    log("=" * 60)
    log(f"Phase Auto-Responder — Phase: {phase}")

    # ========================================
    # Step 3: Read transcript
    # ========================================
    if hook_info is None:
        hook_info = {}

    transcript_path = hook_info.get("transcript_path", "")
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")

    messages = []
    conversation_text = ""

    if transcript_path and Path(transcript_path).exists():
        context_config = config.get("context", {})
        focus_chars = context_config.get("focus_chars", 5000)

        messages = read_transcript(transcript_path)
        conversation_text = extract_conversation_text(messages, max_chars=focus_chars)
        log(f"Transcript loaded: {len(conversation_text)} chars")
    else:
        log("No transcript available")

    if not conversation_text:
        log("No conversation text — allowing stop")
        output_decision("approve", f"[PHASE-RESPONDER] No conversation text")
        return

    # ========================================
    # Step 4: Fast-path completion check
    # ========================================
    completion_signals = config.get("completion_signals", [])
    conversation_lower = conversation_text.lower()

    for signal in completion_signals:
        if signal.lower() in conversation_lower:
            log(f"Completion signal detected: '{signal}'")
            _delete_selfcheck_flag(phase)
            output_decision("approve", f"[PHASE-RESPONDER] Phase {phase} complete: {signal}")
            return

    # ========================================
    # Step 5: Rate limit check
    # ========================================
    if check_phase_rate_limit(phase, config):
        log("Rate limit exceeded — allowing stop")
        _delete_selfcheck_flag(phase)
        output_decision(
            "approve",
            f"[PHASE-RESPONDER] Rate limit exceeded for {phase}. Hook auto-disabled.",
        )
        return

    # ========================================
    # Step 5.5: Two-stage routing
    # ========================================
    research_folder = phase_info.get("research_folder") or None

    if not research_folder and project_dir:
        candidates = []
        for pattern in [
            os.path.join(project_dir, "docs/youra_research/"),
            os.path.join(project_dir, "docs/youra_research/*/"),
            os.path.join(project_dir, "*/"),
            os.path.join(project_dir, "*/*/"),
        ]:
            for f in glob.glob(pattern):
                f = f.rstrip("/")
                if os.path.isdir(f) and os.path.exists(os.path.join(f, "00_brainstorm_session.md")):
                    candidates.append(f)
        if candidates:
            research_folder = max(candidates, key=os.path.getmtime)

    log(f"Research folder: {research_folder}")

    selfcheck_flag = _load_selfcheck_flag(phase, session_key)

    if selfcheck_flag is None:
        # ========================================
        # 1st Stage: Self-check prompt
        # ========================================
        log(f"1st stage: sending self-check prompt to main Claude session")

        hypothesis = phase_info.get("hypothesis")
        selfcheck_prompt = _build_selfcheck_prompt(phase, research_folder or "(unknown)", hypothesis)

        # Save flag with current transcript length (pre-selfcheck)
        _save_selfcheck_flag(phase, session_key, len(conversation_text))

        # Block stop and send self-check prompt to main Claude
        output_decision("block", f"[AUTO-RESPONDER] {selfcheck_prompt}")
        return

    # ========================================
    # 2nd Stage: LLM decision
    # ========================================
    log(f"2nd stage: LLM decision (selfcheck done)")

    # Use transcript length from BEFORE self-check for GPT-5.2 context
    pre_selfcheck_len = selfcheck_flag.get("transcript_len", len(conversation_text))
    if pre_selfcheck_len < len(conversation_text):
        # Trim conversation_text to pre-selfcheck length
        conversation_text_for_llm = conversation_text[:pre_selfcheck_len]
        log(f"Using pre-selfcheck transcript: {pre_selfcheck_len} chars (current: {len(conversation_text)})")
    else:
        conversation_text_for_llm = conversation_text
        log(f"Transcript unchanged since selfcheck: {len(conversation_text)} chars")

    # Delete selfcheck flag — next Stop will start fresh (1st stage again)
    _delete_selfcheck_flag(phase)

    # ========================================
    # Step 6: Load API key
    # ========================================
    openrouter = config.get("openrouter", {})
    if not openrouter.get("enabled", True):
        log("OpenRouter disabled — allowing stop")
        output_decision("approve", f"[PHASE-RESPONDER] LLM disabled for {phase}")
        return

    api_key_env = openrouter.get("api_key_env", "OPENROUTER_API_KEY")
    api_key = load_api_key(project_dir or str(SCRIPT_DIR.parent.parent), api_key_env)

    if not api_key:
        log("No API key — allowing stop")
        output_decision("approve", f"[PHASE-RESPONDER] No API key for {phase}")
        return

    # ========================================
    # Step 7: Load and prepare prompt
    # ========================================
    prompt_file = config.get("prompt_file", "")

    if not prompt_file:
        global_config_path = SCRIPT_DIR / "auto_responder_config.yaml"
        try:
            import yaml as _yaml
            with open(global_config_path, "r", encoding="utf-8") as _f:
                global_config = _yaml.safe_load(_f) or {}
            prompts_dir = global_config.get("prompts_dir", "")
            if prompts_dir:
                prompt_file = str(Path(prompts_dir) / f"{phase}_responder.md")
                log(f"prompt_file resolved from prompts_dir: {prompt_file}")
        except Exception as e:
            log(f"Warning: failed to load global config for prompts_dir: {e}")

    prompt_content = load_and_prepare_prompt(prompt_file, config)

    if not prompt_content:
        log("Failed to load prompt — allowing stop")
        output_decision("approve", f"[PHASE-RESPONDER] Failed to load prompt for {phase}")
        return

    # ========================================
    # Step 8: Snapshot-based file diff
    # ========================================
    if research_folder:
        file_diff_summary = build_file_diff_summary(phase, research_folder)
    else:
        file_diff_summary = "No research folder detected."

    # ========================================
    # Step 9: Call LLM
    # ========================================
    llm_response = call_phase_llm(
        conversation_text=conversation_text_for_llm,
        file_diff_summary=file_diff_summary,
        prompt_content=prompt_content,
        config=config,
        api_key=api_key,
    )

    if llm_response is None:
        log("LLM API failed — blocking stop with retry")
        output_decision(
            "block",
            f"[AUTO-RESPONDER] LLM API temporarily failed. Stop and wait.",
        )
        return

    # ========================================
    # Step 10: Parse LLM response
    # ========================================
    response_stripped = llm_response.strip()

    # Check for PHASE_COMPLETE
    if response_stripped.upper().startswith("PHASE_COMPLETE"):
        log(f"LLM decided: PHASE_COMPLETE for {phase}")
        try:
            phase_complete_lock = CACHE_DIR / f"{phase}_complete.lock"
            phase_complete_lock.write_text(session_key)
            log(f"Created PHASE_COMPLETE lock: {phase_complete_lock}")
        except Exception as _e:
            log(f"WARNING: failed to create PHASE_COMPLETE lock: {_e}")
        output_decision("approve", f"[PHASE-RESPONDER] Phase {phase} complete (LLM confirmed)")
        return

    # Check for MUST_STOP
    if response_stripped.upper().startswith("MUST_STOP"):
        reason = response_stripped[len("MUST_STOP:"):].strip() if ":" in response_stripped else response_stripped
        log(f"LLM decided: MUST_STOP for {phase}: {reason[:100]}")
        try:
            must_stop_path = CACHE_DIR / "must_stop.json"
            with open(must_stop_path, "w", encoding="utf-8") as _f:
                json.dump({"phase": phase, "reason": reason}, _f, indent=2)
            log(f"Wrote must_stop.json: {must_stop_path}")
        except Exception as _e:
            log(f"WARNING: failed to write must_stop.json: {_e}")
        output_decision("approve", f"[PHASE-RESPONDER] MUST_STOP: {reason[:200]}")
        return

    # Otherwise: resume prompt — block stop and send it
    log(f"LLM generated resume prompt ({len(response_stripped)} chars)")
    output_decision("block", f"[AUTO-RESPONDER] {response_stripped}")
    return


if __name__ == "__main__":
    # When called directly (not via hook_router), read stdin
    hook_info = {}
    try:
        if not sys.stdin.isatty():
            stdin_data = sys.stdin.read()
            if stdin_data.strip():
                hook_info = json.loads(stdin_data)
    except Exception:
        pass

    main(hook_info)
