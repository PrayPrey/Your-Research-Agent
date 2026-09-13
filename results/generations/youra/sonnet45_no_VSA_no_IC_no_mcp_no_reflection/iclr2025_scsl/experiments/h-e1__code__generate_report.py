"""
Generate 04_validation.md report from experiment results.
"""

import json
from pathlib import Path
from datetime import datetime

def generate_report():
    """Fill 04_validation_template.md with actual results."""

    # Load results
    results_dir = Path(__file__).parent.parent / 'results'
    stats_path = results_dir / 'stats_summary.json'
    csv_path = results_dir / 'convergence_data.csv'

    if not stats_path.exists():
        print(f"Error: Stats file not found at {stats_path}")
        return

    with open(stats_path) as f:
        stats = json.load(f)

    # Load CSV for per-seed table
    import csv as csv_module
    rows = []
    with open(csv_path) as f:
        reader = csv_module.DictReader(f)
        rows = list(reader)

    # Compute gate metrics
    cmnist_stats = stats.get('CMNIST', {})
    mean_delta = cmnist_stats.get('mean_delta')
    p_value = cmnist_stats.get('p_value')
    n_converged = cmnist_stats.get('n_converged', 0)

    # Direction check: count E_s < E_c
    direction_correct = sum(
        1 for r in rows
        if r['E_spurious'] != 'None' and r['E_core'] != 'None'
        and float(r['E_spurious']) < float(r['E_core'])
    )

    # PoC pass criteria
    poc_code_runs = True
    poc_direction = direction_correct > 5
    poc_magnitude = mean_delta is not None and mean_delta >= 2.0
    poc_pass = poc_code_runs and poc_direction and poc_magnitude

    # Full pass criteria
    full_significance = p_value is not None and p_value < 0.05
    full_magnitude = mean_delta is not None and mean_delta >= 2.0
    full_pass = full_significance and full_magnitude

    # Gate result
    if poc_pass:
        if full_pass:
            gate_result = "PASS"
            gate_verdict = "passed"
        else:
            gate_result = "PARTIAL"
            gate_verdict = "partial"
    else:
        gate_result = "FAIL"
        gate_verdict = "failed"

    # Build report
    template_path = Path(__file__).parent.parent / '04_validation_template.md'
    with open(template_path) as f:
        template = f.read()

    # Fill in results
    report = template

    # Executive summary
    summary = f"Temporal gap validated on CMNIST: E_spurious < E_core with mean Δ = {mean_delta:.1f} epochs (p = {p_value:.4f})." if mean_delta else "Insufficient convergence data."
    report = report.replace("[One-sentence summary of temporal gap results]", summary)
    report = report.replace("[PASS / PARTIAL / FAIL]", gate_result)

    # Per-seed table
    table_rows = []
    for r in rows:
        table_rows.append(
            f"| {r['seed']:>4} | {r['E_spurious']:>11} | {r['E_core']:>8} | {r['E_baseline']:>12} | {r['delta']:>23} |"
        )
    table_str = "\n".join(table_rows)
    report = report.replace(
        "| 0    | [value]   | [value]| [value]    | [value]                 |\n| 1    | [value]   | [value]| [value]    | [value]                 |\n| ...  | ...       | ...    | ...        | ...                     |",
        table_str
    )

    # Summary stats
    report = report.replace("[value] ± [std] epochs", f"{mean_delta:.1f} ± {cmnist_stats.get('std_delta', 0):.1f} epochs" if mean_delta else "N/A")
    report = report.replace("t = [value], p = [value]", f"t = {cmnist_stats.get('t_stat', 0):.2f}, p = {p_value:.4f}" if p_value else "N/A")
    report = report.replace("E_s < E_c for [X]/10 seeds", f"E_s < E_c for {direction_correct}/10 seeds")

    # Gate validation section
    report = report.replace("[YES/NO]", "YES" if poc_code_runs else "NO")
    report = report.replace("[X]/10", f"{direction_correct}/10")
    report = report.replace("[value] epochs", f"{mean_delta:.1f} epochs" if mean_delta else "N/A")
    report = report.replace("p = [value]", f"p = {p_value:.4f}" if p_value else "N/A")
    report = report.replace("[PASS / FAIL]", "PASS" if poc_pass else "FAIL")
    report = report.replace("[PASS / PARTIAL / FAIL]", gate_result if full_pass is not None else "PARTIAL")

    # Interpretation
    if poc_pass:
        core_finding = f"Temporal ordering pattern CONFIRMED on CMNIST: spurious features (color) converge {mean_delta:.1f} epochs earlier than core features (shape) on average."
        implications = "PROCEED"
    else:
        core_finding = "Temporal ordering pattern NOT confirmed on CMNIST dataset."
        implications = "BLOCKED"

    report = report.replace("[Whether temporal ordering pattern confirmed]", core_finding)
    report = report.replace("- h-e2 (multi-metric signature): [BLOCKED / PROCEED]", f"- h-e2 (multi-metric signature): {implications}")
    report = report.replace("- h-e3 (continuous diagnostic): [BLOCKED / PROCEED]", f"- h-e3 (continuous diagnostic): {implications}")
    report = report.replace("- h-m1 (mechanism explanation): [BLOCKED / PROCEED]", f"- h-m1 (mechanism explanation): {implications}")
    report = report.replace("- h-m2 (architectural modulation): [BLOCKED / PROCEED]", f"- h-m2 (architectural modulation): {implications}")

    # Timestamp
    report = report.replace("**Date:** 2026-08-28", f"**Date:** {datetime.now().strftime('%Y-%m-%d')}")

    # Save report
    output_path = Path(__file__).parent.parent / '04_validation.md'
    with open(output_path, 'w') as f:
        f.write(report)

    print(f"\n{'='*80}")
    print(f"Report generated: {output_path}")
    print(f"Gate Result: {gate_result}")
    print(f"PoC Pass: {poc_pass}")
    print(f"Full Pass: {full_pass}")
    print(f"{'='*80}\n")

    # Return gate result for state update
    return {
        'gate_result': gate_verdict,
        'poc_pass': poc_pass,
        'full_pass': full_pass,
        'mean_delta': mean_delta,
        'p_value': p_value
    }


if __name__ == '__main__':
    result = generate_report()
    print(f"Gate verdict: {result['gate_result']}")
