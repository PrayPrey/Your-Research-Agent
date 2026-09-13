import json
from pathlib import Path
import config


def print_summary_table(results: dict, activated: bool, indicators: dict) -> None:
    print("\n=== H-M1 RESULTS ===")
    print(f"{'Encoder':<12} {'max_diff':>12} {'mean_diff':>12} {'median':>12} {'p95':>12} {'PASS?':>8}")
    print("-" * 68)
    for name, stats in results.items():
        if stats is None:
            print(f"{name:<12} {'SKIPPED':>12}")
            continue
        tol = config.TOL_EQUIV if name != "flat_mlp" else None
        passed = stats["pass"]
        flag = "PASS" if passed else ("FAIL" if passed is False else "N/A")
        print(f"{name:<12} {stats['max_diff']:>12.2e} {stats['mean_diff']:>12.2e} "
              f"{stats['median_diff']:>12.2e} {stats['p95_diff']:>12.2e} {flag:>8}")
    print(f"\nGate activated: {activated}")
    print(f"Indicators: {indicators}")


def save_json(results: dict, activated: bool, indicators: dict, path: Path = None) -> Path:
    Path(config.RESULTS_DIR).mkdir(parents=True, exist_ok=True)
    out = {
        "activated": activated,
        "indicators": indicators,
        "encoders": {
            k: {kk: vv for kk, vv in v.items() if kk != "all_diffs"}
            for k, v in results.items() if v is not None
        },
    }
    save_path = path or Path(config.RESULTS_DIR) / "equivariance_results.json"
    with open(save_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Results saved to {save_path}")
    return save_path
