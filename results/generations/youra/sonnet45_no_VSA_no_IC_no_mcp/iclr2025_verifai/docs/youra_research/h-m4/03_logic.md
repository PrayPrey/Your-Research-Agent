# Logic Design: h-m4 Final Valid Output Selection

**Date:** 2026-08-25  
**Author:** yoon303@ust.ac.kr  
**Hypothesis:** h-m4 (MECHANISM)  
**Subtask Budget:** 4 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** API signatures verified from h-m3/code/ actual implementation  
**Analyzed Path:** /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_verifai/docs/youra_research/h-m3/code/  
**Relevant Symbols:** validate_syntax_timed, combined_score, run_beam_search_with_tracking, BeamValidityTracker

---

## Applied Patterns

**Applied:** Argmax Selection Pattern  
**Applied:** Error Rate Comparison Pattern  
**Applied:** Stratified Analysis Pattern

---

## A-2: FinalOutputSelector [Complexity: 7, Budget: 1 subtask]

**Applied:** Argmax Selection Pattern

### API Signatures

```python
import numpy as np
from scoring import combined_score

class FinalOutputSelector:
    """Select best beam from k candidates using combined scoring."""
    
    def __init__(self, alpha: float = 0.7, beta: float = 0.3):
        self.alpha = alpha
        self.beta = beta
    
    def select_final_output(
        self,
        beams: list[str],
        log_likelihoods: list[float]
    ) -> tuple[str, int, list[float]]:
        """
        Select beam with highest final_score.
        
        Args:
            beams: [k] code strings
            log_likelihoods: [k] log probabilities
        
        Returns:
            (selected_beam, beam_idx, all_scores)
        """
        final_scores = []
        for beam, log_likelihood in zip(beams, log_likelihoods):
            score, _, _ = combined_score(log_likelihood, beam, self.alpha, self.beta)
            final_scores.append(score)
        
        best_idx = int(np.argmax(final_scores))
        return beams[best_idx], best_idx, final_scores
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | select_final_output | Argmax selection on combined scores |

---

## A-3: GreedySampler [Complexity: 6, Budget: 1 subtask]

**Applied:** Standard Generation Pattern

### API Signatures

```python
import torch

def run_greedy_baseline(
    model,
    tokenizer,
    prompts: list[str],
    max_tokens: int = 512,
    temperature: float = 0.8
) -> list[str]:
    """
    Run greedy sampling (num_beams=1).
    
    Args:
        prompts: [N] input prompts
    
    Returns:
        [N] generated code strings
    """
    outputs = []
    for prompt in prompts:
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        generated = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temperature,
            num_beams=1,
            do_sample=False
        )
        output = tokenizer.decode(generated[0], skip_special_tokens=True)
        outputs.append(output)
    return outputs
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | run_greedy_baseline | Greedy generation loop |

---

## A-4: SelectionAnalyzer [Complexity: 8, Budget: 1 subtask]

**Applied:** Stratified Analysis Pattern

### API Signatures

```python
import numpy as np
from ast_validator import validate_syntax_timed

class SelectionAnalyzer:
    """Analyze selection quality by beam availability."""
    
    @staticmethod
    def compute_selection_accuracy(
        all_beams: list[list[str]],
        selected_indices: list[int]
    ) -> dict:
        """
        Compute selection accuracy when valid beams available.
        
        Args:
            all_beams: [N][k] all beam candidates per problem
            selected_indices: [N] selected beam index per problem
        
        Returns:
            {
                'accuracy_1plus': float,  # ≥1 valid beam available
                'accuracy_3plus': float,  # ≥3 valid beams available
                'miss_rate': float
            }
        """
        correct_1plus = 0
        total_1plus = 0
        correct_3plus = 0
        total_3plus = 0
        misses = 0
        
        for beams, selected_idx in zip(all_beams, selected_indices):
            validity = [validate_syntax_timed(b)[0] for b in beams]
            valid_count = sum(validity)
            selected_valid = validity[selected_idx]
            
            if valid_count >= 1:
                total_1plus += 1
                if selected_valid:
                    correct_1plus += 1
                else:
                    misses += 1
            
            if valid_count >= 3:
                total_3plus += 1
                if selected_valid:
                    correct_3plus += 1
        
        return {
            'accuracy_1plus': correct_1plus / total_1plus if total_1plus > 0 else 0.0,
            'accuracy_3plus': correct_3plus / total_3plus if total_3plus > 0 else 0.0,
            'miss_rate': misses / total_1plus if total_1plus > 0 else 0.0
        }
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | compute_selection_accuracy | Stratified accuracy computation |

---

## A-5: StrategyComparator [Complexity: 9, Budget: 1 subtask]

**Applied:** Strategy Ablation Pattern

### API Signatures

```python
import numpy as np
from ast_validator import validate_syntax_timed

