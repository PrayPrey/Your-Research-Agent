import sys
from config import ExperimentConfig, load_config
from analyze import run


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="H-M2: Partial Spearman + Fisher Z Difference Test")
    parser.add_argument("--config", default=None, help="Path to YAML config file")
    args = parser.parse_args()

    cfg = load_config(args.config) if args.config else ExperimentConfig()
    results = run(cfg)

    gate_str = "PASS" if results["gate_pass"] else "FAIL"
    p_val = results.get("p_value", float("nan"))
    print(f"\n{'='*60}")
    print(f"H-M2 Gate Result: {gate_str}")
    print(f"  N                = {results['N']}")
    print(f"  raw_rho          = {results.get('raw_rho', float('nan')):.4f}")
    print(f"  partial_rho      = {results.get('partial_rho', float('nan')):.4f}")
    print(f"  Fisher z p-value = {p_val:.4f}")
    print(f"  outcome          = {results.get('outcome', 'N/A')}")
    print(f"  CI overlap       = {results.get('ci_overlap_status', 'N/A')}")
    print(f"{'='*60}")
    print(f"EXPERIMENT COMPLETE (exit=0, gate={gate_str})")

    sys.exit(0 if results["gate_pass"] else 1)


if __name__ == "__main__":
    main()
