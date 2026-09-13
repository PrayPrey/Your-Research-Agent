#!/usr/bin/env python3
"""
Phase Output Verifier — Shared verification module for run_phase*.py launchers.

Each phase launcher calls verify_and_write_json(phase, research_folder) just before
sys.exit(). Results are written to .cache/phase*_output_verify.json.

JSON schema:
{
  "phase": "phase0",
  "research_folder": "/path/to/folder",
  "verified_at": "2026-03-06T02:30:00",
  "claude_exit_code": 0,
  "passed": true,
  "checks": [
    {"file": "00_brainstorm_session.md", "exists": true, "size": 15420,
     "no_unfilled": true, "contains_phase1_input": true, "ok": true},
    ...
  ],
  "errors": []
}
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).parent
CACHE_DIR = SCRIPT_DIR / ".cache"


def _load_max_retries() -> int:
    """Load MAX_RETRIES from auto_responder_config.yaml (pipeline_retry.max_retries)."""
    try:
        import yaml
        cfg_path = SCRIPT_DIR / "auto_responder_config.yaml"
        with open(cfg_path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
        return int(cfg.get("pipeline_retry", {}).get("max_retries", 2))
    except Exception:
        return 2


# ============================================================
# Internal helpers
# ============================================================

def _check_yaml_field(
    yaml_path: Path,
    field_path: str,
    expected_value: str,
) -> Dict[str, Any]:
    """
    Check that a specific field in a YAML file equals expected_value.

    field_path uses dot notation, e.g. "sub_hypotheses.h-e1.experiment_design.status".
    Returns a check entry dict compatible with _format_verify_summary().
    """
    entry: Dict[str, Any] = {
        "file": str(yaml_path.name),
        "field": field_path,
        "expected": expected_value,
        "ok": False,
    }

    if not yaml_path.exists():
        entry["exists"] = False
        return entry

    entry["exists"] = True

    try:
        import yaml
        with open(yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception as e:
        entry["yaml_error"] = str(e)
        return entry

    # Traverse dot-separated path
    parts = field_path.split(".")
    node = data
    for part in parts:
        if not isinstance(node, dict) or part not in node:
            entry["actual"] = None
            entry["field_missing"] = True
            return entry
        node = node[part]

    entry["actual"] = str(node) if node is not None else "null"
    entry["ok"] = (str(node).lower() == expected_value.lower())
    return entry


def _check_yaml_field_not(
    yaml_path: Path,
    field_path: str,
    rejected_value: str,
) -> Dict[str, Any]:
    """
    Check that a specific field in a YAML file does NOT equal rejected_value.

    Useful for Phase 4 where validation.status can be COMPLETED, FAIL, PARTIAL, etc.
    — any value other than NOT_STARTED (or null) means the phase actually ran.

    field_path uses dot notation, e.g. "sub_hypotheses.h-e1.validation.status".
    Returns a check entry dict compatible with _format_verify_summary().
    """
    entry: Dict[str, Any] = {
        "file": str(yaml_path.name),
        "field": field_path,
        "rejected": rejected_value,
        "ok": False,
    }

    if not yaml_path.exists():
        entry["exists"] = False
        return entry

    entry["exists"] = True

    try:
        import yaml
        with open(yaml_path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception as e:
        entry["yaml_error"] = str(e)
        return entry

    parts = field_path.split(".")
    node = data
    for part in parts:
        if not isinstance(node, dict) or part not in node:
            entry["actual"] = None
            entry["field_missing"] = True
            return entry
        node = node[part]

    entry["actual"] = str(node) if node is not None else "null"
    entry["ok"] = (entry["actual"] != rejected_value)
    return entry


def _check(
    folder: Path,
    rel_path: str,
    check_unfilled: bool = False,
    check_contains: Optional[str] = None,
) -> Dict[str, Any]:
    fpath = folder / rel_path
    entry: Dict[str, Any] = {"file": rel_path, "ok": False}

    if not fpath.exists():
        entry["exists"] = False
        return entry

    entry["exists"] = True
    entry["size"] = fpath.stat().st_size

    if entry["size"] == 0:
        entry["empty"] = True
        return entry

    if check_unfilled or check_contains:
        text = fpath.read_text(encoding="utf-8", errors="ignore")
        if check_unfilled:
            entry["no_unfilled"] = "{{UNFILLED:" not in text
            if not entry["no_unfilled"]:
                return entry
        if check_contains:
            key = f"contains_{check_contains.replace(' ', '_').lower()[:30]}"
            entry[key] = check_contains in text
            if not entry[key]:
                return entry

    entry["ok"] = True
    return entry


def _check_phase4_reflection_outcome_when_gate_failed(
    vs_path: Path,
    folder: Path,
    h_id: str,
) -> Dict[str, Any]:
    """Require step-06b reflection outcome when Phase 4 gate is not satisfied."""
    entry: Dict[str, Any] = {
        "file": "04_checkpoint.yaml",
        "field": "reflection_outcome",
        "ok": False,
    }

    if not vs_path.exists():
        entry["detail"] = "verification_state.yaml missing"
        return entry

    try:
        import yaml
        with open(vs_path, encoding="utf-8") as f:
            state = yaml.safe_load(f) or {}
    except Exception as e:
        entry["detail"] = f"verification_state.yaml error: {e}"
        return entry

    h_data = state.get("sub_hypotheses", {}).get(h_id, {})
    gate = h_data.get("gate", {})
    gate_satisfied = gate.get("satisfied") if isinstance(gate, dict) else None
    gate_failed = gate_satisfied is False or str(gate_satisfied).lower() == "false"
    if not gate_failed:
        entry["ok"] = True
        entry["detail"] = "gate.satisfied is not false; reflection_outcome not required"
        return entry

    checkpoint_path = folder / "04_checkpoint.yaml"
    if not checkpoint_path.exists():
        entry["detail"] = "gate.satisfied=false but 04_checkpoint.yaml missing"
        return entry

    try:
        import yaml
        with open(checkpoint_path, encoding="utf-8") as f:
            checkpoint = yaml.safe_load(f) or {}
    except Exception as e:
        entry["detail"] = f"04_checkpoint.yaml error: {e}"
        return entry

    reflection_outcome = checkpoint.get("reflection_outcome")
    if reflection_outcome:
        entry["ok"] = True
        entry["actual"] = str(reflection_outcome)
        return entry

    entry["actual"] = "null"
    entry["detail"] = (
        "gate.satisfied=false but reflection_outcome is null; "
        "Phase 4 step-06b reflection was skipped or not persisted"
    )
    return entry


# ============================================================
# Per-phase check definitions
# ============================================================

def _checks_phase0(folder: Path) -> List[Dict[str, Any]]:
    return [
        _check(folder, "00_brainstorm_session.md",
               check_unfilled=True, check_contains="<phase1-input>"),
    ]


def _checks_phase1(folder: Path) -> List[Dict[str, Any]]:
    return [
        _check(folder, "01_targeted_research.md", check_unfilled=True),
        _check(folder, "01_targeted_research_full.md", check_unfilled=True),
    ]


def _checks_phase2a(folder: Path) -> List[Dict[str, Any]]:
    return [
        _check(folder, "03_refinement.yaml"),
        _check(folder, "02_synthesis.yaml"),
        _check(folder, "01_round_table/final_opinions.yaml"),
        _check(folder, "03_refinement.md"),
        _check(folder, "discussion_log.md", check_contains="Final Assessments"),
    ]


def _checks_phase2b(folder: Path) -> List[Dict[str, Any]]:
    return [
        _check(folder, "verification_state.yaml"),
        _check(folder, "02b_verification_plan.md", check_unfilled=True),
        _check_verification_state_schema(folder),
    ]


def _check_verification_state_schema(folder: Path) -> Dict[str, Any]:
    """Check that verification_state.yaml has 'sub_hypotheses' as a dict (not 'hypotheses' list).

    Phase 2B must generate sub_hypotheses as a dict keyed by hypothesis ID.
    If it generates 'hypotheses' as a list instead, the hypothesis loop will fail.
    """
    entry: Dict[str, Any] = {
        "file": "verification_state.yaml [sub_hypotheses schema]",
        "ok": False,
    }

    vs_path = folder / "verification_state.yaml"
    if not vs_path.exists():
        entry["exists"] = False
        entry["detail"] = "FILE MISSING"
        return entry

    entry["exists"] = True

    try:
        import yaml
        with open(vs_path, encoding="utf-8") as f:
            state = yaml.safe_load(f) or {}
    except Exception as e:
        entry["detail"] = f"YAML error: {e}"
        return entry

    sub_hyps = state.get("sub_hypotheses")
    if isinstance(sub_hyps, dict) and len(sub_hyps) > 0:
        entry["ok"] = True
        entry["detail"] = f"sub_hypotheses dict with {len(sub_hyps)} hypotheses"
        return entry

    # Check for wrong schema
    hyps_list = state.get("hypotheses")
    if isinstance(hyps_list, list) and hyps_list:
        entry["ok"] = False
        entry["detail"] = (
            f"WRONG SCHEMA: 'hypotheses' is a list ({len(hyps_list)} items) — "
            f"must be 'sub_hypotheses' dict keyed by hypothesis ID. "
            f"Re-generate verification_state.yaml using step-10-finalize template."
        )
        return entry

    entry["ok"] = False
    entry["detail"] = "sub_hypotheses missing or empty"
    return entry


def _check_no_synthetic_dataset(folder: Path) -> Dict[str, Any]:
    """Check that 02c_experiment_brief.md does not contain Type: synthetic dataset."""
    entry: Dict[str, Any] = {
        "file": "02c_experiment_brief.md [synthetic data check]",
        "ok": False,
    }
    brief_path = folder / "02c_experiment_brief.md"
    if not brief_path.exists():
        entry["exists"] = False
        entry["detail"] = "FILE MISSING"
        return entry

    entry["exists"] = True
    try:
        import re
        content = brief_path.read_text(encoding="utf-8", errors="ignore")
        # Check for synthetic dataset type indicators
        synthetic_patterns = [
            r'[Tt]ype\s*:\s*synthetic',
            r'[Tt]ype\s*:\s*`synthetic`',
            r'\*\*[Tt]ype\*\*\s*:\s*synthetic',
            r'\*\*[Tt]ype\*\*\s*:\s*`synthetic`',
            r'dataset_type\s*:\s*synthetic',
            r'dataset_type\s*:\s*"synthetic"',
            r"dataset_type\s*:\s*'synthetic'",
            r'FAILED_NO_REAL_DATA',
        ]
        found_synthetic = []
        for pattern in synthetic_patterns:
            matches = re.findall(pattern, content)
            if matches:
                found_synthetic.extend(matches)

        if found_synthetic:
            entry["ok"] = False
            entry["detail"] = f"SYNTHETIC DATA DETECTED: {found_synthetic[0]}. Synthetic datasets are prohibited — replace with real data (standard/custom/programmatic-api)"
        else:
            entry["ok"] = True
            entry["detail"] = "No synthetic dataset found"
    except Exception as e:
        entry["detail"] = f"Error reading file: {e}"

    return entry


def _checks_phase2c(folder: Path, research_folder: Optional[Path] = None, h_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """folder = {research_folder}/{h_id}/"""
    checks = [
        _check(folder, "02c_experiment_brief.md", check_unfilled=True),
        _check_no_synthetic_dataset(folder),
    ]
    if research_folder and h_id:
        vs = research_folder / "verification_state.yaml"
        checks.append(_check_yaml_field(
            vs,
            f"sub_hypotheses.{h_id}.experiment_design.status",
            "COMPLETED",
        ))
        checks.append(_check_yaml_field_not(
            vs,
            f"sub_hypotheses.{h_id}.experiment_design.file",
            "null",
        ))
    return checks


def _checks_phase3(folder: Path, research_folder: Optional[Path] = None, h_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """folder = {research_folder}/{h_id}/"""
    checks = [
        _check(folder, "03_prd.md", check_unfilled=True),
        _check(folder, "03_architecture.md", check_unfilled=True),
        _check(folder, "03_logic.md", check_unfilled=True),
        _check(folder, "03_config.md", check_unfilled=True),
    ]
    if research_folder and h_id:
        vs = research_folder / "verification_state.yaml"
        checks.append(_check_yaml_field(
            vs,
            f"sub_hypotheses.{h_id}.implementation_planning.status",
            "COMPLETED",
        ))
        checks.append(_check_yaml_field_not(
            vs,
            f"sub_hypotheses.{h_id}.implementation_planning.tasks_file",
            "null",
        ))
    return checks


def _checks_phase4(folder: Path, research_folder: Optional[Path] = None, h_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """folder = {research_folder}/{h_id}/"""
    checks = [
        _check(folder, "04_validation.md", check_unfilled=True),
        _check(folder, "04_checkpoint.yaml"),
    ]
    if research_folder and h_id:
        vs = research_folder / "verification_state.yaml"
        # Phase 4 can end as COMPLETED, FAIL, or PARTIAL — any non-NOT_STARTED means it ran
        checks.append(_check_yaml_field_not(
            vs,
            f"sub_hypotheses.{h_id}.validation.status",
            "NOT_STARTED",
        ))
        checks.append(_check_yaml_field_not(
            vs,
            f"sub_hypotheses.{h_id}.validation.result",
            "null",
        ))
        checks.append(_check_yaml_field_not(
            vs,
            f"sub_hypotheses.{h_id}.gate.satisfied",
            "null",
        ))
        checks.append(_check_phase4_reflection_outcome_when_gate_failed(
            vs, folder, h_id,
        ))
        # Serena Memory: required when gate failed (PARTIAL_FAIL, FAIL, routing)
        checks.append(_check_serena_memory_written(folder))
    return checks


def _check_serena_memory_written(folder: Path) -> Dict[str, Any]:
    """Check that Serena Memory was written when routing or limitation occurred.

    Reads 04_checkpoint.yaml to determine:
    1. Whether routing or limitation occurred (reflection_outcome)
    2. Whether serena_memory.memory_written is true

    Serena memory is required when:
    - ROUTED_TO_PHASE_0 / FAILED → failure record
    - ROUTED_TO_PHASE_2A / SUPERSEDED → superseded record
    - MODIFIED / SELF_MODIFY → pivot record
    - LIMITATION_RECORDED → limitation record (SHOULD_WORK failure)

    For all other outcomes (PASS, no reflection, etc.)
    this check auto-passes.
    """
    entry: Dict[str, Any] = {
        "file": "04_checkpoint.yaml [serena_memory.memory_written]",
        "ok": True,  # default: pass (no routing → no memory needed)
    }

    checkpoint_path = folder / "04_checkpoint.yaml"
    if not checkpoint_path.exists():
        entry["detail"] = "no checkpoint — skipped"
        return entry

    try:
        import yaml
        with open(checkpoint_path, encoding="utf-8") as f:
            checkpoint = yaml.safe_load(f) or {}
    except Exception as e:
        entry["detail"] = f"YAML error: {e}"
        return entry

    reflection_outcome = (checkpoint.get("reflection_outcome") or "").upper()

    # Outcomes that require serena memory (routing + limitation)
    memory_required_outcomes = {
        "ROUTED_TO_PHASE_0", "ROUTED_TO_PHASE_2A",
        "FAILED", "SUPERSEDED",
        "MODIFIED", "SELF_MODIFY",
        "LIMITATION_RECORDED",
    }

    if reflection_outcome not in memory_required_outcomes:
        entry["detail"] = f"reflection_outcome={reflection_outcome or 'N/A'} — serena memory not required"
        return entry

    # Routing occurred → check memory_written
    serena = checkpoint.get("serena_memory", {})
    memory_written = serena.get("memory_written", False)

    if memory_written:
        entry["ok"] = True
        entry["detail"] = f"memory_written=true (routing={reflection_outcome})"
    else:
        entry["ok"] = False
        entry["detail"] = (
            f"SERENA MEMORY NOT WRITTEN — reflection_outcome={reflection_outcome}. "
            f"Must call mcp__serena__write_memory() to record routing decision."
        )

    return entry


def _checks_phase65(folder: Path, research_folder: Optional[Path] = None, h_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """folder = research_folder (Phase 6.5 writes to research_folder/paper/)."""
    rf = research_folder or folder
    paper_dir = rf / "paper"
    review_dir = paper_dir / "review"
    checks = [
        # Final reviewed paper
        _check(paper_dir, "06_paper_final.md", check_unfilled=True),
    ]
    # Review outputs (may be in paper/review/ or paper/)
    review_files = [
        ("065_review_summary.md", review_dir),
        ("065_changelog.md", review_dir),
        ("065_review_checkpoint.yaml", review_dir),
    ]
    for fname, rdir in review_files:
        fpath = rdir / fname
        if fpath.exists():
            checks.append(_check(rdir, fname))
        else:
            # Fallback: check in paper_dir directly
            checks.append(_check(paper_dir, fname))
    # At least one adversary review round must exist
    r1 = review_dir / "065_review_r1.md"
    r1_alt = paper_dir / "065_review_r1.md"
    r1_exists = r1.exists() or r1_alt.exists()
    checks.append({
        "file": "065_review_r1.md",
        "ok": r1_exists,
        "exists": r1_exists,
        "detail": "present" if r1_exists else "MISSING (no adversary R1 review found)",
    })
    # Check that final paper has review metadata or sections
    final_paper = paper_dir / "06_paper_final.md"
    if final_paper.exists():
        try:
            content = final_paper.read_text(encoding="utf-8")
            required_sections = [
                "Abstract",
                "Introduction",
                "Related Work",
                "Methodology",
                "Experiment",
                "Result",
                "Discussion",
                "Conclusion",
            ]
            for section in required_sections:
                found = section.lower() in content.lower()
                checks.append({
                    "file": f"06_paper_final.md [section: {section}]",
                    "ok": found,
                    "detail": "present" if found else "MISSING",
                })
        except Exception as e:
            checks.append({"file": "06_paper_final.md [sections]", "ok": False, "detail": str(e)})
    return checks


def _checks_phase651(folder: Path, research_folder: Optional[Path] = None, h_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """folder = research_folder (Phase 6.5.1 writes to research_folder/paper/overleaf/)."""
    rf = research_folder or folder
    overleaf_dir = rf / "paper" / "overleaf"
    checks = [
        # main.tex must exist
        _check(overleaf_dir, "main.tex"),
    ]
    # Check section .tex files
    sections_dir = overleaf_dir / "sections"
    expected_sections = [
        "abstract.tex", "introduction.tex", "related_work.tex",
        "methodology.tex", "experiments.tex", "results.tex",
        "discussion.tex", "conclusion.tex",
    ]
    for sec in expected_sections:
        sec_path = sections_dir / sec
        checks.append({
            "file": f"overleaf/sections/{sec}",
            "ok": sec_path.exists() and sec_path.stat().st_size > 0,
            "exists": sec_path.exists(),
            "size": sec_path.stat().st_size if sec_path.exists() else 0,
        })
    # Check references.bib copied
    refs = overleaf_dir / "references.bib"
    checks.append({
        "file": "overleaf/references.bib",
        "ok": refs.exists(),
        "exists": refs.exists(),
        "size": refs.stat().st_size if refs.exists() else 0,
    })
    # Check output.pdf (optional — pdflatex may not be available)
    pdf = overleaf_dir / "output.pdf"
    main_pdf = overleaf_dir / "main.pdf"
    pdf_exists = pdf.exists() or main_pdf.exists()
    checks.append({
        "file": "overleaf/output.pdf",
        "ok": True,  # PDF is optional (can compile on Overleaf)
        "exists": pdf_exists,
        "detail": "present" if pdf_exists else "not compiled (can use Overleaf)",
    })
    return checks


def _checks_phase6(folder: Path, research_folder: Optional[Path] = None, h_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """folder = research_folder (Phase 6 writes to research_folder/paper/)."""
    rf = research_folder or folder
    paper_dir = rf / "paper"
    checks = [
        _check(paper_dir, "06_paper.md", check_unfilled=True),
        _check(paper_dir, "065_ground_truth.yaml"),
        _check(paper_dir, "06_references.bib"),
        _check(paper_dir, "06_narrative_blueprint.yaml"),
    ]
    # Check individual sections exist
    sections = [
        "sections/00_abstract.md",
        "sections/01_introduction.md",
        "sections/02_related_work.md",
        "sections/03_methodology.md",
        "sections/04_experiments.md",
        "sections/05_results.md",
        "sections/06_discussion.md",
        "sections/07_conclusion.md",
    ]
    for sec in sections:
        checks.append(_check(paper_dir, sec))
    # Check required sections in the final paper
    paper_file = paper_dir / "06_paper.md"
    if paper_file.exists():
        try:
            content = paper_file.read_text(encoding="utf-8")
            required_sections = [
                "Abstract",
                "Introduction",
                "Related Work",
                "Methodology",
                "Experiment",
                "Result",
                "Discussion",
                "Conclusion",
            ]
            for section in required_sections:
                found = section.lower() in content.lower()
                checks.append({
                    "file": f"06_paper.md [section: {section}]",
                    "ok": found,
                    "detail": "present" if found else "MISSING",
                })
        except Exception as e:
            checks.append({"file": "06_paper.md [sections]", "ok": False, "detail": str(e)})
    return checks


def _checks_phase45(folder: Path, research_folder: Optional[Path] = None, h_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """folder = research_folder (Phase 4.5 writes to research root)."""
    rf = research_folder or folder
    checks = [
        _check(rf, "045_validated_hypothesis.md", check_unfilled=True),
    ]
    # Check required sections in the output
    synth = rf / "045_validated_hypothesis.md"
    if synth.exists():
        try:
            content = synth.read_text(encoding="utf-8")
            required_sections = [
                "Executive Summary",
                "Prediction-Result Matrix",
                "Hypothesis Refinement",
                "Theoretical Interpretation",
                "Experiment Results",
                "Limitations",
                "Future Work",
                "Implications for Phase 6",
            ]
            for section in required_sections:
                found = section.lower() in content.lower()
                checks.append({
                    "file": f"045_validated_hypothesis.md [section: {section}]",
                    "ok": found,
                    "detail": "present" if found else "MISSING",
                })
        except Exception as e:
            checks.append({"file": "045_validated_hypothesis.md [sections]", "ok": False, "detail": str(e)})
    # Check verification_state.yaml updated
    vs = rf / "verification_state.yaml"
    if vs.exists():
        checks.append(_check_yaml_field(vs, "workflow.synthesis_completed", "true"))
    return checks


_PHASE_CHECKS = {
    "phase0": _checks_phase0,
    "phase1": _checks_phase1,
    "phase2a": _checks_phase2a,
    "phase2b": _checks_phase2b,
    # phase2c/3/4/45 use extended signatures — called directly in verify_and_write_json
}


# ============================================================
# Public API
# ============================================================

def verify_and_write_json(
    phase: str,
    research_folder: Optional[str],
    claude_exit_code: int,
    hypothesis_id: Optional[str] = None,
) -> bool:
    """
    Run output checks for the given phase and write results to
    .cache/{phase}_output_verify.json (or .cache/{phase}_{h_id}_output_verify.json).

    For phase2c/3/4, pass hypothesis_id to check {research_folder}/{hypothesis_id}/.

    Returns True if all checks passed, False otherwise.
    Called by each run_phase*.py just before sys.exit().
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    json_key = f"{phase}_{hypothesis_id}" if hypothesis_id else phase
    out_path = CACHE_DIR / f"{json_key}_output_verify.json"

    result: Dict[str, Any] = {
        "phase": phase,
        "hypothesis_id": hypothesis_id or "",
        "research_folder": research_folder or "",
        "verified_at": datetime.now().isoformat(),
        "claude_exit_code": claude_exit_code,
        "passed": False,
        "checks": [],
        "errors": [],
    }

    if not research_folder:
        result["errors"].append("research_folder not provided — cannot verify outputs")
        _write(out_path, result)
        return False

    folder = Path(research_folder)
    if hypothesis_id:
        folder = folder / hypothesis_id
    if not folder.exists():
        result["errors"].append(f"folder does not exist: {folder}")
        _write(out_path, result)
        return False

    # phase2c/3/4 take extra parameters (research_folder, h_id) for YAML field checks
    if phase == "phase2c":
        checks = _checks_phase2c(folder, Path(research_folder), hypothesis_id)
    elif phase == "phase3":
        checks = _checks_phase3(folder, Path(research_folder), hypothesis_id)
    elif phase == "phase4":
        checks = _checks_phase4(folder, Path(research_folder), hypothesis_id)
    elif phase == "phase45":
        checks = _checks_phase45(folder, Path(research_folder))
    elif phase == "phase6":
        checks = _checks_phase6(folder, Path(research_folder))
    elif phase == "phase65":
        checks = _checks_phase65(folder, Path(research_folder))
    elif phase == "phase651":
        checks = _checks_phase651(folder, Path(research_folder))
    else:
        check_fn = _PHASE_CHECKS.get(phase)
        if check_fn is None:
            result["errors"].append(f"No verification defined for phase: {phase}")
            _write(out_path, result)
            return False
        checks = check_fn(folder)
    result["checks"] = checks
    result["passed"] = all(c.get("ok", False) for c in checks)

    _write(out_path, result)

    # Print summary to stderr
    status = "PASSED" if result["passed"] else "FAILED"
    print(f"[VERIFY] {phase} output verification: {status} → {out_path}", flush=True)
    for c in checks:
        icon = "✓" if c.get("ok") else "✗"
        print(f"  {icon} {c['file']}", flush=True)

    return result["passed"]


