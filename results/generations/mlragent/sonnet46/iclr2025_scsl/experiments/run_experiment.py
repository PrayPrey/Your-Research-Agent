"""
Main experiment runner for Causal Gradient Decomposition (CGD) paper.
Tests hypothesis: CAGR reduces spurious feature reliance and improves worst-group accuracy.

Experiments:
1. Linear Synthetic - controlled spurious correlation with OOD test (reversed spurious attr)
2. Image Synthetic (Waterbirds-style) - image-level spurious features with OOD test

Key hypothesis: Spurious features have lower curvature loss landscape directions,
causing SGD to preferentially rely on them. CAGR penalizes spurious gradient directions
to improve generalization to minority groups (and OOD settings).
"""
import os
import sys
import json
import time
import logging
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

sys.path.insert(0, os.path.dirname(__file__))

from datasets import (
    LinearSyntheticDataset, LinearSyntheticOODDataset,
    WaterbirdsSimDataset, WaterbirdsSimOODDataset,
    make_group_splits, get_group_counts
)
from models import LinearClassifier, SimpleCNN
from trainers import ERMTrainer, GroupDROTrainer, JTTTrainer, CAGRTrainer, DFRTrainer
from evaluation import evaluate, compute_group_gap
from visualization import (
    plot_training_curves, plot_accuracy_curves, plot_method_comparison,
    plot_spurious_dominance, plot_per_group_accuracy, plot_curvature_analysis,
    plot_overall_comparison
)

# Configuration
CONFIG = {
    'output_dir': os.path.join(os.path.dirname(__file__), '..', 'results'),
    'device': 'cuda:0' if torch.cuda.is_available() else 'cpu',
    'seed': 42,
    'n_groups': 4,
    'batch_size': 128,
    'num_workers': 2,

    # Linear dataset - make it harder
    'linear': {
        'n_train': 6000,
        'n_test_ood': 2000,
        'd_causal': 5,
        'd_spurious': 20,
        'causal_snr': 0.5,      # weak causal signal
        'spurious_snr': 2.0,    # strong spurious signal
        'spurious_prob_train': 0.95,   # train: 95% correlated
        'spurious_prob_ood': 0.05,     # test: 5% correlated (reversed)
        'epochs': 50,
        'lr': 1e-3,
        'weight_decay': 1e-4,
        'hidden_dim': 128,
    },

    # Image dataset (Waterbirds-style)
    'image': {
        'n_train': 5000,
        'n_test_ood': 2000,
        'spurious_prob_train': 0.95,
        'spurious_prob_ood': 0.05,
        'causal_strength': 0.8,
        'spurious_strength': 3.0,
        'epochs': 40,
        'lr': 1e-3,
        'weight_decay': 1e-4,
        'img_size': 28,
    },

    # CAGR specific
    'cagr': {
        'beta': 2.0,
        'hessian_update_freq': 40,
    },

    # JTT
    'jtt': {
        'phase1_epochs': 15,
        'upweight': 50,
    },

    # DFR
    'dfr': {
        'phase1_epochs': 25,
    }
}


