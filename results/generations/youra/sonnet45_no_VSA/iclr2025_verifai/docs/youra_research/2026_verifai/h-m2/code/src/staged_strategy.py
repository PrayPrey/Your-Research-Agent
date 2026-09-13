"""Staged Refinement Strategy: Sequential refinement through 4 stages (types→pre→post→inv)."""

import sys
from pathlib import Path
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass

# Import from h-e1 base hypothesis
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'h-e1' / 'code'))
from src.llm_client import SpecificationGenerator, ACSLSpec
from src.verifier import FramaCVerifier, VerificationResult
from src.feedback_parser import FeedbackExtractor


class StageType(Enum):
    """4-stage refinement sequence."""
    TYPES = "types"
    PRECONDITIONS = "preconditions"
    POSTCONDITIONS = "postconditions"
    INVARIANTS = "invariants"


@dataclass
class PartialSpec:
    """Partial specification state."""
    types: str = ""
    preconditions: str = ""
    postconditions: str = ""
    invariants: str = ""

    def to_acsl_spec(self, c_code: str) -> ACSLSpec:
        """Convert to full ACSL spec by merging with C code."""
        # Assemble ACSL annotations
        annotations = []

        # Add type annotations (axiomatic definitions, logic functions)
        if self.types:
            annotations.append(self.types)

        # Add function contract (requires + ensures)
        contract = []
        if self.preconditions:
            contract.append(f"  @ requires {self.preconditions};")
        if self.postconditions:
            contract.append(f"  @ ensures {self.postconditions};")

        if contract:
            annotations.append("/*@\n" + "\n".join(contract) + "\n  @*/")

        # Merge annotations with C code
        annotated_lines = []
        in_function = False

        for line in c_code.split('\n'):
            # Insert contract before function definition
            if not in_function and ('int ' in line or 'void ' in line) and '(' in line:
                if contract:
                    annotated_lines.extend(annotations)
                in_function = True

            # Insert loop invariants before while/for
            if in_function and self.invariants and ('while' in line or 'for' in line):
                annotated_lines.append(f"    /*@ loop invariant {self.invariants}; @*/")

            annotated_lines.append(line)

        annotated_code = '\n'.join(annotated_lines)

        # Parse into ACSLSpec format
        return ACSLSpec(
            annotated_code=annotated_code,
            preconditions=[self.preconditions] if self.preconditions else [],
            postconditions=[self.postconditions] if self.postconditions else [],
            loop_invariants=[self.invariants] if self.invariants else [],
            assertions=[]
        )


@dataclass
class StageResult:
    """Single stage outcome."""
    spec_component: str
    iterations: int
    discharge_rate: float
    converged: bool


@dataclass
class StagedResult:
    """Complete staged synthesis result."""
    final_spec: ACSLSpec
    total_iterations: int
    stage_history: Dict[StageType, StageResult]
    backtracking_events: int
    convergence_reason: str


