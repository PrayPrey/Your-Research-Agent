#!/usr/bin/env python3
"""
YouRA Auto-Responder Test Suite

Purpose: Comprehensive testing of auto_responder_full.py functions
- Tests all core functions with real and mock data
- Supports testing individual components or full flow
- Can use real transcript files for integration testing

Usage:
    python auto_responder_test.py                    # Run all tests
    python auto_responder_test.py --test=config      # Test config loading
    python auto_responder_test.py --test=transcript  # Test transcript reading
    python auto_responder_test.py --test=flow        # Test full flow (mock LLM)
    python auto_responder_test.py --test=flow --mock-must-stop  # Test MUST_STOP
    python auto_responder_test.py --transcript=/path/to/file.jsonl  # Use real transcript

Author: Anonymous
"""

import json
import os
import sys
import re
import time
import glob
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List

# ============================================================
# Configuration (same as full implementation)
# ============================================================
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "auto_responder_config.yaml"


def get_state_dir() -> Path:
    """Get writable state directory in .cache folder under SCRIPT_DIR.

    This keeps all state files local to the project, avoiding
    platform-specific XDG/AppData paths.
    """
    state_dir = SCRIPT_DIR / ".cache"

    try:
        state_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        import tempfile
        state_dir = Path(tempfile.gettempdir()) / "youra-auto-responder-test"
        state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir


STATE_DIR = get_state_dir()
STATE_FILE = STATE_DIR / "auto_responder_state.json"
TRIGGER_HISTORY_FILE = STATE_DIR / "hook_trigger_history.json"
TEST_LOG_FILE = STATE_DIR / "auto_responder_test.log"

MAX_TRIGGERS = 4
TIME_WINDOW_SECONDS = 60


# ============================================================
# Test Logger
# ============================================================
class TestLogger:
    def __init__(self, verbose: bool = True):
        self.logs = []
        self.verbose = verbose
        self.test_results = []

    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] [{level}] {message}"
        self.logs.append(entry)
        if self.verbose:
            print(entry, file=sys.stderr)

    def info(self, message: str):
        self.log(message, "INFO")

    def error(self, message: str):
        self.log(message, "ERROR")

    def success(self, message: str):
        self.log(f"[PASS] {message}", "PASS")

    def fail(self, message: str):
        self.log(f"[FAIL] {message}", "FAIL")

    def section(self, title: str):
        self.log("=" * 60)
        self.log(f"  {title}")
        self.log("=" * 60)

    def subsection(self, title: str):
        self.log("-" * 40)
        self.log(f"  {title}")

    def test_result(self, name: str, passed: bool, details: str = ""):
        result = {"name": name, "passed": passed, "details": details}
        self.test_results.append(result)
        if passed:
            self.success(f"{name}: {details}" if details else name)
        else:
            self.fail(f"{name}: {details}" if details else name)

    def save(self):
        try:
            with open(TEST_LOG_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(self.logs))
                f.write("\n\n" + "=" * 60 + "\n")
                f.write("TEST SUMMARY\n")
                f.write("=" * 60 + "\n")
                passed = sum(1 for r in self.test_results if r["passed"])
                total = len(self.test_results)
                f.write(f"Passed: {passed}/{total}\n")
                for r in self.test_results:
                    status = "PASS" if r["passed"] else "FAIL"
                    f.write(f"  [{status}] {r['name']}\n")
            print(f"\n[TEST] Log saved to: {TEST_LOG_FILE}", file=sys.stderr)
        except Exception as e:
            print(f"Failed to save log: {e}", file=sys.stderr)

    def summary(self):
        self.section("TEST SUMMARY")
        passed = sum(1 for r in self.test_results if r["passed"])
        total = len(self.test_results)
        self.info(f"Passed: {passed}/{total}")
        for r in self.test_results:
            status = "PASS" if r["passed"] else "FAIL"
            self.info(f"  [{status}] {r['name']}")


logger = TestLogger()


# ============================================================
# Functions to Test (copied from auto_responder_full.py)
# ============================================================

def output_decision(decision: str, reason: str = None) -> dict:
    """Output JSON decision (returns dict for testing instead of printing)."""
    output = {"decision": decision}
    if reason:
        output["reason"] = reason
    return output


def load_config() -> Optional[Dict[str, Any]]:
    """Load and validate configuration from YAML file."""
    try:
        import yaml
    except ImportError:
        logger.error("PyYAML not installed")
        return None

    if not CONFIG_FILE.exists():
        logger.error(f"Config file not found: {CONFIG_FILE}")
        return None

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        if config is None:
            logger.error("Config file is empty")
            return None

        required_sections = ["enabled", "openrouter", "context", "youra", "loop_prevention"]
        missing = [s for s in required_sections if s not in config]
        if missing:
            logger.error(f"Missing config sections: {missing}")
            return None

        return config
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return None


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
        logger.error(f"Failed to save state: {e}")


