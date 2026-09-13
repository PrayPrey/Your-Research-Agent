# Core Logic Document: H-M2 Staged Progressive Refinement

**Date:** 2026-07-11  
**Hypothesis:** Staged progressive refinement (types→pre→post→inv) converges faster than complete upfront specification  
**Phase:** Phase 3 - Logic Design  
**Budget:** 7 subtasks

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: API signatures verified from h-e1 actual code  
**Analyzed Path**: /workspace/TEST_verifai/docs/youra_research/h-e1/code/  
**Relevant Symbols**: SpecificationGenerator, FramaCVerifier, FeedbackExtractor, ACSLSpec, VerificationResult, StructuredFeedback

**Critical Finding**: All base APIs verified from actual implementation. Parameter names match exactly between spec and code.

---

## Knowledge Base Research (Archon)

**Applied**: Iterative refinement loop pattern, convergence detection

**Key Pattern**: Stage-based progressive synthesis with partial verification checkpoints. Reusing complete refinement strategy from h-e1 as baseline.

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

The following APIs are called from h-e1. Signatures verified from actual implementation:

```python
# From: h-e1/code/src/llm_client.py (ACTUAL CODE)
@dataclass
class ACSLSpec:
    annotated_code: str
    preconditions: List[str]
    postconditions: List[str]
    loop_invariants: List[str]
    assertions: List[str]

class SpecificationGenerator:
    def __init__(self, api_key: str, model: str = "claude-opus-4-5"):
        """Initialize with Anthropic API client."""
        ...
    
    def generate_initial_spec(
        self,
        c_code: str,
        verification_goal: str = "functional correctness"
    ) -> ACSLSpec:
        """Generate ACSL specification from unannotated C code."""
        ...

# From: h-e1/code/src/verifier.py (ACTUAL CODE)
@dataclass
class VerificationResult:
    total_obligations: int
    proved_obligations: int
    failed_obligations: int
    proof_discharge_rate: float
    obligations: List[ProofObligation]
    raw_output: str

class FramaCVerifier:
    def __init__(
        self,
        timeout_per_obligation: int = 10,
        provers: List[str] = None
    ):
        """Initialize verifier with timeout and provers."""
        ...
    
    def verify(self, acsl_spec: ACSLSpec, temp_dir: Path) -> VerificationResult:
        """Verify ACSL specification with Frama-C/WP."""
        ...

# From: h-e1/code/src/feedback_parser.py (ACTUAL CODE)
@dataclass
class StructuredFeedback:
    witness: WitnessInstantiation
    structure: LogicalStructure
    dependency: DependencyPreservation
    natural_language: str

class FeedbackExtractor:
    def extract_feedback(
        self,
        result: VerificationResult,
        acsl_spec: ACSLSpec
    ) -> Optional[StructuredFeedback]:
        """Extract 3-dimensional feedback from failed verifications."""
        ...
```

**Verified from**: h-e1/code/ (actual implementation, NOT spec)

---

## A-1: Staged Refinement Strategy [Complexity: 16, Budget: 7]

**Applied**: Sequential stage-based synthesis with partial verification

### API Signatures

```python
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

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
        # [N/A] - combines partial components into annotated_code string
        ...

@dataclass
class StageResult:
    """Single stage outcome."""
    spec_component: str  # Generated component for this stage
    iterations: int  # Iterations used in this stage
    discharge_rate: float  # Proof discharge after stage
    converged: bool  # Whether stage reached convergence

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
        """
        generator: SpecificationGenerator - From h-e1
        verifier: FramaCVerifier - From h-e1
        feedback_extractor: FeedbackExtractor - From h-e1
        max_iter_per_stage: int - Budget per stage (default: 3)
        """
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
        
        c_code: str - Unannotated C program
        program_id: str - Identifier for logging
        temp_dir: Path - Working directory
        
        Returns: StagedResult with stage history
        """
        # [N/A] - orchestrates 4 stages sequentially
        ...
    
    def refine_stage(
        self,
        c_code: str,
        spec_so_far: PartialSpec,
        stage: StageType,
        temp_dir: Path
    ) -> StageResult:
        """
        Refine single stage with iterative feedback.
        
        c_code: str - Original C code
        spec_so_far: PartialSpec - Specifications from previous stages
        stage: StageType - Current stage to refine
        temp_dir: Path - Working directory
        
        Returns: StageResult with component and metrics
        """
        # [N/A] - iterates up to max_iter_per_stage
        ...
    
    def _build_stage_prompt(
        self,
        c_code: str,
        spec_so_far: PartialSpec,
        stage: StageType
    ) -> str:
        """Build stage-specific generation prompt."""
        # [str] - returns prompt string
        ...
    
    def _verify_partial(
        self,
        c_code: str,
        partial_spec: PartialSpec,
        temp_dir: Path
    ) -> VerificationResult:
        """Verify partial specification (uses h-e1 verifier)."""
        # [VerificationResult] - calls verifier.verify()
        ...
```

### Pseudo-code (Algorithm Flow)

