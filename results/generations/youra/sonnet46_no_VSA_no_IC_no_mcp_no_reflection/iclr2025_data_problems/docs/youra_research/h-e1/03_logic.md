# Logic Design: H-E1 — Corpus Curation Generalization Balance (EXISTENCE PoC)

**Date:** 2026-08-31
**Author:** yoon303@ust.ac.kr
**Hypothesis Type:** EXISTENCE (PoC)
**Budget:** 7 subtasks (E3: 3, E4: 4)

Applied: Fail-Fast Precondition pattern — all checks run before any GPU allocation.
Applied: Resume-Safe Evaluation pattern — skip re-running if results.json already exists on disk.

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field experiment — no existing codebase to analyze. Serena MCP skipped per green-field rule.
**Analyzed Path:** N/A
**Findings:** New implementation from scratch.

---

## lm-evaluation-harness Results JSON Structure (Reference)

```json
{
  "results": {
    "mmlu_abstract_algebra": {"acc,none": 0.31, "acc_stderr,none": 0.046},
    "mmlu_anatomy":          {"acc,none": 0.37, "acc_stderr,none": 0.041},
    "hellaswag":             {"acc,none": 0.63, "acc_norm,none": 0.79},
    "arc_easy":              {"acc,none": 0.72, "acc_norm,none": 0.74},
    "arc_challenge":         {"acc,none": 0.38, "acc_norm,none": 0.42}
  }
}
```

Key naming conventions:
- MMLU subjects: keys starting with `"mmlu_"` (57 total)
- Accuracy field: `"acc,none"` (not `"acc"`)
- ARC-Challenge uses `"acc_norm,none"` (length-normalized) for the primary metric

---

## E3: Evaluator Subtasks

### E3-L1: `build_lm_eval_cmd()`

**Signature:**
```python
def build_lm_eval_cmd(
    model_id: str,
    revision: str,
    output_dir: str,
    fewshot_map: dict[str, int],
    tasks: list[str],
    limit: int | None = None,
    batch_size: str = "auto",
) -> list[str]:
```

**Returns:** `list[str]` — argv list suitable for `subprocess.run(cmd, check=True)`

**Pseudo-code:**
```python
def build_lm_eval_cmd(model_id, revision, output_dir, fewshot_map, tasks, limit=None, batch_size="auto"):
    # lm-eval ≥0.4 requires per-task fewshot via --apply_chat_template or num_fewshot
    # For mixed fewshot (MMLU=5, HellaSwag=0, ARC=25) use comma-separated task groups
    # or pass each task separately; simplest: run all at once with --num_fewshot 0
    # and let task configs override (lm-eval task configs specify default n-shots).
    # CONFIRMED: lm-eval task configs for mmlu=5-shot, hellaswag=0-shot, arc=25-shot by default.
    cmd = [
        "lm_eval",
        "--model", "hf",
        "--model_args", f"pretrained={model_id},revision={revision},dtype=float16",
        "--tasks", ",".join(tasks),
        "--batch_size", batch_size,
        "--output_path", output_dir,
        "--log_samples",
    ]
    if limit is not None:
        cmd += ["--limit", str(limit)]
    return cmd
```

**Edge cases:**
- `revision=""` → will pass empty string to lm-eval which falls back to default branch; precondition_check.py must validate revision before this is called
- `tasks=[]` → lm-eval will error; caller must ensure non-empty list (guaranteed by config.py constant)
- `batch_size="auto"` uses VRAM-adaptive batching; fallback to `"1"` if OOM detected by caller

---

### E3-L2: `run_evaluation()`

**Signature:**
```python
def run_evaluation(
    model_id: str,
    revision: str,
    output_dir: str,
    fewshot_map: dict[str, int] = FEWSHOT_MAP,
    tasks: list[str] = TASKS,
    force_rerun: bool = False,
) -> pathlib.Path:
```

**Returns:** `pathlib.Path` — path to `results.json`

