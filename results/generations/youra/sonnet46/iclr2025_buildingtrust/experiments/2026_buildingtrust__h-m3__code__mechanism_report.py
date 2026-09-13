"""
mechanism_report.py — H-M3 Mechanism Discrimination
H1/H2/H3 discrimination logic, 04_validation.md writer, verification_state.yaml updater.
"""
import json
import logging
import os
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False
    logger.warning("PyYAML not available; verification_state update will use basic string ops.")


def determine_dominant_mechanism(
    spearman_gate: dict,
    partition_results: dict,
    h3_diagnostic: dict,
    sizes: list,
    alignments: list,
) -> dict:
    """Apply FR-5.1 discrimination logic to determine dominant mechanism.

    H1: mean_rho >= 0.9 AND shared-argmax reliability > changed-argmax for most pairs
    H2: mean_rho < 0.85 for any pair
    H3: TruthfulQA ECE increase >> MMLU ECE increase

    Returns:
        {'dominant': 'H1'|'H2'|'H3'|'ambiguous', 'h1_confirmed': bool,
         'h2_dominant': bool, 'h3_flag': bool, 'per_alignment': dict,
         'gate_pass': bool, '6.9b_ppo_exception': str}
    """
    gate_pass = spearman_gate.get("gate_pass", False)
    h3_flag = h3_diagnostic.get("h3_flag", False)

    # H2: any pair has mean_rho < 0.85
    h2_dominant = spearman_gate.get("n_h2_flag", 0) > 0

    # H1: gate_pass (all pairs >= 0.9) AND most pairs show h1_signature
    n_h1_sig = sum(
        1 for v in partition_results.values() if v.get("h1_signature", False)
    )
    total_pairs = len(partition_results)
    h1_confirmed = gate_pass and (n_h1_sig >= total_pairs // 2 + 1 if total_pairs > 0 else False)

    # 6.9b-PPO exception check
    ppo_exception = ""
    ppo_key = "6.9b-ppo"
    if ppo_key in spearman_gate.get("per_pair", {}):
        ppo_rho = spearman_gate["per_pair"][ppo_key].get("mean_rho", 1.0)
        if ppo_rho < 0.9:
            ppo_exception = (
                f"6.9b-PPO shows mean_rho={ppo_rho:.4f} < 0.9 threshold, "
                "suggesting possible boundary shift for largest PPO model."
            )

    # Per-alignment summary
    per_alignment = {}
    for alignment in alignments:
        pairs = [f"{s}-{alignment}" for s in sizes]
        rhos = [
            spearman_gate["per_pair"].get(p, {}).get("mean_rho", float("nan"))
            for p in pairs
            if p in spearman_gate.get("per_pair", {})
        ]
        h1_sigs = [
            partition_results.get(p, {}).get("h1_signature", False)
            for p in pairs
        ]
        per_alignment[alignment] = {
            "mean_rho_avg": float(np.nanmean(rhos)) if rhos else float("nan"),
            "n_h1_signature": sum(h1_sigs),
            "h3_signal": h3_diagnostic.get("per_alignment", {}).get(alignment, {}).get("h3_signal", False),
        }

    # Determine dominant mechanism
    if h2_dominant:
        dominant = "H2"
    elif h3_flag and not h1_confirmed:
        dominant = "H3"
    elif h1_confirmed:
        dominant = "H1"
    elif h3_flag:
        dominant = "H3"
    else:
        dominant = "ambiguous"

    logger.info(
        "Dominant mechanism: %s (h1=%s h2=%s h3=%s gate=%s)",
        dominant, h1_confirmed, h2_dominant, h3_flag, gate_pass,
    )

    return {
        "dominant": dominant,
        "h1_confirmed": h1_confirmed,
        "h2_dominant": h2_dominant,
        "h3_flag": h3_flag,
        "per_alignment": per_alignment,
        "gate_pass": gate_pass,
        "6.9b_ppo_exception": ppo_exception,
        "n_h1_signature": n_h1_sig,
        "total_pairs": total_pairs,
    }


def write_validation_report(
    mechanism_result: dict,
    spearman_results: dict,
    partition_results: dict,
    tqa_ece_results: dict,
    output_path: str,
) -> None:
    """Write FR-7.1 04_validation.md with all required sections."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    dominant = mechanism_result.get("dominant", "unknown")
    gate_pass = mechanism_result.get("gate_pass", False)

    lines = [
        "# H-M3 Validation Report: Mechanism Discrimination",
        "",
        "## Summary",
        "",
        f"- **Dominant Mechanism**: {dominant}",
        f"- **Gate Pass**: {gate_pass}",
        f"- **H1 Confirmed**: {mechanism_result.get('h1_confirmed', False)}",
        f"- **H2 Dominant**: {mechanism_result.get('h2_dominant', False)}",
        f"- **H3 Flag**: {mechanism_result.get('h3_flag', False)}",
        "",
        "## Spearman Rho Results",
        "",
        "| Pair | Mean Rho | H1 Pass | H2 Flag |",
        "|------|----------|---------|---------|",
    ]

    for pair_key, res in sorted(spearman_results.items()):
        lines.append(
            f"| {pair_key} | {res['mean_rho']:.4f} | {res['h1_pass']} | {res['h2_flag']} |"
        )

    lines += [
        "",
        "## Argmax Partition Results",
        "",
        "| Pair | N Shared | N Changed | Rel Shared (aligned) | Rel Changed (aligned) | Cohen's d | H1 Sig |",
        "|------|----------|-----------|---------------------|----------------------|-----------|--------|",
    ]

    for pair_key, res in sorted(partition_results.items()):
        lines.append(
            f"| {pair_key} | {res['n_shared']} | {res['n_changed']} | "
            f"{res['rel_shared_aligned']:.4f} | {res['rel_changed_aligned']:.4f} | "
            f"{res['cohens_d_shared']:.4f} | {res['h1_signature']} |"
        )

    lines += [
        "",
        "## TruthfulQA ECE Results",
        "",
        "| Model | ECE | N Items |",
        "|-------|-----|---------|",
    ]

    for model_key, res in sorted(tqa_ece_results.items()):
        ece = res.get("ece", float("nan"))
        n = res.get("n_items", 0)
        ece_str = f"{ece:.4f}" if not (isinstance(ece, float) and np.isnan(ece)) else "nan"
        lines.append(f"| {model_key} | {ece_str} | {n} |")

    lines += [
        "",
        "## Per-Alignment Summary",
        "",
    ]
    for alignment, info in mechanism_result.get("per_alignment", {}).items():
        lines.append(f"### {alignment.upper()}")
        lines.append(f"- Mean Rho (avg): {info['mean_rho_avg']:.4f}")
        lines.append(f"- N H1 Signature: {info['n_h1_signature']}")
        lines.append(f"- H3 Signal: {info['h3_signal']}")
        lines.append("")

    exception = mechanism_result.get("6.9b_ppo_exception", "")
    if exception:
        lines += [
            "## 6.9B-PPO Exception",
            "",
            exception,
            "",
        ]

    lines += [
        "## Conclusion",
        "",
        f"The dominant calibration mechanism is **{dominant}**.",
        "",
    ]

    with open(output_path, "w") as f:
        f.write("\n".join(lines) + "\n")

    logger.info("Validation report written to %s", output_path)


def update_verification_state(
    state_path: str,
    gate_pass: bool,
    dominant_mechanism: str,
    key_metrics: dict,
) -> None:
    """Update verification_state.yaml with h-m3 gate result."""
    from config import VERIFICATION_STATE_H_M3_KEY

    if not os.path.exists(state_path):
        logger.warning("verification_state.yaml not found at %s, creating new file.", state_path)
        state = {}
    else:
        if _YAML_AVAILABLE:
            with open(state_path, "r") as f:
                state = yaml.safe_load(f) or {}
        else:
            state = {}
            logger.warning("PyYAML not available; starting with empty state.")

    h_m3_state = {
        "gate_pass": gate_pass,
        "dominant_mechanism": dominant_mechanism,
    }
    h_m3_state.update(key_metrics)

    state[VERIFICATION_STATE_H_M3_KEY] = h_m3_state

    if _YAML_AVAILABLE:
        with open(state_path, "w") as f:
            yaml.dump(state, f, default_flow_style=False, sort_keys=True)
    else:
        # Fallback: write as JSON-like YAML manually for key fields
        with open(state_path, "a") as f:
            f.write(f"\n{VERIFICATION_STATE_H_M3_KEY}:\n")
            for k, v in h_m3_state.items():
                f.write(f"  {k}: {v}\n")

    logger.info("Updated verification_state.yaml: h-m3 gate_pass=%s dominant=%s", gate_pass, dominant_mechanism)


def save_experiment_results(
    all_results: dict,
    output_path: str,
) -> None:
    """Save experiment_results.json with all computed metrics."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    def _serialize(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, (np.int32, np.int64)):
            return int(obj)
        if isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        if isinstance(obj, dict):
            return {k: _serialize(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [_serialize(v) for v in obj]
        return obj

    serializable = _serialize(all_results)

    with open(output_path, "w") as f:
        json.dump(serializable, f, indent=2)

    logger.info("Experiment results saved to %s", output_path)
