"""H-M3: Gate evaluation — SHOULD_WORK gate logic."""
import json
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
BONF_ALPHA = 0.0167


def main():
    with open(os.path.join(RESULTS_DIR, 'model_results.json')) as f:
        model = json.load(f)

    is_monotonic = model['is_monotonic']
    n_passing = model['n_adjacent_contrasts_passing']
    cat_irr = model['cat_irr']
    adj_pvals = model['adj_pvals']
    n_corpus = model['n_corpus']

    gate_pass = is_monotonic and (n_passing >= 2)
    result_str = 'PASS' if gate_pass else 'INFORMATIVE_NEGATIVE'

    bin_counts_path = os.path.join(RESULTS_DIR, 'bin_counts.csv')
    bin_counts = {}
    if os.path.exists(bin_counts_path):
        bc = pd.read_csv(bin_counts_path, index_col=0)
        bin_counts = bc.iloc[:, 0].to_dict()

    primary_results = {
        'gate': 'SHOULD_WORK',
        'hypothesis': 'H-M3',
        'is_monotonic': is_monotonic,
        'n_adjacent_contrasts_passing': n_passing,
        'bonferroni_alpha': BONF_ALPHA,
        'passed': gate_pass,
        'result': result_str,
        'irr_by_category': {k: round(v['irr'], 4) for k, v in cat_irr.items()},
        'ci_lower': {k: round(v['ci_lower'], 4) for k, v in cat_irr.items()},
        'ci_upper': {k: round(v['ci_upper'], 4) for k, v in cat_irr.items()},
        'pvalues': {k: float(v['pvalue']) for k, v in cat_irr.items()},
        'n_corpus': int(n_corpus),
        'bin_counts': bin_counts,
        'adj_pvals': adj_pvals,
        'irr_values': model['irr_values'],
    }

    out_path = os.path.join(RESULTS_DIR, 'primary_results.json')
    with open(out_path, 'w') as f:
        json.dump(primary_results, f, indent=2)

    print(f"Gate result: {result_str}")
    print(f"  is_monotonic={is_monotonic}, n_passing={n_passing}/3")
    print(f"  IRR(1-2)={cat_irr.get('1-2',{}).get('irr','?'):.4f}, "
          f"IRR(3-5)={cat_irr.get('3-5',{}).get('irr','?'):.4f}, "
          f"IRR(6+)={cat_irr.get('6+',{}).get('irr','?'):.4f}")
    print(f"Primary results saved: {out_path}")
    return primary_results


if __name__ == '__main__':
    main()
