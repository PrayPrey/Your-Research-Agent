---
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
tier: LIGHT
date: "2026-08-25"
author: Anonymous
---

# Configuration Design: H-E1 — ECE Measurement Pipeline

Applied: dataclass-hyperparameter-configuration-pattern
Applied: bfloat16-4bit-quantization-vram-management

---

## ExperimentConfig Dataclass

```python
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

@dataclass
class ExperimentConfig:
    # ── Reproducibility ───────────────────────────────────────────
    seed: int = 1
    # Fixed for all subsampling (GLUE/MultiNLI 500-example draws).
    # Record in results metadata for reproducibility.

    # ── Evaluation ────────────────────────────────────────────────
    n_bins_primary: int = 15
    # Guo 2017 standard equal-width ECE bin count.
    n_bins_secondary: int = 10
    # Sensitivity check (Risk R5 mitigation from Phase 2B).
    min_examples_per_cell: int = 200
    # Gate requirement: ≥200 valid examples per (model, task, split) cell.
    subsample_clean: int = 500
    # GLUE/MultiNLI validation sets are large (872–40k); subsample to 500
    # for compute efficiency while exceeding the 200-example threshold.
    prevalidation_n: int = 10
    # Examples to run before full cell evaluation (Risk R1 mitigation).

    # ── Models ────────────────────────────────────────────────────
    models: List[str] = field(default_factory=lambda: [
        "meta-llama/Llama-2-7b-hf",
        "meta-llama/Llama-2-7b-chat-hf",
        "meta-llama/Llama-2-13b-chat-hf",
        "mistralai/Mistral-7B-Instruct-v0.1",
    ])
    use_4bit_threshold_gb: float = 40.0
    # If available VRAM < this threshold AND model is 13B, use 4-bit quantization.

    # ── Validation Thresholds ─────────────────────────────────────
    max_confidence_degenerate: float = 0.999
    # Confidence above this = all-confident (degenerate logits).
    non_degenerate_fraction: float = 0.90
    # Fraction of examples that must be below max_confidence_degenerate.
    min_confidence_uniform: float = 0.40
    # Mean max confidence below this = near-uniform (model not conditioning).
    prob_sum_tolerance: float = 1e-3
    # |softmax_sum - 1.0| must be < this for valid probability distributions.
    ece_plausible_min: float = 0.0
    ece_plausible_max: float = 0.5
    # ECE outside [0.0, 0.5] indicates numerical error.

    # ── Sanity Check (Kadavath 2022 baseline) ─────────────────────
    clean_ece_min: float = 0.05
    clean_ece_max: float = 0.15
    # Published LLM clean-split ECE range (Kadavath 2022, TriviaQA/MMLU/BIG-Bench).
    min_models_sanity: int = 2
    # Gate sanity check passes if ≥2/4 models have clean ECE in [0.05, 0.15].

    # ── Gate ──────────────────────────────────────────────────────
    gate_min_cells: int = 20
    # Gate passes if ≥20/24 cells have cell_passed=True.

    # ── Dataset Mapping ───────────────────────────────────────────
    # Maps task name → (clean_hf_key, adversarial_hf_key)
    task_split_map: Dict[str, Tuple[str, str]] = field(default_factory=lambda: {
        "qqp":  ("glue_qqp",  "advglue_qqp"),
        "sst2": ("glue_sst2", "advglue_sst2"),
        "nli":  ("mnli",      "advglue_mnli"),   # ANLI handled separately
    })
    # ANLI rounds treated as additional adversarial splits for NLI task
    anli_splits: List[str] = field(default_factory=lambda: ["anli_r1", "anli_r2", "anli_r3"])

    # ── Paths ─────────────────────────────────────────────────────
    results_dir: str = "docs/youra_research/h-e1/results"
    figures_dir: str = "docs/youra_research/h-e1/figures"
    errors_log: str = "docs/youra_research/h-e1/results/errors.log"
```

---

## Config Field Justification Table

| Field | Value | Source |
|-------|-------|--------|
| `seed` | 1 | PRD NFR-1: fixed seed for reproducibility |
| `n_bins_primary` | 15 | PRD FR-4.1: Guo 2017 standard |
| `n_bins_secondary` | 10 | PRD FR-4.2: Phase 2B Risk R5 mitigation |
| `min_examples_per_cell` | 200 | PRD Success Criteria + gate condition |
| `subsample_clean` | 500 | PRD Section 4.1: exceeds 200-example threshold |
| `prevalidation_n` | 10 | PRD FR-3.4: Phase 2B Risk R1 mitigation |
| `use_4bit_threshold_gb` | 40.0 | PRD FR-2.3: 13B bfloat16 requires ~26GB |
| `max_confidence_degenerate` | 0.999 | PRD FR-3.4: degenerate detection threshold |
| `non_degenerate_fraction` | 0.90 | PRD FR-4.3: verify_logit_extraction spec |
| `min_confidence_uniform` | 0.40 | PRD FR-4.3: near-uniform detection |
| `prob_sum_tolerance` | 1e-3 | PRD FR-4.3: softmax validation |
| `clean_ece_min/max` | [0.05, 0.15] | PRD FR-4.4: Kadavath 2022 baseline |
| `min_models_sanity` | 2 | PRD FR-4.4: ≥2/4 models must pass |
| `gate_min_cells` | 20 | PRD FR-5.3: gate condition ≥20/24 |

