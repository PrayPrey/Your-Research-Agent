#!/usr/bin/env python3
"""
Hypothesis Loop — External for-loop calling run_phase2c/3/4.py per hypothesis

Reads verification_state.yaml, queues READY hypotheses in dependency order,
and for each hypothesis sequentially calls:
  run_phase2c.py → run_phase3.py → run_phase4.py

Gate results are read from run_phase4.py's stdout JSON (last line) to decide
whether to continue, stop (ROUTED), or skip (SHOULD_WORK failure).

This script does NOT directly launch Claude CLI — each run_phase*.py handles
its own Claude CLI session, active_phase.json, and auto_responder_config.

Exit codes:
  0 — All hypotheses processed (all PASS or terminal)
  1 — Error (cannot load state, no READY hypotheses, etc.)
  2 — Routing required (ROUTED_TO_PHASE_0 or ROUTED_TO_PHASE_2A)
  3 — Incomplete (some hypotheses BLOCKED/FAILED, loop cannot continue)

Stdout output (last line, JSON):
  {"status": "COMPLETE", "research_folder": "...", "hypotheses": {...}}
  {"status": "ROUTED", "route_to": "Phase 0", "hypothesis": "h-e1", ...}
  {"status": "INCOMPLETE", "reason": "...", "hypotheses": {...}}

Usage:
  python run_hypothesis_loop.py --research-folder docs/youra_research/20260304_scsl
  python run_hypothesis_loop.py --research-folder <path> --timeout 14400

Author: Anonymous
Version: 3.0
"""

import argparse
import json
import shutil
import signal
import subprocess
import sys
import time
from collections import deque
from datetime import datetime, timezone
from fnmatch import fnmatch
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# ============================================================
# Path Configuration
# ============================================================
SCRIPT_DIR = Path(__file__).parent
CACHE_DIR = SCRIPT_DIR / ".cache"
LOG_FILE = CACHE_DIR / "run_hypothesis_loop.log"

# Phase launcher scripts (same directory)
RUN_PHASE2C = SCRIPT_DIR / "run_phase2c.py"
RUN_PHASE3 = SCRIPT_DIR / "run_phase3.py"
RUN_PHASE4 = SCRIPT_DIR / "run_phase4.py"

# Default timeouts per phase (seconds)
PHASE_TIMEOUTS = {
    "phase2c": 3600,
    "phase3": 5400,
    "phase4": 720000,
}


def _utcnow() -> str:
    """Return current UTC time as ISO string."""
    return datetime.now(timezone.utc).isoformat()


def _normalize_gate(gate_val) -> dict:
    """Normalize gate field: str → dict with 'type' key.

    verification_state.yaml may store gate as either:
      - a string:  gate: MUST_WORK
      - a dict:    gate: {type: MUST_WORK, satisfied: null, result: null}
    This helper ensures downstream code always gets a dict.
    """
    if isinstance(gate_val, str):
        return {"type": gate_val, "satisfied": None, "result": None}
    if isinstance(gate_val, dict):
        return gate_val
    return {}


