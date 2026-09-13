"""Results aggregation and report generation."""

import json
import logging
from typing import Dict, List, Any
from datetime import datetime


class ResultsAggregator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def aggregate_sequence_results(self, sequence_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(sequence_results)
        passed_forward = sum(1 for r in sequence_results if r['forward']['passed'])
        passed_backward = sum(1 for r in sequence_results if r['backward']['passed'])
        passed_overall = sum(1 for r in sequence_results if r['overall_passed'])

        passed_ssm = None
        if sequence_results[0]['ssm_states'] is not None:
            passed_ssm = sum(1 for r in sequence_results
                           if r['ssm_states'] and r['ssm_states']['passed'])

        return {
            'total_sequences': total,
            'passed_forward': passed_forward,
            'passed_backward': passed_backward,
            'passed_ssm': passed_ssm,
            'passed_overall': passed_overall,
            'pass_rate_forward': passed_forward / total,
            'pass_rate_backward': passed_backward / total,
            'pass_rate_ssm': passed_ssm / total if passed_ssm is not None else None,
            'pass_rate_overall': passed_overall / total
        }


class GateDecisionEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def apply_gate_logic(self, aggregated_results: Dict[str, Any]) -> Dict[str, Any]:
        gate_passed = (aggregated_results['pass_rate_overall'] == 1.0)

        failure_reason = None
        route_to = "H-M1" if gate_passed else "Phase 0"

        if not gate_passed:
            failures = []
            if aggregated_results['pass_rate_forward'] < 1.0:
                failures.append("Forward pass failures detected")
            if aggregated_results['pass_rate_backward'] < 1.0:
                failures.append("Backward pass failures detected")
            if (aggregated_results['pass_rate_ssm'] is not None and
                aggregated_results['pass_rate_ssm'] < 1.0):
                failures.append("SSM state validation failures detected")

            failure_reason = "; ".join(failures)

        return {
            'gate_passed': gate_passed,
            'gate_type': 'MUST_WORK',
            'failure_reason': failure_reason,
            'route_to': route_to,
            'timestamp': datetime.now().isoformat()
        }


class MarkdownReportGenerator:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def generate_report(self, sequence_results: List[Dict[str, Any]],
                       baseline_results: Dict[str, Dict[str, Any]],
                       aggregated_results: Dict[str, Any],
                       gate_decision: Dict[str, Any],
                       model_info: Dict[str, Any],
                       output_path: str):
        report_lines = [
            "# Validation Report: Hypothesis h-e1",
            "",
            f"**Generated:** {datetime.now().isoformat()}",
            f"**Hypothesis:** {self.config.experiment.hypothesis_id}",
            f"**Experiment:** {self.config.experiment.name}",
            "",
            "---",
            "",
            "## 1. Experiment Setup",
            "",
            "### Model Configuration",
            f"- **Model:** {self.config.model.name}",
            f"- **Quantization:** {self.config.quantization.bnb_4bit_quant_type} "
            f"({self.config.quantization.bnb_4bit_compute_dtype})",
            f"- **LoRA Rank:** {self.config.lora.r}",
            f"- **LoRA Alpha:** {self.config.lora.lora_alpha}",
            f"- **Target Modules:** {', '.join(model_info.get('target_modules', []))}",
            f"- **Trainable Parameters:** {model_info.get('trainable_params', 0):,}",
            "",
            "### Dataset Configuration",
            f"- **Dataset:** {self.config.data.dataset_name}",
            f"- **Split:** {self.config.data.split}",
            f"- **Sequence Length:** {self.config.data.sequence_length}",
            f"- **Test Sequences:** {self.config.data.num_test_sequences}",
            "",
            "---",
            "",
            "## 2. Test Results",
            "",
            "### Per-Sequence Validation",
            "",
            "| Sequence | Forward | Backward | SSM States | Overall |",
            "|----------|---------|----------|------------|---------|"
        ]

        for i, result in enumerate(sequence_results):
            seq_id = f"seq_{i:04d}"
            forward = "✅" if result['forward']['passed'] else "❌"
            backward = "✅" if result['backward']['passed'] else "❌"
            ssm = "✅" if (result['ssm_states'] and result['ssm_states']['passed']) else ("❌" if result['ssm_states'] else "N/A")
            overall = "✅" if result['overall_passed'] else "❌"

            report_lines.append(f"| {seq_id} | {forward} | {backward} | {ssm} | {overall} |")

        report_lines.extend([
            "",
            "### Summary Statistics",
            "",
            f"- **Total Sequences:** {aggregated_results['total_sequences']}",
            f"- **Forward Pass Rate:** {aggregated_results['pass_rate_forward']*100:.1f}% "
            f"({aggregated_results['passed_forward']}/{aggregated_results['total_sequences']})",
            f"- **Backward Pass Rate:** {aggregated_results['pass_rate_backward']*100:.1f}% "
            f"({aggregated_results['passed_backward']}/{aggregated_results['total_sequences']})",
        ])

        if aggregated_results['pass_rate_ssm'] is not None:
            report_lines.append(
                f"- **SSM State Pass Rate:** {aggregated_results['pass_rate_ssm']*100:.1f}% "
                f"({aggregated_results['passed_ssm']}/{aggregated_results['total_sequences']})"
            )

        report_lines.extend([
            f"- **Overall Pass Rate:** {aggregated_results['pass_rate_overall']*100:.1f}% "
            f"({aggregated_results['passed_overall']}/{aggregated_results['total_sequences']})",
            "",
            "---",
            "",
            "## 3. Baseline Comparisons",
            "",
            "| Baseline | Configuration | Latency (ms) | Memory (MB) | Status |",
            "|----------|---------------|--------------|-------------|--------|"
        ])

        baseline_configs = {
            'B1': 'fp16, no LoRA',
            'B2': 'fp16 + LoRA',
            'B3': '4-bit, no LoRA',
            'B4': '4-bit + LoRA (PRIMARY)'
        }

        for name in ['B1', 'B3', 'B2']:
            if name in baseline_results and baseline_results[name]['success']:
                result = baseline_results[name]
                status = "✅" if not (result['has_nan'] or result['has_inf']) else "❌"
                report_lines.append(
                    f"| {name} | {baseline_configs[name]} | "
                    f"{result['latency_ms']:.1f} | {result['peak_memory_mb']:.1f} | {status} |"
                )
            elif name in baseline_results:
                report_lines.append(
                    f"| {name} | {baseline_configs[name]} | - | - | ❌ Error |"
                )

        report_lines.extend([
            "",
            "---",
            "",
            "## 4. Gate Decision",
            "",
            f"**Gate Type:** {gate_decision['gate_type']}",
            f"**Decision:** {'PASS ✅' if gate_decision['gate_passed'] else 'FAIL ❌'}",
            f"**Route To:** {gate_decision['route_to']}",
            f"**Timestamp:** {gate_decision['timestamp']}",
            ""
        ])

        if gate_decision['failure_reason']:
            report_lines.extend([
                "### Failure Analysis",
                "",
                f"**Reason:** {gate_decision['failure_reason']}",
                ""
            ])

        report_lines.extend([
            "---",
            "",
            "## 5. Recommendations",
            ""
        ])

        if gate_decision['gate_passed']:
            report_lines.extend([
                "✅ **Functional viability confirmed**",
                "",
                "The integration of LoRA (rank=8) + 4-bit NF4 quantization on Mamba-base 125M is functionally viable.",
                "",
                "**Next Steps:**",
                "- Proceed to H-M1 (LoRA adaptation capability validation)",
                "- Use confirmed target modules for downstream experiments",
                "- Monitor memory and latency in full training runs",
                ""
            ])
        else:
            report_lines.extend([
                "❌ **Functional viability NOT confirmed**",
                "",
                f"**Issue:** {gate_decision['failure_reason']}",
                "",
                "**Recommended Actions:**",
                "- Route to Phase 0 for hypothesis redesign",
                "- Consider alternative quantization methods (8-bit, HQQ)",
                "- Investigate mixed-precision strategies",
                "- Re-evaluate target module selection",
                ""
            ])

        with open(output_path, 'w') as f:
            f.write('\n'.join(report_lines))

        self.logger.info(f"Report generated: {output_path}")
