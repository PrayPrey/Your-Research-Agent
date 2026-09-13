from dataclasses import dataclass
from typing import List
import numpy as np
from mutation_tester import KillRateResult

@dataclass
class ComparisonResult:
    program_id: str
    synthesized_kill_rate: float
    gold_kill_rate: float
    relative_performance: float
    synthesized_result: KillRateResult
    gold_result: KillRateResult

@dataclass
class GateDecision:
    gate_passed: bool
    mean_synthesized: float
    mean_gold: float
    threshold: float
    relative_performance: float
    failing_programs: List[str]

class ComparisonAnalyzer:
    def __init__(self, threshold: float = 0.70):
        self.threshold = threshold

    def compare_specs(
        self,
        synthesized_results: List[KillRateResult],
        gold_results: List[KillRateResult]
    ) -> List[ComparisonResult]:
        comparisons = []

        for synth, gold in zip(synthesized_results, gold_results):
            relative_perf = (synth.kill_rate / gold.kill_rate) if gold.kill_rate > 0 else 0.0

            comparisons.append(ComparisonResult(
                program_id=synth.program_id,
                synthesized_kill_rate=synth.kill_rate,
                gold_kill_rate=gold.kill_rate,
                relative_performance=relative_perf,
                synthesized_result=synth,
                gold_result=gold
            ))

        return comparisons

    def compute_gate_decision(self, comparisons: List[ComparisonResult]) -> GateDecision:
        if not comparisons:
            return GateDecision(
                gate_passed=False,
                mean_synthesized=0.0,
                mean_gold=0.0,
                threshold=0.0,
                relative_performance=0.0,
                failing_programs=[]
            )

        synthesized_rates = [c.synthesized_kill_rate for c in comparisons]
        gold_rates = [c.gold_kill_rate for c in comparisons]

        mean_synthesized = np.mean(synthesized_rates)
        mean_gold = np.mean(gold_rates)

        threshold_value = self.threshold * mean_gold
        gate_passed = mean_synthesized >= threshold_value

        relative_performance = mean_synthesized / mean_gold if mean_gold > 0 else 0.0

        failing_programs = [
            c.program_id for c in comparisons
            if c.synthesized_kill_rate < (self.threshold * c.gold_kill_rate)
        ]

        return GateDecision(
            gate_passed=gate_passed,
            mean_synthesized=mean_synthesized,
            mean_gold=mean_gold,
            threshold=threshold_value,
            relative_performance=relative_performance,
            failing_programs=failing_programs
        )

    def generate_statistics(self, comparisons: List[ComparisonResult]) -> dict:
        if not comparisons:
            return {}

        synthesized_rates = [c.synthesized_kill_rate for c in comparisons]
        gold_rates = [c.gold_kill_rate for c in comparisons]
        relative_perfs = [c.relative_performance for c in comparisons]

        return {
            "synthesized": {
                "mean": np.mean(synthesized_rates),
                "std": np.std(synthesized_rates),
                "min": np.min(synthesized_rates),
                "max": np.max(synthesized_rates),
                "median": np.median(synthesized_rates)
            },
            "gold": {
                "mean": np.mean(gold_rates),
                "std": np.std(gold_rates),
                "min": np.min(gold_rates),
                "max": np.max(gold_rates),
                "median": np.median(gold_rates)
            },
            "relative_performance": {
                "mean": np.mean(relative_perfs),
                "std": np.std(relative_perfs),
                "min": np.min(relative_perfs),
                "max": np.max(relative_perfs)
            }
        }
