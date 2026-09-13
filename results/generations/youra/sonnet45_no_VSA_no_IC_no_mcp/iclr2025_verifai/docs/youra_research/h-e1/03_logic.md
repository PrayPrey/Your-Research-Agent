# Logic Design: h-e1 Beam Search Infrastructure PoC

**Date:** 2026-08-25  
**Author:** Anonymous  
**Hypothesis:** h-e1 (EXISTENCE)  
**Subtask Budget:** 2 subtasks (EPIC-4 decomposition)

---

## Codebase Analysis (Serena)

**Analysis Type:** Green-field (no existing codebase)

No existing modules to analyze. This is a foundation hypothesis with no prerequisites. Starting from scratch with minimal PoC implementation.

**Design Implications:**
- Define APIs from scratch
- Focus on simplicity and clarity
- No backward compatibility constraints

---

## Applied Patterns

**Applied:** Functional Decomposition Pattern (Archon KB: API Design Best Practices)  
**Applied:** Type-Safe Interfaces Pattern (Archon KB: Python Type Hints)  
**Applied:** Separation of Concerns Pattern (Archon KB: Module Boundaries)

**Rationale:** Clear function boundaries with explicit type hints enable independent testing and future extension.

---

## Module APIs

### Module 1: Data Preparation (`data_loader.py`)

#### `load_humaneval() -> Dataset`
**Purpose:** Load HumanEval-164 dataset from HuggingFace Hub

**Type Signature:**
```python
from datasets import Dataset

def load_humaneval() -> Dataset:
    """
    Load HumanEval benchmark dataset.
    
    Returns:
        Dataset: HuggingFace Dataset object with 'test' split (164 problems)
    """
```

**Implementation Outline:**
```python
from datasets import load_dataset

def load_humaneval() -> Dataset:
    dataset = load_dataset("openai_humaneval")
    return dataset['test']
```

**Complexity:** Low (single API call)

---

#### `extract_poc_subset(dataset: Dataset, n: int = 5) -> list[dict]`
**Purpose:** Extract first n problems for PoC validation

**Type Signature:**
```python
def extract_poc_subset(
    dataset: Dataset, 
    n: int = 5
) -> list[dict]:
    """
    Extract first n problems from dataset.
    
    Args:
        dataset: Full HumanEval dataset
        n: Number of problems to extract (default: 5)
    
    Returns:
        List of dicts with keys: task_id, prompt, canonical_solution, test, entry_point
    """
```

**Implementation Outline:**
```python
def extract_poc_subset(dataset: Dataset, n: int = 5) -> list[dict]:
    subset = dataset.select(range(n))
    return [
        {
            'task_id': item['task_id'],
            'prompt': item['prompt'],
            'canonical_solution': item['canonical_solution'],
            'test': item['test'],
            'entry_point': item['entry_point']
        }
        for item in subset
    ]
```

**Complexity:** Low (indexing + dict mapping)

---

### Module 2: Model Setup (`model_loader.py`)

#### `setup_device() -> torch.device`
**Purpose:** Detect available hardware and return torch device

**Type Signature:**
```python
import torch

def setup_device() -> torch.device:
    """
    Detect GPU availability and return appropriate device.
    
    Returns:
        torch.device: CUDA device if available, else CPU
    """
```

**Implementation Outline:**
```python
import torch

def setup_device() -> torch.device:
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device("cpu")
        print("Using CPU (no GPU available)")
    return device
```

**Complexity:** Low (hardware detection)

---

#### `load_codellama() -> tuple[AutoModelForCausalLM, AutoTokenizer]`
**Purpose:** Load CodeLlama-7B model and tokenizer from HuggingFace Hub

**Type Signature:**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

def load_codellama(
    device: torch.device
) -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """
    Load CodeLlama-7B model and tokenizer.
    
    Args:
        device: Target device (cuda or cpu)
    
    Returns:
        Tuple of (model, tokenizer)
    """
```

**Implementation Outline:**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

def load_codellama(device: torch.device) -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    model_id = "meta-llama/CodeLlama-7b-hf"
    
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16 if device.type == "cuda" else torch.float32,
        device_map="auto" if device.type == "cuda" else None
    )
    
    if device.type == "cpu":
        model = model.to(device)
    
    return model, tokenizer
```

**Complexity:** Medium (model loading with device management)

---

### Module 3: Beam Search Engine (`beam_search.py`)

#### `validate_syntax(code: str) -> bool`
**Purpose:** Check if generated code is syntactically valid Python

**Type Signature:**
```python
def validate_syntax(code: str) -> bool:
    """
    Parse code with ast.parse to validate syntax.
    
    Args:
        code: Python code string
    
    Returns:
        True if valid syntax, False otherwise
    """
```

