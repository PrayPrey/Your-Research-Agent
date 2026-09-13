# Logic: h-c1-v2
# RLHF Calibration Moderation — Task-Type-Conditional ΔΔECE Analysis

Applied: cache-reuse incremental extension pattern (h-c1 → h-c1-v2)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from base code
**Analyzed Path**: `docs/youra_research/h-c1/code/`
**Relevant Symbols**:
- `CellECE(cell_id, model_id, ece_clean, ece_adv, delta_ece, n_clean, n_adv)` — NamedTuple
- `ModerationResult(cell_id, delta_ece_base, delta_ece_chat, ddece, moderation_confirmed)` — NamedTuple
- `compare_rlhf_moderation(base: CellECE, chat: CellECE) -> ModerationResult`
- `compute_moderation_rate(moderation_results: list) -> float`
- `compute_ece(confidences: np.ndarray, correct: np.ndarray, n_bins: int = 15) -> float`
- `write_json(path: str, data) -> None`
- `extract_cell(model, tokenizer, dataset, task: str, model_id: str, batch_size: int = 8) -> CellResult`

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

```python
# From: h-c1/code/comparison/delta_ece.py (ACTUAL CODE)
class CellECE(NamedTuple):
    cell_id: str
    model_id: str
    ece_clean: float
    ece_adv: float
    delta_ece: float
    n_clean: int
    n_adv: int

class ModerationResult(NamedTuple):
    cell_id: str
    delta_ece_base: float
    delta_ece_chat: float
    ddece: float
    moderation_confirmed: bool

def compare_rlhf_moderation(base: CellECE, chat: CellECE) -> ModerationResult: ...
def compute_moderation_rate(moderation_results: list) -> float: ...

# From: h-c1/code/evaluation/ece.py (ACTUAL CODE)
def compute_ece(confidences: np.ndarray, correct: np.ndarray, n_bins: int = 15) -> float: ...

# From: h-c1/code/results/storage.py (ACTUAL CODE)
def write_json(path: str, data) -> None: ...
```

**Verified from**: `docs/youra_research/h-c1/code/` (actual implementation, NOT spec)

---

## A-4: 13B-chat Inference via lm-evaluation-harness [Complexity: 14, Budget: 4]

Applied: subprocess-orchestrated lm-eval-harness with JSON logit extraction

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | run_lm_eval_13b_chat | Subprocess lm-eval-harness for 4 tasks |
| L-4-2 | parse_lm_eval_output | Extract logits from output JSON |
| L-4-3 | convert_to_cell_ece | Wrap parsed output into CellECE |
| L-4-4 | validate_13b_inference_output | Shape/population checks |

### API Signatures

