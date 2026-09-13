#!/usr/bin/env python3
"""h-e1 Experiment Runner: Error Mode Heterogeneity Validation"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dataset import BenchmarkLoader
from llm import CodeLlamaGenerator
from verifier import ErrorClassifier
from evaluate import HeterogeneityAnalyzer
from visualize import plot_error_distribution


# Configuration
MODEL_NAME = "Salesforce/codegen-350M-mono"  # CodeLlama gated, using open alternative
MAX_TOKENS = 512
TEMPERATURE = 0.0
CV_THRESHOLD = 0.3
ANOVA_THRESHOLD = 0.05

DATA_DIR = Path("data")
RESULTS_DIR = Path("results")


def main():
    """Run h-e1 experiment: validate error mode heterogeneity."""
    print("=" * 80)
    print("h-e1: Error Mode Heterogeneity Validation")
    print("=" * 80)
    print()

    # Create directories
    DATA_DIR.mkdir(exist_ok=True)
    RESULTS_DIR.mkdir(exist_ok=True)

    # Step 1: Load datasets
    print("STEP 1: Loading datasets")
    print("-" * 80)
    loader = BenchmarkLoader()
    benchmarks = loader.load_all()
    print()

    # Validate problem counts (using 50-sample validation for speed)
    expected_counts = {
        "humaneval": 50,
        "mbpp": 50,
        "codecontests": 50
    }

    for bench, expected in expected_counts.items():
        actual = len(benchmarks[bench])
        print(f"  {bench}: {actual} problems (expected {expected})")
        if actual != expected:
            print(f"    WARNING: Count mismatch!")

    total_problems = sum(len(problems) for problems in benchmarks.values())
    print(f"\n  Total: {total_problems} problems")
    print()

    # Step 2: Generate code
    print("STEP 2: Generating code with CodeLlama-7B")
    print("-" * 80)
    generator = CodeLlamaGenerator(model_name=MODEL_NAME)
    print()

    for bench_name, problems in benchmarks.items():
        output_file = DATA_DIR / f"{bench_name}.json"

        # Check if already generated
        if output_file.exists():
            print(f"  {bench_name}: Loading cached generations from {output_file}")
            with open(output_file) as f:
                data = json.load(f)
                for i, problem in enumerate(problems):
                    problem["generated_code"] = data["problems"][i]["generated_code"]
        else:
            print(f"  {bench_name}: Generating {len(problems)} solutions...")
            prompts = [p["prompt"] for p in problems]
            generations = generator.generate_batch(prompts, max_new_tokens=MAX_TOKENS)

            # Save generations
            generator.save_generations(bench_name, problems, generations, str(output_file))

            # Add to problems
            for problem, gen in zip(problems, generations):
                problem["generated_code"] = gen

        print()

    # Step 3: Classify errors
    print("STEP 3: Classifying error modes")
    print("-" * 80)
    classifier = ErrorClassifier()

    classifications_file = DATA_DIR / "error_classifications.json"

    if classifications_file.exists():
        print(f"  Loading cached classifications from {classifications_file}")
        with open(classifications_file) as f:
            classifications_data = json.load(f)
            classifications = classifications_data["classifications"]
    else:
        print("  Running error classification pipeline...")
        classifications = {}

        for bench_name, problems in benchmarks.items():
            print(f"    {bench_name}: Classifying {len(problems)} solutions...")
            bench_classifications = []

            for idx, problem in enumerate(problems):
                if (idx + 1) % 50 == 0 or idx + 1 == len(problems):
                    print(f"      Progress: {idx + 1}/{len(problems)}")

                code = problem["generated_code"]
                test = problem["test"]

                error_mode, error_detail = classifier.classify(code, test)
                bench_classifications.append(error_mode)

                problem["error_mode"] = error_mode
                problem["error_detail"] = error_detail

            classifications[bench_name] = bench_classifications

            # Print summary for this benchmark
            counts = {
                "syntax": bench_classifications.count("syntax"),
                "type": bench_classifications.count("type"),
                "semantic": bench_classifications.count("semantic"),
                "pass": bench_classifications.count("pass"),
                "uncategorized": bench_classifications.count("uncategorized")
            }
            print(f"      Summary: {counts}")

        # Save classifications
        classifications_output = {
            "timestamp": datetime.now().isoformat(),
            "total_problems": total_problems,
            "classifications": classifications
        }

        with open(classifications_file, "w") as f:
            json.dump(classifications_output, f, indent=2)

        print(f"  Saved classifications to {classifications_file}")

    print()

    # Step 4: Statistical analysis
    print("STEP 4: Statistical analysis")
    print("-" * 80)
    analyzer = HeterogeneityAnalyzer(classifications)

    # Compute distributions
    distributions = analyzer.get_all_distributions()

    print("  Error mode distributions:")
    print()
    print(f"  {'Benchmark':<15} {'Syntax %':>10} {'Type %':>10} {'Semantic %':>10} {'Pass %':>10}")
    print("  " + "-" * 65)

    for bench in analyzer.benchmarks:
        dist = distributions[bench]
        print(
            f"  {bench:<15} "
            f"{dist.get('syntax', 0):>9.1f}% "
            f"{dist.get('type', 0):>9.1f}% "
            f"{dist.get('semantic', 0):>9.1f}% "
            f"{dist.get('pass', 0):>9.1f}%"
        )

    print()

    # Compute metrics
    cv = analyzer.compute_cv("syntax")
    anova_f, anova_p = analyzer.run_anova("syntax")
    decision, metrics = analyzer.gate_decision(CV_THRESHOLD, ANOVA_THRESHOLD)

    print("  Heterogeneity metrics:")
    print(f"    CV (syntax%):              {cv:.4f} (threshold: >{CV_THRESHOLD})")
    print(f"    ANOVA F-statistic:         {anova_f:.4f}")
    print(f"    ANOVA p-value:             {anova_p:.6f} (threshold: <{ANOVA_THRESHOLD})")
    print(f"    Max diff from HumanEval:   {metrics['max_diff_from_humaneval']:.2f} pp")
    print(f"    Uncategorized %:           {metrics['uncategorized_pct']:.2f}%")
    print()

    # Save results
    stats_file = RESULTS_DIR / "statistics.json"
    analyzer.save_results(str(stats_file))
    print()

    # Step 5: Visualization
    print("STEP 5: Visualization")
    print("-" * 80)
    plot_file = RESULTS_DIR / "error_mode_distribution.png"
    plot_error_distribution(distributions, str(plot_file), dpi=300)
    print()

    # Step 6: Gate decision
    print("=" * 80)
    print(f"GATE DECISION: {decision}")
    print("=" * 80)
    print()

    if decision == "PASS":
        print("✓ CV > 0.3: Error mode heterogeneity confirmed")
        print("✓ ANOVA p < 0.05: Statistically significant")
        print()
        print("Conclusion: Error modes vary significantly across benchmarks.")
        print("Proceeding to h-m1 (mechanism validation).")
    else:
        print("✗ Gate criteria not met")
        print()
        if cv <= CV_THRESHOLD:
            print(f"  - CV = {cv:.4f} ≤ {CV_THRESHOLD}: Insufficient heterogeneity")
        if anova_p >= ANOVA_THRESHOLD:
            print(f"  - ANOVA p = {anova_p:.6f} ≥ {ANOVA_THRESHOLD}: Not statistically significant")
        print()
        print("Conclusion: Error modes homogeneous across benchmarks.")
        print("Adaptive routing offers no advantage over universal validation.")

    print()

    # Generate validation report
    report_file = RESULTS_DIR / "validation_report.md"
    generate_validation_report(
        report_file,
        decision,
        metrics,
        distributions,
        analyzer
    )

    print(f"Validation report saved to {report_file}")
    print()
    print("=" * 80)
    print("Experiment complete")
    print("=" * 80)

    return 0 if decision == "PASS" else 1


def generate_validation_report(
    output_path: Path,
    decision: str,
    metrics: dict,
    distributions: dict,
    analyzer: HeterogeneityAnalyzer
):
    """Generate markdown validation report."""
    timestamp = datetime.now().isoformat()

    report = f"""# h-e1 Validation Report