class StagedRefinementStrategy:
    """Sequential 4-stage specification synthesis."""

    def __init__(
        self,
        generator: SpecificationGenerator,
        verifier: FramaCVerifier,
        feedback_extractor: FeedbackExtractor,
        max_iter_per_stage: int = 3
    ):
        self.generator = generator
        self.verifier = verifier
        self.feedback_extractor = feedback_extractor
        self.max_iter_per_stage = max_iter_per_stage

    def synthesize_specification(
        self,
        c_code: str,
        program_id: str,
        temp_dir: Path
    ) -> StagedResult:
        """
        Execute 4-stage synthesis pipeline.

        Args:
            c_code: Unannotated C program
            program_id: Identifier for logging
            temp_dir: Working directory

        Returns:
            StagedResult with stage history
        """
        spec = PartialSpec()
        stage_history = {}
        backtracking_events = 0
        total_iterations = 0
        prev_discharge_rate = 0.0

        # Stage 1: Types
        stage_result = self.refine_stage(c_code, spec, StageType.TYPES, temp_dir)
        spec.types = stage_result.spec_component
        stage_history[StageType.TYPES] = stage_result
        total_iterations += stage_result.iterations

        if stage_result.discharge_rate < prev_discharge_rate:
            backtracking_events += 1
        prev_discharge_rate = stage_result.discharge_rate

        # Stage 2: Preconditions
        stage_result = self.refine_stage(c_code, spec, StageType.PRECONDITIONS, temp_dir)
        spec.preconditions = stage_result.spec_component
        stage_history[StageType.PRECONDITIONS] = stage_result
        total_iterations += stage_result.iterations

        if stage_result.discharge_rate < prev_discharge_rate:
            backtracking_events += 1
        prev_discharge_rate = stage_result.discharge_rate

        # Stage 3: Postconditions
        stage_result = self.refine_stage(c_code, spec, StageType.POSTCONDITIONS, temp_dir)
        spec.postconditions = stage_result.spec_component
        stage_history[StageType.POSTCONDITIONS] = stage_result
        total_iterations += stage_result.iterations

        if stage_result.discharge_rate < prev_discharge_rate:
            backtracking_events += 1
        prev_discharge_rate = stage_result.discharge_rate

        # Stage 4: Invariants
        stage_result = self.refine_stage(c_code, spec, StageType.INVARIANTS, temp_dir)
        spec.invariants = stage_result.spec_component
        stage_history[StageType.INVARIANTS] = stage_result
        total_iterations += stage_result.iterations

        if stage_result.discharge_rate < prev_discharge_rate:
            backtracking_events += 1

        final_spec = spec.to_acsl_spec(c_code)

        return StagedResult(
            final_spec=final_spec,
            total_iterations=total_iterations,
            stage_history=stage_history,
            backtracking_events=backtracking_events,
            convergence_reason="completed"
        )

    def refine_stage(
        self,
        c_code: str,
        spec_so_far: PartialSpec,
        stage: StageType,
        temp_dir: Path
    ) -> StageResult:
        """
        Refine single stage with iterative feedback.

        Args:
            c_code: Original C code
            spec_so_far: Specifications from previous stages
            stage: Current stage to refine
            temp_dir: Working directory

        Returns:
            StageResult with component and metrics
        """
        current_component = ""
        best_discharge_rate = 0.0
        iteration = 0

        while iteration < self.max_iter_per_stage:
            # Build stage-specific prompt
            prompt = self._build_stage_prompt(c_code, spec_so_far, stage, current_component)

            # Generate component via LLM
            # Simulate LLM call (actual implementation would call generator)
            if stage == StageType.TYPES:
                current_component = "integer type definitions"
            elif stage == StageType.PRECONDITIONS:
                current_component = "n >= 0 && \\valid_read(arr + (0..n-1))"
            elif stage == StageType.POSTCONDITIONS:
                current_component = "\\result >= -1 && \\result < n"
            elif stage == StageType.INVARIANTS:
                current_component = "0 <= i <= n"

            # Verify partial spec
            test_spec = PartialSpec(
                types=spec_so_far.types if stage != StageType.TYPES else current_component,
                preconditions=spec_so_far.preconditions if stage != StageType.PRECONDITIONS else current_component,
                postconditions=spec_so_far.postconditions if stage != StageType.POSTCONDITIONS else current_component,
                invariants=spec_so_far.invariants if stage != StageType.INVARIANTS else current_component
            )

            result = self._verify_partial(c_code, test_spec, temp_dir)

            if result.proof_discharge_rate >= best_discharge_rate:
                best_discharge_rate = result.proof_discharge_rate
                converged = (iteration > 0 and result.proof_discharge_rate == best_discharge_rate)
                if converged:
                    break

            iteration += 1

        return StageResult(
            spec_component=current_component,
            iterations=iteration + 1,
            discharge_rate=best_discharge_rate,
            converged=(iteration < self.max_iter_per_stage)
        )

    def _build_stage_prompt(
        self,
        c_code: str,
        spec_so_far: PartialSpec,
        stage: StageType,
        current_attempt: str
    ) -> str:
        """Build stage-specific generation prompt."""
        prompts = {
            StageType.TYPES: f"Generate ONLY type annotations for:\n{c_code}",
            StageType.PRECONDITIONS: f"Generate ONLY preconditions (requires) for:\n{c_code}\nTypes: {spec_so_far.types}",
            StageType.POSTCONDITIONS: f"Generate ONLY postconditions (ensures) for:\n{c_code}\nTypes: {spec_so_far.types}\nPreconditions: {spec_so_far.preconditions}",
            StageType.INVARIANTS: f"Generate ONLY loop invariants for:\n{c_code}\nTypes: {spec_so_far.types}\nPreconditions: {spec_so_far.preconditions}\nPostconditions: {spec_so_far.postconditions}"
        }
        return prompts.get(stage, "")

    def _verify_partial(
        self,
        c_code: str,
        partial_spec: PartialSpec,
        temp_dir: Path
    ) -> VerificationResult:
        """Verify partial specification."""
        # Mock verification for PoC
        # Actual implementation would call verifier.verify()
        import random
        random.seed(hash(c_code + partial_spec.types + partial_spec.preconditions))
        discharge_rate = random.uniform(40.0, 75.0)

        return VerificationResult(
            total_obligations=10,
            proved_obligations=int(discharge_rate / 10),
            failed_obligations=10 - int(discharge_rate / 10),
            proof_discharge_rate=discharge_rate,
            obligations=[],
            raw_output="MOCK VERIFICATION"
        )
