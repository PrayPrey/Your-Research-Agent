# Core Logic Document: H-M1 Information Gradient Validation

**Date:** 2026-07-11  
**Hypothesis:** Proof discharge rate scales monotonically with feedback richness  
**Phase:** Phase 3 - Logic Design  
**Budget:** 8 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** API signatures verified from base code (h-e1)  
**Analyzed Path:** `/workspace/TEST_verifai/docs/youra_research/h-e1/code/`  
**Relevant Symbols:** 
- `IterativeRefinementLoop.synthesize_specification(c_code, temp_dir)` - Verified
- `FeedbackExtractor.extract_feedback(result, acsl_spec)` - Verified
- `FramaCVerifier.verify(acsl_spec, temp_dir)` - Verified

**Critical Finding:** All base hypothesis APIs use exact parameter names from actual implementation. No spec-code divergence detected.

---

## Knowledge Base Research (Archon)

**Applied:** Standard statistical testing patterns (scipy.stats)

---

## Task Allocation Reference

From `03_architecture.md`:
- **M-1**: Feedback Ablator (Complexity: 9, Budget: 3 subtasks)
- **M-2**: Ablation Experiment (Complexity: 12, Budget: 2 subtasks)
- **M-3**: Statistical Analyzer (Complexity: 16, Budget: 3 subtasks)

Total Budget: 8 subtasks (simplified from 7 tasks to focus on core logic)

---

## M-1: Feedback Ablator [Complexity: 9, Budget: 3]

**Applied:** Dimension filtering pattern

### API Signatures

```python
from typing import Dict, Optional
from dataclasses import dataclass
from h_e1.src.feedback_parser import StructuredFeedback

class FeedbackCondition:
    """Ablation condition constants."""
    FULL_STRUCTURED = "FullStructured"
    OBLIGATION_SLICE = "ObligationSlice"
    TAG_ONLY = "TagOnly"
    RAW_ERROR = "RawError"

class FeedbackAblator:
    """Filter feedback dimensions based on ablation condition."""
    
    def __init__(self, condition: str):
        """
        Args:
            condition: One of FeedbackCondition values
        """
        self.condition = condition
    
    def ablate_feedback(self, full_feedback: StructuredFeedback) -> StructuredFeedback:
        """
        Filter feedback dimensions based on condition.
        
        Args:
            full_feedback: Complete 3D feedback from base h-e1 code
        
        Returns:
            Filtered feedback matching ablation condition
        """
        if self.condition == FeedbackCondition.RAW_ERROR:
            return self._create_raw_feedback(full_feedback)
        elif self.condition == FeedbackCondition.TAG_ONLY:
            return self._create_tag_only(full_feedback)
        elif self.condition == FeedbackCondition.OBLIGATION_SLICE:
            return self._create_obligation_slice(full_feedback)
        else:  # FULL_STRUCTURED
            return full_feedback
    
    def _create_raw_feedback(self, feedback: StructuredFeedback) -> StructuredFeedback:
        """Baseline: Only raw verifier output, no structured parsing."""
        # Return feedback with only raw text, zero out structured dimensions
        pass
    
    def _create_tag_only(self, feedback: StructuredFeedback) -> StructuredFeedback:
        """Dimension 2 only: Structure (obligation types)."""
        # Keep structure.failure_summary, zero out witness + dependency
        pass
    
    def _create_obligation_slice(self, feedback: StructuredFeedback) -> StructuredFeedback:
        """Dimensions 2+3: Structure + Dependency."""
        # Keep structure + dependency, zero out witness
        pass
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Condition router | Dispatch to correct filter |
| L-1-2 | Dimension masking | Zero out excluded dimensions |
| L-1-3 | NL formatter | Rebuild natural_language text |

---

## M-2: Ablation Experiment [Complexity: 12, Budget: 2]

**Applied:** Iterative experiment orchestration pattern

### API Signatures

```python
from pathlib import Path
from typing import List
from dataclasses import dataclass
from h_e1.src.refinement_loop import IterativeRefinementLoop, RefinementHistory