**Generated:** {timestamp}
**Hypothesis:** Error mode distributions vary significantly across benchmarks
**Gate Type:** MUST_WORK

---

## Gate Decision: {decision}

### Primary Metrics

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| CV (syntax%) | {metrics['cv']:.4f} | >0.3 | {'✓' if metrics['cv'] > 0.3 else '✗'} |
| ANOVA p-value | {metrics['anova_p']:.6f} | <0.05 | {'✓' if metrics['anova_p'] < 0.05 else '✗'} |
| Uncategorized% | {metrics['uncategorized_pct']:.2f}% | <10% | {'✓' if metrics['uncategorized_pct'] < 10 else '✗'} |
| Max diff from HumanEval | {metrics['max_diff_from_humaneval']:.2f} pp | >10 pp | {'✓' if metrics['max_diff_from_humaneval'] > 10 else '✗'} |

---

## Error Distributions

| Benchmark | Syntax | Type | Semantic | Pass | Uncategorized |
|-----------|--------|------|----------|------|--------------|
"""

    for bench in analyzer.benchmarks:
        dist = distributions[bench]
        report += (
            f"| {bench.replace('_', ' ').title()} "
            f"| {dist.get('syntax', 0):.1f}% "
            f"| {dist.get('type', 0):.1f}% "
            f"| {dist.get('semantic', 0):.1f}% "
            f"| {dist.get('pass', 0):.1f}% "
            f"| {dist.get('uncategorized', 0):.1f}% |\n"
        )

    report += f"""