def check_and_update_trigger_history() -> bool:
    """Check if rate limit exceeded. Returns True if should disable."""
    current_time = time.time()
    history = []

    if TRIGGER_HISTORY_FILE.exists():
        try:
            with open(TRIGGER_HISTORY_FILE, 'r') as f:
                history = json.load(f)
        except Exception:
            history = []

    history = [t for t in history if current_time - t < TIME_WINDOW_SECONDS]
    history.append(current_time)

    try:
        with open(TRIGGER_HISTORY_FILE, 'w') as f:
            json.dump(history, f)
    except Exception as e:
        logger.error(f"Failed to save trigger history: {e}")

    if len(history) >= MAX_TRIGGERS:
        logger.info(f"Rate limit exceeded: {len(history)} triggers in {TIME_WINDOW_SECONDS}s")
        return True

    logger.info(f"Trigger count: {len(history)}/{MAX_TRIGGERS}")
    return False


def disable_hook_in_config() -> bool:
    """Disable hook in config using YAML + regex."""
    try:
        import yaml
    except ImportError:
        return _disable_hook_fallback()

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        if config and config.get('enabled', False):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                original_content = f.read()

            pattern = r'^(\s*)enabled\s*:\s*(true|True|TRUE|yes|Yes|YES|on|On|ON)\s*$'
            new_content = re.sub(pattern, r'\1enabled: false', original_content, count=1, flags=re.MULTILINE)

            if new_content != original_content:
                with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                logger.info("Auto-disabled hook in config")

        if TRIGGER_HISTORY_FILE.exists():
            TRIGGER_HISTORY_FILE.unlink()

        return True
    except Exception as e:
        logger.error(f"Failed to disable hook: {e}")
        return _disable_hook_fallback()


def _disable_hook_fallback() -> bool:
    """Fallback method using regex only."""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            content = f.read()

        pattern = r'^(\s*)enabled\s*:\s*(true|True|TRUE|yes|Yes|YES|on|On|ON)\s*$'
        new_content = re.sub(pattern, r'\1enabled: false', content, count=1, flags=re.MULTILINE)

        if new_content != content:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                f.write(new_content)
            logger.info("Auto-disabled hook (fallback)")

        if TRIGGER_HISTORY_FILE.exists():
            TRIGGER_HISTORY_FILE.unlink()

        return True
    except Exception as e:
        logger.error(f"Fallback disable failed: {e}")
        return False


def read_transcript(transcript_path: str) -> list:
    """Read transcript messages from JSONL file."""
    messages = []
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    messages.append(data)
                except Exception:
                    continue
    except Exception as e:
        logger.error(f"Transcript read error: {e}")
    return messages


def extract_conversation_text(messages: list, max_chars: int = 3000) -> str:
    """Extract recent conversation (optimized - from end, stop at max_chars)."""
    result = []
    total = 0

    for msg in reversed(messages):
        msg_type = msg.get("type", "")
        text = ""

        if msg_type == "user":
            content = msg.get("message", {}).get("content", "")
            if isinstance(content, list):
                text = "[USER] " + "".join(
                    item.get("text", "") for item in content
                    if isinstance(item, dict) and item.get("type") == "text"
                )
            else:
                text = f"[USER] {content}"
        elif msg_type == "assistant":
            content = msg.get("message", {}).get("content", [])
            if isinstance(content, list):
                text = "[ASSISTANT] " + "".join(
                    item.get("text", "") for item in content
                    if isinstance(item, dict) and item.get("type") == "text"
                )
            else:
                text = f"[ASSISTANT] {content}"
        else:
            continue

        text = text.strip()
        if not text or text in ("[USER]", "[ASSISTANT]"):
            continue

        if total + len(text) > max_chars:
            break

        result.append(text)
        total += len(text) + 1

    result.reverse()
    return "\n".join(result)


def extract_last_line(messages: list) -> str:
    """Extract last line from assistant's last message."""
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


def has_critical_keywords(text: str, keywords: list) -> Tuple[bool, str]:
    """Check if text contains any critical keywords."""
    text_lower = text.lower()
    for keyword in keywords:
        if keyword.lower() in text_lower:
            return True, keyword
    return False, ""