def set_seed(seed):
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def setup_logging(log_path):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def run_training(trainer, train_loader, val_loader, ood_test_loader,
                 n_epochs, logger, device, val_name='Val', test_name='OOD Test'):
    """Generic training loop that records metrics at each epoch."""
    results = {
        'train_losses': [],
        'val_losses': [],
        'val_overall_accs': [],
        'val_wga': [],
        'rho_history': [],
        'alpha_history': [],
        'curvature_lambda_c': [],
        'curvature_lambda_s': [],
    }

    loss_fn = nn.CrossEntropyLoss()

    for epoch in range(1, n_epochs + 1):
        train_loss, train_acc = trainer.train_epoch(train_loader)

        # Compute val loss
        trainer.model.eval()
        val_loss = 0.0
        val_total = 0
        with torch.no_grad():
            for batch in val_loader:
                if len(batch) == 3:
                    inputs, targets, _ = batch
                else:
                    inputs, targets = batch
                inputs, targets = inputs.to(device), targets.to(device)
                logits = trainer.model(inputs)
                val_loss += loss_fn(logits, targets).item() * len(targets)
                val_total += len(targets)
        val_loss /= max(val_total, 1)

        val_metrics = evaluate(trainer.model, val_loader, device)
        extra = trainer.get_extra_metrics()

        results['train_losses'].append(train_loss)
        results['val_losses'].append(val_loss)
        results['val_overall_accs'].append(val_metrics['overall_acc'])
        results['val_wga'].append(val_metrics['worst_group_acc'])

        if 'rho' in extra and extra['rho'] is not None:
            results['rho_history'].append(extra['rho'])
        if 'alpha' in extra and isinstance(extra.get('alpha'), float):
            results['alpha_history'].append(extra['alpha'])
        if 'lambda_c' in extra:
            results['curvature_lambda_c'].append(extra['lambda_c'])
            results['curvature_lambda_s'].append(extra['lambda_s'])

        rho_str = f" | rho: {extra['rho']:.3f}" if isinstance(extra.get('rho'), float) else ""
        logger.info(
            f"  [{trainer.name}] Epoch {epoch}/{n_epochs} | "
            f"Train Loss: {train_loss:.4f} | {val_name} WGA: {val_metrics['worst_group_acc']:.4f}"
            + rho_str
        )

    # Final OOD test evaluation
    ood_metrics = evaluate(trainer.model, ood_test_loader, device)
    results['final_test_overall_acc'] = ood_metrics['overall_acc']
    results['final_test_wga'] = ood_metrics['worst_group_acc']
    results['final_test_per_group_acc'] = {
        int(k): float(v) for k, v in ood_metrics['per_group_acc'].items()
    }

    # Also record in-dist val final
    val_metrics_final = evaluate(trainer.model, val_loader, device)
    results['final_val_overall_acc'] = val_metrics_final['overall_acc']
    results['final_val_wga'] = val_metrics_final['worst_group_acc']

    logger.info(
        f"  [{trainer.name}] Final {test_name} | Overall: {ood_metrics['overall_acc']:.4f} | "
        f"WGA: {ood_metrics['worst_group_acc']:.4f}"
    )

    return results


