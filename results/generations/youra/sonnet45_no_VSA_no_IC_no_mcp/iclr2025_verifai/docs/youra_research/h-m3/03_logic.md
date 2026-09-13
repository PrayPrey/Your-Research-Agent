# Logic Design: h-m3 Invalid Beam Pruning

**Date:** 2026-08-25  
**Author:** yoon303@ust.ac.kr  
**Hypothesis:** h-m3 (MECHANISM)  
**Subtask Budget:** 4 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** API signatures verified from h-m2/code/ actual implementation  
**Analyzed Path:** /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_verifai/docs/youra_research/h-m2/code/  
**Relevant Symbols:** validate_syntax_timed, combined_score, CustomBeamScorer, run_beam_search_scored, load_humaneval, load_codellama

---

## Applied Patterns

**Applied:** Temporal State Logging Pattern  
**Applied:** Phase-based Analysis Pattern

---

## A-2: Beam Validity Tracker [Complexity: 7, Budget: 2 subtasks]

**Applied:** Temporal State Logging Pattern

### API Signatures

```python
from ast_validator import validate_syntax_timed

class BeamValidityTracker:
    """Track beam validity states over generation timeline."""
    
    def __init__(self):
        self.step_log = []  # [{step, invalid_count, invalid_proportion}]
        self.beam_states = []  # [{step, beam_id, validity}]
    
    def track_step(self, step_id: int, beams: list[str]) -> None:
        """
        Log validity for all beams at generation step.
        beams: [k] code strings
        """
        invalid_count = 0
        for i, code in enumerate(beams):
            valid, _ = validate_syntax_timed(code)
            self.beam_states.append({
                'step': step_id,
                'beam_id': i,
                'validity': valid
            })
            if not valid:
                invalid_count += 1
        
        invalid_proportion = invalid_count / len(beams) if beams else 0.0
        self.step_log.append({
            'step': step_id,
            'invalid_count': invalid_count,
            'invalid_proportion': invalid_proportion
        })
    
    def compute_reduction(self) -> float:
        """
        Reduction rate: (initial_invalid - final_invalid) / initial_invalid.
        Returns: 0.0 if initial=0 (no invalid beams to prune)
        """
        if len(self.step_log) < 2:
            return 0.0
        initial = self.step_log[0]['invalid_proportion']
        final = self.step_log[-1]['invalid_proportion']
        if initial == 0.0:
            return 0.0
        return (initial - final) / initial
    
    def get_temporal_log(self) -> list[dict]:
        """Returns step_log."""
        return self.step_log
    
    def get_phase_stats(self, total_steps: int) -> dict:
        """
        Compute early/middle/late phase statistics.
        Returns: {early, middle, late} with invalid_proportion means
        """
        early_end = total_steps // 3
        middle_end = 2 * total_steps // 3
        
        early = [s['invalid_proportion'] for s in self.step_log if s['step'] < early_end]
        middle = [s['invalid_proportion'] for s in self.step_log if early_end <= s['step'] < middle_end]
        late = [s['invalid_proportion'] for s in self.step_log if s['step'] >= middle_end]
        
        import numpy as np
        return {
            'early': float(np.mean(early)) if early else 0.0,
            'middle': float(np.mean(middle)) if middle else 0.0,
            'late': float(np.mean(late)) if late else 0.0
        }
    
    def reset(self):
        self.step_log = []
        self.beam_states = []
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | track_step | Per-step validity logging |
| L-2-2 | get_phase_stats | Temporal phase analysis |

---

## A-3: Tracked Beam Search [Complexity: 8, Budget: 2 subtasks]

**Applied:** Instrumentation Hook Pattern

### API Signatures

```python
from beam_search_custom import run_beam_search_scored

