import json
import numpy as np
import scipy.stats
from itertools import combinations
from config import ALPHA_DIRECTIONAL, ALPHA_NULL, BOOTSTRAP_N, PARADIGMS, H_D1_RESULTS_PATH


INTERPRETATION_STRINGS = {
    'augmentation_invariance_supported': (
        'MoCo-v3 (contrastive) encodes more spurious features than ERM on Waterbirds '
        'but not on CelebA. This supports the augmentation-invariance hypothesis: '
        'the contrastive objective makes features invariant to augmentations that preserve '
        'spurious attributes (background texture on WB), but CelebA spurious attribute '
        '(Male) is not systematically invariant under standard augmentations.'
    ),
    'label_correlation_confound': (
        'MoCo-v3 > ERM on both datasets suggests that the spurious encoding difference '
        'is not dataset-specific but reflects a general property of contrastive vs supervised '
        'learning. The augmentation-invariance hypothesis cannot be isolated from label '
        'correlation effects.'
    ),
    'effects_cancel': (
        'No significant difference between MoCo-v3 and ERM on either dataset. '
        'Effects may cancel across paradigms or the probe ratio metric lacks sensitivity.'
    ),
    'supervised_label_drives_spurious': (
        'ERM encodes more spurious features than MoCo-v3 on Waterbirds. '
        'This contradicts the augmentation-invariance hypothesis and suggests that '
        'supervised label correlation drives spurious encoding more than contrastive objectives.'
    ),
    'partial_ca': (
        'Waterbirds test fails but CelebA shows significant difference. '
        'Results are inconclusive for the directional hypothesis.'
    ),
}


def cohen_d(a, b):
    n1, n2 = len(a), len(b)
    pooled_std = np.sqrt(((n1-1)*np.var(a, ddof=1) + (n2-1)*np.var(b, ddof=1)) / (n1+n2-2))
    return (np.mean(a) - np.mean(b)) / (pooled_std + 1e-10)


def directional_test(moco_ratios, erm_ratios):
    t, _ = scipy.stats.ttest_ind(moco_ratios, erm_ratios, alternative='two-sided')
    _, p_one = scipy.stats.ttest_ind(moco_ratios, erm_ratios, alternative='greater')
    d = cohen_d(moco_ratios, erm_ratios)
    diff = float(np.mean(moco_ratios) - np.mean(erm_ratios))
    return {
        't': float(t),
        'p_directional': float(p_one),
        'cohen_d': float(d),
        'diff_mean': diff,
        'moco_mean': float(np.mean(moco_ratios)),
        'erm_mean': float(np.mean(erm_ratios)),
        'direction': 'moco_gt_erm' if diff > 0 else 'erm_gt_moco',
    }


def null_test(moco_ratios, erm_ratios):
    t, p_two = scipy.stats.ttest_ind(moco_ratios, erm_ratios, alternative='two-sided')
    d = cohen_d(moco_ratios, erm_ratios)
    diff = float(np.mean(moco_ratios) - np.mean(erm_ratios))
    return {
        't': float(t),
        'p_two_sided': float(p_two),
        'cohen_d': float(d),
        'diff_mean': diff,
        'moco_mean': float(np.mean(moco_ratios)),
        'erm_mean': float(np.mean(erm_ratios)),
    }


def evaluate_gate(p_wb_directional, p_ca_two_sided,
                  alpha_directional=ALPHA_DIRECTIONAL, alpha_null=ALPHA_NULL):
    wb_pass = p_wb_directional < alpha_directional
    ca_pass = p_ca_two_sided > alpha_null
    if wb_pass and ca_pass:
        return 'full_support'
    if wb_pass and not ca_pass:
        return 'partial_wb'
    if not wb_pass and ca_pass:
        return 'partial_ca'
    return 'no_support'


def interpret_result(wb_result, ca_result, gate_verdict):
    wb_direction = wb_result['direction']
    if gate_verdict == 'full_support' and wb_direction == 'moco_gt_erm':
        interp = 'augmentation_invariance_supported'
    elif gate_verdict == 'partial_wb' and wb_direction == 'moco_gt_erm':
        interp = 'label_correlation_confound'
    elif gate_verdict == 'no_support':
        if wb_direction == 'erm_gt_moco':
            interp = 'supervised_label_drives_spurious'
        else:
            interp = 'effects_cancel'
    else:
        interp = 'partial_ca'
    return {
        'gate_verdict': gate_verdict,
        'interpretation': interp,
        'scientific_finding': INTERPRETATION_STRINGS[interp],
    }


