#!/usr/bin/env python3
"""
Pipeline Artifact Verifier — Independent Filesystem Verification

Verifies that pipeline hypothesis folders contain actual implementation artifacts
matching what verification_state.yaml claims. Detects fabricated/simulated results
where the LLM skipped experiment execution but marked hypotheses as PASS.

Key features:
- Phase-by-phase artifact checking (2C, 3, 4 docs, 4 experiment)
- gate_result whitelist validation (rejects PASS_THEORETICAL, etc.)
- Snapshot-based diff tracking (what changed since last check)
- Experiment quality checks (log lines, forbidden patterns, non-null metrics)
- CLI and programmatic usage

Usage:
    # CLI — human-readable report
    python pipeline_artifact_verifier.py --research-folder docs/youra_research

    # CLI — JSON output (for hook integration)
    python pipeline_artifact_verifier.py --json --research-folder docs/youra_research

    # Programmatic
    from pipeline_artifact_verifier import PipelineArtifactVerifier
    v = PipelineArtifactVerifier("docs/youra_research")
    result = v.verify()

Author: Anonymous
"""

import argparse
import glob
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

try:
    import yaml
except ImportError:
    yaml = None


# ─── Default configuration (overridden by auto_responder_config.yaml) ────────

DEFAULT_PHASE_ARTIFACTS = {
    "phase_2c": {
        "required_files": ["02c_experiment_brief.md"],
        "required_dirs": [],
        "description": "Experiment brief",
    },
    "phase_3": {
        "required_files": [
            "03_prd.md",
            "03_architecture.md",
            "03_logic.md",
            "03_config.md",
        ],
        "required_dirs": [],
        "description": "Implementation planning (PRD + Architecture)",
    },
    "phase_4_docs": {
        "required_files": [
            "04_validation.md",
            "04_checkpoint.yaml",
        ],
        "required_dirs": [],
        "description": "Phase 4 documentation",
    },
    "phase_4_experiment": {
        "required_files": ["experiment_results.json"],
        "required_dirs": ["code/"],
        "code_file_check": True,
        "description": "Phase 4 experiment execution",
    },
}

DEFAULT_VALID_GATE_RESULTS: Set[str] = {"PASS", "PARTIAL", "FAIL"}

DEFAULT_EXPERIMENT_QUALITY = {
    "min_log_lines": 20,
    "forbidden_log_patterns": ["command not found", "No module named"],
    "require_non_null_metrics": True,
}


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _load_yaml(path: str) -> Optional[dict]:
    """Load a YAML file, returning None on failure."""
    if yaml is None:
        # Fallback: try basic parsing if PyYAML not available
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ─── Main Class ──────────────────────────────────────────────────────────────

