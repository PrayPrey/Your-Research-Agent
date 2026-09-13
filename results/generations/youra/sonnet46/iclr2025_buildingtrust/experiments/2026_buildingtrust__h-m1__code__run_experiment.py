"""
run_experiment.py — H-M1 Orchestrator

Full pipeline:
  Path A (or A-extended) → gate eval → ordering → figures → report → verification_state.yaml
  Fallback: Path B (lm-eval re-run) if Path A fails
"""

import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

# ── Setup sys.path so imports work from any CWD ──────────────────────────────
_SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(_SCRIPT_DIR))

import config
sys.path.insert(0, config.H_E1_CODE_DIR)

from extract_h_e1_data import extract_or_recompute_ece_base
from gate_and_report import (
    verify_mechanism_activation,
    evaluate_must_work_gate,
    check_ece_ordering,
    generate_validation_report,
)
from plot_results import generate_all_figures

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("run_experiment")


# ═══════════════════════════════════════════════════════════════════════════════
# Path A: extract from h-e1
# ═══════════════════════════════════════════════════════════════════════════════

def run_path_a() -> tuple:
    """
    Run Path A (and A-extended fallback).

    Returns:
        (ece_base: dict, execution_path: str)

    Raises:
        RuntimeError: if both Path A and A-extended fail
    """
    ece_base, execution_path = extract_or_recompute_ece_base(
        validation_file=config.H_E1_VALIDATION_PATH,
        results_dir=config.H_E1_RESULTS_DIR,
    )
    return ece_base, execution_path


# ═══════════════════════════════════════════════════════════════════════════════
# Path B: lm-eval re-run fallback
# ═══════════════════════════════════════════════════════════════════════════════