def pearson_r_with_ci(ratios_all, wga_gaps_all, n_bootstrap=BOOTSTRAP_N, seed=0):
    r, p = scipy.stats.pearsonr(ratios_all, wga_gaps_all)
    rng = np.random.default_rng(seed)
    n = len(ratios_all)
    boot_rs = []
    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        r_b, _ = scipy.stats.pearsonr(ratios_all[idx], wga_gaps_all[idx])
        boot_rs.append(r_b)
    ci_low, ci_high = np.percentile(boot_rs, [2.5, 97.5])
    return {'r': float(r), 'p': float(p),
            'ci_low': float(ci_low), 'ci_high': float(ci_high), 'n': n}


def run_ablation_a(wb_results):
    moco = np.array(wb_results['moco'])
    erm  = np.array(wb_results['erm'])
    return {'description': 'WB-only directional test (MoCo > ERM)',
            **directional_test(moco, erm)}


def run_ablation_b(celeba_results):
    moco = np.array(celeba_results['moco'])
    erm  = np.array(celeba_results['erm'])
    return {'description': 'CelebA-only null test',
            **null_test(moco, erm)}


def run_ablation_c(wb_results):
    pairs = {}
    for p1, p2 in combinations(PARADIGMS, 2):
        a = np.array(wb_results[p1])
        b = np.array(wb_results[p2])
        key = f'{p1}_vs_{p2}'
        pairs[key] = directional_test(a, b)
    return {'description': 'All-paradigm WB directional pairs', 'pairs': pairs}


def run_ablation_d(wb_results, celeba_results):
    erm_wb  = np.array(wb_results['erm'])
    moco_wb = np.array(wb_results['moco'])
    _, p_reversed = scipy.stats.ttest_ind(erm_wb, moco_wb, alternative='greater')
    d = cohen_d(erm_wb, moco_wb)
    return {
        'description': 'Reversed direction: ERM > MoCo on Waterbirds',
        'p_reversed_directional': float(p_reversed),
        'cohen_d': float(d),
        'erm_mean': float(np.mean(erm_wb)),
        'moco_mean': float(np.mean(moco_wb)),
        'diff_erm_minus_moco': float(np.mean(erm_wb) - np.mean(moco_wb)),
        'note': 'Expected to be significant per H-E1 (ERM=1.052 > MoCo=1.027)',
    }


def run_all_analyses(wb_results, celeba_results, wga_data=None, save_path=None):
    erm_wb  = np.array(wb_results['erm'])
    moco_wb = np.array(wb_results['moco'])
    erm_ca  = np.array(celeba_results['erm'])
    moco_ca = np.array(celeba_results['moco'])

    wb_primary = directional_test(moco_wb, erm_wb)
    ca_primary = null_test(moco_ca, erm_ca)
    gate = evaluate_gate(wb_primary['p_directional'], ca_primary['p_two_sided'])
    interpretation = interpret_result(wb_primary, ca_primary, gate)

    ablations = {
        'A': run_ablation_a(wb_results),
        'B': run_ablation_b(celeba_results),
        'C': run_ablation_c(wb_results),
        'D': run_ablation_d(wb_results, celeba_results),
    }

    pearson = None
    if wga_data:
        from wb_loader import load_wb_results
        # Build ratio/gap arrays if provided
        pass

    results = {
        'wb_primary': wb_primary,
        'ca_primary': ca_primary,
        'gate_verdict': gate,
        'interpretation': interpretation,
        'ablations': ablations,
        'pearson_r': pearson,
        'wb_summary': {p: {'mean': float(np.mean(wb_results[p])),
                           'std': float(np.std(wb_results[p]))}
                       for p in wb_results},
        'ca_summary': {p: {'mean': float(np.mean(celeba_results[p])),
                           'std': float(np.std(celeba_results[p]))}
                       for p in celeba_results},
    }

    if save_path is None:
        save_path = H_D1_RESULTS_PATH
    with open(save_path, 'w') as f:
        json.dump(results, f, indent=2, default=float)
    print(f"[analysis] Results saved → {save_path}")
    return results