```python
# comparison/conditional_ece.py (new inference section)

def run_lm_eval_13b_chat(
    model_id: str,                    # "meta-llama/Llama-2-13b-chat-hf"
    tasks: List[str],                 # ["anli_r1", "anli_r2", "anli_r3", "adv_glue_mnli"]
    output_dir: str,                  # config.new_inference_output
    seed: int = 1,
    lm_eval_path: str = "lm_evaluation_harness",
) -> Dict[str, str]:
    """Run lm-eval subprocess per task. Returns {task: output_json_path}."""
    ...


def parse_lm_eval_output(
    results_dir: str,
    task_to_cell_id: Dict[str, str],  # {"anli_r1": "NLI-ANLI-R1", ...}
) -> Dict[str, Dict[str, np.ndarray]]:
    """
    Parse lm-eval JSON output files.
    Returns: {cell_id: {"logits": (N, 3), "labels": (N,)}}
    """
    ...


def convert_to_cell_ece(
    logits: np.ndarray,       # (N, 3) — raw answer-token logits per example
    labels: np.ndarray,       # (N,)  — integer class labels {0,1,2}
    clean_logits: np.ndarray, # (N_clean, 3) — logits on clean split (MultiNLI for ANLI)
    clean_labels: np.ndarray, # (N_clean,)
    cell_id: str,
    model_id: str,
    n_bins: int = 15,
) -> CellECE:
    """Softmax logits -> confidences -> compute_ece -> CellECE."""
    ...


def validate_13b_inference_output(
    cells: Dict[str, CellECE],
    expected_cell_ids: List[str],     # ["NLI-ANLI-R1", "NLI-ANLI-R2", "NLI-ANLI-R3", "NLI-AdvGLUE"]
) -> None:
    """Raise ValueError if any cell missing or shapes invalid."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| logits | (N, 3) | Per-example answer-token logits from lm-eval JSON |
| confidences | (N,) | max(softmax(logits), axis=1) |
| labels | (N,) | Integer {0,1,2} ground truth |
| correct | (N,) | float {0.0, 1.0} — argmax(logits)==labels |

### Pseudo-code (L-4-1)

```
for task in tasks:
    cmd = ["python", "main.py", "--model", "hf",
           "--model_args", f"pretrained={model_id}",
           "--tasks", task,
           "--log_samples",
           "--output_path", output_dir,
           "--seed", str(seed)]
    subprocess.run(cmd, cwd=lm_eval_path, check=True)
    output_path = find_latest_json(output_dir, task)
    result[task] = output_path
return result
```

### Pseudo-code (L-4-2)

```
for task, json_path in results_dir items:
    data = json.load(json_path)
    samples = data["samples"][task]  # list of per-example dicts
    logits = np.array([s["filtered_resps"] for s in samples])  # (N, 3)
    labels = np.array([s["target"] for s in samples])          # (N,)
    cell_id = task_to_cell_id[task]
    parsed[cell_id] = {"logits": logits, "labels": labels}
return parsed
```

### Pseudo-code (L-4-3)

```
probs = softmax(logits, axis=1)            # (N, 3)
preds = argmax(probs, axis=1)              # (N,)
confidences = probs[range(N), preds]       # (N,)
correct = (preds == labels).astype(float)  # (N,)
ece_adv = compute_ece(confidences, correct, n_bins)

clean_probs = softmax(clean_logits, axis=1)
clean_preds = argmax(clean_probs, axis=1)
clean_conf = clean_probs[range(N_clean), clean_preds]
clean_correct = (clean_preds == clean_labels).astype(float)
ece_clean = compute_ece(clean_conf, clean_correct, n_bins)

return CellECE(cell_id, model_id, ece_clean, ece_adv,
               delta_ece=ece_adv - ece_clean,
               n_clean=N_clean, n_adv=N)
```

---

## A-5: Conditional ΔΔECE [Complexity: 12, Budget: 2]

Applied: Standard PyTorch / numpy — delegates to h-c1 compare_rlhf_moderation

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | compute_moderation_by_benchmark_type | ANLI vs AdvGLUE separated moderation |
| L-5-2 | evaluate_gate | Primary gate with report dict |

### API Signatures

```python
# comparison/conditional_ece.py

def compute_moderation_by_benchmark_type(
    base_results: Dict[str, CellECE],    # {cell_id: CellECE} for base model
    chat_results: Dict[str, CellECE],    # {cell_id: CellECE} for chat model
    anli_cells: List[str],               # ["NLI-ANLI-R1", "NLI-ANLI-R2", "NLI-ANLI-R3"]
    advglue_cells: List[str],            # ["NLI-AdvGLUE"]
    ddece_threshold: float = 0.01,
) -> Tuple[List[ModerationResult], List[ModerationResult], float, float]:
    """
    Separate moderation by benchmark type.
    Returns: (anli_results, advglue_results, anli_rate, advglue_rate)
    anli_rate = fraction of ANLI cells with ddece > ddece_threshold
    """
    ...


