# Architecture: h-m1 (MECHANISM)

**Hypothesis:** Semantic entropy achieves AUROC >= 0.70 on TruthfulQA mc1 via NLI-clustered generations
**Type:** MECHANISM — reuses h-e1 data/model loaders, adds NLI clustering + dedicated mechanism verification.

Applied: NLI-clustering mechanism pipeline (generate -> cluster -> entropy -> AUROC -> verify)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: Reused h-e1's `data.py`/`model.py` interfaces directly (verified from `docs/youra_research/h-e1/03_architecture.md`; no separate code/ dir found to introspect beyond spec, so specs treated as implementation reference per h-e1 authorship). h-e1 already implements a `semantic_entropy` method inline in `UQMethodsWrapper` — h-m1 extracts/expands this into a standalone `SemanticEntropy` module per PRD FR-1..FR-3, with its own NLI model config and mechanism verification (not present in h-e1).
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: h-e1 provides `load_truthfulqa_mc1()` and `load_model_and_tokenizer()`/`generate_samples()` — reused as-is via import. No conflicting patterns.

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| load_truthfulqa_mc1 | `from h_e1.data import load_truthfulqa_mc1` | `docs/youra_research/h-e1/code/data.py` |
| load_model_and_tokenizer | `from h_e1.model import load_model_and_tokenizer` | `docs/youra_research/h-e1/code/model.py` |
| generate_samples | `from h_e1.model import generate_samples` | `docs/youra_research/h-e1/code/model.py` |

**Verified from**: `docs/youra_research/h-e1/03_architecture.md` (h-e1 module interfaces section)

---

## File Organization

```
docs/youra_research/h-m1/code/
├── config.py            # fixed hyperparams (N=10, temp=0.7, threshold=0.7, seed=42)
├── nli_cluster.py        # DeBERTa-mnli entailment + greedy clustering
├── semantic_entropy.py    # SemanticEntropy class: generate -> cluster -> entropy
├── baselines.py           # loads h-e1 max_prob/choice_entropy scores for comparison
├── evaluate.py            # AUROC computation, mechanism verification, gate check
├── visualize.py           # AUROC bar chart, cluster histogram, correlation scatter, ROC overlay
├── run_experiment.py      # main entrypoint
└── results/                # scores.csv, metrics.json, cluster_stats.json
docs/youra_research/h-m1/figures/
```

## Data Flow

1. `data.py` (imported from h-e1) loads TruthfulQA mc1 -> 817 `{question, choices, correct_idx}`
2. `semantic_entropy.py` generates N=10 samples per question via h-e1's `generate_samples()`
3. `nli_cluster.py` computes bidirectional entailment for sample pairs, greedy-clusters at threshold=0.7
4. `semantic_entropy.py` computes cluster-size distribution entropy per question
5. `baselines.py` loads h-e1's `results/scores.csv` for max_prob (0.8068) / choice_entropy (0.7703)
6. `evaluate.py` computes semantic_entropy AUROC, runs mechanism verification (avg_clusters<10, entropy variance>0), applies 0.70 gate
7. `visualize.py` renders comparison bar chart + cluster/correlation/ROC figures

---

## Module Interfaces

### config.py

```python
SEED: int = 42
NUM_SAMPLES: int = 10
TEMPERATURE: float = 0.7
MAX_NEW_TOKENS: int = 128
ENTAILMENT_THRESHOLD: float = 0.7
AUROC_GATE: float = 0.70
NLI_MODEL_ID: str = "microsoft/deberta-v3-large-mnli"
```

### nli_cluster.py (`code/nli_cluster.py`)

**Dependencies**: transformers, torch, config

```python
def load_nli_model(model_id: str) -> tuple: ...  # (model, tokenizer)

def entailment_prob(nli_model, nli_tokenizer, premise: str, hypothesis: str) -> float: ...
# returns P(entailment) from softmax[2]

def bidirectional_entailment(nli_model, nli_tokenizer, text1: str, text2: str, threshold: float) -> bool: ...

def cluster_samples(nli_model, nli_tokenizer, samples: list[str], threshold: float) -> list[list[str]]: ...
# greedy clustering against first member of each cluster
```

