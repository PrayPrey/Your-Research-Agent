"""Validation and export module for H-E1 Cross-Benchmark Analysis."""

import json
import os
import numpy as np
from typing import Dict, Any


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy types."""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


class ResultValidator:
    """Result validation and export for H-E1."""

    def __init__(self, hypothesis_folder: str):
        self.hypothesis_folder = hypothesis_folder
        self.results_dir = os.path.join(hypothesis_folder, 'results')
        os.makedirs(self.results_dir, exist_ok=True)

    def save_metrics_summary(
        self,
        correlations: Dict[str, Dict[str, float]],
        gate_status: Dict[str, Any],
        falsification: Dict[str, Any],
        model_overlap: int
    ) -> None:
        """Export to {hypothesis_folder}/results/metrics_summary.json"""
        metrics = {
            'hypothesis_id': 'h-e1',
            'model_overlap': model_overlap,
            'correlations': correlations,
            'gate_status': {
                'passed': gate_status['passed'],
                'success_count': gate_status['success_count'],
                'target_range': gate_status['target_range'],
                'success_pairs': gate_status['success_pairs'],
                'all_pairs': gate_status['all_pairs']
            },
            'falsification': {
                'falsified': falsification['falsified'],
                'flags': falsification['flags'],
                'reasons': falsification['reasons']
            }
        }

        output_path = os.path.join(self.results_dir, 'metrics_summary.json')
        with open(output_path, 'w') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)

        print(f"\n[Export] Saved metrics summary: {output_path}")

    def generate_validation_report(self, results: Dict[str, Any]) -> str:
        """Generate validation report text. Returns: report string"""
        lines = []
        lines.append("=" * 70)
        lines.append("H-E1 VALIDATION REPORT")
        lines.append("Cross-Benchmark Ranking Disagreement Analysis")
        lines.append("=" * 70)
        lines.append("")

        # Model overlap
        lines.append(f"Model Overlap: {results['model_overlap']} models")
        lines.append("")

        # Correlations
        lines.append("Pairwise Spearman Correlations:")
        lines.append("-" * 70)
        for pair_info in results['gate_status']['all_pairs']:
            pair = pair_info['pair']
            rho = pair_info['rho']
            pval = pair_info['pvalue']
            in_range = pair_info['in_range']
            sig = pair_info['significant']

            status = "✓" if pair_info['meets_gate'] else "✗"
            lines.append(f"  {status} {pair:25s} ρ = {rho:6.3f}, p = {pval:.4f}  "
                        f"[Range: {'YES' if in_range else 'NO ':3s}, Sig: {'YES' if sig else 'NO ':3s}]")

        lines.append("")

        # Gate status
        gate = results['gate_status']
        lines.append("Gate Verdict (MUST_WORK):")
        lines.append("-" * 70)
        lines.append(f"  Target Range: [{gate['target_range'][0]}, {gate['target_range'][1]}]")
        lines.append(f"  Success Count: {gate['success_count']}/3 pairs")
        lines.append(f"  Gate Status: {'PASSED ✓' if gate['passed'] else 'FAILED ✗'}")

        if gate['success_pairs']:
            lines.append(f"  Success Pairs: {', '.join(gate['success_pairs'])}")

        lines.append("")

        # Falsification check
        falsif = results['falsification']
        lines.append("Falsification Check:")
        lines.append("-" * 70)
        lines.append(f"  Falsified: {'YES ✗' if falsif['falsified'] else 'NO ✓'}")

        if falsif['flags']:
            lines.append(f"  Flags: {', '.join(falsif['flags'])}")
            for reason in falsif['reasons']:
                lines.append(f"    - {reason}")
        else:
            lines.append("  No falsification conditions detected")

        lines.append("")
        lines.append("=" * 70)

        report = "\n".join(lines)
        print("\n" + report)

        # Save to file
        report_path = os.path.join(self.results_dir, 'validation_report.txt')
        with open(report_path, 'w') as f:
            f.write(report)

        print(f"\n[Export] Saved validation report: {report_path}")

        return report
