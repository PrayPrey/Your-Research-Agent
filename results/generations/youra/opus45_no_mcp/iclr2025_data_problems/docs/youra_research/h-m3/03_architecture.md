# Architecture: H-M3 (Representation Invariance -> Confidence Uniformity)

**Type**: MECHANISM | **Gate**: SHOULD_WORK (r < -0.4)
**Applied**: correlation-analysis-over-invariant-representations pattern (KB)

## System Overview

Inference-adjacent analysis pipeline. **Correction vs brief**: H-M2 does not persist
LoRA checkpoints to disk (`save_strategy="no"`, no `save_pretrained` call in
`train.py`) — models only exist in-memory per seed inside `run_experiment()` then are
deleted. There is no `h-m2/checkpoints/` on disk. H-M3 therefore reuses H-M2's
training code as a library (imported directly, not checkpoint-loaded) to reproduce
verbatim and paraphrase-trained models in-process per seed, then extracts hidden
states + confidence scores on those in-memory models before computing correlation.
No new training logic is written; H-M2 functions are called unmodified.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Actual code read directly (no Serena MCP; used Read tool on h-m2/code/*.py)
**Analyzed Path**: `docs/youra_research/h-m2/code/`
**Findings**: H-M2 `train.py` trains verbatim + paraphrase LoRA models per seed
in-memory and discards them (`del ...; torch.cuda.empty_cache()`) after computing MPS.
No adapter weights saved despite `output_dir=` args passed to `inject_contamination`
(Trainer `save_strategy="no"`). H-M3 must call the same training path itself.

## Module Structure

### confidence.py

**Dependencies**: h-m2/data.py (format_mmlu_prompt), h-m2/model.py (get_answer_token_ids)

```python
def extract_confidence(model, tokenizer, prompt: str, answer_token_id: int) -> float: ...
def batch_extract_confidences(model, tokenizer, prompts: list, answer_token_ids: list, batch_size: int = 8) -> list: ...
def confidence_variance(confidences: list) -> float: ...
```

### invariance_confidence.py

**Dependencies**: h-m2/representation.py, confidence.py, h-m2/data.py

```python
def extract_hidden_and_confidence(model, tokenizer, item: dict, paraphrase_prompts: list, answer_token_id: int) -> tuple: ...
def compute_rep_variance(hidden_states) -> float: ...  # 1 - mean pairwise cosine sim
def compute_item_variances(model, tokenizer, item: dict, paraphrase_prompts: list, answer_token_id: int) -> tuple: ...  # (rep_var, conf_var)
def run_variance_extraction(model, tokenizer, test_set, paraphrase_bank: dict, item_ids: list) -> dict: ...  # {idx: (rep_var, conf_var)}
```

### correlation.py

**Dependencies**: scipy.stats, numpy

```python
def compute_correlations(rep_variances: list, conf_variances: list) -> dict: ...  # pearson r,p + spearman r,p
def group_by_mps(mps_values: list, threshold: float = None) -> tuple: ...  # (high_idx, low_idx), median split if threshold None
def group_comparison(conf_variances: list, high_idx: list, low_idx: list) -> dict: ...  # mean/std per group + Cohen's d
def per_subject_correlation(rep_variances: dict, conf_variances: dict, subjects: dict) -> dict: ...  # {subject: r}
def verify_gate(r_pearson: float, threshold: float = -0.4) -> dict: ...  # {mechanism_active, gate_passes}
```

### run_experiment.py

**Dependencies**: All above + h-m2/{config,data,model,paraphrase,train}.py

```python
def run_seed(config, seed: int) -> dict: ...  # trains verbatim+paraphrase models (H-M2 code), extracts variances, correlates
def aggregate_across_seeds(results_per_seed: list) -> dict: ...
def main() -> None: ...
```

### visualize.py

**Dependencies**: matplotlib, numpy

```python
def plot_gate_metrics(target_r: float, actual_r: float, out_dir: str) -> None: ...
def plot_scatter_variance(rep_variances: list, conf_variances: list, out_dir: str) -> None: ...
def plot_boxplot_by_mps_group(conf_var_high: list, conf_var_low: list, out_dir: str) -> None: ...
def plot_correlation_histogram(r_per_seed: list, out_dir: str) -> None: ...
def plot_subject_heatmap(subject_correlations: dict, out_dir: str) -> None: ...
```

### config.py

```python
@dataclass
class Config:
    model_id: str = "mistralai/Mistral-7B-v0.1"
    contamination_frac: float = 0.10
    k_paraphrases_bank: int = 5
    k_paraphrases_train: int = 3
    n_eval_items: int = 1000  # match H-M2 eval subset; full 14042 optional via flag
    seeds: tuple = (42, 123, 456)
    epochs_verbatim: int = 12
    epochs_paraphrase: int = 3
    correlation_threshold: float = -0.4
    mps_median_split: bool = True
```

## File Organization

```
h-m3/code/
  config.py            # new (extends H-M2 Config with correlation_threshold)
  confidence.py         # new
  invariance_confidence.py  # new
  correlation.py         # new
  visualize.py           # new
  run_experiment.py      # new (orchestrator, calls H-M2 modules directly)
  results/
    correlation_results.json
  figures/
    gate_metrics.png
    scatter_variance.png
    boxplot_mps_group.png
    correlation_histogram.png
    subject_heatmap.png
```

H-M2 modules are imported via sys.path insert of `h-m2/code/` (no code duplication):
`data.py`, `model.py`, `paraphrase.py`, `representation.py`, `train.py` (for
`build_augmented_training_set`).

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M3-1 | Setup + H-M2 import bridge | sys.path wiring to h-m2/code, config.py, answer token setup | 6 | 2+2+1+1 |
| M3-2 | Confidence extraction module | confidence.py: softmax prob of correct answer token, batched | 8 | 2+2+2+2 |
| M3-3 | Variance computation module | invariance_confidence.py: rep_variance + conf_variance per item | 9 | 3+2+3+1 |
| M3-4 | Reuse H-M2 training pipeline | Call inject_contamination for verbatim+paraphrase per seed (in-memory, no checkpoint I/O) | 10 | 2+4+2+2 |
| M3-5 | Correlation analysis module | correlation.py: pearson/spearman, group split, Cohen's d, gate check | 9 | 3+2+3+1 |
| M3-6 | Per-subject correlation (A2) | per_subject_correlation across 57 MMLU subjects | 6 | 2+2+2+0 |
| M3-7 | Multi-seed orchestration | run_experiment.py: loop seeds 42/123/456, aggregate, run_seed | 10 | 3+3+2+2 |
| M3-8 | Figure generation | visualize.py: 5 required plots (gate bar, scatter, boxplot, histogram, heatmap) | 7 | 3+1+1+2 |
| M3-9 | Results persistence + validation report | Save correlation_results.json, gate check output | 5 | 2+1+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M3-3, M3-4, M3-5, M3-7], Low(4-8): [M3-1, M3-2, M3-6, M3-8, M3-9]

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| load_mmlu, format_mmlu_prompt, sample_contamination_ids, build_training_dataset | `from data import load_mmlu, format_mmlu_prompt, sample_contamination_ids, build_training_dataset` | `h-m2/code/data.py` |
| load_base_model, build_lora_config_m1, inject_contamination, get_answer_token_ids | `from model import load_base_model, build_lora_config_m1, inject_contamination, get_answer_token_ids` | `h-m2/code/model.py` |
| build_paraphrase_bank, load_paraphraser | `from paraphrase import build_paraphrase_bank, load_paraphraser` | `h-m2/code/paraphrase.py` |
| extract_representation, batch_extract_representations, compute_paraphrase_similarity, evaluate_invariance | `from representation import extract_representation, batch_extract_representations, compute_paraphrase_similarity, evaluate_invariance` | `h-m2/code/representation.py` |
| build_augmented_training_set | `from train import build_augmented_training_set` | `h-m2/code/train.py` |
| Config | `from config import Config` (H-M2 base config, extended in h-m3/code/config.py) | `h-m2/code/config.py` |

**Verified from**: `h-m2/code/` (actual implementation, read directly).
**Caveat**: No trained checkpoints exist on disk — H-M3 must retrain verbatim and
paraphrase models per seed via `inject_contamination` (same code, in-memory) rather
than loading saved adapters as the PRD/brief assume.
