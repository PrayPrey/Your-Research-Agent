import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Allow imports from project root when run from any directory
_code_dir = Path(__file__).parent
sys.path.insert(0, str(_code_dir))

from config import CFG, FIG_CFG
from cox_analysis import load_panel, fit_models, run_lrt, run_diagnostics
from visualization import save_all_figures


def main() -> None:
    """Orchestrate: load → fit → lrt → diagnostics → figures → serialize → print."""
    # Resolve paths relative to project root (4 levels up from code/)
    project_root = _code_dir.parent.parent.parent.parent

    print("=" * 60)
    print("H-M1: Cox PH Diversity Significance Test")
    print("=" * 60)

    # 1. Load panel
    panel_path = project_root / CFG.panel_path
    _cfg = CFG.__class__(**{**CFG.__dict__, "panel_path": str(panel_path)})
    try:
        panel_df = load_panel(_cfg)
    except FileNotFoundError as e:
        print(f"ERROR: Panel CSV not found — run H-E1 first.\n{e}")
        raise SystemExit(1)

    # 2. Fit M0 / M1
    M0, M1 = fit_models(panel_df, _cfg)

    # 3. LRT
    result = run_lrt(M0, M1, _cfg)
    # Note: under L2 penalizer M1.ll can be marginally < M0.ll; run_lrt clips lrt_stat to 0
    print(f"M1 fitted: HR={result.HR:.4f}, p={result.p_value:.4f}, |HR-1|={result.abs_effect:.4f}")

    # 4. Diagnostics
    diag = run_diagnostics(M1, panel_df)
    print(f"Concordance: {diag['concordance']:.4f}")
    if diag["ph_violations"]:
        print(f"PH assumption violations: {diag['ph_violations']}")
    else:
        print("PH assumption: no violations detected")

    # 5. Figures — update figures_dir to absolute path
    figures_dir = project_root / CFG.figures_dir
    figures_dir.mkdir(parents=True, exist_ok=True)
    _cfg_fig = CFG.__class__(**{**_cfg.__dict__, "figures_dir": str(figures_dir)})
    saved_figs = save_all_figures(M1, panel_df, result, _cfg_fig, FIG_CFG)
    print(f"Figures saved: {len(saved_figs)}")

    # 6. Serialize results
    results_path = project_root / CFG.results_path
    results_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "hypothesis_id": "H-M1",
        "gate_passed": bool(result.gate_passed),
        "lrt_stat": float(result.lrt_stat),
        "p_value": result.p_value,
        "HR": result.HR,
        "CI_lower": result.CI_lower,
        "CI_upper": result.CI_upper,
        "abs_effect": result.abs_effect,
        "concordance_M1": result.concordance,
        "M0_log_likelihood": result.M0_log_likelihood,
        "M1_log_likelihood": result.M1_log_likelihood,
        "direction": result.direction,
        "diagnostics": diag,
        "figures": saved_figs,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with open(str(results_path), "w") as f:
        json.dump(payload, f, indent=2)
    print(f"Results saved: {results_path}")

    # 7. Print gate summary
    gate_str = "PASS" if result.gate_passed else "FAIL (meaningful null)"
    print("\n" + "=" * 60)
    print(f"H-M1 GATE: {gate_str}")
    print(f"  direction={result.direction}, p={result.p_value:.4f}, HR={result.HR:.4f}, |HR-1|={result.abs_effect:.4f}")
    print(f"  LRT stat={result.lrt_stat:.4f}")
    print(f"  95% CI: [{result.CI_lower:.4f}, {result.CI_upper:.4f}]")
    print(f"  Concordance (M1): {result.concordance:.4f}")
    print("=" * 60)
    print("EXPERIMENT COMPLETE")


if __name__ == "__main__":
    main()
