#!/usr/bin/env python3
"""
YouRA Auto-Responder (LLM-Driven, Independent Artifact Verifier)

Features:
- LLM-based MUST_STOP detection (analyzes full context, not just patterns)
- LLM-generated Resume Prompt for pipeline continuation
- Continues in SAME session (no new terminal needed)
- Critical keyword pre-scan to skip unsafe pattern matching
- Rate limiting: auto-disable after 3 triggers in 60 seconds
- Configurable via YAML config file
- Artifact verification through filesystem-level checks for hypothesis outputs
  to detect fabricated or simulated results when code files are missing

Flow:
1. Load config from YAML
2. Check rate limit (auto-disable if triggered too often)
3. Read transcript and extract conversation context
4. Pre-scan for critical keywords
5. If no critical keywords AND pattern match → quick response (skip LLM)
6. Otherwise → LLM analyzes context for MUST_STOP detection
7. LLM naturally discovers and analyzes state files
8. LLM decides MUST_STOP → disable hook, allow stop
9. LLM decides CONTINUE → block stop, send resume prompt

Author: Anonymous
"""

import json
import os
import sys
import re
import glob
import subprocess
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

# ============================================================
# Path Configuration (Local .cache folder for portability)
# ============================================================
SCRIPT_DIR = Path(__file__).parent

# Config file stays in SCRIPT_DIR (read-only is OK)
CONFIG_FILE = SCRIPT_DIR / "auto_responder_config.yaml"
DISABLE_HOOK_SCRIPT = SCRIPT_DIR / "disable_hook.py"


def get_state_dir() -> Path:
    """
    Get writable state directory in .cache folder under SCRIPT_DIR.

    This keeps all state files local to the project, avoiding
    platform-specific XDG/AppData paths.

    Location: .claude/hooks/.cache/
    """
    state_dir = SCRIPT_DIR / ".cache"

    # Create if doesn't exist
    try:
        state_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        # Fallback to temp directory if somehow not writable
        import tempfile
        state_dir = Path(tempfile.gettempdir()) / "youra-auto-responder"
        state_dir.mkdir(parents=True, exist_ok=True)

    return state_dir


# State files go to .cache folder under SCRIPT_DIR
STATE_DIR = get_state_dir()
STATE_FILE = STATE_DIR / "auto_responder_state.json"
TRIGGER_HISTORY_FILE = STATE_DIR / "hook_trigger_history.json"

# Rate limiting settings
MAX_TRIGGERS = 4
TIME_WINDOW_SECONDS = 180


# ============================================================
# Logging
# ============================================================
class Logger:
    def __init__(self, log_file: Path, verbose: bool = True):
        self.log_file = log_file
        self.verbose = verbose

    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
            if self.verbose:
                print(log_entry, file=sys.stderr)
        except Exception:
            pass

    def info(self, message: str):
        self.log(message, "INFO")

    def error(self, message: str):
        self.log(message, "ERROR")

    def debug(self, message: str):
        self.log(message, "DEBUG")


# Global logger (initialized in main)
logger: Optional[Logger] = None


def log(message: str):
    """Backward compatible log function"""
    if logger:
        logger.info(message)
    else:
        print(f"[LOG] {message}", file=sys.stderr)


def output_decision(decision: str, reason: str = None) -> None:
    """
    Output JSON decision to stdout (required by Claude hook system).
    MUST be called on ALL exit paths for Linux compatibility.

    Args:
        decision: "approve" (allow stop) or "block" (prevent stop)
        reason: Optional reason string
    """
    output = {"decision": decision}
    if reason:
        output["reason"] = reason
    print(json.dumps(output))


# ============================================================
# Configuration Loading
# ============================================================
def load_config() -> Optional[Dict[str, Any]]:
    """Load and validate configuration from YAML file."""
    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
        return None

    if not CONFIG_FILE.exists():
        print(f"ERROR: Config file not found: {CONFIG_FILE}", file=sys.stderr)
        return None

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        if config is None:
            print("ERROR: Config file is empty", file=sys.stderr)
            return None

        # Validate required top-level sections
        required_sections = ["enabled", "openrouter", "context", "youra", "loop_prevention"]
        missing = [s for s in required_sections if s not in config]
        if missing:
            print(f"ERROR: Missing config sections: {missing}", file=sys.stderr)
            return None

        return config

    except Exception as e:
        print(f"ERROR: Failed to load config: {e}", file=sys.stderr)
        return None


# ============================================================
# State Management
# ============================================================
def load_state() -> Dict[str, Any]:
    """Load state including retry count."""
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
                now = datetime.now().timestamp()
                last_update = state.get("last_update", 0)
                time_window = state.get("time_window", 300)

                if now - last_update > time_window:
                    return {"retry_count": 0, "last_update": now, "time_window": time_window}
                return state
    except Exception:
        pass
    return {"retry_count": 0, "last_update": datetime.now().timestamp(), "time_window": 300}


def save_state(state: Dict[str, Any]):
    """Save state to file."""
    try:
        state["last_update"] = datetime.now().timestamp()
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f)
    except Exception as e:
        log(f"Failed to save state: {e}")


def reset_retry_count(time_window: int = 300):
    """Reset retry count to 0."""
    state = {"retry_count": 0, "last_update": datetime.now().timestamp(), "time_window": time_window}
    save_state(state)
    log("Retry count reset to 0")


def increment_retry_count(time_window: int = 300) -> int:
    """Increment and return new retry count."""
    state = load_state()
    state["retry_count"] = state.get("retry_count", 0) + 1
    state["time_window"] = time_window
    save_state(state)
    log(f"Retry count incremented to {state['retry_count']}")
    return state["retry_count"]


# ============================================================
# Rate Limiting (Auto-disable after N triggers in M seconds)
# ============================================================
def check_and_update_trigger_history() -> bool:
    """
    Check if hook has been triggered too many times within the time window.
    Returns True if rate limit exceeded (should disable), False otherwise.
    """
    import time

    current_time = time.time()
    history = []

    # Load existing history
    if TRIGGER_HISTORY_FILE.exists():
        try:
            with open(TRIGGER_HISTORY_FILE, 'r') as f:
                history = json.load(f)
        except Exception:
            history = []

    # Filter to keep only recent triggers within time window
    history = [t for t in history if current_time - t < TIME_WINDOW_SECONDS]

    # Add current trigger
    history.append(current_time)

    # Save updated history
    try:
        with open(TRIGGER_HISTORY_FILE, 'w') as f:
            json.dump(history, f)
    except Exception as e:
        log(f"Failed to save trigger history: {e}")

    # Check if rate limit exceeded
    if len(history) >= MAX_TRIGGERS:
        log(f"Rate limit exceeded: {len(history)} triggers in {TIME_WINDOW_SECONDS}s")
        return True

    log(f"Trigger count: {len(history)}/{MAX_TRIGGERS} in last {TIME_WINDOW_SECONDS}s")
    return False


