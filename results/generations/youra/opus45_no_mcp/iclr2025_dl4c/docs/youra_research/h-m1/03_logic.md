# Logic Specification: h-m1 (Gradient Concentration Analysis)

**Type:** MECHANISM — gradient analysis, no training
**Model:** CodeT5-large (770M, encoder-decoder)
**Base:** H-E1 (extends reward.py, data.py, model.py)

---

## Codebase Analysis (Serena)

**Project Type:** incremental
**Status:** Extends H-E1 with gradient tracking, reuses existing APIs
**Analyzed Path:** h-e1/code/
**Relevant Symbols:** classify_error, parse_traceback_line, compute_gated_reward, execute_code_safely

---

## A-1: Token-Line Mapping [Complexity: Medium, Budget: 3]

**Applied:** CodeT5 tokenizer + source line tracking

### API Signatures

```python
@dataclass
class TokenWithLine:
    token_id: int
    text: str
    line: int
    position: int  # position within line

def tokenize_with_lines(
    code: str,
    tokenizer: "AutoTokenizer",
) -> tuple[list[TokenWithLine], list[int]]:
    """
    Tokenize code and track which source line each token came from.
    
    Returns:
        - tokens: list of TokenWithLine objects
        - line_numbers: list[int] of length gen_len, mapping token idx -> line
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| code | str | Raw Python code |
| tokens | list, len=gen_len | gen_len <= 256 |
| line_numbers | [gen_len] | int, 1-indexed line numbers |

### Pseudo-code

```
1. Split code into lines
2. For each line:
   - Tokenize line with tokenizer
   - Record (token_id, text, line_num) for each token
3. Concatenate all tokens
4. Return tokens, line_number array
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | line_splitter | Split code preserving line boundaries |
| L-1-2 | per_line_tokenize | Tokenize each line, track offsets |
| L-1-3 | aggregate_mapping | Combine into single token list with line info |

---

## A-2: Gradient Extraction [Complexity: High, Budget: 4]

**Applied:** PyTorch autograd with per-token gradient tracking

### API Signatures

```python
def extract_token_gradients(
    model: "PolicyModel",
    input_ids: Tensor,       # [1, seq_len]
    reward: Tensor,          # [seq_len]
) -> Tensor:                 # [seq_len] gradient magnitudes
    """
    Compute |grad| per token position via backward pass.
    
    Note: Approximates per-token gradient via weighted policy loss.
    """
    ...

def aggregate_gradients_by_line(
    token_gradients: Tensor,   # [seq_len]
    token_lines: list[int],    # [seq_len]
) -> dict[int, float]:
    """
    Sum gradient magnitudes per source line.
    
    Returns: {line_num: sum(|grad|) for tokens on that line}
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, seq_len] | Tokenized code |
| logits | [1, seq_len, 32100] | Model output |
| reward | [seq_len] | Fine-grained reward from H-E1 |
| token_gradients | [seq_len] | |grad| per token |
| line_gradients | dict[int, float] | Aggregated by line |

### Pseudo-code

```
1. model.zero_grad()
2. logits = model(input_ids)
3. log_probs = logits.log_softmax(-1)
4. # Policy gradient approximation: grad = E[log_pi * R]
5. loss = -(log_probs.gather(-1, input_ids) * reward).sum()
6. loss.backward()
7. # Extract gradient from embedding layer (most interpretable)
8. emb_grad = model.get_input_embeddings().weight.grad
9. token_gradients = emb_grad[input_ids].norm(dim=-1)  # [seq_len]
10. return token_gradients
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | gradient_setup | Zero grads, enable grad tracking |
| L-2-2 | policy_loss | Weighted policy gradient loss |
| L-2-3 | gradient_extraction | Extract embedding gradients |
| L-2-4 | line_aggregation | Sum gradients per line |

---

## A-3: Concentration Metrics [Complexity: Medium, Budget: 3]

**Applied:** Standard statistical aggregation

### API Signatures

```python
def compute_concentration_metrics(
    line_gradients: dict[int, float],
    error_line: int,
) -> dict[str, float]:
    """
    Compute gradient concentration metrics.
    
    Returns:
        - error_line_gradient: mean |grad| at error line
        - other_line_gradient: mean |grad| at other lines
        - concentration_ratio: error / other
        - within_2_lines_pct: fraction of total gradient within ±2 lines
        - success: bool, both criteria met
    """
    ...

def analyze_single_sample(
    model: "PolicyModel",
    code: str,
    traceback: str,
    tokenizer: "AutoTokenizer",
    reward_fn: Callable,
) -> dict[str, float]:
    """
    Full analysis pipeline for one sample.
    """
    ...
```

### Pseudo-code