@dataclass
class TrialResult:
    """Single program × condition trial."""
    program_id: str
    condition: str
    discharge_rate: float
    iterations: int
    convergence_reason: str
    api_calls: int
    verifier_time_ms: float

@dataclass
class ConditionResults:
    """Aggregated results per condition."""
    condition: str
    trials: List[TrialResult]
    mean_rate: float
    std_rate: float
    mean_iterations: float
    total_compute: Dict[str, float]

@dataclass
class AblationResults:
    """Complete ablation study results."""
    results_by_condition: Dict[str, ConditionResults]
    raw_trials: List[TrialResult]

class AblationExperiment:
    """Run controlled ablation across 4 conditions."""
    
    def __init__(
        self,
        base_refinement_loop: IterativeRefinementLoop,
        output_dir: Path
    ):
        """
        Args:
            base_refinement_loop: H-E1 refinement loop (reused)
            output_dir: Directory for trial checkpoints
        """
        self.base_loop = base_refinement_loop
        self.output_dir = output_dir
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
        
        for program in programs:
            for condition in self.conditions:
                trial = self._run_single_trial(program, condition, temp_dir)
                raw_trials.append(trial)
                self._checkpoint_trial(trial)  # Save immediately
        
        # Aggregate by condition
        results_by_condition = {}
        for condition in self.conditions:
            condition_trials = [t for t in raw_trials if t.condition == condition]
            results_by_condition[condition] = self._aggregate_condition(condition, condition_trials)
        
        return AblationResults(
            results_by_condition=results_by_condition,
            raw_trials=raw_trials
        )
    
    def _run_single_trial(
        self,
        program: Dict,
        condition: str,
        temp_dir: Path
    ) -> TrialResult:
        """
        Run refinement loop with ablated feedback.
        
        Pseudo-code:
        1. Create FeedbackAblator for condition
        2. Wrap base loop's feedback extraction with ablation filter
        3. Run loop (reuse h-e1 synthesize_specification)
        4. Extract metrics from RefinementHistory
        """
        pass
    
    def _aggregate_condition(self, condition: str, trials: List[TrialResult]) -> ConditionResults:
        """Compute mean/std statistics per condition."""
        import numpy as np
        rates = [t.discharge_rate for t in trials]
        iterations = [t.iterations for t in trials]
        
        return ConditionResults(
            condition=condition,
            trials=trials,
            mean_rate=np.mean(rates),
            std_rate=np.std(rates),
            mean_iterations=np.mean(iterations),
            total_compute={
                "api_calls": sum(t.api_calls for t in trials),
                "verifier_time_ms": sum(t.verifier_time_ms for t in trials)
            }
        )
    
    def _checkpoint_trial(self, trial: TrialResult):
        """Save trial to JSON for crash recovery."""
        import json
        checkpoint_file = self.output_dir / f"{trial.program_id}_{trial.condition}.json"
        with checkpoint_file.open('w') as f:
            json.dump(trial.__dict__, f, indent=2)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Trial execution wrapper | Integrate ablator with base loop |
| L-2-2 | Condition aggregation | Compute per-condition statistics |

---

## M-3: Statistical Analyzer [Complexity: 16, Budget: 3]

**Applied:** Standard hypothesis testing (scipy.stats)

### API Signatures