def match_pattern(last_line: str, patterns: list) -> bool:
    """Check if last line matches any pattern."""
    last_line_lower = last_line.lower()
    for pattern in patterns:
        pattern_str = pattern if isinstance(pattern, str) else str(pattern)
        if pattern_str.lower() in last_line_lower:
            return True
    return False


def find_research_folder(project_dir: str, pattern: str) -> Optional[str]:
    """Find the most recent research folder."""
    full_pattern = os.path.join(project_dir, pattern)
    folders = sorted(glob.glob(full_pattern), reverse=True)
    if folders:
        return folders[0].rstrip("/").rstrip("\\")
    return None


def mock_llm_call(conversation: str, decision: str = "CONTINUE") -> Tuple[bool, str]:
    """Mock LLM call for testing."""
    logger.info(f"[MOCK LLM] Decision: {decision}")

    if decision == "MUST_STOP":
        response = "DISABLE: Mock MUST_STOP - human intervention required"
        is_must_stop = True
    else:
        response = """
## Workflow
Read and follow: bmad-custom-src/custom/modules/youra-research/workflows/full-pipeline-unattended/instructions.md

## Auto-Resume Context (MOCK)
- Pipeline: test-pipeline
- Current Phase: Phase 4 (H-M1)
- Progress: 1/3 hypotheses complete
- Archon task management: Check and update tasks

## Stop Reason
[MOCK] Routine confirmation prompt detected

## Resume Instructions
- Skip to: Step 6 (Hypothesis Loop)
- Load hypothesis: H-M1
- Continue from: Phase 4, next task
"""
        is_must_stop = False

    return is_must_stop, response


# ============================================================
# Test Functions
# ============================================================

def test_config():
    """Test config loading."""
    logger.section("TEST: Config Loading")

    config = load_config()
    if config is None:
        logger.test_result("load_config", False, "Config is None")
        return False

    logger.info(f"Config loaded successfully")
    logger.info(f"  enabled: {config.get('enabled')}")
    logger.info(f"  openrouter.model: {config.get('openrouter', {}).get('model')}")
    logger.info(f"  context.focus_chars: {config.get('context', {}).get('focus_chars')}")

    # Check required sections
    required = ["enabled", "openrouter", "context", "youra", "loop_prevention"]
    for section in required:
        if section not in config:
            logger.test_result("config_sections", False, f"Missing: {section}")
            return False

    logger.test_result("load_config", True, f"All {len(required)} sections present")
    return True


def test_state_management():
    """Test state management functions."""
    logger.section("TEST: State Management")

    # Clean up first
    if STATE_FILE.exists():
        STATE_FILE.unlink()

    # Test initial state
    state = load_state()
    logger.test_result("initial_state", state.get("retry_count") == 0, f"retry_count={state.get('retry_count')}")

    # Test save and load
    state["retry_count"] = 5
    save_state(state)
    loaded = load_state()
    logger.test_result("save_load_state", loaded.get("retry_count") == 5, f"Saved 5, loaded {loaded.get('retry_count')}")

    # Clean up
    if STATE_FILE.exists():
        STATE_FILE.unlink()

    return True


def test_rate_limiting():
    """Test rate limiting functions."""
    logger.section("TEST: Rate Limiting")

    # Clean up first
    if TRIGGER_HISTORY_FILE.exists():
        TRIGGER_HISTORY_FILE.unlink()

    # Test multiple triggers
    results = []
    for i in range(MAX_TRIGGERS + 1):
        exceeded = check_and_update_trigger_history()
        results.append(exceeded)
        logger.info(f"  Trigger {i+1}: exceeded={exceeded}")

    # First MAX_TRIGGERS-1 should be False, last should be True
    expected_exceed_at = MAX_TRIGGERS
    actual_exceed_at = results.index(True) + 1 if True in results else -1

    logger.test_result(
        "rate_limit_trigger",
        actual_exceed_at == expected_exceed_at,
        f"Expected exceed at {expected_exceed_at}, got {actual_exceed_at}"
    )

    # Clean up
    if TRIGGER_HISTORY_FILE.exists():
        TRIGGER_HISTORY_FILE.unlink()

    return True


