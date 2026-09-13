# Logic: h-e1 Prescreening Validation

**Hypothesis:** h-e1 (EXISTENCE)
**Generated:** 2026-03-15

Applied: subprocess-sandbox-with-timeout, batched-inference-pipeline, fail-early-validation

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - no existing code to analyze
**Analyzed Path:** N/A — `h-e1/code/` does not exist yet
**Relevant Symbols:** None - new implementation

---

## E-4: Inference Pipeline [Complexity: 13, Budget: 2 subtasks]

### API Signatures

```python
# prescreening.py

def load_model(
    sft_checkpoint_path: str,
    base_model_id: str = "Qwen/Qwen2.5-Coder-7B-Instruct",
    dtype: torch.dtype = torch.bfloat16,
) -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Load SFT checkpoint or fallback to base model."""
    ...

def generate_rollouts(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    problems: list[dict],
    k: int = 8,
    temperature: float = 0.8,
    max_new_tokens: int = 1024,
    batch_size: int = 4,
    seed: int = 42,
) -> dict[int, list[str]]:
    """Generate k rollouts per problem. Returns {problem_id: [code_0, ..., code_k-1]}."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [batch_size * k, seq_len] | problems replicated k times |
| attention_mask | [batch_size * k, seq_len] | padding mask, right-pad |
| generated_ids | [batch_size * k, seq_len + max_new_tokens] | full sequence |
| new_tokens | [batch_size * k, max_new_tokens] | sliced from generated_ids |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Batched Rollout Generation | `generate_rollouts()` batching strategy, tokenization, decode |
| L-4-2 | Model Loading with SFT Fallback | `load_model()` path check, bfloat16, device_map="auto" |

---

## L-4-1: Batched Rollout Generation

### API Signature

```python
def generate_rollouts(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    problems: list[dict],        # each: {problem_id: int, prompt: str, test_cases: list, T: int}
    k: int = 8,
    temperature: float = 0.8,
    max_new_tokens: int = 1024,
    batch_size: int = 4,
    seed: int = 42,
) -> dict[int, list[str]]:       # {problem_id: [rollout_0, ..., rollout_{k-1}]}
    ...
```

### Tensor Shapes

```
# For one micro-batch of B problems × k rollouts:
# input_ids:       [B*k, seq_len]   — each problem prompt repeated k times
# attention_mask:  [B*k, seq_len]   — 1 for real tokens, 0 for left-padding
# generated_ids:   [B*k, seq_len + max_new_tokens]
# decoded:         list of length B*k strings, then reshaped to [B, k]
```

### Pseudo-code

```
torch.manual_seed(seed)
results = {}

for batch_start in range(0, len(problems), batch_size):
    batch = problems[batch_start : batch_start + batch_size]  # up to B problems

    # Replicate each problem k times
    prompts = [apply_chat_template(p["prompt"]) for p in batch for _ in range(k)]
    # len(prompts) == B*k

    inputs = tokenizer(
        prompts,
        return_tensors="pt",
        padding=True,          # right-pad to longest in batch
        truncation=True,
        max_length=2048,
    ).to(model.device)
    # input_ids: [B*k, seq_len]

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=temperature,
            pad_token_id=tokenizer.eos_token_id,
        )
    # output_ids: [B*k, seq_len + new_tokens]

    # Slice only newly generated tokens
    new_ids = output_ids[:, inputs["input_ids"].shape[1]:]
    decoded = tokenizer.batch_decode(new_ids, skip_special_tokens=True)
    # decoded: list of B*k strings

    # Reshape to [B, k] and store
    for i, prob in enumerate(batch):
        results[prob["problem_id"]] = decoded[i*k : (i+1)*k]

return results  # {problem_id: [k strings]}
```

---

## L-4-2: Model Loading with SFT Fallback

### API Signature

```python
def load_model(
    sft_checkpoint_path: str,
    base_model_id: str = "Qwen/Qwen2.5-Coder-7B-Instruct",
    dtype: torch.dtype = torch.bfloat16,
) -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    """Check sft_checkpoint_path; load SFT if present, else load base with warning."""
    ...
```

### Pseudo-code

```
if os.path.isdir(sft_checkpoint_path) and len(os.listdir(sft_checkpoint_path)) > 0:
    model_path = sft_checkpoint_path
    logger.info(f"Loading SFT checkpoint from {model_path}")
else:
    model_path = base_model_id
    logger.warning(f"SFT checkpoint not found at {sft_checkpoint_path}. Falling back to {base_model_id}")

model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=dtype,
    device_map="auto",
)
tokenizer = AutoTokenizer.from_pretrained(model_path, padding_side="right")
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model.eval()
return model, tokenizer
```

---

## E-2: Execution Sandbox [Complexity: 11, Budget: 1 subtask]

### API Signatures

```python
# execution_sandbox.py

def execute_code(
    code: str,
    stdin: str,
    timeout: float = 5.0,
) -> tuple[str, bool]:
    """Write code to tempfile, run with subprocess, inject stdin. Returns (stdout, success)."""
    ...