class PipelineArtifactVerifier:
    """
    Verifies pipeline artifacts against claimed state in verification_state.yaml.

    Parameters
    ----------
    research_folder : str
        Path to the research folder (e.g. docs/youra_research).
    config : dict, optional
        Configuration dict (artifact_verification section from auto_responder_config.yaml).
        If None, uses defaults.
    """

    def __init__(self, research_folder: str, config: Optional[Dict[str, Any]] = None):
        self.research_folder = os.path.abspath(research_folder)
        self.config = config or {}

        # Merge config with defaults
        self.phase_artifacts = self._build_phase_artifacts()
        self.valid_gate_results = set(
            self.config.get("valid_gate_results", DEFAULT_VALID_GATE_RESULTS)
        )
        self.experiment_quality = {
            **DEFAULT_EXPERIMENT_QUALITY,
            **self.config.get("experiment_quality", {}),
        }

        # Snapshot file location
        snapshot_name = self.config.get("snapshot_file", ".artifact_snapshot.json")
        hooks_dir = os.path.dirname(os.path.abspath(__file__))
        self.snapshot_path = os.path.join(hooks_dir, snapshot_name)

    def _build_phase_artifacts(self) -> Dict[str, dict]:
        """Build phase artifacts from config, falling back to defaults."""
        cfg_phases = self.config.get("phase_artifacts", {})
        if not cfg_phases:
            return dict(DEFAULT_PHASE_ARTIFACTS)

        result = {}
        for phase_key, default_spec in DEFAULT_PHASE_ARTIFACTS.items():
            if phase_key in cfg_phases:
                cfg_spec = cfg_phases[phase_key]
                result[phase_key] = {
                    "required_files": cfg_spec.get("required_files", default_spec.get("required_files", [])),
                    "required_dirs": cfg_spec.get("required_dirs", default_spec.get("required_dirs", [])),
                    "code_file_check": cfg_spec.get("code_file_check", default_spec.get("code_file_check", False)),
                    "description": cfg_spec.get("description", default_spec.get("description", "")),
                }
            else:
                result[phase_key] = dict(default_spec)
        return result

    # ── State Parsing ────────────────────────────────────────────────────

    def _parse_verification_state(self) -> Dict[str, Any]:
        """Parse verification_state.yaml and extract hypothesis claims."""
        state_file = os.path.join(self.research_folder, "verification_state.yaml")
        if not os.path.exists(state_file):
            return {"exists": False, "hypotheses": [], "pipeline": {}}

        data = _load_yaml(state_file)
        if not data:
            return {"exists": False, "hypotheses": [], "pipeline": {}}

        pipeline_info = data.get("pipeline", {})
        raw_hypotheses = data.get("hypotheses", [])
        gate_results = data.get("gate_results", {})

        hypotheses = []
        if isinstance(raw_hypotheses, list):
            for h in raw_hypotheses:
                if not isinstance(h, dict):
                    continue
                h_id = h.get("id", "")
                # Get gate_result from the hypothesis itself or from top-level gate_results
                h_gate = h.get("gate_result", "")
                if not h_gate and h_id in gate_results:
                    gr = gate_results[h_id]
                    h_gate = gr.get("decision", "") if isinstance(gr, dict) else str(gr)

                hypotheses.append({
                    "id": h_id,
                    "status": h.get("status", ""),
                    "gate_result": h_gate,
                    "order": h.get("order", 0),
                    "type": h.get("type", ""),
                    "dependencies": h.get("dependencies", []),
                    "folder": f"h-{h_id.lower().replace('-', '-')}".lower()
                        if h_id else "",
                })

        return {
            "exists": True,
            "hypotheses": hypotheses,
            "pipeline": pipeline_info,
            "gate_results": gate_results,
        }

    # ── Snapshot Management ──────────────────────────────────────────────

    def _load_snapshot(self) -> Dict[str, Any]:
        """Load previous artifact snapshot."""
        if not os.path.exists(self.snapshot_path):
            return {}
        try:
            with open(self.snapshot_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_snapshot(self, snapshot: Dict[str, Any]) -> None:
        """Save current artifact snapshot."""
        try:
            os.makedirs(os.path.dirname(self.snapshot_path), exist_ok=True)
            with open(self.snapshot_path, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, indent=2)
        except Exception:
            pass  # Non-critical — snapshot is informational

    # ── Filesystem Scanning ──────────────────────────────────────────────

    def _scan_hypothesis_folder(self, h_id: str) -> Dict[str, Any]:
        """Scan a hypothesis folder for artifacts."""
        # Map hypothesis ID to folder name
        folder_name = f"h-{h_id.lower().replace('h-', '')}"
        folder_path = os.path.join(self.research_folder, folder_name)

        scan = {
            "folder_exists": os.path.isdir(folder_path),
            "folder_path": folder_path,
            "files_found": [],
            "dirs_found": [],
            "code_files": [],
            "experiment_results_size": 0,
            "log_lines": 0,
            "log_issues": [],
            "metrics_non_null": False,
        }

        if not scan["folder_exists"]:
            return scan

        # List all files in the folder (non-recursive for top-level)
        for entry in os.listdir(folder_path):
            entry_path = os.path.join(folder_path, entry)
            if os.path.isfile(entry_path):
                scan["files_found"].append(entry)
            elif os.path.isdir(entry_path):
                scan["dirs_found"].append(entry + "/")

        # Find code files recursively
        for ext in [".py", ".ipynb"]:
            code_matches = glob.glob(
                os.path.join(folder_path, "**", f"*{ext}"), recursive=True
            )
            for cf in code_matches:
                scan["code_files"].append(os.path.relpath(cf, folder_path))

        # Check experiment_results.json size
        results_path = os.path.join(folder_path, "experiment_results.json")
        if os.path.exists(results_path):
            scan["experiment_results_size"] = os.path.getsize(results_path)

        # Check experiment_log.txt
        log_path = os.path.join(folder_path, "experiment_log.txt")
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    log_content = f.read()
                log_lines = log_content.strip().split("\n")
                scan["log_lines"] = len(log_lines)

                # Check for forbidden patterns
                forbidden = self.experiment_quality.get("forbidden_log_patterns", [])
                for pattern in forbidden:
                    if pattern.lower() in log_content.lower():
                        scan["log_issues"].append(f"Found forbidden pattern: '{pattern}'")
            except Exception:
                pass

        # Check 04_checkpoint.yaml metrics
        ckpt_path = os.path.join(folder_path, "04_checkpoint.yaml")
        if os.path.exists(ckpt_path):
            ckpt_data = _load_yaml(ckpt_path)
            if ckpt_data and isinstance(ckpt_data, dict):
                metrics = ckpt_data.get("metrics", {})
                if isinstance(metrics, dict):
                    for v in metrics.values():
                        if v is not None:
                            scan["metrics_non_null"] = True
                            break

        return scan

    # ── Phase Artifact Checks ────────────────────────────────────────────

    def _check_phase_artifacts(
        self, h_id: str, scan: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Check each phase's required artifacts against the scan.

        Returns dict keyed by phase_key, each with:
            - passed: bool
            - present: list of present files/dirs
            - missing: list of missing files/dirs
            - issues: list of quality issues
        """
        results = {}
        for phase_key, spec in self.phase_artifacts.items():
            phase_result = {
                "passed": True,
                "present": [],
                "missing": [],
                "issues": [],
                "description": spec.get("description", phase_key),
            }

            # Check required files
            for req_file in spec.get("required_files", []):
                if req_file in scan["files_found"]:
                    phase_result["present"].append(req_file)
                else:
                    phase_result["missing"].append(req_file)
                    phase_result["passed"] = False

            # Check required dirs
            for req_dir in spec.get("required_dirs", []):
                dir_name = req_dir.rstrip("/") + "/"
                if dir_name in scan["dirs_found"]:
                    phase_result["present"].append(req_dir)
                else:
                    phase_result["missing"].append(req_dir)
                    phase_result["passed"] = False

            # Code file check (Phase 4 experiment)
            if spec.get("code_file_check", False):
                if scan["code_files"]:
                    phase_result["present"].append(
                        f"code files: {', '.join(scan['code_files'][:3])}"
                    )
                else:
                    phase_result["missing"].append("*.py files in code/ directory")
                    phase_result["passed"] = False

            # Experiment quality checks (Phase 4 experiment only)
            if phase_key == "phase_4_experiment":
                # experiment_results.json must not be empty
                if "experiment_results.json" in scan["files_found"]:
                    if scan["experiment_results_size"] <= 2:  # Empty JSON: {} or []
                        phase_result["issues"].append(
                            "experiment_results.json is empty or trivial"
                        )
                        phase_result["passed"] = False

                # Log quality
                if scan["log_lines"] > 0:
                    min_lines = self.experiment_quality.get("min_log_lines", 20)
                    if scan["log_lines"] < min_lines:
                        phase_result["issues"].append(
                            f"experiment_log.txt has only {scan['log_lines']} lines (min: {min_lines})"
                        )
                    for issue in scan["log_issues"]:
                        phase_result["issues"].append(issue)
                        phase_result["passed"] = False

                # Metrics check
                if self.experiment_quality.get("require_non_null_metrics", True):
                    if not scan["metrics_non_null"]:
                        phase_result["issues"].append(
                            "04_checkpoint.yaml: all metrics are null"
                        )
                        # Note: this is a warning, not necessarily a hard failure
                        # because some phases may legitimately have null metrics before execution

            results[phase_key] = phase_result

        return results

    # ── Gate Result Validation ───────────────────────────────────────────

    def _validate_gate_result(self, gate_result: str) -> Dict[str, Any]:
        """Validate a gate_result value against the whitelist."""
        if not gate_result:
            return {"valid": False, "reason": "No gate_result set"}
        if gate_result in self.valid_gate_results:
            return {"valid": True, "reason": ""}
        return {
            "valid": False,
            "reason": f"Invalid gate_result: '{gate_result}' "
                      f"(allowed: {', '.join(sorted(self.valid_gate_results))})",
        }

    # ── Resume Point Computation ────────────────────────────────────────

    def _compute_resume_point(
        self, h_id: str, phase_results: Dict[str, Dict[str, Any]], scan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine where to restart execution for a failed hypothesis.

        Logic (earliest missing phase wins):
            - phase_2c missing  → resume_from: "phase_2c"
            - phase_3 missing   → resume_from: "phase_3"
            - phase_4 missing   → resume_from: "phase_4"
              (If phase_3 artifacts exist, Phase 4 MUST reference them for code generation)

        Returns dict with:
            resume_from: str (phase key to restart from)
            has_phase3_artifacts: bool (Phase 3 docs available for code gen)
            phase3_files: list of existing Phase 3 files
            instruction: str (human-readable re-execution instruction)
        """
        # Check phases in order
        phase_order = ["phase_2c", "phase_3", "phase_4_docs", "phase_4_experiment"]

        resume_from = None
        for pk in phase_order:
            pr = phase_results.get(pk, {})
            if not pr.get("passed", True):
                resume_from = pk
                break

        if resume_from is None:
            # All phases passed but gate is invalid — just need re-gating
            return {
                "resume_from": "gate_only",
                "has_phase3_artifacts": True,
                "phase3_files": phase_results.get("phase_3", {}).get("present", []),
                "instruction": f"{h_id}: Re-evaluate gate with valid result (PASS/PARTIAL/FAIL only).",
            }

        has_phase3 = phase_results.get("phase_3", {}).get("passed", False)
        phase3_files = phase_results.get("phase_3", {}).get("present", [])

        if resume_from == "phase_2c":
            return {
                "resume_from": "phase_2c",
                "has_phase3_artifacts": has_phase3,
                "phase3_files": phase3_files,
                "instruction": f"{h_id}: Restart from Phase 2C (experiment brief missing).",
            }
        elif resume_from == "phase_3":
            return {
                "resume_from": "phase_3",
                "has_phase3_artifacts": False,
                "phase3_files": [],
                "instruction": (
                    f"{h_id}: Restart from Phase 3 (implementation planning docs missing). "
                    f"Must produce 03_prd.md, 03_architecture.md, 03_logic.md, 03_config.md."
                ),
            }
        else:
            # phase_4_docs or phase_4_experiment
            instruction = (
                f"{h_id}: Restart from Phase 4 (code/experiment execution missing)."
            )
            if has_phase3:
                instruction += (
                    f" Phase 3 artifacts EXIST ({', '.join(phase3_files)}) — "
                    f"use these as the implementation spec for code generation. "
                    f"Do NOT skip code generation."
                )
            else:
                instruction = (
                    f"{h_id}: Restart from Phase 3 (no Phase 3 docs to base code on). "
                    f"Must produce 03_prd.md, 03_architecture.md, 03_logic.md, 03_config.md, "
                    f"THEN generate code in Phase 4."
                )
            return {
                "resume_from": "phase_3" if not has_phase3 else "phase_4",
                "has_phase3_artifacts": has_phase3,
                "phase3_files": phase3_files,
                "instruction": instruction,
            }

    # ── Diff Computation ─────────────────────────────────────────────────

    def _compute_diff(
        self, prev_snapshot: Dict[str, Any], current_hypotheses: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compute diff between previous snapshot and current state."""
        prev_hyps = prev_snapshot.get("hypotheses", {})
        diff = {
            "new_hypotheses": [],
            "changed_hypotheses": [],
            "unchanged_hypotheses": [],
            "new_files": {},
            "removed_files": {},
        }

        for h_id, current in current_hypotheses.items():
            if h_id not in prev_hyps:
                diff["new_hypotheses"].append(h_id)
                diff["new_files"][h_id] = current.get("files_found", [])
                continue

            prev = prev_hyps[h_id]
            prev_files = set(prev.get("files_found", []))
            curr_files = set(current.get("files_found", []))
            prev_status = prev.get("claimed_status", "")
            curr_status = current.get("claimed_status", "")

            new_files = curr_files - prev_files
            removed = prev_files - curr_files

            if new_files or removed or prev_status != curr_status:
                diff["changed_hypotheses"].append(h_id)
                if new_files:
                    diff["new_files"][h_id] = list(new_files)
                if removed:
                    diff["removed_files"][h_id] = list(removed)
            else:
                diff["unchanged_hypotheses"].append(h_id)

        return diff

    # ── Main Verify ──────────────────────────────────────────────────────

    def verify(self) -> Dict[str, Any]:
        """
        Run full verification and return results.

        Returns dict with:
            passed, fabrication_detected, hypotheses_checked, hypotheses_passed,
            hypotheses_failed, invalid_gates, missing_artifacts,
            diff_from_previous, report
        """
        now = _now_iso()

        # 1. Parse verification_state.yaml
        state = self._parse_verification_state()
        if not state["exists"]:
            return {
                "passed": False,
                "fabrication_detected": False,
                "hypotheses_checked": 0,
                "hypotheses_passed": 0,
                "hypotheses_failed": 0,
                "invalid_gates": [],
                "missing_artifacts": {},
                "diff_from_previous": {},
                "report": "No verification_state.yaml found — nothing to verify.",
                # Backwards-compatible fields for auto_responder_full.py
                "verified": False,
                "error": "No verification_state.yaml",
                "state_claims_complete": False,
                "total_hypotheses_claimed": 0,
                "total_hypothesis_folders": 0,
                "verified_count": 0,
            }

        # 2. Load previous snapshot
        prev_snapshot = self._load_snapshot()

        # 3. Check each hypothesis
        hypotheses = state["hypotheses"]
        pipeline = state["pipeline"]

        per_hypothesis = {}
        invalid_gates = []
        missing_artifacts = {}
        total_checked = 0
        total_passed = 0
        total_failed = 0
        fabrication_detected = False

        current_snapshot_hyps = {}

        for h in hypotheses:
            h_id = h["id"]
            if not h_id:
                continue

            total_checked += 1

            # Scan filesystem
            scan = self._scan_hypothesis_folder(h_id)

            # Check phase artifacts
            phase_results = self._check_phase_artifacts(h_id, scan)

            # Validate gate result
            gate_check = self._validate_gate_result(h["gate_result"])
            if not gate_check["valid"]:
                invalid_gates.append({
                    "id": h_id,
                    "gate_result": h["gate_result"],
                    "reason": gate_check["reason"],
                })

            # Determine overall hypothesis pass/fail
            # A hypothesis passes if: folder exists AND all phases pass AND gate is valid
            h_passed = (
                scan["folder_exists"]
                and all(pr["passed"] for pr in phase_results.values())
                and gate_check["valid"]
            )

            if h_passed:
                total_passed += 1
            else:
                total_failed += 1
                # Collect missing artifacts
                h_missing = []
                if not scan["folder_exists"]:
                    h_missing.append(f"h-{h_id.lower()} folder")
                for pk, pr in phase_results.items():
                    h_missing.extend(pr["missing"])
                    h_missing.extend(pr["issues"])
                if not gate_check["valid"]:
                    h_missing.append(gate_check["reason"])
                missing_artifacts[h_id] = h_missing

            # Check for fabrication: status claims PASS/COMPLETED but artifacts missing
            claimed_pass = h["status"] in ("PASS", "COMPLETED", "VALIDATED", "COMPLETE")
            has_critical_missing = not scan["folder_exists"] or any(
                not pr["passed"] for pk, pr in phase_results.items()
                if pk in ("phase_2c", "phase_3")  # At minimum 2C and 3 should exist
            )
            if claimed_pass and has_critical_missing:
                fabrication_detected = True

            # Compute resume point for failed hypotheses
            resume_point = None
            if not h_passed:
                resume_point = self._compute_resume_point(h_id, phase_results, scan)

            per_hypothesis[h_id] = {
                "claimed_status": h["status"],
                "gate_result": h["gate_result"],
                "gate_valid": gate_check["valid"],
                "folder_exists": scan["folder_exists"],
                "phase_results": phase_results,
                "scan": scan,
                "passed": h_passed,
                "resume_point": resume_point,
            }

            # Build snapshot entry
            current_snapshot_hyps[h_id] = {
                "claimed_status": h["status"],
                "claimed_phase": pipeline.get("current_phase", ""),
                "files_found": scan["files_found"],
                "dirs_found": scan["dirs_found"],
                "code_files": scan["code_files"],
            }

        # 4. Compute diff
        diff = self._compute_diff(prev_snapshot, current_snapshot_hyps)

        # 5. Save new snapshot
        new_snapshot = {
            "timestamp": now,
            "hypotheses": current_snapshot_hyps,
            "pipeline_status": pipeline.get("status", ""),
        }
        self._save_snapshot(new_snapshot)

        # 6. Build per-hypothesis resume instructions
        resume_instructions = {}
        for h_id, info in per_hypothesis.items():
            if info["resume_point"]:
                resume_instructions[h_id] = info["resume_point"]

        # 7. Build report
        report = self._build_report(
            now=now,
            prev_timestamp=prev_snapshot.get("timestamp", "(none)"),
            per_hypothesis=per_hypothesis,
            invalid_gates=invalid_gates,
            missing_artifacts=missing_artifacts,
            resume_instructions=resume_instructions,
            diff=diff,
            total_checked=total_checked,
            total_passed=total_passed,
            total_failed=total_failed,
            fabrication_detected=fabrication_detected,
        )

        overall_passed = total_failed == 0 and len(invalid_gates) == 0

        # Count hypothesis folders for backwards compatibility
        h_folder_pattern = os.path.join(self.research_folder, "h-*/")
        h_folders = glob.glob(h_folder_pattern)

        return {
            "passed": overall_passed,
            "fabrication_detected": fabrication_detected,
            "hypotheses_checked": total_checked,
            "hypotheses_passed": total_passed,
            "hypotheses_failed": total_failed,
            "invalid_gates": [ig["id"] for ig in invalid_gates],
            "missing_artifacts": missing_artifacts,
            "resume_instructions": resume_instructions,
            "diff_from_previous": diff,
            "report": report,
            # Backwards-compatible fields for auto_responder_full.py
            "verified": overall_passed,
            "state_claims_complete": pipeline.get("status") in (
                "COMPLETED", "PAPER_GENERATED", "Pipeline Complete"
            ),
            "total_hypotheses_claimed": total_checked,
            "total_hypothesis_folders": len(h_folders),
            "verified_count": total_passed,
            "details": {
                h_id: {
                    "missing_files": missing_artifacts.get(h_id, []),
                    "has_code": bool(info["scan"]["code_files"]),
                    "code_files_found": info["scan"]["code_files"][:5],
                }
                for h_id, info in per_hypothesis.items()
            },
        }

    # ── Report Formatting ────────────────────────────────────────────────

    def _build_report(
        self,
        now: str,
        prev_timestamp: str,
        per_hypothesis: Dict[str, Any],
        invalid_gates: List[dict],
        missing_artifacts: Dict[str, List[str]],
        resume_instructions: Dict[str, Dict[str, Any]],
        diff: Dict[str, Any],
        total_checked: int,
        total_passed: int,
        total_failed: int,
        fabrication_detected: bool,
    ) -> str:
        lines = []
        sep = "=" * 60
        lines.append(sep)
        lines.append("PIPELINE ARTIFACT DIFF REPORT")
        lines.append(sep)
        lines.append(f"Timestamp: {now}")
        lines.append(f"Previous snapshot: {prev_timestamp}")
        lines.append("")

        # Per-hypothesis details
        for h_id, info in sorted(per_hypothesis.items()):
            status_str = info["claimed_status"]
            gate_str = info["gate_result"]
            lines.append(f"--- {h_id} (claimed: {status_str}) ---")

            for phase_key, pr in info["phase_results"].items():
                phase_label = pr["description"]
                for item in pr["present"]:
                    lines.append(f"  {phase_label}: OK {item}")
                for item in pr["missing"]:
                    lines.append(f"  {phase_label}: MISSING {item}")
                for issue in pr.get("issues", []):
                    lines.append(f"  {phase_label}: WARNING {issue}")

            if info["gate_valid"]:
                lines.append(f"  Gate: OK gate_result='{gate_str}'")
            else:
                lines.append(f"  Gate: INVALID gate_result: '{gate_str}'")

            if not info["folder_exists"]:
                lines.append(f"  Folder: MISSING (no h-{h_id.lower()} directory)")

            lines.append("")

        # Diff summary
        if diff.get("new_files") or diff.get("removed_files"):
            lines.append("--- DIFF FROM PREVIOUS SNAPSHOT ---")
            for h_id, files in diff.get("new_files", {}).items():
                if files:
                    lines.append(f"  {h_id}: +{len(files)} new files: {', '.join(files)}")
            for h_id, files in diff.get("removed_files", {}).items():
                if files:
                    lines.append(f"  {h_id}: -{len(files)} removed files: {', '.join(files)}")
            if diff.get("unchanged_hypotheses"):
                lines.append(
                    f"  Unchanged: {', '.join(diff['unchanged_hypotheses'])}"
                )
            lines.append("")

        # Resume instructions (per-hypothesis re-execution plan)
        if resume_instructions:
            lines.append("--- RE-EXECUTION PLAN (per hypothesis) ---")
            for h_id, ri in sorted(resume_instructions.items()):
                lines.append(f"  {ri['instruction']}")
                if ri.get("has_phase3_artifacts") and ri["resume_from"] == "phase_4":
                    lines.append(
                        f"    -> Phase 3 docs available: {', '.join(ri['phase3_files'])}"
                    )
                    lines.append(
                        f"    -> MUST use these as implementation spec for code generation"
                    )
            lines.append("")

        # Summary
        lines.append(sep)
        if total_failed == 0 and not invalid_gates:
            lines.append("RESULT: VERIFICATION PASSED")
            lines.append(f"  - {total_passed}/{total_checked} hypotheses fully verified")
        else:
            lines.append("RESULT: VERIFICATION FAILED")
            if total_failed > 0:
                lines.append(
                    f"  - {total_failed}/{total_checked} hypotheses have missing artifacts"
                )
            if invalid_gates:
                lines.append(
                    f"  - {len(invalid_gates)}/{total_checked} hypotheses have invalid gate_results"
                )
            if fabrication_detected:
                lines.append(
                    "  - Fabrication detected: state claims COMPLETED but artifacts missing"
                )
        lines.append(sep)

        return "\n".join(lines)


# ─── CLI Entry Point ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Pipeline Artifact Verifier — check hypothesis folder artifacts"
    )
    parser.add_argument(
        "--research-folder",
        required=True,
        help="Path to research folder (e.g. docs/youra_research)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output JSON instead of human-readable report",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to auto_responder_config.yaml (optional)",
    )
    args = parser.parse_args()

    # Load config if provided
    config = {}
    if args.config:
        full_config = _load_yaml(args.config)
        if full_config:
            config = full_config.get("artifact_verification", {})
    else:
        # Try default location
        hooks_dir = os.path.dirname(os.path.abspath(__file__))
        default_config = os.path.join(hooks_dir, "auto_responder_config.yaml")
        if os.path.exists(default_config):
            full_config = _load_yaml(default_config)
            if full_config:
                config = full_config.get("artifact_verification", {})

    verifier = PipelineArtifactVerifier(args.research_folder, config)
    result = verifier.verify()

    if args.json_output:
        # JSON output — remove non-serializable items, keep it clean
        json_result = {
            k: v for k, v in result.items()
            if k != "report"  # report is included as text
        }
        json_result["report_text"] = result.get("report", "")
        print(json.dumps(json_result, indent=2))
    else:
        print(result["report"])

    # Exit code: 0 = passed, 1 = failed
    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
