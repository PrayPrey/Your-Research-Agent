"""H-M1 Pipeline: Task Feature Correlation with Error Modes."""
import sys
import json
from pathlib import Path
import pandas as pd
import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

sys.path.append(str(Path(__file__).parent / 'src'))
from features import extract_task_features
from classifier import compute_error_distribution
from correlation import analyze_correlation
from regression import fit_regression, gate_decision
from visualize import plot_gate_metrics, plot_correlation_heatmap, plot_feature_importance, plot_cv_results


CONFIG = {
    "datasets": {
        "humaneval": {
            "hf_identifier": "openai_humaneval",
            "split": "test",
            "poc_limit": 50,
            "production_limit": 164
        },
        "mbpp": {
            "hf_identifier": "mbpp",
            "hf_subset": "sanitized",
            "split": "test",
            "poc_limit": 50,
            "production_limit": 500
        },
        "codecontests": {
            "hf_identifier": "deepmind/code_contests",
            "split": "test",
            "poc_limit": 50,
            "production_limit": 50
        },
        "cache_dir": "~/.cache/huggingface/datasets"
    },
    "model": {
        "model_name": "Salesforce/codegen-350M-mono",
        "cache_dir": "~/.cache/huggingface/hub",
        "generation": {
            "max_new_tokens": 256,
            "temperature": 0.8,
            "top_p": 0.95,
            "num_return_sequences": 1,
            "do_sample": True
        }
    },
    "regression": {
        "r2_threshold": 0.6
    },
    "execution": {
        "mode": "poc",
        "seed": 42,
        "samples_per_problem": 10
    }
}


def run_experiment():
    """Full pipeline: dataset → features → errors → correlation → regression."""
    print("=== H-M1 Experiment: Task Feature Correlation ===\n")
    mode = CONFIG["execution"]["mode"]

    # 1. Load datasets
    print(f"[1/7] Loading datasets ({mode} mode)...")
    benchmarks = {}
    for name, cfg in CONFIG["datasets"].items():
        if name == "cache_dir":
            continue
        print(f"  Loading {name}...")
        limit = cfg[f"{mode}_limit"]
        if name == "mbpp":
            ds = load_dataset(cfg["hf_identifier"], cfg["hf_subset"], split=cfg["split"], trust_remote_code=True)
        else:
            ds = load_dataset(cfg["hf_identifier"], split=cfg["split"], trust_remote_code=True)
        benchmarks[name] = ds.select(range(min(limit, len(ds))))
    print(f"  Loaded: HumanEval({len(benchmarks['humaneval'])}), MBPP({len(benchmarks['mbpp'])}), CodeContests({len(benchmarks['codecontests'])})\n")

    # 2. Extract task features
    print("[2/7] Extracting task features...")
    features_list = []
    for bench_name, ds in benchmarks.items():
        for i, problem in enumerate(ds):
            if bench_name == 'humaneval':
                ref_sol = problem['canonical_solution']
                pid = problem['task_id']
            elif bench_name == 'mbpp':
                ref_sol = problem['code']
                pid = f"MBPP/{problem['task_id']}"
            else:
                ref_sol = problem.get('solutions', {}).get('solution', [''])[0] if 'solutions' in problem else ''
                pid = f"CodeContests/{i}"

            feats = extract_task_features(ref_sol)
            feats['problem_id'] = pid
            feats['benchmark'] = bench_name
            features_list.append(feats)
    features_df = pd.DataFrame(features_list)
    print(f"  Extracted features for {len(features_df)} problems\n")

    # 3. Generate code + classify errors
    print("[3/7] Loading model and generating code...")
    model = AutoModelForCausalLM.from_pretrained(
        CONFIG["model"]["model_name"],
        use_safetensors=True
    )
    tokenizer = AutoTokenizer.from_pretrained(CONFIG["model"]["model_name"])
    tokenizer.pad_token = tokenizer.eos_token

    errors_list = []
    n_samples = CONFIG["execution"]["samples_per_problem"]
    gen_cfg = CONFIG["model"]["generation"]

    for bench_name, ds in benchmarks.items():
        print(f"  Processing {bench_name}...")
        for i, problem in enumerate(ds):
            if bench_name == 'humaneval':
                prompt = problem['prompt']
                pid = problem['task_id']
            elif bench_name == 'mbpp':
                prompt = problem['text']
                pid = f"MBPP/{problem['task_id']}"
            else:
                prompt = problem.get('description', '')
                pid = f"CodeContests/{i}"

            inputs = tokenizer(prompt, return_tensors='pt', truncation=True, max_length=512)
            samples = []

            with torch.no_grad():
                for _ in range(n_samples):
                    output = model.generate(
                        **inputs,
                        max_new_tokens=gen_cfg["max_new_tokens"],
                        temperature=gen_cfg["temperature"],
                        top_p=gen_cfg["top_p"],
                        do_sample=gen_cfg["do_sample"]
                    )
                    code = tokenizer.decode(output[0], skip_special_tokens=True)
                    samples.append(code)

            dist = compute_error_distribution(samples)
            dist['problem_id'] = pid
            dist['benchmark'] = bench_name
            errors_list.append(dist)
    errors_df = pd.DataFrame(errors_list)
    print(f"  Generated and classified {n_samples} samples per problem\n")

    # 4. Correlation analysis
    print("[4/7] Computing correlation matrix...")
    corr_matrix, p_values = analyze_correlation(features_df, errors_df)
    print("  Correlation analysis complete\n")

    # 5. Regression analysis
    print("[5/7] Fitting regression model...")
    merged = pd.merge(features_df, errors_df, on='problem_id')
    X = merged[['ast_depth', 'function_count', 'control_flow_density', 'complexity_score']]
    y = merged['syntax_pct']
    r_squared, coefficients, cv_scores = fit_regression(X, y)
    print(f"  R² = {r_squared:.4f}\n")

    # 6. Visualizations
    print("[6/7] Generating visualizations...")
    output_dir = Path("experiments/h-m1/figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_gate_metrics(r_squared, CONFIG["regression"]["r2_threshold"], str(output_dir / "gate_metrics.png"))
    plot_correlation_heatmap(corr_matrix, str(output_dir / "correlation_heatmap.png"))
    plot_feature_importance(coefficients, str(output_dir / "feature_importance.png"))
    plot_cv_results(cv_scores, str(output_dir / "cv_boxplot.png"))
    print(f"  Saved 4 figures to {output_dir}\n")

    # 7. Gate decision
    print("[7/7] Gate evaluation...")
    verdict = gate_decision(r_squared, CONFIG["regression"]["r2_threshold"])
    print(f"  Gate: {verdict} (R² = {r_squared:.4f}, threshold = {CONFIG['regression']['r2_threshold']})\n")

    # Save results
    results = {
        'r_squared': r_squared,
        'coefficients': coefficients,
        'cv_scores': cv_scores,
        'p_values': {k: {'r': v[0], 'p': v[1]} for k, v in p_values.items()},
        'gate_pass': verdict == 'PASS'
    }

    with open("experiments/h-m1/data/regression_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    features_df.to_csv("experiments/h-m1/data/task_features.csv", index=False)
    errors_df.to_csv("experiments/h-m1/data/error_distributions.csv", index=False)
    corr_matrix.to_csv("experiments/h-m1/data/correlation_matrix.csv")

    print(f"=== Experiment Complete ===")
    print(f"Gate: {verdict}")
    print(f"R²: {r_squared:.4f}")
    return results


if __name__ == '__main__':
    run_experiment()