def run_against_test_cases(
    code: str,
    test_cases: list[dict],    # each: {input: str, output: str}
    timeout: float = 5.0,
) -> int:
    """Run code against all test cases. Returns tests_passed count in [0, T]."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Subprocess Execution Harness | execute_code + run_against_test_cases with timeout, stdin injection, error handling |

---

## L-2-1: Subprocess Execution Harness

### execute_code Pseudo-code

```
def execute_code(code, stdin, timeout=5.0) -> tuple[str, bool]:
    try:
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write(code)
            tmp_path = f.name

        result = subprocess.run(
            ["python3", tmp_path],
            input=stdin,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        stdout = result.stdout
        success = (result.returncode == 0)
        return stdout, success

    except subprocess.TimeoutExpired:
        return "", False
    except OSError:
        return "", False
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
```

### run_against_test_cases Pseudo-code

```
def run_against_test_cases(code, test_cases, timeout=5.0) -> int:
    tests_passed = 0
    for tc in test_cases:
        stdin_str = tc["input"]
        expected = tc["output"].strip()
        try:
            stdout, success = execute_code(code, stdin=stdin_str, timeout=timeout)
            if success and stdout.strip() == expected:
                tests_passed += 1
        except Exception:
            pass  # any unhandled error counts as failure; continue
    return tests_passed
```

### Error Handling Table

| Error Type | execute_code behavior | tests_passed contribution |
|------------|----------------------|--------------------------|
| TimeoutExpired | return ("", False) | 0 |
| SyntaxError / RuntimeError | returncode != 0 | 0 |
| OSError (file write) | return ("", False) | 0 |
| Wrong output | stdout.strip() != expected | 0 |
| Correct output | stdout.strip() == expected | +1 |

---

## E-5: Gate Metric Evaluation [Complexity: 10, Budget: 1 subtask]

### API Signatures

```python
# evaluate.py

def compute_variance_ratio_per_group(
    r_ratio_vec: list[float],   # length k=8, values in [0, 1]
    r_binary_vec: list[float],  # length k=8, values in {0.0, 1.0}
) -> float | None:
    """Compute var(r_ratio) / var(r_binary). Returns None if var_binary <= 1e-8."""
    ...

def compute_gate_metrics(
    per_problem_results: list[dict],
    threshold_pass_ge1: float = 0.10,
    threshold_pct_above: float = 0.80,
    variance_ratio_threshold: float = 1.5,
) -> dict:
    """Aggregate per-problem stats into gate metrics dict."""
    ...

def check_gate(metrics: dict) -> tuple[bool, str]:
    """Return (gate_pass, message) based on threshold checks."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Variance Ratio Computation | compute_gate_metrics + compute_variance_ratio_per_group with division guard |

---

## L-5-1: Variance Ratio Computation

### compute_variance_ratio_per_group Pseudo-code

```
def compute_variance_ratio_per_group(r_ratio_vec, r_binary_vec) -> float | None:
    arr_ratio  = np.array(r_ratio_vec,  dtype=np.float64)   # [k]
    arr_binary = np.array(r_binary_vec, dtype=np.float64)   # [k]

    var_ratio  = np.var(arr_ratio)    # scalar, ddof=0 (population variance)
    var_binary = np.var(arr_binary)   # scalar

    if var_binary <= 1e-8:
        return None   # degenerate group (all-pass or all-fail): excluded from pct computation

    return float(var_ratio / var_binary)
```

### compute_gate_metrics Pseudo-code

```
def compute_gate_metrics(per_problem_results, ...) -> dict:
    # per_problem_results: list of dicts with keys:
    #   problem_id, s_term, r_ratio_vec [k], r_binary_vec [k], tests_passed_vec [k], T

    fraction_k_pass_ge1_list = []   # bool per problem: any(r_binary > 0)
    variance_ratios = []            # float per non-degenerate group

    for row in per_problem_results:
        r_ratio_vec  = row["r_ratio_vec"]    # list[float], len=k
        r_binary_vec = row["r_binary_vec"]   # list[float], len=k

        # Metric (a): at least one partial pass
        k_pass_ge1 = float(any(tp >= 1 for tp in row["tests_passed_vec"]))
        fraction_k_pass_ge1_list.append(k_pass_ge1)

        # Metric (b): variance ratio
        vr = compute_variance_ratio_per_group(r_ratio_vec, r_binary_vec)
        if vr is not None:
            variance_ratios.append(vr)

    fraction_k_pass_ge1 = float(np.mean(fraction_k_pass_ge1_list))
    mean_var_ratio       = float(np.mean(variance_ratios)) if variance_ratios else 0.0
    pct_groups_above_1_5x = float(
        np.mean([vr >= variance_ratio_threshold for vr in variance_ratios])
    ) if variance_ratios else 0.0

    gate_pass = (
        fraction_k_pass_ge1 >= threshold_pass_ge1
        and pct_groups_above_1_5x >= threshold_pct_above
    )

    return {
        "fraction_k_pass_ge1": fraction_k_pass_ge1,
        "mean_var_ratio": mean_var_ratio,
        "pct_groups_above_1_5x": pct_groups_above_1_5x,
        "gate_pass": gate_pass,
        "n_problems": len(per_problem_results),
        "n_non_degenerate_groups": len(variance_ratios),
    }
```

