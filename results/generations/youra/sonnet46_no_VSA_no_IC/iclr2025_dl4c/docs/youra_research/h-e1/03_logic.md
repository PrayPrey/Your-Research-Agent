# Logic Design: H-E1
# Frozen-Model Variance Profiling — API Signatures, Pseudo-code, Subtasks

**Hypothesis ID:** h-e1
**Generated:** 2026-08-21
**Phase:** 3 — Implementation Planning

Applied: single-script profiling pattern (agentpatterns.ai variance-based RL sample selection — run baseline k times, compute variance per sample, filter to high-variance subset)

---

## Codebase Analysis (Serena)

Green-field project — no existing codebase. Serena analysis skipped. No existing symbols, imports, or module patterns to discover. All APIs are designed from scratch based on PRD and Architecture specifications.

---

## Module: `code/profile_mbpp.py`

Single-file implementation. All functions defined at module level.

---

## API Signatures

### A-2: Data Loading

```python
def load_mbpp_train(dataset_id: str = "google-research-datasets/mbpp",
                    config: str = "full",
                    split: str = "train") -> datasets.Dataset:
    """
    Load MBPP training split from HuggingFace Hub.

    Returns:
        Dataset with fields: task_id (int), text (str), code (str), test_list (list[str])
    Raises:
        AssertionError: if len(dataset) != 374
    """

def format_mbpp_prompt(problem: dict) -> str:
    """
    Format MBPP problem dict as DeepSeek instruction prompt.

    Args:
        problem: dict with 'text' field (problem description)
    Returns:
        Formatted prompt string for chat-instruct model
    """
```

### A-3: Model Loading

```python
def load_frozen_model(model_id: str = "deepseek-ai/deepseek-coder-7b-instruct-v1.5",
                      torch_dtype: torch.dtype = torch.bfloat16,
                      device_map: str = "auto"
                      ) -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """
    Load DeepSeek-Coder-7B-Instruct in frozen inference mode.

    Returns:
        (model, tokenizer) — model.eval() called, no grad tracking
    Note:
        Sets model.eval(). Caller must use torch.no_grad() context.
    """
```

### A-4: Generation + Execution (subtasks A4-S1, A4-S2)

```python
def generate_one(model: AutoModelForCausalLM,
                 tokenizer: AutoTokenizer,
                 prompt: str,
                 seed: int,
                 max_new_tokens: int = 512,
                 temperature: float = 1.0,
                 top_p: float = 0.95) -> str:
    """
    Generate one completion from frozen model with fixed seed.

    Input tensor shape: [1, prompt_seq_len] (batch=1)
    Output tensor shape: [1, prompt_seq_len + generated_len]
    Returns:
        Generated text only (prompt stripped from output)
    Side effects:
        torch.manual_seed(seed) called before generation
    """

def execute_and_test(code_str: str,
                     test_cases: list[str],
                     timeout: int = 10) -> bool:
    """
    Execute generated code + test cases in subprocess sandbox.

    Args:
        code_str: Generated Python function as string
        test_cases: List of assertion strings from MBPP test_list
        timeout: Max seconds before TimeoutExpired → False
    Returns:
        True if subprocess returncode == 0 (all tests pass), else False
    Algorithm:
        1. Write code_str + "\n" + "\n".join(test_cases) to NamedTemporaryFile
        2. subprocess.run(["python", fname], timeout=timeout, capture_output=True)
        3. return result.returncode == 0
    Cleanup:
        os.unlink(fname) in finally block
    """
```

**Tensor shapes for A-4:**
```
prompt tokens:     [1, L_prompt]     where L_prompt ≈ 50-200 tokens
generated tokens:  [1, L_generated]  where L_generated ≤ max_new_tokens=512
attention mask:    [1, L_prompt]     all ones
output ids:        [1, L_prompt + L_generated]  sliced to [L_generated:] for decode
```

### A-5: Profiling Loop + Checkpoint (subtasks A5-S1, A5-S2)

```python
def profile_all_problems(model: AutoModelForCausalLM,
                         tokenizer: AutoTokenizer,
                         problems: datasets.Dataset,
                         k: int = 8,
                         checkpoint_every: int = 50,
                         results_dir: Path = Path("docs/youra_research/h-e1/results"),
                         seed_base: int = 42) -> dict[int, dict]:
    """
    Profile all MBPP problems: generate k completions each, compute p_i and variance_i.

    Args:
        problems: MBPP train split (374 problems)
        k: Number of i.i.d. completions per problem
        checkpoint_every: Save intermediate results every N problems
        seed_base: Base seed; per-completion seed = seed_base + problem_idx*k + completion_idx
    Returns:
        results: {task_id: {"p_i": float, "variance_i": float,
                            "pass_count": int, "k": int}}
    Resume logic:
        If results_dir/checkpoint_latest.json exists, load it and skip already-profiled task_ids
    """
```

