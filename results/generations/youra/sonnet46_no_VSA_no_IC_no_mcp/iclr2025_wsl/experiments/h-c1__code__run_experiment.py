"""H-C1: Full experiment pipeline — sign-flip canonicalization uniqueness audit."""
import json
import sys
from pathlib import Path

CODE_DIR = Path(__file__).parent
sys.path.insert(0, str(CODE_DIR))

RESULTS_DIR = CODE_DIR.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

GATE_THRESHOLD_UNIQUE = 0.99
GATE_THRESHOLD_SCOPE = 0.95


def main():
    print("=" * 60)
    print("H-C1: Sign-Flip Canonicalization Uniqueness Audit")
    print("=" * 60)

    # Step 1: Load data
    print("\n[1/6] Loading zoo sample (N=500, seed=1)...")
    from data_loader import load_zoo_sample
    models = load_zoo_sample(n=500, seed=1)
    print(f"  Loaded {len(models)} models")

    # Step 2: Self-check idempotency on first model
    print("\n[2/6] Self-check idempotency on first model...")
    from audit import self_check_idempotency
    self_check_idempotency(*models[0])
    print("  OK — idempotency asserted on model[0]")

    # Step 3: Run full audit
    print(f"\n[3/6] Running audit on {len(models)} models...")
    from audit import run_audit
    results, summary = run_audit(models)
    print(f"  fraction_unique     = {summary['fraction_unique']:.4f}")
    print(f"  fraction_idempotent = {summary['fraction_idempotent']:.4f}")
    print(f"  degenerate_count    = {summary['degenerate_count']}")

    # Step 4: Degeneracy characterization (conditional)
    degen_stats = {}
    w_stats = {}
    if summary["degenerate_count"] > 0:
        print(f"\n[4/6] Characterizing {summary['degenerate_count']} degenerate models...")
        from audit import compute_degeneracy_stats, weight_stats_tied_neurons
        degen_stats = compute_degeneracy_stats(results)
        w_stats = weight_stats_tied_neurons(models, degen_stats["degenerate_indices"])
        print(f"  mean_tied_neurons   = {degen_stats['mean_tied_neurons_per_degenerate_model']:.2f}")
        print(f"  max_tied_neurons    = {degen_stats['max_tied_neurons']}")
    else:
        print("\n[4/6] No degenerate cases found — skipping characterization")

    # Step 5: Visualize
    print("\n[5/6] Generating figures...")
    from visualize import plot_gate_metric, plot_tied_neuron_hist
    plot_gate_metric(summary["fraction_unique"], threshold=GATE_THRESHOLD_UNIQUE)
    if summary["degenerate_count"] > 0:
        plot_tied_neuron_hist(results)

    # Step 6: Gate verdict
    frac_unique = summary["fraction_unique"]
    frac_idem = summary["fraction_idempotent"]
    if frac_unique >= GATE_THRESHOLD_UNIQUE and frac_idem == 1.0:
        gate_result = "PASS"
    elif frac_unique >= GATE_THRESHOLD_SCOPE:
        gate_result = "DOCUMENT"  # [0.95, 0.99) — borderline, document limitation
    else:
        gate_result = "SCOPE_BOUNDARY"

    print("\n" + "=" * 60)
    print("GATE VERDICT")
    print("=" * 60)
    print(f"  P1 fraction_unique    = {frac_unique:.4f}  (threshold=0.99)  {'PASS' if frac_unique >= GATE_THRESHOLD_UNIQUE else 'FAIL'}")
    print(f"  P2 fraction_idempotent= {frac_idem:.4f}  (threshold=1.00)  {'PASS' if frac_idem == 1.0 else 'FAIL'}")
    print(f"  GATE RESULT: {gate_result}")
    print("=" * 60)

    # Save results
    output = {
        "summary": summary,
        "gate_result": gate_result,
        "gate_thresholds": {
            "unique": GATE_THRESHOLD_UNIQUE,
            "scope": GATE_THRESHOLD_SCOPE,
        },
        "degeneracy_stats": degen_stats,
        "weight_stats": w_stats,
        "per_model": results,
    }
    out_path = RESULTS_DIR / "audit_results.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved: {out_path}")

    return gate_result, summary


if __name__ == "__main__":
    main()
