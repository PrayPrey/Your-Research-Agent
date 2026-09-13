"""Timeout policy helpers (Option C: kill on timeout, advance pipeline).

Used by all run_phase*.py launchers and run_hypothesis_loop.py.

Behavior:
- First Claude CLI run hits args.timeout → terminate; retry once.
- Retry hits timeout → launcher decides exit code based on whether the
  phase's *core artifacts* exist on disk.
- Phase 4 has its own kill_phase4_experiment() since the experiment is
  detached via nohup and would otherwise become a GPU zombie.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Iterable

# ============================================================
# Core artifacts per phase (existence-based check)
# ============================================================
# Paths are relative to research_folder. {h_id} is substituted with the
# hypothesis id when applicable.
CORE_ARTIFACTS = {
    "phase0":  ["00_brainstorm_session.md"],
    "phase1":  ["01_targeted_research.md"],
    "phase2a": ["03_refinement.yaml"],
    "phase2b": ["verification_state.yaml"],
    "phase2c": ["{h_id}/02c_experiment_brief.md"],
    "phase3":  ["{h_id}/03_prd.md"],
    "phase4":  ["{h_id}/04_validation.md", "{h_id}/04_checkpoint.yaml"],
    "phase45": ["045_validated_hypothesis.md"],
    "phase6":  ["paper/06_paper.md"],
    "phase65": ["paper/06_paper_final.md"],
    "phase651": ["paper/overleaf/main.tex"],
}


def core_artifacts_exist(
    research_folder: str | Path,
    phase: str,
    hypothesis_id: str | None = None,
) -> tuple[bool, list[str]]:
    """Return (all_exist, missing_paths)."""
    patterns = CORE_ARTIFACTS.get(phase, [])
    if not patterns:
        return True, []
    root = Path(research_folder)
    missing: list[str] = []
    for pat in patterns:
        rel = pat.format(h_id=hypothesis_id or "")
        if not (root / rel).exists():
            missing.append(rel)
    return len(missing) == 0, missing


# ============================================================
# TIMEOUT marker logging
# ============================================================
def log_timeout_marker(
    log_fn,
    phase: str,
    elapsed: float,
    *,
    attempt: str = "initial",
    hypothesis_id: str | None = None,
    extra: dict | None = None,
) -> None:
    """Emit a structured marker line so external tools can grep for timeouts."""
    payload = {
        "marker": "TIMEOUT",
        "phase": phase,
        "attempt": attempt,
        "elapsed_seconds": round(elapsed, 1),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    if hypothesis_id:
        payload["hypothesis_id"] = hypothesis_id
    if extra:
        payload.update(extra)
    log_fn(f"⏱️  TIMEOUT MARKER {json.dumps(payload, ensure_ascii=False)}")


# ============================================================
# Phase 4 detached experiment kill
# ============================================================
def kill_phase4_experiment(
    research_folder: str | Path,
    hypothesis_id: str,
    log_fn,
    grace_seconds: int = 10,
) -> None:
    """Kill the nohup'd experiment launched by Phase 4 step-05b.

    Reads {hypothesis_folder}/code/experiment.pid, sends SIGTERM to the
    process group, waits grace_seconds, then SIGKILL if still alive.
    Removes experiment.pid on success.
    """
    pid_file = Path(research_folder) / hypothesis_id / "code" / "experiment.pid"
    if not pid_file.exists():
        log_fn(f"kill_phase4_experiment: no pid file at {pid_file} — nothing to kill")
        return

    try:
        pid_str = pid_file.read_text(encoding="utf-8").strip()
        if not pid_str:
            log_fn(f"kill_phase4_experiment: empty pid file {pid_file}")
            return
        pid = int(pid_str)
    except (OSError, ValueError) as e:
        log_fn(f"kill_phase4_experiment: failed to read {pid_file}: {e}")
        return

    if not _pid_alive(pid):
        log_fn(f"kill_phase4_experiment: pid {pid} already dead")
        try:
            pid_file.unlink()
        except OSError:
            pass
        return

    log_fn(f"kill_phase4_experiment: sending SIGTERM to pid {pid} (and pgroup)")
    _terminate_pgroup(pid, signal.SIGTERM, log_fn)

    deadline = time.time() + grace_seconds
    while time.time() < deadline:
        if not _pid_alive(pid):
            log_fn(f"kill_phase4_experiment: pid {pid} terminated cleanly")
            try:
                pid_file.unlink()
            except OSError:
                pass
            return
        time.sleep(0.5)

    log_fn(f"kill_phase4_experiment: pid {pid} still alive after {grace_seconds}s — SIGKILL")
    _terminate_pgroup(pid, signal.SIGKILL, log_fn)
    try:
        pid_file.unlink()
    except OSError:
        pass


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def _terminate_pgroup(pid: int, sig: int, log_fn) -> None:
    """Try to signal the whole process group, fall back to single PID."""
    try:
        pgid = os.getpgid(pid)
        os.killpg(pgid, sig)
        return
    except (ProcessLookupError, PermissionError, OSError) as e:
        log_fn(f"_terminate_pgroup: pgroup signal failed ({e}), trying single PID")
    try:
        os.kill(pid, sig)
    except ProcessLookupError:
        pass
    except OSError as e:
        log_fn(f"_terminate_pgroup: os.kill({pid},{sig}) failed: {e}")


# ============================================================
# Phase 4 synthetic gate JSON for hypothesis_loop
# ============================================================
def emit_phase4_timeout_gate(
    hypothesis_id: str,
    research_folder: str | Path,
    *,
    gate_type: str = "MUST_WORK",
    elapsed_seconds: float | None = None,
) -> dict:
    """Return the dict that run_phase4.py prints as its final stdout JSON.

    Caller is responsible for printing it as the last stdout line so
    run_hypothesis_loop.py can parse it.
    """
    payload = {
        "hypothesis_id": hypothesis_id,
        "hypothesis": hypothesis_id,
        "gate_result": "TIMEOUT_PARTIAL",
        "gate_type": gate_type,
        "route_to": None,
        "research_folder": str(research_folder),
        "exit_code": 0,
        "timeout": True,
    }
    if elapsed_seconds is not None:
        payload["elapsed_seconds"] = round(elapsed_seconds, 1)
    return payload


# ============================================================
# Decide launcher exit code after retry timeout
# ============================================================
def post_timeout_exit_code(
    research_folder: str | Path,
    phase: str,
    log_fn,
    hypothesis_id: str | None = None,
) -> int:
    """Returns 0 if core artifacts exist (advance pipeline), else 1."""
    ok, missing = core_artifacts_exist(research_folder, phase, hypothesis_id)
    if ok:
        log_fn(f"post_timeout_exit_code: core artifacts present for {phase} → exit 0 (advance)")
        return 0
    log_fn(
        f"post_timeout_exit_code: missing core artifacts for {phase}: {missing} → exit 1 (fail)"
    )
    return 1
