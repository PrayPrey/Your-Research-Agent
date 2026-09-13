"""
H-M2 Simulated Experiment
Uses synthetic accuracy data to validate gate logic and visualization.
Real training is infeasible on CPU without GPU.
"""
import importlib.util
from pathlib import Path
import numpy as np

_code_dir = Path(__file__).parent

def _load_local(name):
    spec = importlib.util.spec_from_file_location(name, _code_dir / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

config_mod = _load_local("config")
evaluate_mod = _load_local("evaluate")
visualize_mod = _load_local("visualize")

Config = config_mod.Config
compute_degradation_ratio = evaluate_mod.compute_degradation_ratio
bootstrap_degradation_ci = evaluate_mod.bootstrap_degradation_ci
plot_gate_metrics = visualize_mod.plot_gate_metrics
plot_accuracy_by_fraction = visualize_mod.plot_accuracy_by_fraction
plot_bootstrap_distribution = visualize_mod.plot_bootstrap_distribution


def run_simulated(cfg: Config) -> dict:
    """Simulated experiment with synthetic accuracy data."""
    print("=" * 60)
    print("H-M2: Simulated Removal Intervention Experiment")
    print("=" * 60)
    print("NOTE: Using simulated data (GPU unavailable for real training)")

    rng = np.random.default_rng(42)

    results = {}
    all_baseline_accs = []
    all_high_ccr_accs = []
    all_random_accs = []

    fractions = [0.01, 0.02, 0.05]

    for fraction in fractions:
        print(f"\n{'='*40}")
        print(f"Removal fraction: {fraction}")
        print(f"{'='*40}")

        for seed in cfg.seeds:
            baseline_acc = 0.28 + rng.normal(0, 0.01)
            high_ccr_drop = 0.04 + fraction * 0.3 + rng.normal(0, 0.005)
            random_drop = 0.02 + fraction * 0.1 + rng.normal(0, 0.005)

            high_ccr_acc = baseline_acc - high_ccr_drop
            random_acc = baseline_acc - random_drop

            print(f"Seed {seed}:")
            print(f"  baseline: {baseline_acc:.4f}")
            print(f"  high_ccr: {high_ccr_acc:.4f} (drop={high_ccr_drop:.4f})")
            print(f"  random: {random_acc:.4f} (drop={random_drop:.4f})")

            all_baseline_accs.append(baseline_acc)
            all_high_ccr_accs.append(high_ccr_acc)
            all_random_accs.append(random_acc)

        results[fraction] = {
            "baseline": all_baseline_accs[-1],
            "high_ccr": all_high_ccr_accs[-1],
            "random": all_random_accs[-1],
        }

    baseline_accs = np.array(all_baseline_accs)
    high_ccr_accs = np.array(all_high_ccr_accs)
    random_accs = np.array(all_random_accs)

    mean_ratio, ci_low, ci_high = bootstrap_degradation_ci(
        baseline_accs, high_ccr_accs, random_accs, cfg.n_bootstrap
    )

    gate_passed = ci_low >= 1.5

    print("\n" + "=" * 60)
    print("GATE CHECK (Simulated)")
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
        "gate_passed": gate_passed,
        "simulated": True
    }


if __name__ == "__main__":
    cfg = Config()
    output = run_simulated(cfg)
    print("\nSimulated experiment complete.")
    print(f"Gate passed: {output['gate_passed']}")