def disable_hook_in_config():
    """
    Disable the hook by setting enabled: false in config.
    Uses YAML library for robust parsing (handles whitespace, case, comments).
    Falls back to regex-based approach if YAML fails.
    """
    try:
        import yaml
    except ImportError:
        log("PyYAML not available, using fallback method")
        return _disable_hook_fallback()

    try:
        # Method 1: Use YAML library (preserves comments with ruamel.yaml, basic with PyYAML)
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        if config and config.get('enabled', False):
            config['enabled'] = False

            # Re-read original content for comment preservation
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # Use regex replacement to preserve formatting/comments
            # This handles: enabled: true, enabled:true, enabled: True, etc.
            import re
            pattern = r'^(\s*)enabled\s*:\s*(true|True|TRUE|yes|Yes|YES|on|On|ON)\s*$'
            new_content = re.sub(pattern, r'\1enabled: false', original_content, count=1, flags=re.MULTILINE)

            if new_content != original_content:
                with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                log("Auto-disabled hook in config (YAML + regex method)")
            else:
                log("Config already disabled or pattern not found")

        # Clear trigger history after disabling
        if TRIGGER_HISTORY_FILE.exists():
            TRIGGER_HISTORY_FILE.unlink()

        return True

    except Exception as e:
        log(f"YAML method failed: {e}, trying fallback")
        return _disable_hook_fallback()


def _disable_hook_fallback():
    """Fallback method using simple string replacement."""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            content = f.read()

        # More robust pattern matching
        import re
        pattern = r'^(\s*)enabled\s*:\s*(true|True|TRUE|yes|Yes|YES|on|On|ON)(\s*#.*)?$'
        new_content = re.sub(pattern, r'\1enabled: false\3', content, count=1, flags=re.MULTILINE)

        if new_content != content:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                f.write(new_content)
            log("Auto-disabled hook in config (fallback method)")

        # Clear trigger history
        if TRIGGER_HISTORY_FILE.exists():
            TRIGGER_HISTORY_FILE.unlink()

        return True
    except Exception as e:
        log(f"Failed to disable hook: {e}")
        return False