def run_lmeval_for_model(
    model_id: str,
    output_dir: str,
    device: str = "cuda",
) -> Path:
    """
    Execute lm_eval CLI for a single Pythia base model.

    Args:
        model_id: HuggingFace model ID (e.g., "EleutherAI/pythia-1.4b")
        output_dir: directory to write lm_eval results
        device: "cuda" or "cpu"

    Returns:
        Path: output directory for this model

    Raises:
        RuntimeError: if subprocess fails after 1 retry
    """
    model_dir = Path(output_dir) / model_id.replace("/", "_")
    model_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, "-m", "lm_eval",
        "--model", "hf",
        "--model_args", f"pretrained={model_id}",
        "--tasks", "mmlu",
        "--num_fewshot", "0",
        "--batch_size", "8",
        "--device", device,
        "--output_path", str(model_dir),
        "--log_samples",
        "--trust_remote_code",
    ]

    logger.info(f"  Running lm_eval for {model_id}...")
    logger.debug(f"  Command: {' '.join(cmd)}")

    for attempt in range(2):
        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=config.LMEVAL_TIMEOUT_SECONDS,
            )
            logger.info(f"  ✓ lm_eval completed for {model_id}")
            return model_dir
        except subprocess.CalledProcessError as e:
            logger.warning(
                f"  lm_eval attempt {attempt+1} failed for {model_id}: {e.returncode}"
            )
            if attempt == 0:
                logger.info("  Retrying...")
                continue
            raise RuntimeError(
                f"lm_eval failed for {model_id} after 2 attempts. "
                f"stderr: {e.stderr[-500:]}"
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError(
                f"lm_eval timed out for {model_id} "
                f"(timeout={config.LMEVAL_TIMEOUT_SECONDS}s)"
            )

    raise RuntimeError(f"lm_eval failed for {model_id}")  # unreachable


def run_path_b(
    output_dir: str = None,
    device: str = "cuda",
) -> dict:
    """
    Path B: re-run lm_eval for all 3 Pythia base models sequentially.

    Returns:
        dict: {"1.4b": float, "2.8b": float, "6.9b": float} ECE values

    Raises:
        RuntimeError: if any model fails
    """
    if output_dir is None:
        output_dir = config.H_M1_RESULTS_DIR

    logger.info("=== Path B: lm-eval re-run for 3 base models ===")

    try:
        from calibration_analysis import load_lmeval_samples, compute_ece
        from scipy.special import softmax
    except ImportError as e:
        raise ImportError(f"Cannot import calibration_analysis: {e}")

    ece_base = {}
    for size in config.BASE_SIZES:
        hf_id = config.BASE_MODEL_HF_IDS[size]
        logger.info(f"\n--- Processing {size} ({hf_id}) ---")

        # Run lm_eval
        model_out_dir = run_lmeval_for_model(hf_id, output_dir, device=device)

        # Load samples and compute ECE
        model_id_short = f"pythia-{size}-base"
        logprobs, y_true = load_lmeval_samples(
            model_id_short, results_dir=str(model_out_dir)
        )
        probs = softmax(logprobs, axis=1)
        ece = float(compute_ece(y_true, probs, n_bins=config.N_BINS))
        ece_base[size] = ece
        logger.info(f"  ECE_base[{size}] = {ece:.4f}")

    logger.info(f"✓ Path B complete: {ece_base}")
    return ece_base


# ═══════════════════════════════════════════════════════════════════════════════
# verification_state.yaml update
# ═══════════════════════════════════════════════════════════════════════════════

def write_gate_to_verification_state(
    gate_result: str,
    ece_base: dict,
    gate_report_path: str,
    verification_state_path: str = None,
) -> None:
    """
    Update h-m1 gate and validation fields in verification_state.yaml.
    Preserves all other hypothesis entries.

    Args:
        gate_result: "PASS" or "FAIL"
        ece_base: {"1.4b": float, "2.8b": float, "6.9b": float}
        gate_report_path: path to h-m1/04_validation.md
        verification_state_path: path to verification_state.yaml
    """
    if verification_state_path is None:
        verification_state_path = config.VERIFICATION_STATE_PATH

    path = Path(verification_state_path)
    if not path.exists():
        logger.warning(f"verification_state.yaml not found: {path}")
        return

    # Read
    with open(path, "r", encoding="utf-8") as f:
        state = yaml.safe_load(f)

    ts = datetime.now(timezone.utc).isoformat()

    # Update h-m1 gate
    h_m1 = state.get("sub_hypotheses", {}).get("h-m1", {})
    gate_satisfied = gate_result == "PASS"

    h_m1.setdefault("gate", {})
    h_m1["gate"]["satisfied"] = gate_satisfied
    h_m1["gate"]["result"] = gate_result

    # Update validation status
    h_m1.setdefault("validation", {})
    h_m1["validation"]["status"] = "COMPLETED"
    h_m1["validation"]["result"] = gate_result
    h_m1["validation"]["report_file"] = gate_report_path
    h_m1["validation"]["completed_at"] = ts
    h_m1["validation"]["key_metrics"] = {
        "ece_base_1.4b": ece_base.get("1.4b"),
        "ece_base_2.8b": ece_base.get("2.8b"),
        "ece_base_6.9b": ece_base.get("6.9b"),
        "gate_threshold": config.GATE_THRESHOLD,
        "all_pass": gate_satisfied,
    }
    h_m1["validation"]["key_findings"] = [
        f"MUST_WORK gate {gate_result}: ECE_base < 0.15 for all 3 sizes = {gate_satisfied}",
        f"ECE_base: 1.4b={ece_base.get('1.4b', 'N/A'):.4f}, "
        f"2.8b={ece_base.get('2.8b', 'N/A'):.4f}, "
        f"6.9b={ece_base.get('6.9b', 'N/A'):.4f}",
        "Pretraining yields well-calibrated logit distributions (ECE_base < 0.15)" if gate_satisfied
        else "Unexpected overconfidence in base models before alignment",
    ]

    # Update h-m1 top-level status
    h_m1["status"] = "COMPLETED"
    h_m1["completed"] = True
    h_m1["completed_at"] = ts

    state["sub_hypotheses"]["h-m1"] = h_m1

    # Update statistics
    stats = state.get("statistics", {})
    if gate_result == "PASS":
        stats["validated_sub_hypotheses"] = stats.get("validated_sub_hypotheses", 0) + 1
        stats["gates_passed"] = stats.get("gates_passed", 0) + 1
    else:
        stats["failed_sub_hypotheses"] = stats.get("failed_sub_hypotheses", 0) + 1
        stats["gates_failed"] = stats.get("gates_failed", 0) + 1
    stats["in_progress_sub_hypotheses"] = max(
        0, stats.get("in_progress_sub_hypotheses", 1) - 1
    )
    phases = stats.get("phases_completed", {})
    phases["phase_4"] = phases.get("phase_4", 0) + 1
    stats["phases_completed"] = phases
    state["statistics"] = stats

    # Update history
    state.setdefault("history", []).append({
        "event": f"Phase 4 coding completed — MUST_WORK {gate_result}",
        "timestamp": ts,
        "phase": "Phase 4",
        "hypothesis_id": "h-m1",
        "details": (
            f"Phase 4 COMPLETED. Gate {gate_result}. "
            f"ECE_base: {ece_base}. "
            f"Gate threshold: {config.GATE_THRESHOLD}. "
            f"04_validation.md written."
        ),
    })

    # Write back
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(state, f, default_flow_style=False, allow_unicode=True,
                  sort_keys=False)

    logger.info(f"✓ verification_state.yaml updated: h-m1.gate.satisfied = {gate_satisfied}")


# ═══════════════════════════════════════════════════════════════════════════════
# Main Pipeline
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """
    Full H-M1 pipeline:
    Step 1: Data extraction (Path A → A-extended → B fallback)
    Step 2: Validate ECE dict
    Step 3: Gate evaluation
    Step 4: Ordering check
    Step 5: Figure generation
    Step 6: Validation report
    Step 7: verification_state.yaml update
    Step 8: Save experiment_results.json
    """
    logger.info("=" * 60)
    logger.info("H-M1: Base Calibration Verification")
    logger.info("Gate: MUST_WORK (ECE_base < 0.15 for all 3 Pythia base models)")
    logger.info("=" * 60)

    execution_path = "Path A (regex parse h-e1/04_validation.md)"

    # ── Step 1: Data extraction ────────────────────────────────────────────────
    logger.info("\n[1/8] Extracting ECE_base data...")
    ece_base = None
    try:
        ece_base, execution_path = run_path_a()
        logger.info(f"✓ ECE_base extracted via {execution_path}")
    except RuntimeError as e:
        logger.warning(f"Path A/A-extended failed: {e}")
        logger.info("[1/8] Attempting Path B (lm-eval re-run)...")
        device = "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES", "") != "" else "cpu"
        try:
            ece_base = run_path_b(device=device)
            execution_path = "Path B (lm-eval re-run)"
            logger.info("✓ Path B succeeded")
        except Exception as e2:
            logger.error(f"❌ Path B also failed: {e2}")
            raise RuntimeError(
                f"All execution paths failed. "
                f"Path A/A-extended: {e}. "
                f"Path B: {e2}"
            )

    logger.info(f"  ECE_base: {ece_base}")

    # ── Step 2: Validate ECE dict ─────────────────────────────────────────────
    logger.info("\n[2/8] Validating ECE values...")
    verify_mechanism_activation(ece_base)
    logger.info("✓ ECE validation passed")

    # ── Step 3: Gate evaluation ───────────────────────────────────────────────
    logger.info("\n[3/8] Evaluating MUST_WORK gate...")
    gate_result, failed_ids = evaluate_must_work_gate(ece_base)
    logger.info(f"✓ Gate result: {gate_result}" + (f" (failed: {failed_ids})" if failed_ids else ""))

    # ── Step 4: ECE ordering ──────────────────────────────────────────────────
    logger.info("\n[4/8] Checking ECE ordering (base < aligned)...")
    # Use H-E1 aligned ECE values for ordering check
    h_e1_sft_ece = {"1.4b": 0.1415, "2.8b": 0.0694, "6.9b": 0.0830}
    ece_aligned_for_ordering = {
        size: {"sft": h_e1_sft_ece[size]} for size in config.BASE_SIZES
    }
    ece_ordering = check_ece_ordering(ece_base, ece_aligned=ece_aligned_for_ordering)
    logger.info(f"✓ ECE ordering: {ece_ordering}")

    # ── Step 5: Figure generation ─────────────────────────────────────────────
    logger.info("\n[5/8] Generating figures...")
    figure_paths = []
    # Ensure figures dir exists
    Path(config.H_M1_FIGURES_DIR).mkdir(parents=True, exist_ok=True)
    try:
        figure_paths = generate_all_figures(ece_base, figures_dir=config.H_M1_FIGURES_DIR)
        logger.info(f"✓ {len(figure_paths)} figures generated")
    except Exception as e:
        logger.error(f"❌ Figure generation failed: {e}")
        # Non-critical for gate — continue

    # ── Step 6: Validation report ─────────────────────────────────────────────
    logger.info("\n[6/8] Writing validation report...")
    report_path = generate_validation_report(
        ece_base=ece_base,
        gate_result=gate_result,
        failed_ids=failed_ids,
        execution_path=execution_path,
        figure_paths=figure_paths,
        ece_ordering=ece_ordering,
    )
    logger.info(f"✓ Report written: {report_path}")

    # ── Step 7: Update verification_state.yaml ────────────────────────────────
    logger.info("\n[7/8] Updating verification_state.yaml...")
    write_gate_to_verification_state(
        gate_result=gate_result,
        ece_base=ece_base,
        gate_report_path=report_path,
    )

    # ── Step 8: Save experiment_results.json ──────────────────────────────────
    logger.info("\n[8/8] Saving experiment_results.json...")
    ts = datetime.now(timezone.utc).isoformat()
    results = {
        "hypothesis_id": "h-m1",
        "gate_type": "MUST_WORK",
        "gate_result": gate_result,
        "gate_satisfied": gate_result == "PASS",
        "execution_path": execution_path,
        "timestamp": ts,
        "ece_base": ece_base,
        "gate_threshold": config.GATE_THRESHOLD,
        "failed_ids": failed_ids,
        "ece_ordering": {k: v for k, v in ece_ordering.items()},
        "figure_paths": figure_paths,
        "report_path": report_path,
    }
    json_path = Path(config.H_M1_EXPERIMENT_RESULTS_JSON)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    logger.info(f"✓ Experiment results saved: {json_path}")

    # ── Final summary ──────────────────────────────────────────────────────────
    logger.info("\n" + "=" * 60)
    logger.info(f"H-M1 COMPLETE — Gate: {gate_result}")
    for size in config.BASE_SIZES:
        status = "✅" if ece_base[size] < config.GATE_THRESHOLD else "❌"
        logger.info(f"  {status} Pythia-{size.upper()}: ECE_base = {ece_base[size]:.4f}")
    logger.info(f"Execution path: {execution_path}")
    logger.info(f"Report: {report_path}")
    logger.info("=" * 60)

    return results


if __name__ == "__main__":
    results = main()
    sys.exit(0 if results["gate_satisfied"] else 1)
