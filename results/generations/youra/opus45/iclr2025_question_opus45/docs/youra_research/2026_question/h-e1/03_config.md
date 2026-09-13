# Config: h-e1 SEDP Existence Validation

**Hypothesis**: EXISTENCE (PoC)
**Applied**: Standard sklearn-logistic-regression probe pattern (SEP paper, Kossen et al. 2024)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## A-4: Similarity Feature Computation [Complexity: 10, Budget: 3]

**Applied**: Standard sentence-transformers embedding pattern

### Configuration

```python
from dataclasses import dataclass, field

@dataclass
class ExperimentConfig:
    # --- Data ---
    dataset_name: str = "truthfulqa/truthful_qa"
    dataset_config: str = "generation"
    test_size: float = 0.2
    seed: int = 42

    # --- Generation ---
    llm_name: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    n_responses: int = 20
    temperature: float = 0.7
    max_new_tokens: int = 100
    layer_idx: int = 25           # Middle-to-late layer per SEP paper recommendation

    # --- SE Labels ---
    nli_model_name: str = "microsoft/deberta-v3-large-mnli"
    entailment_threshold: float = 0.5

    # --- Similarity Features ---
    # sentence-transformers model for response embeddings
    embedder_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    # Output: (N, 4) [mean, std, min, max] of pairwise cosine similarities

    # --- Probe ---
    probe_C: float = 1.0
    probe_max_iter: int = 1000    # Sufficient for LBFGS convergence on ~653 samples

    # --- Evaluation ---
    rho_threshold: float = 0.3    # Gate threshold: SEDP rho >= 0.3 to pass

    # --- Paths ---
    cache_dir: str = "h-e1/cache"
    figures_dir: str = "h-e1/figures"
    results_path: str = "h-e1/04_validation.md"
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | EmbedderConfig | embedder_name default for sentence-transformers |
| C-4-2 | SimFeatureShape | Document output shape (N, 4) in config comments |
| C-4-3 | CachePaths | cache_dir, figures_dir, results_path defaults |

---

## A-5: Probe Training (SEP + SEDP) [Complexity: 9, Budget: 3]

**Applied**: sklearn LogisticRegression defaults from SEP paper

### Configuration

```python
# Probe config fields (within ExperimentConfig above):
#   probe_C: float = 1.0        - L2 regularization strength (SEP paper default)
#   probe_max_iter: int = 1000  - LBFGS iterations
#
# SEP input:  (N, 4096)   hidden states only
# SEDP input: (N, 4100)   hidden states + 4 similarity features
#
# Both probes: LogisticRegression(C=probe_C, max_iter=probe_max_iter, solver="lbfgs")
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | ProbeRegularization | probe_C=1.0, solver=lbfgs per SEP paper |
| C-5-2 | FeatureDimensions | SEP=4096, SEDP=4100 documented |
| C-5-3 | TrainSplit | test_size=0.2, seed=42 for reproducibility |

---

## A-6: Evaluation & Visualization [Complexity: 11, Budget: 3]

**Applied**: scipy.stats.spearmanr + sklearn.metrics.roc_auc_score pattern

### Configuration

```python
# Evaluation config fields (within ExperimentConfig above):
#   rho_threshold: float = 0.3  - Gate: SEDP rho >= 0.3 (MUST_WORK condition)
#
# Metrics computed:
#   spearman_rho  - scipy.stats.spearmanr(predicted_se, true_se_continuous)
#   p_value       - from spearmanr output
#   auroc         - sklearn.metrics.roc_auc_score(se_binary, predicted_proba)
#
# Figures saved to figures_dir:
#   gate_metrics.png  - bar chart: SEP vs SEDP rho with threshold line
#   scatter.png       - predicted SE vs true SE scatter
#   roc_curves.png    - ROC comparison
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | GateThreshold | rho_threshold=0.3 in config |
| C-6-2 | MetricsSpec | spearman_rho, p_value, auroc fields in results dict |
| C-6-3 | FiguresPaths | figures_dir default, 3 figure filenames documented |

---

## Hyperparameter Table

| Parameter | Value | Source |
|-----------|-------|--------|
| dataset_name | truthfulqa/truthful_qa | SEP paper (Kossen et al., 2024) |
| dataset_config | generation | TruthfulQA HF config |
| test_size | 0.2 | Standard 80/20 split |
| seed | 42 | Fixed for reproducibility |
| llm_name | meta-llama/Meta-Llama-3-8B-Instruct | SEP paper |
| n_responses | 20 | SEP paper |
| temperature | 0.7 | SEP paper |
| max_new_tokens | 100 | SEP paper |
| layer_idx | 25 | SEP paper (middle-to-late, layers 23-27 for Llama-3-8B) |
| nli_model_name | microsoft/deberta-v3-large-mnli | jlko/semantic_uncertainty |
| entailment_threshold | 0.5 | SEP paper |
| embedder_name | sentence-transformers/all-MiniLM-L6-v2 | Lightweight default for similarity stats |
| probe_C | 1.0 | SEP paper (sklearn default) |
| probe_max_iter | 1000 | Sufficient for LBFGS on N~653 |
| rho_threshold | 0.3 | Phase 2B gate condition |

---

## YAML Schema

```yaml
experiment_config:
  data:
    dataset_name: "truthfulqa/truthful_qa"
    dataset_config: "generation"
    test_size: 0.2
    seed: 42
  generation:
    llm_name: "meta-llama/Meta-Llama-3-8B-Instruct"
    n_responses: 20
    temperature: 0.7
    max_new_tokens: 100
    layer_idx: 25
  se_labels:
    nli_model_name: "microsoft/deberta-v3-large-mnli"
    entailment_threshold: 0.5
  similarity_features:
    embedder_name: "sentence-transformers/all-MiniLM-L6-v2"
  probe:
    probe_C: 1.0
    probe_max_iter: 1000
  evaluation:
    rho_threshold: 0.3
  paths:
    cache_dir: "h-e1/cache"
    figures_dir: "h-e1/figures"
    results_path: "h-e1/04_validation.md"
```

---

*Generated by Configuration Agent - Phase 3*
*Hypothesis: h-e1 EXISTENCE (PoC)*
*All hyperparameters sourced from SEP paper (Kossen et al., 2024)*