def run_linear_experiment(config, logger, output_dir):
    """Run experiment on linear synthetic dataset with OOD test."""
    logger.info("\n" + "="*60)
    logger.info("EXPERIMENT 1: Linear Synthetic Dataset (OOD Evaluation)")
    logger.info("="*60)

    device = config['device']
    set_seed(config['seed'])
    lcfg = config['linear']

    logger.info(f"Dataset params: spurious_prob={lcfg['spurious_prob_train']}, "
                f"causal_snr={lcfg['causal_snr']}, spurious_snr={lcfg['spurious_snr']}")
    train_full = LinearSyntheticDataset(
        n_samples=lcfg['n_train'],
        d_causal=lcfg['d_causal'],
        d_spurious=lcfg['d_spurious'],
        causal_snr=lcfg['causal_snr'],
        spurious_snr=lcfg['spurious_snr'],
        spurious_prob=lcfg['spurious_prob_train'],
        seed=config['seed']
    )
    train_set, val_set = make_group_splits(train_full, seed=config['seed'])

    ood_test = LinearSyntheticOODDataset(
        n_samples=lcfg['n_test_ood'],
        d_causal=lcfg['d_causal'],
        d_spurious=lcfg['d_spurious'],
        causal_snr=lcfg['causal_snr'],
        spurious_snr=lcfg['spurious_snr'],
        ood_spurious_prob=lcfg['spurious_prob_ood'],
        seed=config['seed'] + 100
    )

    logger.info(f"Train: {len(train_set)}, Val (ID): {len(val_set)}, OOD Test: {len(ood_test)}")
    group_counts = get_group_counts(train_set)
    logger.info(f"Train group distribution: {group_counts}")

    train_loader = DataLoader(train_set, batch_size=config['batch_size'], shuffle=True,
                              num_workers=config['num_workers'])
    val_loader = DataLoader(val_set, batch_size=config['batch_size'], shuffle=False,
                            num_workers=config['num_workers'])
    ood_loader = DataLoader(ood_test, batch_size=config['batch_size'], shuffle=False,
                            num_workers=config['num_workers'])

    input_dim = lcfg['d_causal'] + lcfg['d_spurious']
    causal_idx = train_full.causal_idx
    spurious_idx = train_full.spurious_idx

    all_results = {}

    # --- ERM ---
    logger.info("\n[ERM] Training ERM baseline...")
    set_seed(config['seed'])
    model_erm = LinearClassifier(input_dim, num_classes=2, hidden_dim=lcfg['hidden_dim']).to(device)
    trainer_erm = ERMTrainer(model_erm, lr=lcfg['lr'], weight_decay=lcfg['weight_decay'], device=device)
    all_results['ERM'] = run_training(trainer_erm, train_loader, val_loader, ood_loader,
                                      lcfg['epochs'], logger, device)

    # --- GroupDRO ---
    logger.info("\n[GroupDRO] Training GroupDRO...")
    set_seed(config['seed'])
    model_dro = LinearClassifier(input_dim, num_classes=2, hidden_dim=lcfg['hidden_dim']).to(device)
    trainer_dro = GroupDROTrainer(model_dro, n_groups=config['n_groups'],
                                   lr=lcfg['lr'], weight_decay=lcfg['weight_decay'],
                                   device=device)
    all_results['GroupDRO'] = run_training(trainer_dro, train_loader, val_loader, ood_loader,
                                           lcfg['epochs'], logger, device)

    # --- JTT ---
    logger.info("\n[JTT] Training JTT Phase 1 (ERM identification)...")
    set_seed(config['seed'])
    model_jtt_p1 = LinearClassifier(input_dim, num_classes=2, hidden_dim=lcfg['hidden_dim']).to(device)
    trainer_jtt_p1 = JTTTrainer(model_jtt_p1, None, lr=lcfg['lr'],
                                  weight_decay=lcfg['weight_decay'],
                                  upweight=config['jtt']['upweight'], device=device)
    for ep in range(config['jtt']['phase1_epochs']):
        trainer_jtt_p1.train_epoch(train_loader)
    n_errors = trainer_jtt_p1.identify_errors(train_loader)
    logger.info(f"[JTT] Phase 1 done. Error set: {n_errors} samples")

    logger.info("[JTT] Training JTT Phase 2 (upweighted)...")
    set_seed(config['seed'] + 1)
    model_jtt_p2 = LinearClassifier(input_dim, num_classes=2, hidden_dim=lcfg['hidden_dim']).to(device)
    trainer_jtt_p2 = JTTTrainer(model_jtt_p2, None, lr=lcfg['lr'],
                                  weight_decay=lcfg['weight_decay'],
                                  upweight=config['jtt']['upweight'], device=device)
    trainer_jtt_p2.phase = 2
    trainer_jtt_p2.error_set = trainer_jtt_p1.error_set
    all_results['JTT'] = run_training(trainer_jtt_p2, train_loader, val_loader, ood_loader,
                                      lcfg['epochs'], logger, device)

    # --- DFR ---
    logger.info("\n[DFR] Training DFR Phase 1 (ERM)...")
    set_seed(config['seed'])
    model_dfr = LinearClassifier(input_dim, num_classes=2, hidden_dim=lcfg['hidden_dim']).to(device)
    trainer_dfr = DFRTrainer(model_dfr, lr=lcfg['lr'], weight_decay=lcfg['weight_decay'], device=device)
    for ep in range(config['dfr']['phase1_epochs']):
        trainer_dfr.train_epoch(train_loader)
    trainer_dfr.freeze_features()
    trainer_dfr.phase = 2
    logger.info("[DFR] Training DFR Phase 2 (last layer retrain)...")
    all_results['DFR'] = run_training(trainer_dfr, train_loader, val_loader, ood_loader,
                                      lcfg['epochs'], logger, device)

    # --- CAGR (Proposed Method) ---
    logger.info("\n[CAGR] Training CAGR (Proposed Method)...")
    set_seed(config['seed'])
    model_cagr = LinearClassifier(input_dim, num_classes=2, hidden_dim=lcfg['hidden_dim']).to(device)
    trainer_cagr = CAGRTrainer(
        model_cagr,
        causal_idx=causal_idx,
        spurious_idx=spurious_idx,
        lr=lcfg['lr'],
        weight_decay=lcfg['weight_decay'],
        beta=config['cagr']['beta'],
        hessian_update_freq=config['cagr']['hessian_update_freq'],
        device=device
    )
    cagr_res = run_training(trainer_cagr, train_loader, val_loader, ood_loader,
                             lcfg['epochs'], logger, device)
    cagr_res['rho_history'] = trainer_cagr.rho_history
    cagr_res['alpha_history'] = trainer_cagr.alpha_history
    if trainer_cagr.lambda_c != 1.0:
        cagr_res['curvature_lambda_c'].append(trainer_cagr.lambda_c)
        cagr_res['curvature_lambda_s'].append(trainer_cagr.lambda_s)
    all_results['CAGR'] = cagr_res

    # Generate plots
    ds_name = 'Linear_Synthetic'
    logger.info(f"\nGenerating plots for {ds_name}...")
    plot_training_curves(all_results, output_dir, ds_name)
    plot_accuracy_curves(all_results, output_dir, ds_name)
    plot_method_comparison(all_results, output_dir, ds_name)
    plot_per_group_accuracy(all_results, output_dir, ds_name)
    if all_results['CAGR']['rho_history']:
        plot_spurious_dominance(all_results['CAGR'], output_dir, ds_name)
    if all_results['CAGR']['curvature_lambda_c']:
        curvature_data = {
            'lambda_c': all_results['CAGR']['curvature_lambda_c'],
            'lambda_s': all_results['CAGR']['curvature_lambda_s'],
        }
        plot_curvature_analysis(curvature_data, output_dir, ds_name)

    return all_results


