"""Complete Refinement Strategy: All components simultaneously (baseline from H-E1)."""

import sys
from pathlib import Path
from typing import List
from dataclasses import dataclass

# Import from h-e1 base hypothesis
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'h-e1' / 'code'))
from src.llm_client import SpecificationGenerator, ACSLSpec
from src.verifier import FramaCVerifier, VerificationResult
from src.feedback_parser import FeedbackExtractor


@dataclass
class CompleteResult:
    """Complete refinement result."""
    final_spec: ACSLSpec
    total_iterations: int
    discharge_history: List[float]
    converged: bool
    convergence_reason: str


class CompleteRefinementStrategy:
    """Generate all spec components simultaneously (baseline)."""

    def __init__(
        self,
        generator: SpecificationGenerator,
        verifier: FramaCVerifier,
        feedback_extractor: FeedbackExtractor,
        max_iterations: int = 10
    ):
        self.generator = generator
        self.verifier = verifier
        self.feedback_extractor = feedback_extractor
        self.max_iterations = max_iterations

    def synthesize_specification(
        self,
        c_code: str,
        program_id: str,
        temp_dir: Path
    ) -> CompleteResult:
        """
        Execute complete refinement (all components jointly).

        Args:
            c_code: Unannotated C program
            program_id: Identifier for logging
            temp_dir: Working directory

        Returns:
            CompleteResult with discharge history
        """
        discharge_history = []
        current_spec = None
        previous_rate = 0.0
        converged = False

        for iteration in range(self.max_iterations):
            # Generate all components simultaneously
            # Mock generation for PoC
            if iteration == 0:
                current_spec = self._generate_initial_spec(c_code)
            else:
                # Refinement iteration
                current_spec = self._refine_spec(c_code, current_spec)

            # Verify complete spec
            result = self._verify_complete(c_code, current_spec, temp_dir)
            discharge_history.append(result.proof_discharge_rate)

            # Check convergence: 2 consecutive iterations with same rate
            if iteration > 0 and result.proof_discharge_rate == previous_rate:
                converged = True
                break

            previous_rate = result.proof_discharge_rate

        return CompleteResult(
            final_spec=current_spec,
            total_iterations=len(discharge_history),
            discharge_history=discharge_history,
            converged=converged,
            convergence_reason="converged" if converged else "max_iterations"
        )

    def _generate_initial_spec(self, c_code: str) -> ACSLSpec:
        """Generate initial complete specification."""
        # Mock complete spec generation
        annotated_code = f"""
/*@ requires n >= 0;
  @ requires \\valid_read(arr + (0..n-1));
  @ ensures \\result >= -1 && \\result < n;
  @*/
{c_code}
"""
        return ACSLSpec(
            annotated_code=annotated_code,
            preconditions=["n >= 0", "\\valid_read(arr + (0..n-1))"],
            postconditions=["\\result >= -1 && \\result < n"],
            loop_invariants=["0 <= i <= n"],
            assertions=[]
        )

    def _refine_spec(self, c_code: str, current_spec: ACSLSpec) -> ACSLSpec:
        """Refine all components jointly."""
        # Mock refinement (would use feedback in actual implementation)
        return current_spec

    def _verify_complete(
        self,
        c_code: str,
        spec: ACSLSpec,
        temp_dir: Path
    ) -> VerificationResult:
        """Verify complete specification."""
        # Mock verification for PoC
        import random
        random.seed(hash(c_code + str(spec.preconditions)))
        discharge_rate = random.uniform(50.0, 70.0)

        return VerificationResult(
            total_obligations=10,
            proved_obligations=int(discharge_rate / 10),
            failed_obligations=10 - int(discharge_rate / 10),
            proof_discharge_rate=discharge_rate,
            obligations=[],
            raw_output="MOCK VERIFICATION"
        )