**Implementation Outline:**
```python
import ast

def validate_syntax(code: str) -> bool:
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False
```

**Complexity:** Low (try-except wrapper)

---

#### `custom_scoring_fn(outputs: list[str], logprobs: list[float]) -> list[float]`
**Purpose:** Compute combined score: α * log_likelihood + β * validity_score

**Type Signature:**
```python
def custom_scoring_fn(
    outputs: list[str], 
    logprobs: list[float]
) -> list[float]:
    """
    Compute combined fluency + validity scores for beam candidates.
    
    Args:
        outputs: List of k generated code strings
        logprobs: List of k log-probability scores from model
    
    Returns:
        List of k combined scores (higher is better)
    
    Formula:
        score = 0.7 * logprob + 0.3 * validity_score
        where validity_score ∈ {0.0, 1.0}
    """
```

**Implementation Outline:**
```python
def custom_scoring_fn(outputs: list[str], logprobs: list[float]) -> list[float]:
    ALPHA = 0.7  # Fluency weight
    BETA = 0.3   # Validity weight
    
    scores = []
    for output, logprob in zip(outputs, logprobs):
        validity = 1.0 if validate_syntax(output) else 0.0
        combined_score = ALPHA * logprob + BETA * validity
        scores.append(combined_score)
    
    return scores
```

**Complexity:** Low (linear iteration)

---

#### SUBTASK 1: `run_beam_search(model, tokenizer, prompts, k=5) -> list[list[str]]`
**Purpose:** Execute beam search with custom scoring for each prompt

**Type Signature:**
```python
def run_beam_search(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    prompts: list[str],
    k: int = 5
) -> list[list[str]]:
    """
    Run beam search with custom AST-based scoring.
    
    Args:
        model: Loaded CodeLlama model
        tokenizer: Loaded tokenizer
        prompts: List of n problem prompts
        k: Beam width (number of candidates per prompt)
    
    Returns:
        List of n lists, each containing k candidate solutions
    
    Shape: [n_prompts, k_candidates]
    """
```

**Implementation Approach:**

**Option A: HuggingFace generate() with num_beams** (if custom scoring not supported)
```python
def run_beam_search(model, tokenizer, prompts, k=5):
    all_candidates = []
    
    for prompt in prompts:
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        outputs = model.generate(
            **inputs,
            num_beams=k,
            num_return_sequences=k,
            max_new_tokens=256,
            do_sample=False  # Deterministic beam search
        )
        
        candidates = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        all_candidates.append(candidates)
    
    return all_candidates
```

**Limitation:** Standard beam search doesn't integrate custom scoring DURING generation. Post-hoc reranking possible.

---

**Option B: LogitsProcessor for custom scoring** (if HF supports it)
```python
from transformers import LogitsProcessor

class ASTValidityProcessor(LogitsProcessor):
    def __init__(self, tokenizer, alpha=0.7, beta=0.3):
        self.tokenizer = tokenizer
        self.alpha = alpha
        self.beta = beta
    
    def __call__(self, input_ids, scores):
        # Decode current candidates
        candidates = self.tokenizer.batch_decode(input_ids, skip_special_tokens=True)
        
        # Adjust scores based on AST validity
        for i, candidate in enumerate(candidates):
            validity = 1.0 if validate_syntax(candidate) else 0.0
            # Combine with existing logprob scores
            scores[i] = self.alpha * scores[i] + self.beta * validity
        
        return scores

def run_beam_search(model, tokenizer, prompts, k=5):
    processor = ASTValidityProcessor(tokenizer)
    
    all_candidates = []
    for prompt in prompts:
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        outputs = model.generate(
            **inputs,
            num_beams=k,
            num_return_sequences=k,
            max_new_tokens=256,
            logits_processor=[processor]
        )
        
        candidates = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        all_candidates.append(candidates)
    
    return all_candidates
```

**Recommended:** Start with Option A (standard beam search), measure baseline. If time permits, implement Option B for integrated scoring.

**Complexity:** Medium (beam search integration, device management, batching)

---

#### SUBTASK 2: `rerank_by_validity(candidates: list[list[str]]) -> list[list[str]]`
**Purpose:** Post-hoc reranking of beam candidates by combined score

**Type Signature:**
```python
def rerank_by_validity(
    candidates: list[list[str]],
    logprobs: list[list[float]]
) -> list[list[str]]:
    """
    Rerank beam candidates using custom scoring function.
    
    Args:
        candidates: [n_prompts, k_candidates] code strings
        logprobs: [n_prompts, k_candidates] log-probability scores
    
    Returns:
        Reranked candidates [n_prompts, k_candidates]
    """
```

