# Architecture: H-M1 (MECHANISM)

**Hypothesis:** CCR(perplexity-filtered) - CCR(random) > 0.1, p<0.05 bootstrap
**Type:** MECHANISM — 3 conditions × 5 seeds = 15 trained Pythia-1B models

Applied: contamination-attribution-pipeline pattern (n-gram detection + linear/bootstrap comparison, reused from H-E1 design)

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (h-e1) — but no actual code present
**Status:** `h-e1/code/` directory does not exist yet (glob returned no files). Only `h-e1/03_architecture.md` spec is available.
**Analyzed Path:** `docs/youra_research/h-e1/code/`
**Findings:** No implemented code to import from. Per spec-vs-code rule, since no actual code exists, H-M1 must re-implement the n-gram detector and CCR function locally (do not assume unverified import paths). Interfaces below mirror H-E1's spec (`detect.py: ngram_overlap_detect`, `model.py: compute_ccr`) but are copied into h-m1/code/ rather than imported cross-hypothesis, since there is no verified package path.

---

## File Structure

```
h-m1/code/
  config.py       # 3 strategies x 5 seeds config
  data.py         # RedPajama loading, perplexity filtering, MMLU injection
  detect.py       # 8-gram overlap detector (from H-E1, n=8 per ConTAM)
  train.py        # Pythia-1B training loop per (strategy, seed)
  evaluate.py     # CCR, MMLU accuracy, bootstrap test
  visualize.py    # 4 required figures
  main.py         # orchestrates 15 runs
figures/
```

---

## Modules

### Config (`config.py`)

**Dependencies**: None

```python
@dataclass
class Config:
    model_id: str = "EleutherAI/pythia-1b"
    strategies: tuple = ("perplexity", "random", "inverse_perplexity")
    seeds: tuple = (42, 43, 44, 45, 46)
    percentile: int = 30
    ngram_n: int = 8
    injection_rates: tuple = (0.001, 0.005, 0.01)
    lr: float = 2.5e-4
    betas: tuple = (0.9, 0.95)
    eps: float = 1e-8
    weight_decay: float = 0.1
    warmup_ratio: float = 0.01
    min_lr: float = 2.5e-5
    batch_size: int = 512
    seq_len: int = 2048
    train_tokens: int = 1_000_000_000
    grad_clip: float = 1.0
    out_dir: str = "figures/"
```

### Data (`data.py`)

**Dependencies**: Config

```python
def load_redpajama_stream(cfg: Config): ...
def extract_perplexity(sample: dict) -> float: ...
def filter_by_strategy(dataset, strategy: str, percentile: int, seed: int) -> list[str]: ...
def load_mmlu() -> list[dict]: ...
def inject_mmlu(corpus: list[str], mmlu: list[dict], rate: float, seed: int) -> tuple[list[str], list[int]]: ...
```

### Detector (`detect.py`)

**Dependencies**: None (copied from H-E1 spec, n=8)

```python
def ngram_overlap_detect(corpus: list[str], benchmark: list[dict], n: int = 8) -> set[int]: ...
```

### Train (`train.py`)

**Dependencies**: Config, Data, transformers

```python
def load_model_and_tokenizer(cfg: Config): ...
def train_one_run(cfg: Config, corpus: list[str], strategy: str, seed: int) -> PreTrainedModel: ...
def save_checkpoint(model, strategy: str, seed: int, out_dir: str) -> str: ...
```

### Evaluate (`evaluate.py`)

**Dependencies**: Config, Detector

```python
def compute_ccr(model_path: str, tokenizer, mmlu: list[dict], corpus: list[str], n: int = 8) -> float: ...
def eval_mmlu_accuracy(model_path: str, num_fewshot: int = 5) -> float:  # via lm-eval
    ...
def bootstrap_ccr_diff(ccr_ppl: np.ndarray, ccr_rand: np.ndarray, n_bootstrap: int = 1000) -> tuple[float, float]:  # (mean_diff, p_value)
    ...
```

### Visualize (`visualize.py`)

**Dependencies**: Config

```python
def plot_ccr_by_strategy(results: dict, out_dir: str) -> None: ...
def plot_ccr_boxplot(results: dict, out_dir: str) -> None: ...
def plot_bootstrap_histogram(diffs: np.ndarray, p_value: float, out_dir: str) -> None: ...
def plot_gate_metrics(target: dict, actual: dict, out_dir: str) -> None: ...
```

### Main (`main.py`)

**Dependencies**: all above

```python
def run_all(cfg: Config) -> dict:  # {strategy: {seed: {ccr, mmlu_acc}}}
    ...

if __name__ == "__main__":
    run_all(Config())
```

---

## External Dependencies (Base Hypothesis)

**Verified from**: `h-m1/../h-e1/code/` — directory does not exist (no actual implementation committed yet).

No import paths could be verified. `detect.py` (`ngram_overlap_detect`) and CCR logic are **re-implemented locally** in h-m1/code/ rather than imported from h-e1, matching H-E1's spec interface (n changed 13→8 per PRD FR-3.1/ConTAM recommendation). If h-e1/code/ is populated before Phase 4, Coder should re-check for reusable modules and import instead of duplicating.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Config + data loading | RedPajama streaming, quality_signals parsing | 6 | 2+1+2+1 |
| M-2 | Perplexity filtering | 3 strategy variants, size-matched 1B tokens | 8 | 2+2+2+2 |
| M-3 | MMLU injection | Load MMLU, inject at 3 rates, track positions | 5 | 1+1+2+1 |
| M-4 | 8-gram detector | Overlap detection (n=8, ConTAM) | 5 | 2+1+1+1 |
| M-5 | Training loop | Pythia-1B AdamW/cosine, 15 runs (3 strategy x 5 seed) | 12 | 3+3+3+3 |
| M-6 | CCR computation | Per-model CCR via detector | 6 | 2+2+1+1 |
| M-7 | MMLU eval | lm-eval harness integration, 5-shot | 6 | 2+2+1+1 |
| M-8 | Bootstrap statistics | 1000-resample diff test, p-value | 6 | 1+2+2+1 |
| M-9 | Visualization | 4 required figures | 5 | 2+1+1+1 |
| M-10 | Orchestration | main.py loop over 15 runs, checkpoint mgmt, gate check | 7 | 2+2+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M-2, M-5], Low(4-8): [M-1, M-3, M-4, M-6, M-7, M-8, M-9, M-10]

---

## Notes

- M-5 (training loop) is highest complexity: 15 full Pythia-1B training runs, multi-GPU required (NFR-1).
- h-e1/code/ not yet implemented; detector/CCR re-implemented per spec rather than cross-imported. Recheck at Phase 4 in case H-E1 code lands first.
