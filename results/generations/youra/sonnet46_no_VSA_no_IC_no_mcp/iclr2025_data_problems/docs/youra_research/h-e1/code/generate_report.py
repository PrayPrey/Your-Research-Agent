"""E6: Generate 04_validation.md from statistical results."""
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
STATS_FILE = BASE_DIR / "statistical_results.json"
CHECKPOINT_MAP_FILE = BASE_DIR / "checkpoint_map.json"
REPORT_FILE = BASE_DIR / "04_validation.md"

BENCHMARKS = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
CORRECTED_ALPHA = 0.0125


def gate_passed(stats: dict) -> bool:
    return bool(stats.get("gate_passed", False))


def format_report(stats: dict, checkpoint_map: dict) -> str:
    passed = gate_passed(stats)
    verdict = "PASS" if passed else "FAIL"
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    lines = [
        "# H-E1 Validation Report",
        f"**Hypothesis:** H-E1 — Deduplication Benchmark Signature (EXISTENCE)",
        f"**Generated:** {ts}",
        f"**Gate:** MUST_WORK",
        f"**Verdict:** {verdict}",
        "",
        "---",
        "",
        "## Experiment Setup",
        "",
        "| Parameter | Value |",
        "|-----------|-------|",
        "| Models | Pythia 160M, 410M, 1B, 6.9B (Pile + dedup-Pile) |",
        "| Token matching | Pile step 99,000 ≈ 207B tokens (mismatch <0.3%) |",
        "| dedup-Pile checkpoint | step 143,000 (final) |",
        "| Benchmarks | MMLU (5-shot), HellaSwag (0-shot), ARC-Challenge (25-shot), WinoGrande (5-shot) |",
        "| Statistical test | Paired t-test across 4 model sizes (n=4), two-tailed |",
        "| Significance threshold | Bonferroni-corrected α = 0.0125 (0.05 / 4 benchmarks) |",
        "",
        "## Checkpoint Map",
        "",
        "| Size | Pile step | dedup step | Token mismatch |",
        "|------|-----------|------------|---------------|",
    ]
    for size, info in checkpoint_map.items():
        lines.append(
            f"| {size} | step{info['pile_step']} | step{info['dedup_step']} | {info['token_mismatch_pct']:.2f}% |"
        )

    lines += [
        "",
        "## Statistical Results",
        "",
        "| Benchmark | t-stat | p-value | mean Δ (dedup−pile) | Direction | Significant? |",
        "|-----------|--------|---------|----------------------|-----------|-------------|",
    ]
    for bench in BENCHMARKS:
        r = stats.get(bench, {})
        if r.get("t_stat") is None:
            lines.append(f"| {bench} | — | — | — | insufficient data | No |")
        else:
            sig = "**Yes***" if r["significant"] else "No"
            lines.append(
                f"| {bench} | {r['t_stat']:.3f} | {r['p_value']:.4f} | "
                f"{r['mean_diff']:+.4f} | {r['direction']} | {sig} |"
            )

    lines += [
        "",
        "## Gate Evaluation",
        "",
        f"**Condition:** ≥1 benchmark with p < {CORRECTED_ALPHA} (Bonferroni) across ≥2 model sizes (implicit in paired t-test n=4)",
        "",
        f"**Mechanism Verified:** {stats.get('mechanism_verified', False)}",
        f"**Gate Passed:** {passed}",
        "",
        f"### Verdict: {verdict}",
        "",
    ]

    if passed:
        sig_benches = [b for b in BENCHMARKS if stats.get(b, {}).get("significant")]
        lines += [
            f"Statistically significant deduplication effect detected on: **{', '.join(sig_benches)}**.",
            "",
            "H-E1 EXISTENCE hypothesis confirmed: deduplication produces a detectable benchmark signature.",
            "Proceed to Phase 5 for baseline comparison.",
            "",
        ]
    else:
        lines += [
            "No benchmark reached Bonferroni-corrected significance. H-E1 EXISTENCE hypothesis not confirmed.",
            "",
            "Possible causes:",
            "- Effect is too small to detect with n=4 paired observations",
            "- Token matching introduces noise masking the deduplication signal",
            "- Benchmarks chosen are not sensitive to deduplication",
            "",
            "Return to Phase 2A for hypothesis redesign.",
            "",
        ]

    lines += [
        "---",
        "",
        "## Files",
        "",
        "| File | Description |",
        "|------|-------------|",
        "| `checkpoint_map.json` | Token-matched checkpoint steps |",
        "| `results_matrix.json` | Accuracy[size][corpus][benchmark] |",
        "| `statistical_results.json` | Full t-test results |",
        "| `figures/differential_bar.png` | Per-benchmark accuracy difference |",
        "| `figures/scaling_plot.png` | Scaling curves Pile vs dedup-Pile |",
        "| `figures/paired_scatter.png` | Paired scatter per benchmark |",
        "| `figures/pvalue_heatmap.png` | -log10(p) significance chart |",
    ]

    return "\n".join(lines) + "\n"


def main() -> None:
    stats = json.loads(STATS_FILE.read_text())
    checkpoint_map = json.loads(CHECKPOINT_MAP_FILE.read_text())
    report = format_report(stats, checkpoint_map)
    REPORT_FILE.write_text(report)
    passed = gate_passed(stats)
    print(f"Wrote {REPORT_FILE}")
    print(f"Gate: {'PASS' if passed else 'FAIL'}")


if __name__ == "__main__":
    main()
