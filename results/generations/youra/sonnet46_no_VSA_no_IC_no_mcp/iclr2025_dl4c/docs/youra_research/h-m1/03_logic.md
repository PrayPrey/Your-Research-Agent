---
title: "Logic: H-M1 — SFT Signal Void at Hard Difficulty"
hypothesis_id: H-M1
hypothesis_type: MECHANISM
tier: FULL
date: "2026-08-26"
author: yoon303@ust.ac.kr
---

Applied: Flat-script pattern (one file per concern, no shared base classes)
Applied: Subprocess-sandboxed execution pattern (no in-process exec, ulimit recommended)
Applied: Results-file decoupling pattern (each script reads/writes JSON independently)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1 extends H-E1)
**Status**: H-E1 is green-field (Phase 4 not yet materialized) — architecture spec used as source of truth
**Analyzed Path**: `docs/youra_research/h-e1/03_architecture.md`
**Relevant Symbols**:
- `run_harness(checkpoint_path, task, output_path)` — shell-out pattern reused by `analyze_sft_lcb.py`
- `_execute_code(code, stdin, timeout)` — subprocess execution pattern reused by `check_apps_coverage.py`

H-M1 does NOT import H-E1 Python modules. It reuses the shell-out pattern and subprocess execution pattern by copying the idiom, not by importing.

---

## External Dependencies API (Base Hypothesis H-E1)

Patterns verified from `docs/youra_research/h-e1/03_architecture.md`:

```python
# From: h-e1/code/evaluate.py (shell-out pattern — copy idiom, do not import)
def run_harness(checkpoint_path: str, task: str, output_path: str) -> dict:
    """Shells out to bigcode-evaluation-harness. Returns parsed JSON results."""
    # subprocess.run(["accelerate", "launch", "main.py", "--model", checkpoint_path,
    #                 "--tasks", task, "--metric_output_path", output_path, ...])
    ...

# From: h-e1/code/reward.py (subprocess execution pattern — copy idiom)
def _execute_code(code: str, stdin: str, timeout: float = 3.0) -> str:
    """Subprocess execution. Raises subprocess.TimeoutExpired on timeout."""
    ...
```

**Verified from**: `docs/youra_research/h-e1/03_architecture.md` (actual code not yet written; spec is source of truth)

---

## A-M1-3: APPS Loss Stratification [Complexity: 12, Budget: 2 subtasks]

Applied: Forward-pass-only eval pattern (model.eval(), torch.no_grad(), no gradient updates)

### API Signatures

```python
# analyze_sft_loss.py

def load_model_and_tokenizer(
    checkpoint_path: str,
    device: str = "cuda",
) -> tuple:
    """Load model in eval mode. Returns (model, tokenizer)."""
    ...

def compute_per_example_loss(
    model,                        # AutoModelForCausalLM, already in eval mode
    tokenizer,                    # AutoTokenizer
    example: dict,                # APPS dataset row: {"problem": str, "solutions": str (JSON), "difficulty": str}
    max_length: int = 2048,
    device: str = "cuda",
) -> float:
    """Forward pass on one APPS example. Returns scalar cross-entropy loss (nats).
    Returns None if example["solutions"] is empty or unparseable."""
    ...

def compute_difficulty_stratified_loss(
    checkpoint_path: str,
    dataset_name: str = "codeparrot/apps",
    split: str = "train",
    output_path: str = "results/h-m1/apps_difficulty_loss.json",
    max_examples_per_bucket: int = 500,
    device: str = "cuda",
) -> dict:
    """Stratified loss computation. Returns full results dict (also written to output_path)."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, T] | T <= max_length=2048; single example, batch=1 |
| labels | [1, T] | problem tokens masked to -100; loss computed on solution tokens only |
| loss (per token) | scalar | mean CE loss over unmasked (solution) tokens, in nats |

### Pseudo-code: compute_per_example_loss

```
1. Parse solutions JSON: solns = json.loads(example["solutions"])
   - If solns is empty list or parse fails: return None

2. Use first solution: solution_str = solns[0]

3. Build prompt: text = example["problem"] + "\n" + solution_str

4. Tokenize: enc = tokenizer(text, max_length=2048, truncation=True, return_tensors="pt")
   # Truncation from right (default). input_ids: [1, T], T <= 2048.

5. Build labels: labels = enc["input_ids"].clone()
   # Find boundary: problem_len = len(tokenizer(example["problem"])["input_ids"])
   # Clamp to T if problem_len >= T (entire input is problem, no solution tokens → return None)
   # labels[:, :problem_len] = -100   # mask problem tokens

6. Forward (no_grad):
   with torch.no_grad():
       out = model(**enc, labels=labels)
   return out.loss.item()   # scalar float
```

### Pseudo-code: compute_difficulty_stratified_loss

```
1. model, tokenizer = load_model_and_tokenizer(checkpoint_path, device)
2. ds = load_dataset(dataset_name, split=split)
3. buckets = {"introductory": [], "interview": [], "competition": []}

