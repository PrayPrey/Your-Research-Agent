"""Full pipeline for H-M1 experiment: Error Traces Contain Counterfactual Information."""
import json
import os
import sys
import pandas as pd
from pathlib import Path
import numpy as np
from config import CFG
from data_loader import load_all_problems
from bug_injector import BugInjector
from sandbox_executor import SandboxExecutor
from trace_parser import TraceParser
from cf_annotator import CounterfactualAnnotator
import metrics

def ensure_dirs():
    Path(CFG.data_dir).mkdir(parents=True, exist_ok=True)
    Path(CFG.results_dir).mkdir(parents=True, exist_ok=True)

def run_bug_injection(limit: int = None):
    """Stage 1: Generate buggy samples from correct solutions."""
    print("=== Stage 1: Bug Injection ===")
    ensure_dirs()
    problems = load_all_problems()
    if limit:
        problems = problems[:limit]
    print(f"Loaded {len(problems)} problems")
    injector = BugInjector(seed=CFG.seed)
    all_buggy = []
    for i, problem in enumerate(problems):
        buggy_samples = injector.inject_all_types(problem)
        all_buggy.extend(buggy_samples)
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{len(problems)} problems, {len(all_buggy)} buggy samples")
    output_path = os.path.join(CFG.data_dir, "buggy_samples.jsonl")
    with open(output_path, "w") as f:
        for sample in all_buggy:
            f.write(json.dumps(sample) + "\n")
    print(f"Wrote {len(all_buggy)} buggy samples to {output_path}")
    return all_buggy