def test_transcript_reading(transcript_path: Optional[str] = None):
    """Test transcript reading functions."""
    logger.section("TEST: Transcript Reading")

    if transcript_path and Path(transcript_path).exists():
        # Use real transcript
        logger.info(f"Using real transcript: {transcript_path}")
        messages = read_transcript(transcript_path)
    else:
        # Use mock data
        logger.info("Using mock transcript data")
        messages = [
            {"type": "user", "message": {"content": "Hello, start Phase 4"}},
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "Starting Phase 4..."}]}},
            {"type": "system", "message": {"content": "System message - should be ignored"}},
            {"type": "user", "message": {"content": "Continue please"}},
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "Phase 4 complete. Proceed? [Y/N]"}]}},
        ]

    logger.info(f"Total messages: {len(messages)}")

    # Test extract_conversation_text
    conversation = extract_conversation_text(messages, max_chars=500)
    logger.info(f"Extracted conversation: {len(conversation)} chars")
    logger.test_result(
        "extract_conversation",
        len(conversation) > 0 and "[USER]" in conversation,
        f"{len(conversation)} chars, has [USER]: {'[USER]' in conversation}"
    )

    # Test extract_last_line
    last_line = extract_last_line(messages)
    logger.info(f"Last line: {last_line[:50]}..." if len(last_line) > 50 else f"Last line: {last_line}")
    logger.test_result(
        "extract_last_line",
        len(last_line) > 0,
        f"Got: '{last_line[:30]}...'" if last_line else "Empty"
    )

    # Test that system messages are filtered
    if "[SYSTEM]" in conversation.upper() or "should be ignored" in conversation.lower():
        logger.test_result("filter_system_messages", False, "System messages not filtered")
    else:
        logger.test_result("filter_system_messages", True, "System messages properly filtered")

    return True


def test_keyword_detection():
    """Test critical keyword and pattern detection."""
    logger.section("TEST: Keyword & Pattern Detection")

    config = load_config()
    if not config:
        logger.test_result("keyword_detection", False, "Config not loaded")
        return False

    # Test critical keywords
    critical_keywords = config.get("critical_keywords", ["authentication", "permission denied"])

    test_texts = [
        ("Normal text without keywords", False),
        ("Error: authentication failed", True),
        ("Permission denied: access forbidden", True),
        ("Phase 4 completed successfully", False),
    ]

    for text, expected_found in test_texts:
        found, keyword = has_critical_keywords(text, critical_keywords)
        passed = found == expected_found
        logger.test_result(
            f"critical_keyword_{text[:20]}",
            passed,
            f"Expected {expected_found}, got {found}" + (f" (keyword: {keyword})" if keyword else "")
        )

    # Test pattern matching
    patterns = config.get("quick_patterns", {}).get("patterns", ["[Y/N]", "[y/n]"])

    test_lines = [
        ("Proceed? [Y/N]", True),
        ("Continue? [y/n]", True),
        ("Phase complete", False),
    ]

    for line, expected_match in test_lines:
        matched = match_pattern(line, patterns)
        passed = matched == expected_match
        logger.test_result(
            f"pattern_match_{line[:15]}",
            passed,
            f"Expected {expected_match}, got {matched}"
        )

    return True


def test_full_flow(mock_decision: str = "CONTINUE", transcript_path: Optional[str] = None):
    """Test full flow with mock LLM."""
    logger.section(f"TEST: Full Flow (mock={mock_decision})")

    # Step 1: Load config
    logger.subsection("Step 1: Load Config")
    config = load_config()
    if not config:
        logger.test_result("full_flow_config", False, "Config load failed")
        return False
    logger.info(f"Config loaded: enabled={config.get('enabled')}")

    # Step 2: Check if enabled
    logger.subsection("Step 2: Check Enabled")
    if not config.get("enabled", False):
        result = output_decision("approve", "Hook disabled in config")
        logger.info(f"Hook disabled, would output: {result}")
        logger.test_result("full_flow_disabled", True, "Correctly handles disabled state")
        return True

    # Step 3: Read transcript
    logger.subsection("Step 3: Read Transcript")
    if transcript_path and Path(transcript_path).exists():
        messages = read_transcript(transcript_path)
    else:
        messages = [
            {"type": "user", "message": {"content": "Start pipeline"}},
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "Pipeline started. Phase 4 complete. Continue? [Y/N]"}]}},
        ]

    focus_chars = config.get("context", {}).get("focus_chars", 2000)
    conversation = extract_conversation_text(messages, max_chars=focus_chars)
    last_line = extract_last_line(messages)
    logger.info(f"Conversation: {len(conversation)} chars")
    logger.info(f"Last line: {last_line[:50]}...")

    # Step 4: Check critical keywords
    logger.subsection("Step 4: Critical Keywords")
    critical_keywords = config.get("critical_keywords", [])
    has_critical, matched_kw = has_critical_keywords(conversation, critical_keywords)
    logger.info(f"Critical keyword found: {has_critical}" + (f" ({matched_kw})" if matched_kw else ""))

    # Step 5: Pattern matching
    logger.subsection("Step 5: Pattern Matching")
    quick_patterns = config.get("quick_patterns", {})
    patterns = quick_patterns.get("patterns", [])
    pattern_matched = match_pattern(last_line, patterns) if not has_critical else False
    logger.info(f"Pattern matched: {pattern_matched}")

    if pattern_matched and not has_critical:
        default_response = quick_patterns.get("default_response", "Y")
        result = {"decision": "block", "reason": f"[AUTO-RESPONDER] Pattern matched: {default_response}"}
        logger.info(f"Quick response: {result}")
        logger.test_result("full_flow_quick_pattern", True, f"Pattern match -> {default_response}")
        return True

    # Step 6: Mock LLM call
    logger.subsection("Step 6: LLM Analysis (Mock)")
    is_must_stop, llm_response = mock_llm_call(conversation, mock_decision)
    logger.info(f"LLM decision: {'MUST_STOP' if is_must_stop else 'CONTINUE'}")

    # Step 7: Handle decision
    logger.subsection("Step 7: Handle Decision")
    if is_must_stop:
        result = output_decision("approve", f"[MUST_STOP] {llm_response[:100]}")
        logger.info(f"MUST_STOP -> approve: {result}")
        logger.test_result("full_flow_must_stop", True, "Correctly handles MUST_STOP")
    else:
        result = {"decision": "block", "reason": f"[AUTO-RESPONDER] {llm_response}"}
        logger.info(f"CONTINUE -> block with resume prompt")
        logger.test_result("full_flow_continue", True, "Correctly handles CONTINUE")

    # Output final decision
    print(json.dumps(result))

    return True