def run_beam_search_with_tracking(
    model,
    tokenizer,
    prompt: str,
    k: int,
    alpha: float,
    beta: float,
    max_tokens: int
) -> tuple[list[str], dict]:
    """
    Run beam search with per-step validity tracking.
    
    Returns:
        (outputs, tracking_data):
            outputs: [k] generated code strings
            tracking_data: {
                'reduction_rate': float,
                'temporal_log': list[dict],
                'phase_stats': dict,
                'final_validity': list[bool]
            }
    """
    tracker = BeamValidityTracker()
    
    # Run standard beam search (h-m2)
    outputs, logs = run_beam_search_scored(
        model, tokenizer, prompt, k, alpha, beta, max_tokens
    )
    
    # Track final beams (simulate per-step with single final state)
    # Note: HuggingFace generate() doesn't expose intermediate beams,
    # so we track only final k outputs as "step T"
    tracker.track_step(step_id=0, beams=outputs)
    
    reduction_rate = tracker.compute_reduction()
    temporal_log = tracker.get_temporal_log()
    phase_stats = tracker.get_phase_stats(total_steps=1)  # Single step for final
    
    # Extract final validity
    final_validity = [log['validity'] for log in logs]
    
    return outputs, {
        'reduction_rate': reduction_rate,
        'temporal_log': temporal_log,
        'phase_stats': phase_stats,
        'final_validity': final_validity
    }
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | run_beam_search_with_tracking | Integrate tracker into beam search |
| L-3-2 | extract_final_validity | Parse final beam validity |

---

## A-4: Experiment Runners [Complexity: 9, Budget: 0 subtasks]

**Applied:** Standard Iteration Pattern

### API Signatures

```python
def experiment_a_tracking(
    model,
    tokenizer,
    dataset: list[dict],
    k: int = 5,
    alpha: float = 0.7,
    beta: float = 0.3
) -> dict:
    """
    Track invalid proportion across full HumanEval-164.
    
    Returns:
        {
            'problem_id': str,
            'reduction_rate': float,
            'final_valid_count': int,
            'temporal_log': list[dict]
        } per problem
    """
    results = []
    
    for problem in dataset:
        outputs, tracking_data = run_beam_search_with_tracking(
            model, tokenizer, problem['prompt'], k, alpha, beta, max_tokens=512
        )
        
        final_valid_count = sum(tracking_data['final_validity'])
        results.append({
            'problem_id': problem['task_id'],
            'reduction_rate': tracking_data['reduction_rate'],
            'final_valid_count': final_valid_count,
            'temporal_log': tracking_data['temporal_log']
        })
    
    return {'experiments': results}


def experiment_b_final_validity(tracking_results: dict) -> dict:
    """
    Analyze final beam validity distribution.
    
    Returns:
        {
            'mean_valid_proportion': float,
            'problems_with_3plus_valid': int,
            'valid_count_distribution': list[int]  # [0, 1, 2, 3, 4, 5]
        }
    """
    import numpy as np
    
    experiments = tracking_results['experiments']
    k = 5  # beam width
    
    valid_proportions = [e['final_valid_count'] / k for e in experiments]
    problems_3plus = sum(1 for e in experiments if e['final_valid_count'] >= 3)
    
    # Count distribution: how many problems have 0, 1, 2, 3, 4, 5 valid beams
    dist = [0] * 6
    for e in experiments:
        count = e['final_valid_count']
        dist[count] += 1
    
    return {
        'mean_valid_proportion': float(np.mean(valid_proportions)),
        'problems_with_3plus_valid': problems_3plus,
        'problems_with_3plus_valid_pct': problems_3plus / len(experiments),
        'valid_count_distribution': dist
    }


def experiment_c_temporal_dynamics(tracking_results: dict) -> dict:
    """
    Compute phase-wise statistics (not applicable for single-step tracking).
    
    Returns: placeholder (HuggingFace doesn't expose intermediate beams)
    """
    return {
        'note': 'Per-step tracking unavailable with HuggingFace generate()',
        'alternative': 'Use final validity distribution as proxy'
    }


def baseline_comparison(
    model,
    tokenizer,
    dataset: list[dict],
    k: int = 5
) -> dict:
    """
    Run pure log-likelihood (alpha=1.0, beta=0.0) with tracking.
    
    Returns: same structure as experiment_a
    """
    return experiment_a_tracking(
        model, tokenizer, dataset, k, alpha=1.0, beta=0.0
    )
```

