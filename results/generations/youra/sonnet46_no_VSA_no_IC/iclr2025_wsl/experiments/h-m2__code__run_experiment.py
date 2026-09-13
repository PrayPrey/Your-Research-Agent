"""
H-M2: Sample Efficiency Learning Curve Experiment.
Entrypoint: loads H-E1 results or trains fallback, computes efficiency ratios, generates figures.
"""
import os
import sys
import json

# Ensure this code dir is on path
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

import config as cfg
from results_loader import get_results, check_and_merge, load_h_e1_results
from analysis import (compute_all_efficiency_ratios, check_gate,
                      verify_mechanism_activated_batch)
from visualize import plot_learning_curves, plot_efficiency_bar, plot_seed_traces


def check_dwsnets_compatibility(zoo_name="cifar10"):
    """Return True if CNN zoo has >2 FC layers (DWSNets requirement)."""
    try:
        zoo_path = cfg.ZOO_PATHS.get(zoo_name)
        if not zoo_path or not os.path.exists(zoo_path):
            return False
        import torch
        data = torch.load(zoo_path, map_location="cpu", weights_only=False)
        # Inspect first model in trainset
        trainset = data.get("trainset") or data.get("train") or []
        if not trainset:
            return False
        state_dict, _ = trainset[0]
        fc_weights = [k for k, v in state_dict.items()
                      if "weight" in k and hasattr(v, "dim") and v.dim() == 2]
        n_fc = len(fc_weights)
        print(f"  DWSNets compat check ({zoo_name}): {n_fc} FC layers found")
        return n_fc > 2
    except Exception as e:
        print(f"  DWSNets compat check failed: {e}")
        return False


def save_results_json(results, efficiency_ratios, gate_passed, out_path):
    """Save full results + efficiency ratios to JSON."""
    out = {
        "results": results,
        "efficiency_ratios": {
            enc: {zoo: (ratio if ratio != float('inf') else "inf")
                  for zoo, ratio in zoo_ratios.items()}
            for enc, zoo_ratios in efficiency_ratios.items()
        },
        "gate_passed": gate_passed,
        "config": {
            "peak_fraction": cfg.PEAK_FRACTION,
            "efficiency_gate": cfg.EFFICIENCY_GATE,
            "encoder_names": cfg.ENCODER_NAMES,
            "zoo_names": cfg.ZOO_NAMES,
            "training_sizes": [str(s) for s in cfg.TRAINING_SIZES],
            "seeds": cfg.SEEDS,
        }
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"  Saved results JSON: {out_path}")


def print_summary_table(efficiency_ratios, gate_passed):
    """Print encoder | zoo | N_90 | efficiency_ratio | gate table."""
    print("\n" + "=" * 75)
    print(f"{'Encoder':<22} {'Zoo':<10} {'Efficiency Ratio':<18} {'Gate (≥2.0)'}")
    print("-" * 75)
    equivariant = [e for e in efficiency_ratios if e in ("gnn_nfn", "dwsnets")]
    for enc in equivariant:
        for zoo, ratio in efficiency_ratios[enc].items():
            ratio_str = f"{ratio:.3f}×" if ratio != float('inf') else "∞"
            gate_str = "PASS ✓" if ratio >= cfg.EFFICIENCY_GATE else "FAIL ✗"
            print(f"{enc:<22} {zoo:<10} {ratio_str:<18} {gate_str}")
    print("=" * 75)
    print(f"\nGate result: {'PASS ✓' if gate_passed else 'FAIL ✗'} "
          f"(SHOULD_WORK — failure is a limitation note, not pipeline stop)")


def main():
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    # 1. DWSNets compatibility
    dwsnets_ok = check_dwsnets_compatibility("cifar10")
    encoder_names = list(cfg.ENCODER_NAMES)
    if dwsnets_ok:
        encoder_names.append("dwsnets")
        print("✓ DWSNets compatible — added to encoder list")
    else:
        print("⚠ DWSNets incompatible with CNN-s zoo (≤2 FC layers) — excluded")

    # 2. Load or compute results
    print("\n[Step 2] Loading results...")
    results = get_results(device=device)

    # 3. Analysis
    print("\n[Step 3] Computing efficiency ratios...")
    efficiency_ratios = compute_all_efficiency_ratios(results)
    for enc, zoo_ratios in efficiency_ratios.items():
        for zoo, ratio in zoo_ratios.items():
            ratio_str = f"{ratio:.3f}" if ratio != float('inf') else "inf"
            print(f"  {enc}/{zoo}: efficiency_ratio = {ratio_str}")

    # 4. Mechanism verification
    print("\n[Step 4] Mechanism verification (equivariance sanity check)...")
    mechanism_checks = {}
    for enc in [e for e in encoder_names if e in ("gnn_nfn", "dwsnets")]:
        check = verify_mechanism_activated_batch(enc, results, device)
        mechanism_checks[enc] = check
        print(f"  {enc}: equivariance_holds={check['equivariance_holds']}, "
              f"max_diff={check.get('max_diff', 'N/A')}")

    # 5. Gate check
    print("\n[Step 5] Gate check...")
    gate_passed, gate_details = check_gate(efficiency_ratios)
    print(f"  Gate passed: {gate_passed}")
    for enc, detail in gate_details.items():
        print(f"  {enc}: meets_gate={detail['meets_gate']}, ratios={detail['ratios']}")

    # 6. Visualize
    print("\n[Step 6] Generating figures...")
    os.makedirs(cfg.FIGURES_DIR, exist_ok=True)
    for zoo in cfg.ZOO_NAMES:
        plot_learning_curves(
            results, zoo,
            os.path.join(cfg.FIGURES_DIR, f"learning_curves_{zoo}.png"))
        plot_seed_traces(
            results, zoo,
            os.path.join(cfg.FIGURES_DIR, f"seed_traces_{zoo}.png"))
    plot_efficiency_bar(
        efficiency_ratios,
        os.path.join(cfg.FIGURES_DIR, "efficiency_ratio_bar.png"))

    # 7. Save results JSON + print summary
    print("\n[Step 7] Saving results...")
    json_path = os.path.join(cfg.RESULTS_DIR, "learning_curve_results.json")
    save_results_json(results, efficiency_ratios, gate_passed, json_path)
    print_summary_table(efficiency_ratios, gate_passed)

    # Write gate result to a simple text file for easy parsing
    gate_result_path = os.path.join(cfg.RESULTS_DIR, "gate_result.txt")
    with open(gate_result_path, "w") as f:
        f.write(f"gate_passed={gate_passed}\n")
        for enc, zoo_ratios in efficiency_ratios.items():
            for zoo, ratio in zoo_ratios.items():
                f.write(f"{enc}/{zoo}={ratio}\n")
        for enc, check in mechanism_checks.items():
            f.write(f"equivariance/{enc}={check['equivariance_holds']}\n")
    print(f"\n✓ Gate result written to {gate_result_path}")
    print("\nEXPERIMENT COMPLETE")
    return gate_passed


if __name__ == "__main__":
    main()