---

## YAML Config Equivalent

```yaml
# h-e1-config.yaml — CLI override for ExperimentConfig
seed: 1
n_bins_primary: 15
n_bins_secondary: 10
min_examples_per_cell: 200
subsample_clean: 500
prevalidation_n: 10
use_4bit_threshold_gb: 40.0
max_confidence_degenerate: 0.999
non_degenerate_fraction: 0.90
min_confidence_uniform: 0.40
prob_sum_tolerance: 0.001
ece_plausible_min: 0.0
ece_plausible_max: 0.5
clean_ece_min: 0.05
clean_ece_max: 0.15
min_models_sanity: 2
gate_min_cells: 20
results_dir: "docs/youra_research/h-e1/results"
figures_dir: "docs/youra_research/h-e1/figures"
models:
  - "meta-llama/Llama-2-7b-hf"
  - "meta-llama/Llama-2-7b-chat-hf"
  - "meta-llama/Llama-2-13b-chat-hf"
  - "mistralai/Mistral-7B-Instruct-v0.1"
```

---

## Subtask Specifications

### C-5-1: Cell Iteration Control Flow

**Parent Epic:** A-5 (Orchestration + Storage, complexity 12)
**File:** `run_experiment.py`

```python
def main(config: ExperimentConfig) -> None:
    # 1. Load all datasets once
    datasets = load_all_datasets(seed=config.seed)
    save_manifest(datasets, f"{config.results_dir}/dataset_manifest.json")

    ece_rows = []           # accumulate for gate evaluation
    clean_ece_by_model = {} # {model_id: {task: ece_15}}

    # 2. Sequential model loop (VRAM management)
    for model_id in config.models:
        use_4bit = decide_quantization(model_id, config)
        model, tokenizer = load_model(model_id, use_4bit=use_4bit)
        checkpoint_hash = get_checkpoint_hash(model_id)

        for task in ["qqp", "sst2", "nli"]:
            clean_key, adv_key = config.task_split_map[task]
            splits = {
                "clean": datasets[clean_key],
                "adversarial": datasets[adv_key],
            }
            # For NLI, also evaluate ANLI rounds as adversarial
            if task == "nli":
                for anli_split in config.anli_splits:
                    splits[anli_split] = datasets[anli_split]

            for split_name, dataset in splits.items():
                try:
                    # Pre-validation gate (Risk R1)
                    pre_result = prevalidate_cell(
                        model, tokenizer, dataset, task, model_id,
                        n=config.prevalidation_n
                    )
                    if not pre_result.passed:
                        log_error(config.errors_log,
                            f"Pre-validation FAILED: {model_id}/{task}/{split_name} "
                            f"indicators={pre_result.indicators}")
                        ece_rows.append({
                            "model": model_id, "task": task, "split": split_name,
                            "n_examples": 0, "ece_15": None, "ece_10": None,
                            "accuracy": None, "mean_confidence": None,
                            "cell_passed": False
                        })
                        continue  # skip full evaluation

                    # Full cell evaluation
                    cell_result = extract_cell(
                        model, tokenizer, dataset, task, model_id,
                        batch_size=config.batch_size
                    )
                    ece_15, ece_10 = compute_both(
                        cell_result.confidences,
                        (cell_result.pred_labels == cell_result.true_labels)
                    )
                    val_result = verify_logit_extraction(cell_result, ece_15)

                    row = {
                        "model": model_id, "task": task, "split": split_name,
                        "n_examples": len(cell_result.confidences),
                        "ece_15": ece_15, "ece_10": ece_10,
                        "accuracy": (cell_result.pred_labels == cell_result.true_labels).mean(),
                        "mean_confidence": cell_result.confidences.mean(),
                        "cell_passed": val_result.passed,
                        "checkpoint_hash": checkpoint_hash,
                    }
                    append_cell_row(f"{config.results_dir}/ece_results.csv", row)
                    write_cell_jsonl(
                        f"{config.results_dir}/{model_id.split('/')[-1]}_{task}_{split_name}_examples.jsonl",
                        cell_result
                    )
                    ece_rows.append(row)

                    if split_name == "clean":
                        clean_ece_by_model.setdefault(model_id, {})[task] = ece_15

                except Exception as e:
                    log_error(config.errors_log,
                        f"Cell FAILED: {model_id}/{task}/{split_name} error={e}")
                    ece_rows.append({
                        "model": model_id, "task": task, "split": split_name,
                        "n_examples": 0, "ece_15": None, "ece_10": None,
                        "accuracy": None, "mean_confidence": None,
                        "cell_passed": False
                    })

        unload_model(model)

    # 3. Gate evaluation + finalize
    _finalize(config, ece_rows, clean_ece_by_model)
```

