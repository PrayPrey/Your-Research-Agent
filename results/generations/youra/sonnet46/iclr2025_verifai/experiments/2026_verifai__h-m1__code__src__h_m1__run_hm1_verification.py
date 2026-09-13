"""H-M1: Main entry point for pass@1 coverage verification."""
from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from h_m1.verify_coverage import (
    MODEL_SHORT_NAMES,
    DEFAULT_H_E1_RESULTS,
    run_verification,
)
from h_m1.visualize_hm1 import (
    plot_coverage_rates,
    plot_coverage_heatmap,
    plot_pass_at_1_histograms,
    plot_pass_at_1_cdf,
)

logger = logging.getLogger(__name__)

DEFAULT_OUTPUT_DIR: str = "results"
DEFAULT_FIGURES_DIR: str = "figures"


# ─── Argument parsing ─────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="H-M1: Verify pass@1 coverage from h-e1 results."
    )
    parser.add_argument(
        "--h_e1_results_dir",
        type=str,
        default=DEFAULT_H_E1_RESULTS,
        help=f"Path to h-e1/results/ directory (default: {DEFAULT_H_E1_RESULTS})",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory for JSON/CSV results (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--figures_dir",
        type=str,
        default=DEFAULT_FIGURES_DIR,
        help=f"Output directory for figures (default: {DEFAULT_FIGURES_DIR})",
    )
    parser.add_argument(
        "--smoke_test",
        action="store_true",
        help="Run on 10-problem subset (no file writes)",
    )
    parser.add_argument(
        "--force_regenerate",
        action="store_true",
        help="Force solution regeneration (not in h-m1 scope — raises NotImplementedError)",
    )
    return parser.parse_args()


# ─── Save verified output (FR-5.1) ────────────────────────────────────────────

def save_verified_output(
    pass_at_1_by_model: dict[str, dict[str, float]],
    coverage_data: dict[str, dict[str, float]],
    gate_pass: bool,
    output_path: Path,
) -> None:
    """Write pass_at_1_hm1_verified.json (FR-5.1 schema).

    Schema:
        {
            "metadata": {
                "source": "h-e1",
                "verification_status": "PASS"|"FAIL",
                "coverage_combined": {model_short: float},
                "timestamp": "<ISO-8601>"
            },
            "models": {
                "<hf_model_id>": {task_id: float}
            }
        }
    """
    # Short name → coverage combined
    coverage_combined = {
        model_short: data.get("combined", 0.0)
        for model_short, data in coverage_data.items()
    }

    # Reverse mapping: short name → HF model ID
    short_to_hf = {v: k for k, v in MODEL_SHORT_NAMES.items()}

    # Build models dict with HF model IDs as keys
    models_dict = {}
    for model_short, p1 in pass_at_1_by_model.items():
        hf_id = short_to_hf.get(model_short, model_short)
        models_dict[hf_id] = p1

    output = {
        "metadata": {
            "source": "h-e1",
            "verification_status": "PASS" if gate_pass else "FAIL",
            "coverage_combined": coverage_combined,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        "models": models_dict,
    }

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    logger.info(f"Saved verified output → {output_path}")


# ─── Save coverage report ─────────────────────────────────────────────────────

def save_coverage_report(
    coverage_data: dict[str, dict[str, float]],
    stats_by_model: dict[str, dict],
    gate_results: dict,
    output_dir: Path,
) -> None:
    """Write coverage_report.json and coverage_report.csv.

    JSON structure:
        {
            "timestamp": "<ISO-8601>",
            "models": {
                "model_short": {
                    "coverage": {humaneval, mbpp, combined},
                    "stats": {mean, std, min, max, histogram_6pt, non_trivial},
                    "gate": {gate_pass, checks}
                }
            },
            "overall_gate_pass": bool
        }

    CSV columns: model,benchmark,coverage,mean,std,min,max,gate_pass
    (3 rows per model: humaneval, mbpp, combined)
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    overall_gate_pass = all(r.get("gate_pass", False) for r in gate_results.values())

    # Build JSON report
    models_report = {}
    for model_short in coverage_data:
        models_report[model_short] = {
            "coverage": coverage_data[model_short],
            "stats": stats_by_model.get(model_short, {}),
            "gate": gate_results.get(model_short, {}),
        }

    json_report = {
        "timestamp": timestamp,
        "models": models_report,
        "overall_gate_pass": overall_gate_pass,
    }

    json_path = output_dir / "coverage_report.json"
    with open(json_path, "w") as f:
        json.dump(json_report, f, indent=2)
    logger.info(f"Saved coverage_report.json → {json_path}")

    # Build CSV report: 3 rows per model
    csv_path = output_dir / "coverage_report.csv"
    fieldnames = ["model", "benchmark", "coverage", "mean", "std", "min", "max", "gate_pass"]

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for model_short, cov in coverage_data.items():
            stats = stats_by_model.get(model_short, {})
            gate = gate_results.get(model_short, {})
            gate_pass = gate.get("gate_pass", False)

            for bench in ["humaneval", "mbpp", "combined"]:
                row = {
                    "model": model_short,
                    "benchmark": bench,
                    "coverage": cov.get(bench, 0.0),
                    "mean": stats.get("mean", "") if bench == "combined" else "",
                    "std": stats.get("std", "") if bench == "combined" else "",
                    "min": stats.get("min", "") if bench == "combined" else "",
                    "max": stats.get("max", "") if bench == "combined" else "",
                    "gate_pass": gate_pass,
                }
                writer.writerow(row)

    logger.info(f"Saved coverage_report.csv → {csv_path}")


# ─── Format gate output ───────────────────────────────────────────────────────

def format_gate_output(
    overall_gate_pass: bool,
    per_model_results: dict[str, dict],
    coverage_data: dict[str, dict[str, float]],
) -> str:
    """Format gate result for structured stdout output."""
    lines = [
        "",
        "=" * 40,
        "H-M1 Gate Result",
        "=" * 40,
        f"Overall: {'PASS' if overall_gate_pass else 'FAIL'}",
        "Models:",
    ]

    has_partial = False
    for model_short, res in per_model_results.items():
        status = "PASS" if res["gate_pass"] else "FAIL"
        cov = coverage_data.get(model_short, {}).get("combined", 0.0)
        std = res.get("std", 0.0)
        lines.append(f"  {model_short}: {status} (coverage={cov:.4f}, std={std:.4f})")
        if res.get("partial", False):
            has_partial = True

    if has_partial:
        n_pass = sum(1 for r in per_model_results.values() if r["gate_pass"])
        lines.append(f"[WARN: PARTIAL - {n_pass}/3 models pass gate]")

    lines.append("=" * 40)
    return "\n".join(lines)


# ─── Main entry point ─────────────────────────────────────────────────────────

def main() -> None:
    """Main entry point.

    Exit codes:
        0 → gate PASS
        1 → gate FAIL or PARTIAL
        2 → runtime error (file missing, exception)
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    args = parse_args()

    h_e1_results_dir = Path(args.h_e1_results_dir)
    output_dir = Path(args.output_dir)
    figures_dir = Path(args.figures_dir)

    try:
        results = run_verification(
            h_e1_results_dir=h_e1_results_dir,
            output_dir=output_dir,
            smoke_test=args.smoke_test,
            force_regenerate=args.force_regenerate,
        )
    except Exception as e:
        logger.error(f"Verification failed: {e}", exc_info=True)
        sys.exit(2)

    overall_gate_pass = results["overall_gate_pass"]
    pass_at_1_by_model = results["pass_at_1_by_model"]
    coverage_data = results["coverage_data"]
    stats_by_model = results["stats_by_model"]
    gate_results = results["gate_results"]

    # Save outputs (skip in smoke test mode)
    if not args.smoke_test:
        try:
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save verified output
            verified_path = output_dir / "pass_at_1_hm1_verified.json"
            save_verified_output(
                pass_at_1_by_model, coverage_data, overall_gate_pass, verified_path
            )

            # Save coverage report
            save_coverage_report(coverage_data, stats_by_model, gate_results, output_dir)

            # Generate figures
            figures_dir.mkdir(parents=True, exist_ok=True)
            plot_coverage_rates(coverage_data, str(figures_dir / "coverage_rates.png"))
            plot_coverage_heatmap(coverage_data, str(figures_dir / "coverage_heatmap.png"))
            plot_pass_at_1_histograms(pass_at_1_by_model, str(figures_dir / "pass_at_1_histograms.png"))
            plot_pass_at_1_cdf(pass_at_1_by_model, str(figures_dir / "pass_at_1_cdf.png"))

        except Exception as e:
            logger.error(f"Failed to save outputs: {e}", exc_info=True)
            sys.exit(2)

    # Print gate result
    gate_str = format_gate_output(overall_gate_pass, gate_results, coverage_data)
    print(gate_str)
    if not args.smoke_test:
        print(f"Output: {output_dir / 'pass_at_1_hm1_verified.json'}")

    sys.exit(0 if overall_gate_pass else 1)


if __name__ == "__main__":
    main()