```
ALGORITHM: Staged Progressive Refinement

INPUT: c_code (unannotated C)
OUTPUT: StagedResult

1. spec = PartialSpec()  # Empty
2. stage_history = {}
3. backtracking_events = 0
4. total_iterations = 0
5. prev_discharge_rate = 0.0

6. FOR stage IN [TYPES, PRECONDITIONS, POSTCONDITIONS, INVARIANTS]:
7.     stage_result = refine_stage(c_code, spec, stage, temp_dir)
8.     
9.     # Detect backtracking
10.    IF stage_result.discharge_rate < prev_discharge_rate:
11.        backtracking_events += 1
12.    
13.    # Update partial spec
14.    UPDATE spec WITH stage_result.spec_component
15.    stage_history[stage] = stage_result
16.    total_iterations += stage_result.iterations
17.    prev_discharge_rate = stage_result.discharge_rate

18. final_spec = spec.to_acsl_spec(c_code)
19. RETURN StagedResult(final_spec, total_iterations, stage_history, backtracking_events, "completed")

---

SUBROUTINE: refine_stage(c_code, spec_so_far, stage, temp_dir)

1. current_component = ""
2. best_discharge_rate = 0.0
3. iteration = 0

4. WHILE iteration < max_iter_per_stage:
5.     prompt = _build_stage_prompt(c_code, spec_so_far, stage)
6.     new_component = LLM.generate(prompt)  # Temperature: 0.7
7.     
8.     # Build partial spec with new component
9.     test_spec = COPY(spec_so_far)
10.    SET test_spec[stage] = new_component
11.    
12.    # Verify partial
13.    result = _verify_partial(c_code, test_spec, temp_dir)
14.    
15.    IF result.discharge_rate >= best_discharge_rate:
16.        current_component = new_component
17.        best_discharge_rate = result.discharge_rate
18.    ELSE:
19.        # No improvement - try refinement if feedback available
20.        IF iteration < max_iter_per_stage - 1:
21.            feedback = feedback_extractor.extract_feedback(result, test_spec.to_acsl_spec())
22.            IF feedback:
23.                current_component = LLM.refine(current_component, feedback)  # Temperature: 0.5
24.    
25.    iteration += 1

26. RETURN StageResult(current_component, iteration, best_discharge_rate, converged=(iteration < max_iter_per_stage))
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Stage prompt templates | Create 4 stage-specific prompts |
| L-1-2 | Partial spec builder | Merge partial components |
| L-1-3 | Stage iteration loop | Per-stage refinement with feedback |
| L-1-4 | Backtracking detector | Track discharge rate decreases |
| L-1-5 | Stage orchestration | Sequential 4-stage pipeline |
| L-1-6 | Partial verification | Verify incomplete specs |
| L-1-7 | Result aggregation | Build StagedResult |

---

## A-2: Complete Refinement Strategy (Baseline Adapter) [Complexity: 10, Budget: 0 - INHERITED]

**Applied**: Reuse h-e1 refinement loop with adapter wrapper

**Note**: This component wraps h-e1's existing `IterativeRefinementLoop` class. No new logic required - just import and use directly.

### API Signatures

```python
from h_e1.src.refinement_loop import IterativeRefinementLoop, RefinementHistory

@dataclass
class CompleteResult:
    """Adapter for h-e1 RefinementHistory to match comparison interface."""
    final_spec: ACSLSpec
    total_iterations: int
    discharge_history: List[float]
    converged: bool
    convergence_reason: str
    
    @classmethod
    def from_refinement_history(cls, history: RefinementHistory) -> "CompleteResult":
        """Convert h-e1 RefinementHistory to CompleteResult."""
        # [N/A] - extracts discharge_history from iterations
        ...

class CompleteRefinementStrategy:
    """Wrapper for h-e1 complete refinement (baseline)."""
    
    def __init__(
        self,
        generator: SpecificationGenerator,
        verifier: FramaCVerifier,
        feedback_extractor: FeedbackExtractor,
        max_iterations: int = 10
    ):
        """Initialize by wrapping h-e1 IterativeRefinementLoop."""
        self.loop = IterativeRefinementLoop(
            generator, verifier, feedback_extractor,
            max_iterations=max_iterations,
            no_improvement_threshold=3
        )
    
    def synthesize_specification(
        self,
        c_code: str,
        program_id: str,
        temp_dir: Path
    ) -> CompleteResult:
        """Execute complete refinement (delegates to h-e1)."""
        history = self.loop.synthesize_specification(c_code, temp_dir)
        return CompleteResult.from_refinement_history(history)
```

**Subtasks**: None (reuses h-e1 implementation)

---

**End of Document**

**Total Budget Used**: 7/7 subtasks

**Critical Design Decisions**:
1. Staged strategy uses 3 iterations/stage (12 total) vs Complete's 10 iterations for fair comparison
2. Backtracking detected as discharge_rate[stage_N] < discharge_rate[stage_N-1]
3. Partial verification after each stage enables incremental feedback
4. Complete strategy directly wraps h-e1 to ensure identical baseline

**Ready for Phase 4**: All signatures copy-paste ready with verified h-e1 dependencies.

**File Paths**:
- Input specs: /workspace/TEST_verifai/docs/youra_research/h-m2/03_architecture.md
- Input PRD: /workspace/TEST_verifai/docs/youra_research/h-m2/03_prd.md
- Base code: /workspace/TEST_verifai/docs/youra_research/h-e1/code/
- Output: /workspace/TEST_verifai/docs/youra_research/h-m2/03_logic.md