def log(message: str):
    """Log to file and stderr."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    print(entry, file=sys.stderr)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except Exception:
        pass


def output_result(result: dict):
    """Output structured result as JSON to stdout (last line)."""
    print(json.dumps(result, ensure_ascii=False))


# ============================================================
# Archive on Routing (deterministic, no Claude dependency)
# ============================================================

# Residual artifact indicators (from step-00-init.md Section 0.3.5)
_RESIDUAL_DIRS = [
    "h-*", "01_round_table", "papers", "paper_summaries", "paper", ".data_cache",
]
_RESIDUAL_FILES = [
    "verification_state.yaml", "02b_verification_plan*.md", "02_synthesis.yaml",
    "03_refinement.yaml", "03_refinement.md", "discussion_log.md",
    "phase2a_step_tasks.yaml", "paper_config.yaml", "045_validated_hypothesis.md",
    "stage1_context_gap*.yaml",
]
# Phase 2A routing preserves these (Phase 0 routing moves everything)
_PHASE2A_PRESERVE = [
    "00_brainstorm_session.md", "01_targeted_research*.md",
]


def archive_research_folder(
    research_folder: str,
    route_to: str,
    routed_hypothesis: str = "unknown",
    gate_result: str = "unknown",
) -> bool:
    """Archive residual artifacts before routing restart.

    For Phase 0 routing: moves ALL files except _archive/ itself.
    For Phase 2A routing: preserves brainstorm, targeted research, papers/.

    Returns True if archive was executed, False if skipped (no residuals).
    """
    rf = Path(research_folder)
    if not rf.is_dir():
        log(f"Archive: research folder does not exist: {research_folder}")
        return False

    # Check for residual artifacts
    has_residuals = False
    for pattern in _RESIDUAL_DIRS:
        if list(rf.glob(pattern)):
            has_residuals = True
            break
    if not has_residuals:
        for pattern in _RESIDUAL_FILES:
            if list(rf.glob(pattern)):
                has_residuals = True
                break
    if not has_residuals:
        log("Archive: no residual artifacts found — skipping")
        return False

    # Determine preserve list based on routing target
    if route_to in ("Phase 2A-Dialogue", "Phase 2A"):
        preserve = _PHASE2A_PRESERVE
    else:
        # Phase 0: move everything (only preserve _archive/ itself)
        preserve = []

    # Create timestamped archive subfolder
    ts = datetime.now().strftime("%Y%m%dT%H%M%S")
    archive_dir = rf / "_archive" / f"{ts}_routing_recovery"
    archive_dir.mkdir(parents=True, exist_ok=True)
    log(f"Archive: created _archive/{ts}_routing_recovery/")

    moved_count = 0
    for item in sorted(rf.iterdir()):
        name = item.name

        # Never move _archive/ itself
        if name == "_archive":
            continue

        # Check preserve list
        if any(fnmatch(name, p) for p in preserve):
            log(f"Archive: preserved {name}")
            continue

        # Move to archive
        dest = archive_dir / name
        try:
            shutil.move(str(item), str(dest))
            moved_count += 1
        except Exception as e:
            log(f"Archive: WARNING — failed to move {name}: {e}")

    # Create marker file
    marker = archive_dir / "_ARCHIVED.md"
    marker.write_text(
        f"# Archive Record\n\n"
        f"**Archived:** {ts}\n"
        f"**Route target:** {route_to}\n"
        f"**Triggered by:** {routed_hypothesis} ({gate_result})\n"
        f"**Reason:** Deterministic archive before routing restart\n"
        f"**Files moved:** {moved_count}\n",
        encoding="utf-8",
    )

    log(f"Archive: moved {moved_count} items to _archive/{ts}_routing_recovery/")
    return True


# ============================================================
# Verification State Management
# ============================================================
def _normalize_hypotheses_schema(state: dict, research_folder: str) -> dict:
    """Convert 'hypotheses' list schema to 'sub_hypotheses' dict schema if needed.

    Phase 2B sometimes generates verification_state.yaml with:
      hypotheses:          # list of dicts with 'id' key
        - id: "h-e1"
          type: EXISTENCE
          ...
    But the pipeline expects:
      sub_hypotheses:      # dict keyed by hypothesis id
        h-e1:
          type: EXISTENCE
          ...

    If conversion happens, the YAML file is updated in place.
    """
    known = {"READY", "IN_PROGRESS", "NOT_STARTED",
             "COMPLETED", "VALIDATED", "FAILED", "BLOCKED"}
    active = {"READY", "IN_PROGRESS"}
    terminal = {"COMPLETED", "VALIDATED", "FAILED", "BLOCKED"}

    def _nid(x):
        return str(x).strip().lower()

    def _is_entry(v):
        return isinstance(v, dict) and (
            "gate" in v or "status" in v or "type" in v or "id" in v
        )

    # Collect candidate entries. sub_hypotheses (may hold mid-run state) is
    # the base; missing fields are filled from the top-level 'hypotheses'
    # list, which usually carries gate/dependency info.
    sh = state.get("sub_hypotheses")
    from_list = {}
    hypotheses_list = state.get("hypotheses")
    if isinstance(hypotheses_list, list):
        for h in hypotheses_list:
            if isinstance(h, dict) and h.get("id"):
                from_list[_nid(h["id"])] = dict(h)

    entries = {}
    if isinstance(sh, dict) and sh and all(_is_entry(v) for v in sh.values()):
        for k, v in sh.items():
            k2 = _nid(k)
            merged = dict(from_list.get(k2, {}))
            merged.update(v)  # mid-run state in sub_hypotheses wins
            entries[k2] = merged
    else:
        if sh is not None:
            # Metadata block (schema_version/by_type/...) — stash it aside
            state["sub_hypotheses_meta"] = sh
            state.pop("sub_hypotheses", None)
        entries = from_list

    if not entries:
        return state  # nothing to normalize

    sub_hypotheses = {}
    for h_id, h in entries.items():
        h = dict(h)
        h.pop("id", None)

        # Normalize prerequisites: accept 'dependencies' alias, dict items
        raw_prereqs = h.get("prerequisites")
        if raw_prereqs is None:
            raw_prereqs = h.get("dependencies")
        h["prerequisites"] = [
            _nid(p.get("id") or p.get("hypothesis") or "") if isinstance(p, dict) else _nid(p)
            for p in (raw_prereqs or []) if p
        ]
        h.pop("dependencies", None)

        # Normalize gate: string → dict, ensure satisfied/result keys
        gate = h.get("gate")
        if isinstance(gate, str):
            h["gate"] = {"type": gate, "satisfied": None, "result": None}
        elif isinstance(gate, dict):
            h["gate"].setdefault("satisfied", None)
            h["gate"].setdefault("result", None)

        # Non-standard statuses (todo, PENDING, missing) → derive from prereqs
        if h.get("status") not in known:
            h["status"] = "READY" if not h["prerequisites"] else "NOT_STARTED"

        h.setdefault("experiment_design", {"status": "NOT_STARTED", "file": None})
        h.setdefault("implementation_planning", {"status": "NOT_STARTED"})
        h.setdefault("validation", {"status": "NOT_STARTED", "result": None})
        h.setdefault("version", 1)
        h.setdefault("completed", False)

        sub_hypotheses[h_id] = h

    # Stuck state: nothing active and nothing terminal means the loop could
    # never start — promote prerequisite-free NOT_STARTED entries to READY.
    statuses = {v["status"] for v in sub_hypotheses.values()}
    if not (statuses & active) and not (statuses & terminal):
        for v in sub_hypotheses.values():
            if v["status"] == "NOT_STARTED" and not v["prerequisites"]:
                v["status"] = "READY"

    if state.get("sub_hypotheses") == sub_hypotheses:
        return state  # already normalized

    state["sub_hypotheses"] = sub_hypotheses

    # Update statistics
    stats = state.setdefault("statistics", {})
    stats["total_sub_hypotheses"] = len(sub_hypotheses)

    # Save corrected file
    save_verification_state(research_folder, state)
    ready = [k for k, v in sub_hypotheses.items() if v["status"] in active]
    log(f"Saved normalized verification_state.yaml with {len(sub_hypotheses)} sub_hypotheses "
        f"(active: {', '.join(ready) or 'none'})")

    return state


def load_verification_state(research_folder: str) -> dict:
    """Load verification_state.yaml with YAML error recovery and schema normalization."""
    state_path = Path(research_folder) / "verification_state.yaml"
    if not state_path.exists():
        log(f"ERROR: verification_state.yaml not found at {state_path}")
        return {}
    with open(state_path, "r", encoding="utf-8") as f:
        content = f.read()
    try:
        state = yaml.safe_load(content) or {}
    except yaml.YAMLError as e:
        log(f"WARNING: YAML parse error, attempting recovery: {e}")
        markers = ["# SERENA MEMORY REFERENCES", "\nserena_memory:\n"]
        for marker in markers:
            idx = content.rfind(marker)
            if idx > 0:
                try:
                    truncated = content[:idx]
                    state = yaml.safe_load(truncated) or {}
                    if state.get("sub_hypotheses") or state.get("hypotheses"):
                        log(f"Recovered YAML by truncating at last '{marker.strip()}' (kept {idx} chars)")
                        break
                except yaml.YAMLError:
                    continue
        else:
            log("ERROR: Cannot parse verification_state.yaml even after recovery attempts")
            return {}

    # Normalize schema: hypotheses list → sub_hypotheses dict
    state = _normalize_hypotheses_schema(state, research_folder)

    return state


def save_verification_state(research_folder: str, state: dict):
    """Save verification_state.yaml."""
    state_path = Path(research_folder) / "verification_state.yaml"
    with open(state_path, "w", encoding="utf-8") as f:
        yaml.dump(state, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)


def get_ready_hypotheses(state: dict) -> list:
    """Get READY hypotheses sorted by dependency order.

    Returns: IN_PROGRESS first (resume), then READY in topological order.
    """
    sub_hyps = state.get("sub_hypotheses", {})
    if not sub_hyps:
        return []

    in_progress = []
    ready = []

    for h_id, h_data in sub_hyps.items():
        status = h_data.get("status", "NOT_STARTED")
        if status == "IN_PROGRESS":
            in_progress.append(h_id)
        elif status == "READY":
            ready.append(h_id)

    ready_sorted = _topological_sort(ready, sub_hyps)
    return in_progress + ready_sorted


def _normalize_prereqs(prereqs: list) -> list:
    """Ensure prerequisites is a flat list of string IDs (handles dict entries)."""
    result = []
    for p in prereqs:
        if isinstance(p, str):
            result.append(p)
        elif isinstance(p, dict):
            # Extract id/hypothesis_id from dict
            pid = p.get("id") or p.get("hypothesis_id") or p.get("name", "")
            if pid:
                result.append(str(pid))
        else:
            result.append(str(p))
    return result


def _topological_sort(hypothesis_ids: list, sub_hyps: dict) -> list:
    """Sort hypothesis IDs by prerequisite dependencies (Kahn's algorithm)."""
    if not hypothesis_ids:
        return []

    id_set = set(hypothesis_ids)
    in_degree = {h_id: 0 for h_id in hypothesis_ids}
    adj = {h_id: [] for h_id in hypothesis_ids}

    for h_id in hypothesis_ids:
        prereqs = _normalize_prereqs(sub_hyps.get(h_id, {}).get("prerequisites", []) or [])
        for prereq in prereqs:
            if prereq in id_set:
                in_degree[h_id] += 1
                adj[prereq].append(h_id)

    queue = deque(h_id for h_id in hypothesis_ids if in_degree[h_id] == 0)
    result = []

    while queue:
        h_id = queue.popleft()
        result.append(h_id)
        for dep in adj.get(h_id, []):
            in_degree[dep] -= 1
            if in_degree[dep] == 0:
                queue.append(dep)

    # Append remaining (circular deps — shouldn't happen)
    for h_id in hypothesis_ids:
        if h_id not in result:
            result.append(h_id)

    return result


def set_hypothesis_in_progress(research_folder: str, h_id: str):
    """Set hypothesis status to IN_PROGRESS before Phase execution."""
    state = load_verification_state(research_folder)
    sub_hyps = state.get("sub_hypotheses", {})

    if h_id in sub_hyps:
        sub_hyps[h_id]["status"] = "IN_PROGRESS"

        state.setdefault("workflow", {})["current_phase"] = "Phase 2C"
        state["workflow"]["next_action"] = f"Execute Phase 2C for {h_id}"
        state.setdefault("metadata", {})["last_updated"] = _utcnow()
        state.setdefault("history", []).append({
            "event": f"Hypothesis {h_id} set to IN_PROGRESS",
            "timestamp": _utcnow(),
            "phase": "Hypothesis Loop",
            "details": f"External loop starting Phase 2C → 3 → 4 for {h_id}",
        })

        stats = state.get("statistics", {})
        in_progress_count = sum(
            1 for h in sub_hyps.values() if h.get("status") == "IN_PROGRESS"
        )
        stats["in_progress_sub_hypotheses"] = in_progress_count

        save_verification_state(research_folder, state)
        log(f"Set {h_id} → IN_PROGRESS")
    else:
        log(f"WARNING: Hypothesis {h_id} not found in verification_state.yaml")


def verify_phase_completion(research_folder: str, h_id: str, phase_name: str) -> bool:
    """Verify that a Phase completed by reading verification_state.yaml (read-only)."""
    state = load_verification_state(research_folder)
    h_data = state.get("sub_hypotheses", {}).get(h_id, {})

    if phase_name == "2c":
        ed_status = h_data.get("experiment_design", {}).get("status", "NOT_STARTED")
        if ed_status == "COMPLETED":
            log(f"Phase 2C verified complete for {h_id}")
            return True
        brief_file = Path(research_folder) / h_id / "02c_experiment_brief.md"
        if brief_file.exists():
            log(f"Phase 2C: 02c_experiment_brief.md exists for {h_id} (status={ed_status})")
            return True
        log(f"Phase 2C NOT complete for {h_id}: experiment_design.status={ed_status}")
        return False

    elif phase_name == "3":
        ip_status = h_data.get("implementation_planning", {}).get("status", "NOT_STARTED")
        if ip_status == "COMPLETED":
            log(f"Phase 3 verified complete for {h_id}")
            return True
        h_folder = Path(research_folder) / h_id
        required_files = ["03_prd.md", "03_architecture.md", "03_logic.md", "03_config.md"]
        found = sum(1 for f in required_files if (h_folder / f).exists())
        if found >= 4:
            log(f"Phase 3: all 4 documents exist for {h_id} (status={ip_status})")
            return True
        log(f"Phase 3 NOT complete for {h_id}: {found}/4 files, status={ip_status}")
        return False

    elif phase_name == "4":
        val_status = h_data.get("validation", {}).get("status", "NOT_STARTED")
        if val_status in ("COMPLETED", "PASS", "FAIL", "PARTIAL"):
            log(f"Phase 4 verified complete for {h_id}: validation.status={val_status}")
            return True
        validation_md = Path(research_folder) / h_id / "04_validation.md"
        if not validation_md.exists():
            # Fallback: check _archive/ in case Claude archived the hypothesis folder directly
            archive_root = Path(research_folder) / "_archive"
            candidate = archive_root / h_id / "04_validation.md"
            if candidate.exists():
                validation_md = candidate
                log(f"Phase 4: 04_validation.md found in _archive/{h_id}/ — using archived copy")
            else:
                for ts_dir in sorted(archive_root.iterdir(), key=lambda d: d.name, reverse=True) if archive_root.exists() else []:
                    candidate = ts_dir / h_id / "04_validation.md"
                    if candidate.exists():
                        validation_md = candidate
                        log(f"Phase 4: 04_validation.md found in _archive/{ts_dir.name}/{h_id}/ — using archived copy")
                        break
        if validation_md.exists():
            log(f"Phase 4: 04_validation.md exists for {h_id} (status={val_status})")
            return True
        log(f"Phase 4 NOT complete for {h_id}: validation.status={val_status}")
        return False

    else:
        log(f"WARNING: Unknown phase name: {phase_name}")
        return False


def propagate_dependencies(research_folder: str, completed_h_id: str):
    """After successful validation: transition dependent hypotheses NOT_STARTED → READY."""
    state = load_verification_state(research_folder)
    sub_hyps = state.get("sub_hypotheses", {})
    changed = False

    for h_id, h_data in sub_hyps.items():
        prereqs = _normalize_prereqs(h_data.get("prerequisites", []) or [])
        if completed_h_id not in prereqs:
            continue

        all_satisfied = True
        for prereq in prereqs:
            prereq_data = sub_hyps.get(prereq, {})
            prereq_status = prereq_data.get("status", "NOT_STARTED")
            if prereq_status not in ("VALIDATED", "COMPLETED", "PASSED"):
                # SHOULD_WORK gate FAILED → don't block dependents (limitation recorded only)
                prereq_gate = _normalize_gate(prereq_data.get("gate", {}))
                if prereq_gate.get("type") == "SHOULD_WORK" and prereq_status == "FAILED":
                    continue  # treat as satisfied
                all_satisfied = False
                break
            # MUST_WORK FAIL: gate.satisfied=False → prerequisite NOT met
            if _normalize_gate(prereq_data.get("gate", {})).get("satisfied") is False:
                all_satisfied = False
                break

        if all_satisfied and h_data.get("status") == "NOT_STARTED":
            h_data["status"] = "READY"
            log(f"Propagated: {h_id} → READY (all prerequisites satisfied)")
            changed = True

    if changed:
        stats = state.get("statistics", {})
        validated_count = sum(
            1 for h in sub_hyps.values()
            if h.get("status") in ("VALIDATED", "COMPLETED")
        )
        stats["validated_sub_hypotheses"] = validated_count
        state.setdefault("metadata", {})["last_updated"] = _utcnow()
        save_verification_state(research_folder, state)


def all_processed(state: dict) -> bool:
    """Check if all hypotheses are in terminal states."""
    sub_hyps = state.get("sub_hypotheses", {})
    if not sub_hyps:
        return True
    terminal = {"VALIDATED", "COMPLETED", "PASSED", "FAILED", "BLOCKED", "SUPERSEDED", "LIMITATION_RECORDED"}
    return all(h.get("status", "NOT_STARTED") in terminal for h in sub_hyps.values())


def get_hypotheses_summary(state: dict) -> dict:
    """Get a summary of all hypothesis statuses for output."""
    sub_hyps = state.get("sub_hypotheses", {})
    summary = {}
    for h_id, h_data in sub_hyps.items():
        summary[h_id] = {
            "status": h_data.get("status", "NOT_STARTED"),
            "gate_type": _normalize_gate(h_data.get("gate", {})).get("type"),
            "gate_satisfied": _normalize_gate(h_data.get("gate", {})).get("satisfied"),
        }
    return summary


# ============================================================
# Phase Launcher Subprocess Calls
# ============================================================
def run_phase_script(script_path: Path, research_folder: str, h_id: str, timeout: int) -> int:
    """Run a Phase launcher script (run_phase2c/3/4.py) via subprocess.

    Streams stdout/stderr to our stderr (log stream).
    Returns the script's exit code.
    """
    cmd = [
        sys.executable,
        str(script_path),
        "--research-folder", research_folder,
        "--hypothesis", h_id,
        "--timeout", str(timeout),
    ]

    log(f"Running: {' '.join(cmd)}")
    start_time = time.time()

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        # Stream stderr (log output) to our stderr
        # stdout is captured for JSON parsing (run_phase4.py)
        stdout_lines = []

        import select as sel
        while True:
            reads = []
            if process.stdout:
                reads.append(process.stdout)
            if process.stderr:
                reads.append(process.stderr)
            if not reads:
                break

            ready, _, _ = sel.select(reads, [], [], 1.0)

            for stream in ready:
                line = stream.readline()
                if not line:
                    continue
                if stream == process.stderr:
                    sys.stderr.write(line)
                    sys.stderr.flush()
                elif stream == process.stdout:
                    stdout_lines.append(line)
                    sys.stderr.write(f"[stdout] {line}")
                    sys.stderr.flush()

            if process.poll() is not None:
                # Drain remaining
                if process.stdout:
                    for line in process.stdout:
                        stdout_lines.append(line)
                        sys.stderr.write(f"[stdout] {line}")
                        sys.stderr.flush()
                if process.stderr:
                    for line in process.stderr:
                        sys.stderr.write(line)
                        sys.stderr.flush()
                break

        exit_code = process.wait()
        elapsed = time.time() - start_time
        log(f"{script_path.name} exited with code {exit_code} after {elapsed:.0f}s")

        # Save stdout for later JSON parsing (run_phase4.py)
        if stdout_lines:
            stdout_file = CACHE_DIR / f"{script_path.stem}_{h_id}_stdout.txt"
            with open(stdout_file, "w", encoding="utf-8") as f:
                f.writelines(stdout_lines)

        return exit_code

    except FileNotFoundError:
        log(f"ERROR: Script not found: {script_path}")
        return 127
    except Exception as e:
        log(f"ERROR running {script_path.name}: {e}")
        return 1


def parse_phase4_gate_result(research_folder: str, h_id: str) -> dict:
    """Parse run_phase4.py's gate result from its stdout JSON (last line).

    Falls back to reading verification_state.yaml if stdout JSON is unavailable.
    """
    # Try to read from saved stdout
    stdout_file = CACHE_DIR / f"run_phase4_{h_id}_stdout.txt"
    if stdout_file.exists():
        try:
            with open(stdout_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            # Last non-empty line should be JSON
            for line in reversed(lines):
                line = line.strip()
                if line and line.startswith("{"):
                    result = json.loads(line)
                    log(f"Parsed Phase 4 gate JSON: {result}")
                    return result
        except (json.JSONDecodeError, Exception) as e:
            log(f"WARNING: Failed to parse Phase 4 stdout JSON: {e}")

    # Fallback: read from verification_state.yaml directly
    log("Falling back to verification_state.yaml for gate result")
    state = load_verification_state(research_folder)
    h_data = state.get("sub_hypotheses", {}).get(h_id, {})

    gate = _normalize_gate(h_data.get("gate", {}))
    gate_satisfied = gate.get("satisfied")
    h_status = h_data.get("status", "UNKNOWN")
    _val_raw = h_data.get("validation", {}).get("result") or ""
    if isinstance(_val_raw, dict):
        # LLM sometimes writes a metrics dict here — extract a verdict field
        _val_raw = (_val_raw.get("verdict") or _val_raw.get("result")
                    or _val_raw.get("status")
                    or ("PASS" if _val_raw.get("primary_pass") is True
                        or _val_raw.get("passed") is True else ""))
    validation_result = str(_val_raw or "").upper()
    _gate_result_raw = gate.get("result") or ""
    gate_result_field = (_gate_result_raw.get("verdict", "") if isinstance(_gate_result_raw, dict) else _gate_result_raw).upper()

    result = {
        "hypothesis": h_id,
        "gate_result": "UNKNOWN",
        "gate_type": gate.get("type", "UNKNOWN"),
        "route_to": None,
        "hypothesis_status": h_status,
        "research_folder": research_folder,
        "exit_code": -1,
    }

    # Priority: gate.satisfied > validation.result/gate.result > status
    # gate.satisfied=False means gate not met, even if status=COMPLETED
    if gate_satisfied is False:
        effective_result = validation_result or gate_result_field
        result["gate_result"] = "FAILED"  # Default

        # Read checkpoint for reflection outcome (Phase 4 step-06b sets this)
        checkpoint_path = Path(research_folder) / h_id / "04_checkpoint.yaml"
        reflection_outcome = None
        if checkpoint_path.exists():
            try:
                with open(checkpoint_path, "r", encoding="utf-8") as cf:
                    checkpoint = yaml.safe_load(cf) or {}
                reflection_outcome = checkpoint.get("reflection_outcome")
            except Exception:
                pass

        if reflection_outcome:
            # Step-06b ran and determined outcome
            ro = str(reflection_outcome).upper()
            if ro in ("ROUTED_TO_PHASE_0", "FAILED"):
                result["gate_result"] = "ROUTED_TO_PHASE_0"
                result["route_to"] = "Phase 0"
            elif ro in ("ROUTED_TO_PHASE_2A", "SUPERSEDED"):
                result["gate_result"] = "ROUTED_TO_PHASE_2A"
                result["route_to"] = "Phase 2A-Dialogue"
            elif ro in ("MODIFIED", "SELF_MODIFY"):
                result["gate_result"] = "SELF_MODIFY"
                result["route_to"] = "Phase 2C"
            elif ro == "LIMITATION_RECORDED":
                result["gate_result"] = "LIMITATION_RECORDED"
        # else: reflection_outcome is null — keeps default "FAILED"

    elif gate_satisfied is True and h_status in ("VALIDATED", "COMPLETED"):
        result["gate_result"] = "PASS"
    elif h_status == "FAILED":
        result["gate_result"] = "FAILED"
    elif h_status == "LIMITATION_RECORDED":
        result["gate_result"] = "LIMITATION_RECORDED"

    return result


# ============================================================
# Signal Handler
# ============================================================
def signal_handler(signum, _frame):
    """Handle SIGINT/SIGTERM gracefully."""
    sig_name = signal.Signals(signum).name
    log(f"Received {sig_name} — shutting down hypothesis loop")
    sys.exit(128 + signum)


# ============================================================
# Main Loop
# ============================================================
def main_loop(research_folder: str, timeout: int) -> int:
    """Main hypothesis for-loop.

    For each READY hypothesis:
      1. run_phase2c.py → verify completion
      2. run_phase3.py  → verify completion
      3. run_phase4.py  → parse gate result JSON
      4. Gate decision:
         - PASS: propagate dependencies, next hypothesis
         - ROUTED (MUST_WORK): output JSON, exit code 2
         - FAILED (SHOULD_WORK): continue (Phase 4 recorded limitation)
         - FAILED (MUST_WORK): continue (Phase 4 already cascaded dependents)
    """
    iteration = 0

    while True:
        iteration += 1
        log(f"\n{'#' * 60}")
        log(f"Hypothesis Loop — Iteration {iteration}")
        log(f"{'#' * 60}")

        state = load_verification_state(research_folder)
        if not state:
            log("ERROR: Cannot load verification_state.yaml — aborting")
            output_result({
                "status": "ERROR",
                "reason": "Cannot load verification_state.yaml",
                "research_folder": research_folder,
            })
            return 1

        queue = get_ready_hypotheses(state)

        if not queue:
            if all_processed(state):
                log("All hypotheses processed — loop complete")
                state.setdefault("workflow", {})["sub_hypotheses_complete"] = True
                state["workflow"]["hypothesis_loop_completed_at"] = _utcnow()
                state["workflow"]["current_phase"] = "Phase 5"
                state["workflow"]["status"] = "COMPLETED"
                state["workflow"]["next_action"] = "Proceed to Phase 5 (if applicable) or Phase 6"
                state["workflow"]["phase4_completed_at"] = _utcnow()
                state.setdefault("metadata", {})["last_updated"] = _utcnow()
                save_verification_state(research_folder, state)
                output_result({
                    "status": "COMPLETE",
                    "research_folder": research_folder,
                    "hypotheses": get_hypotheses_summary(state),
                })
                return 0
            else:
                # Recovery: a crash may have interrupted dependency propagation
                # right after a hypothesis completed — re-propagate from all
                # completed hypotheses and retry the queue before declaring
                # anything blocked.
                _completed = [
                    _h for _h, _hd in state.get("sub_hypotheses", {}).items()
                    if _hd.get("status") in ("VALIDATED", "COMPLETED")
                ]
                if _completed:
                    for _h in _completed:
                        propagate_dependencies(research_folder, _h)
                    if get_ready_hypotheses(load_verification_state(research_folder)):
                        log("Recovered READY hypotheses after re-propagating "
                            f"completed dependencies ({', '.join(_completed)}) — retrying")
                        continue

                # Mark NOT_STARTED hypotheses as BLOCKED if prerequisites can never be met
                sub_hyps = state.get("sub_hypotheses", {})
                blocked_any = False
                for h_id, h_data in sub_hyps.items():
                    if h_data.get("status") != "NOT_STARTED":
                        continue
                    prereqs = _normalize_prereqs(h_data.get("prerequisites", []) or [])
                    for prereq in prereqs:
                        prereq_data = sub_hyps.get(prereq, {})
                        prereq_status = prereq_data.get("status", "NOT_STARTED")
                        prereq_gate = _normalize_gate(prereq_data.get("gate", {}))
                        # Prerequisite failed or gate not satisfied → can never proceed
                        if prereq_status in ("FAILED", "BLOCKED", "SUPERSEDED"):
                            h_data["status"] = "BLOCKED"
                            h_data["blocked_by"] = prereq
                            h_data["blocked_reason"] = f"Prerequisite {prereq} status={prereq_status}"
                            log(f"Marked {h_id} as BLOCKED (prerequisite {prereq} is {prereq_status})")
                            blocked_any = True
                            break
                        if prereq_gate.get("satisfied") is False:
                            h_data["status"] = "BLOCKED"
                            h_data["blocked_by"] = prereq
                            h_data["blocked_reason"] = f"Prerequisite {prereq} gate not satisfied"
                            log(f"Marked {h_id} as BLOCKED (prerequisite {prereq} gate.satisfied=false)")
                            blocked_any = True
                            break

                if blocked_any:
                    state.setdefault("metadata", {})["last_updated"] = _utcnow()
                    save_verification_state(research_folder, state)

                # Re-check after blocking
                if all_processed(state):
                    log("All hypotheses processed (after blocking unreachable) — loop complete")
                    state.setdefault("workflow", {})["sub_hypotheses_complete"] = True
                    state["workflow"]["hypothesis_loop_completed_at"] = _utcnow()
                    state["workflow"]["current_phase"] = "Phase 5"
                    state["workflow"]["status"] = "COMPLETED"
                    state["workflow"]["next_action"] = "Proceed to Phase 5 (if applicable) or Phase 6"
                    state["workflow"]["phase4_completed_at"] = _utcnow()
                    state.setdefault("metadata", {})["last_updated"] = _utcnow()
                    save_verification_state(research_folder, state)
                    output_result({
                        "status": "COMPLETE",
                        "research_folder": research_folder,
                        "hypotheses": get_hypotheses_summary(state),
                    })
                    return 0

                log("No READY hypotheses and not all processed — cannot proceed")
                output_result({
                    "status": "BLOCKED",
                    "reason": "No READY hypotheses, remaining are BLOCKED or NOT_STARTED with unmet prerequisites",
                    "research_folder": research_folder,
                    "hypotheses": get_hypotheses_summary(state),
                })
                return 3

        log(f"Hypothesis queue: {queue}")

        for h_id in queue:
            log(f"\n{'=' * 60}")
            log(f"Processing hypothesis: {h_id}")
            log(f"{'=' * 60}")

            # Set hypothesis IN_PROGRESS
            set_hypothesis_in_progress(research_folder, h_id)

            # Determine which phases to run (resume support)
            state = load_verification_state(research_folder)
            h_data = state.get("sub_hypotheses", {}).get(h_id, {})

            phases_to_run = []
            ed_status = h_data.get("experiment_design", {}).get("status", "NOT_STARTED")
            ip_status = h_data.get("implementation_planning", {}).get("status", "NOT_STARTED")
            val_status = h_data.get("validation", {}).get("status", "NOT_STARTED")

            if ed_status != "COMPLETED":
                phases_to_run.append("phase2c")
            if ip_status != "COMPLETED":
                phases_to_run.append("phase3")
            if val_status not in ("COMPLETED", "PASS", "FAIL", "PARTIAL"):
                phases_to_run.append("phase4")

            if not phases_to_run:
                log(f"All phases already completed for {h_id} — checking gate result")
                gate_info = parse_phase4_gate_result(research_folder, h_id)
                if gate_info.get("gate_result") == "PASS":
                    # Fix: ensure hypothesis status is VALIDATED (not stuck in IN_PROGRESS)
                    state = load_verification_state(research_folder)
                    sub_hyps = state.get("sub_hypotheses", {})
                    if h_id in sub_hyps and sub_hyps[h_id].get("status") not in ("VALIDATED", "COMPLETED"):
                        sub_hyps[h_id]["status"] = "VALIDATED"
                        state.setdefault("metadata", {})["last_updated"] = _utcnow()
                        save_verification_state(research_folder, state)
                        log(f"Fixed {h_id} status: IN_PROGRESS → VALIDATED (gate PASS)")
                    propagate_dependencies(research_folder, h_id)
                continue

            log(f"Phases to run for {h_id}: {phases_to_run}")

            # ---- Phase 2C ----
            if "phase2c" in phases_to_run:
                phase_timeout = min(timeout, PHASE_TIMEOUTS["phase2c"])
                exit_code = run_phase_script(RUN_PHASE2C, research_folder, h_id, phase_timeout)

                if not verify_phase_completion(research_folder, h_id, "2c"):
                    log(f"Phase 2C did not complete for {h_id} (exit_code={exit_code})")
                    log(f"Skipping remaining phases for {h_id}")
                    continue

            # ---- Phase 3 ----
            if "phase3" in phases_to_run:
                phase_timeout = min(timeout, PHASE_TIMEOUTS["phase3"])
                exit_code = run_phase_script(RUN_PHASE3, research_folder, h_id, phase_timeout)

                if not verify_phase_completion(research_folder, h_id, "3"):
                    log(f"Phase 3 did not complete for {h_id} (exit_code={exit_code})")
                    log(f"Skipping remaining phases for {h_id}")
                    continue

            # ---- Phase 4 ----
            if "phase4" in phases_to_run:
                phase_timeout = min(timeout, PHASE_TIMEOUTS["phase4"])
                exit_code = run_phase_script(RUN_PHASE4, research_folder, h_id, phase_timeout)

                if not verify_phase_completion(research_folder, h_id, "4"):
                    log(f"Phase 4 did not complete for {h_id} (exit_code={exit_code})")
                    continue

            # ---- Gate Result Processing ----
            gate_info = parse_phase4_gate_result(research_folder, h_id)
            gate_result = gate_info.get("gate_result", "UNKNOWN")
            gate_type = gate_info.get("gate_type", "MUST_WORK")
            log(f"Gate result for {h_id}: {gate_result} (gate_type={gate_type})")

            if gate_result == "PASS":
                log(f"PASS: {h_id} validated — propagating dependencies")
                propagate_dependencies(research_folder, h_id)

            elif gate_result in ("ROUTED_TO_PHASE_0", "ROUTED_TO_PHASE_2A"):
                if gate_type == "SHOULD_WORK":
                    # SHOULD_WORK does not route — only records a limitation
                    log(f"SHOULD_WORK {h_id}: routing ignored — continuing")
                    propagate_dependencies(research_folder, h_id)
                else:
                    # MUST_WORK routing: archive → emit JSON → stop the loop
                    route_target = gate_info.get("route_to", "Phase 0")
                    log(f"ROUTING REQUIRED: {h_id} → {route_target}")

                    archive_research_folder(
                        research_folder, route_target, h_id, gate_result,
                    )

                    output_result({
                        "status": "ROUTED",
                        "route_to": route_target,
                        "hypothesis": h_id,
                        "gate_result": gate_result,
                        "gate_type": gate_type,
                        "research_folder": research_folder,
                        "hypotheses": get_hypotheses_summary(
                            load_verification_state(research_folder)
                        ),
                    })
                    return 2

            elif gate_result == "SELF_MODIFY":
                # Phase 4 reflection determined SELF_MODIFY → new version enters Phase 2C
                # step-06b should have: (1) set original to COMPLETED, (2) added new version as READY
                # Defensive: ensure original is terminal so it's not re-queued
                state = load_verification_state(research_folder)
                sub_hyps = state.get("sub_hypotheses", {})
                if h_id in sub_hyps and sub_hyps[h_id].get("status") not in ("COMPLETED", "SUPERSEDED", "FAILED"):
                    sub_hyps[h_id]["status"] = "COMPLETED"
                    state.setdefault("metadata", {})["last_updated"] = _utcnow()
                    save_verification_state(research_folder, state)
                    log(f"SELF_MODIFY: Forced {h_id} status → COMPLETED (was not terminal)")

                # Fallback: if step-06b did NOT create a new version as READY,
                # create one ourselves so the loop doesn't dead-end.
                state = load_verification_state(research_folder)
                sub_hyps = state.get("sub_hypotheses", {})
                original = sub_hyps.get(h_id, {})
                mod_attempt = original.get("modification_attempt", 0) + 1
                new_h_id = f"{h_id}-v{mod_attempt + 1}"

                # Check if any new version already exists and is READY
                new_version_exists = any(
                    hid.startswith(f"{h_id}-v") and hd.get("status") in ("READY", "IN_PROGRESS", "NOT_STARTED")
                    for hid, hd in sub_hyps.items()
                )
                # Also check if original was reset to READY (in-place modification)
                if original.get("status") == "READY":
                    new_version_exists = True

                if not new_version_exists:
                    # Create new version by cloning original with incremented modification_attempt
                    import copy
                    new_hyp = copy.deepcopy(original)
                    new_hyp["status"] = "READY"
                    new_hyp["modification_attempt"] = mod_attempt
                    new_hyp["version"] = mod_attempt + 1
                    new_hyp["gate"]["satisfied"] = None
                    new_hyp["gate"]["result"] = None
                    new_hyp["gate"]["failed_checks"] = []
                    new_hyp.pop("blocked_by", None)
                    new_hyp.pop("blocked_reason", None)
                    new_hyp["validation"] = {"status": "NOT_STARTED", "result": None, "key_findings": []}
                    new_hyp["experiment_design"] = {"status": "NOT_STARTED", "file": None}
                    new_hyp.setdefault("implementation_planning", {})["status"] = "NOT_STARTED"
                    new_hyp.setdefault("data_setup", {})["status"] = "NOT_STARTED"
                    new_hyp["completed"] = False
                    new_hyp["completed_at"] = None
                    new_hyp.setdefault("superseded", {})["superseded_by"] = None

                    # Mark original as superseded
                    original.setdefault("superseded", {})["superseded_by"] = new_h_id
                    original["superseded"]["superseded_at"] = _utcnow()
                    original["superseded"]["superseded_reason"] = "SELF_MODIFY fallback — new version created by hypothesis loop"
                    original["superseded"]["partial_results_preserved"] = True

                    sub_hyps[new_h_id] = new_hyp
                    state.setdefault("metadata", {})["last_updated"] = _utcnow()
                    save_verification_state(research_folder, state)
                    log(f"SELF_MODIFY FALLBACK: Created {new_h_id} as READY (step-06b did not create new version)")
                else:
                    log(f"SELF_MODIFY: New version already exists or original reset to READY — no fallback needed")

                log(f"SELF_MODIFY: {h_id} — new version will be picked up in next loop iteration")
                # Don't propagate — the new version needs to pass first

            elif gate_result in ("FAILED", "LIMITATION_RECORDED"):
                if gate_type == "SHOULD_WORK":
                    # SHOULD_WORK failure: do not block dependents, continue to next hypothesis
                    log(f"SHOULD_WORK {h_id}: FAILED — limitation recorded, dependents NOT blocked")
                    propagate_dependencies(research_folder, h_id)
                else:
                    # MUST_WORK failure: archive → emit routing JSON → stop the loop
                    log(f"MUST_WORK {h_id}: FAILED — routing to Phase 0")

                    archive_research_folder(
                        research_folder, "Phase 0", h_id, gate_result,
                    )

                    output_result({
                        "status": "ROUTED",
                        "route_to": "Phase 0",
                        "hypothesis": h_id,
                        "gate_result": gate_result,
                        "gate_type": gate_type,
                        "reason": "MUST_WORK gate FAILED",
                        "research_folder": research_folder,
                        "hypotheses": get_hypotheses_summary(
                            load_verification_state(research_folder)
                        ),
                    })
                    return 2

            elif gate_result == "UNKNOWN":
                # gate_result=UNKNOWN means checkpoint/verification_state was archived by Claude
                # before run_phase4.py could read it — treat as ROUTED_TO_PHASE_0
                log(f"UNKNOWN gate result for {h_id} — treating as ROUTED_TO_PHASE_0 (files likely archived)")
                if gate_type != "SHOULD_WORK":
                    archive_research_folder(research_folder, "Phase 0", h_id, gate_result)
                    output_result({
                        "status": "ROUTED",
                        "route_to": "Phase 0",
                        "hypothesis": h_id,
                        "gate_result": gate_result,
                        "gate_type": gate_type,
                        "research_folder": research_folder,
                        "hypotheses": {},
                    })
                    return 2

            else:
                log(f"Unknown gate result: {gate_result} for {h_id}")

        # Queue exhausted — check if new hypotheses became READY
        state = load_verification_state(research_folder)
        new_queue = get_ready_hypotheses(state)

        if not new_queue:
            if all_processed(state):
                log("All hypotheses processed — loop complete")
                state.setdefault("workflow", {})["sub_hypotheses_complete"] = True
                state["workflow"]["hypothesis_loop_completed_at"] = _utcnow()
                state["workflow"]["current_phase"] = "Phase 5"
                state["workflow"]["status"] = "COMPLETED"
                state["workflow"]["next_action"] = "Proceed to Phase 5 (if applicable) or Phase 6"
                state["workflow"]["phase4_completed_at"] = _utcnow()
                state.setdefault("metadata", {})["last_updated"] = _utcnow()
                save_verification_state(research_folder, state)
                output_result({
                    "status": "COMPLETE",
                    "research_folder": research_folder,
                    "hypotheses": get_hypotheses_summary(state),
                })
                return 0
            else:
                log("No more READY hypotheses — loop finished with incomplete state")
                output_result({
                    "status": "INCOMPLETE",
                    "reason": "Some hypotheses BLOCKED or FAILED, no more READY",
                    "research_folder": research_folder,
                    "hypotheses": get_hypotheses_summary(state),
                })
                return 3
        else:
            log(f"New READY hypotheses found: {new_queue} — continuing loop")
            continue


# ============================================================
# CLI Entry Point
# ============================================================
def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Hypothesis Loop — Run Phase 2C → 3 → 4 for each hypothesis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exit codes:
  0 — All hypotheses processed successfully
  1 — Error (cannot load state, missing files)
  2 — Routing required (check stdout JSON for route_to)
  3 — Incomplete (some hypotheses BLOCKED/FAILED)

Examples:
  %(prog)s --research-folder docs/youra_research/20260304_scsl
  %(prog)s --research-folder /absolute/path --timeout 14400
        """,
    )

    parser.add_argument("--research-folder", type=str, required=True,
                        help="Path to research folder containing verification_state.yaml")
    parser.add_argument("--timeout", type=int, default=14400,
                        help="Max runtime per Phase in seconds (default: 14400 = 4 hours)")

    return parser.parse_args()


def main():
    args = parse_args()

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    research_folder = str(Path(args.research_folder).resolve())

    # Validate
    if not Path(research_folder).exists():
        log(f"ERROR: Research folder does not exist: {research_folder}")
        output_result({"status": "ERROR", "reason": f"Research folder not found: {research_folder}"})
        sys.exit(1)

    state_path = Path(research_folder) / "verification_state.yaml"
    if not state_path.exists():
        log(f"ERROR: verification_state.yaml not found in {research_folder}")
        output_result({"status": "ERROR", "reason": "verification_state.yaml not found"})
        sys.exit(1)

    # Validate phase scripts exist
    for script_name, script_path in [
        ("run_phase2c.py", RUN_PHASE2C),
        ("run_phase3.py", RUN_PHASE3),
        ("run_phase4.py", RUN_PHASE4),
    ]:
        if not script_path.exists():
            log(f"ERROR: {script_name} not found at {script_path}")
            output_result({"status": "ERROR", "reason": f"{script_name} not found"})
            sys.exit(1)

    # Load initial state and show summary
    state = load_verification_state(research_folder)
    sub_hyps = state.get("sub_hypotheses", {})
    queue = get_ready_hypotheses(state)

    log("=" * 60)
    log("Hypothesis Loop Launcher starting")
    log(f"  Research folder: {research_folder}")
    log(f"  Total hypotheses: {len(sub_hyps)}")
    log(f"  READY/IN_PROGRESS: {len(queue)}")
    log(f"  Timeout per phase: {args.timeout}s")
    log(f"  Hypothesis queue: {queue}")

    for h_id, h_data in sub_hyps.items():
        status = h_data.get("status", "NOT_STARTED")
        gate_type = _normalize_gate(h_data.get("gate", {})).get("type", "?")
        prereqs = h_data.get("prerequisites", []) or []
        log(f"    {h_id}: status={status}, gate={gate_type}, prereqs={prereqs}")

    log("=" * 60)

    if not queue:
        # Recovery: a crash may have interrupted dependency propagation right
        # after a hypothesis completed — re-propagate from all completed
        # hypotheses and retry the queue before giving up.
        _completed = [
            _h for _h, _hd in sub_hyps.items()
            if _hd.get("status") in ("VALIDATED", "COMPLETED")
        ]
        if _completed:
            for _h in _completed:
                propagate_dependencies(research_folder, _h)
            state = load_verification_state(research_folder)
            sub_hyps = state.get("sub_hypotheses", {})
            queue = get_ready_hypotheses(state)
            if queue:
                log("Recovered READY hypotheses after re-propagating completed "
                    f"dependencies ({', '.join(_completed)}): {queue}")

    if not queue:
        if all_processed(state):
            log("All hypotheses already processed — nothing to do")
            output_result({
                "status": "COMPLETE",
                "research_folder": research_folder,
                "hypotheses": get_hypotheses_summary(state),
            })
            sys.exit(0)
        else:
            log("No READY or IN_PROGRESS hypotheses — cannot start loop")
            output_result({
                "status": "BLOCKED",
                "reason": "No READY or IN_PROGRESS hypotheses",
                "research_folder": research_folder,
                "hypotheses": get_hypotheses_summary(state),
            })
            sys.exit(3)

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run the main loop
    exit_code = main_loop(research_folder, args.timeout)

    log("Hypothesis Loop Launcher complete")
    log("=" * 60)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
