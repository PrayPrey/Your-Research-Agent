# Logic Design: h-m1 Beam Search Mechanism Validation

**Date:** 2026-08-25  
**Author:** Anonymous  
**Hypothesis:** h-m1 (MECHANISM)  
**Subtask Budget:** 2 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** API signatures verified from h-e1/code/  
**Analyzed Path:** /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_verifai/docs/youra_research/h-e1/code/  
**Relevant Symbols:** load_humaneval, extract_poc_subset, setup_device, load_codellama, run_beam_search, time_generation, measure_ast_latency, compute_gate_metrics

---

## Applied Patterns

**Applied:** Callback Hook Pattern (HuggingFace transformers.StoppingCriteria)  
**Applied:** Statistical Aggregation Pattern (diversity metrics)

---

## M-2: Beam Count Logger [Complexity: 7, Budget: 2 subtasks]

**Applied:** Callback Hook Pattern

### API Signatures

```python
class BeamCountLogger:
    def __init__(self):
        """Initialize beam count tracker."""
        self.counts: list[int] = []
    
    def __call__(self, input_ids: torch.Tensor, scores: torch.Tensor, **kwargs) -> bool:
        """
        Log beam count at current step. Called by HF generate().
        input_ids: [num_beams, seq_len]
        """
        self.counts.append(input_ids.shape[0])
        return False  # Never stop early
    
    def get_counts(self) -> list[int]:
        """Return logged counts."""
        return self.counts
    
    def beam_maintained(self, expected_k: int) -> bool:
        """Check if all steps maintained k beams."""
        return all(c == expected_k for c in self.counts)
    
    def reset(self):
        """Clear counts for next problem."""
        self.counts = []
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | BeamCountLogger callback | __call__ implementation to track beam shape |
| L-2-2 | Validation method | beam_maintained() check logic |

---

## M-3: Diversity Measurement [Complexity: 4, Budget: 0 subtasks]

**Applied:** Set-based Deduplication Pattern

### API Signatures

```python
def measure_diversity(outputs: list[str]) -> dict:
    """
    Measure uniqueness of k beam outputs.
    outputs: k generated code strings
    Returns: {unique_count, diversity_ratio, unique_outputs}
    """
    unique = set(outputs)
    return {
        'unique_count': len(unique),
        'diversity_ratio': len(unique) / len(outputs) if outputs else 0.0,
        'unique_outputs': list(unique)
    }
```

---

## M-5: Ablation Study [Complexity: 9, Budget: 0 subtasks]

**Applied:** Iterative Parameter Sweep Pattern

### API Signatures

```python
def run_ablation_study(
    model,
    tokenizer,
    prompts: list[str],
    k_values: list[int],
    max_tokens: int
) -> dict:
    """
    Run beam search for each k, return metrics.
    Returns: {k: {beam_maintained, diversity, time_sec}}
    """
    results = {}
    
    for k in k_values:
        logger = BeamCountLogger()
        start = time.time()
        
        outputs = run_beam_search_with_logger(
            model, tokenizer, prompts, k, max_tokens, logger
        )
        
        elapsed = time.time() - start
        
        results[k] = {
            'beam_maintained': logger.beam_maintained(k),
            'beam_counts': logger.get_counts(),
            'diversity': [measure_diversity(out) for out in outputs],
            'time_sec': elapsed,
            'outputs': outputs
        }
    
    return results

def compare_ablation_results(results: dict) -> dict:
    """
    Compute comparison statistics.
    Returns: {avg_diversity_by_k, time_vs_k, maintenance_rate}
    """
    comparison = {}
    
    for k, metrics in results.items():
        div_ratios = [d['diversity_ratio'] for d in metrics['diversity']]
        comparison[k] = {
            'avg_diversity': sum(div_ratios) / len(div_ratios),
            'time_sec': metrics['time_sec'],
            'maintenance_rate': sum(metrics['beam_counts']) / (len(metrics['beam_counts']) * k)
        }
    
    return comparison
```

### Helper Function

```python
def run_beam_search_with_logger(
    model, tokenizer, prompts, k, max_tokens, logger
) -> list[list[str]]:
    """
    Wrapper around h-e1 run_beam_search with logger callback.
    Uses StoppingCriteriaList to inject logger.
    """
    from transformers import StoppingCriteriaList
    
    all_candidates = []
    
    for prompt in prompts:
        logger.reset()
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        # Inject logger as stopping criteria (but never actually stops)
        stopping = StoppingCriteriaList([logger])
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                num_beams=k,
                num_return_sequences=k,
                max_new_tokens=max_tokens,
                do_sample=False,
                stopping_criteria=stopping,
                pad_token_id=tokenizer.eos_token_id
            )
        
        candidates = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        candidates = [c[len(prompt):].strip() for c in candidates]
        all_candidates.append(candidates)
    
    return all_candidates
