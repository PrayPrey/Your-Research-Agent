# Architecture: H-M2 (Robustness of Routing to Paraphrase/Masking)

Applied: sklearn-Pipeline-Evaluation-Pattern (frozen encoder + linear probe, no training loop)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: Analyzed actual H-E1 code (not just specs)
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**:
- `model.py::AdapterSelectionProbe` wraps `SentenceTransformer` + `LogisticRegression`, exposes `encode/fit/predict/predict_proba/evaluate`.
- **Critical deviation from PRD**: `train.py` never pickles the probe (no `joblib.dump`). Only `experiment_results.json` and `outputs/results.csv` are persisted. PRD's `h-e1/probe_model.pkl` does **not exist**.
- Fix: H-M2 must **re-run H-E1's exact pipeline** (`stream_instructions` + `stratified_split` + `AdapterSelectionProbe.fit`, same `CONFIG`/seed) in-process to reconstruct an equivalent probe and test set, rather than loading a missing artifact.
- `data.py::stream_instructions` re-derives `task_families` dynamically each run (Counter-based) — must reuse same `random_state=42` for reproducible family discovery/order.
- `evaluate.py` has 4 plot functions (`plot_gate_metrics`, `plot_confusion_matrix`, `plot_per_class_accuracy`, `plot_embedding_tsne`) — pattern to follow for new figures.

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| Config/CONFIG | `from h_e1.config import CONFIG` | `docs/youra_research/h-e1/code/config.py` |
| stream_instructions, encode_labels, stratified_split | `from h_e1.data import stream_instructions, encode_labels, stratified_split` | `docs/youra_research/h-e1/code/data.py` |
| AdapterSelectionProbe | `from h_e1.model import AdapterSelectionProbe` | `docs/youra_research/h-e1/code/model.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation; PRD's pkl artifact path is stale)

**Reuse note**: Copy the three files above (or import via relative path if run from sibling dir) — no code changes needed. Do not re-implement classifier logic.

## File Organization

- `code/config.py` — H-M2 config (perturbation params, gate thresholds)
- `code/reuse_probe.py` — reconstructs H-E1 probe + test split in-process
- `code/perturb.py` — paraphrase (TextAttack) + keyword masking (nlpaug) generators
- `code/robustness_eval.py` — cosine similarity, routing consistency, accuracy drop
- `code/visualize.py` — 4 required figures
- `code/train.py` — orchestration entrypoint (mirrors H-E1 `train.py` structure)

## Modules

### Config (`code/config.py`)

**Dependencies**: none

```python
@dataclass
class MConfig:
    wordnet_pct_swap: float = 0.3
    wordnet_n: int = 5
    embedding_n: int = 3
    embedding_min_cosine: float = 0.8
    mask_ratios: tuple = (0.2, 0.5)
    random_state: int = 42  # must match H-E1

COSINE_PASS = 0.90
COSINE_FAIL = 0.80
ACC_DROP_PASS = 0.10
ACC_DROP_FAIL = 0.20
ROUTING_CONSISTENCY_PASS = 0.85
ROUTING_CONSISTENCY_FAIL = 0.70
```

### ProbeContext (`code/reuse_probe.py`)

**Dependencies**: h_e1.config, h_e1.data, h_e1.model

```python
@dataclass
class ProbeContext:
    probe: "AdapterSelectionProbe"
    X_test: list[str]
    y_test: list[int]
    task_families: list[str]

def build_probe_context(m_cfg: MConfig) -> ProbeContext: ...
```

### PerturbationEngine (`code/perturb.py`)

**Dependencies**: textattack, nlpaug

```python
class PerturbationEngine:
    def __init__(self, m_cfg: MConfig): ...
    def wordnet_paraphrases(self, text: str) -> list[str]: ...
    def embedding_paraphrases(self, text: str) -> list[str]: ...
    def mask_keywords(self, text: str, ratio: float) -> str: ...
    def mask_random(self, text: str, ratio: float) -> str: ...
```

### RobustnessEvaluator (`code/robustness_eval.py`)

**Dependencies**: ProbeContext, PerturbationEngine, sklearn.metrics.pairwise

```python
def eval_paraphrase_robustness(ctx: ProbeContext, engine: PerturbationEngine, variant: str) -> dict: ...
    # returns: cosine_mean, cosine_min, routing_consistency, per_sample: list[dict]

def eval_masking_robustness(ctx: ProbeContext, engine: PerturbationEngine, ratio: float, mode: str) -> dict: ...
    # returns: original_acc, masked_acc, accuracy_drop

def per_class_consistency(ctx: ProbeContext, results: list[dict]) -> dict: ...
    # class_name -> consistency rate, for heatmap
```

### Visualization (`code/visualize.py`)

**Dependencies**: matplotlib, seaborn, robustness_eval outputs

```python
def plot_gate_metrics(cosine_mean: float, acc_drop: float, path: str) -> None: ...
def plot_cosine_distribution(cosine_values: list[float], path: str) -> None: ...
def plot_drop_by_perturbation(drops: dict[str, float], path: str) -> None: ...
def plot_per_class_heatmap(per_class: dict, path: str) -> None: ...
def plot_failure_cases(failures: list[dict], path: str, n: int = 5) -> None: ...
```

### Orchestration (`code/train.py`)

**Dependencies**: all above

```python
def main() -> str:  # returns gate_result: PASS/PARTIAL/FAIL
    ...
```

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Reconstruct H-E1 probe context | Reuse config/data/model to rebuild probe + test split (450 samples) in-process | 10 | 3+3+2+2 |
| A-2 | Config module | M-Config dataclass with perturbation params + gate thresholds | 4 | 1+1+1+1 |
| A-3 | WordNet paraphrase generator | TextAttack WordNetAugmenter wrapper, 5 paraphrases/sample | 8 | 2+3+2+1 |
| A-4 | Embedding paraphrase generator | TextAttack EmbeddingAugmenter wrapper, cosine≥0.8 filter | 8 | 2+3+2+1 |
| A-5 | Keyword + random masking | nlpaug TfIdfAug for keyword mask (20%/50%) + random-word control mask | 9 | 2+3+3+1 |
| A-6 | Cosine/routing metrics | Compute cosine sim + routing consistency across all paraphrase variants | 10 | 2+3+3+2 |
| A-7 | Accuracy drop metrics | Compute original vs masked accuracy for keyword/random masking variants | 8 | 2+2+2+2 |
| A-8 | Per-class robustness aggregation | Aggregate routing consistency per FLAN task family for heatmap | 6 | 2+2+1+1 |
| A-9 | Visualization suite | 4 required figures (gate, cosine dist, drop-by-type, heatmap) + failure examples | 9 | 3+2+2+2 |
| A-10 | Orchestration + gate check | train.py wiring all modules, JSON/CSV results, gate PASS/PARTIAL/FAIL logic | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-5, A-6, A-9], Low(4-8): [A-2, A-3, A-4, A-7, A-8, A-10]