def run_image_experiment(config, logger, output_dir):
    """Run experiment on image synthetic dataset (Waterbirds-style) with OOD test."""
    logger.info("\n" + "="*60)
    logger.info("EXPERIMENT 2: Image Synthetic Dataset (Waterbirds-style, OOD Evaluation)")
    logger.info("="*60)

    device = config['device']
    set_seed(config['seed'])
    icfg = config['image']

    logger.info(f"Dataset params: spurious_prob={icfg['spurious_prob_train']}, "
                f"causal_strength={icfg['causal_strength']}, "
                f"spurious_strength={icfg['spurious_strength']}")
    train_full = WaterbirdsSimDataset(
        n_samples=icfg['n_train'],
        img_size=icfg['img_size'],
        spurious_prob=icfg['spurious_prob_train'],
        causal_strength=icfg['causal_strength'],
        spurious_strength=icfg['spurious_strength'],
        seed=config['seed']
    )
    train_set, val_set = make_group_splits(train_full, seed=config['seed'])

    ood_test = WaterbirdsSimOODDataset(
        n_samples=icfg['n_test_ood'],
        img_size=icfg['img_size'],
        ood_spurious_prob=icfg['spurious_prob_ood'],
        causal_strength=icfg['causal_strength'],
        spurious_strength=icfg['spurious_strength'],
        seed=config['seed'] + 100
    )

    logger.info(f"Train: {len(train_set)}, Val (ID): {len(val_set)}, OOD Test: {len(ood_test)}")
    group_counts = get_group_counts(train_set)
    logger.info(f"Train group distribution: {group_counts}")

    train_loader = DataLoader(train_set, batch_size=config['batch_size'], shuffle=True,
                              num_workers=config['num_workers'])
    val_loader = DataLoader(val_set, batch_size=config['batch_size'], shuffle=False,
                            num_workers=config['num_workers'])
    ood_loader = DataLoader(ood_test, batch_size=config['batch_size'], shuffle=False,
                            num_workers=config['num_workers'])

    causal_idx = list(range(icfg['img_size'] // 4, 3 * icfg['img_size'] // 4))
    spurious_idx = list(range(0, icfg['img_size'] // 4))

    all_results = {}

    # --- ERM ---
    logger.info("\n[ERM] Training ERM baseline...")
    set_seed(config['seed'])
    model_erm = SimpleCNN(in_channels=1, num_classes=2, img_size=icfg['img_size']).to(device)
    trainer_erm = ERMTrainer(model_erm, lr=icfg['lr'], weight_decay=icfg['weight_decay'], device=device)
    all_results['ERM'] = run_training(trainer_erm, train_loader, val_loader, ood_loader,
                                      icfg['epochs'], logger, device)

    # --- GroupDRO ---
    logger.info("\n[GroupDRO] Training GroupDRO...")
    set_seed(config['seed'])
    model_dro = SimpleCNN(in_channels=1, num_classes=2, img_size=icfg['img_size']).to(device)
    trainer_dro = GroupDROTrainer(model_dro, n_groups=config['n_groups'],
                                   lr=icfg['lr'], weight_decay=icfg['weight_decay'],
                                   device=device)
    all_results['GroupDRO'] = run_training(trainer_dro, train_loader, val_loader, ood_loader,
                                           icfg['epochs'], logger, device)

    # --- JTT ---
    logger.info("\n[JTT] Training JTT Phase 1...")
    set_seed(config['seed'])
    model_jtt_p1 = SimpleCNN(in_channels=1, num_classes=2, img_size=icfg['img_size']).to(device)
    trainer_jtt_p1 = JTTTrainer(model_jtt_p1, None, lr=icfg['lr'],
                                  weight_decay=icfg['weight_decay'],
                                  upweight=config['jtt']['upweight'], device=device)
    for ep in range(config['jtt']['phase1_epochs']):
        trainer_jtt_p1.train_epoch(train_loader)
    n_errors = trainer_jtt_p1.identify_errors(train_loader)
    logger.info(f"[JTT] Error set: {n_errors}")

    logger.info("[JTT] Training JTT Phase 2...")
    set_seed(config['seed'] + 1)
    model_jtt_p2 = SimpleCNN(in_channels=1, num_classes=2, img_size=icfg['img_size']).to(device)
    trainer_jtt_p2 = JTTTrainer(model_jtt_p2, None, lr=icfg['lr'],
                                  weight_decay=icfg['weight_decay'],
                                  upweight=config['jtt']['upweight'], device=device)
    trainer_jtt_p2.phase = 2
    trainer_jtt_p2.error_set = trainer_jtt_p1.error_set
    all_results['JTT'] = run_training(trainer_jtt_p2, train_loader, val_loader, ood_loader,
                                      icfg['epochs'], logger, device)

    # --- DFR ---
    logger.info("\n[DFR] Training DFR Phase 1...")
    set_seed(config['seed'])
    model_dfr = SimpleCNN(in_channels=1, num_classes=2, img_size=icfg['img_size']).to(device)
    trainer_dfr = DFRTrainer(model_dfr, lr=icfg['lr'], weight_decay=icfg['weight_decay'], device=device)
    for ep in range(config['dfr']['phase1_epochs']):
        trainer_dfr.train_epoch(train_loader)
    trainer_dfr.freeze_features()
    trainer_dfr.phase = 2
    logger.info("[DFR] Training DFR Phase 2...")
    all_results['DFR'] = run_training(trainer_dfr, train_loader, val_loader, ood_loader,
                                      icfg['epochs'], logger, device)

    # --- CAGR (Proposed Method) ---
    logger.info("\n[CAGR] Training CAGR (Proposed Method)...")
    set_seed(config['seed'])
    model_cagr = SimpleCNN(in_channels=1, num_classes=2, img_size=icfg['img_size']).to(device)
    trainer_cagr = CAGRTrainer(
        model_cagr,
        causal_idx=causal_idx,
        spurious_idx=spurious_idx,
        lr=icfg['lr'],
        weight_decay=icfg['weight_decay'],
        beta=config['cagr']['beta'],
        hessian_update_freq=config['cagr']['hessian_update_freq'],
        device=device
    )
    cagr_res = run_training(trainer_cagr, train_loader, val_loader, ood_loader,
                             icfg['epochs'], logger, device)
    cagr_res['rho_history'] = trainer_cagr.rho_history
    cagr_res['alpha_history'] = trainer_cagr.alpha_history
    all_results['CAGR'] = cagr_res

    # Generate plots
    ds_name = 'Image_Waterbirds_Style'
    logger.info(f"\nGenerating plots for {ds_name}...")
    plot_training_curves(all_results, output_dir, ds_name)
    plot_accuracy_curves(all_results, output_dir, ds_name)
    plot_method_comparison(all_results, output_dir, ds_name)
    plot_per_group_accuracy(all_results, output_dir, ds_name)
    if all_results['CAGR']['rho_history']:
        plot_spurious_dominance(all_results['CAGR'], output_dir, ds_name)

    return all_results


def save_results(all_dataset_results, output_dir):
    """Save results to JSON."""
    def to_serializable(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, dict):
            return {str(k): to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [to_serializable(x) for x in obj]
        return obj

    results_path = os.path.join(output_dir, 'results.json')
    with open(results_path, 'w') as f:
        json.dump(to_serializable(all_dataset_results), f, indent=2)
    print(f"Saved results: {results_path}")


def print_summary(all_dataset_results, logger):
    """Print results summary."""
    logger.info("\n" + "="*65)
    logger.info("RESULTS SUMMARY (OOD Test Performance)")
    logger.info("="*65)
    for ds_name, ds_results in all_dataset_results.items():
        logger.info(f"\n{ds_name}:")
        logger.info(f"{'Method':<12} {'OOD Overall':>13} {'OOD WGA':>10} {'Val WGA':>10}")
        logger.info("-" * 50)
        for method, res in ds_results.items():
            oa = res['final_test_overall_acc']
            wga = res['final_test_wga']
            val_wga = res.get('final_val_wga', 0.0)
            logger.info(f"{method:<12} {oa:>13.4f} {wga:>10.4f} {val_wga:>10.4f}")


def main():
    output_dir = os.path.abspath(CONFIG['output_dir'])
    os.makedirs(output_dir, exist_ok=True)

    log_path = os.path.join(output_dir, 'log.txt')
    logger = setup_logging(log_path)

    logger.info("Starting CGD Spurious Correlation Experiments")
    logger.info(f"Device: {CONFIG['device']}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Config:\n{json.dumps(CONFIG, indent=2)}")

    start_time = time.time()
    all_dataset_results = {}

    # Experiment 1: Linear Synthetic
    linear_results = run_linear_experiment(CONFIG, logger, output_dir)
    all_dataset_results['Linear_Synthetic'] = linear_results

    # Experiment 2: Image Synthetic (Waterbirds-style)
    image_results = run_image_experiment(CONFIG, logger, output_dir)
    all_dataset_results['Image_Waterbirds_Style'] = image_results

    # Overall comparison plot
    logger.info("\nGenerating overall comparison plot...")
    try:
        plot_overall_comparison(all_dataset_results, output_dir)
    except Exception as e:
        logger.warning(f"Overall comparison failed: {e}")

    # Save results
    save_results(all_dataset_results, output_dir)

    elapsed = time.time() - start_time
    logger.info(f"\nAll experiments completed in {elapsed/60:.1f} minutes")

    print_summary(all_dataset_results, logger)

    return all_dataset_results


if __name__ == '__main__':
    main()