```python
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class MonotonicTest:
    """Test if conditions are monotonically ordered."""
    passed: bool
    ordering: List[str]  # Actual ordering by mean
    expected: List[str]  # Expected: [Raw, Tag, Obl, Full]
    violations: List[str]  # Where ordering fails

@dataclass
class GapTest:
    """Test if adjacent gaps ≥ threshold."""
    passed: bool
    gaps: Dict[str, float]  # Adjacent pairs -> gap in pp
    threshold: float
    failed_gaps: List[str]  # Which gaps < threshold

@dataclass
class RegressionResult:
    """Linear regression: feedback richness -> discharge rate."""
    coefficient: float  # β (slope)
    p_value: float
    r_squared: float
    significant: bool  # p < 0.05

@dataclass
class GateDecision:
    """Final hypothesis validation decision."""
    status: str  # SATISFIED | FAILED
    passing_tests: List[str]
    failing_tests: List[str]
    reason: str

class StatisticalAnalyzer:
    """Hypothesis testing for information gradient."""
    
    def __init__(self, significance_level: float = 0.05):
        self.alpha = significance_level
    
    def test_monotonic_ordering(
        self,
        condition_means: Dict[str, float]
    ) -> MonotonicTest:
        """
        Check: FullStructured > ObligationSlice > TagOnly > RawError.
        
        Args:
            condition_means: {condition -> mean discharge rate}
        
        Returns:
            MonotonicTest result
        """
        expected = [
            FeedbackCondition.RAW_ERROR,
            FeedbackCondition.TAG_ONLY,
            FeedbackCondition.OBLIGATION_SLICE,
            FeedbackCondition.FULL_STRUCTURED
        ]
        
        # Sort by mean rate (ascending)
        actual = sorted(condition_means.keys(), key=lambda c: condition_means[c])
        
        passed = (actual == expected)
        violations = [f"{actual[i]} vs {expected[i]}" 
                     for i in range(len(expected)) if actual[i] != expected[i]]
        
        return MonotonicTest(
            passed=passed,
            ordering=actual,
            expected=expected,
            violations=violations
        )
    
    def test_adjacent_gaps(
        self,
        condition_means: Dict[str, float],
        threshold: float = 10.0
    ) -> GapTest:
        """
        Check: Each adjacent gap ≥ 10 percentage points.
        
        Args:
            condition_means: {condition -> mean discharge rate}
            threshold: Minimum gap in pp (default: 10.0)
        
        Returns:
            GapTest result
        """
        # Compute adjacent gaps in expected order
        expected_order = [
            FeedbackCondition.RAW_ERROR,
            FeedbackCondition.TAG_ONLY,
            FeedbackCondition.OBLIGATION_SLICE,
            FeedbackCondition.FULL_STRUCTURED
        ]
        
        gaps = {}
        failed_gaps = []
        
        for i in range(len(expected_order) - 1):
            lower = expected_order[i]
            upper = expected_order[i + 1]
            gap = condition_means[upper] - condition_means[lower]
            gap_name = f"{upper} - {lower}"
            gaps[gap_name] = gap
            
            if gap < threshold:
                failed_gaps.append(gap_name)
        
        return GapTest(
            passed=(len(failed_gaps) == 0),
            gaps=gaps,
            threshold=threshold,
            failed_gaps=failed_gaps
        )
    
    def run_regression(
        self,
        ablation_results: AblationResults
    ) -> RegressionResult:
        """
        Linear regression: ordinal feedback -> discharge rate.
        
        Encoding:
            RawError -> 1
            TagOnly -> 2
            ObligationSlice -> 3
            FullStructured -> 4
        
        Test: β > 0, p < 0.05
        
        Args:
            ablation_results: All trial results
        
        Returns:
            RegressionResult with coefficient and significance
        """
        import numpy as np
        from scipy.stats import linregress
        
        # Encode conditions as ordinal values
        encoding = {
            FeedbackCondition.RAW_ERROR: 1,
            FeedbackCondition.TAG_ONLY: 2,
            FeedbackCondition.OBLIGATION_SLICE: 3,
            FeedbackCondition.FULL_STRUCTURED: 4
        }
        
        x = []  # Feedback richness (ordinal)
        y = []  # Discharge rate (%)
        
        for trial in ablation_results.raw_trials:
            x.append(encoding[trial.condition])
            y.append(trial.discharge_rate)
        
        # Linear regression
        slope, intercept, r_value, p_value, std_err = linregress(x, y)
        
        return RegressionResult(
            coefficient=slope,
            p_value=p_value,
            r_squared=r_value ** 2,
            significant=(p_value < self.alpha and slope > 0)
        )
    
    def make_gate_decision(
        self,
        monotonic: MonotonicTest,
        gaps: GapTest,
        regression: RegressionResult
    ) -> GateDecision:
        """
        Combine all tests for final gate decision.
        
        SATISFIED: All 3 tests pass
        FAILED: Any test fails
        
        Args:
            monotonic: Ordering test result
            gaps: Gap test result
            regression: Regression test result
        
        Returns:
            GateDecision with status and reason
        """
        passing = []
        failing = []
        
        if monotonic.passed:
            passing.append("monotonic_ordering")
        else:
            failing.append("monotonic_ordering")
        
        if gaps.passed:
            passing.append("adjacent_gaps")
        else:
            failing.append("adjacent_gaps")
        
        if regression.significant:
            passing.append("regression_significance")
        else:
            failing.append("regression_significance")
        
        if len(failing) == 0:
            status = "SATISFIED"
            reason = "All 3 hypothesis tests passed: information gradient confirmed"
        else:
            status = "FAILED"
            reason = f"Failed tests: {', '.join(failing)}"
        
        return GateDecision(
            status=status,
            passing_tests=passing,
            failing_tests=failing,
            reason=reason
        )
```

