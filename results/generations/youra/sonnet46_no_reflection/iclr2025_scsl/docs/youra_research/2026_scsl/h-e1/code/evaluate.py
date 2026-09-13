"""Gate check, results reporting, end-to-end orchestration."""
import os
import sys
import argparse
import json
import yaml
import numpy as np
from typing import Dict, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cluster as cluster_module
import visualize


AMI_THRESHOLD = 0.5
PURITY_THRESHOLD = 0.75


def check_gate(results: Dict) -> Tuple[bool, Dict]:
    per_dataset = {}
    for ds, r in results.items():
        ami_pass = r['ami'] >= AMI_THRESHOLD
        purity_pass = r['worst_purity'] >= PURITY_THRESHOLD
        per_dataset[ds] = {
            'ami': r['ami'],
            'worst_purity': r['worst_purity'],
            'ami_pass': ami_pass,
            'purity_pass': purity_pass,
            'dataset_pass': ami_pass and purity_pass,
        }
    gate_pass = all(v['dataset_pass'] for v in per_dataset.values())
    return gate_pass, per_dataset


def format_results_table(results: Dict) -> str:
    header = f"{'Dataset':<15} {'AMI':>8} {'Purity':>8} {'AMI>=0.5':>10} {'Purity>=0.75':>12} {'Pass':>6}"
    sep = '-' * len(header)
    rows = [header, sep]
    for ds, r in results.items():
        ami_ok = 'Y' if r.get('ami_pass', r['ami'] >= AMI_THRESHOLD) else 'N'
        pur_ok = 'Y' if r.get('purity_pass', r['worst_purity'] >= PURITY_THRESHOLD) else 'N'
        ds_pass = 'Y' if r.get('dataset_pass', ami_ok == 'Y' and pur_ok == 'Y') else 'N'
        rows.append(f"{ds:<15} {r['ami']:>8.4f} {r['worst_purity']:>8.4f} {ami_ok:>10} {pur_ok:>12} {ds_pass:>6}")
    return '\n'.join(rows)


def save_results(results: Dict, gate_pass: bool, output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)
    overall = {
        'hypothesis': 'h-e1',
        'epoch': 5,
        'datasets': {ds: {'ami': r['ami'], 'worst_purity': r['worst_purity'],
                          'pass': r.get('dataset_pass', False)}
                     for ds, r in results.items()},
        'gate': {
            'overall_pass': gate_pass,
            'gate_type': 'MUST_WORK',
            'blocks_pipeline': True,
            'ami_threshold': AMI_THRESHOLD,
            'purity_threshold': PURITY_THRESHOLD,
        }
    }
    yaml_path = os.path.join(output_dir, 'overall_results.yaml')
    json_path = os.path.join(output_dir, 'overall_results.json')
    with open(yaml_path, 'w') as f:
        yaml.dump(overall, f, default_flow_style=False)
    with open(json_path, 'w') as f:
        json.dump(overall, f, indent=2)
    print(f'Results saved: {yaml_path}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--wb_embeddings', required=True)
    parser.add_argument('--wb_group_ids', required=True)
    parser.add_argument('--celeba_embeddings', required=True)
    parser.add_argument('--celeba_group_ids', required=True)
    parser.add_argument('--output_dir', required=True)
    parser.add_argument('--figures_dir', default='./figures')
    parser.add_argument('--embeddings_dir', default='./embeddings/h-e1')
    args = parser.parse_args()

    print('\n' + '='*60)
    print('H-E1 GATE EVALUATION')
    print('='*60)

    results = {}
    for ds, emb_path, grp_path in [
        ('waterbirds', args.wb_embeddings, args.wb_group_ids),
        ('celeba', args.celeba_embeddings, args.celeba_group_ids),
    ]:
        print(f'\nRunning k-means probe on {ds}...')
        r = cluster_module.probe(emb_path, grp_path)
        results[ds] = r
        print(f'  AMI={r["ami"]:.4f}, Purity={r["worst_purity"]:.4f}')
        print(f'  Random baseline: AMI={r["ami_random"]:.4f}, Purity={r["purity_random"]:.4f}')
        print(f'  Mechanism OK: {r["mechanism_ok"]}')

    gate_pass, per_dataset = check_gate(results)
    for ds, r in per_dataset.items():
        results[ds].update(r)

    print('\n' + format_results_table(per_dataset))
    print('\n' + '='*60)
    if gate_pass:
        print('GATE: PASS -- H-E1 validated. H-M1, H-M2, H-M3, H-M4, H-C1 UNBLOCKED')
    else:
        print('GATE: FAIL -- H-M1, H-M2, H-M3, H-M4, H-C1 BLOCKED')
    print('='*60)

    save_results(results, gate_pass, args.output_dir)
    visualize.generate_all_figures(results, args.embeddings_dir, args.figures_dir)


if __name__ == '__main__':
    main()