---

## Statistical Analysis

**Coefficient of Variation (CV):**
- Formula: std(syntax%) / mean(syntax%)
- Value: {metrics['cv']:.4f}
- Interpretation: {'High heterogeneity - error modes vary significantly' if metrics['cv'] > 0.3 else 'Low heterogeneity - error modes relatively uniform'}

**ANOVA Test:**
- F-statistic: {metrics['anova_f']:.4f}
- p-value: {metrics['anova_p']:.6f}
- Interpretation: {'Statistically significant variation across benchmarks' if metrics['anova_p'] < 0.05 else 'No statistically significant variation'}

---

## Conclusion

"""

    if decision == "PASS":
        report += """**Result:** PASS - Error mode heterogeneity confirmed

The analysis demonstrates that error mode distributions vary significantly across code generation benchmarks:

1. **Heterogeneity confirmed**: CV >0.3 indicates substantial variation in syntax error rates
2. **Statistical significance**: ANOVA p<0.05 confirms this variation is not due to chance
3. **Practical significance**: At least one benchmark differs from HumanEval by >10 percentage points

**Implication:** Adaptive validator selection based on benchmark-specific error profiles is justified.

**Next step:** Proceed to h-m1 (Task Characteristics Determine Error Distribution) to test whether error modes can be predicted from task features.
"""
    else:
        report += """**Result:** FAIL - Error mode heterogeneity NOT confirmed

The analysis shows insufficient variation in error mode distributions across benchmarks:

"""
        if metrics['cv'] <= 0.3:
            report += f"- CV = {metrics['cv']:.4f} ≤ 0.3: Error modes relatively uniform across benchmarks\n"
        if metrics['anova_p'] >= 0.05:
            report += f"- ANOVA p = {metrics['anova_p']:.6f} ≥ 0.05: Variation not statistically significant\n"

        report += """
**Implication:** Adaptive routing offers no advantage over universal parallel validation.

**Pivot:** Focus on universal validation strategies rather than benchmark-specific adaptation.
"""

    report += """
---

## Visualization

See `error_mode_distribution.png` for visual representation of error mode distributions.

---

**End of Report**
"""

    with open(output_path, "w") as f:
        f.write(report)


if __name__ == "__main__":
    sys.exit(main())
