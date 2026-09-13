"""Gate evaluation and results saving for H-M3 analysis."""
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict
import numpy as np

from config import AnalysisConfig


def evaluate_gate_condition(
    g3_rate: float,
    g4_rate: float,
    mcnemar_pvalue: float,
    margin: float = 0.02
) -> Dict:
    """Evaluate H-M3 gate condition.

    Gate Logic:
    - PASS if McNemar p >= 0.05 (no significant difference)
    - PASS if p < 0.05 AND G3 > G4 (G3 significantly superior)
    - FAIL if p < 0.05 AND G4 > G3 (G4 significantly better - contradicts non-monotonicity)

    Args:
        g3_rate: G3 success rate
        g4_rate: G4 success rate
        mcnemar_pvalue: p-value from McNemar's test
        margin: Equivalence margin (default 0.02 = 2%)

    Returns:
        Dict with gate evaluation results
    """
    difference = g4_rate - g3_rate
    within_margin = difference <= margin
    significant = mcnemar_pvalue < 0.05

    # Gate logic
    if not significant:
        # No significant difference - supports non-monotonicity (G3 ~ G4)
        gate_passed = True
        reason = f"No significant difference (p={mcnemar_pvalue:.4f} >= 0.05): G3 and G4 are comparable"
    elif g3_rate >= g4_rate:
        # G3 significantly better or equal - supports non-monotonicity
        gate_passed = True
        reason = f"G3 >= G4 with significant difference (p={mcnemar_pvalue:.4f}): G3 superior confirms non-monotonicity"
    else:
        # G4 significantly better - contradicts non-monotonicity hypothesis
        gate_passed = False
        reason = f"G4 significantly outperforms G3 (p={mcnemar_pvalue:.4f}, diff={difference*100:.2f}%): contradicts non-monotonicity"

    result = {
        "g3_rate": g3_rate,
        "g4_rate": g4_rate,
        "difference": difference,
        "margin": margin,
        "within_margin": within_margin,
        "mcnemar_pvalue": mcnemar_pvalue,
        "significant": significant,
        "gate_passed": gate_passed,
        "reason": reason
    }

    status = "PASS" if gate_passed else "FAIL"
    print(f"\n{'='*60}")
    print(f"GATE EVALUATION: {status}")
    print(f"{'='*60}")
    print(f"G3 rate: {g3_rate*100:.2f}%")
    print(f"G4 rate: {g4_rate*100:.2f}%")
    print(f"Difference (G4-G3): {difference*100:.2f}%")
    print(f"Within {margin*100:.0f}% margin: {within_margin}")
    print(f"McNemar p-value: {mcnemar_pvalue:.4f}")
    print(f"Reason: {reason}")
    print(f"{'='*60}\n")

    return result


def save_results(
    contingency_table: np.ndarray,
    mcnemar_result: Dict,
    tost_result: Dict,
    ci_result: Dict,
    gate_result: Dict,
    cfg: AnalysisConfig
) -> None:
    """Save all results to JSON and YAML files.

    Args:
        contingency_table: 2x2 McNemar table
        mcnemar_result: McNemar test results
        tost_result: TOST equivalence results
        ci_result: Confidence interval results
        gate_result: Gate evaluation results
        cfg: Analysis configuration
    """
    # Ensure output directories exist
    Path(cfg.results_dir).mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().isoformat()

    # Save contingency table as JSON
    contingency_data = {
        "table": contingency_table.tolist(),
        "labels": {
            "rows": ["G3_success", "G3_fail"],
            "cols": ["G4_success", "G4_fail"]
        },
        "cells": {
            "both_success": int(contingency_table[0, 0]),
            "g3_only": int(contingency_table[0, 1]),
            "g4_only": int(contingency_table[1, 0]),
            "both_fail": int(contingency_table[1, 1])
        },
        "generated_at": timestamp
    }
    with open(cfg.output_contingency, 'w') as f:
        json.dump(contingency_data, f, indent=2)
    print(f"Saved contingency table to {cfg.output_contingency}")

    # Save statistical tests as YAML
    stats_data = {
        "mcnemar": {
            "statistic": float(mcnemar_result["statistic"]),
            "pvalue": float(mcnemar_result["pvalue"]),
            "significant": bool(mcnemar_result["significant"]),
            "interpretation": mcnemar_result["interpretation"]
        },
        "tost": {
            "g3_rate": float(tost_result["g3_rate"]),
            "g4_rate": float(tost_result["g4_rate"]),
            "difference": float(tost_result["difference"]),
            "margin": float(tost_result["margin"]),
            "p_lower": float(tost_result["p_lower"]),
            "p_upper": float(tost_result["p_upper"]),
            "tost_pvalue": float(tost_result["tost_pvalue"]),
            "equivalent": bool(tost_result["equivalent"]),
            "interpretation": tost_result["interpretation"]
        },
        "confidence_interval": {
            "point_estimate": float(ci_result["point_estimate"]),
            "ci_lower": float(ci_result["ci_lower"]),
            "ci_upper": float(ci_result["ci_upper"]),
            "confidence": float(ci_result["confidence"]),
            "interpretation": ci_result["interpretation"]
        },
        "generated_at": timestamp
    }
    with open(cfg.output_stats, 'w') as f:
        yaml.dump(stats_data, f, default_flow_style=False)
    print(f"Saved statistical tests to {cfg.output_stats}")

    # Save gate metrics as YAML
    metrics_data = {
        "gate": {
            "g3_rate": float(gate_result["g3_rate"]),
            "g4_rate": float(gate_result["g4_rate"]),
            "difference": float(gate_result["difference"]),
            "margin": float(gate_result["margin"]),
            "within_margin": bool(gate_result["within_margin"]),
            "mcnemar_pvalue": float(gate_result["mcnemar_pvalue"]),
            "gate_passed": bool(gate_result["gate_passed"]),
            "reason": gate_result["reason"]
        },
        "generated_at": timestamp
    }
    with open(cfg.output_metrics, 'w') as f:
        yaml.dump(metrics_data, f, default_flow_style=False)
    print(f"Saved gate metrics to {cfg.output_metrics}")
