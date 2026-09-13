"""End-to-end experiment orchestration for H-E1."""
import os
import sys
import subprocess
import argparse
import json
import yaml

CODE_DIR = os.path.dirname(os.path.abspath(__file__))


def run_cmd(cmd, cwd=None):
    print(f'\n>>> {" ".join(cmd)}')
    result = subprocess.run(cmd, cwd=cwd or CODE_DIR, check=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_root', default=os.path.join(CODE_DIR, 'data'))
    parser.add_argument('--output_root', default=CODE_DIR)
    args = parser.parse_args()

    code = CODE_DIR
    wb_data = os.path.join(args.data_root, 'waterbirds', 'waterbird_complete95_forest2water2')
    celeba_data = os.path.join(args.data_root, 'celeba', 'celebA_v1.0')
    wb_ckpt_dir = os.path.join(args.output_root, 'checkpoints', 'h-e1', 'waterbirds')
    celeba_ckpt_dir = os.path.join(args.output_root, 'checkpoints', 'h-e1', 'celeba')
    emb_dir = os.path.join(args.output_root, 'embeddings', 'h-e1')
    results_dir = os.path.join(args.output_root, 'results', 'h-e1')
    figures_dir = os.path.abspath(os.path.join(args.output_root, '..', 'figures'))

    wb_config = os.path.join(code, 'configs', 'waterbirds.yaml')
    celeba_config = os.path.join(code, 'configs', 'celeba.yaml')

    print('='*60)
    print('H-E1: Spurious Direction Recovery via K-Means Clustering')
    print('='*60)

    # Step 1: Train Waterbirds (5 epochs)
    print('\n[1/5] Training ERM on Waterbirds (5 epochs)...')
    run_cmd([sys.executable, os.path.join(code, 'train.py'),
             '--config', wb_config, '--dataset', 'waterbirds',
             '--output_dir', wb_ckpt_dir, '--stop_epoch', '5'])

    # Step 2: Train CelebA (5 epochs)
    print('\n[2/5] Training ERM on CelebA (5 epochs)...')
    run_cmd([sys.executable, os.path.join(code, 'train.py'),
             '--config', celeba_config, '--dataset', 'celeba',
             '--output_dir', celeba_ckpt_dir, '--stop_epoch', '5'])

    # Step 3: Extract embeddings
    print('\n[3/5] Extracting embeddings -- Waterbirds...')
    wb_ckpt = os.path.join(wb_ckpt_dir, 'epoch_005.pt')
    run_cmd([sys.executable, os.path.join(code, 'extract.py'),
             '--ckpt', wb_ckpt, '--dataset', 'waterbirds',
             '--data_dir', wb_data, '--output_dir', emb_dir])

    print('\n[4/5] Extracting embeddings -- CelebA...')
    celeba_ckpt = os.path.join(celeba_ckpt_dir, 'epoch_005.pt')
    run_cmd([sys.executable, os.path.join(code, 'extract.py'),
             '--ckpt', celeba_ckpt, '--dataset', 'celeba',
             '--data_dir', celeba_data, '--output_dir', emb_dir])

    # Step 5: Evaluate gate
    print('\n[5/5] Gate evaluation...')
    run_cmd([sys.executable, os.path.join(code, 'evaluate.py'),
             '--wb_embeddings', os.path.join(emb_dir, 'waterbirds_epoch5.npy'),
             '--wb_group_ids', os.path.join(emb_dir, 'waterbirds_group_ids.npy'),
             '--celeba_embeddings', os.path.join(emb_dir, 'celeba_epoch5.npy'),
             '--celeba_group_ids', os.path.join(emb_dir, 'celeba_group_ids.npy'),
             '--output_dir', results_dir,
             '--figures_dir', figures_dir,
             '--embeddings_dir', emb_dir])

    print('\n' + '='*60)
    print('EXPERIMENT COMPLETE')
    print('='*60)

    overall_yaml = os.path.join(results_dir, 'overall_results.yaml')
    if os.path.exists(overall_yaml):
        with open(overall_yaml) as f:
            overall = yaml.safe_load(f)
        gate_pass = overall.get('gate', {}).get('overall_pass', False)
        print(f'Final gate result: {"PASS" if gate_pass else "FAIL"}')


if __name__ == '__main__':
    main()
