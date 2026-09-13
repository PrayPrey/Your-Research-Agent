"""Shared Claude CLI runner with automatic retry on API overload (5xx).

Extracted from the per-phase _run_claude implementations so that retry policy
for transient Anthropic API errors (529 Overloaded, 5xx, network blips) lives
in one place.

Detection: after Claude CLI exits with a non-zero code, the tail of the output
log is scanned for known transient-error signatures. If found, the same prompt
is re-invoked after an exponential backoff. Real failures (non-transient
exit-1) are returned immediately without retrying.

Used by: run_phase0/1/2a/2b/2c/3/4/45/6/65/651.py
"""
from __future__ import annotations

import os
import re
import select
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable, Optional

import json as _json

from phase_output_verifier import build_claude_cmd
from timeout_policy import log_timeout_marker


# ----- Retry policy -----
MAX_OVERLOAD_RETRIES = 5
BACKOFF_SCHEDULE = [30, 60, 120, 240, 480]  # seconds; len must be >= MAX_OVERLOAD_RETRIES

# Patterns that indicate a transient server-side failure worth retrying.
# Kept narrow: we only retry when we are confident the failure was upstream,
# not a real Claude error from the prompt itself.
TRANSIENT_PATTERNS = [
    re.compile(r"API Error:\s*5\d\d", re.IGNORECASE),
    re.compile(r"\bOverloaded\b", re.IGNORECASE),
    re.compile(r"\brate[_\- ]?limit", re.IGNORECASE),
    re.compile(r"\b(?:Connection|Connection reset|ECONNRESET|ETIMEDOUT)\b"),
    re.compile(r"\b502\s+Bad Gateway\b", re.IGNORECASE),
    re.compile(r"\b503\s+Service Unavailable\b", re.IGNORECASE),
    re.compile(r"\b504\s+Gateway Timeout\b", re.IGNORECASE),
]


def _tail_for_transient(log_path: Path, tail_bytes: int = 8192) -> Optional[str]:
    """Return the matching transient pattern label, or None."""
    try:
        if not log_path.exists():
            return None
        size = log_path.stat().st_size
        with open(log_path, "rb") as f:
            if size > tail_bytes:
                f.seek(-tail_bytes, os.SEEK_END)
            tail = f.read().decode("utf-8", errors="replace")
        for pat in TRANSIENT_PATTERNS:
            m = pat.search(tail)
            if m:
                return m.group(0)
        return None
    except Exception:
        return None


def _emit_stream_json_text(line: str, log_fn: Callable[[str], None]) -> None:
    """Render a single stream-json line to stdout.

    Mirrors the per-event display logic used by phase0/1/2a runners:
    - assistant content -> write text blocks
    - result events -> log session cost
    - non-JSON lines -> echo as-is
    """
    try:
        event = _json.loads(line.strip())
    except Exception:
        sys.stdout.write(line)
        sys.stdout.flush()
        return
    etype = event.get("type")
    if etype == "assistant" and "content" in event:
        for block in event.get("content") or []:
            if block.get("type") == "text":
                sys.stdout.write(block.get("text", ""))
                sys.stdout.flush()
    elif etype == "result":
        log_fn(f"Session complete. Cost: {event.get('cost_usd', 'N/A')}")


