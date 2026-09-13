"""Main pipeline for H-M2: Proof Depth Filtering Analysis."""
import sys
import os
from pathlib import Path
from datetime import datetime
from config import validate_config
from proof_runner import ProofRunner
from tactic_extractor import TacticExtractor
from analyzer import StratificationAnalyzer


def write_report(analysis_results: dict, output_dir: str):
    """Generate validation report."""
    report_path = f"{output_dir}/04_validation.md"

    strat = analysis_results["stratified_results"]
    stats = analysis_results["statistical_tests"]
    gate = analysis_results["gate_evaluation"]

    with open(report_path, "w") as f:
        f.write("# Validation Report: H-M2\n")
        f.write("# Proof Depth Filtering Analysis\n\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Hypothesis ID**: h-m2\n")
        f.write(f"**Gate Type**: SHOULD_WORK\n\n")

        f.write("---\n\n")
        f.write("## Executive Summary\n\n")

        gate_outcome = "PASS" if gate["pass"] else "FAIL"
        f.write(f"**Outcome**: {gate_outcome}\n\n")

        f.write(f"**Key Finding**: Proof depth filtering (≤3 tactics) reduces LLM success rate by **{strat['delta']:.1%}** ")
        f.write(f"({strat['delta']*100:.1f} percentage points).\n\n")

        f.write(f"- Success (all depths): {strat['success_full']:.1%} ({strat['n_solved_full']}/{strat['n_total']})\n")
        f.write(f"- Success (shallow only): {strat['success_shallow']:.1%} ({strat['n_solved_shallow']}/{strat['n_total']})\n")
        f.write(f"- Δ = {strat['delta']:.1%}\n\n")

        f.write(f"**Gate Criteria**: {gate['target_range'][0]:.0%} < Δ < {gate['target_range'][1]:.0%}\n")
        f.write(f"**Result**: {'Within bounds → PASS' if gate['pass'] else 'Outside bounds → FAIL'}\n\n")

        f.write("---\n\n")
        f.write("## Experimental Results\n\n")

        f.write("### Stratified Success Rates\n\n")
        f.write(f"| Metric | Value |\n")
        f.write(f"|--------|-------|\n")
        f.write(f"| Total problems | {strat['n_total']} |\n")
        f.write(f"| Solved (all depths) | {strat['n_solved_full']} ({strat['success_full']:.1%}) |\n")
        f.write(f"| Solved (shallow ≤3) | {strat['n_solved_shallow']} ({strat['success_shallow']:.1%}) |\n")
        f.write(f"| Δ (effect size) | {strat['delta']:.1%} ({strat['delta']*100:.1f} pp) |\n\n")

        f.write("### Depth Distribution\n\n")
        dist = strat["depth_distribution"]
        f.write(f"- **Shallow** (≤3 tactics): {dist['shallow']} problems\n")
        f.write(f"- **Medium** (4-10 tactics): {dist['medium']} problems\n")
        f.write(f"- **Deep** (>10 tactics): {dist['deep']} problems\n\n")

        f.write("### Statistical Validation\n\n")
        f.write(f"**McNemar Test**:\n")
        f.write(f"- χ² statistic: {stats['mcnemar_chi2']:.3f}\n")
        f.write(f"- p-value: {stats['mcnemar_pvalue']:.4f}\n")
        f.write(f"- Significant (α=0.05): {'Yes' if stats['is_significant'] else 'No'}\n\n")

        f.write(f"**Bootstrap 95% CI for Δ**:\n")
        f.write(f"- Lower bound: {stats['bootstrap_ci_lower']:.1%}\n")
        f.write(f"- Upper bound: {stats['bootstrap_ci_upper']:.1%}\n\n")

        f.write(f"**Power Analysis**:\n")
        f.write(f"- Solved problems: {strat['n_solved_full']}\n")
        f.write(f"- Minimum required: 30\n")
        f.write(f"- Sufficient power: {'Yes' if stats['sufficient_power'] else 'No'}\n\n")

        f.write("---\n\n")
        f.write("## Gate Evaluation\n\n")

        f.write(f"**Hypothesis**: Depth filtering drops success by 10-20 pp (testing 30% contribution claim)\n\n")
        f.write(f"**Gate Criteria**: SHOULD_WORK → 5% < Δ < 30%\n\n")
        f.write(f"**Measured Δ**: {strat['delta']:.1%} ({strat['delta']*100:.1f} pp)\n\n")

        if gate["pass"]:
            f.write("**Result**: ✓ PASS (within target range)\n\n")
            f.write("**Interpretation**: Proof depth contributes a measurable portion of LLM advantage, ")
            f.write("consistent with the 30% attribution claim. The effect size suggests depth filtering ")
            f.write(f"accounts for approximately {strat['delta']*100/50:.0f}% of the baseline gap (assuming 50pp LLM advantage).\n\n")
        else:
            f.write("**Result**: ✗ FAIL (outside target range)\n\n")
            if strat['delta'] < gate['target_range'][0]:
                f.write(f"**Interpretation**: Δ = {strat['delta']:.1%} < 5% → depth contributes <8% of advantage, ")
                f.write("rejecting the 30% attribution claim.\n\n")
            else:
                f.write(f"**Interpretation**: Δ = {strat['delta']:.1%} > 30% → depth explains >60% of advantage, ")
                f.write("contradicting NL understanding dominance (60% claim).\n\n")

        f.write("---\n\n")
        f.write("## Limitations\n\n")

        f.write("### Post-hoc Analysis Constraints\n")
        f.write("- **Search bias**: LLM may preferentially find shallow proofs (not a controlled ablation)\n")
        f.write("- **Difficulty confound**: Shallow-solvable problems may be inherently easier\n")
        f.write("- **Observational**: Cannot establish causal claim (depth *causes* advantage)\n\n")

        f.write("### Tactic Extraction\n")
        f.write("- **Mock data**: This implementation uses synthetic proofs (real data requires LLM API)\n")
        f.write("- **Fallback metric**: Production version would use Lean 4 AST parsing\n\n")

        f.write("### Statistical Considerations\n")
        if not stats['sufficient_power']:
            f.write("- **Power warning**: <30 solved problems, results may be unreliable\n")
        if not stats['is_significant']:
            f.write("- **Non-significant**: McNemar test p > 0.05 (no statistical evidence for effect)\n")
        f.write("\n")

        f.write("---\n\n")
        f.write("## Files Generated\n\n")
        f.write("- `proofs.json`: All successful proofs (mock data)\n")
        f.write("- `tactic_counts.csv`: Extracted tactic depths per theorem\n")
        f.write("- `results.json`: Stratified success rates and statistics\n")
        f.write("- `depth_histogram.png`: Tactic count distribution visualization\n")
        f.write("- `04_validation.md`: This report\n\n")

        f.write("---\n\n")
        f.write(f"**Validation Status**: {'CONFIRMED' if gate['pass'] else 'REJECTED'}\n")
        f.write(f"**Gate Result**: {'PASS' if gate['pass'] else 'FAIL'}\n")

    print(f"[Report] Saved validation report to {report_path}")