### semantic_entropy.py (`code/semantic_entropy.py`)

**Dependencies**: nli_cluster, h_e1.model (generate_samples), scipy, numpy

```python
class SemanticEntropy:
    def __init__(self, llm_model, llm_tokenizer, nli_model, nli_tokenizer,
                 num_samples: int = 10, threshold: float = 0.7): ...
    def compute(self, prompt: str, temperature: float = 0.7, max_tokens: int = 128) -> dict: ...
    # returns {"semantic_entropy": float, "num_clusters": int,
    #          "cluster_sizes": list[int], "samples": list[str]}

def score_dataset(se: SemanticEntropy, questions: list[dict]) -> list[dict]: ...
# returns per-question dicts merging compute() output + correct_idx label
```

### baselines.py (`code/baselines.py`)

**Dependencies**: pandas

```python
def load_h_e1_scores(scores_csv_path: str) -> dict[str, list[float]]: ...
# returns {"max_prob": [...], "choice_entropy": [...]}, aligned by question index
```

### evaluate.py (`code/evaluate.py`)

**Dependencies**: sklearn.metrics, numpy, config

```python
def compute_auroc(y_true: list[int], scores: list[float]) -> float: ...

def verify_mechanism(results: list[dict]) -> dict: ...
# checks: avg_clusters < num_samples, entropy std > 0, cluster sizes vary
# returns {"avg_clusters": float, "entropy_std": float, "passed": bool}

def apply_gate(semantic_auroc: float, threshold: float = 0.70) -> dict: ...
# returns {"gate": "PASSED"|"FAILED", "action": str, "result": str}
```

### visualize.py (`code/visualize.py`)

**Dependencies**: matplotlib, evaluate

```python
def plot_auroc_comparison(aurocs: dict[str, float], out_path: str) -> None: ...
def plot_cluster_histogram(results: list[dict], out_path: str) -> None: ...
def plot_score_correlation(semantic_scores: list[float], max_prob_scores: list[float], out_path: str) -> None: ...
def plot_roc_overlay(y_true, scores: dict[str, list[float]], out_path: str) -> None: ...
```

### run_experiment.py (`code/run_experiment.py`)

**Dependencies**: all above, h_e1.data, h_e1.model

```python
def main() -> None: ...
# load data -> load LLM + NLI models -> score_dataset -> load baselines ->
# compute_auroc -> verify_mechanism -> apply_gate -> visualize -> write results/
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Wire h-e1 data/model imports | Import & verify load_truthfulqa_mc1, load_model_and_tokenizer, generate_samples reuse | 4 | 1+2+1+0 |
| M-2 | Load NLI model | DeBERTa-v3-large-mnli load + entailment_prob helper | 5 | 2+1+1+1 |
| M-3 | Implement bidirectional entailment + greedy clustering | cluster_samples with threshold=0.7, batching for efficiency | 9 | 2+2+3+2 |
| M-4 | Implement SemanticEntropy class | generate -> cluster -> entropy computation, per-question | 8 | 2+2+3+1 |
| M-5 | Score full dataset (817 Qs) | Loop questions, cache NLI results, log cluster stats | 9 | 2+3+2+2 |
| M-6 | Load h-e1 baseline scores | Parse h-e1 results/scores.csv, align indices | 4 | 1+2+1+0 |
| M-7 | Compute AUROC + mechanism verification | AUROC calc, avg_clusters/entropy-variance checks, apply 0.70 gate | 7 | 2+2+2+1 |
| M-8 | Build visualizations | Bar chart, cluster histogram, correlation scatter, ROC overlay | 6 | 2+1+1+2 |
| M-9 | Integrate end-to-end run | Wire run_experiment.py, execute full pipeline, write results/ | 7 | 2+3+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M-3, M-5], Low(4-8): [M-1, M-2, M-4, M-6, M-7, M-8, M-9]