class StrategyComparator:
    """Compare alternative selection strategies."""
    
    @staticmethod
    def compare_strategies(
        all_beams: list[list[str]],
        all_scores: list[list[float]]
    ) -> dict:
        """
        Test argmax, validity-first, random-valid strategies.
        
        Args:
            all_beams: [N][k] beam candidates
            all_scores: [N][k] final scores
        
        Returns:
            {
                'argmax_validity': float,
                'validity_first_validity': float,
                'random_valid_validity': float,
                'best_strategy': str
            }
        """
        # Strategy 1: argmax(final_score) - current
        argmax_selected = [beams[int(np.argmax(scores))] for beams, scores in zip(all_beams, all_scores)]
        argmax_valid = sum(validate_syntax_timed(b)[0] for b in argmax_selected) / len(argmax_selected)
        
        # Strategy 2: validity-first (argmax validity, tie-break by score)
        validity_first_selected = []
        for beams, scores in zip(all_beams, all_scores):
            validity = [validate_syntax_timed(b)[0] for b in beams]
            if any(validity):
                # Pick highest-scoring valid beam
                valid_indices = [i for i, v in enumerate(validity) if v]
                best_valid = max(valid_indices, key=lambda i: scores[i])
                validity_first_selected.append(beams[best_valid])
            else:
                # Fallback to argmax score
                validity_first_selected.append(beams[int(np.argmax(scores))])
        vf_valid = sum(validate_syntax_timed(b)[0] for b in validity_first_selected) / len(validity_first_selected)
        
        # Strategy 3: random from valid beams
        import random
        random.seed(42)
        random_valid_selected = []
        for beams in all_beams:
            validity = [validate_syntax_timed(b)[0] for b in beams]
            valid_beams = [b for b, v in zip(beams, validity) if v]
            if valid_beams:
                random_valid_selected.append(random.choice(valid_beams))
            else:
                random_valid_selected.append(random.choice(beams))
        rv_valid = sum(validate_syntax_timed(b)[0] for b in random_valid_selected) / len(random_valid_selected)
        
        results = {
            'argmax': argmax_valid,
            'validity_first': vf_valid,
            'random_valid': rv_valid
        }
        best_strategy = max(results, key=results.get)
        
        return {
            'argmax_validity': argmax_valid,
            'validity_first_validity': vf_valid,
            'random_valid_validity': rv_valid,
            'best_strategy': best_strategy
        }
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | compare_strategies | Test 3 selection strategies |

---

## A-7: ErrorRateComparator [Complexity: 5, Budget: 0 subtasks]

**Applied:** Error Rate Comparison Pattern

### API Signatures

```python
def compute_error_reduction(
    greedy_outputs: list[str],
    beam_outputs: list[str]
) -> dict:
    """
    Compare greedy vs beam search syntax error rates.
    
    Args:
        greedy_outputs: [N] greedy generated code
        beam_outputs: [N] beam-selected code
    
    Returns:
        {
            'greedy_error_rate': float,
            'beam_error_rate': float,
            'absolute_reduction': float,
            'relative_reduction': float  # percentage
        }
    """
    from ast_validator import validate_syntax_timed
    
    greedy_errors = sum(1 for code in greedy_outputs if not validate_syntax_timed(code)[0])
    beam_errors = sum(1 for code in beam_outputs if not validate_syntax_timed(code)[0])
    
    greedy_error_rate = greedy_errors / len(greedy_outputs)
    beam_error_rate = beam_errors / len(beam_outputs)
    
    absolute_reduction = greedy_error_rate - beam_error_rate
    relative_reduction = (absolute_reduction / greedy_error_rate * 100) if greedy_error_rate > 0 else 0.0
    
    return {
        'greedy_error_rate': greedy_error_rate,
        'beam_error_rate': beam_error_rate,
        'absolute_reduction': absolute_reduction,
        'relative_reduction': relative_reduction
    }
```

---

## External Dependencies (h-m3 Base Hypothesis)

### API Signatures (Verified from Actual Code)

```python
# From: h-m3/code/ast_validator.py
def validate_syntax_timed(code: str) -> Tuple[bool, float]:
    """
    Validate syntax and measure latency.
    Returns: (is_valid, elapsed_ms)
    """
    ...

# From: h-m3/code/scoring.py
def combined_score(
    log_likelihood: float,
    code: str,
    alpha: float = 0.7,
    beta: float = 0.3
) -> Tuple[float, bool, float]:
    """Returns: (final_score, validity, elapsed_ms)"""
    ...

# From: h-m3/code/beam_search_tracked.py
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
    Run beam search with tracking.
    Returns: (outputs, tracking_data)
    """
    ...
```

**Verified from:** h-m3/code/ actual implementation

---

**Document Status:** Ready for Phase 4 Implementation
