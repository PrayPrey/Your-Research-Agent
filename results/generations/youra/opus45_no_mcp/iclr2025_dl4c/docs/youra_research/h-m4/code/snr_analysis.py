"""SNR analysis for H-M4: compare fine-always vs fine-gated policies."""
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import numpy as np


@dataclass
class SNRResult:
    snr: float
    mean_signal: float
    mean_noise: float
    n_samples: int
    signals: List[float]
    noises: List[float]


def extract_signal_noise(result: Dict[str, float]) -> Optional[Tuple[float, float]]:
    """Extract signal (gt_grad) and noise (other_grad) from H-M3 result."""
    if result is None:
        return None
    gt_grad = result.get("gt_grad")
    other_grad = result.get("other_grad")
    if gt_grad is None or other_grad is None:
        return None
    return float(gt_grad), float(other_grad)


def compute_policy_snr(results: List[Dict[str, float]], policy: str) -> SNRResult:
    """Compute aggregate SNR for a policy."""
    signals, noises = [], []
    for r in results:
        pair = extract_signal_noise(r)
        if pair is not None:
            signals.append(pair[0])
            noises.append(pair[1])

    if not signals:
        return SNRResult(snr=0.0, mean_signal=0.0, mean_noise=0.0,
                         n_samples=0, signals=[], noises=[])

    mean_signal = float(np.mean(signals))
    mean_noise = float(np.mean(noises)) + 1e-8
    snr = mean_signal / mean_noise

    return SNRResult(
        snr=snr,
        mean_signal=mean_signal,
        mean_noise=mean_noise,
        n_samples=len(signals),
        signals=signals,
        noises=noises
    )


def compare_policies(
    u_line_results: List[Dict],
    u_ignore_results: List[Dict]
) -> Dict[str, SNRResult]:
    """
    Compare aggregate SNR between two policies:
    - fine_always: all U_line + U_ignore samples
    - fine_gated: U_line samples only
    """
    all_results = u_line_results + u_ignore_results
    snr_always = compute_policy_snr(all_results, "fine_always")
    snr_gated = compute_policy_snr(u_line_results, "fine_gated")
    return {"fine_always": snr_always, "fine_gated": snr_gated}
