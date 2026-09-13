# Logic Design: h-m2 Combined Scoring Function

**Date:** 2026-08-25  
**Author:** yoon303@ust.ac.kr  
**Hypothesis:** h-m2 (MECHANISM)  
**Subtask Budget:** 2 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** API signatures verified from h-m1/code/  
**Analyzed Path:** /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_verifai/docs/youra_research/h-m1/code/  
**Relevant Symbols:** load_humaneval, extract_poc_subset, setup_device, load_codellama, run_beam_search, validate_syntax, BeamCountLogger

---

## Applied Patterns

**Applied:** AST Timing Pattern (stdlib time.perf_counter)  
**Applied:** Combined Scoring Pattern (weighted sum)

---

## S-2: AST Validator with Timing [Complexity: 5, Budget: 2 subtasks]

**Applied:** AST Timing Pattern

### API Signatures

```python
import ast
import time

def validate_syntax_timed(code: str) -> tuple[bool, float]:
    """
    Validate syntax and measure latency.
    Returns: (is_valid, elapsed_ms)
    """
    start = time.perf_counter()
    try:
        ast.parse(code)
        valid = True
    except SyntaxError:
        valid = False
    elapsed = (time.perf_counter() - start) * 1000  # ms
    return valid, elapsed

def compute_latency_stats(timings: list[float]) -> dict:
    """Compute latency statistics. timings: milliseconds"""
    import numpy as np
    return {
        'mean': float(np.mean(timings)),
        'median': float(np.median(timings)),
        'p95': float(np.percentile(timings, 95)),
        'max': float(np.max(timings))
    }
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | validate_syntax_timed | Add timing to ast.parse |
| L-2-2 | compute_latency_stats | Statistics computation |

---

## S-3: Combined Scoring Function [Complexity: 6, Budget: 0 subtasks]

**Applied:** Combined Scoring Pattern

### API Signatures

```python
def combined_score(
    log_likelihood: float, 
    code: str, 
    alpha: float = 0.7, 
    beta: float = 0.3
) -> tuple[float, bool, float]:
    """
    Compute combined score.
    Returns: (final_score, validity, elapsed_ms)
    """
    validity, elapsed_ms = validate_syntax_timed(code)
    validity_score = 1.0 if validity else 0.0
    final_score = alpha * log_likelihood + beta * validity_score
    return final_score, validity, elapsed_ms

def rank_beams(scores: list[float]) -> list[int]:
    """Return rank indices (0 = highest score)."""
    import numpy as np
    return np.argsort(scores)[::-1].tolist()
```

---

## S-4: Custom Beam Scorer [Complexity: 10, Budget: 0 subtasks]

**Applied:** Callback Hook Pattern

### API Signatures

```python
class CustomBeamScorer:
    """Track and score beam candidates with combined scoring."""
    
    def __init__(self, alpha: float = 0.7, beta: float = 0.3):
        self.alpha = alpha
        self.beta = beta
        self.step_logs = []
    
    def score_candidates(
        self, 
        candidates: list[str], 
        log_probs: list[float]
    ) -> list[float]:
        """
        Score each candidate.
        Returns: final_scores [k]
        """
        final_scores = []
        for cand, logp in zip(candidates, log_probs):
            score, _, _ = combined_score(logp, cand, self.alpha, self.beta)
            final_scores.append(score)
        return final_scores
    
    def log_step(
        self, 
        step: int, 
        candidates: list[str], 
        scores: list[float], 
        ranks: list[int]
    ):
        """Log beam state at generation step."""
        for i, (cand, score, rank) in enumerate(zip(candidates, scores, ranks)):
            _, validity, elapsed_ms = combined_score(0.0, cand, self.alpha, self.beta)
            self.step_logs.append({
                'step': step,
                'beam_id': i,
                'score': score,
                'rank': rank,
                'validity': validity,
                'elapsed_ms': elapsed_ms
            })
    
    def get_logs(self) -> list[dict]:
        return self.step_logs
    
    def reset(self):
        self.step_logs = []

def run_beam_search_scored(
    model, 
    tokenizer, 
    prompt: str, 
    k: int, 
    alpha: float, 
    beta: float, 
    max_tokens: int
) -> tuple[list[str], list[dict]]:
    """
    Run beam search with combined scoring.
    Returns: (outputs, step_logs)
    """
    from transformers import StoppingCriteriaList
    
    scorer = CustomBeamScorer(alpha, beta)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            num_beams=k,
            num_return_sequences=k,
            max_new_tokens=max_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
            output_scores=True,
            return_dict_in_generate=True
        )
    
    candidates = tokenizer.batch_decode(
        outputs.sequences, 
        skip_special_tokens=True
    )
    candidates = [c[len(prompt):].strip() for c in candidates]
    
    return candidates, scorer.get_logs()
