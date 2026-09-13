"""H-M4 Analyzer: Timing normalization and cross-benchmark statistics"""
import numpy as np
from typing import Optional
from detector import smooth_curve, second_derivative, detect_peak
from config import TimingConfig, CONFIG


def normalize_peak_timing(peak_epoch: int, total_epochs: int) -> float:
    """Convert absolute epoch to percentage of total training."""
    return (peak_epoch / total_epochs) * 100.0


def range_compliant(normalized_timing: Optional[float], expected_range: tuple) -> bool:
    """Check if timing falls within expected range."""
    if normalized_timing is None:
        return False
    return expected_range[0] <= normalized_timing <= expected_range[1]


def analyze_single_run(benchmark: str, seed: int, wga: np.ndarray,
                       total_epochs: int, config: TimingConfig) -> dict:
    """Full detection + normalization for one (benchmark, seed) curve."""
    smoothed = smooth_curve(wga, config.smoothing_window)
    d2 = second_derivative(smoothed)
    peak_info = detect_peak(d2, config.prominence_threshold)

    if peak_info['detected']:
        norm_timing = normalize_peak_timing(peak_info['epoch'], total_epochs)
        in_range = range_compliant(norm_timing, config.expected_range)
    else:
        norm_timing = None
        in_range = False

    return {
        'benchmark': benchmark,
        'seed': seed,
        'detected': peak_info['detected'],
        'peak_epoch': peak_info['epoch'],
        'total_epochs': total_epochs,
        'normalized_timing_percent': norm_timing,
        'in_expected_range': in_range,
        'expected_range': config.expected_range,
        'snr': peak_info['snr'],
        'prominence': peak_info['prominence']
    }


def analyze_all_runs(wga_curves: dict, config: TimingConfig) -> dict:
    """Analyze all (benchmark, seed) combinations."""
    results = {}
    for benchmark, seeds_data in wga_curves.items():
        results[benchmark] = {'runs': []}
        total_epochs = config.benchmarks[benchmark].total_epochs
        for seed, wga in seeds_data.items():
            run_result = analyze_single_run(benchmark, seed, wga, total_epochs, config)
            results[benchmark]['runs'].append(run_result)
    return results


def aggregate_per_benchmark(results: dict, config: TimingConfig) -> dict:
    """Per-benchmark: mean/std timing, detection rate, in_range flag."""
    aggregated = {}
    for benchmark, data in results.items():
        runs = data['runs']
        detected = [r for r in runs if r['detected']]
        detection_rate = len(detected) / len(runs) if runs else 0.0

        if detected:
            timings = [r['normalized_timing_percent'] for r in detected]
            mean_timing = float(np.mean(timings))
            timing_std = float(np.std(timings))
            in_range = range_compliant(mean_timing, config.expected_range)
            snrs = [r['snr'] for r in detected if r['snr'] is not None]
            mean_snr = float(np.mean(snrs)) if snrs else 0.0
        else:
            mean_timing = None
            timing_std = None
            in_range = False
            mean_snr = 0.0

        aggregated[benchmark] = {
            'detection_rate': detection_rate,
            'mean_normalized_timing': mean_timing,
            'timing_std': timing_std,
            'in_expected_range': in_range,
            'expected_range': config.expected_range,
            'mean_snr': mean_snr,
            'total_seeds': len(runs),
            'detected_count': len(detected)
        }
    return aggregated


def compute_cross_benchmark_variance(aggregated: dict) -> dict:
    """Std dev of per-benchmark mean timing across all benchmarks."""
    timings = [a['mean_normalized_timing'] for a in aggregated.values()
               if a['mean_normalized_timing'] is not None]
    if len(timings) < 2:
        return {'variance': 0.0, 'n_benchmarks': len(timings)}
    return {
        'variance': float(np.std(timings)),
        'n_benchmarks': len(timings),
        'mean_across_benchmarks': float(np.mean(timings)),
        'range': (float(min(timings)), float(max(timings)))
    }


def compute_range_compliance(aggregated: dict, expected_range: tuple = (20.0, 40.0)) -> float:
    """% of benchmarks with mean timing in expected range."""
    valid = [a for a in aggregated.values() if a['mean_normalized_timing'] is not None]
    if not valid:
        return 0.0
    in_range = sum(1 for a in valid if a['in_expected_range'])
    return in_range / len(valid) * 100.0


def detect_seed_outliers(results: dict, config: TimingConfig) -> dict:
    """Flag seeds >2 std from per-benchmark mean."""
    outliers = {}
    for benchmark, data in results.items():
        runs = data['runs']
        detected = [r for r in runs if r['detected']]
        if len(detected) < 2:
            outliers[benchmark] = []
            continue
        timings = [r['normalized_timing_percent'] for r in detected]
        mean_t = np.mean(timings)
        std_t = np.std(timings)
        if std_t < 1e-6:
            outliers[benchmark] = []
            continue
        outliers[benchmark] = [
            r['seed'] for r in detected
            if abs(r['normalized_timing_percent'] - mean_t) > 2 * std_t
        ]
    return outliers


def evaluate_gate(aggregated: dict, cross_var: dict, compliance: float,
                  config: TimingConfig) -> dict:
    """PASS: 100% compliance + variance<10%. CONDITIONAL: consistent but outside range. FAIL: otherwise."""
    variance = cross_var.get('variance', 0.0)
    all_in_range = all(a['in_expected_range'] for a in aggregated.values()
                       if a['mean_normalized_timing'] is not None)
    detection_ok = all(a['detection_rate'] >= config.detection_rate_target
                       for a in aggregated.values())

    if all_in_range and variance < config.variance_target and detection_ok:
        status = 'PASS'
    elif variance < 15.0 and detection_ok:
        status = 'CONDITIONAL'
    else:
        status = 'FAIL'

    return {
        'status': status,
        'metrics': {
            'range_compliance_percent': compliance,
            'all_in_range': all_in_range,
            'cross_benchmark_variance': variance,
            'variance_target': config.variance_target,
            'detection_ok': detection_ok
        },
        'gate_type': 'SHOULD_WORK'
    }