**Pseudo-code:**
```python
def run_evaluation(model_id, revision, output_dir, fewshot_map=FEWSHOT_MAP, tasks=TASKS, force_rerun=False):
    results_path = pathlib.Path(output_dir) / "results.json"
    
    # Resume-safe: skip if results already exist
    if results_path.exists() and not force_rerun:
        print(f"[SKIP] Results already exist at {results_path}")
        return results_path
    
    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
    cmd = build_lm_eval_cmd(model_id, revision, output_dir, fewshot_map, tasks)
    
    print(f"[EVAL] Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)  # raises CalledProcessError on non-zero exit
    
    # lm-eval may write to output_dir/<model_name>/<timestamp>/results.json
    # Search for the most recent results.json under output_dir
    candidates = sorted(pathlib.Path(output_dir).rglob("results.json"), key=lambda p: p.stat().st_mtime)
    if not candidates:
        raise FileNotFoundError(f"lm-eval completed but no results.json found under {output_dir}")
    return candidates[-1]
```

**Edge cases:**
- lm-eval writes results to a timestamped subdirectory; use `rglob` + sort-by-mtime to find the latest
- `subprocess.run` raises `CalledProcessError` on OOM; caller should catch and retry with `batch_size="1"`
- `force_rerun=True` skips the existence check (for re-running with different params)

---

### E3-L3: `load_results()`

**Signature:**
```python
def load_results(results_path: pathlib.Path) -> dict[str, dict]:
```

**Returns:** `dict` — `{"mmlu_abstract_algebra": {"acc,none": float, ...}, "hellaswag": {...}, ...}`

**Pseudo-code:**
```python
def load_results(results_path: pathlib.Path) -> dict:
    with open(results_path) as f:
        data = json.load(f)
    
    raw = data.get("results", {})
    if not raw:
        raise ValueError(f"No 'results' key in {results_path} — lm-eval may have failed silently")
    
    # Validate required keys are present
    required_non_mmlu = {"hellaswag", "arc_easy", "arc_challenge"}
    present = set(raw.keys())
    mmlu_keys = {k for k in present if k.startswith("mmlu_")}
    
    missing = required_non_mmlu - present
    if missing:
        raise KeyError(f"Missing expected task results: {missing}")
    if len(mmlu_keys) < 10:  # expect 57 subjects; <10 suggests partial run
        raise ValueError(f"Only {len(mmlu_keys)} MMLU subjects found (expected 57); partial evaluation?")
    
    return raw
```

**Edge cases:**
- Partial MMLU run (interrupted): `len(mmlu_keys) < 10` guard raises early rather than silently producing wrong ratio
- Key format `"acc,none"` not `"acc"`: downstream functions must use `"acc,none"` (documented in metrics.py)
- `"aggregate_metric_list"` key in some lm-eval versions: ignored; only `"results"` sub-dict is used

---

## E4: Metric Computer Subtasks

### E4-L1: `compute_ratio()`

**Signature:**
```python
def compute_ratio(results: dict[str, dict]) -> float:
```

**Returns:** `float` — `mean(MMLU subject acc) / HellaSwag acc`

**Pseudo-code:**
```python
def compute_ratio(results: dict) -> float:
    mmlu_keys = [k for k in results if k.startswith("mmlu_")]
    if not mmlu_keys:
        raise ValueError("No MMLU subject keys found in results")
    
    mmlu_accs = [results[k]["acc,none"] for k in mmlu_keys]
    mmlu_mean = np.mean(mmlu_accs)
    
    hellaswag_acc = results["hellaswag"]["acc,none"]
    if hellaswag_acc == 0.0:
        raise ZeroDivisionError("HellaSwag acc=0.0 — evaluation likely failed")
    
    return float(mmlu_mean / hellaswag_acc)
```

**Edge cases:**
- `hellaswag_acc == 0.0`: guard against ZeroDivision (would only occur on broken eval)
- MMLU key detection uses `startswith("mmlu_")` — robust to lm-eval adding new MMLU subtasks
- Returns `float` not `np.float64` for JSON serialization compatibility