# ============================================================
# Disable Hook
# ============================================================
def call_disable_hook(reason: str) -> bool:
    """Call disable_hook.py script to disable the hook."""
    if not DISABLE_HOOK_SCRIPT.exists():
        log(f"ERROR: disable_hook.py not found: {DISABLE_HOOK_SCRIPT}")
        return False

    try:
        result = subprocess.run(
            [sys.executable, str(DISABLE_HOOK_SCRIPT), reason],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            log("disable_hook.py executed successfully")
            return True
        else:
            log(f"disable_hook.py failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        log("disable_hook.py timed out")
        return False
    except Exception as e:
        log(f"Failed to call disable_hook.py: {e}")
        return False


# ============================================================
# Transcript Reading
# ============================================================
def read_last_message_only(transcript_path: str) -> dict:
    """
    Read ONLY the last message from JSONL file (most recent conversation turn).

    This reads only the last line of the file, avoiding all historical context.
    Perfect for eliminating false positives from old error messages.

    Args:
        transcript_path: Path to the JSONL transcript file

    Returns:
        dict: Last message, or empty dict if error
    """
    try:
        # Read last 100KB from file (enough for any single message)
        with open(transcript_path, "rb") as f:
            f.seek(0, 2)  # Seek to end
            file_size = f.tell()

            # Read from end
            read_size = min(100000, file_size)
            f.seek(file_size - read_size)

            # Read lines and get the last one
            lines = f.readlines()
            if lines:
                last_line = lines[-1]
                return json.loads(last_line.strip())

    except Exception as e:
        log(f"Last message read error: {e}")

    return {}


def read_transcript(transcript_path: str, max_chars: int = 3000) -> list:
    """
    Read last few messages from JSONL file to find one with text content.

    Args:
        transcript_path: Path to the JSONL transcript file
        max_chars: Not used (kept for compatibility)

    Returns:
        list: Last 5 messages (to ensure we get one with text)
    """
    messages = []

    try:
        # Use collections.deque to get last 5 lines
        from collections import deque

        with open(transcript_path, 'rb') as f:
            # deque with maxlen=5 keeps last 5 lines
            last_lines = deque(f, maxlen=5)

            for line in last_lines:
                try:
                    data = json.loads(line.strip())
                    messages.append(data)
                except Exception:
                    continue

    except Exception as e:
        log(f"Transcript read error: {e}")

    return messages


def extract_conversation_text(messages: list, max_chars: int = 5000) -> str:
    """
    Extract text from recent messages (finds first message with text content).

    Args:
        messages: List of recent messages (last 5)
        max_chars: Maximum characters to extract (default: 5000)

    Returns:
        str: Extracted text from most recent message with text, or empty string
    """
    if not messages:
        return ""

    # Search backwards for a message with text content
    for msg in reversed(messages):
        msg_type = msg.get("type", "")
        text = ""

        if msg_type == "assistant":
            content = msg.get("message", {}).get("content", [])
            if isinstance(content, list):
                text = "".join(
                    item.get("text", "") for item in content
                    if isinstance(item, dict) and item.get("type") == "text"
                )
            else:
                text = str(content)
        elif msg_type == "user":
            content = msg.get("message", {}).get("content", "")
            if isinstance(content, list):
                text = "".join(
                    item.get("text", "") for item in content
                    if isinstance(item, dict) and item.get("type") == "text"
                )
            else:
                text = str(content)

        # If we found text, return it
        text = text.strip()
        if text:
            if len(text) > max_chars:
                text = text[:max_chars]
            return text

    return ""


def extract_last_line(messages: list) -> str:
    """Extract last line from most recent message with text."""
    if not messages:
        return ""

    # Search backwards for a message with text content
    for msg in reversed(messages):
        if msg.get("type") == "assistant":
            content = msg.get("message", {}).get("content", [])
            if isinstance(content, list):
                for item in content:
                    if item.get("type") == "text":
                        text = item.get("text", "").strip()
                        if text:
                            lines = text.split('\n')
                            return lines[-1] if lines else ""
            elif isinstance(content, str):
                lines = content.strip().split('\n')
                return lines[-1] if lines else ""

    return ""


def save_conversation_log(conversation_text: str, log_file: Path):
    """Save conversation to log file for debugging."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"=== Conversation Log ({timestamp}) ===\n\n")
            f.write(conversation_text)
            f.write("\n\n=== End of Log ===\n")
    except Exception as e:
        log(f"Failed to save conversation log: {e}")


# ============================================================
# Critical Keyword Detection
# ============================================================
def has_critical_keywords(text: str, keywords: list) -> Tuple[bool, str]:
    """Check if text contains any critical keywords."""
    text_lower = text.lower()
    for keyword in keywords:
        if keyword.lower() in text_lower:
            log(f"Critical keyword detected: '{keyword}'")
            return True, keyword
    return False, ""


# ============================================================
# Pattern Matching
# ============================================================
def match_pattern(last_line: str, patterns: list) -> bool:
    """Check if last line matches any pattern."""
    last_line_lower = last_line.lower()
    for pattern in patterns:
        pattern_str = pattern if isinstance(pattern, str) else str(pattern)
        if pattern_str.lower() in last_line_lower:
            log(f"Pattern matched: '{pattern_str}'")
            return True
    return False


# ============================================================
# Anonymous Pipeline State Detection
# ============================================================
def find_research_folder(project_dir: str, pattern: str) -> Optional[str]:
    """Find the most recent research folder by modification time."""
    full_pattern = os.path.join(project_dir, pattern)
    folders = glob.glob(full_pattern)
    if folders:
        latest = max(folders, key=os.path.getmtime)
        return latest.rstrip("/").rstrip("\\")
    return None


def find_state_files(research_folder: str, config: Dict[str, Any]) -> Dict[str, Optional[str]]:
    """
    Find core state files for pipeline status detection.

    Finds verification_state.yaml and the latest hypothesis checkpoint.
    Also scans all hypothesis checkpoints for Gate FAIL/ROUTED status.
    Conditionally includes 05_baseline_checkpoint.yaml when Phase 5 is active
    (skip_baseline_comparison=false or baseline_comparison.status != SKIPPED).
    """
    youra_config = config.get("youra", {})
    files = {
        "verification_state": None,
        "checkpoint": None,              # Latest hypothesis checkpoint (Phase 4)
        "fail_checkpoint": None,         # Gate FAIL hypothesis checkpoint (if different)
        "baseline_checkpoint": None,     # Phase 5 baseline checkpoint (conditional)
        "hypothesis_folder": None
    }

    if not research_folder:
        return files

    # verification_state.yaml (root level)
    state_file = youra_config.get("state_file", "verification_state.yaml")
    state_path = os.path.join(research_folder, state_file)
    if os.path.exists(state_path):
        files["verification_state"] = state_path

    # Find all hypothesis folders
    h_pattern = youra_config.get("hypothesis_folder_pattern", "h-*/")
    h_folders = glob.glob(os.path.join(research_folder, h_pattern))
    checkpoint_file = youra_config.get("checkpoint_file", "04_checkpoint.yaml")

    if h_folders:
        # Latest hypothesis folder (by modification time)
        latest_h = max(h_folders, key=os.path.getmtime)
        files["hypothesis_folder"] = latest_h.rstrip("/").rstrip("\\")

        # 04_checkpoint.yaml from latest hypothesis
        checkpoint_path = os.path.join(latest_h, checkpoint_file)
        if os.path.exists(checkpoint_path):
            files["checkpoint"] = checkpoint_path

        # Scan all hypothesis checkpoints for Gate FAIL
        for h_folder in h_folders:
            cp_path = os.path.join(h_folder, checkpoint_file)
            if not os.path.exists(cp_path) or cp_path == files["checkpoint"]:
                continue
            try:
                import yaml
                with open(cp_path, 'r', encoding='utf-8') as f:
                    cp_data = yaml.safe_load(f)
                if isinstance(cp_data, dict):
                    # Actual schema: gate_result: {decision: "PASS"|"FAIL"|...}
                    gr = cp_data.get("gate_result", {})
                    decision = gr.get("decision", "") if isinstance(gr, dict) else ""
                    if decision == "FAIL":
                        files["fail_checkpoint"] = cp_path
                        log(f"Found Gate FAIL checkpoint: {cp_path}")
                        break  # One FAIL checkpoint is enough
            except Exception as e:
                log(f"WARNING: Could not scan {cp_path}: {e}")

    # Phase 5 baseline checkpoint (conditional — only when Phase 5 is active)
    if files["verification_state"]:
        try:
            import yaml
            with open(files["verification_state"], 'r', encoding='utf-8') as f:
                vs_data = yaml.safe_load(f)
            if isinstance(vs_data, dict):
                # Actual schema: phase5_plan: {enabled: true/false}
                p5 = vs_data.get("phase5_plan", {})
                p5_enabled = p5.get("enabled", False) if isinstance(p5, dict) else False
                if p5_enabled:
                    # Phase 5 is active — find baseline checkpoint
                    for h_folder in (h_folders or []):
                        bc_path = os.path.join(h_folder, "baseline_comparison", "05_baseline_checkpoint.yaml")
                        if os.path.exists(bc_path):
                            files["baseline_checkpoint"] = bc_path
                            log(f"Phase 5 active, loaded baseline checkpoint: {bc_path}")
                            break
                else:
                    log(f"Phase 5 skipped (phase5_plan.enabled={p5_enabled}), baseline checkpoint not loaded")
        except Exception as e:
            log(f"WARNING: Could not check Phase 5 status: {e}")

    return files


def verify_hypothesis_artifacts(research_folder: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verify that hypothesis folders contain actual implementation artifacts.

    Filesystem-level verification to detect fabricated/simulated results.
    Checks each h-*/ folder for required files that prove actual execution occurred.

    Required artifacts per completed hypothesis:
    - 02c_experiment_brief.md (Phase 2C output)
    - 03_tasks.yaml (Phase 3 output)
    - 04_checkpoint.yaml (Phase 4 tracking)
    - 04_validation.md (Phase 4 validation report)
    - At least one .py file (actual code was written)

    Returns:
        Dict with verification results:
        - verified: bool (all checks passed)
        - total_hypotheses: int
        - verified_count: int
        - missing_artifacts: dict per hypothesis
        - state_claims_complete: bool (what verification_state.yaml says)
        - fabrication_detected: bool (state says complete but artifacts missing)
    """
    if not research_folder or not os.path.isdir(research_folder):
        return {"verified": False, "error": "No research folder", "fabrication_detected": False}

    youra_config = config.get("youra", {})
    artifact_config = config.get("artifact_verification", {})

    # Required files per hypothesis (configurable)
    required_files = artifact_config.get("required_files", [
        "02c_experiment_brief.md",
        "03_tasks.yaml",
        "04_checkpoint.yaml",
        "04_validation.md",
    ])
    require_code_files = artifact_config.get("require_code_files", True)
    code_extensions = artifact_config.get("code_extensions", [".py", ".ipynb"])

    # Find hypothesis folders
    h_pattern = youra_config.get("hypothesis_folder_pattern", "h-*/")
    h_folders = glob.glob(os.path.join(research_folder, h_pattern))

    # Read verification_state.yaml to check claimed status
    state_claims_complete = False
    claimed_completed_count = 0
    claimed_hypothesis_ids = []

    state_file = os.path.join(research_folder, youra_config.get("state_file", "verification_state.yaml"))
    if os.path.exists(state_file):
        try:
            import yaml
            with open(state_file, 'r', encoding='utf-8') as f:
                vs_data = yaml.safe_load(f)
            if isinstance(vs_data, dict):
                # Actual schema: pipeline.status, hypotheses[] list
                pipeline = vs_data.get("pipeline", {})
                state_claims_complete = pipeline.get("status") in (
                    "COMPLETED", "PAPER_GENERATED", "Pipeline Complete"
                )

                # Count claimed completed hypotheses from list
                hyps = vs_data.get("hypotheses", [])
                if isinstance(hyps, list) and hyps:
                    for h_data in hyps:
                        if isinstance(h_data, dict):
                            h_id = h_data.get("id", "")
                            if h_id:
                                claimed_hypothesis_ids.append(h_id)
                            if h_data.get("status") in ("PASS", "COMPLETED", "VALIDATED", "COMPLETE"):
                                claimed_completed_count += 1
        except Exception as e:
            log(f"WARNING: Could not parse verification_state.yaml for artifact check: {e}")

    # Verify each hypothesis folder
    results = {
        "verified": True,
        "total_hypotheses_claimed": claimed_completed_count,
        "total_hypothesis_folders": len(h_folders),
        "verified_count": 0,
        "missing_artifacts": {},
        "state_claims_complete": state_claims_complete,
        "fabrication_detected": False,
        "details": {},
    }

    if not h_folders and state_claims_complete and claimed_completed_count > 0:
        # State says hypotheses completed but NO hypothesis folders exist at all
        results["verified"] = False
        results["fabrication_detected"] = True
        results["missing_artifacts"]["ALL"] = {
            "error": f"State claims {claimed_completed_count} hypotheses completed but NO h-*/ folders found",
            "missing_files": ["entire h-*/ folder structure"],
            "has_code": False,
        }
        log(f"FABRICATION DETECTED: State claims {claimed_completed_count} completed but 0 h-*/ folders exist")
        return results

    for h_folder in sorted(h_folders):
        h_name = os.path.basename(h_folder.rstrip("/").rstrip("\\"))
        folder_detail = {
            "missing_files": [],
            "has_code": False,
            "code_files_found": [],
        }

        # Check required files
        for req_file in required_files:
            file_path = os.path.join(h_folder, req_file)
            if not os.path.exists(file_path):
                folder_detail["missing_files"].append(req_file)

        # Check for code files (recursively in hypothesis folder)
        if require_code_files:
            for ext in code_extensions:
                code_files = glob.glob(os.path.join(h_folder, "**", f"*{ext}"), recursive=True)
                if code_files:
                    folder_detail["has_code"] = True
                    folder_detail["code_files_found"].extend(
                        [os.path.relpath(f, h_folder) for f in code_files[:5]]  # Max 5 for brevity
                    )

        # Determine if this hypothesis has sufficient artifacts
        is_verified = len(folder_detail["missing_files"]) == 0
        if require_code_files and not folder_detail["has_code"]:
            is_verified = False

        if is_verified:
            results["verified_count"] += 1
        else:
            results["missing_artifacts"][h_name] = folder_detail

        results["details"][h_name] = folder_detail

    # Check for fabrication: state claims complete but artifacts missing
    if state_claims_complete and claimed_completed_count > 0:
        if results["verified_count"] == 0:
            results["fabrication_detected"] = True
            results["verified"] = False
            log(f"FABRICATION DETECTED: State claims {claimed_completed_count} hypotheses complete, "
                f"but {len(results['missing_artifacts'])} folders have missing artifacts and 0 verified")
        elif results["verified_count"] < claimed_completed_count:
            # Partial fabrication — some hypotheses missing artifacts
            results["verified"] = False
            if results["verified_count"] == 0:
                results["fabrication_detected"] = True
            log(f"PARTIAL ARTIFACT GAP: {results['verified_count']}/{claimed_completed_count} "
                f"hypotheses have complete artifacts")

    log(f"Artifact verification: verified={results['verified']}, "
        f"fabrication={results['fabrication_detected']}, "
        f"{results['verified_count']}/{len(h_folders)} folders complete")

    return results


def format_artifact_report(artifact_results: Dict[str, Any]) -> str:
    """Format artifact verification results for inclusion in LLM prompt."""
    if artifact_results.get("error"):
        return f"⚠ Artifact verification error: {artifact_results['error']}"

    # If the new verifier produced a full report, use it directly
    full_report = artifact_results.get("report", "")
    if full_report:
        return full_report

    # Legacy fallback format
    lines = []
    lines.append(f"State claims complete: {artifact_results.get('state_claims_complete', False)}")
    lines.append(f"Hypotheses claimed completed: {artifact_results.get('total_hypotheses_claimed', 0)}")
    lines.append(f"Hypothesis folders found: {artifact_results.get('total_hypothesis_folders', 0)}")
    lines.append(f"Fully verified (all artifacts present): {artifact_results.get('verified_count', 0)}")
    lines.append(f"Fabrication detected: {artifact_results.get('fabrication_detected', False)}")

    missing = artifact_results.get("missing_artifacts", {})
    if missing:
        lines.append(f"\nMissing artifacts in {len(missing)} hypothesis folder(s):")
        for h_name, detail in missing.items():
            if isinstance(detail, dict):
                missing_files = detail.get("missing_files", [])
                has_code = detail.get("has_code", False)
                lines.append(f"  {h_name}:")
                if missing_files:
                    lines.append(f"    Missing files: {', '.join(missing_files)}")
                if not has_code:
                    lines.append(f"    Missing code: No .py or .ipynb files found")
            elif isinstance(detail, list):
                lines.append(f"  {h_name}:")
                for item in detail[:10]:
                    lines.append(f"    - {item}")
            else:
                lines.append(f"  {h_name}: {detail}")

    return "\n".join(lines)


def read_file_content(file_path: str) -> str:
    """Read full file content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"


def extract_resume_fields(file_path: str) -> str:
    """
    Extract only resume-critical fields from verification_state.yaml.

    Actual schema uses:
    - pipeline: status, current_phase, current_hypothesis, hypotheses_complete/total
    - hypotheses: list of {id, type, order, status, gate_result, dependencies}
    - gate_results: {H-ID: {decision, confidence, timestamp}}
    - main_hypothesis: {id, statement, gap_addressed}
    - phase5_plan: {enabled, note}
    """
    try:
        import yaml

        with open(file_path, 'r', encoding='utf-8') as f:
            state = yaml.safe_load(f)

        if not isinstance(state, dict):
            log("WARNING: verification_state.yaml parse returned non-dict, falling back to full read")
            return read_file_content(file_path)

        extracted = {}

        # 1. pipeline section (critical for resume decision)
        pipeline = state.get("pipeline", {})
        extracted["pipeline"] = {
            "status": pipeline.get("status"),
            "current_phase": pipeline.get("current_phase"),
            "current_hypothesis": pipeline.get("current_hypothesis"),
            "hypotheses_complete": pipeline.get("hypotheses_complete"),
            "hypotheses_total": pipeline.get("hypotheses_total"),
            "timestamp": pipeline.get("timestamp"),
        }

        # 2. hypotheses — id, status, gate_result, order, dependencies
        raw_hyps = state.get("hypotheses", [])
        extracted_hyps = []
        if isinstance(raw_hyps, list):
            for h in raw_hyps:
                if not isinstance(h, dict):
                    continue
                extracted_hyps.append({
                    "id": h.get("id"),
                    "type": h.get("type"),
                    "order": h.get("order"),
                    "status": h.get("status"),
                    "gate_result": h.get("gate_result"),
                    "dependencies": h.get("dependencies", []),
                })
        extracted["hypotheses"] = extracted_hyps

        # 3. gate_results — decision summary per hypothesis
        gate_results = state.get("gate_results", {})
        extracted_gates = {}
        for h_id, gr in gate_results.items():
            if isinstance(gr, dict):
                extracted_gates[h_id] = {
                    "decision": gr.get("decision"),
                    "confidence": gr.get("confidence"),
                }
            else:
                extracted_gates[h_id] = str(gr)
        extracted["gate_results"] = extracted_gates

        # 4. phase5_plan
        p5 = state.get("phase5_plan", {})
        if isinstance(p5, dict):
            extracted["phase5_plan"] = {
                "enabled": p5.get("enabled"),
                "note": p5.get("note"),
            }

        # 5. main_hypothesis — identity only
        main_h = state.get("main_hypothesis", {})
        if isinstance(main_h, dict):
            extracted["main_hypothesis"] = {
                "id": main_h.get("id"),
                "statement": main_h.get("statement"),
            }

        result = yaml.dump(extracted, default_flow_style=False, allow_unicode=True, sort_keys=False)
        log(f"Extracted resume fields: {len(result)} chars (full file: {os.path.getsize(file_path)} bytes)")
        return result

    except ImportError:
        log("WARNING: PyYAML not available, falling back to full read")
        return read_file_content(file_path)
    except Exception as e:
        log(f"WARNING: extract_resume_fields failed ({e}), falling back to full read")
        return read_file_content(file_path)


def extract_checkpoint_fields(file_path: str) -> str:
    """
    Extract only resume-critical fields from 04_checkpoint.yaml.

    Actual schema:
    - hypothesis_id, phase, status, started_at (flat top-level)
    - tasks: {H-ID-T1: {status, attempts, last_error}, ...}
    - metrics: {metric_name: value_or_null, ...}
    - gate_result: {decision, timestamp, justification}
    - retry_count, max_retries
    """
    try:
        import yaml

        with open(file_path, 'r', encoding='utf-8') as f:
            state = yaml.safe_load(f)

        if not isinstance(state, dict):
            log("WARNING: 04_checkpoint.yaml parse returned non-dict, falling back to full read")
            return read_file_content(file_path)

        extracted = {}

        # 1. Identity + status (flat top-level fields)
        extracted["hypothesis_id"] = state.get("hypothesis_id")
        extracted["phase"] = state.get("phase")
        extracted["status"] = state.get("status")
        extracted["started_at"] = state.get("started_at")

        # 2. Tasks — compute summary from flat dict
        tasks = state.get("tasks", {})
        if isinstance(tasks, dict):
            total = len(tasks)
            completed = sum(1 for t in tasks.values()
                           if isinstance(t, dict) and t.get("status") in ("completed", "complete"))
            pending = sum(1 for t in tasks.values()
                         if isinstance(t, dict) and t.get("status") == "pending")
            in_progress = sum(1 for t in tasks.values()
                              if isinstance(t, dict) and t.get("status") == "in_progress")
            extracted["tasks_summary"] = {
                "total": total,
                "completed": completed,
                "pending": pending,
                "in_progress": in_progress,
            }

        # 3. Metrics — include as-is (small dict)
        metrics = state.get("metrics", {})
        if isinstance(metrics, dict):
            extracted["metrics"] = metrics

        # 4. Gate result
        gate = state.get("gate_result", {})
        if isinstance(gate, dict):
            extracted["gate_result"] = {
                "decision": gate.get("decision"),
                "timestamp": gate.get("timestamp"),
                "justification": gate.get("justification"),
            }

        # 5. Retry tracking
        extracted["retry_count"] = state.get("retry_count")
        extracted["max_retries"] = state.get("max_retries")

        result = yaml.dump(extracted, default_flow_style=False, allow_unicode=True, sort_keys=False)
        log(f"Extracted checkpoint fields: {len(result)} chars (full file: {os.path.getsize(file_path)} bytes)")
        return result

    except ImportError:
        log("WARNING: PyYAML not available, falling back to full read")
        return read_file_content(file_path)
    except Exception as e:
        log(f"WARNING: extract_checkpoint_fields failed ({e}), falling back to full read")
        return read_file_content(file_path)


def extract_baseline_checkpoint_fields(file_path: str) -> str:
    """
    Extract only resume-critical fields from 05_baseline_checkpoint.yaml.

    Only called when Phase 5 is active (skip_baseline_comparison=false).
    Falls back to full file content on any parsing error.

    Fields extracted:
    - identity: hypothesis_id, status, current_step, gate_result
    - baseline_gate: result, baselines_won/lost, threshold_met
    - retry_tracking: retry_count, max_retries, return_to_phase0
    - failure_analysis: failure_type, baselines_lost_to
    """
    try:
        import yaml

        with open(file_path, 'r', encoding='utf-8') as f:
            state = yaml.safe_load(f)

        if not isinstance(state, dict):
            log("WARNING: 05_baseline_checkpoint.yaml parse returned non-dict, falling back to full read")
            return read_file_content(file_path)

        extracted = {}

        # 1. identity + status
        extracted["hypothesis_id"] = state.get("hypothesis_id")
        extracted["status"] = state.get("status")
        extracted["current_step"] = state.get("current_step")
        extracted["gate_result"] = state.get("gate_result")
        extracted["completed_at"] = state.get("completed_at")

        # 2. baseline_gate — DETERMINES_SUCCESS result
        bg = state.get("baseline_gate", {})
        extracted["baseline_gate"] = {
            "result": bg.get("result"),
            "baselines_won": bg.get("baselines_won"),
            "baselines_lost": bg.get("baselines_lost"),
            "threshold_met": bg.get("threshold_met"),
            "evaluated_at": bg.get("evaluated_at"),
        }

        # 3. retry_tracking
        rt = state.get("retry_tracking", {})
        extracted["retry_tracking"] = {
            "phase5_retry_count": rt.get("phase5_retry_count"),
            "max_phase5_retries": rt.get("max_phase5_retries"),
            "return_to_phase0": rt.get("return_to_phase0"),
        }

        # 4. failure_analysis — summary only
        fa = state.get("failure_analysis", {})
        extracted["failure_analysis"] = {
            "failure_type": fa.get("failure_type"),
            "baselines_lost_to": fa.get("baselines_lost_to", []),
        }

        result = yaml.dump(extracted, default_flow_style=False, allow_unicode=True, sort_keys=False)
        log(f"Extracted baseline checkpoint fields: {len(result)} chars (full file: {os.path.getsize(file_path)} bytes)")
        return result

    except ImportError:
        log("WARNING: PyYAML not available, falling back to full read")
        return read_file_content(file_path)
    except Exception as e:
        log(f"WARNING: extract_baseline_checkpoint_fields failed ({e}), falling back to full read")
        return read_file_content(file_path)


# ============================================================
# API Key Loading
# ============================================================
def load_api_key(project_dir: str, env_var_name: str) -> Optional[str]:
    """Load API key from environment or .env file."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        log("WARNING: python-dotenv not installed")
        return os.getenv(env_var_name)

    # Try loading .env from multiple locations
    env_paths = [
        Path(project_dir) / ".env",
        SCRIPT_DIR.parent.parent / ".env",
        SCRIPT_DIR.parent.parent.parent / ".env",
        Path.home() / ".env"
    ]

    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path, override=True)
            log(f"Loaded .env from {env_path}")
            break

    api_key = os.getenv(env_var_name)
    if api_key:
        log("API key loaded successfully")
    else:
        log(f"No {env_var_name} found in environment")
    return api_key


# ============================================================
# LLM Call - Combined MUST_STOP Detection and Resume Context Generation
# ============================================================
def analyze_and_generate_resume(
    conversation_text: str,
    research_folder: Optional[str],
    state_files: Dict[str, Optional[str]],
    config: Dict[str, Any],
    api_key: str,
    artifact_results: Optional[Dict[str, Any]] = None
) -> Tuple[bool, Optional[str]]:
    """
    Call LLM to:
    1. Determine if MUST_STOP (human intervention required)
    2. If CONTINUE, generate Resume Context for current session

    Returns:
        (is_must_stop, response)
        - is_must_stop=True: response contains DISABLE reason
        - is_must_stop=False: response contains Resume Context
    """
    openrouter = config.get("openrouter", {})
    context_config = config.get("context", {})

    # Read state file contents (core files only)
    # The LLM can naturally discover additional files from folder structure.
    file_contents = ""
    files_found = []

    if state_files.get("verification_state"):
        content = extract_resume_fields(state_files["verification_state"])
        file_contents += f"\n### verification_state.yaml (resume-critical fields only)\n```yaml\n{content}\n```\n"
        files_found.append("verification_state.yaml (extracted)")

    if state_files.get("checkpoint"):
        content = extract_checkpoint_fields(state_files["checkpoint"])
        file_contents += f"\n### 04_checkpoint.yaml — Latest Hypothesis (resume-critical fields only)\n```yaml\n{content}\n```\n"
        files_found.append("04_checkpoint.yaml (extracted)")

    if state_files.get("fail_checkpoint"):
        content = extract_checkpoint_fields(state_files["fail_checkpoint"])
        file_contents += f"\n### 04_checkpoint.yaml — Gate FAIL Hypothesis (resume-critical fields only)\n**⚠ This hypothesis has a Gate FAIL — routing action required.**\n```yaml\n{content}\n```\n"
        files_found.append("04_checkpoint.yaml FAIL (extracted)")

    if state_files.get("baseline_checkpoint"):
        content = extract_baseline_checkpoint_fields(state_files["baseline_checkpoint"])
        file_contents += f"\n### 05_baseline_checkpoint.yaml — Phase 5 Baseline Comparison (resume-critical fields only)\n```yaml\n{content}\n```\n"
        files_found.append("05_baseline_checkpoint.yaml (extracted)")

    # Add hypothesis folder info
    if state_files.get("hypothesis_folder"):
        file_contents += f"\n### Current Hypothesis Folder\n`{state_files['hypothesis_folder']}`\n"

    log(f"State files loaded: {files_found}")

    # Artifact verification report
    artifact_report = ""
    if artifact_results:
        artifact_report = format_artifact_report(artifact_results)
        log(f"Artifact report included: fabrication={artifact_results.get('fabrication_detected', False)}")

    # Read resume reference file (hook-specific summary)
    workflow_instructions = ""
    resume_ref_path = SCRIPT_DIR / "resume_reference.md"
    if resume_ref_path.exists():
        workflow_instructions = read_file_content(str(resume_ref_path))
        log(f"Loaded resume reference: {len(workflow_instructions)} chars")

    focus_chars = context_config.get("focus_chars", 2000)

    prompt = f"""You are the Anonymous Pipeline Auto-Responder. You have TWO tasks:

## TASK 1: Determine if MUST_STOP (Human Intervention Required)

**CRITICAL: Default to CONTINUE. ALWAYS CONTINUE unless there is a FATAL, UNRECOVERABLE error.**
**EXCEPTION: FABRICATED RESULTS require FORCE_REEXECUTE (see condition #6 below).**

### MUST_STOP Conditions (these 5 scenarios require DISABLE):
1. **API Key FAILURE** - Authentication completely failed (not just warnings)
2. **Manual Download REQUIRED** - Data that CANNOT be fetched programmatically
3. **Access DENIED** - Permission errors blocking the entire pipeline
4. **FATAL Crash** - Unrecoverable system state, segfault, kernel panic
5. **Hardware FAILURE** - GPU unavailable, OOM that cannot be resolved

### FORCE_REEXECUTE Condition (requires CONTINUE with re-execution instructions):
6. **FABRICATED RESULTS** - State files claim hypotheses are completed but the Artifact Verification
   Report shows missing artifacts (no code files, no validation reports, no checkpoint files).
   This means the pipeline SKIPPED actual experiment execution and generated fake results.
   **Action: CONTINUE but instruct Claude to DISCARD fabricated state and RE-EXECUTE the
   hypothesis loop from Phase 2C for ALL incomplete hypotheses.**

**UNATTENDED MODE PRINCIPLE:**
This is FULLY AUTOMATED execution. The user has explicitly requested NO human intervention.
Your job is to keep the pipeline running, NOT to ask for permission.
**When in doubt: CONTINUE. Only DISABLE for truly FATAL, UNRECOVERABLE errors.**

**IMPORTANT: Artifact Verification Override**
When the Artifact Verification Report shows `Fabrication detected: True`:
- This is a CONTINUE (not DISABLE) — but with FORCE re-execution
- The report includes a "RE-EXECUTION PLAN (per hypothesis)" section — follow it exactly
- The resume prompt MUST instruct Claude to:
  1. Reset verification_state.yaml: set pipeline.status back to "ACTIVE", all failed hypothesis statuses to "READY"
  2. Delete any fabricated 045_validated_hypothesis.md, paper/ outputs
  3. Re-execute EACH failed hypothesis starting from its specific resume point (see RE-EXECUTION PLAN)
     - Some hypotheses may restart from Phase 2C, others from Phase 3 or Phase 4
     - DO NOT restart ALL hypotheses from Phase 2C if some have valid Phase 2C/3 artifacts
  4. When Phase 4 code generation is needed and Phase 3 artifacts EXIST (03_architecture.md, 03_logic.md, 03_config.md):
     - MUST read and follow the Phase 3 docs as the implementation specification
     - Generate actual executable .py code based on these specs
     - Run the code and capture experiment_results.json
  5. When Phase 3 artifacts are MISSING: run Phase 3 first to produce them, THEN Phase 4
  6. Each hypothesis MUST produce: executable code (.py), experiment_results.json, valid gate_result (PASS/PARTIAL/FAIL only)

**IMPORTANT: Gate FAIL / ROUTED Status Handling**
When state files show gate_result.decision="FAIL" or pipeline.status="ROUTED":
- This is STILL a CONTINUE (not DISABLE) — the pipeline handles routing itself
- But the resume prompt MUST instruct Claude to execute the **routing procedure**:
  1. Archive current files (see "MANDATORY: Archive Execution on Routing" in Resume Reference)
  2. Route to the target phase (Phase 0 or Phase 2A-Dialogue)
- Do NOT instruct Claude to "retry the current task" or "reinterpret the metric"
- Do NOT treat a Gate FAIL as a recoverable error within the same hypothesis

## TASK 2: Generate Resume Prompt

If the pipeline can continue, generate a complete resume prompt. While generating:

**Naturally analyze the situation:**
- Read the conversation to understand what actually happened
- Check the state files to see the last saved state
- If you notice any gaps between actual progress (from conversation) and saved state (from files),
  mention them naturally in the resume prompt so Claude can update them
- If Archon tasks should be updated based on progress, include that reminder naturally

**Keep it flexible - don't follow a rigid checklist.** Just understand the situation and communicate
clearly what needs to happen next.

---

## Recent Conversation (Last {len(conversation_text)} chars) - PRIMARY SOURCE
**Read this FIRST to understand the current situation.**
```
{conversation_text}
```

## State Files (Core files - Claude can discover additional files naturally)
**Note:** These files reflect the last SAVED state. The actual progress may be ahead.
If conversation shows more recent progress, PRIORITIZE the conversation over these files.
**IMPORTANT:** NEVER search in `_archive/` folder. Archive folders contain old/failed research attempts
and should be IGNORED when determining current pipeline state.
{file_contents if file_contents else "No state files found."}

## Artifact Verification Report (FILESYSTEM CHECK — OVERRIDES STATE FILES)
**This is a HARD CHECK of what actually exists on disk, independent of what state files claim.**
**If this report shows fabrication, the state files are LYING — trust THIS report.**
```
{artifact_report if artifact_report else "Artifact verification not performed."}
```

## Resume Reference (AUTHORITATIVE SOURCE for Step/Phase Mapping, Resume Detection, Prompt Template)
**Use this reference for:**
- Step ↔ Phase Mapping (which Step to resume)
- Resume Detection Logic (how to determine current phase from state files)
- Resume Prompt Template (exact format to generate)
- Gate System (MUST_WORK / DETERMINES_SUCCESS gate handling)
- Archive Execution on Routing (if workflow.status = "ROUTED")

{workflow_instructions}

## Research Folder
{research_folder or "Not detected"}

---

## YOUR RESPONSE FORMAT

**If MUST_STOP (human intervention required):**
```
DISABLE: <Brief explanation of why human intervention is needed>
```

**If CONTINUE (can auto-resume):**
Generate a resume prompt following the **Resume Prompt Template** in Resume Reference above.

**Key requirements for Resume Prompt:**

1. **Workflow Reference**
```
Read and follow: bmad-custom-src/custom/modules/youra-research/workflows/full-pipeline-unattended/instructions.md
```

2. **Context & Progress** - Clearly state:
   - Current phase and hypothesis
   - What was just completed (from conversation)
   - What needs to happen next

3. **State Synchronization** (if needed) - If you noticed any gaps:
   - Mention naturally what files or Archon tasks should be updated
   - Don't be overly prescriptive - just note what seems out of sync
   - Example: "Note: The conversation shows Phase 3 completed, but verification_state.yaml
     may need updating. Also verify Archon task status reflects current progress."

4. **Resume Instructions** - Must be DIRECT and ACTIONABLE
   - **NEVER** include "Should I proceed?" or "Is this okay?"
   - **ALWAYS** include "Execute immediately without confirmation"
   - If experiments pending → "RUN THEM NOW"
   - If code ready → "EXECUTE IT NOW"

---

Now analyze and respond:
"""

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "X-Title": "YouRA Auto Responder"
            },
            json={
                "model": openrouter.get("model", "anthropic/claude-3.5-sonnet"),
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": openrouter.get("max_tokens", 2000)
            },
            timeout=openrouter.get("timeout_seconds", 180)
        )

        if response.status_code == 200:
            result = response.json()
            llm_response = result.get("choices", [{}])[0].get("message", {}).get("content", "")

            # Check if response starts with DISABLE:
            is_must_stop = llm_response.strip().upper().startswith("DISABLE:")

            log(f"LLM response: MUST_STOP={is_must_stop}, length={len(llm_response)}")

            # Log full LLM response if debug setting enabled
            debug_config = config.get("debug", {})
            if debug_config.get("log_llm_interactions", False):
                log("=" * 60)
                log("LLM FULL RESPONSE:")
                log(llm_response)
                log("=" * 60)

            return is_must_stop, llm_response
        else:
            log(f"LLM API error: {response.status_code} - {response.text[:200]}")
            return False, None

    except requests.exceptions.Timeout:
        log("LLM API timeout")
        return False, None
    except Exception as e:
        log(f"LLM API call failed: {e}")
        return False, None