def run_execution(limit: int = None):
    """Stage 2: Execute buggy samples and collect traces."""
    print("\n=== Stage 2: Execution ===")
    input_path = os.path.join(CFG.data_dir, "buggy_samples.jsonl")
    with open(input_path) as f:
        samples = [json.loads(line) for line in f]
    if limit:
        samples = samples[:limit]
    print(f"Executing {len(samples)} buggy samples")
    executor = SandboxExecutor()
    results = []
    for i, sample in enumerate(samples):
        result = executor.run(sample["buggy_code"], sample["tests"])
        results.append({
            "id": sample["id"],
            "original_id": sample["original_id"],
            "bug_type": sample["bug_type"],
            "bug_line": sample["bug_line"],
            "bug_description": sample["bug_description"],
            "exit_code": result.exit_code,
            "timed_out": result.timed_out,
            "stdout": result.stdout[:1000] if result.stdout else "",
            "stderr": result.stderr[:2000] if result.stderr else "",
            "traceback": result.traceback[:2000] if result.traceback else "",
        })
        if (i + 1) % 100 == 0:
            print(f"  Executed {i + 1}/{len(samples)}")
    output_path = os.path.join(CFG.data_dir, "execution_traces.jsonl")
    with open(output_path, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    print(f"Wrote {len(results)} traces to {output_path}")
    return results

def run_annotation():
    """Stage 3: Annotate traces with counterfactual information."""
    print("\n=== Stage 3: CF Annotation ===")
    input_path = os.path.join(CFG.data_dir, "execution_traces.jsonl")
    with open(input_path) as f:
        traces = [json.loads(line) for line in f]
    print(f"Annotating {len(traces)} traces")
    parser = TraceParser()
    annotator = CounterfactualAnnotator()
    from sandbox_executor import ExecutionResult
    annotations = []
    for trace in traces:
        exec_result = ExecutionResult(
            stdout=trace["stdout"],
            stderr=trace["stderr"],
            exit_code=trace["exit_code"],
            traceback=trace["traceback"],
            timed_out=trace["timed_out"],
        )
        parsed = parser.parse(exec_result)
        annotation = annotator.annotate(parsed, trace["bug_line"])
        annotations.append({
            "id": trace["id"],
            "original_id": trace["original_id"],
            "bug_type": trace["bug_type"],
            "bug_line": trace["bug_line"],
            "has_line": annotation.has_line,
            "has_expected": annotation.has_expected,
            "has_actual": annotation.has_actual,
            "has_type_info": annotation.has_type_info,
            "has_variable_state": annotation.has_variable_state,
            "identifies_root_cause": annotation.identifies_root_cause,
            "cf_score": annotation.cf_score,
            "line_numbers": parsed.line_numbers,
            "type_info": parsed.type_info,
        })
    output_path = os.path.join(CFG.data_dir, "cf_annotations.jsonl")
    with open(output_path, "w") as f:
        for a in annotations:
            f.write(json.dumps(a) + "\n")
    df = pd.DataFrame(annotations)
    csv_path = os.path.join(CFG.results_dir, "cf_scores.csv")
    df.to_csv(csv_path, index=False)
    print(f"Wrote annotations to {output_path}")
    print(f"Wrote scores to {csv_path}")
    return annotations

def run_analysis():
    """Stage 4: Statistical analysis and report generation."""
    print("\n=== Stage 4: Analysis ===")
    csv_path = os.path.join(CFG.results_dir, "cf_scores.csv")
    df = pd.read_csv(csv_path)
    print(f"Analyzing {len(df)} samples")
    dist = metrics.cf_score_distribution(df)
    hyp_test = metrics.hypothesis_test(df)
    anova = metrics.cf_by_bug_type_anova(df)
    root_cause = metrics.root_cause_accuracy(df)
    above_thresh = metrics.above_threshold_rate(df)
    report = f"""# H-M1 Analysis Report: Error Traces Contain Counterfactual Information

## Summary

- **Total samples**: {len(df)}
- **Mean CF score**: {dist['mean']:.3f}
- **Median CF score**: {dist['median']:.3f}
- **Samples with CF_score >= 0.4**: {above_thresh['count_above']} ({above_thresh['rate']*100:.1f}%)

## Success Criteria Evaluation

| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| CF_score >= 0.4 rate | >70% | {above_thresh['rate']*100:.1f}% | {'PASS' if above_thresh['rate'] > 0.7 else 'FAIL'} |
| Mean CF_score | >0.5 | {dist['mean']:.3f} | {'PASS' if dist['mean'] > 0.5 else 'FAIL'} |
| Root cause accuracy | >60% | {root_cause['overall']*100:.1f}% | {'PASS' if root_cause['overall'] > 0.6 else 'FAIL'} |

## Gate Verdict

**{'PASS' if above_thresh['rate'] > 0.7 else 'EXPLORE' if above_thresh['rate'] >= 0.5 else 'FAIL'}**: {above_thresh['rate']*100:.1f}% of traces have CF_score >= 0.4

## CF Score Distribution

- Mean: {dist['mean']:.3f}
- Median: {dist['median']:.3f}
- Std: {dist['std']:.3f}
- 70th percentile: {dist['p70']:.3f}
- Min: {dist['min']:.3f}
- Max: {dist['max']:.3f}

## Hypothesis Test

H0: mean CF_score <= {hyp_test['threshold']}
H1: mean CF_score > {hyp_test['threshold']}

- t-statistic: {hyp_test['t_statistic']:.3f}
- p-value (one-sided): {hyp_test['p_value_one_sided']:.4f}
- **Result**: {'Reject H0' if hyp_test['reject_null'] else 'Fail to reject H0'}

## CF Score by Bug Type (ANOVA)

"""
    if anova["f_statistic"]:
        report += f"- F-statistic: {anova['f_statistic']:.3f}\n"
        report += f"- p-value: {anova['p_value']:.4f}\n"
        report += f"- Significant difference: {'Yes' if anova['significant'] else 'No'}\n\n"
        report += "| Bug Type | Mean CF Score |\n|----------|---------------|\n"
        for bt, mean in anova["group_means"].items():
            report += f"| {bt} | {mean:.3f} |\n"
    report += f"""
## Root Cause Identification

- Overall accuracy: {root_cause['overall']*100:.1f}%

| Bug Type | Accuracy |
|----------|----------|
"""
    for bt, acc in root_cause["by_bug_type"].items():
        report += f"| {bt} | {acc*100:.1f}% |\n"
    report += f"""
## Feature Presence

| Feature | Present Rate |
|---------|--------------|
| has_line | {df['has_line'].mean()*100:.1f}% |
| has_expected | {df['has_expected'].mean()*100:.1f}% |
| has_actual | {df['has_actual'].mean()*100:.1f}% |
| has_type_info | {df['has_type_info'].mean()*100:.1f}% |
| has_variable_state | {df['has_variable_state'].mean()*100:.1f}% |
"""
    report_path = os.path.join(CFG.results_dir, "analysis_report.md")
    with open(report_path, "w") as f:
        f.write(report)
    print(f"Wrote report to {report_path}")
    def convert_numpy(obj):
        if isinstance(obj, (np.bool_, np.integer)):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, dict):
            return {k: convert_numpy(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [convert_numpy(i) for i in obj]
        return obj
    results = convert_numpy({
        "distribution": dist,
        "hypothesis_test": hyp_test,
        "anova": anova,
        "root_cause": root_cause,
        "above_threshold": above_thresh,
        "gate_result": "PASS" if above_thresh['rate'] > 0.7 else "EXPLORE" if above_thresh['rate'] >= 0.5 else "FAIL",
    })
    results_path = os.path.join(CFG.results_dir, "experiment_results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Wrote results to {results_path}")
    return results

def main(stage: str = "all", limit: int = None):
    """Run pipeline stages."""
    print(f"H-M1 Pipeline: stage={stage}, limit={limit}")
    if stage in ("all", "inject"):
        run_bug_injection(limit)
    if stage in ("all", "execute"):
        run_execution(limit)
    if stage in ("all", "annotate"):
        run_annotation()
    if stage in ("all", "analyze"):
        results = run_analysis()
        print(f"\n=== GATE RESULT: {results['gate_result']} ===")
        return results
    return None

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", default="all", choices=["all", "inject", "execute", "annotate", "analyze"])
    parser.add_argument("--limit", type=int, default=None, help="Limit number of problems (for testing)")
    args = parser.parse_args()
    main(args.stage, args.limit)
