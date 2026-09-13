import json
import sys
from config import AnalysisConfig, load_config
from analyze import run


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="H-M1: MMLU Scale Covariate Pre-Test")
    parser.add_argument("--config", default=None, help="Path to YAML config file")
    args = parser.parse_args()

    cfg = load_config(args.config) if args.config else AnalysisConfig()
    results = run(cfg)

    gate_str = "PASS" if results["gate_pass"] else "FAIL"
    print(f"\n{'='*60}")
    print(f"H-M1 Gate Result: {gate_str}")
    print(f"  N = {results['N']}")
    print(f"  R²(MMLU × TruthfulQA MC2) = {results['R2_mmlu_truthqa']:.4f}  (threshold > 0.05)")
    print(f"  R²(MMLU × BBQ accuracy)   = {results['R2_mmlu_bbq']:.4f}  (threshold > 0.05)")
    print(f"  Baseline rho(TruthfulQA, BBQ) = {results['raw_rho_truth_bbq']:.4f}  [H-M2 input]")
    print(f"{'='*60}")
    print(f"EXPERIMENT COMPLETE (exit=0, gate={gate_str})")

    # Exit 0 always — gate FAIL is a valid publishable null, not an error
    sys.exit(0)


if __name__ == "__main__":
    main()
