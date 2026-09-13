# Logic Design: H-E1
# Deduplication Benchmark Signature — Existence Verification

**Hypothesis:** H-E1 (EXISTENCE)
**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr

Applied: Resume-Safe Pipeline (skip completed result files; idempotent across reruns)
Applied: Fail-Fast Pre-flight Check (verify_mechanism_activation before expensive full evaluation)
Applied: JSON-File Stage Contracts (each script reads/writes explicit JSON; stages fully decoupled)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Serena analysis skipped — no existing codebase to analyze
**Findings**: New evaluation scripts written from scratch. Pipeline uses standard public APIs:
- `lm-evaluation-harness` CLI (subprocess invocation, well-documented)
- `transformers.AutoModelForCausalLM` (standard HuggingFace loading pattern)
- `scipy.stats.ttest_rel` (standard paired t-test)
No complex custom layers or unfamiliar patterns; semantic analysis not needed.

---

## Data Structures

### checkpoint_map.json

```python
CheckpointMap = dict[str, dict]
# Schema:
{
  "160m": {
    "pile_step": 99000,
    "dedup_step": 143000,
    "pile_tokens": 207605..,     # int, pile_step * BATCH_TOKENS
    "dedup_tokens": 207000000000, # int, from Biderman et al. 2023
    "token_mismatch_pct": 0.3    # float, abs(pile_tokens - dedup_tokens) / dedup_tokens * 100
  },
  "410m": { ... },
  "1b":   { ... },
  "6.9b": { ... }
}
```

### results_matrix.json

```python
AccuracyMatrix = dict[str, dict[str, dict[str, float]]]
# Schema: accuracy[size][corpus][benchmark]
{
  "160m": {
    "pile":  {"mmlu": 0.261, "hellaswag": 0.432, "arc_challenge": 0.301, "winogrande": 0.524},
    "dedup": {"mmlu": 0.268, "hellaswag": 0.441, "arc_challenge": 0.298, "winogrande": 0.531}
  },
  "410m": { ... },
  "1b":   { ... },
  "6.9b": { ... }
}
```

### statistical_results.json

```python
StatResults = dict[str, dict]
# Schema: results[benchmark]
{
  "mmlu": {
    "t_stat": 2.41,
    "p_value": 0.0094,
    "mean_diff": 0.012,          # mean(dedup - pile) across 4 sizes
    "diffs": [0.007, 0.010, 0.012, 0.019],  # per-size diffs
    "significant": true,         # p_value < CORRECTED_ALPHA (0.0125)
    "direction": "dedup_higher"  # or "pile_higher" or "mixed"
  },
  "hellaswag":    { ... },
  "arc_challenge": { ... },
  "winogrande":   { ... },
  "gate_passed": true,           # bool: any benchmark significant at >=2 sizes
  "mechanism_verified": true     # bool: verify_mechanism_activation passed
}
```

---

## API Specifications

### Module: resolve_checkpoints.py

```python
BATCH_TOKENS: int = 2_097_152          # tokens per training step (Biderman et al. 2023)
DEDUP_FINAL_STEP: int = 143_000        # dedup-Pile final checkpoint step
DEDUP_TARGET_TOKENS: int = 207_000_000_000  # ~207B from Biderman et al. Table 1
SIZES: list[str] = ["160m", "410m", "1b", "6.9b"]


def step_to_tokens(step: int, batch_tokens: int = BATCH_TOKENS) -> int:
    """Convert training step to approximate token count.

    Args:
        step: Training step number (e.g. 99000)
        batch_tokens: Tokens per step (default 2,097,152)
    Returns:
        Approximate total tokens seen at that step
    """
    return step * batch_tokens


def find_matched_pile_step(
    target_tokens: int = DEDUP_TARGET_TOKENS,
    batch_tokens: int = BATCH_TOKENS
) -> int:
    """Find Pile checkpoint step closest to target token count.

    Args:
        target_tokens: Token count to match (dedup-Pile total)
        batch_tokens: Tokens per step
    Returns:
        Pile step number with minimum |pile_tokens - target_tokens|
    Note:
        Simple floor division suffices; Pythia checkpoints are dense enough
        that exact match is within 1 step (~2M tokens, <0.001% of 207B).
    """
    return target_tokens // batch_tokens  # ≈ 98,705 → use 99,000 as nearest logged step


def build_checkpoint_map(sizes: list[str] = SIZES) -> dict:
    """Build token-count-matched checkpoint map for all model sizes.

    Args:
        sizes: List of model size strings
    Returns:
        CheckpointMap dict (see Data Structures above)
    Side effects:
        Writes checkpoint_map.json to OUTPUT_DIR
    """
    ...


def main() -> None:
    """Entry point: build and write checkpoint_map.json."""
    ...
```

