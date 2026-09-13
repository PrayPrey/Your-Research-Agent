"""H-M3 Analyzer: Aggregation, gate evaluation, and statistical analysis"""
import numpy as np
from typing import Optional
from detector import smooth_curve, second_derivative, detect_peak, run_sensitivity_analysis
from config import DetectionConfig, CONFIG


def analyze_curve(benchmark: str, seed: int, wga: np.ndarray,
                  config: DetectionConfig) -> dict:
    """Full analysis pipeline for one curve."""
    smoothed = smooth_curve(wga, config.primary_window)
    d2 = second_derivative(smoothed)
    primary_result = detect_peak(d2, config.prominence_threshold)
    sensitivity = run_sensitivity_analysis(wga, config.smoothing_windows,
                                           config.prominence_threshold)
    return {
        'benchmark': benchmark,
        'seed': seed,
        **primary_result,
        'sensitivity': sensitivity,
        'wga': wga.tolist(),
        'smoothed': smoothed.tolist(),
        'd2': d2.tolist()
    }


def aggregate_seed_results(results: list) -> dict:
    """Group results by benchmark, compute detection_rate/variance/snr."""
    by_benchmark = {}
    for r in results:
        bm = r['benchmark']
        if bm not in by_benchmark:
            by_benchmark[bm] = []
        by_benchmark[bm].append(r)
    aggregated = {}
    for bm, group in by_benchmark.items():
        detected = [r for r in group if r['detected']]
        detection_rate = len(detected) / len(group) if group else 0.0
        if detected:
            epochs = [r['epoch'] for r in detected]
            timing_variance = float(np.std(epochs))
            mean_snr = float(np.mean([r['snr'] for r in detected]))
        else:
            timing_variance = float('inf')
            mean_snr = 0.0
        aggregated[bm] = {
            'detection_rate': detection_rate,
            'timing_variance_epochs': timing_variance,
            'mean_snr': mean_snr,
            'total_seeds': len(group),
            'detected_count': len(detected)
        }
    return aggregated


def compute_window_robustness(sensitivity_results: dict, primary_epoch: Optional[int],
                               tolerance_epochs: int = 3) -> float:
    """Compute % of windows detecting same peak within tolerance."""
    if primary_epoch is None:
        return 0.0
    agreements = 0
    total = 0
    for key, result in sensitivity_results.items():
        if key.startswith('w'):
            total += 1
            if result['detected'] and result['epoch'] is not None:
                if abs(result['epoch'] - primary_epoch) <= tolerance_epochs:
                    agreements += 1
    return agreements / total if total > 0 else 0.0


def compute_cross_benchmark_correlation(aggregated: dict, epochs_by_benchmark: dict) -> float:
    """Correlation of normalized peak timing across benchmarks."""
    timings = []
    for bm, stats in aggregated.items():
        if stats['detection_rate'] > 0 and stats['timing_variance_epochs'] != float('inf'):
            normalized = stats.get('mean_epoch', 0) / epochs_by_benchmark.get(bm, 100)
            timings.append(normalized)
    if len(timings) < 2:
        return 0.0
    return float(np.corrcoef(timings, range(len(timings)))[0, 1]) if len(timings) > 1 else 0.0


def evaluate_gate(aggregated: dict, config: DetectionConfig) -> dict:
    """Evaluate MUST_WORK gate: detection_rate>0.8, variance<5, snr>2.0."""
    total_detected = sum(s['detected_count'] for s in aggregated.values())
    total_seeds = sum(s['total_seeds'] for s in aggregated.values())
    overall_rate = total_detected / total_seeds if total_seeds > 0 else 0.0
    all_variances = [s['timing_variance_epochs'] for s in aggregated.values()
                     if s['timing_variance_epochs'] != float('inf')]
    overall_variance = float(np.mean(all_variances)) if all_variances else float('inf')
    all_snrs = [s['mean_snr'] for s in aggregated.values() if s['mean_snr'] > 0]
    overall_snr = float(np.mean(all_snrs)) if all_snrs else 0.0
    passed = (
        overall_rate >= config.detection_rate_target and
        overall_variance <= config.variance_target_epochs and
        overall_snr >= config.snr_target
    )
    return {
        'passed': passed,
        'detection_rate': {
            'value': overall_rate,
            'target': config.detection_rate_target,
            'failure_threshold': 0.5
        },
        'timing_variance_epochs': {
            'value': overall_variance,
            'target': config.variance_target_epochs,
            'failure_threshold': 10.0
        },
        'snr': {
            'value': overall_snr,
            'target': config.snr_target,
            'failure_threshold': 1.0
        }
    }