---

### E4-L2: `bootstrap_ratio_diff()`

**Signature:**
```python
def bootstrap_ratio_diff(
    pythia_results: dict[str, dict],
    olmo_results: dict[str, dict],
    n: int = 1000,
    seed: int = 42,
) -> dict:
```

**Returns:**
```python
{
    "mean_diff": float,        # mean(olmo_ratio - pythia_ratio) across bootstrap samples
    "ci_95": [float, float],   # [2.5th percentile, 97.5th percentile]
    "p_value": float,          # one-sided: P(diff <= 0)
    "bootstrap_diffs": list[float],  # all 1000 diffs, for figure generation
}
```

**Pseudo-code:**
```python
def bootstrap_ratio_diff(pythia_results, olmo_results, n=1000, seed=42):
    rng = np.random.default_rng(seed)
    
    mmlu_keys = np.array([k for k in pythia_results if k.startswith("mmlu_")])
    # Verify both have same MMLU keys
    olmo_mmlu_keys = {k for k in olmo_results if k.startswith("mmlu_")}
    common_keys = [k for k in mmlu_keys if k in olmo_mmlu_keys]
    if len(common_keys) < 50:
        raise ValueError(f"Only {len(common_keys)} common MMLU keys between models")
    common_keys = np.array(common_keys)
    
    hellaswag_p = pythia_results["hellaswag"]["acc,none"]
    hellaswag_o = olmo_results["hellaswag"]["acc,none"]
    
    diffs = []
    for _ in range(n):
        sample_keys = rng.choice(common_keys, size=len(common_keys), replace=True)
        p_mmlu = np.mean([pythia_results[k]["acc,none"] for k in sample_keys])
        o_mmlu = np.mean([olmo_results[k]["acc,none"] for k in sample_keys])
        p_ratio = p_mmlu / hellaswag_p
        o_ratio = o_mmlu / hellaswag_o
        diffs.append(float(o_ratio - p_ratio))
    
    diffs_arr = np.array(diffs)
    return {
        "mean_diff": float(np.mean(diffs_arr)),
        "ci_95": [float(np.percentile(diffs_arr, 2.5)), float(np.percentile(diffs_arr, 97.5))],
        "p_value": float(np.mean(diffs_arr <= 0)),  # one-sided P(OLMo ratio ≤ Pythia ratio)
        "bootstrap_diffs": diffs,
    }
```