**Edge cases:**
- OOM during model load → caught by outer try/except; all cells for that model marked failed
- Empty dataset after subsampling → pre-validation catches coverage_met=False
- NLI task: 4 adversarial splits (advglue_mnli + anli_r1/r2/r3) × 4 models = 16 additional cells beyond the base 24 — document this in gate evaluation

---

### C-5-2: Gate Evaluation and Results Finalization

**Parent Epic:** A-5 (Orchestration + Storage, complexity 12)
**File:** `run_experiment.py` (`_finalize` function)

```python
def _finalize(config, ece_rows, clean_ece_by_model):
    import pandas as pd

    df = pd.DataFrame(ece_rows)

    # Gate evaluation
    passed_cells = df["cell_passed"].sum()
    failed_cells = df[~df["cell_passed"]][["model", "task", "split"]].to_dict("records")

    clean_sanity_passed, sanity_details = check_clean_sanity(clean_ece_by_model)

    gate_passed = (passed_cells >= config.gate_min_cells) and clean_sanity_passed

    write_gate_result(
        path=f"{config.results_dir}/gate_result.json",
        passed_cells=int(passed_cells),
        failed_cells=failed_cells,
        clean_sanity=clean_sanity_passed,
    )

    # Visualizations (all 5 required figures)
    import os; os.makedirs(config.figures_dir, exist_ok=True)
    fig1_ece_comparison(df, f"{config.figures_dir}/fig1_ece_comparison.png")
    example_paths = [
        f"{config.results_dir}/{m.split('/')[-1]}_{t}_{s}_examples.jsonl"
        for m in config.models for t in ["qqp", "sst2", "nli"] for s in ["clean", "adversarial"]
    ]
    fig2_reliability_diagrams(example_paths, f"{config.figures_dir}/fig2_reliability_diagrams.png")
    fig3_coverage_heatmap(df, f"{config.figures_dir}/fig3_coverage_heatmap.png")
    fig4_confidence_boxplots(example_paths, f"{config.figures_dir}/fig4_confidence_distribution.png")
    fig5_ece_sensitivity(df, f"{config.figures_dir}/fig5_ece_sensitivity.png")

    # Summary
    print(f"\n{'='*60}")
    print(f"H-E1 GATE RESULT: {'PASS' if gate_passed else 'FAIL'}")
    print(f"  Cells passed: {passed_cells}/24")
    print(f"  Clean sanity: {'PASS' if clean_sanity_passed else 'FAIL'} {sanity_details}")
    print(f"  Gate condition: passed_cells >= {config.gate_min_cells} AND clean_sanity")
    print(f"{'='*60}\n")
```

---

### C-2-1: VRAM-Based Quantization Decision

**Parent Epic:** A-2 (Model Management, complexity 11)
**File:** `models/loader.py`

```python
def decide_quantization(model_id: str, config: ExperimentConfig) -> bool:
    """
    Returns use_4bit: True if VRAM is insufficient for bfloat16 inference.

    VRAM estimates (bfloat16):
      7B model:  ~14 GB  (2 bytes × 7e9 params)
      13B model: ~26 GB  (2 bytes × 13e9 params)

    VRAM estimates (4-bit BitsAndBytes):
      7B model:  ~4 GB
      13B model: ~7 GB
    """
    vram_gb = check_vram_gb()
    is_13b = "13b" in model_id.lower()

    if is_13b and vram_gb < config.use_4bit_threshold_gb:
        import warnings
        warnings.warn(
            f"13B model with {vram_gb:.1f}GB VRAM < {config.use_4bit_threshold_gb}GB threshold. "
            f"Using 4-bit quantization. Note: 4-bit inference is non-deterministic on some hardware."
        )
        return True
    return False


def load_model(model_id: str, use_4bit: bool = False):
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    import torch

    quant_config = None
    if use_4bit:
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16 if not use_4bit else None,
        quantization_config=quant_config,
        device_map="auto",
    )
    model.eval()
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return model, tokenizer


def check_vram_gb() -> float:
    import torch
    if not torch.cuda.is_available():
        return 0.0
    return torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)


def unload_model(model) -> None:
    import torch, gc
    del model
    torch.cuda.empty_cache()
    gc.collect()
```

**Reproducibility note:** 4-bit NF4 quantization (BitsAndBytes) is generally deterministic for inference given fixed seed, but may produce slightly different logit values on different GPU architectures. Record `use_4bit=True/False` per model in results metadata.
