#!/usr/bin/env python3
"""R8 "clean disable" audit for the VSA-IC ablation (ws4 spec section 4 R8).

Audits every Claude session transcript in .cache/ for tool calls that
Read/Edit/Write any of the three VSA target files. A single hit means the
ablation was NOT cleanly applied ("silent no-op" — worse than a bad result)
and the run must be flagged FAIL.

Two transcript formats are supported:
  1. stream-json (JSONL events — what shadow-mode sessions log): tool_use
     content blocks are inspected DIRECTLY (name + input), which is precise
     and immune to rendering changes. This is the authoritative path.
  2. plain text (legacy/fallback): regex over "Read(...file...)" renderings.
     NOTE: `claude -p` text mode logs only the final message, so this path
     cannot prove anything by itself — shadow mode therefore forces
     stream-json logging (see run_phase*.py _run_claude).

Bash-mediated access (command string mentions a target file) is reported as
a WARNING, not a failure — path strings also legitimately appear in echoed
prompts; warnings are for human review.

Usage:
  python ablation_audit.py [--cache-dir .cache] [--exempt PATTERN ...] [--json]
  python ablation_audit.py --clean-disable-report --research-folder <path>
Exit codes: 0 = clean, 1 = violations found.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

TARGET_FILES = ["verification_state.yaml", "04_checkpoint.yaml", "03_tasks.yaml"]

# File-touching tools whose use on a target file is a hard violation.
_VIOLATION_TOOLS = {"Read", "Edit", "MultiEdit", "Write", "NotebookEdit"}
# Tool-call renderings in plain-text transcripts (legacy fallback).
_TOOL_CALL_RE = r"(?:Read|Edit|MultiEdit|Write|NotebookEdit)"


def _iter_stream_tool_uses(content: str):
    """Yield (tool_name, input_dict) for every tool_use event in a
    stream-json transcript. Yields nothing for non-stream content."""
    for line in content.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            evt = json.loads(line)
        except ValueError:
            continue
        if not isinstance(evt, dict):
            continue
        msg = evt.get("message") if isinstance(evt.get("message"), dict) else evt
        blocks = msg.get("content")
        if not isinstance(blocks, list):
            continue
        for block in blocks:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                yield (block.get("name") or "", block.get("input") or {})


def _looks_stream_json(content: str) -> bool:
    head = content.lstrip()[:1]
    return head == "{"


def audit_clean_disable(cache_dir, exempt_patterns=None,
                        glob_pattern: str = "phase*_*.log"):
    """Return (passed, violations, warnings).

    violations: tool calls (Read/Edit/Write/MultiEdit/NotebookEdit) on target
    files (hard FAIL). warnings: Bash access mentioning a target file.
    """
    cache_dir = Path(cache_dir)
    exempt_patterns = exempt_patterns or []
    violations: list[str] = []
    warnings: list[str] = []

    for log_file in sorted(cache_dir.glob(glob_pattern)):
        if any(p in log_file.name for p in exempt_patterns):
            continue
        try:
            content = log_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        if _looks_stream_json(content):
            # Authoritative path: inspect tool_use events directly.
            for name, tool_input in _iter_stream_tool_uses(content):
                if name in _VIOLATION_TOOLS:
                    # Violation = the tool's TARGET PATH is a VSA file. Matching
                    # the whole input blob would flag Writes of unrelated files
                    # whose *content* merely mentions a VSA filename (5 of the
                    # 6 "violations" in the 2026-07-09 dl4c audit were such
                    # false positives).
                    paths = [tool_input.get(k) for k in
                             ("file_path", "notebook_path", "path")]
                    for raw in paths:
                        if not isinstance(raw, str):
                            continue
                        basename = raw.rstrip("/").rsplit("/", 1)[-1]
                        if basename in TARGET_FILES or ".ablation_shadow/" in raw:
                            blob = json.dumps(tool_input, ensure_ascii=False)
                            violations.append(
                                f"{log_file.name}: {name}({blob[:180]})")
                            break
                elif name == "Bash":
                    blob = json.dumps(tool_input, ensure_ascii=False)
                    if any(target in blob for target in TARGET_FILES):
                        warnings.append(
                            f"{log_file.name}: Bash({blob[:180]})")
        else:
            # Legacy text fallback (cannot see tool calls in `claude -p`
            # text mode — kept for completeness only).
            for lineno, line in enumerate(content.splitlines(), 1):
                for target in TARGET_FILES:
                    if target not in line:
                        continue
                    esc = re.escape(target)
                    if re.search(rf"{_TOOL_CALL_RE}\([^)]*{esc}", line):
                        violations.append(
                            f"{log_file.name}:{lineno}: {line.strip()[:200]}")
                    elif re.search(rf"Bash\([^)]*{esc}", line):
                        warnings.append(
                            f"{log_file.name}:{lineno}: {line.strip()[:200]}")

    return (len(violations) == 0, violations, warnings)


def clean_disable_report(research_folder, cache_dir,
                         exempt_patterns=None) -> dict:
    """Machine-check the ws4 spec section-5 clean-disable conditions.

    1. R8 audit: 0 violations                              → automated
    2. no hypothesis ended gate_result=UNKNOWN             → automated
       (shadow state: gate.satisfied null AND terminal status = relay failure)
    3. no SPURIOUS ROUTED_TO_PHASE_0 (spurious ⇔ the routed hypothesis has
       gate.satisfied null rather than explicitly false)   → automated heuristic
    4. pipeline produced paper/06_paper_final.md           → automated
    5. 4-judge scoring — external, reported as MANUAL
    """
    rf = Path(research_folder)
    report: dict = {"conditions": {}, "passed": None}

    passed, violations, warnings = audit_clean_disable(
        cache_dir, exempt_patterns=exempt_patterns)
    report["conditions"]["1_r8_audit"] = {
        "passed": passed, "violations": violations, "warnings": len(warnings)}

    unknown, spurious = [], []
    try:
        import yaml
        shadow_vs = rf / ".ablation_shadow" / "verification_state.yaml"
        vs_path = shadow_vs if shadow_vs.exists() else rf / "verification_state.yaml"
        state = yaml.safe_load(vs_path.read_text(encoding="utf-8")) or {}
        for h_id, h in (state.get("sub_hypotheses") or {}).items():
            if not isinstance(h, dict):
                continue
            gate = h.get("gate") or {}
            satisfied = gate.get("satisfied") if isinstance(gate, dict) else None
            status = str(h.get("status") or "")
            if satisfied is None and status in ("FAILED", "BLOCKED", "SUPERSEDED"):
                unknown.append(h_id)
            ro = str(h.get("reflection_outcome") or "")
            if "ROUTED_TO_PHASE_0" in ro and satisfied is None:
                spurious.append(h_id)
    except Exception as e:
        report["conditions"]["state_read_error"] = str(e)
    report["conditions"]["2_no_unknown_gate"] = {
        "passed": not unknown, "unknown_hypotheses": unknown}
    report["conditions"]["3_no_spurious_routing"] = {
        "passed": not spurious, "spurious_hypotheses": spurious,
        "heuristic": "gate.satisfied null (relay failure) vs false (legit)"}

    paper = rf / "paper" / "06_paper_final.md"
    report["conditions"]["4_paper_produced"] = {
        "passed": paper.exists() and paper.stat().st_size > 0 if paper.exists() else False}

    report["conditions"]["5_judge_scoring"] = {
        "passed": None, "note": "MANUAL — run 4-judge scoring externally"}

    auto = [c for k, c in report["conditions"].items()
            if isinstance(c, dict) and c.get("passed") is not None]
    report["passed"] = all(c["passed"] for c in auto)
    return report


def write_audit_report(cache_dir, passed: bool, violations, warnings,
                       out_name: str = "ablation_audit.json"):
    report = {
        "audited_at": datetime.now().isoformat(),
        "passed": passed,
        "violation_count": len(violations),
        "violations": violations,
        "warning_count": len(warnings),
        "warnings": warnings,
        "target_files": TARGET_FILES,
    }
    out = Path(cache_dir) / out_name
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False),
                   encoding="utf-8")
    return out


def main():
    parser = argparse.ArgumentParser(description="VSA-IC R8 clean-disable audit")
    parser.add_argument("--cache-dir", default=str(Path(__file__).parent / ".cache"))
    parser.add_argument("--exempt", action="append", default=[],
                        help="Log-name substring to exempt (repeatable)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--clean-disable-report", action="store_true",
                        help="Full ws4 section-5 clean-disable report")
    parser.add_argument("--research-folder", default=None,
                        help="Required with --clean-disable-report")
    args = parser.parse_args()

    if args.clean_disable_report:
        if not args.research_folder:
            parser.error("--clean-disable-report requires --research-folder")
        report = clean_disable_report(args.research_folder, args.cache_dir,
                                      exempt_patterns=args.exempt)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        sys.exit(0 if report["passed"] else 1)

    passed, violations, warnings = audit_clean_disable(
        args.cache_dir, exempt_patterns=args.exempt)
    write_audit_report(args.cache_dir, passed, violations, warnings)

    if args.json:
        print(json.dumps({"passed": passed, "violations": violations,
                          "warnings": warnings}, ensure_ascii=False))
    else:
        print(f"R8 audit: {'PASS' if passed else 'FAIL'} "
              f"({len(violations)} violations, {len(warnings)} warnings)")
        for v in violations:
            print(f"  VIOLATION {v}")
        for w in warnings[:20]:
            print(f"  warning   {w}")
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