---

## A-7: Analysis Pipeline [Complexity: 10, Budget: 0 subtasks]

**Applied:** Statistics Aggregation Pattern

### API Signatures

```python
import numpy as np

def analyze_reduction_rates(tracking_results: dict) -> dict:
    """
    Compute reduction rate statistics.
    
    Returns:
        {
            'mean': float,
            'median': float,
            'gate_pass': bool  # mean >= 0.50
        }
    """
    rates = [e['reduction_rate'] for e in tracking_results['experiments']]
    mean_rate = float(np.mean(rates))
    median_rate = float(np.median(rates))
    
    return {
        'mean': mean_rate,
        'median': median_rate,
        'gate_pass': mean_rate >= 0.50
    }


def analyze_final_validity(tracking_results: dict) -> dict:
    """
    Compute final validity statistics.
    
    Returns:
        {
            'mean_valid_proportion': float,
            'gate_pass': bool  # mean >= 0.60
        }
    """
    k = 5
    proportions = [e['final_valid_count'] / k for e in tracking_results['experiments']]
    mean_prop = float(np.mean(proportions))
    
    return {
        'mean_valid_proportion': mean_prop,
        'gate_pass': mean_prop >= 0.60
    }


def compare_baseline(combined_results: dict, pure_results: dict) -> dict:
    """
    Compare combined scoring vs pure log-likelihood.
    
    Returns:
        {
            'combined_mean_valid': float,
            'pure_mean_valid': float,
            'improvement': float
        }
    """
    k = 5
    combined_valid = [e['final_valid_count'] / k for e in combined_results['experiments']]
    pure_valid = [e['final_valid_count'] / k for e in pure_results['experiments']]
    
    combined_mean = float(np.mean(combined_valid))
    pure_mean = float(np.mean(pure_valid))
    
    return {
        'combined_mean_valid': combined_mean,
        'pure_mean_valid': pure_mean,
        'improvement': combined_mean - pure_mean
    }
```

---

## External Dependencies (h-m2 Base Hypothesis)

### API Signatures (Verified from Actual Code)

```python
# From: h-m2/code/ast_validator.py
def validate_syntax_timed(code: str) -> Tuple[bool, float]:
    """
    Validate syntax and measure latency.
    Returns: (is_valid, elapsed_ms)
    """
    ...

def compute_latency_stats(timings: list) -> dict:
    """Returns: {mean, median, p95, max}"""
    ...


# From: h-m2/code/scoring.py
def combined_score(
    log_likelihood: float,
    code: str,
    alpha: float = 0.7,
    beta: float = 0.3
) -> Tuple[float, bool, float]:
    """Returns: (final_score, validity, elapsed_ms)"""
    ...

def rank_beams(scores: list) -> list:
    """Returns: rank indices [0 = highest]"""
    ...


# From: h-m2/code/beam_search_custom.py
class CustomBeamScorer:
    def __init__(self, alpha: float = 0.7, beta: float = 0.3): ...
    def score_candidates(self, candidates: list, log_probs: list) -> list: ...
    def log_step(self, step: int, candidates: list, scores: list, ranks: list): ...
    def get_logs(self) -> list: ...
    def reset(self): ...

def run_beam_search_scored(
    model,
    tokenizer,
    prompt: str,
    k: int,
    alpha: float,
    beta: float,
    max_tokens: int
) -> Tuple[list, list]:
    """Returns: (outputs, logs)"""
    ...


# From: h-m2/code/data_loader.py
def load_humaneval():
    """Load HumanEval-164."""
    ...


# From: h-m2/code/model_loader.py
def load_codellama(model_id: str, device, dtype: str):
    """Returns: (model, tokenizer)"""
    ...
```

**Verified from:** h-m2/code/ actual implementation

---

**Document Status:** Ready for Phase 4 Implementation