### Pseudo-code (Statistical Pipeline)

```
ALGORITHM: Information Gradient Hypothesis Testing

INPUT: ablation_results (all program × condition trials)
OUTPUT: gate_decision (SATISFIED | FAILED)

1. Extract condition means:
   condition_means = {
       c: mean([t.discharge_rate for t in trials if t.condition == c])
       for c in [Raw, Tag, Obl, Full]
   }

2. Test 1: Monotonic Ordering
   expected_order = [Raw, Tag, Obl, Full]
   actual_order = sort(conditions, key=mean_rate)
   monotonic_passed = (actual_order == expected_order)

3. Test 2: Adjacent Gaps
   gaps = [
       Full - Obl,
       Obl - Tag,
       Tag - Raw
   ]
   gaps_passed = all(gap >= 10.0 for gap in gaps)

4. Test 3: Regression
   X = encode_ordinal([Raw=1, Tag=2, Obl=3, Full=4])
   Y = discharge_rates
   β, p = linear_regression(X, Y)
   regression_passed = (β > 0 AND p < 0.05)

5. Gate Decision:
   IF monotonic_passed AND gaps_passed AND regression_passed:
       RETURN "SATISFIED"
   ELSE:
       RETURN "FAILED"
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Monotonic test | Check ordering by mean |
| L-3-2 | Gap test | Compute adjacent differences |
| L-3-3 | Regression test | Linear regression + significance |

---

## External Dependencies API (Base Hypothesis)

**CRITICAL:** The following APIs are called from h-e1. Signatures verified from actual code.

### From h-e1/code/src/refinement_loop.py (ACTUAL CODE)

```python
class IterativeRefinementLoop:
    def __init__(
        self,
        generator: SpecificationGenerator,
        verifier: FramaCVerifier,
        feedback_extractor: FeedbackExtractor,
        max_iterations: int = 10,
        no_improvement_threshold: int = 3
    ):
        pass
    
    def synthesize_specification(
        self,
        c_code: str,
        temp_dir: Path
    ) -> RefinementHistory:
        """
        Complete synthesis pipeline.
        
        Args:
            c_code: Unannotated C program
            temp_dir: Working directory
        
        Returns:
            RefinementHistory with iterations
        """
        pass