**Implementation Outline:**
```python
def rerank_by_validity(candidates, logprobs):
    reranked = []
    
    for prompt_candidates, prompt_logprobs in zip(candidates, logprobs):
        scores = custom_scoring_fn(prompt_candidates, prompt_logprobs)
        
        # Sort by combined score (descending)
        sorted_pairs = sorted(
            zip(scores, prompt_candidates),
            key=lambda x: x[0],
            reverse=True
        )
        
        reranked_candidates = [code for _, code in sorted_pairs]
        reranked.append(reranked_candidates)
    
    return reranked
```

**Complexity:** Low (sorting k candidates per prompt)

---

### Module 4: Evaluation Metrics (`metrics.py`)

#### `time_generation(fn: callable) -> tuple[Any, float]`
**Purpose:** Measure wall-clock time for generation function

**Type Signature:**
```python
from typing import Any, Callable

def time_generation(fn: Callable) -> tuple[Any, float]:
    """
    Time a generation function execution.
    
    Args:
        fn: Callable that performs generation
    
    Returns:
        Tuple of (function result, elapsed seconds)
    """
```

**Implementation Outline:**
```python
import time

def time_generation(fn):
    start = time.time()
    result = fn()
    elapsed = time.time() - start
    return result, elapsed
```

**Complexity:** Low (simple timer wrapper)

---

#### `measure_ast_latency(candidates: list[list[str]]) -> dict`
**Purpose:** Measure AST parse latency per candidate

**Type Signature:**
```python
def measure_ast_latency(candidates: list[list[str]]) -> dict:
    """
    Measure AST parse latency statistics.
    
    Args:
        candidates: [n_prompts, k_candidates] code strings
    
    Returns:
        Dict with keys:
            - mean: average latency (ms)
            - min: minimum latency (ms)
            - max: maximum latency (ms)
            - all: list of all latencies (ms)
    """
```

**Implementation Outline:**
```python
import time
import ast

def measure_ast_latency(candidates):
    latencies = []
    
    for prompt_candidates in candidates:
        for code in prompt_candidates:
            start = time.time()
            try:
                ast.parse(code)
            except SyntaxError:
                pass  # Still measure latency for failed parses
            elapsed_ms = (time.time() - start) * 1000
            latencies.append(elapsed_ms)
    
    return {
        'mean': sum(latencies) / len(latencies),
        'min': min(latencies),
        'max': max(latencies),
        'all': latencies
    }
```

**Complexity:** Low (linear iteration)

---

#### `compute_gate_metrics(time_sec: float, latency_ms: float) -> dict`
**Purpose:** Check if gate criteria are met

**Type Signature:**
```python
def compute_gate_metrics(time_sec: float, latency_ms: float) -> dict:
    """
    Compute gate pass/fail status.
    
    Args:
        time_sec: Total generation time in seconds
        latency_ms: Average AST parse latency in milliseconds
    
    Returns:
        Dict with keys:
            - time_target: 1800 (30 min in seconds)
            - time_actual: time_sec
            - time_pass: bool
            - latency_target: 50 (ms)
            - latency_actual: latency_ms
            - latency_pass: bool
            - gate_pass: bool (both criteria met)
    """
```

**Implementation Outline:**
```python
def compute_gate_metrics(time_sec, latency_ms):
    TIME_TARGET = 1800  # 30 minutes in seconds
    LATENCY_TARGET = 50  # milliseconds
    
    time_pass = time_sec < TIME_TARGET
    latency_pass = latency_ms < LATENCY_TARGET
    
    return {
        'time_target': TIME_TARGET,
        'time_actual': time_sec,
        'time_pass': time_pass,
        'latency_target': LATENCY_TARGET,
        'latency_actual': latency_ms,
        'latency_pass': latency_pass,
        'gate_pass': time_pass and latency_pass
    }
```

**Complexity:** Low (simple comparison)

---

### Module 5: Visualization (`visualizations.py`)

#### `plot_gate_metrics(metrics: dict, save_path: str) -> None`
**Purpose:** Generate mandatory gate metrics bar chart

**Type Signature:**
```python
def plot_gate_metrics(metrics: dict, save_path: str) -> None:
    """
    Plot target vs actual for gate metrics.
    
    Args:
        metrics: Output from compute_gate_metrics()
        save_path: File path to save figure (e.g., 'figures/gate_metrics.png')
    """
```

**Implementation Outline:**
```python
import matplotlib.pyplot as plt

def plot_gate_metrics(metrics, save_path):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Time comparison
    axes[0].bar(['Target', 'Actual'], 
                [metrics['time_target'], metrics['time_actual']],
                color=['green', 'blue'])
    axes[0].set_ylabel('Time (seconds)')
    axes[0].set_title('Computational Time')
    axes[0].axhline(y=metrics['time_target'], color='red', linestyle='--', label='Threshold')
    
    # Latency comparison
    axes[1].bar(['Target', 'Actual'], 
                [metrics['latency_target'], metrics['latency_actual']],
                color=['green', 'orange'])
    axes[1].set_ylabel('Latency (ms)')
    axes[1].set_title('AST Parse Latency')
    axes[1].axhline(y=metrics['latency_target'], color='red', linestyle='--', label='Threshold')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
```