def evaluate_gate(
    anli_moderation_rate: float,
    threshold: float = 0.60,
) -> Tuple[bool, Dict]:
    """
    Primary gate check.
    Returns: (gate_passed, report_dict)
    report_dict keys: "anli_rate", "threshold", "gate_passed", "margin"
    """
    ...
```

### Pseudo-code (L-5-1)

```
anli_results = []
for cell_id in anli_cells:
    r = compare_rlhf_moderation(base_results[cell_id], chat_results[cell_id])
    # override moderation_confirmed with threshold-based check
    confirmed = r.ddece > ddece_threshold
    anli_results.append(r._replace(moderation_confirmed=confirmed))
anli_rate = compute_moderation_rate(anli_results)

advglue_results = []
for cell_id in advglue_cells:
    r = compare_rlhf_moderation(base_results[cell_id], chat_results[cell_id])
    confirmed = r.ddece > ddece_threshold
    advglue_results.append(r._replace(moderation_confirmed=confirmed))
advglue_rate = compute_moderation_rate(advglue_results)

return anli_results, advglue_results, anli_rate, advglue_rate
```

### Pseudo-code (L-5-2)

```
gate_passed = anli_moderation_rate >= threshold
report = {
    "anli_rate": anli_moderation_rate,
    "threshold": threshold,
    "gate_passed": gate_passed,
    "margin": anli_moderation_rate - threshold,
}
return gate_passed, report
```

---

## A-8: Orchestrator [Complexity: 10, Budget: 2]

Applied: Standard PyTorch / numpy — linear control flow with error serialization

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | main | Full control flow with error handling |
| L-8-2 | write_validation_report | Markdown report serialization |

### API Signatures

```python
# run_experiment.py

def main(config: "HC1V2Config" = None) -> bool:
    """
    Orchestrate full h-c1-v2 pipeline.
    Returns gate_passed bool.
    Exit code: 0 (pass) / 1 (fail).
    """
    ...


def write_validation_report(
    results: Dict,
    gate_passed: bool,
    config: "HC1V2Config",
) -> str:
    """
    Write markdown validation report to config.validation_report.
    Returns report string.
    """
    ...
```

### Pseudo-code (L-8-1)

```
config = config or HC1V2Config()
os.makedirs(config.results_dir, exist_ok=True)
os.makedirs(config.figures_dir, exist_ok=True)

# Step 1: Load h-c1 cache (7B base + 7B chat, all cells)
cache = load_h_c1_cache(config.h_c1_results_file)   # {model_id: {cell_id: CellECE}}
base_7b  = cache["meta-llama/Llama-2-7b-hf"]
chat_7b  = cache["meta-llama/Llama-2-7b-chat-hf"]

# Step 2: Run 13B-chat new inference (lm-eval subprocess)
try:
    task_paths = run_lm_eval_13b_chat(
        model_id="meta-llama/Llama-2-13b-chat-hf",
        tasks=["anli_r1", "anli_r2", "anli_r3", "adv_glue_mnli"],
        output_dir=config.new_inference_output,
        seed=config.seed,
    )
    parsed = parse_lm_eval_output(config.new_inference_output, TASK_TO_CELL_ID)
    datasets_clean = load_hc1v2_datasets(seed=config.seed)
    chat_13b = {}
    for cell_id, d in parsed.items():
        clean_key = CELL_TO_CLEAN_KEY[cell_id]
        clean_ds = datasets_clean[clean_key]
        chat_13b[cell_id] = convert_to_cell_ece(
            d["logits"], d["labels"],
            clean_logits_from_ds(clean_ds, config),  # run 13B on clean split too
            ..., cell_id, "meta-llama/Llama-2-13b-chat-hf"
        )
    validate_13b_inference_output(chat_13b, list(TASK_TO_CELL_ID.values()))
except Exception as e:
    with open(config.errors_log, "a") as f:
        f.write(f"13B inference failed: {e}\n{traceback.format_exc()}\n")
    raise

