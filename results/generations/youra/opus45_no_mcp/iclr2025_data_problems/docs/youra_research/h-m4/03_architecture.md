# Architecture: H-M4 — SSI Captures Invariance as Contamination Signal

**Tier**: FULL (MECHANISM) | **Applied**: per-item variance aggregation -> inverse-variance score -> AUC/Pearson gate evaluation (same pattern as H-M1 SSI + H-M3 correlation gate)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1 checkpoints/SSI code, H-M3 confidence extraction code, H-E1 paraphrase artifacts)
**Status**: Actual code found and read directly (Serena MCP unavailable, used direct file read as fallback)
**Analyzed Path**: `docs/youra_research/h-m1/code/`, `docs/youra_research/h-m3/code/`, `docs/youra_research/h-e1/code/`
**Findings**: H-M1's `ssi.py` already implements `compute_ssi`/`compute_ssi_batch` (SSI=1/(var+1e-8), K=20 paraphrases, MMLU prompt format) — this is the primary reuse target. H-M3's `confidence.py` has a token-id-based confidence extractor (different interface: fixed A/B/C/D token, batched). H-M1's `data.py` has `load_mmlu`, `format_mmlu_prompt`, contamination sampling. No standalone H-E1 paraphrase-bank loader found; H-M1's `data.py` generates paraphrases inline via `generate_paraphrases` (imported in `ssi.py` but not present in the `data.py` read — verify at Coder time) or H-M3's `run_variance_extraction` consumes a `paraphrase_bank: dict` passed in. H-M4 should reuse H-M1's `ssi.py` almost as-is and only add: multi-checkpoint loop, per-item contamination labels, AUC/Pearson evaluation (new — no prior hypothesis computed AUC on SSI directly).

---

## Data Flow

```
H-M1 checkpoints (5: 0/5/10/20/50pct)
  + H-E1/H-M1 paraphrase bank (14,042 items x 20 paraphrases)
  -> [per checkpoint] compute_ssi_batch(model, tokenizer, items, answer_tokens, k=20)   [reuse h-m1/code/ssi.py]
  -> SSI array (n_items,) per checkpoint
  -> LabelBuilder: per-item contaminated/clean label (from H-M1 contamination_ids for that checkpoint)
  -> Evaluator: roc_auc_score(SSI, label) per checkpoint; pearsonr(contamination_pct, mean_SSI) across 5 checkpoints; cohens_d(SSI_0pct, SSI_50pct)
  -> Gate check: AUC>0.7 (primary), r>0.6 and d>0.5 (secondary)
  -> Visualize + write results/mechanism_results.json
```

---

## Components

### 1. SSI Computation (`h-m4/code/ssi.py`)

**Reuse**: `h-m1/code/ssi.py` (copy/import as-is, no changes needed)

```python
SSI_EPSILON = 1e-8

def extract_confidence(model, tokenizer, prompt: str, answer_tokens: list[int]) -> float: ...
def compute_ssi(model, tokenizer, item: dict, paraphrases: list[str],
                 answer_tokens: list[int]) -> tuple[float, list[float]]: ...
def compute_ssi_batch(model, tokenizer, items: list[dict], answer_tokens: list[int],
                       k_paraphrases: int = 20) -> tuple[list[float], list[list[float]]]: ...
```

### 2. Data / Checkpoint Loading (`h-m4/code/data.py`)

**Reuse**: `h-m1/code/data.py` (`load_mmlu`, `format_mmlu_prompt`, `sample_contamination_ids`)

```python
def load_mmlu() -> "Dataset": ...
def format_mmlu_prompt(item: dict) -> str: ...
def sample_contamination_ids(test_set, frac: float, seed: int) -> set: ...

def load_checkpoint(model_id: str, contamination_pct: int):
    """New: load one of 5 H-M1 checkpoints by contamination level (0/5/10/20/50)."""
```

### 3. LabelBuilder (`h-m4/code/labels.py`)

**New module** — no prior hypothesis needed binary per-item labels.

```python
def build_labels(item_ids: list[int], contaminated_ids: set) -> "np.ndarray":
    """1 if item_id in contaminated_ids else 0, shape (n_items,)."""
```

### 4. Evaluator (`h-m4/code/evaluate.py`)

**Partial reuse**: `h-m3/code/correlation.py` (`cohens_d`, pattern for pearsonr/verify_gate) — new AUC logic added.

```python
from sklearn.metrics import roc_auc_score
from scipy.stats import pearsonr

def compute_auc(ssi: "np.ndarray", labels: "np.ndarray") -> float: ...
def compute_pearson_by_level(mean_ssi_per_level: list[float],
                              contamination_pcts: list[float]) -> tuple[float, float]: ...
def cohens_d(group1: "np.ndarray", group2: "np.ndarray") -> float:  # reuse h-m3/code/correlation.py
    ...
def verify_gate(auc: float, r: float, d: float) -> dict:
    """PASS/PARTIAL/FAIL per PRD gate logic (AUC>0.7 primary; r>0.6, d>0.5 secondary)."""
```