**Edge cases:**
- Use `np.random.default_rng(seed)` (Generator API) not legacy `np.random.seed()` for reproducibility across numpy versions
- HellaSwag acc is NOT resampled (it's a single point estimate); only MMLU subjects are resampled — this matches the hypothesis design
- `p_value = mean(diffs <= 0)` is one-sided; if all 1000 diffs > 0, p_value = 0.0 (report as p < 0.001)

---

### E4-L3: `cohens_d()`

**Signature:**
```python
def cohens_d(bootstrap_diffs: list[float]) -> float:
```

**Returns:** `float` — effect size d = mean(diffs) / std(diffs)

**Pseudo-code:**
```python
def cohens_d(bootstrap_diffs: list[float]) -> float:
    arr = np.array(bootstrap_diffs)
    std = np.std(arr, ddof=1)  # sample std
    if std == 0.0:
        return float("inf")  # all bootstrap samples identical — degenerate case
    return float(np.mean(arr) / std)
```

**Note:** This is bootstrap-based Cohen's d (mean/std of the difference distribution), not the classical two-sample d. Appropriate here because we have a bootstrap distribution of ratio differences, not two independent samples. Threshold d > 0.2 is a small effect size by convention (Cohen 1988).

---

### E4-L4: `evaluate_hypothesis()`

**Signature:**
```python
def evaluate_hypothesis(
    pythia_results: dict[str, dict],
    olmo_results: dict[str, dict],
    ratio_threshold: float = 0.02,
    p_threshold: float = 0.05,
    d_threshold: float = 0.2,
    arc_p_threshold: float = 0.10,
) -> dict:
```

**Returns:**
```python
{
    "pythia_ratio": float,
    "olmo_ratio": float,
    "ratio_diff": float,          # olmo_ratio - pythia_ratio (point estimate)
    "arc_delta_pythia": float,    # arc_challenge acc_norm - arc_easy acc
    "arc_delta_olmo": float,
    "bootstrap": dict,            # output of bootstrap_ratio_diff()
    "cohens_d": float,
    "primary_pass": bool,         # ratio_diff > threshold AND p < 0.05 AND d > 0.2
    "secondary_pass": bool,       # olmo_arc_delta > pythia_arc_delta
    "verdict": str,               # "CONFIRMED" | "FAILED"
    "evidence": str,              # human-readable summary
}
```

**Pseudo-code:**
```python
def evaluate_hypothesis(pythia_results, olmo_results,
                        ratio_threshold=0.02, p_threshold=0.05,
                        d_threshold=0.2, arc_p_threshold=0.10):
    p_ratio = compute_ratio(pythia_results)
    o_ratio = compute_ratio(olmo_results)
    ratio_diff = o_ratio - p_ratio

    p_arc = results["arc_challenge"]["acc_norm,none"] - results["arc_easy"]["acc,none"]  # pythia
    o_arc = olmo_results["arc_challenge"]["acc_norm,none"] - olmo_results["arc_easy"]["acc,none"]

    boot = bootstrap_ratio_diff(pythia_results, olmo_results)
    d = cohens_d(boot["bootstrap_diffs"])

    primary_pass = (
        boot["mean_diff"] > ratio_threshold
        and boot["p_value"] < p_threshold
        and d > d_threshold
    )
    secondary_pass = o_arc > p_arc

    verdict = "CONFIRMED" if primary_pass else "FAILED"

    evidence = (
        f"OLMo ratio={o_ratio:.4f}, Pythia ratio={p_ratio:.4f}, "
        f"diff={boot['mean_diff']:.4f} (95% CI [{boot['ci_95'][0]:.4f}, {boot['ci_95'][1]:.4f}]), "
        f"p={boot['p_value']:.4f}, d={d:.3f}. "
        f"Primary: {'PASS' if primary_pass else 'FAIL'}. "
        f"ARC delta: OLMo={o_arc:.4f}, Pythia={p_arc:.4f} ({'PASS' if secondary_pass else 'FAIL'})."
    )

    return {
        "pythia_ratio": p_ratio, "olmo_ratio": o_ratio, "ratio_diff": ratio_diff,
        "arc_delta_pythia": p_arc, "arc_delta_olmo": o_arc,
        "bootstrap": boot, "cohens_d": d,
        "primary_pass": primary_pass, "secondary_pass": secondary_pass,
        "verdict": verdict, "evidence": evidence,
    }
```

**Edge cases:**
- Uses `boot["mean_diff"]` (bootstrap mean) not raw `ratio_diff` for primary threshold comparison — more robust
- `arc_challenge` uses `acc_norm,none` (length-normalized), `arc_easy` uses `acc,none` — asymmetric but matches lm-eval convention and original papers

---

## Subtask Summary

| ID | Module | Function | Complexity contribution |
|----|--------|----------|------------------------|
| E3-L1 | evaluator.py | `build_lm_eval_cmd()` | CLI construction |
| E3-L2 | evaluator.py | `run_evaluation()` | Resume-safe subprocess |
| E3-L3 | evaluator.py | `load_results()` | JSON parsing + validation |
| E4-L1 | metrics.py | `compute_ratio()` | MMLU key detection + ratio |
| E4-L2 | metrics.py | `bootstrap_ratio_diff()` | Bootstrap CI (n=1000) |
| E4-L3 | metrics.py | `cohens_d()` | Effect size computation |
| E4-L4 | metrics.py | `evaluate_hypothesis()` | Aggregation + verdict |

**Total: 7 subtasks — within LIGHT budget allocation**