# Step 3: 7B pair conditional ΔΔECE
anli_results_7b, advglue_results_7b, anli_rate_7b, advglue_rate_7b = \
    compute_moderation_by_benchmark_type(
        base_7b, chat_7b, config.anli_cells, config.advglue_cells,
        config.ddece_threshold
    )

# Step 4: 13B cross-size ΔΔECE (ANLI only)
anli_results_13b, anli_rate_13b = compute_cross_size_moderation(
    base_7b, chat_13b, config.anli_cells, config.ddece_threshold
)

# Step 5: Primary gate
gate_passed, gate_report = evaluate_gate(anli_rate_7b, config.moderation_rate_threshold)

# Step 6: Save results
results = summarize_results(
    (anli_results_7b, advglue_results_7b, anli_rate_7b, advglue_rate_7b),
    (anli_results_13b, anli_rate_13b),
)
results["gate"] = gate_report
write_json(config.results_file, results)
report = write_validation_report(results, gate_passed, config)

# Step 7: Generate figures
all_cells = {**base_7b, **chat_7b, **{"13b_chat_" + k: v for k, v in chat_13b.items()}}
fig1_ddece_bar(anli_results_7b, advglue_results_7b, "7B pair",
               os.path.join(config.figures_dir, "ddece_comparison_bar_7b.png"))
fig1_ddece_bar(anli_results_13b, [], "13B pair",
               os.path.join(config.figures_dir, "ddece_comparison_bar_13b.png"))
fig2_reliability_diagrams(base_7b, chat_7b,
                           ["NLI-ANLI-R3", "NLI-AdvGLUE"],
                           os.path.join(config.figures_dir, "reliability_diagram.png"))
fig3_confidence_histogram(base_7b, chat_7b, "NLI-ANLI-R1",
                           os.path.join(config.figures_dir, "confidence_distribution_adv.png"))
fig4_moderation_heatmap(cache | {"meta-llama/Llama-2-13b-chat-hf": chat_13b},
                         row_models=config.models,
                         col_cells=config.anli_cells + config.advglue_cells,
                         out_path=os.path.join(config.figures_dir, "moderation_heatmap.png"))
fig5_ddece_vs_difficulty(anli_results_7b, "7B pair",
                          os.path.join(config.figures_dir, "ddece_vs_difficulty.png"))

return gate_passed
```

### Pseudo-code (L-8-2)

```
lines = [
    f"# Validation Report: h-c1-v2",
    f"Date: {datetime.now().isoformat()}",
    f"",
    f"## Gate Result: {'PASS' if gate_passed else 'FAIL'}",
    f"",
    f"| Metric | Value | Threshold |",
    f"|--------|-------|-----------|",
    f"| ANLI moderation rate (7B) | {results['anli_rate_7b']:.4f} | ≥0.60 |",
    f"| ANLI moderation rate (13B) | {results['anli_rate_13b']:.4f} | ≥0.60 |",
    f"| AdvGLUE moderation rate | {results['advglue_rate_7b']:.4f} | boundary |",
    # per-cell ΔΔECE table
    ...
]
report = "\n".join(lines)
with open(config.validation_report, "w") as f:
    f.write(report)
return report
```

---

## Constants

```python
# run_experiment.py (module-level)
TASK_TO_CELL_ID: Dict[str, str] = {
    "anli_r1":       "NLI-ANLI-R1",
    "anli_r2":       "NLI-ANLI-R2",
    "anli_r3":       "NLI-ANLI-R3",
    "adv_glue_mnli": "NLI-AdvGLUE",
}

CELL_TO_CLEAN_KEY: Dict[str, str] = {
    "NLI-ANLI-R1": "anli_r1_clean",   # MultiNLI slice
    "NLI-ANLI-R2": "anli_r2_clean",
    "NLI-ANLI-R3": "anli_r3_clean",
    "NLI-AdvGLUE": "glue_mnli",
}
```