def _write(path: Path, data: Dict[str, Any]) -> None:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[VERIFY] WARNING: failed to write {path}: {e}", flush=True)


# ============================================================
# MUST_STOP Support (written by phase_auto_responder.py)
# ============================================================

MUST_STOP_FILE = CACHE_DIR / "must_stop.json"


def clear_must_stop() -> None:
    """Delete must_stop.json if it exists (call at phase start to clear stale flags)."""
    try:
        if MUST_STOP_FILE.exists():
            MUST_STOP_FILE.unlink()
            print(f"[VERIFY] Cleared stale must_stop.json", flush=True)
    except Exception as e:
        print(f"[VERIFY] WARNING: failed to clear must_stop.json: {e}", flush=True)


def clear_phase_complete_lock(phase: str) -> None:
    """Delete {phase}_complete.lock if it exists.

    Call at phase start (to clear stale lock from previous run) and
    before each retry loop (to prevent hook from immediately approving
    the retry session due to a lock written by the just-completed session).
    """
    lock_path = CACHE_DIR / f"{phase}_complete.lock"
    try:
        if lock_path.exists():
            lock_path.unlink()
            print(f"[VERIFY] Cleared {phase}_complete.lock", flush=True)
    except Exception as e:
        print(f"[VERIFY] WARNING: failed to clear {phase}_complete.lock: {e}", flush=True)


