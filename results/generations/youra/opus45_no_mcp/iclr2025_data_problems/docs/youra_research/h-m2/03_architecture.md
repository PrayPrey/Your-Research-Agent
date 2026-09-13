# Architecture: H-M2 (Training Develops Robust Semantic Representations — MECHANISM)

Applied: mean-pooled last-hidden-state extraction + cosine similarity pattern (sentence-transformers / HF `output_hidden_states`)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Actual H-M1 code read directly (file read; Serena MCP unavailable, used direct inspection per PRD mandate to trust code over specs)
**Analyzed Path**: `h-m1/code/data.py`, `h-m1/code/model.py`, `h-m1/code/config.py`
**Findings**: H-M1 is PoC-scale, not matching 02c brief assumptions — `config.py` uses `n_test_items=2000`, `seeds=(42,)` (single seed, not 3), `contamination_levels=(0.0, 0.10, 0.50)`. Critically, `inject_contamination()` in `h-m1/code/model.py` returns an **in-memory `PeftModel`, never saved to disk** — there is no `h-m1/checkpoints/contaminated_10pct` path as the brief assumes. H-M2 must therefore **retrain** the verbatim-only baseline itself by calling `inject_contamination` directly (reusing H-M1's data/model functions), not load a checkpoint. `format_training_example`, `load_base_model`, `build_lora_config_m1`, `sample_contamination_ids`, `build_training_dataset` are reused as-is.

---

## Module Structure

### data.py (`h-m2/code/data.py`)

**Dependencies**: H-M1 `data.py` (reused), datasets, transformers (T5 paraphraser)

```python
from h_m1.code.data import load_mmlu, sample_contamination_ids, build_training_dataset, format_mmlu_prompt

def load_paraphraser():
    """Vamsi995/T5_Paraphrase_Paws -> (model, tokenizer)"""

def generate_paraphrases(item: dict, para_model, para_tokenizer, k: int = 5, seed: int = 42) -> list[str]:
    """T5-paraphrase (mix with rule-based synonym fallback) -> list[str] len k"""

def build_paraphrase_bank(contaminated_items: Dataset, para_model, para_tokenizer,
                           k: int = 5, seed: int = 42) -> dict[int, list[str]]:
    """idx -> [paraphrase_text, ...] for every contaminated item; cache to disk (json)"""

def build_augmented_training_set(contaminated_items: Dataset, paraphrase_bank: dict,
                                  n_paraphrases_train: int = 3) -> Dataset:
    """original + first n_paraphrases_train paraphrases per item, formatted as training examples"""
```

### model.py (`h-m2/code/model.py`)

**Dependencies**: H-M1 `model.py` (reused), torch, peft

```python
from h_m1.code.model import load_base_model, build_lora_config_m1, inject_contamination, format_training_example

def train_verbatim_model(contaminated_items: Dataset, seed: int, epochs: int = 12) -> PeftModel:
    """Baseline: reuse inject_contamination on verbatim-only items, epoch-matched compute"""

def train_paraphrase_model(augmented_items: Dataset, seed: int, epochs: int = 3) -> PeftModel:
    """Proposed: reuse inject_contamination on original+paraphrase items"""
```

### representation.py (`h-m2/code/representation.py`)

**Dependencies**: model.py, torch, torch.nn.functional

```python
def extract_representation(model, tokenizer, text: str) -> torch.Tensor:
    """output_hidden_states=True; hidden_states[-1] mean-pooled over attention_mask -> [4096]"""

def batch_extract_representations(model, tokenizer, texts: list[str], batch_size: int = 8) -> torch.Tensor:
    """Batched extract_representation -> [N, 4096]"""

def compute_paraphrase_similarity(orig_rep: torch.Tensor, para_reps: torch.Tensor) -> float:
    """mean cosine_similarity(orig_rep, para_reps, dim=-1) over K paraphrases"""

def evaluate_invariance(model, tokenizer, items: list[dict], paraphrase_bank: dict) -> np.ndarray:
    """Per-item MPS array, shape [n_items]"""
```

### mechanism.py (`h-m2/code/mechanism.py`)

**Dependencies**: representation.py, scipy.stats, numpy

```python
def verify_invariance_mechanism(mps_verbatim: np.ndarray, mps_paraphrase: np.ndarray) -> dict:
    """t-test + Cohen's d; mechanism_active = mean(mps_paraphrase) > mean(mps_verbatim);
    logs [MECHANISM CHECK] per PRD FR-7.4"""

def aggregate_across_seeds(results_per_seed: list[dict]) -> dict:
    """Mean/std of MPS difference and effect_size across 3 seeds; reproducibility 3/3 check"""
```

### evaluate.py (`h-m2/code/evaluate.py`)

**Dependencies**: representation.py

```python
def evaluate_representation_invariance(model, tokenizer, eval_items: list[dict],
                                        paraphrase_bank: dict) -> np.ndarray:
    """Wraps evaluate_invariance for 1000-item eval subset (FR-4.4)"""

def build_eval_subset(contaminated_items: Dataset, n: int = 1000, seed: int = 42) -> list[dict]:
    """Deterministic subsample of contaminated items for representation eval"""
```

### train.py (`h-m2/code/train.py`)

**Dependencies**: data.py, model.py, representation.py, mechanism.py, evaluate.py

```python
def run_experiment(config: Config) -> None:
    """
    For each seed in config.seeds:
      1. load_mmlu, sample_contamination_ids(frac=0.10), build_training_dataset
      2. load_paraphraser, build_paraphrase_bank (k=5)
      3. build_augmented_training_set (k_train=3)
      4. train_verbatim_model, train_paraphrase_model
      5. build_eval_subset (n=1000)
      6. evaluate_representation_invariance for both models -> mps_verbatim, mps_paraphrase
      7. verify_invariance_mechanism -> per-seed result
    aggregate_across_seeds -> final mechanism_active, effect_size
    Save results/mechanism_results.json
    """
```

### visualize.py (`h-m2/code/visualize.py`)

**Dependencies**: matplotlib, mechanism_results.json

```python
def plot_mps_distribution(mps_verbatim: np.ndarray, mps_paraphrase: np.ndarray) -> None:
    """Histogram/density comparison -> figures/mps_distribution.png (required)"""

def plot_mps_boxplot(mps_verbatim: np.ndarray, mps_paraphrase: np.ndarray) -> None:
    """Side-by-side box plot -> figures/mps_boxplot.png (required)"""

def plot_tsne_representations(reps_verbatim: np.ndarray, reps_paraphrase: np.ndarray) -> None:
    """Optional t-SNE colored by condition -> figures/tsne_representations.png"""
```

### config.py (`h-m2/code/config.py`)

```python
@dataclass
class Config:
    model_id: str = "mistralai/Mistral-7B-v0.1"
    lora_rank: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: tuple = ("q_proj", "v_proj", "k_proj", "o_proj")
    lr: float = 2e-5
    batch_size: int = 4
    grad_accum: int = 8
    epochs_verbatim: int = 12
    epochs_paraphrase: int = 3
    contamination_frac: float = 0.10
    k_paraphrases_bank: int = 5
    k_paraphrases_train: int = 3
    n_eval_items: int = 1000
    seeds: tuple = (42, 123, 456)
    mps_diff_threshold: float = 0.05
    effect_size_target: float = 0.3
```

---

## File Organization

```
h-m2/code/
  config.py
  data.py
  model.py
  representation.py
  mechanism.py
  evaluate.py
  train.py
  visualize.py
h-m2/results/
  mechanism_results.json
  paraphrase_bank.json
h-m2/figures/
  mps_distribution.png
  mps_boxplot.png
  tsne_representations.png
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M2-1 | Paraphrase generation pipeline | T5-paraphrase + rule-based fallback, K=5 bank, cache to disk | 12 | 3+3+3+3 |
| M2-2 | Augmented dataset construction | Reuse H-M1 sampling; build verbatim & augmented training sets | 5 | 2+1+2 |
| M2-3 | Verbatim baseline training | Reuse inject_contamination, epoch-matched compute (12 epochs) | 8 | 3+3+2 |
| M2-4 | Paraphrase-augmented training | Reuse inject_contamination on augmented set (3 epochs) | 8 | 3+3+2 |
| M2-5 | Representation extraction | Hidden state extraction + mean pooling, batched, both models | 14 | 4+4+3+3 |
| M2-6 | Similarity computation | Cosine similarity, MPS per item, eval-subset orchestration | 5 | 2+1+2 |
| M2-7 | Statistical mechanism verification | t-test, Cohen's d, mechanism_active logging, cross-seed aggregation | 8 | 3+3+2 |
| M2-8 | Visualization | Distribution histogram, box plot, optional t-SNE | 5 | 2+1+2 |
| M2-9 | Experiment orchestration | Wire 3-seed loop, checkpointing, results JSON persistence | 8 | 3+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [M2-5], Medium(9-13): [M2-1], Low(4-8): [M2-2, M2-3, M2-4, M2-6, M2-7, M2-8, M2-9]

**Total subtasks**: 3+2+3+3+4+2+3+2+3 (using max breakdown counts above, e.g. M2-1 has 4) = 4+3+3+3+4+3+3+3+3 = 29 (within FULL tier budget of 30).

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| load_mmlu | `from h_m1.code.data import load_mmlu` | `h-m1/code/data.py` |
| sample_contamination_ids | `from h_m1.code.data import sample_contamination_ids` | `h-m1/code/data.py` |
| build_training_dataset | `from h_m1.code.data import build_training_dataset` | `h-m1/code/data.py` |
| format_mmlu_prompt | `from h_m1.code.data import format_mmlu_prompt` | `h-m1/code/data.py` |
| load_base_model | `from h_m1.code.model import load_base_model` | `h-m1/code/model.py` |
| build_lora_config_m1 | `from h_m1.code.model import build_lora_config_m1` | `h-m1/code/model.py` |
| inject_contamination | `from h_m1.code.model import inject_contamination` | `h-m1/code/model.py` |
| format_training_example | `from h_m1.code.model import format_training_example` | `h-m1/code/model.py` |

**Verified from**: `h-m1/code/data.py`, `h-m1/code/model.py`, `h-m1/code/config.py` (actual implementation). Note: brief's assumption of a saved checkpoint at `h-m1/checkpoints/contaminated_10pct` is **incorrect** — `inject_contamination` returns an in-memory `PeftModel` only; H-M2 must retrain verbatim baseline via direct function call, not checkpoint load.
