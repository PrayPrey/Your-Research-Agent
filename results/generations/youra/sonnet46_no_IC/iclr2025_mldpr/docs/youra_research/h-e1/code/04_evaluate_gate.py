"""
04_evaluate_gate.py — H-E1 Gate Evaluation

Load model_results.json, apply MUST_WORK gate logic, write primary_results.json,
print clear PASS/PARTIAL_PASS/FAIL verdict.
"""

import json
import os
import sys

# === PATHS ===
BASE_DIR        = "docs/youra_research/h-e1"
MODEL_RESULTS   = f"{BASE_DIR}/results/model_results.json"
PRIMARY_RESULTS = f"{BASE_DIR}/results/primary_results.json"

# === GATE THRESHOLDS ===
GATE_IRR_MIN      = 1.1
GATE_CI_LOWER_MIN = 1.1
GATE_PVAL_MAX     = 0.05
PARTIAL_CI_MIN    = 1.05


def evaluate_gate(irr: float, ci_lower: float, ci_upper: float, pval: float) -> str:
    """
    Returns "PASS", "PARTIAL_PASS", or "FAIL".
    PASS: irr >= 1.1 AND ci_lower >= 1.1 AND pval < 0.05
    PARTIAL_PASS: 1.05 <= ci_lower < 1.1 AND pval < 0.05
    FAIL: otherwise
    """
    if irr >= GATE_IRR_MIN and ci_lower >= GATE_CI_LOWER_MIN and pval < GATE_PVAL_MAX:
        return "PASS"
    elif PARTIAL_CI_MIN <= ci_lower < GATE_CI_LOWER_MIN and pval < GATE_PVAL_MAX:
        return "PARTIAL_PASS"
    else:
        return "FAIL"


def main():
    print("=" * 60)
    print("H-E1 Step 04: Gate Evaluation")
    print("=" * 60)

    print(f"\n[1] Loading {MODEL_RESULTS}...")
    with open(MODEL_RESULTS) as f:
        results = json.load(f)
    print("  ✓ Loaded")

    print("\n[2] Extracting has_tags stats from proposed model...")
    proposed = results['proposed']
    hs = proposed['has_tags']
    irr      = float(hs['irr'])
    ci_lower = float(hs['ci_lower'])
    ci_upper = float(hs['ci_upper'])
    pval     = float(hs['pval'])

    print(f"  IRR      = {irr:.4f}")
    print(f"  CI lower = {ci_lower:.4f}")
    print(f"  CI upper = {ci_upper:.4f}")
    print(f"  p-value  = {pval:.4e}")

    print("\n[3] Evaluating gate (MUST_WORK)...")
    gate_result = evaluate_gate(irr, ci_lower, ci_upper, pval)

    # Determine which conditions passed/failed
    cond_irr      = irr >= GATE_IRR_MIN
    cond_ci_lower = ci_lower >= GATE_CI_LOWER_MIN
    cond_pval     = pval < GATE_PVAL_MAX

    print(f"\n  Gate conditions:")
    print(f"    IRR >= {GATE_IRR_MIN}:      {'✓' if cond_irr else '✗'}  ({irr:.4f})")
    print(f"    CI_lower >= {GATE_CI_LOWER_MIN}: {'✓' if cond_ci_lower else '✗'}  ({ci_lower:.4f})")
    print(f"    p < {GATE_PVAL_MAX}:         {'✓' if cond_pval else '✗'}  ({pval:.4e})")

    print(f"\n  *** GATE RESULT: {gate_result} ***")

    if gate_result == "PASS":
        print("  → MUST_WORK gate PASSED. Proceed to Phase 5.")
    elif gate_result == "PARTIAL_PASS":
        print("  → PARTIAL_PASS: CI_lower in [1.05, 1.10). Scientifically informative.")
        print("    Continue with qualified claim.")
    else:
        print("  → FAIL: MUST_WORK gate NOT satisfied.")
        print("    Pipeline routes to Phase 0 for hypothesis redesign.")

    # RC-7 attenuation info
    rc7 = results.get('rc7_age_vs_decade', {})
    if rc7.get('attenuation_ratio') is not None:
        print(f"\n  RC-7 (Decade FE attenuation): ratio = {rc7['attenuation_ratio']:.4f}")
        if rc7['attenuation_ratio'] > 1.1:
            print("  ⚠ WARNING: Decade FE substantially absorbs has_tags effect (RC-3 risk confirmed)")

    print(f"\n[4] Writing {PRIMARY_RESULTS}...")
    os.makedirs(os.path.dirname(PRIMARY_RESULTS), exist_ok=True)

    primary = {
        'hypothesis_id': 'h-e1',
        'gate_type': 'MUST_WORK',
        'gate_result': gate_result,
        'irr': irr,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper,
        'pval': pval,
        'gate_conditions': {
            'irr_pass': cond_irr,
            'ci_lower_pass': cond_ci_lower,
            'pval_pass': cond_pval,
        },
        'thresholds': {
            'gate_irr_min': GATE_IRR_MIN,
            'gate_ci_lower_min': GATE_CI_LOWER_MIN,
            'gate_pval_max': GATE_PVAL_MAX,
            'partial_ci_min': PARTIAL_CI_MIN,
        },
        'rc_summary': {
            'rc4_irr': results.get('rc4_winsorized', {}).get('irr'),
            'rc4_ci_lower': results.get('rc4_winsorized', {}).get('ci_lower'),
            'rc5_irr': results.get('rc5_tagged_only', {}).get('irr'),
            'rc7_attenuation_ratio': rc7.get('attenuation_ratio'),
        },
        'model_fit': {
            'n_obs': proposed.get('n_obs'),
            'aic': proposed.get('aic'),
            'bic': proposed.get('bic'),
            'llf': proposed.get('llf'),
            'converged': proposed.get('converged'),
        }
    }

    with open(PRIMARY_RESULTS, 'w') as f:
        json.dump(primary, f, indent=2)
    print(f"  ✓ Saved to {PRIMARY_RESULTS}")

    print(f"\n{'='*60}")
    print(f"FINAL GATE VERDICT: {gate_result}")
    print(f"{'='*60}")

    # Exit code: 0 for PASS/PARTIAL_PASS, 1 for FAIL (for pipeline detection)
    if gate_result == "FAIL":
        sys.exit(1)


if __name__ == "__main__":
    main()
