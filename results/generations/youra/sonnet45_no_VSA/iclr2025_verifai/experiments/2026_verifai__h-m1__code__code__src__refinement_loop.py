"""Iterative refinement loop orchestrator."""

from enum import Enum
from typing import List, Optional
from dataclasses import dataclass
from pathlib import Path

from .llm_client import ACSLSpec, SpecificationGenerator
from .verifier import FramaCVerifier, VerificationResult
from .feedback_parser import FeedbackExtractor, StructuredFeedback


class ConvergenceReason(Enum):
    """Why the loop terminated."""
    ALL_PROVED = "all_proved"
    MAX_ITERATIONS = "max_iterations"
    NO_IMPROVEMENT = "no_improvement"
    ERROR = "error"


@dataclass
class RefinementIteration:
    """Single iteration state."""
    iteration: int
    spec: ACSLSpec
    result: VerificationResult
    feedback: Optional[StructuredFeedback]
    proof_discharge_rate: float


@dataclass
class RefinementHistory:
    """Complete refinement process."""
    iterations: List[RefinementIteration]
    final_spec: ACSLSpec
    convergence_reason: ConvergenceReason
    total_iterations: int
    improvement_achieved: bool


class IterativeRefinementLoop:
    """Main refinement orchestrator."""

    def __init__(
        self,
        generator: SpecificationGenerator,
        verifier: FramaCVerifier,
        feedback_extractor: FeedbackExtractor,
        max_iterations: int = 10,
        no_improvement_threshold: int = 3
    ):
        """
        Args:
            max_iterations: Maximum refinement attempts
            no_improvement_threshold: Stop after N iterations with no progress
        """
        self.generator = generator
        self.verifier = verifier
        self.feedback_extractor = feedback_extractor
        self.max_iterations = max_iterations
        self.no_improvement_threshold = no_improvement_threshold

    def synthesize_specification(
        self,
        c_code: str,
        temp_dir: Path
    ) -> RefinementHistory:
        """
        Complete synthesis pipeline with iterative refinement.

        Args:
            c_code: Unannotated C program
            temp_dir: Working directory

        Returns:
            RefinementHistory with all iterations
        """
        # Initial generation
        initial_spec = self.generator.generate_initial_spec(c_code)

        iterations = []
        no_improvement_count = 0
        prev_discharge_rate = 0.0

        current_spec = initial_spec

        for iteration in range(self.max_iterations):
            # Verify current specification
            result = self.verifier.verify(current_spec, temp_dir)

            # Record iteration
            iterations.append(RefinementIteration(
                iteration=iteration,
                spec=current_spec,
                result=result,
                feedback=None,  # Will be set below
                proof_discharge_rate=result.proof_discharge_rate
            ))

            # Check convergence: All proved
            if result.proof_discharge_rate >= 100.0:
                return RefinementHistory(
                    iterations=iterations,
                    final_spec=current_spec,
                    convergence_reason=ConvergenceReason.ALL_PROVED,
                    total_iterations=iteration + 1,
                    improvement_achieved=self._check_improvement(iterations)
                )

            # Extract feedback (3 dimensions)
            feedback = self.feedback_extractor.extract_feedback(result, current_spec)
            iterations[-1].feedback = feedback

            if feedback is None:
                # All proved (edge case)
                return RefinementHistory(
                    iterations=iterations,
                    final_spec=current_spec,
                    convergence_reason=ConvergenceReason.ALL_PROVED,
                    total_iterations=iteration + 1,
                    improvement_achieved=self._check_improvement(iterations)
                )

            # Check improvement
            if result.proof_discharge_rate <= prev_discharge_rate:
                no_improvement_count += 1
            else:
                no_improvement_count = 0  # Reset counter

            # Early stopping: No improvement
            if no_improvement_count >= self.no_improvement_threshold:
                return RefinementHistory(
                    iterations=iterations,
                    final_spec=current_spec,
                    convergence_reason=ConvergenceReason.NO_IMPROVEMENT,
                    total_iterations=iteration + 1,
                    improvement_achieved=self._check_improvement(iterations)
                )

            # Refine specification using feedback
            try:
                current_spec = self._refine_spec(current_spec, feedback, iteration)
            except Exception as e:
                print(f"Error during refinement iteration {iteration}: {e}")
                return RefinementHistory(
                    iterations=iterations,
                    final_spec=current_spec,
                    convergence_reason=ConvergenceReason.ERROR,
                    total_iterations=iteration + 1,
                    improvement_achieved=self._check_improvement(iterations)
                )

            prev_discharge_rate = result.proof_discharge_rate

        # Max iterations reached
        return RefinementHistory(
            iterations=iterations,
            final_spec=current_spec,
            convergence_reason=ConvergenceReason.MAX_ITERATIONS,
            total_iterations=self.max_iterations,
            improvement_achieved=self._check_improvement(iterations)
        )

    def _refine_spec(
        self,
        current_spec: ACSLSpec,
        feedback: StructuredFeedback,
        iteration: int
    ) -> ACSLSpec:
        """Refinement using LLM with structured feedback."""

        prompt = f"""TASK: Refine ACSL specification based on verification feedback.

ITERATION: {iteration + 1}

CURRENT SPECIFICATION:
```c
{current_spec.annotated_code}
```

{feedback.natural_language}

REFINEMENT INSTRUCTIONS:
1. Analyze the counterexample values (Dimension 1: Witness)
2. Identify which proof obligations failed (Dimension 2: Structure)
3. Fix dependency violations (Dimension 3: Dependencies)
4. Preserve already-proved obligations (do NOT weaken working specs)
5. Focus on critical failures first (preconditions, loop invariants)

REFINEMENT STRATEGIES:
- If precondition failed: Strengthen requires clauses to exclude counterexample
- If loop invariant failed: Adjust invariant to hold at loop entry/preservation/exit
- If postcondition failed: Check if loop invariant implies postcondition
- If dependency broken: Ensure dependent clauses are consistent

OUTPUT FORMAT:
Return ONLY the refined C code with updated ACSL annotations.
"""

        response = self.generator.client.messages.create(
            model=self.generator.model,
            max_tokens=4096,
            temperature=0.5,  # Lower temperature for refinement
            messages=[{"role": "user", "content": prompt}]
        )

        refined_code = self.generator._extract_code_from_response(response.content)
        return self.generator._parse_acsl_spec(refined_code)

    def _check_improvement(self, iterations: List[RefinementIteration]) -> bool:
        """Check if ANY iteration improved proof discharge rate."""
        if len(iterations) < 2:
            return False

        for i in range(1, len(iterations)):
            if iterations[i].proof_discharge_rate > iterations[i-1].proof_discharge_rate:
                return True

        return False