**Statistical note:** With k=8 rollouts, variance estimates are noisy (chi-squared with df=7). Expect ±0.15 standard error on pct_groups_above_1_5x for N=200 problems. The gate threshold of 0.80 provides ~2σ margin above chance.

---

## Main Orchestration: prescreening.py

### Complete Pseudo-code

```
def main(seed: int = 42, batch_size: int = 4) -> None:
    setup_logging()
    torch.manual_seed(seed)

    # --- Resume logic ---
    results_dir = "h-e1/results"
    os.makedirs(results_dir, exist_ok=True)
    os.makedirs("h-e1/figures", exist_ok=True)

    per_problem_csv = os.path.join(results_dir, "per_problem_results.csv")
    processed_ids: set[int] = set()
    existing_results: list[dict] = []

    if os.path.exists(per_problem_csv):
        existing_df = pd.read_csv(per_problem_csv)
        processed_ids = set(existing_df["problem_id"].tolist())
        existing_results = existing_df.to_dict("records")
        logger.info(f"Resume: skipping {len(processed_ids)} already-processed problems")

    # --- Data loading ---
    problems_all = load_apps_introductory(min_test_cases=3)
    if len(problems_all) < 50:
        raise RuntimeError(f"FAIL EARLY: T>=3 filter yielded only {len(problems_all)} problems (need >=50)")

    remaining = [p for p in problems_all if p["problem_id"] not in processed_ids]
    logger.info(f"Problems to process: {len(remaining)} / {len(problems_all)}")

    # --- Model loading ---
    sft_path = os.path.join(os.path.dirname(__file__), "sft_checkpoint")
    model, tokenizer = load_model(sft_checkpoint_path=sft_path)

    # --- Inference ---
    rollouts = generate_rollouts(
        model, tokenizer, remaining,
        k=8, temperature=0.8, max_new_tokens=1024,
        batch_size=batch_size, seed=seed,
    )

    # --- Per-problem evaluation ---
    new_results: list[dict] = []
    for prob in tqdm(remaining, desc="Evaluating rollouts"):
        pid = prob["problem_id"]
        codes = rollouts[pid]                          # list of k strings
        tests_passed_vec = [
            run_against_test_cases(code, prob["test_cases"], timeout=5.0)
            for code in codes
        ]                                              # list[int], len=k
        T = prob["T"]
        r_ratio_vec  = [compute_r_ratio(tp, T)  for tp in tests_passed_vec]
        r_binary_vec = [compute_r_binary(tp, T) for tp in tests_passed_vec]
        s_term       = compute_s_term(codes, prob["test_cases"])

        new_results.append({
            "problem_id":       pid,
            "s_term":           s_term,
            "T":                T,
            "r_ratio_vec":      r_ratio_vec,
            "r_binary_vec":     r_binary_vec,
            "tests_passed_vec": tests_passed_vec,
        })

        # Intermediate logging every 100 problems
        if len(new_results) % 100 == 0:
            logger.info(f"Processed {len(new_results)} problems ...")

    # Persist incremental results
    all_results = existing_results + new_results
    pd.DataFrame(all_results).to_csv(per_problem_csv, index=False)

    # --- S_term prescreening filter ---
    prescreened = [r for r in all_results if 0.3 <= r["s_term"] <= 0.55]
    logger.info(f"Prescreened: {len(prescreened)} / {len(all_results)} problems (S_term in [0.3, 0.55])")
    if len(prescreened) < 50:
        raise RuntimeError(f"FAIL EARLY: prescreened subset has only {len(prescreened)} problems")

    # --- Gate metrics ---
    metrics = compute_gate_metrics(prescreened)
    gate_pass, gate_msg = check_gate(metrics)
    logger.info(f"Gate result: {gate_msg}")

    # --- Persist gate metrics ---
    with open(os.path.join(results_dir, "gate_metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    # --- Visualization ---
    generate_all_figures(
        metrics=metrics,
        per_problem_results=prescreened,
        figures_dir="h-e1/figures",
    )

    logger.info("Prescreening complete.")
    sys.exit(0 if gate_pass else 1)
```

---

## Results Serialization Format

### gate_metrics.json

```json
{
  "fraction_k_pass_ge1": 0.42,
  "mean_var_ratio": 2.1,
  "pct_groups_above_1_5x": 0.87,
  "gate_pass": true,
  "n_problems": 312,
  "n_non_degenerate_groups": 289
}
```

### per_problem_results.csv columns

| Column | Type | Description |
|--------|------|-------------|
| problem_id | int | APPS problem index |
| s_term | float | fraction of rollouts with tests_passed >= 1 |
| T | int | number of test cases |
| r_ratio_vec | str | JSON-encoded list[float] length k |
| r_binary_vec | str | JSON-encoded list[float] length k |
| tests_passed_vec | str | JSON-encoded list[int] length k |

**Note:** list columns stored as JSON strings in CSV; deserialize with `json.loads()` on read.

---

*Logic document generated for Phase 4 Coder.*
*Source: 03_architecture.md + 03_prd.md*