**Pseudo-code for A-5:**
```
FUNCTION profile_all_problems(model, tokenizer, problems, k, checkpoint_every, results_dir, seed_base):
    results_dir.mkdir(parents=True, exist_ok=True)
    results = load_checkpoint(results_dir)  # {} if no checkpoint

    already_done = set(results.keys())
    remaining = [p for p in problems if p["task_id"] not in already_done]

    FOR problem_idx, problem IN enumerate(tqdm(remaining, desc="Profiling MBPP")):
        task_id = problem["task_id"]
        prompt = format_mbpp_prompt(problem)
        test_cases = problem["test_list"]
        pass_count = 0

        WITH torch.no_grad():
            FOR comp_idx IN range(k):
                seed = seed_base + problem_idx * k + comp_idx
                code_str = generate_one(model, tokenizer, prompt, seed)
                passed = execute_and_test(code_str, test_cases)
                pass_count += int(passed)

        p_i = pass_count / k
        variance_i = p_i * (1 - p_i)
        results[task_id] = {"p_i": p_i, "variance_i": variance_i,
                            "pass_count": pass_count, "k": k}

        IF (problem_idx + 1) % checkpoint_every == 0:
            save_checkpoint(results, results_dir / "checkpoint_latest.json")
            torch.cuda.empty_cache()

    RETURN results
```

### A-6: Gate + Output + Figures (subtasks A6-S1, A6-S2)

```python
def compute_gate(results: dict[int, dict],
                 variance_threshold: float = 0.1,
                 min_count: int = 50) -> tuple[bool, int, list[int]]:
    """
    Check MUST_WORK gate and select top-50 by variance.

    Returns:
        (gate_passed, count_above_threshold, top50_task_ids)
    where:
        gate_passed = count_above_threshold >= min_count
        top50_task_ids = task_ids sorted by variance_i desc, take [:50]
    """

def save_results(results: dict[int, dict],
                 top50_ids: list[int],
                 gate_result: bool,
                 metrics: dict,
                 output_path: Path) -> None:
    """
    Save full results JSON for downstream H-M1 use.

    Output schema:
        {
          "gate_passed": bool,
          "metrics": {"count_nonzero_variance": int, "mean_p_top50": float, ...},
          "top50_ids": list[int],
          "problems": {task_id: {"p_i", "variance_i", "pass_count", "k", "rank_by_variance"}}
        }
    """

def generate_figures(results: dict[int, dict],
                     top50_ids: list[int],
                     metrics: dict,
                     figures_dir: Path) -> None:
    """
    Generate 4 mandatory matplotlib figures.

    Figure 1 — fig1_gate_metrics.png:
        Bar chart: [count_nonzero_variance, threshold=50], [mean_p_top50, bounds=[0.25, 0.75]]
    Figure 2 — fig2_pass_rate_histogram.png:
        Histogram of p_i across 374 problems; shade [0.25, 0.75] zone green
    Figure 3 — fig3_variance_histogram.png:
        Histogram of variance_i=p_i*(1-p_i); vertical line at 0.1 threshold
    Figure 4 — fig4_top50_scatter.png:
        Scatter all 374 problems (x=rank_by_variance, y=p_i);
        top-50 in red, rest in gray; horizontal band [0.25, 0.75] shaded

    Saves all figures to figures_dir/fig{N}_*.png
    """

def main() -> None:
    """
    Entry point. Orchestrates full profiling pipeline.

    Exit codes:
        0 — gate passed (count_nonzero_variance >= 50)
        1 — gate failed
    """
```

---

## Subtask List (6 subtasks for A-4, A-5, A-6)

| ID | Parent Epic | Title | Description |
|----|-------------|-------|-------------|
| A4-S1 | A-4 | Implement `generate_one()` | Full implementation with seed management, token slicing, decode |
| A4-S2 | A-4 | Implement `execute_and_test()` | Subprocess sandbox with tempfile, timeout, cleanup |
| A5-S1 | A-5 | Implement profiling loop core | Per-problem k-completion loop with tqdm, pass_count accumulation |
| A5-S2 | A-5 | Implement checkpoint save/resume | load_checkpoint, save_checkpoint, resume logic from checkpoint_latest.json |
| A6-S1 | A-6 | Implement gate + results | compute_gate, select_top50, save_results JSON, sys.exit(0/1) |
| A6-S2 | A-6 | Implement generate_figures | All 4 matplotlib figures with proper labels, shading, threshold lines |

---

## Implementation Notes

### Seed Management
- Global seed: `torch.manual_seed(42)` at script start
- Per-completion: `torch.manual_seed(seed_base + problem_idx * k + comp_idx)`
- Ensures exact reproducibility of any individual completion

### Memory Management
- `torch.no_grad()` wraps all generation calls
- `torch.cuda.empty_cache()` every 50 problems
- Batch size 1 throughout (no batched generation)

### Code Extraction from Completion
```python
def extract_code(completion: str) -> str:
    """Extract Python code block from completion if markdown-fenced."""
    if "```python" in completion:
        return completion.split("```python")[1].split("```")[0].strip()
    elif "```" in completion:
        return completion.split("```")[1].split("```")[0].strip()
    return completion.strip()
```