4. for example in tqdm(ds):
       diff = example["difficulty"]
       if diff not in buckets: continue
       if len(buckets[diff]) >= max_examples_per_bucket: continue
       # ponytail: global cap per bucket; per-bucket stratified sampling if class imbalance matters
       loss = compute_per_example_loss(model, tokenizer, example, device=device)
       if loss is not None:
           buckets[diff].append(loss)

5. results = {}
   for diff, losses in buckets.items():
       arr = np.array(losses)
       results[diff] = {"mean": float(arr.mean()), "std": float(arr.std()), "count": len(arr)}

6. json.dump(results, open(output_path, "w"), indent=2)
7. return results
```

### Output JSON Schema

```json
{
  "introductory": {"mean": 1.23, "std": 0.45, "count": 500},
  "interview":    {"mean": 1.89, "std": 0.61, "count": 500},
  "competition":  {"mean": 2.74, "std": 0.88, "count": 312}
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M1-3-1 | compute_per_example_loss | Tokenize, mask problem tokens, forward pass, return scalar loss or None |
| L-M1-3-2 | compute_difficulty_stratified_loss | Stratification loop, bucket aggregation, JSON output |

---

## A-M1-4: APPS Coverage Check [Complexity: 11, Budget: 2 subtasks]

Applied: Subprocess-sandboxed execution pattern (no exec(), stdin injection, stdout capture)

### API Signatures

```python
# check_apps_coverage.py

def check_solution_passes(
    solution: str,              # Python source code string
    test_cases: list[dict],     # [{"input": str, "output": str}, ...]
    timeout: float = 5.0,
) -> bool:
    """Execute solution against all test cases in subprocess.
    Returns True iff ALL test cases pass. Returns False on any failure or timeout."""
    ...

def compute_coverage(
    dataset_name: str = "codeparrot/apps",
    difficulty: str = "competition",
    output_path: str = "results/h-m1/apps_hard_coverage.json",
    max_problems: int = None,   # None = full split (~600 competition problems)
) -> dict:
    """Per-problem: solvable if ANY reference solution passes ALL test cases.
    Returns coverage dict (also written to output_path)."""
    ...
```

### Pseudo-code: check_solution_passes

```
1. Write solution to tmp file: f = tempfile.NamedTemporaryFile(suffix=".py", delete=False)

2. for tc in test_cases:
       try:
           proc = subprocess.run(
               ["python", f.name],
               input=tc["input"],
               capture_output=True,
               text=True,
               timeout=timeout,
               # ponytail: ulimit via preexec_fn=set_limits recommended for sandboxing
           )
           if proc.returncode != 0: return False
           if proc.stdout.strip() != tc["output"].strip(): return False
       except subprocess.TimeoutExpired:
           return False
       except Exception:
           return False

3. return True
```

### Pseudo-code: compute_coverage

```
1. ds = load_dataset(dataset_name, split="train")
   problems = [ex for ex in ds if ex["difficulty"] == difficulty]
   if max_problems: problems = problems[:max_problems]
   # Full competition split ~600 problems — manageable, no sampling needed
   # ponytail: global cap via max_problems; stratified sampling if split size grows

2. solvable = 0
   for problem in tqdm(problems):
       solns = json.loads(problem.get("solutions", "[]") or "[]")
       tests = json.loads(problem.get("input_output", "{}") or "{}")
       # test_cases: zip(tests.get("inputs",[]), tests.get("outputs",[]))
       test_cases = [{"input": i, "output": o}
                     for i, o in zip(tests.get("inputs", []), tests.get("outputs", []))]

       if not solns or not test_cases:
           continue   # no solution or no test cases: not solvable

       problem_solvable = False
       for soln in solns:
           if check_solution_passes(soln, test_cases):
               problem_solvable = True
               break   # ANY solution passing is enough
       if problem_solvable:
           solvable += 1

3. total = len(problems)
   coverage_pct = round(solvable / total * 100, 2) if total > 0 else 0.0
   result = {
       "difficulty": difficulty,
       "total": total,
       "solvable": solvable,
       "coverage_pct": coverage_pct,
   }
   json.dump(result, open(output_path, "w"), indent=2)
   return result
```

### Output JSON Schema

```json
{
  "difficulty": "competition",
  "total": 600,
  "solvable": 46,
  "coverage_pct": 7.67
}
```

### Edge Cases

| Case | Handling |
|------|---------|
| `example["solutions"]` is `"[]"` or `""` | `json.loads` → `[]`, skip problem (not solvable) |
| `example["input_output"]` missing/empty | No test cases, skip problem |
| subprocess.TimeoutExpired | `check_solution_passes` returns False |
| solution crashes (non-zero returncode) | Returns False |
| output trailing whitespace | `.strip()` comparison |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M1-4-1 | check_solution_passes | Subprocess execution, stdin injection, timeout → False, all-tests-pass check |
| L-M1-4-2 | compute_coverage | Full competition split scan, any-solution-passes logic, JSON output |
