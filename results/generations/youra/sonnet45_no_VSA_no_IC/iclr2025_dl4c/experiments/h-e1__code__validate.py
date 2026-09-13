"""Validation reporter: gate checking, visualization, state updates."""

import logging
import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

logger = logging.getLogger(__name__)

class ValidationReporter:
    def __init__(self, config: dict):
        self.config = config
        self.gate_thresholds = config["gate"]["thresholds"]

    def check_gate(self, sft_pass1: float, binary_pass1: float, error_type_pass1: float) -> dict:
        """Verify dual-threshold success criteria."""
        logger.info("Checking gate thresholds...")

        absolute_improvement = (binary_pass1 - sft_pass1) * 100

        threshold_1_met = absolute_improvement >= self.gate_thresholds["absolute_improvement"]

        error_type_gain = error_type_pass1 - sft_pass1
        if error_type_gain > 0:
            binary_gain = binary_pass1 - sft_pass1
            retention_ratio = binary_gain / error_type_gain
            threshold_2_met = retention_ratio >= self.gate_thresholds["retention_ratio"]
        else:
            retention_ratio = None
            threshold_2_met = False

        gate_passed = threshold_1_met and threshold_2_met

        result = {
            "gate_passed": gate_passed,
            "absolute_improvement": absolute_improvement,
            "retention_ratio": retention_ratio,
            "threshold_1_met": threshold_1_met,
            "threshold_2_met": threshold_2_met,
            "sft_pass1": sft_pass1,
            "binary_pass1": binary_pass1,
            "error_type_pass1": error_type_pass1
        }

        logger.info(f"Gate Result: {'PASS' if gate_passed else 'FAIL'}")
        logger.info(f"  Absolute Improvement: {absolute_improvement:.2f} pp (threshold: {self.gate_thresholds['absolute_improvement']} pp) - {'✓' if threshold_1_met else '✗'}")
        logger.info(f"  Retention Ratio: {retention_ratio:.2f if retention_ratio else 'N/A'} (threshold: {self.gate_thresholds['retention_ratio']}) - {'✓' if threshold_2_met else '✗'}")

        return result

    def generate_gate_metrics_figure(self, gate_result: dict, output_path: str):
        """Create gate metrics comparison bar chart."""
        logger.info("Generating gate metrics figure...")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

        abs_imp = gate_result["absolute_improvement"]
        abs_threshold = self.gate_thresholds["absolute_improvement"]

        ax1.bar(["Actual", "Threshold"], [abs_imp, abs_threshold],
                color=['green' if abs_imp >= abs_threshold else 'red', 'gray'])
        ax1.set_ylabel("Percentage Points")
        ax1.set_title("Absolute Improvement (Binary - SFT)")
        ax1.axhline(y=abs_threshold, color='black', linestyle='--', linewidth=1)

        if gate_result["retention_ratio"] is not None:
            ret_ratio = gate_result["retention_ratio"]
            ret_threshold = self.gate_thresholds["retention_ratio"]

            ax2.bar(["Actual", "Threshold"], [ret_ratio, ret_threshold],
                    color=['green' if ret_ratio >= ret_threshold else 'red', 'gray'])
            ax2.set_ylabel("Ratio")
            ax2.set_title("Retention Ratio (Binary Gain / Error-Type Gain)")
            ax2.axhline(y=ret_threshold, color='black', linestyle='--', linewidth=1)
        else:
            ax2.text(0.5, 0.5, "Retention Ratio: N/A\n(Error-Type gain ≤ 0)",
                     ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title("Retention Ratio")

        plt.tight_layout()
        plt.savefig(output_path, dpi=300)
        plt.close()

        logger.info(f"Gate metrics figure saved to {output_path}")

    def generate_pass_rates_figure(self, gate_result: dict, output_path: str):
        """Create pass@1 comparison bar chart."""
        logger.info("Generating pass rates figure...")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        fig, ax = plt.subplots(figsize=(8, 6))

        models = ["SFT Baseline", "Binary RLVR", "Error-Type RLVR"]
        pass_rates = [
            gate_result["sft_pass1"] * 100,
            gate_result["binary_pass1"] * 100,
            gate_result["error_type_pass1"] * 100
        ]

        ax.bar(models, pass_rates, color=['gray', 'blue', 'orange'])
        ax.set_ylabel("Pass@1 (%)")
        ax.set_title("HumanEval Pass@1 Comparison")
        ax.set_ylim([0, max(pass_rates) * 1.2])

        for i, v in enumerate(pass_rates):
            ax.text(i, v + max(pass_rates) * 0.02, f"{v:.2f}%", ha='center', va='bottom')

        plt.tight_layout()
        plt.savefig(output_path, dpi=300)
        plt.close()

        logger.info(f"Pass rates figure saved to {output_path}")