# ============================================================
# Main
# ============================================================
def main(hook_info: Dict[str, Any] = None):
    global logger

    # ========================================
    # Step 0: Load Config
    # ========================================
    config = load_config()
    if config is None:
        print('{"decision": "approve"}')  # Allow stop if config fails
        return

    # Initialize logger (use STATE_DIR for writable log file)
    debug_config = config.get("debug", {})
    log_file = STATE_DIR / debug_config.get("log_file", "auto_responder.log")
    logger = Logger(log_file, debug_config.get("verbose", True))

    log("=" * 60)
    log("YouRA Auto-Responder (LLM-Driven, Independent Artifact Verifier) - Triggered")

    # Check if enabled
    if not config.get("enabled", False):
        log("Hook DISABLED in config - allowing stop")
        output_decision("approve", "Hook disabled in config")
        return

    # ========================================
    # Step 0.5: Rate Limit Check
    # ========================================
    if check_and_update_trigger_history():
        log("Rate limit exceeded - auto-disabling hook")
        disable_hook_in_config()
        output = {"decision": "approve", "reason": "[AUTO-DISABLED] Too many triggers in short time. Hook disabled."}
        print(json.dumps(output))
        log("=" * 60)
        return

    # ========================================
    # Step 1: Read Hook Info
    # ========================================
    if hook_info is None:
        hook_info = {}
        try:
            if not sys.stdin.isatty():
                stdin_data = sys.stdin.read()
                if stdin_data:
                    hook_info = json.loads(stdin_data)
        except Exception as e:
            log(f"STDIN parse error: {e}")

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    transcript_path = hook_info.get("transcript_path", "")

    if not project_dir:
        log("No project dir - allowing stop")
        output_decision("approve", "No project directory detected")
        return

    # ========================================
    # Step 2: Read Transcript (Last Message Only)
    # ========================================
    messages = []
    conversation_text = ""
    last_line = ""

    if transcript_path and Path(transcript_path).exists():
        messages = read_transcript(transcript_path)
        conversation_text = extract_conversation_text(messages, max_chars=5000)
        last_line = extract_last_line(messages)

        # Save conversation log (use STATE_DIR for writable location)
        output_config = config.get("output", {})
        conv_log_file = STATE_DIR / output_config.get("conversation_log_file", "conversation_log.txt")
        save_conversation_log(conversation_text, conv_log_file)

        log(f"Transcript loaded: {len(conversation_text)} chars, last_line: {last_line[:50]}...")

    # ========================================
    # Step 3: Pre-scan for Critical Keywords
    # ========================================
    critical_keywords = config.get("critical_keywords", [])
    has_critical, matched_keyword = has_critical_keywords(conversation_text, critical_keywords)

    if has_critical:
        log(f"Critical keyword '{matched_keyword}' found - skipping pattern matching")

    # ========================================
    # Step 4: Quick Pattern Matching (if no critical keywords)
    # ========================================
    quick_patterns = config.get("quick_patterns", {})

    if not has_critical and quick_patterns.get("enabled", True) and last_line:
        patterns = quick_patterns.get("patterns", [])

        if match_pattern(last_line, patterns):
            # Safe pattern match - quick response without LLM
            loop_config = config.get("loop_prevention", {})
            reset_retry_count(loop_config.get("time_window_seconds", 300))

            default_response = quick_patterns.get("default_response", "Y")
            output_config = config.get("output", {})
            reason_template = output_config.get("reason_template", "[AUTO-RESPONDER] {response}")
            reason = reason_template.format(response=f"Pattern matched (safe). Response: {default_response}")

            output = {"decision": "block", "reason": reason}
            print(json.dumps(output))
            log(f"Quick pattern match - returning: {default_response}")
            log("=" * 60)
            return

    # ========================================
    # Step 5: Check Retry Count
    # ========================================
    loop_config = config.get("loop_prevention", {})
    time_window = loop_config.get("time_window_seconds", 300)
    max_retries = loop_config.get("max_retries", 3)

    state = load_state()
    current_retry = state.get("retry_count", 0)

    if current_retry >= max_retries:
        log(f"Max retries reached ({current_retry}/{max_retries}) - disabling hook")
        call_disable_hook(f"Max API retries reached ({current_retry} failures)")
        reset_retry_count(time_window)
        output_decision("approve", f"[AUTO-DISABLED] Max retries reached ({current_retry}/{max_retries})")
        return

    # ========================================
    # Step 6: Load API Key
    # ========================================
    openrouter = config.get("openrouter", {})

    if not openrouter.get("enabled", True):
        log("OpenRouter disabled - allowing stop (safe fallback)")
        output_decision("approve", "[AUTO-RESPONDER] LLM disabled, allowing stop")
        return

    api_key_env = openrouter.get("api_key_env", "OPENROUTER_API_KEY")
    api_key = load_api_key(project_dir, api_key_env)

    if not api_key:
        log("No API key - disabling hook")
        call_disable_hook("No OpenRouter API key found")
        output_decision("approve", "[AUTO-DISABLED] No API key found")
        return

    # ========================================
    # Step 7: Find YouRA State Files
    # ========================================
    youra_config = config.get("youra", {})
    research_folder = find_research_folder(
        project_dir,
        youra_config.get("research_folder_pattern", "docs/youra_research/*/")
    )
    state_files = find_state_files(research_folder, config)

    log(f"Research folder: {research_folder}")
    log(f"State files: {state_files}")

    # ========================================
    # Step 7.5: Verify Hypothesis Artifacts (Independent Verifier)
    # ========================================
    artifact_results = None
    artifact_config = config.get("artifact_verification", {})
    if artifact_config.get("enabled", True) and research_folder:
        try:
            from pipeline_artifact_verifier import PipelineArtifactVerifier
            verifier = PipelineArtifactVerifier(research_folder, artifact_config)
            artifact_results = verifier.verify()
            log(f"Independent verifier: passed={artifact_results.get('passed')}, "
                f"fabrication={artifact_results.get('fabrication_detected')}, "
                f"checked={artifact_results.get('hypotheses_checked')}, "
                f"invalid_gates={artifact_results.get('invalid_gates', [])}")
        except ImportError:
            log("WARNING: pipeline_artifact_verifier.py not found, falling back to legacy")
            artifact_results = verify_hypothesis_artifacts(research_folder, config)
        except Exception as e:
            log(f"WARNING: Independent verifier failed ({e}), falling back to legacy")
            artifact_results = verify_hypothesis_artifacts(research_folder, config)

        if artifact_results.get("fabrication_detected"):
            log(f"⚠ FABRICATION DETECTED — artifact verification failed")
            log(f"  Claimed completed: {artifact_results.get('total_hypotheses_claimed', 0)}")
            log(f"  Actually verified: {artifact_results.get('verified_count', 0)}")
            log(f"  Missing: {list(artifact_results.get('missing_artifacts', {}).keys())}")
            log(f"  Invalid gates: {artifact_results.get('invalid_gates', [])}")
    else:
        log("Artifact verification skipped (disabled or no research folder)")

    # ========================================
    # Step 8: Call LLM for Analysis and Resume Generation
    # ========================================
    is_must_stop, llm_response = analyze_and_generate_resume(
        conversation_text=conversation_text,
        research_folder=research_folder,
        state_files=state_files,
        config=config,
        api_key=api_key,
        artifact_results=artifact_results
    )

    if llm_response is None:
        # LLM API failed
        new_retry = increment_retry_count(time_window)
        log(f"LLM API failed - retry count: {new_retry}/{max_retries}")

        output_config = config.get("output", {})
        reason_template = output_config.get("reason_template", "[AUTO-RESPONDER] {response}")
        reason = reason_template.format(response=f"LLM API failed, retrying ({new_retry}/{max_retries})")

        output = {"decision": "block", "reason": reason}
        print(json.dumps(output))
        log("=" * 60)
        return

    # Reset retry count on successful API call
    reset_retry_count(time_window)

    # ========================================
    # Step 9: Handle LLM Decision
    # ========================================
    if is_must_stop:
        # MUST_STOP → Disable hook, allow stop
        log(f"LLM decided: MUST_STOP")
        log(f"Reason: {llm_response[:200]}...")
        call_disable_hook(llm_response[:500])
        log("Hook disabled - allowing stop for human intervention")
        log("=" * 60)
        output_decision("approve", f"[MUST_STOP] {llm_response[:200]}")
        return
    else:
        # CONTINUE → Block stop and send resume prompt to current session
        log("LLM decided: CONTINUE")
        log("Blocking stop and sending resume prompt to current session")

        # Simply block the stop and send resume prompt as reason
        # Claude will continue in the SAME session with this prompt
        output_config = config.get("output", {})
        reason_template = output_config.get("reason_template", "[AUTO-RESPONDER] {response}")
        reason = reason_template.format(response=llm_response)

        output = {"decision": "block", "reason": reason}
        print(json.dumps(output))
        log("Resume prompt sent - Claude continues in current session")

        log("=" * 60)
        return


if __name__ == "__main__":
    main()
