import importlib.util
from pathlib import Path
import numpy as np
import torch

_code_dir = Path(__file__).parent

def _load_local(name):
    spec = importlib.util.spec_from_file_location(name, _code_dir / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

config_mod = _load_local("config")
removal_mod = _load_local("removal")
evaluate_mod = _load_local("evaluate")
visualize_mod = _load_local("visualize")
h_m1_imports_mod = _load_local("h_m1_imports")
train_mod = _load_local("h_m2_train")

Config = config_mod.Config
per_example_ccr = removal_mod.per_example_ccr
RemovalIntervention = removal_mod.RemovalIntervention
eval_mmlu_accuracy = evaluate_mod.eval_mmlu_accuracy
compute_degradation_ratio = evaluate_mod.compute_degradation_ratio
bootstrap_degradation_ci = evaluate_mod.bootstrap_degradation_ci
plot_gate_metrics = visualize_mod.plot_gate_metrics
plot_accuracy_by_fraction = visualize_mod.plot_accuracy_by_fraction
plot_bootstrap_distribution = visualize_mod.plot_bootstrap_distribution
load_corpus = h_m1_imports_mod.load_corpus
load_mmlu = h_m1_imports_mod.load_mmlu
filter_by_strategy = h_m1_imports_mod.filter_by_strategy
train_condition = train_mod.train_condition


def run_all(cfg: Config) -> dict:
    """Main experiment: 3 conditions x 3 fractions x seeds."""
    print("=" * 60)
    print("H-M2: High-CCR Removal Intervention Experiment")
    print("=" * 60)

    samples = load_corpus(cfg)
    base_corpus = filter_by_strategy(samples, "perplexity", cfg.percentile, cfg.corpus_size, 42)
    mmlu = load_mmlu(cfg)

    print(f"Computing per-example CCR for {len(base_corpus)} documents...")
    ccr_scores = per_example_ccr(base_corpus, mmlu, cfg.ngram_n)
    print(f"CCR stats: min={ccr_scores.min():.4f}, max={ccr_scores.max():.4f}, mean={ccr_scores.mean():.4f}")

    results = {}
    all_baseline_accs = []
    all_high_ccr_accs = []
    all_random_accs = []

    for fraction in cfg.removal_fractions:
        print(f"\n{'='*40}")
        print(f"Removal fraction: {fraction}")
        print(f"{'='*40}")

        intervention = RemovalIntervention(ccr_scores, fraction)
        high_ccr_mask = intervention.get_high_ccr_mask()

        fraction_results = {"baseline": [], "high_ccr": [], "random": []}

        for seed in cfg.seeds:
            random_mask = intervention.get_random_mask(seed)

            corpus_baseline = base_corpus
            corpus_high_ccr = intervention.apply(base_corpus, high_ccr_mask)
            corpus_random = intervention.apply(base_corpus, random_mask)

            print(f"\nSeed {seed}:")
            print(f"  Baseline: {len(corpus_baseline)} examples")
            print(f"  High-CCR removed: {len(corpus_high_ccr)} examples")
            print(f"  Random removed: {len(corpus_random)} examples")

            for condition, corpus in [
                ("baseline", corpus_baseline),
                ("high_ccr", corpus_high_ccr),
                ("random", corpus_random)
            ]:
                model, tokenizer = train_condition(cfg, corpus, condition, seed)
                acc = eval_mmlu_accuracy(model, tokenizer, mmlu)
                fraction_results[condition].append(acc)
                print(f"  {condition}: MMLU acc = {acc:.4f}")

                del model
                torch.cuda.empty_cache() if torch.cuda.is_available() else None

        results[fraction] = {
            "baseline": np.mean(fraction_results["baseline"]),
            "high_ccr": np.mean(fraction_results["high_ccr"]),
            "random": np.mean(fraction_results["random"]),
        }

        all_baseline_accs.extend(fraction_results["baseline"])
        all_high_ccr_accs.extend(fraction_results["high_ccr"])
        all_random_accs.extend(fraction_results["random"])

    baseline_accs = np.array(all_baseline_accs)
    high_ccr_accs = np.array(all_high_ccr_accs)
    random_accs = np.array(all_random_accs)

    mean_ratio, ci_low, ci_high = bootstrap_degradation_ci(
        baseline_accs, high_ccr_accs, random_accs, cfg.n_bootstrap
    )

    gate_passed = ci_low >= 1.5

    print("\n" + "=" * 60)
    print("GATE CHECK")
    print("=" * 60)
    print(f"Mean degradation ratio: {mean_ratio:.3f}")
    print(f"95% CI: [{ci_low:.3f}, {ci_high:.3f}]")
    print(f"CI excludes 1.0 (null): {ci_low > 1.0}")
    print(f"Ratio >= 1.5: {mean_ratio >= 1.5}")
    print(f"CI lower bound >= 1.5: {ci_low >= 1.5}")
    print(f"\nGATE RESULT: {'PASS' if gate_passed else 'FAIL'}")

    Path(cfg.out_dir).mkdir(parents=True, exist_ok=True)

    plot_accuracy_by_fraction(results, cfg.out_dir)
    plot_gate_metrics(
        {"degradation_ratio": 1.5},
        {"degradation_ratio": mean_ratio},
        cfg.out_dir
    )

    rng = np.random.default_rng(42)
    n = len(baseline_accs)
    bootstrap_ratios = []
    for _ in range(cfg.n_bootstrap):
        idx = rng.choice(n, n, replace=True)
        ratio = compute_degradation_ratio(
            baseline_accs[idx].mean(),
            high_ccr_accs[idx].mean(),
            random_accs[idx].mean()
        )
        bootstrap_ratios.append(ratio)
    plot_bootstrap_distribution(np.array(bootstrap_ratios), (ci_low, ci_high), cfg.out_dir)

    return {
        "results": results,
        "mean_ratio": mean_ratio,
        "ci": (ci_low, ci_high),
        "gate_passed": gate_passed
    }


if __name__ == "__main__":
    cfg = Config()
    output = run_all(cfg)
    print("\nExperiment complete.")
    print(f"Gate passed: {output['gate_passed']}")