```

---

## M-6: Visualization [Complexity: 6, Budget: 0 subtasks]

**Applied:** Matplotlib Subplots Pattern

### API Signatures

```python
def plot_beam_count_over_steps(beam_counts: list[int], k: int, save_path: str):
    """
    Line plot of beam count per generation step.
    Expected: flat line at k (validation check).
    """
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=(10, 5))
    plt.plot(beam_counts, marker='o', label=f'k={k}')
    plt.axhline(y=k, color='red', linestyle='--', label='Expected')
    plt.xlabel('Generation Step')
    plt.ylabel('Active Beam Count')
    plt.title(f'Beam Count Maintenance (k={k})')
    plt.legend()
    plt.grid(True)
    plt.savefig(save_path, dpi=150)
    plt.close()

def plot_diversity_by_k(results: dict, save_path: str):
    """Bar chart of diversity ratio for each k."""
    import matplotlib.pyplot as plt
    
    k_vals = sorted(results.keys())
    avg_divs = [results[k]['avg_diversity'] for k in k_vals]
    
    plt.figure(figsize=(8, 5))
    plt.bar([str(k) for k in k_vals], avg_divs, color='skyblue')
    plt.axhline(y=0.6, color='red', linestyle='--', label='Target (60%)')
    plt.xlabel('Beam Width (k)')
    plt.ylabel('Diversity Ratio')
    plt.title('Output Diversity vs Beam Width')
    plt.legend()
    plt.savefig(save_path, dpi=150)
    plt.close()

def plot_compute_time_vs_k(results: dict, save_path: str):
    """Bar chart of generation time for each k."""
    import matplotlib.pyplot as plt
    
    k_vals = sorted(results.keys())
    times = [results[k]['time_sec'] for k in k_vals]
    
    plt.figure(figsize=(8, 5))
    plt.bar([str(k) for k in k_vals], times, color='orange')
    plt.xlabel('Beam Width (k)')
    plt.ylabel('Generation Time (seconds)')
    plt.title('Computational Cost vs Beam Width')
    plt.savefig(save_path, dpi=150)
    plt.close()
```

---

## External Dependencies (h-e1 Base Hypothesis)

### API Signatures (Verified from Actual Code)

```python
# From: h-e1/code/data_loader.py
def load_humaneval() -> Dataset:
    """Load HumanEval-164 test split."""
    ...

def extract_poc_subset(dataset: Dataset, n: int = 5) -> list[dict]:
    """Extract first n problems. Returns list with keys: task_id, prompt, test, entry_point."""
    ...

# From: h-e1/code/model_loader.py
def setup_device(device_str: str = "auto") -> torch.device:
    """Detect GPU and return device. device_str: "auto" | "cuda" | "cpu"."""
    ...

def load_codellama(model_id: str, device: torch.device, dtype: str) -> tuple:
    """Load model and tokenizer. dtype: "float16" | "float32". Returns (model, tokenizer)."""
    ...

# From: h-e1/code/beam_search.py
def run_beam_search(
    model, 
    tokenizer, 
    prompts: list[str], 
    k: int = 5, 
    max_new_tokens: int = 256
) -> list[list[str]]:
    """Run beam search. Returns [n_prompts, k_candidates]."""
    ...

def validate_syntax(code: str) -> bool:
    """AST parse validation."""
    ...

# From: h-e1/code/metrics.py
def time_generation(fn: Callable) -> tuple[Any, float]:
    """Time function execution. Returns (result, elapsed_sec)."""
    ...

def measure_ast_latency(candidates: list[list[str]]) -> dict:
    """Measure parse latency. Returns {mean, min, max, all}."""
    ...

def compute_gate_metrics(
    time_sec: float, 
    latency_ms: float, 
    time_target: int, 
    latency_target: int
) -> dict:
    """Gate check. Returns {time_pass, latency_pass, gate_pass}."""
    ...
```

**Verified from:** h-e1/code/ (actual implementation, NOT spec)

---

**Document Status:** Ready for Phase 4 Implementation
