"""
04_evaluate_gate.py — H-M2 Gate Evaluation
SHOULD_WORK gate: IRR CI_lower >= 1.05 AND p < 0.05
INFORMATIVE_NEGATIVE is not a failure — document and proceed.
"""

import json
from pathlib import Path

PROJECT_ROOT    = Path(__file__).resolve().parents[4]
MODEL_RESULTS   = PROJECT_ROOT / "docs/youra_research/h-m2/results/model_results.json"
PRIMARY_RESULTS = PROJECT_ROOT / "docs/youra_research/h-m2/results/primary_results.json"

GATE_CI_LOWER_MIN = 1.05
GATE_PVAL_MAX     = 0.05


def evaluate_gate(irr: float, ci_lower: float, ci_upper: float, pval: float,
                  n_tagged: int, attenuation_ratio: float) -> dict:
    passed = (ci_lower >= GATE_CI_LOWER_MIN) and (pval < GATE_PVAL_MAX)
    result_label = 'PASS' if passed else 'INFORMATIVE_NEGATIVE'
    return {
        'gate': 'SHOULD_WORK',
        'gate_threshold': {'ci_lower_min': GATE_CI_LOWER_MIN, 'pval_max': GATE_PVAL_MAX},
        'passed': passed,
        'IRR_P2': round(irr, 4),
        'CI_lower_P2': round(ci_lower, 4),
        'CI_upper_P2': round(ci_upper, 4),
        'p_value_P2': float(pval),
        'result': result_label,
        'n_tagged_subset': n_tagged,
        'attenuation_ratio': round(attenuation_ratio, 4) if attenuation_ratio else None,
        'interpretation': (
            'Dose-response confirmed: more tags → more N_tasks above binary threshold.'
            if passed else
            'Informative negative: binary has_tags threshold captures full FAIR F1 signal. '
            'Continuous tag count does not add incremental predictive value. Proceed to H-M3.'
        )
    }


def main():
    print("=" * 60)
    print("H-M2 Step 04: Gate Evaluation")
    print("=" * 60)

    print(f"\n[1] Loading {MODEL_RESULTS}...")
    with open(MODEL_RESULTS) as f:
        results = json.load(f)

    print("\n[2] Extracting proposed model IV stats...")
    proposed = results['proposed_with_fe']
    iv = proposed['log_tag_count_p1_stats']
    irr       = iv['irr']
    ci_lower  = iv['ci_lower']
    ci_upper  = iv['ci_upper']
    pval      = iv['pval']
    n_tagged  = proposed['n_obs']
    attenuation = results.get('attenuation_ratio', None)

    print(f"  IRR_P2      = {irr:.4f}")
    print(f"  CI_lower_P2 = {ci_lower:.4f}")
    print(f"  CI_upper_P2 = {ci_upper:.4f}")
    print(f"  p_value_P2  = {pval:.4e}")
    print(f"  N_tagged    = {n_tagged}")

    print("\n[3] Evaluating SHOULD_WORK gate...")
    gate_result = evaluate_gate(irr, ci_lower, ci_upper, pval, n_tagged, attenuation)

    verdict = gate_result['result']
    print(f"\n  *** GATE VERDICT: {verdict} ***")
    print(f"  {gate_result['interpretation']}")

    print(f"\n[4] Saving {PRIMARY_RESULTS}...")
    PRIMARY_RESULTS.parent.mkdir(parents=True, exist_ok=True)
    with open(PRIMARY_RESULTS, 'w') as f:
        json.dump(gate_result, f, indent=2)
    print(f"  Results saved to {PRIMARY_RESULTS}")

    print("\n Gate evaluation complete")


if __name__ == "__main__":
    main()