```
1. error_grad = line_gradients[error_line]
2. other_grads = [v for k, v in line_gradients.items() if k != error_line]
3. other_grad = mean(other_grads) if other_grads else 1e-8
4. ratio = error_grad / max(other_grad, 1e-8)

5. nearby_lines = {error_line-2, error_line-1, error_line, error_line+1, error_line+2}
6. nearby_grad = sum(line_gradients[l] for l in nearby_lines if l in line_gradients)
7. total_grad = sum(line_gradients.values())
8. within_2_pct = nearby_grad / max(total_grad, 1e-8)

9. success = (ratio > 1.0) and (within_2_pct > 0.80)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | concentration_ratio | error_line / other_lines gradient ratio |
| L-3-2 | within_lines_pct | Fraction of gradient within ±2 lines |
| L-3-3 | success_check | Combined criterion evaluation |

---

## A-4: Sample Collection [Complexity: Medium, Budget: 4]

**Applied:** Model generation + execution filtering

### API Signatures

```python
def generate_failing_samples(
    model: "PolicyModel",
    tokenizer: "AutoTokenizer",
    dataset: list[dict],
    n_samples: int = 500,
    error_type_filter: str | None = None,
) -> list[dict]:
    """
    Generate code samples that fail with parseable tracebacks.
    
    Returns list of:
        - code: str
        - traceback: str
        - error_type: 'U_line' | 'U_ignore'
        - error_line: int
        - problem_id: str
    """
    ...
```

### Pseudo-code

```
1. samples = []
2. for problem in dataset:
3.     if len(samples) >= n_samples: break
4.     code = model.generate(problem["prompt"])
5.     result, traceback = execute_code_safely(code, problem["tests"])
6.     if result in ["FAIL", "ERROR"] and traceback:
7.         error_line = parse_traceback_line(traceback)
8.         if error_line is None: continue
9.         error_type = classify_error(traceback)
10.        if error_type_filter and error_type != error_type_filter: continue
11.        samples.append({code, traceback, error_type, error_line, problem_id})
12. return samples
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | sample_generation | Model generation loop |
| L-4-2 | execution_filtering | Filter for failing samples |
| L-4-3 | traceback_validation | Ensure parseable error line |
| L-4-4 | error_type_stratification | Filter by U_line/U_ignore |

---

## A-5: Aggregate Analysis [Complexity: Medium, Budget: 3]

**Applied:** Statistical aggregation + confidence intervals

### API Signatures

```python
def run_full_analysis(
    model: "PolicyModel",
    samples: list[dict],
    reward_fn: Callable,
    tokenizer: "AutoTokenizer",
) -> dict[str, Any]:
    """
    Run gradient analysis across all samples.
    
    Returns:
        - n_samples: int
        - mean_concentration_ratio: float
        - std_concentration_ratio: float
        - ci_95_ratio: tuple[float, float]
        - mean_within_2_lines_pct: float
        - std_within_2_lines_pct: float
        - ci_95_within: tuple[float, float]
        - success_rate: float
        - primary_criterion_met: bool
        - secondary_criterion_met: bool
        - t_stat: float
        - p_value: float
        - per_sample_results: list[dict]
    """
    ...

def run_stratified_analysis(
    model: "PolicyModel",
    samples: list[dict],
    reward_fn: Callable,
    tokenizer: "AutoTokenizer",
) -> dict[str, dict]:
    """
    Run analysis stratified by error type.
    
    Returns: {
        "all": full_results,
        "u_line": u_line_results,
        "u_ignore": u_ignore_results,
        "random": random_baseline_results,
    }
    """
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | sample_loop | Iterate analyze_single_sample over all samples |
| L-5-2 | stats_aggregation | Mean, std, CI, t-test |
| L-5-3 | stratified_grouping | Group by error type and re-analyze |

---

## A-6: Visualization [Complexity: Low, Budget: 2]

**Applied:** matplotlib for all figures

### API Signatures

```python
def plot_gradient_comparison(
    error_grad: float,
    other_grad: float,
    out_path: str,
) -> None:
    """Required figure: bar chart of error-line vs other-lines gradient."""
    ...

def plot_concentration_histogram(
    ratios: list[float],
    threshold: float = 1.0,
    out_path: str,
) -> None:
    """Distribution of concentration ratios, vertical line at threshold."""
    ...

def plot_line_gradient_heatmap(
    samples: list[tuple[dict[int, float], int]],  # (line_gradients, error_line)
    out_path: str,
) -> None:
    """Heatmap with error line centered, shows gradient spread."""
    ...

def plot_error_type_comparison(
    u_line_ratio: float,
    u_ignore_ratio: float,
    random_ratio: float,
    out_path: str,
) -> None:
    """Bar chart comparing concentration by error type."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | core_figures | gradient_comparison (required) + histogram |
| L-6-2 | analysis_figures | heatmap + error_type comparison |

---

## A-7: Main Runner [Complexity: Low, Budget: 2]

**Applied:** Orchestration script

### API Signatures

```python
def main() -> dict:
    """
    Entry point for H-M1 gradient concentration analysis.
    
    Steps:
        1. Load model and tokenizer
        2. Load APPS dataset
        3. Generate 500 failing samples
        4. Run stratified gradient analysis
        5. Generate visualizations
        6. Write results and verdict
    
    Returns:
        - verdict: "PASS" | "FAIL"
        - results: full analysis dict
    """
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | orchestration | Load models, call analysis functions |
| L-7-2 | verdict_output | Write results JSON, return PASS/FAIL |