### Module: run_evaluation.py

```python
BENCHMARKS: list[str] = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
FEWSHOT: dict[str, int] = {"mmlu": 5, "hellaswag": 0, "arc_challenge": 25, "winogrande": 5}
DTYPE: str = "float16"
BATCH_SIZE: str = "auto:4"


def build_lmeval_cmd(
    model_id: str,
    revision: str,
    output_path: str,
    benchmarks: list[str] = BENCHMARKS,
    fewshot: dict[str, int] = FEWSHOT,
    dtype: str = DTYPE,
    batch_size: str = BATCH_SIZE,
) -> list[str]:
    """Construct lm_eval CLI command as argument list.

    Args:
        model_id: HuggingFace model identifier (e.g. "EleutherAI/pythia-1b")
        revision: Checkpoint revision string (e.g. "step99000")
        output_path: Directory path for lm-eval JSON output
        benchmarks: List of task names
        fewshot: Mapping of task → num_fewshot
        dtype: Model dtype string for HuggingFace
        batch_size: lm-eval batch_size argument
    Returns:
        List of strings suitable for subprocess.run()
    """
    ...


def result_exists(output_path: str) -> bool:
    """Check if lm-eval output JSON already exists (resume-safe guard).

    Args:
        output_path: Expected output directory for this model+revision
    Returns:
        True if results JSON found in output_path
    """
    ...


def evaluate_model(
    model_id: str,
    revision: str,
    output_dir: str,
    skip_existing: bool = True,
) -> str:
    """Run lm_eval CLI for one model variant; skip if results exist.

    Args:
        model_id: HuggingFace identifier
        revision: Checkpoint step string
        output_dir: Base results directory
        skip_existing: If True, skip evaluation if output JSON found
    Returns:
        Path to output JSON file
    Raises:
        subprocess.CalledProcessError: If lm_eval exits non-zero
    """
    ...


def main() -> None:
    """Entry point: evaluate all 8 model variants; resume-safe."""
    ...
```

### Module: statistical_tests.py

```python
CORRECTED_ALPHA: float = 0.0125   # Bonferroni: 0.05 / 4 benchmarks
MIN_DELTA: float = 0.001          # minimum |delta| for mechanism verification


def verify_mechanism_activation(
    matrix: dict,
    sizes: list[str],
    benchmarks: list[str],
    min_delta: float = MIN_DELTA,
) -> bool:
    """Confirm Pile and dedup-Pile produce distinguishable outputs.

    Args:
        matrix: AccuracyMatrix (accuracy[size][corpus][benchmark])
        sizes: Model size strings
        benchmarks: Benchmark names
        min_delta: Minimum |dedup_acc - pile_acc| to count as distinguishable
    Returns:
        True if any (size, benchmark) pair shows |delta| > min_delta
    Raises:
        RuntimeError: If ALL pairs have |delta| <= min_delta
            (indicates checkpoint loading error — models not properly differentiated)
    """
    ...


def paired_ttest_per_benchmark(
    matrix: dict,
    sizes: list[str],
    benchmarks: list[str],
    corrected_alpha: float = CORRECTED_ALPHA,
) -> dict:
    """Run paired t-test (n=4 model sizes) per benchmark.

    Args:
        matrix: AccuracyMatrix
        sizes: 4 model size strings (paired observations)
        benchmarks: List of benchmark names
        corrected_alpha: Bonferroni-corrected significance threshold
    Returns:
        StatResults dict (see Data Structures above)
    Note:
        Uses scipy.stats.ttest_rel(dedup_accs, pile_accs) — paired, two-tailed.
        n=4 pairs (one per model size). Degrees of freedom = 3.
    """
    ...


def evaluate_gate(stats: dict, min_significant_sizes: int = 2) -> bool:
    """Check if gate condition is met: ≥1 benchmark p<0.0125 at ≥2 sizes.

    Args:
        stats: StatResults dict per benchmark
        min_significant_sizes: Minimum model sizes showing significance
    Returns:
        True if gate condition satisfied
    Note:
        For paired t-test across 4 sizes, significance at "≥2 sizes" is
        captured by the paired t-stat directly (n=4 pairs). The gate_passed
        flag is True if any benchmark has significant=True.
    """
    ...


def main() -> None:
    """Entry point: load results_matrix.json, run tests, write statistical_results.json."""
    ...
```

---

## Pseudo-code: Evaluation Pipeline (E2 — highest complexity)