def main():
    """Execute H-M2 pipeline."""
    print("[Main] Starting H-M2: Proof Depth Filtering Analysis")
    print("[Main] Validating configuration...")
    validate_config()
    print("[Main] Configuration valid\n")

    # Set output directory
    output_dir = Path(__file__).parent.parent / "results"
    output_dir.mkdir(exist_ok=True)
    output_dir = str(output_dir)

    print(f"[Main] Output directory: {output_dir}\n")

    # A-1: Infrastructure (config validation done)
    print("[Main] Task A-1: Infrastructure Setup - COMPLETE\n")

    # A-2: Proof Collection
    print("[Main] Task A-2: Proof Collection")
    runner = ProofRunner(output_dir)
    proof_stats = runner.collect_all_proofs()
    print()

    # A-3: Tactic Extraction
    print("[Main] Task A-3: Tactic Extraction")
    extractor = TacticExtractor(output_dir)
    extraction_stats = extractor.process_proofs()
    print()

    # A-4: Statistical Analysis
    print("[Main] Task A-4: Statistical Analysis")
    analyzer = StratificationAnalyzer(output_dir)
    analysis_results = analyzer.run_full_analysis()
    print()

    # A-5: Report Generation
    print("[Main] Task A-5: Report Generation")
    write_report(analysis_results, output_dir)
    print()

    print("[Main] Pipeline complete!")
    print(f"[Main] Gate outcome: {'PASS' if analysis_results['gate_evaluation']['pass'] else 'FAIL'}")


if __name__ == "__main__":
    main()
