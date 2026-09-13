"""JSON serialization and results summary generation."""
from __future__ import annotations
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
import config


def _to_serializable(obj):
    if isinstance(obj, dict):
        return {k: _to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_to_serializable(x) for x in obj]
    elif hasattr(obj, "__dataclass_fields__"):
        return {f: _to_serializable(getattr(obj, f)) for f in obj.__dataclass_fields__}
    elif hasattr(obj, "item"):
        return obj.item()
    return obj


def save_correlation_matrix(corr_by_model: dict, out_path: str) -> None:
    serialized = {}
    for model_size, matrix in corr_by_model.items():
        serialized[model_size] = {}
        for domain, benchmarks in matrix.items():
            serialized[model_size][domain] = {}
            for benchmark, result in benchmarks.items():
                serialized[model_size][domain][benchmark] = _to_serializable(result)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(serialized, indent=2))


def save_gate_summary(mechanism_activated: bool, indicators: dict, out_path: str) -> None:
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps({
        "mechanism_activated": mechanism_activated,
        "indicators": indicators,
        "gate_type": "SHOULD_WORK",
    }, indent=2))


def save_fisher_tests(test_results: dict, out_path: str) -> None:
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(_to_serializable(test_results), indent=2))


def save_decontamination_report(report: dict, out_path: str) -> None:
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(_to_serializable(report), indent=2))


def write_results_summary(
    indicators: dict,
    corr_by_model: dict,
    test_results: dict,
    out_path: str,
) -> None:
    """Write 04_results_summary.md."""
    wiki = config.FOCAL_DOMAINS["wikipedia"]
    books = config.FOCAL_DOMAINS["books"]

    lines = [
        "# H-M2 Results Summary\n",
        f"## Gate Verdict\n",
        f"- P1 directional count: {indicators['p1_directional_count']}/3 (gate: ≥2)\n",
        f"- P2 directional count: {indicators['p2_directional_count']}/3 (gate: ≥2)\n",
        f"- P1 gate passed: {indicators['p1_gate_passed']}\n",
        f"- P2 gate passed: {indicators['p2_gate_passed']}\n\n",
        "## Focal Correlations\n\n",
        "| Model | ρ(Wiki→MMLU) | ρ(Wiki→HellaSwag) | ρ(Books→HellaSwag) | ρ(Books→MMLU) | N_valid |\n",
        "|-------|-------------|------------------|-------------------|--------------|--------|\n",
    ]
    for model_size in config.MODEL_SIZES:
        matrix = corr_by_model[model_size]
        n = matrix[wiki]["mmlu"].n
        lines.append(
            f"| {model_size} | {matrix[wiki]['mmlu'].rho:.4f} | "
            f"{matrix[wiki]['hellaswag'].rho:.4f} | "
            f"{matrix[books]['hellaswag'].rho:.4f} | "
            f"{matrix[books]['mmlu'].rho:.4f} | {n} |\n"
        )

    lines.append("\n## Fisher z-Tests\n\n")
    lines.append("| Model | P1 z | P1 p | P1 reject | P2 z | P2 p | P2 reject |\n")
    lines.append("|-------|------|------|-----------|------|------|----------|\n")
    for model_size in config.MODEL_SIZES:
        tr = test_results[model_size]
        lines.append(
            f"| {model_size} | {tr['p1']['z_stat']:.3f} | {tr['p1']['p_one_tailed']:.4f} | "
            f"{tr['p1'].get('holm_reject', 'N/A')} | "
            f"{tr['p2']['z_stat']:.3f} | {tr['p2']['p_one_tailed']:.4f} | "
            f"{tr['p2'].get('holm_reject', 'N/A')} |\n"
        )

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text("".join(lines))