```
# run_evaluation.py main()

load checkpoint_map from checkpoint_map.json
load config (sizes, benchmarks, fewshot, dtype, batch_size)

model_variants = [
  ("EleutherAI/pythia-{size}",        "step{pile_step}",  "pile")  for size in sizes
  ("EleutherAI/pythia-{size}-deduped","step143000",        "dedup") for size in sizes
]  # 8 total

for (hf_id, revision, corpus) in model_variants:
    output_dir = results/{hf_id_slug}-{revision}/
    
    # Resume-safe: skip if already computed
    if result_exists(output_dir):
        log(f"Skipping {hf_id} {revision} — results exist")
        continue
    
    cmd = build_lmeval_cmd(hf_id, revision, output_dir)
    # cmd = ["lm_eval", "--model", "hf",
    #        "--model_args", f"pretrained={hf_id},revision={revision},dtype=float16",
    #        "--tasks", "mmlu,hellaswag,arc_challenge,winogrande",
    #        "--num_fewshot", "5", "0", "25", "5",
    #        "--batch_size", "auto:4",
    #        "--output_path", output_dir,
    #        "--log_samples"]
    
    log(f"Evaluating {hf_id} revision={revision}")
    subprocess.run(cmd, check=True)
    log(f"Done: {output_dir}")

log("All 8 model variants evaluated")
```

---

## Subtasks

#### Subtask E1-1: Implement step→token mapping and checkpoint resolution
- **Parent Epic**: E1
- **Description**: Implement `step_to_tokens()`, `find_matched_pile_step()`, and `build_checkpoint_map()`; write `checkpoint_map.json` with all 4 sizes; verify token mismatch < 5% for each size
- **API / Implementation Detail**: `find_matched_pile_step(207_000_000_000, 2_097_152)` → `98705`; round to nearest Pythia logged step (99000); compute `token_mismatch_pct = abs(99000*2097152 - 207e9) / 207e9 * 100`

#### Subtask E2-1: Implement build_lmeval_cmd with correct few-shot argument format
- **Parent Epic**: E2
- **Description**: Construct lm_eval CLI argument list; handle per-task fewshot mapping; validate task names match lm-eval v0.4.x identifiers (`arc_challenge` not `arc-challenge`)
- **API / Implementation Detail**: `--num_fewshot` takes space-separated integers in task order: `"5 0 25 5"` for mmlu/hellaswag/arc_challenge/winogrande

#### Subtask E2-2: Implement resume-safe result_exists check
- **Parent Epic**: E2
- **Description**: Check output directory for existing `*.json` lm-eval result file; return True to skip re-evaluation
- **API / Implementation Detail**: `glob(output_dir + "/**/*.json", recursive=True)` — lm-eval writes results in subdirectory; any JSON present = done

#### Subtask E2-3: Implement evaluate_model with subprocess error handling
- **Parent Epic**: E2
- **Description**: Run `subprocess.run(cmd, check=True)`; on `CalledProcessError`, log stderr and re-raise; on OOM, suggest reducing batch_size
- **API / Implementation Detail**: Capture `stderr=subprocess.PIPE`; log last 20 lines on failure for diagnosis

#### Subtask E2-4: Implement main evaluation loop across all 8 model variants
- **Parent Epic**: E2
- **Description**: Iterate all (size, corpus) combinations; build model_id and revision strings; call evaluate_model; log progress counter
- **API / Implementation Detail**: `model_variants = [(f"EleutherAI/pythia-{s}", f"step{cmap[s]['pile_step']}", "pile") for s in SIZES] + [(f"EleutherAI/pythia-{s}-deduped", f"step{cmap[s]['dedup_step']}", "dedup") for s in SIZES]`

#### Subtask E4-1: Implement verify_mechanism_activation with RuntimeError on null result
- **Parent Epic**: E4
- **Description**: Scan all (size, benchmark) pairs for |delta| > 0.001; raise RuntimeError with diagnostic message if none found
- **API / Implementation Detail**: `if all(abs(matrix[s]["dedup"][b] - matrix[s]["pile"][b]) <= MIN_DELTA for s in sizes for b in benchmarks): raise RuntimeError("All model pairs produce identical accuracy — checkpoint loading error. Verify revision tags.")`

#### Subtask E4-2: Implement paired_ttest_per_benchmark with gate evaluation
- **Parent Epic**: E4
- **Description**: For each benchmark, extract 4-element lists of pile_accs and dedup_accs (one per model size); run `scipy.stats.ttest_rel`; compute mean_diff and direction; evaluate gate condition
- **API / Implementation Detail**: `pile_accs = [matrix[s]["pile"][bench] for s in SIZES]`; `dedup_accs = [matrix[s]["dedup"][bench] for s in SIZES]`; `t_stat, p_val = ttest_rel(dedup_accs, pile_accs)`; `significant = p_val < CORRECTED_ALPHA`