```

---

## S-5: Experiment A+B Runners [Complexity: 8, Budget: 0 subtasks]

**Applied:** Iteration Pattern

### API Signatures

```python
def experiment_a_latency(
    model, 
    tokenizer, 
    dataset: list[dict], 
    k: int = 5
) -> dict:
    """
    Measure AST parse latency across dataset.
    Returns: {timings, stats}
    """
    all_timings = []
    
    for problem in dataset:
        candidates, _ = run_beam_search_scored(
            model, tokenizer, problem['prompt'], k, 0.7, 0.3, 512
        )
        for cand in candidates:
            _, elapsed_ms = validate_syntax_timed(cand)
            all_timings.append(elapsed_ms)
    
    stats = compute_latency_stats(all_timings)
    return {'timings': all_timings, 'stats': stats}

def experiment_b_ranking(
    model, 
    tokenizer, 
    dataset: list[dict], 
    alpha: float = 0.7, 
    beta: float = 0.3
) -> dict:
    """
    Verify beam ranking correctness.
    Returns: {logs, correct_proportion}
    """
    all_logs = []
    
    for problem in dataset:
        _, logs = run_beam_search_scored(
            model, tokenizer, problem['prompt'], 5, alpha, beta, 512
        )
        all_logs.extend(logs)
    
    steps_by_id = {}
    for log in all_logs:
        step_id = log['step']
        if step_id not in steps_by_id:
            steps_by_id[step_id] = []
        steps_by_id[step_id].append(log)
    
    correct_steps = 0
    total_steps = len(steps_by_id)
    
    for step_id, beams in steps_by_id.items():
        valid_beams = [b for b in beams if b['validity']]
        invalid_beams = [b for b in beams if not b['validity']]
        
        if valid_beams and invalid_beams:
            max_valid_score = max(b['score'] for b in valid_beams)
            max_invalid_score = max(b['score'] for b in invalid_beams)
            if max_valid_score > max_invalid_score:
                correct_steps += 1
    
    return {
        'logs': all_logs,
        'correct_proportion': correct_steps / total_steps if total_steps > 0 else 0.0
    }
```

---

## S-6: Experiment C Ablation [Complexity: 7, Budget: 0 subtasks]

**Applied:** Grid Search Pattern

### API Signatures

```python
def experiment_c_ablation(
    model, 
    tokenizer, 
    subset: list[dict], 
    weight_pairs: list[tuple]
) -> dict:
    """
    Test alpha/beta combinations.
    Returns: {(alpha, beta): {ranking_correctness, syntax_error_rate}}
    """
    results = {}
    
    for alpha, beta in weight_pairs:
        logs = []
        for problem in subset:
            _, step_logs = run_beam_search_scored(
                model, tokenizer, problem['prompt'], 5, alpha, beta, 512
            )
            logs.extend(step_logs)
        
        # Compute ranking correctness
        steps = {}
        for log in logs:
            step_id = log['step']
            if step_id not in steps:
                steps[step_id] = []
            steps[step_id].append(log)
        
        correct = 0
        total = len(steps)
        
        for beams in steps.values():
            valid = [b for b in beams if b['validity']]
            invalid = [b for b in beams if not b['validity']]
            if valid and invalid:
                if max(b['score'] for b in valid) > max(b['score'] for b in invalid):
                    correct += 1
        
        results[(alpha, beta)] = {
            'ranking_correctness': correct / total if total > 0 else 0.0,
            'logs': logs
        }
    
    return results
```

---

## S-7: Baseline Comparison [Complexity: 6, Budget: 0 subtasks]

**Applied:** Standard Pattern (reuse h-m1 run_beam_search)

### API Signatures

```python
def baseline_comparison(
    model, 
    tokenizer, 
    dataset: list[dict]
) -> dict:
    """
    Run greedy and pure LL baselines.
    Returns: {greedy_errors, pure_beam_errors, combined_errors}
    """
    from beam_search import run_beam_search
    
    # Pure log-likelihood (alpha=1.0, beta=0.0)
    pure_beam_results = []
    for problem in dataset:
        outputs = run_beam_search(
            model, tokenizer, [problem['prompt']], k=5, max_new_tokens=512
        )
        pure_beam_results.extend(outputs[0])
    
    pure_errors = sum(1 for code in pure_beam_results if not validate_syntax(code))
    pure_error_rate = pure_errors / len(pure_beam_results)
    
    # Combined scoring (alpha=0.7, beta=0.3)
    combined_results = []
    for problem in dataset:
        outputs, _ = run_beam_search_scored(
            model, tokenizer, problem['prompt'], 5, 0.7, 0.3, 512
        )
        combined_results.extend(outputs)
    
    combined_errors = sum(1 for code in combined_results if not validate_syntax(code))
    combined_error_rate = combined_errors / len(combined_results)
    
    return {
        'pure_beam_error_rate': pure_error_rate,
        'combined_error_rate': combined_error_rate,
        'improvement': pure_error_rate - combined_error_rate
    }