### 5. Visualization (`h-m4/code/visualize.py`)

**Reuse pattern**: `h-m1/code/visualize.py`, `h-m3/code/viz_m3.py`

```python
def plot_ssi_distribution_by_level(ssi_by_level: dict) -> None: ...
def plot_roc_curve(ssi: "np.ndarray", labels: "np.ndarray", auc: float) -> None: ...
def plot_correlation_scatter(pcts: list[float], mean_ssi: list[float], r: float) -> None: ...
def plot_gate_bar(gate_result: dict) -> None: ...
```

### 6. Config (`h-m4/code/config.py`)

**Reuse pattern**: `h-m1/code/config.py`

```python
@dataclass
class Config:
    checkpoints: tuple = (0, 5, 10, 20, 50)  # contamination pct, maps to H-M1 checkpoints
    k_paraphrases: int = 20
    ssi_epsilon: float = 1e-8
    auc_threshold: float = 0.7
    pearson_threshold: float = 0.6
    cohens_d_threshold: float = 0.5
    n_items: int = 14042
    seeds: tuple = (42, 123, 456)
```

### 7. Run Script (`h-m4/code/run_experiment.py`)

**Reuse pattern**: `h-m3/code/run_experiment.py`

```python
def run_experiment(config: Config) -> dict:
    """Loop over 5 checkpoints, compute SSI batch, build labels, evaluate, save results."""
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Load H-M1 checkpoints + paraphrase bank | Verify 5 checkpoint paths load; confirm 14,042x20 paraphrase availability | 4 | 1+1+1+1 |
| A-2 | Wire SSI module | Import/adapt `h-m1/code/ssi.py` unchanged into h-m4/code | 2 | 1+1+0+0 |
| A-3 | Implement LabelBuilder | Per-checkpoint contaminated/clean label array from contamination_ids | 3 | 1+1+1+0 |
| A-4 | Implement AUC evaluation | roc_auc_score per checkpoint (5 runs) | 3 | 1+1+1+0 |
| A-5 | Implement Pearson + Cohen's d | Mean SSI per level -> pearsonr; d between 0pct/50pct SSI (reuse h-m3 cohens_d) | 3 | 1+1+1+0 |
| A-6 | Gate logic + config | verify_gate PASS/PARTIAL/FAIL, Config dataclass | 2 | 1+1+0+0 |
| A-7 | Build run_experiment pipeline | Loop 5 checkpoints x 14,042 items x 20 paraphrases, aggregate results | 7 | 3+2+2+0 |
| A-8 | Visualization suite | 4 required figures (distribution, ROC, scatter, gate bar) | 4 | 2+1+1+0 |
| A-9 | Run full experiment + write results.json | Execute pipeline end-to-end, validate against gate thresholds | 5 | 2+1+2+0 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1(4), A-2(2), A-3(3), A-4(3), A-5(3), A-6(2), A-7(7), A-8(4), A-9(5)]

Total: 9 Epic tasks (within FULL tier 6-12 band, well under 30-task cap).

---

## External Dependencies (Base Hypotheses)

### Module Paths (Verified from actual code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| SSI computation | `from ssi import compute_ssi_batch, SSI_EPSILON` (copy into h-m4/code) | `h-m1/code/ssi.py` |
| MMLU data/prompting | `from data import load_mmlu, format_mmlu_prompt, sample_contamination_ids` | `h-m1/code/data.py` |
| Cohen's d / gate pattern | `from correlation import cohens_d, verify_gate` (reference for gate style) | `h-m3/code/correlation.py` |
| Confidence extraction (alt) | `from confidence import get_answer_token_id, batch_extract_confidences` | `h-m3/code/confidence.py` |

**Verified from**: direct read of `h-m1/code/ssi.py`, `h-m1/code/data.py`, `h-m1/code/config.py`, `h-m3/code/confidence.py`, `h-m3/code/invariance_confidence.py`, `h-m3/code/correlation.py`, `h-m3/code/config.py` (2026-08-19).

**Note**: `h-m1/code/ssi.py` imports `generate_paraphrases` and `format_mmlu_with_paraphrase` from its local `data.py`, but these two functions were not present in the `data.py` excerpt read — Coder must verify their existence/location in `h-m1/code/data.py` (full file) before reuse, or source paraphrases from H-E1 artifacts instead.

---

## Self-Check

- 9 Epic tasks (within 6-12 band), complexity 2-7 (max task A-7 at 7, matches pipeline-loop scale)
- No new dependencies: reuses torch/numpy/scipy/sklearn already present in H-M1/H-M3 code
- No ASCII diagrams, module sections are interface-only
- ponytail: SSI module copied rather than cross-imported across hypothesis folders (avoids fragile relative imports between sibling dirs) — if a shared `common/` package emerges later, consolidate