**Complexity:** Low (matplotlib API calls)

---

### Module 6: Main Execution Pipeline (`run_poc.py`)

#### `main() -> None`
**Purpose:** Orchestrate end-to-end PoC execution

**Type Signature:**
```python
def main() -> None:
    """
    Execute full PoC pipeline:
    1. Load data and model
    2. Run beam search on 5 problems
    3. Measure metrics
    4. Generate visualizations
    5. Save results
    """
```

**Implementation Outline:**
```python
import json
from pathlib import Path

def main():
    # Setup
    device = setup_device()
    model, tokenizer = load_codellama(device)
    
    # Data
    dataset = load_humaneval()
    problems = extract_poc_subset(dataset, n=5)
    prompts = [p['prompt'] for p in problems]
    
    # Generation with timing
    def generate():
        return run_beam_search(model, tokenizer, prompts, k=5)
    
    candidates, elapsed_sec = time_generation(generate)
    
    # Metrics
    latency_stats = measure_ast_latency(candidates)
    gate_metrics = compute_gate_metrics(elapsed_sec, latency_stats['mean'])
    
    # Visualizations
    Path('figures').mkdir(exist_ok=True)
    plot_gate_metrics(gate_metrics, 'figures/gate_metrics.png')
    
    # Save results
    results = {
        'gate_metrics': gate_metrics,
        'latency_stats': latency_stats,
        'num_problems': len(prompts),
        'beam_width': 5
    }
    
    with open('outputs/results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"PoC Complete!")
    print(f"Gate Pass: {gate_metrics['gate_pass']}")
    print(f"Time: {elapsed_sec:.1f}s / {gate_metrics['time_target']}s")
    print(f"Latency: {latency_stats['mean']:.1f}ms / {gate_metrics['latency_target']}ms")
    print(f"{'='*60}")
```

**Complexity:** Low (sequential orchestration)

---

## Tensor Shapes (N/A for PoC)

No custom tensor operations in this PoC. All tensor handling is internal to HuggingFace Transformers:

- Input IDs: `[batch_size, seq_len]` (handled by tokenizer)
- Model outputs: `[batch_size * k, output_seq_len]` (k=beam width)
- Logits: `[batch_size * k, seq_len, vocab_size]` (internal)

---

## Algorithms

### Beam Search with Custom Scoring

**Pseudocode:**
```
FUNCTION beam_search(model, prompt, k):
    candidates = []
    
    IF HF_supports_custom_scoring:
        # Option B: Integrated scoring
        processor = ASTValidityProcessor(tokenizer, alpha=0.7, beta=0.3)
        candidates = model.generate(
            prompt, 
            num_beams=k, 
            logits_processor=[processor]
        )
    ELSE:
        # Option A: Standard beam search + post-hoc reranking
        candidates = model.generate(prompt, num_beams=k)
        logprobs = extract_logprobs(model, candidates)
        candidates = rerank_by_validity(candidates, logprobs)
    
    RETURN top_k(candidates)
```

**Time Complexity:** O(k * T * V) where T = max_tokens, V = vocab_size (standard beam search)

**Space Complexity:** O(k * T) for maintaining k beams

---

## Error Handling

### Critical Error Points

1. **Model Loading:**
   - GPU OOM → Fallback to CPU
   - Missing model → Pre-download in setup

2. **Beam Search:**
   - OOM during generation → Reduce batch size to 1
   - Invalid outputs → AST validation catches

3. **AST Parsing:**
   - SyntaxError → Return validity=0.0 (handled in validate_syntax)

---

## Performance Considerations

### Bottlenecks
1. **Model inference:** 7B parameters, k=5 beams → 5x slower than greedy
2. **AST parsing:** Per-candidate validation

### Optimizations
- **Not needed for PoC** — targets already lenient (30 min, 50ms)
- If needed: batch AST parsing, cache tokenizer outputs

---

## Dependencies on Other Modules

| This Module | Depends On |
|-------------|------------|
| beam_search.py | model_loader.py (model, tokenizer) |
| metrics.py | beam_search.py (candidates) |
| visualizations.py | metrics.py (gate_metrics) |
| run_poc.py | All modules |

**Dependency Graph:**
```
data_loader.py ─┐
                ├─→ run_poc.py
model_loader.py ┴

beam_search.py → metrics.py → visualizations.py → run_poc.py
```

---

**Document Status:** Ready for Configuration Design (Step 5 parallel)
