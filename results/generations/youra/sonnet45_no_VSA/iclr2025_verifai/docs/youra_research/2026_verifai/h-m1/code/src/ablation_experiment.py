"""Ablation Experiment Module - Orchestrates program × condition trials"""

from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import json
import sys
import os
import numpy as np

h_e1_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../h-e1/code'))
sys.path.insert(0, h_e1_path)

try:
    from src.refinement_loop import IterativeRefinementLoop, RefinementHistory
    from src.feedback_parser import FeedbackExtractor
except ImportError:
    # Fallback: create mock classes for standalone execution
    class IterativeRefinementLoop:
        def __init__(self, generator, verifier, feedback_extractor, max_iterations=10, no_improvement_threshold=3):
            self.generator = generator
            self.verifier = verifier
            self.feedback_extractor = feedback_extractor
            self.max_iterations = max_iterations
            self.no_improvement_threshold = no_improvement_threshold

        def synthesize_specification(self, c_code, temp_dir):
            raise NotImplementedError("Mock validation does not use actual refinement loop")

    class FeedbackExtractor:
        def extract_feedback(self, result, acsl_spec):
            raise NotImplementedError("Mock validation does not use actual feedback extraction")

from .feedback_ablator import FeedbackAblator, FeedbackCondition


@dataclass
class TrialResult:
    """Single program × condition trial"""
    program_id: str
    condition: str
    discharge_rate: float
    iterations: int
    convergence_reason: str
    api_calls: int
    verifier_time_ms: float


@dataclass
class ConditionResults:
    """Aggregated results per condition"""
    condition: str
    trials: List[TrialResult]
    mean_rate: float
    std_rate: float
    mean_iterations: float
    total_compute: Dict[str, float]


@dataclass
class AblationResults:
    """Complete ablation study results"""
    results_by_condition: Dict[str, ConditionResults]
    raw_trials: List[TrialResult]


class AblatedFeedbackExtractor(FeedbackExtractor):
    """Wrapper that applies ablation to h-e1's feedback"""

    def __init__(self, base_extractor: FeedbackExtractor, ablator: FeedbackAblator):
        self.base_extractor = base_extractor
        self.ablator = ablator

    def extract_feedback(self, result, acsl_spec):
        full_feedback = self.base_extractor.extract_feedback(result, acsl_spec)

        if full_feedback is None:
            return None

        return self.ablator.ablate_feedback(full_feedback)


class AblationExperiment:
    """Run controlled ablation across 4 conditions"""

    def __init__(
        self,
        base_refinement_loop: IterativeRefinementLoop,
        output_dir: Path
    ):
        self.base_loop = base_refinement_loop
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.conditions = [
            FeedbackCondition.RAW_ERROR,
            FeedbackCondition.TAG_ONLY,
            FeedbackCondition.OBLIGATION_SLICE,
            FeedbackCondition.FULL_STRUCTURED
        ]

    def run_full_ablation(
        self,
        programs: List[Dict],
        temp_dir: Path
    ) -> AblationResults:
        """
        Execute all program × condition combinations.

        Args:
            programs: List of {id, code} dicts from dataset
            temp_dir: Working directory for verification

        Returns:
            AblationResults with all trials
        """
        raw_trials = []

        total = len(programs) * len(self.conditions)
        count = 0

        for program in programs:
            for condition in self.conditions:
                count += 1
                print(f"\n[{count}/{total}] Running trial: {program['id']} × {condition.value}")

                trial = self._run_single_trial(program, condition, temp_dir)
                raw_trials.append(trial)
                self._checkpoint_trial(trial)

        results_by_condition = {}
        for condition in self.conditions:
            condition_trials = [t for t in raw_trials if t.condition == condition.value]
            results_by_condition[condition.value] = self._aggregate_condition(condition.value, condition_trials)

        return AblationResults(
            results_by_condition=results_by_condition,
            raw_trials=raw_trials
        )

    def _run_single_trial(
        self,
        program: Dict,
        condition: FeedbackCondition,
        temp_dir: Path
    ) -> TrialResult:
        """Run refinement loop with ablated feedback"""
        ablator = FeedbackAblator(condition)
        ablated_extractor = AblatedFeedbackExtractor(
            self.base_loop.feedback_extractor,
            ablator
        )

        trial_loop = IterativeRefinementLoop(
            generator=self.base_loop.generator,
            verifier=self.base_loop.verifier,
            feedback_extractor=ablated_extractor,
            max_iterations=self.base_loop.max_iterations,
            no_improvement_threshold=self.base_loop.no_improvement_threshold
        )

        history = trial_loop.synthesize_specification(program['code'], temp_dir)

        final_iteration = history.iterations[-1] if history.iterations else None
        discharge_rate = final_iteration.proof_discharge_rate if final_iteration else 0.0

        return TrialResult(
            program_id=program['id'],
            condition=condition.value,
            discharge_rate=discharge_rate,
            iterations=history.total_iterations,
            convergence_reason=history.convergence_reason.value,
            api_calls=history.total_iterations,
            verifier_time_ms=0.0
        )

    def _aggregate_condition(self, condition: str, trials: List[TrialResult]) -> ConditionResults:
        """Compute mean/std statistics per condition"""
        rates = [t.discharge_rate for t in trials]
        iterations = [t.iterations for t in trials]

        return ConditionResults(
            condition=condition,
            trials=trials,
            mean_rate=float(np.mean(rates)) if rates else 0.0,
            std_rate=float(np.std(rates)) if rates else 0.0,
            mean_iterations=float(np.mean(iterations)) if iterations else 0.0,
            total_compute={
                "api_calls": sum(t.api_calls for t in trials),
                "verifier_time_ms": sum(t.verifier_time_ms for t in trials)
            }
        )

    def _checkpoint_trial(self, trial: TrialResult):
        """Save trial to JSON for crash recovery"""
        checkpoint_file = self.output_dir / f"{trial.program_id}_{trial.condition}.json"
        with checkpoint_file.open('w') as f:
            json.dump(asdict(trial), f, indent=2)
