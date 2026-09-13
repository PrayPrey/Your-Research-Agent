"""Gate metrics computation for H-M3."""

from typing import List, Dict, Any
from positional_analysis import PositionalAnalysis


def compute_gate_metrics(
    analyses: List[PositionalAnalysis],
    gate_1_threshold: float = 0.99,
    gate_2_threshold: float = 0.95
) -> Dict[str, Any]:
    """Compute H-M3 gate validation metrics."""
    valid = [a for a in analyses if a.has_confidence]
    with_markers = [a for a in valid if len(a.hedging_markers) > 0]

    cot_order_count = sum(1 for a in valid if a.cot_then_confidence_order)
    cot_order_rate = cot_order_count / len(valid) if valid else 0.0

    if with_markers:
        all_precede_count = sum(1 for a in with_markers if a.markers_after_confidence == 0)
        all_precede_rate = all_precede_count / len(with_markers)
    else:
        all_precede_rate = 1.0

    return {
        'total_outputs': len(analyses),
        'valid_outputs': len(valid),
        'outputs_with_markers': len(with_markers),
        'cot_order_count': cot_order_count,
        'cot_order_rate': round(cot_order_rate, 4),
        'markers_precede_rate': round(all_precede_rate, 4),
        'gate_1_threshold': gate_1_threshold,
        'gate_2_threshold': gate_2_threshold,
        'gate_1_pass': cot_order_rate > gate_1_threshold,
        'gate_2_pass': all_precede_rate > gate_2_threshold,
        'all_gates_pass': cot_order_rate > gate_1_threshold and all_precede_rate > gate_2_threshold
    }