def check_must_stop() -> Optional[str]:
    """
    Check if must_stop.json exists. If so, read reason, delete the file, and return reason.
    Returns None if no must_stop signal.
    """
    if not MUST_STOP_FILE.exists():
        return None
    try:
        with open(MUST_STOP_FILE, encoding="utf-8") as f:
            data = json.load(f)
        reason = data.get("reason", "unknown")
        MUST_STOP_FILE.unlink()
        print(f"[VERIFY] MUST_STOP detected: {reason}", flush=True)
        return reason
    except Exception as e:
        print(f"[VERIFY] WARNING: failed to read must_stop.json: {e}", flush=True)
        return None


# ============================================================
# Retry Support (used by individual run_phase*.py launchers)
# ============================================================

MAX_RETRIES = _load_max_retries()  # loaded from auto_responder_config.yaml → pipeline_retry.max_retries


def _load_claude_config() -> dict:
    """Load claude_model and claude_effort from auto_responder_config.yaml.

    Returns dict with 'model' and 'effort' keys (empty string if not set).
    """
    try:
        import yaml
        cfg_path = SCRIPT_DIR / "auto_responder_config.yaml"
        with open(cfg_path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
        return {
            "model": str(cfg.get("claude_model") or "").strip(),
            "effort": str(cfg.get("claude_effort") or "").strip(),
        }
    except Exception:
        return {"model": "", "effort": ""}


def load_claude_model() -> str:
    """Load claude_model from auto_responder_config.yaml.

    Returns model string (e.g. 'claude-sonnet-4-6') or empty string if not set.
    """
    return _load_claude_config()["model"]


_EFFORT_SUPPORTED_MODELS = {
    "claude-opus-4-6", "claude-sonnet-4-6", "claude-opus-4-5",
    "opus", "sonnet",  # CLI shorthands
}


def _model_supports_effort(model: str) -> bool:
    """Check if the model supports the --effort flag."""
    if not model:
        return True  # default model (likely supports effort)
    m = model.lower().strip()
    return any(s in m for s in _EFFORT_SUPPORTED_MODELS)


def build_claude_cmd(claude_cli: Path, prompt: str, extra_flags: list = None) -> list:
    """Build Claude CLI command with optional --model and --effort from config.

    Effort flag is only added for models that support it.
    For unsupported models (e.g. sonnet-4.5, haiku), effort is silently skipped.

    Usage in run_phase*.py:
        from phase_output_verifier import build_claude_cmd
        claude_cmd = build_claude_cmd(CLAUDE_CLI, prompt)
    """
    cmd = [str(claude_cli), "-p", prompt, "--dangerously-skip-permissions"]
    cfg = _load_claude_config()
    if cfg["model"]:
        cmd.extend(["--model", cfg["model"]])
    if cfg["effort"] and _model_supports_effort(cfg["model"]):
        cmd.extend(["--effort", cfg["effort"]])
    if extra_flags:
        cmd.extend(extra_flags)
    return cmd


def _proc_tree_pids(root_pid: int) -> list:
    """Return root_pid + all descendant PIDs by walking /proc."""
    try:
        pids = [root_pid]
        children = {}
        for entry in os.listdir("/proc"):
            if not entry.isdigit():
                continue
            try:
                with open(f"/proc/{entry}/stat", "r") as f:
                    fields = f.read().split()
                ppid = int(fields[3])
                children.setdefault(ppid, []).append(int(entry))
            except (FileNotFoundError, IndexError, ValueError):
                continue
        stack = [root_pid]
        seen = {root_pid}
        while stack:
            p = stack.pop()
            for c in children.get(p, []):
                if c not in seen:
                    seen.add(c)
                    pids.append(c)
                    stack.append(c)
        return pids
    except Exception:
        return [root_pid]


def proc_tree_cputime(root_pid: int) -> int:
    """Sum utime+stime (clock ticks) of root_pid and all descendants.

    Hang signal: if this value does not increase for several minutes, the
    process tree is stuck in blocking syscalls (e.g., heredoc waiting on
    closed stdin). Real training keeps growing because data loaders and
    the Python interpreter accumulate CPU time even when GPU-bound.
    """
    total = 0
    for pid in _proc_tree_pids(root_pid):
        try:
            with open(f"/proc/{pid}/stat", "r") as f:
                fields = f.read().split()
            total += int(fields[13]) + int(fields[14])
        except (FileNotFoundError, IndexError, ValueError):
            continue
    return total


def _format_verify_summary(data: dict) -> str:
    if not data:
        return "  (no verification data available)"
    lines = []
    for c in data.get("checks", []):
        icon = "✓" if c.get("ok") else "✗"
        detail = []
        # YAML field check (has "field" key)
        if "field" in c:
            if not c.get("exists", True):
                detail.append("FILE MISSING")
            elif c.get("field_missing"):
                detail.append(f"field '{c['field']}' not found in YAML")
            elif c.get("yaml_error"):
                detail.append(f"YAML parse error: {c['yaml_error']}")
            elif not c.get("ok"):
                if "rejected" in c:
                    # _check_yaml_field_not style
                    detail.append(
                        f"field {c['field']}={c.get('actual', '?')} (must NOT be {c['rejected']})"
                    )
                else:
                    # _check_yaml_field style
                    detail.append(
                        f"field {c['field']}={c.get('actual', '?')} (expected {c.get('expected', '?')})"
                    )
            suffix = f" — {', '.join(detail)}" if detail else f" [field {c['field']}={c.get('actual')}]"
            lines.append(f"  {icon} {c['file']}{suffix}")
            continue
        # File check
        if not c.get("exists", True):
            detail.append("FILE MISSING")
        elif c.get("empty"):
            detail.append("EMPTY FILE")
        elif c.get("no_unfilled") is False:
            detail.append("has {{UNFILLED:}} placeholders")
        else:
            for k, v in c.items():
                if k not in ("file", "ok", "exists", "size", "no_unfilled") and v is False:
                    detail.append(f"{k}=False")
        suffix = f" — {', '.join(detail)}" if detail else f" ({c.get('size', 0)} bytes)"
        lines.append(f"  {icon} {c['file']}{suffix}")
    for e in data.get("errors", []):
        lines.append(f"  ! ERROR: {e}")
    return "\n".join(lines)


def build_retry_prompt(phase: str, research_folder: str, hypothesis_id: Optional[str] = None) -> str:
    """Build a corrective retry prompt from the last verify JSON for the given phase."""
    json_key = f"{phase}_{hypothesis_id}" if hypothesis_id else phase
    json_path = CACHE_DIR / f"{json_key}_output_verify.json"
    data = {}
    if json_path.exists():
        try:
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass

    summary = _format_verify_summary(data)

    slash_cmd = {
        "phase0":  "/phase0-brainstorm",
        "phase1":  "/phase1-targeted",
        "phase2a": "/phase2a-dialogue",
        "phase2b": "/phase2b-planning",
        "phase2c": "/phase2c-experiment-design",
        "phase3":  "/phase3-implementation-planning",
        "phase4":  "/phase4-coding",
        "phase45": "/phase45-hypothesis-synthesis",
        "phase6":  "/phase6-paper-writing",
        "phase65": "/phase65-adversarial-review",
        "phase651": "/phase651-overleaf",
    }.get(phase, f"/{phase}")

    required = {
        "phase0":  "00_brainstorm_session.md (with <phase1-input> section, no {{UNFILLED:}})",
        "phase1":  "01_targeted_research.md AND 01_targeted_research_full.md (no {{UNFILLED:}})",
        "phase2a": "03_refinement.yaml, 02_synthesis.yaml, 01_round_table/final_opinions.yaml, "
                   "03_refinement.md, discussion_log.md (with 'Final Assessments' section)",
        "phase2b": "verification_state.yaml, 02b_verification_plan.md (no {{UNFILLED:}})",
        "phase2c": "02c_experiment_brief.md (no {{UNFILLED:}}), verification_state.yaml (sub_hypotheses.{h_id}.experiment_design.status = \"COMPLETED\", experiment_design.file != null)",
        "phase3":  "03_prd.md, 03_architecture.md, 03_logic.md, 03_config.md (no {{UNFILLED:}}), verification_state.yaml (sub_hypotheses.{h_id}.implementation_planning.status = \"COMPLETED\", implementation_planning.tasks_file != null)",
        "phase4":  "04_validation.md (no {{UNFILLED:}}), 04_checkpoint.yaml, verification_state.yaml (sub_hypotheses.{h_id}.validation.status != NOT_STARTED, validation.result != null, gate.satisfied != null)",
        "phase45": "045_validated_hypothesis.md (with all 8 sections: Executive Summary, Prediction-Result Matrix, Hypothesis Refinement, Theoretical Interpretation, Experiment Results, Limitations, Future Work, Implications for Phase 6), verification_state.yaml (workflow.synthesis_completed = true)",
        "phase6":  "paper/06_paper.md (final ICML paper with all sections: Abstract, Introduction, Related Work, Methodology, Experiments, Results, Discussion, Conclusion), "
                   "paper/065_ground_truth.yaml, paper/06_references.bib, paper/06_narrative_blueprint.yaml, "
                   "paper/sections/00_abstract.md through paper/sections/07_conclusion.md (8 section files)",
        "phase65": "paper/06_paper_final.md (reviewed final paper with all sections), "
                   "paper/review/065_review_summary.md, paper/review/065_changelog.md, "
                   "paper/review/065_review_checkpoint.yaml, paper/review/065_review_r1.md (at least Round 1 adversary review)",
        "phase651": "paper/overleaf/main.tex (ICML LaTeX document), "
                    "paper/overleaf/sections/*.tex (8 section files), "
                    "paper/overleaf/references.bib, paper/overleaf/output.pdf (if pdflatex available)",
    }.get(phase, "(see workflow documentation)")

    # Replace {h_id} placeholder with actual hypothesis_id
    h_id_str = hypothesis_id or "UNKNOWN"
    required = required.replace("{h_id}", h_id_str)

    extra = {
        "phase1":  "- At Step 9, auto-select [E] Exit to complete\n",
        "phase2a": "- Step 1: Run the Tikitaka discussion loop until convergence\n"
                   "- Step 2: Structure outputs into Phase 2B-compatible YAML files\n",
        "phase2b": "- When presented with any menu, automatically select [C] Continue\n"
                   "- Step 10: Generate verification_state.yaml\n"
                   "- CRITICAL: verification_state.yaml MUST use 'sub_hypotheses' as a DICT keyed by hypothesis ID:\n"
                   "    sub_hypotheses:\n"
                   "      h-e1:\n"
                   "        type: EXISTENCE\n"
                   "        status: READY\n"
                   "        ...\n"
                   "  Do NOT use 'hypotheses' as a list. The hypothesis loop will fail if the schema is wrong.\n",
        "phase2c": "- Focus on completing 02c_experiment_brief.md with all sections filled\n"
                   f"- Update verification_state.yaml for sub_hypotheses.{h_id_str}:\n"
                   f"  - experiment_design.status: set to \"COMPLETED\"\n"
                   f"  - experiment_design.file: set to the experiment brief filename (NOT null)\n"
                   "- CRITICAL: Do NOT use synthetic/simulated datasets (Type: synthetic)\n"
                   "  - If the current brief has Type: synthetic, REPLACE it with a real dataset\n"
                   "  - Acceptable types: standard, custom, programmatic-api\n"
                   "  - Search Archon KB and Exa for real benchmark datasets\n"
                   "  - If no real dataset exists, set dataset_type to FAILED_NO_REAL_DATA\n",
        "phase3":  "- Complete all four design documents (PRD, Architecture, Logic, Config)\n"
                   f"- Update verification_state.yaml for sub_hypotheses.{h_id_str}:\n"
                   f"  - implementation_planning.status: set to \"COMPLETED\"\n"
                   f"  - implementation_planning.tasks_file: set to the tasks filename (NOT null)\n",
        "phase45": "- Read all h-*/04_validation.md and h-*/04_checkpoint.yaml\n"
                   "- Execute all 8 steps (init, alignment, refinement, interpretation, limitations, future work, generate, finalize)\n"
                   "- Generate 045_validated_hypothesis.md with all 8 sections filled\n"
                   "- Update verification_state.yaml with synthesis_completed: true\n",
        "phase4":  "- Complete implementation and generate 04_validation.md and 04_checkpoint.yaml\n"
                   f"- Update verification_state.yaml for sub_hypotheses.{h_id_str}:\n"
                   f"  - validation.status: set to actual result (COMPLETED/FAIL/PARTIAL — NOT 'NOT_STARTED')\n"
                   f"  - validation.result: set to experiment result summary (NOT null)\n"
                   f"  - gate.satisfied: set to true/false based on gate evaluation (NOT null)\n"
                   "- SERENA MEMORY (if gate failed/partial/routed):\n"
                   "  1. Read the helpers file: bmad-custom-src/custom/modules/youra-research/workflows/helpers/serena_memory_patterns.md\n"
                   "  2. Based on the reflection_outcome in 04_checkpoint.yaml, call mcp__serena__write_memory() NOW:\n"
                   "     - FAILED/ROUTED_TO_PHASE_0: write failure record (failure_{hypothesis_id}.md)\n"
                   "     - ROUTED_TO_PHASE_2A/SUPERSEDED: write superseded record (superseded_{hypothesis_id}.md)\n"
                   "     - MODIFIED/SELF_MODIFY: write pivot record (pivot_{hypothesis_id}.md)\n"
                   "     - LIMITATION_RECORDED: write limitation record (limitation_{hypothesis_id}.md) for SHOULD_WORK failures\n"
                   "  3. After writing, update 04_checkpoint.yaml: serena_memory.memory_written: true, serena_memory.written_at: (ISO timestamp)\n"
                   "  4. This is MANDATORY — verification will fail again if memory is not written\n",
        "phase6":  "- Read 045_validated_hypothesis.md as PRIMARY input\n"
                   "- Execute all 7 steps (init, narrative design, foundation, evidence, closure, references, merge)\n"
                   "- Generate 06_narrative_blueprint.yaml before writing any sections\n"
                   "- Generate all 8 section files (00_abstract.md through 07_conclusion.md)\n"
                   "- Generate 00_abstract.md LAST with actual quantitative results\n"
                   "- Compile 06_references.bib with Semantic Scholar verification\n"
                   "- Merge all sections into final 06_paper.md\n"
                   "- Extract ground truth into 065_ground_truth.yaml for Phase 6.5\n",
        "phase65": "- Read paper/06_paper.md and paper/065_ground_truth.yaml as PRIMARY inputs\n"
                   "- Execute adversarial review with 3 personas (Accuracy Checker, Bored Reviewer, Skeptical Expert)\n"
                   "- Run at least 1 round of adversary review → revision\n"
                   "- Check convergence: FATAL=0, MAJOR=0, persuasiveness_passed\n"
                   "- Do NOT auto-fix MINOR issues — collect in 065_human_review_notes.md\n"
                   "- Generate 06_paper_final.md (reviewed final paper)\n"
                   "- Generate 065_review_summary.md, 065_changelog.md\n"
                   "- Update verification_state.yaml with Phase 6.5 completion\n",
        "phase651": "- Read paper/06_paper_final.md as PRIMARY input\n"
                    "- Execute all 4 steps (init, markdown-to-latex, assemble, compile)\n"
                    "- Create paper/overleaf/ with main.tex and sections/*.tex\n"
                    "- Copy references.bib and figures to overleaf/\n"
                    "- Run pdflatex + bibtex to compile output.pdf (skip if pdflatex unavailable)\n"
                    "- Update verification_state.yaml with Phase 6.5.1 completion\n",
    }.get(phase, "")

    h_line = f"- Hypothesis: {hypothesis_id}\n" if hypothesis_id else ""

    return (
        f"{slash_cmd}\n\n"
        f"#batch-mode\n\n"
        f"RETRY after incomplete execution. Research folder: {research_folder}\n\n"
        f"The previous run did not produce all required outputs.\n"
        f"Verification result:\n{summary}\n\n"
        f"Please re-execute {slash_cmd} in Unattended mode.\n"
        f"- Research folder: {research_folder}\n"
        f"{h_line}"
        f"- Required outputs: {required}\n"
        f"{extra}"
        f"- Do NOT ask for user confirmation — proceed through all steps without stopping"
    )