def run_claude_once(
    *,
    claude_cli: Path,
    project_dir: Path,
    cache_dir: Path,
    prompt: str,
    timeout: int,
    output_log: Path,
    phase_name: str,
    log_fn: Callable[[str], None],
    process_setter: Callable[[Optional[subprocess.Popen]], None],
    echo_to_stdout: bool = True,
    monitor_complete_lock: bool = False,
    lock_grace_period: int = 60,
    extra_cli_args: Optional[list] = None,
    stream_json: bool = False,
    separate_stderr: bool = False,
    hang_startup_grace: Optional[int] = None,
    hang_idle_secs: Optional[int] = None,
    proc_tree_cputime_fn: Optional[Callable[[int], float]] = None,
) -> int:
    """Single invocation of Claude CLI. No retry. Returns exit code.

    Mirrors the original _run_claude semantics: streams stdout, enforces
    timeout (returns 124), optionally watches for the PHASE_COMPLETE lock to
    force-terminate stragglers.

    process_setter: callback to publish the live Popen handle so signal
    handlers in the caller can terminate it.
    """
    claude_cmd = build_claude_cmd(claude_cli, prompt, extra_cli_args) if extra_cli_args else build_claude_cmd(claude_cli, prompt)
    env = os.environ.copy()
    env.pop("CLAUDECODE", None)

    phase_complete_lock = cache_dir / f"{phase_name}_complete.lock" if monitor_complete_lock else None
    lock_detected_at: Optional[float] = None
    hang_check_enabled = (
        hang_startup_grace is not None
        and hang_idle_secs is not None
        and proc_tree_cputime_fn is not None
    )

    stderr_mode = subprocess.PIPE if separate_stderr else subprocess.STDOUT
    timed_out = False
    proc: Optional[subprocess.Popen] = None
    try:
        proc = subprocess.Popen(
            claude_cmd, cwd=str(project_dir),
            stdout=subprocess.PIPE, stderr=stderr_mode,
            text=True, bufsize=1, env=env,
        )
        process_setter(proc)
        start_time = time.time()
        last_cpu = 0.0
        last_cpu_change = start_time
        with open(output_log, "a", encoding="utf-8") as out_f:
            while True:
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    log_timeout_marker(log_fn, phase_name, elapsed, attempt="retry")
                    log_fn(f"_run_claude TIMEOUT after {elapsed:.0f}s — terminating")
                    proc.terminate()
                    try:
                        proc.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                    timed_out = True
                    break

                if hang_check_enabled and elapsed > hang_startup_grace:
                    cur_cpu = proc_tree_cputime_fn(proc.pid)
                    if cur_cpu > last_cpu:
                        last_cpu = cur_cpu
                        last_cpu_change = time.time()
                    elif time.time() - last_cpu_change > hang_idle_secs:
                        log_fn(f"_run_claude HANG detected (CPU idle {hang_idle_secs}s) — terminating")
                        proc.terminate()
                        try:
                            proc.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            proc.kill()
                        break

                if phase_complete_lock is not None and phase_complete_lock.exists():
                    if lock_detected_at is None:
                        lock_detected_at = time.time()
                        log_fn("_run_claude: PHASE_COMPLETE lock detected, waiting for graceful exit...")
                    elif time.time() - lock_detected_at > lock_grace_period:
                        log_fn(
                            f"_run_claude: Claude still running {lock_grace_period}s "
                            f"after PHASE_COMPLETE — force terminating"
                        )
                        proc.terminate()
                        try:
                            proc.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            proc.kill()
                        break

                ready, _, _ = select.select([proc.stdout], [], [], 1.0)
                if ready:
                    line = proc.stdout.readline()
                    if not line:
                        break
                    out_f.write(line); out_f.flush()
                    if stream_json:
                        _emit_stream_json_text(line, log_fn)
                    elif echo_to_stdout:
                        sys.stdout.write(line); sys.stdout.flush()
                elif proc.poll() is not None:
                    for line in proc.stdout:
                        out_f.write(line); out_f.flush()
                        if stream_json:
                            _emit_stream_json_text(line, log_fn)
                        elif echo_to_stdout:
                            sys.stdout.write(line); sys.stdout.flush()
                    break
        rc = proc.wait()
        # Capture stderr for debugging when separated
        if separate_stderr and proc.stderr is not None:
            try:
                stderr_output = proc.stderr.read()
                if stderr_output and stderr_output.strip():
                    log_fn(f"Claude CLI stderr:\n{stderr_output.strip()}")
            except Exception:
                pass
        if timed_out:
            return 124
        return rc
    except Exception as e:
        log_fn(f"ERROR in _run_claude: {e}")
        return 1
    finally:
        process_setter(None)


def run_claude_with_retry(
    *,
    claude_cli: Path,
    project_dir: Path,
    cache_dir: Path,
    prompt: str,
    timeout: int,
    output_log: Path,
    phase_name: str,
    log_fn: Callable[[str], None],
    process_setter: Callable[[Optional[subprocess.Popen]], None],
    echo_to_stdout: bool = True,
    monitor_complete_lock: bool = False,
    lock_grace_period: int = 60,
    max_overload_retries: int = MAX_OVERLOAD_RETRIES,
    extra_cli_args: Optional[list] = None,
    stream_json: bool = False,
    separate_stderr: bool = False,
    hang_startup_grace: Optional[int] = None,
    hang_idle_secs: Optional[int] = None,
    proc_tree_cputime_fn: Optional[Callable[[int], float]] = None,
) -> int:
    """Run Claude CLI; auto-retry with exponential backoff on Anthropic 5xx/Overloaded.

    Returns the final exit code from Claude CLI. Real (non-transient) failures
    are returned immediately. Timeouts (124) are NOT retried here — caller
    decides if they want to re-run.
    """
    log_path = Path(output_log)
    for attempt in range(max_overload_retries + 1):
        if attempt > 0:
            backoff_idx = min(attempt - 1, len(BACKOFF_SCHEDULE) - 1)
            wait_s = BACKOFF_SCHEDULE[backoff_idx]
            log_fn(
                f"[overload-retry] attempt {attempt}/{max_overload_retries} — "
                f"sleeping {wait_s}s before retry"
            )
            time.sleep(wait_s)

        rc = run_claude_once(
            claude_cli=claude_cli,
            project_dir=project_dir,
            cache_dir=cache_dir,
            prompt=prompt,
            timeout=timeout,
            output_log=log_path,
            phase_name=phase_name,
            log_fn=log_fn,
            process_setter=process_setter,
            echo_to_stdout=echo_to_stdout,
            monitor_complete_lock=monitor_complete_lock,
            lock_grace_period=lock_grace_period,
            extra_cli_args=extra_cli_args,
            stream_json=stream_json,
            separate_stderr=separate_stderr,
            hang_startup_grace=hang_startup_grace,
            hang_idle_secs=hang_idle_secs,
            proc_tree_cputime_fn=proc_tree_cputime_fn,
        )

        if rc == 0 or rc == 124:
            return rc

        matched = _tail_for_transient(log_path)
        if matched is None:
            return rc

        log_fn(
            f"[overload-retry] detected transient API error ({matched!r}) "
            f"in {log_path.name}; exit_code={rc}"
        )
        if attempt >= max_overload_retries:
            log_fn(
                f"[overload-retry] giving up after {max_overload_retries} retries; "
                f"returning exit_code={rc}"
            )
            return rc
    return rc