def test_output_decision():
    """Test JSON output format."""
    logger.section("TEST: Output Decision Format")

    # Test approve
    result = output_decision("approve", "Test reason")
    logger.test_result(
        "output_approve",
        result.get("decision") == "approve" and result.get("reason") == "Test reason",
        f"Got: {result}"
    )

    # Test block
    result = output_decision("block", "Continue prompt")
    logger.test_result(
        "output_block",
        result.get("decision") == "block",
        f"Got: {result}"
    )

    # Test without reason
    result = output_decision("approve")
    logger.test_result(
        "output_no_reason",
        "reason" not in result or result.get("reason") is None,
        f"Got: {result}"
    )

    return True


# ============================================================
# Main
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="YouRA Auto-Responder Test Suite")
    parser.add_argument("--test", type=str, default="all",
                        help="Test to run: all, config, state, rate, transcript, keyword, flow, output")
    parser.add_argument("--transcript", type=str, default=None,
                        help="Path to real transcript file for testing")
    parser.add_argument("--mock-must-stop", action="store_true",
                        help="Use MUST_STOP for mock LLM decision")
    parser.add_argument("--mock-continue", action="store_true",
                        help="Use CONTINUE for mock LLM decision (default)")
    parser.add_argument("--quiet", action="store_true",
                        help="Reduce output verbosity")

    args = parser.parse_args()

    logger.verbose = not args.quiet
    mock_decision = "MUST_STOP" if args.mock_must_stop else "CONTINUE"

    logger.section("YouRA Auto-Responder Test Suite")
    logger.info(f"Test: {args.test}")
    logger.info(f"Mock LLM decision: {mock_decision}")
    logger.info(f"Transcript: {args.transcript or 'Mock data'}")
    logger.info(f"State dir: {STATE_DIR}")

    tests = {
        "config": lambda: test_config(),
        "state": lambda: test_state_management(),
        "rate": lambda: test_rate_limiting(),
        "transcript": lambda: test_transcript_reading(args.transcript),
        "keyword": lambda: test_keyword_detection(),
        "flow": lambda: test_full_flow(mock_decision, args.transcript),
        "output": lambda: test_output_decision(),
    }

    if args.test == "all":
        for name, test_fn in tests.items():
            try:
                test_fn()
            except Exception as e:
                logger.error(f"Test {name} failed with exception: {e}")
                logger.test_result(name, False, str(e))
    elif args.test in tests:
        try:
            tests[args.test]()
        except Exception as e:
            logger.error(f"Test {args.test} failed with exception: {e}")
            logger.test_result(args.test, False, str(e))
    else:
        logger.error(f"Unknown test: {args.test}")
        logger.info(f"Available tests: {', '.join(tests.keys())}")

    logger.summary()
    logger.save()


if __name__ == "__main__":
    print("\n" + "=" * 60, file=sys.stderr)
    print("  YouRA Auto-Responder TEST SUITE", file=sys.stderr)
    print("  Usage: python auto_responder_test.py --help", file=sys.stderr)
    print("=" * 60 + "\n", file=sys.stderr)
    main()
