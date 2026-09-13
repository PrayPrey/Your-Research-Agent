import sys
from pathlib import Path

# Add h-m4/code to path for imports
sys.path.insert(0, str(Path(__file__).parent))


def main() -> None:
    from config import H_M4Config
    from evaluate import verify_checkpoints, run_fallback_training, run_all_evaluations
    from metrics import compute_metrics, finalize_p3, save_gate_results, print_gate_summary
    from visualize import generate_all_figures

    cfg = H_M4Config()

    # Step 1: Verify H-M2 checkpoints; fallback train if missing
    missing = verify_checkpoints(cfg)
    needs_training = {c: s for c, s in missing.items() if s}
    if needs_training:
        print(f"[H-M4] Missing checkpoints detected: {needs_training}")
        run_fallback_training(cfg, needs_training)
    else:
        print("[H-M4] All H-M2 checkpoints present. Skipping training.")

    # Step 2: Run all EvalPlus evaluations
    pass_at_1 = run_all_evaluations(cfg)

    # Step 3: Compute metrics and gate
    results = compute_metrics(pass_at_1, cfg)
    results = finalize_p3(results, cfg)

    # Step 4: Save results and print summary
    save_gate_results(results, cfg)
    print_gate_summary(results)

    # Step 5: Generate figures
    fig_paths = generate_all_figures(results, cfg)
    print(f"[H-M4] Figures saved: {fig_paths}")

    # Final verdict
    gate = results["gate_passed"]
    print(f"\n{'='*60}")
    print(f"H-M4 GATE: {'PASS' if gate else 'FAIL'}")
    print(f"P1: improvement_variance50 >= 2pp AND gap_vs_random50 >= 1pp")
    print(f"{'='*60}")
    print("EXPERIMENT COMPLETE")


if __name__ == "__main__":
    main()