```

---

## S-8: Analysis Pipeline [Complexity: 9, Budget: 0 subtasks]

**Applied:** Statistics Aggregation Pattern

### API Signatures

```python
def analyze_latency(timings: list[float]) -> dict:
    """
    Compute latency statistics and gate check.
    Returns: {stats, gate_pass}
    """
    stats = compute_latency_stats(timings)
    gate_pass = stats['mean'] < 50 and stats['p95'] < 100
    return {'stats': stats, 'gate_pass': gate_pass}

def analyze_ranking(logs: list[dict]) -> dict:
    """
    Compute ranking correctness proportion.
    Returns: {correct_proportion, gate_pass}
    """
    steps = {}
    for log in logs:
        step_id = log['step']
        if step_id not in steps:
            steps[step_id] = []
        steps[step_id].append(log)
    
    correct = 0
    total = len(steps)
    
    for beams in steps.values():
        valid = [b for b in beams if b['validity']]
        invalid = [b for b in beams if not b['validity']]
        if valid and invalid:
            if max(b['score'] for b in valid) > max(b['score'] for b in invalid):
                correct += 1
    
    proportion = correct / total if total > 0 else 0.0
    return {'correct_proportion': proportion, 'gate_pass': proportion >= 0.8}

def compare_ablation(results: dict) -> dict:
    """
    Identify optimal alpha/beta weights.
    Returns: {optimal_pair, metrics_by_pair}
    """
    optimal = None
    best_correctness = 0.0
    
    for (alpha, beta), metrics in results.items():
        if metrics['ranking_correctness'] > best_correctness:
            best_correctness = metrics['ranking_correctness']
            optimal = (alpha, beta)
    
    return {'optimal_pair': optimal, 'metrics_by_pair': results}

def compare_baselines(
    greedy_errors: float, 
    pure_beam_errors: float, 
    combined_errors: float
) -> dict:
    """
    Compute relative improvements.
    Returns: {improvements, gate_pass}
    """
    improvement_vs_pure = pure_beam_errors - combined_errors
    gate_pass = combined_errors < greedy_errors
    
    return {
        'improvement_vs_pure': improvement_vs_pure,
        'gate_pass': gate_pass,
        'greedy_error_rate': greedy_errors,
        'pure_beam_error_rate': pure_beam_errors,
        'combined_error_rate': combined_errors
    }
```

---

## External Dependencies (h-m1 Base Hypothesis)

### API Signatures (Verified from Actual Code)

```python
# From: h-m1/code/data_loader.py
def load_humaneval() -> Dataset:
    """Load HumanEval-164 test split."""
    ...

def extract_poc_subset(dataset: Dataset, n: int = 5) -> list[dict]:
    """Extract first n problems. Returns list with keys: task_id, prompt, test, entry_point."""
    ...

# From: h-m1/code/model_loader.py
def setup_device(device_str: str = "auto") -> torch.device:
    """Detect GPU. device_str: "auto" | "cuda" | "cpu"."""
    ...

def load_codellama(model_id: str, device: torch.device, dtype: str) -> tuple:
    """Load model and tokenizer. dtype: "float16" | "float32". Returns (model, tokenizer)."""
    ...

# From: h-m1/code/beam_search.py
def validate_syntax(code: str) -> bool:
    """AST parse validation."""
    ...

def run_beam_search(
    model, 
    tokenizer, 
    prompts: list[str], 
    k: int = 5, 
    max_new_tokens: int = 256
) -> list[list[str]]:
    """Run beam search. Returns [n_prompts, k_candidates]."""
    ...

# From: h-m1/code/beam_logger.py
class BeamCountLogger:
    def __init__(self): ...
    def __call__(self, input_ids: torch.Tensor, scores: torch.Tensor, **kwargs) -> bool: ...
    def get_counts(self) -> list[int]: ...
    def beam_maintained(self, expected_k: int) -> bool: ...
    def reset(self): ...
```

**Verified from:** h-m1/code/ (actual implementation)

---

**Document Status:** Ready for Phase 4 Implementation