```

### From h-e1/code/src/feedback_parser.py (ACTUAL CODE)

```python
@dataclass
class StructuredFeedback:
    """Complete 3-dimensional feedback."""
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
        """
        Extract structured feedback from failed verifications.
        
        Args:
            result: WP output
            acsl_spec: Current specification
        
        Returns:
            StructuredFeedback or None if all proved
        """
        pass
```

### From h-e1/code/src/verifier.py (ACTUAL CODE)

```python
class FramaCVerifier:
    def verify(
        self,
        acsl_spec: ACSLSpec,
        temp_dir: Path
    ) -> VerificationResult:
        """
        Verify ACSL specification with Frama-C/WP.
        
        Args:
            acsl_spec: ACSL-annotated C code
            temp_dir: Directory for temporary files
        
        Returns:
            VerificationResult with proof obligations
        """
        pass
```

**Verified from:** `/workspace/TEST_verifai/docs/youra_research/h-e1/code/`

**Critical Notes:**
- Parameter names match actual implementation (no spec divergence)
- h-m1 wraps h-e1's `synthesize_specification` with `FeedbackAblator`
- Ablation modifies feedback between iterations, not loop structure

---

## Integration Pattern (Critical Design)

### How h-m1 Uses h-e1 Code

```python
# h-m1/src/ablation_experiment.py

from h_e1.src.refinement_loop import IterativeRefinementLoop
from h_e1.src.feedback_parser import FeedbackExtractor

class AblatedFeedbackExtractor(FeedbackExtractor):
    """Wrapper that applies ablation to h-e1's feedback."""
    
    def __init__(self, base_extractor: FeedbackExtractor, ablator: FeedbackAblator):
        self.base_extractor = base_extractor
        self.ablator = ablator
    
    def extract_feedback(self, result, acsl_spec):
        # Get full feedback from h-e1
        full_feedback = self.base_extractor.extract_feedback(result, acsl_spec)
        
        if full_feedback is None:
            return None
        
        # Apply ablation filter
        return self.ablator.ablate_feedback(full_feedback)

# Usage in AblationExperiment._run_single_trial:
def _run_single_trial(self, program, condition, temp_dir):
    # Create ablated extractor
    ablator = FeedbackAblator(condition)
    ablated_extractor = AblatedFeedbackExtractor(
        self.base_loop.feedback_extractor,
        ablator
    )
    
    # Create modified loop
    trial_loop = IterativeRefinementLoop(
        generator=self.base_loop.generator,
        verifier=self.base_loop.verifier,
        feedback_extractor=ablated_extractor,  # Wrap with ablation
        max_iterations=self.base_loop.max_iterations,
        no_improvement_threshold=self.base_loop.no_improvement_threshold
    )
    
    # Run loop (identical to h-e1, but with ablated feedback)
    history = trial_loop.synthesize_specification(program['code'], temp_dir)
    
    return TrialResult(
        program_id=program['id'],
        condition=condition,
        discharge_rate=history.iterations[-1].proof_discharge_rate,
        iterations=history.total_iterations,
        convergence_reason=history.convergence_reason.value,
        api_calls=history.total_iterations,
        verifier_time_ms=0.0  # Track from history
    )
```

**Key Design Principle:** 
- h-e1 provides the refinement engine
- h-m1 controls what feedback the engine sees
- Same loop logic, different feedback richness

---

## Summary

This logic document provides copy-paste ready APIs for Phase 4 implementation.

**Delivered Components:**
1. FeedbackAblator: 4-condition feedback filtering
2. AblationExperiment: Program × condition trial orchestration
3. StatisticalAnalyzer: 3 hypothesis tests + gate decision

**Critical Verification:**
- Base h-e1 APIs verified from actual code (no spec-code divergence)
- All parameter names match implementation
- Integration pattern preserves h-e1 logic while controlling feedback

**Ready for Phase 4:** All signatures include type hints and are copy-paste ready.

**Total Budget:** 8 subtasks (3 + 2 + 3) ✓
