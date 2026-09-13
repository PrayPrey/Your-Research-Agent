from pathlib import Path
import json
from typing import List
from comparison_analyzer import GateDecision, ComparisonResult

class ValidationReporter:
    def __init__(self, hypothesis_folder: str):
        self.hypothesis_folder = Path(hypothesis_folder)

    def generate_validation_report(
        self,
        gate_decision: GateDecision,
        comparisons: List[ComparisonResult],
        stats: dict
    ) -> str:
        report = f"""# Validation Report: H-C2

## Hypothesis
Synthesized specifications achieve ≥70% mutation kill rate relative to expert-written gold specs, demonstrating non-vacuity

## Gate Result: {'PASSED' if gate_decision.gate_passed else 'FAILED'}

### Summary Statistics

**Synthesized Specifications:**
- Mean Kill Rate: {gate_decision.mean_synthesized:.2f}%
- Threshold Required: {gate_decision.threshold:.2f}%

**Gold Specifications (Baseline):**
- Mean Kill Rate: {gate_decision.mean_gold:.2f}%

**Relative Performance:**
- Synthesized / Gold: {gate_decision.relative_performance:.2f} ({gate_decision.relative_performance * 100:.1f}%)

### Detailed Statistics

**Synthesized Specs:**
- Mean: {stats.get('synthesized', {}).get('mean', 0):.2f}%
- Std Dev: {stats.get('synthesized', {}).get('std', 0):.2f}%
- Min: {stats.get('synthesized', {}).get('min', 0):.2f}%
- Max: {stats.get('synthesized', {}).get('max', 0):.2f}%
- Median: {stats.get('synthesized', {}).get('median', 0):.2f}%

**Gold Specs:**
- Mean: {stats.get('gold', {}).get('mean', 0):.2f}%
- Std Dev: {stats.get('gold', {}).get('std', 0):.2f}%
- Min: {stats.get('gold', {}).get('min', 0):.2f}%
- Max: {stats.get('gold', {}).get('max', 0):.2f}%
- Median: {stats.get('gold', {}).get('median', 0):.2f}%

### Per-Program Results

| Program ID | Synthesized Kill Rate | Gold Kill Rate | Relative Performance |
|------------|----------------------|----------------|---------------------|
"""

        for comp in comparisons[:10]:
            report += f"| {comp.program_id} | {comp.synthesized_kill_rate:.2f}% | {comp.gold_kill_rate:.2f}% | {comp.relative_performance:.2f} |\n"

        if len(comparisons) > 10:
            report += f"\n... and {len(comparisons) - 10} more programs\n"

        if gate_decision.failing_programs:
            report += f"\n### Failing Programs ({len(gate_decision.failing_programs)})\n\n"
            for prog_id in gate_decision.failing_programs[:5]:
                report += f"- {prog_id}\n"
            if len(gate_decision.failing_programs) > 5:
                report += f"- ... and {len(gate_decision.failing_programs) - 5} more\n"

        report += f"""
## Conclusion

The mutation testing validation {'PASSED' if gate_decision.gate_passed else 'FAILED'} the MUST_WORK gate.
Synthesized specifications achieved {gate_decision.mean_synthesized:.2f}% kill rate compared to the threshold of {gate_decision.threshold:.2f}%.

This {'demonstrates' if gate_decision.gate_passed else 'does not demonstrate'} that specifications generated via structured feedback are semantically meaningful and non-vacuous.
"""

        return report

    def save_checkpoint(self, results: dict, checkpoint_name: str):
        checkpoint_path = self.hypothesis_folder / "results" / "checkpoints" / f"{checkpoint_name}.json"
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

        with open(checkpoint_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)

    def load_checkpoint(self, checkpoint_name: str) -> dict:
        checkpoint_path = self.hypothesis_folder / "results" / "checkpoints" / f"{checkpoint_name}.json"

        if not checkpoint_path.exists():
            return {}

        with open(checkpoint_path, 'r') as f:
            return json.load(f)
