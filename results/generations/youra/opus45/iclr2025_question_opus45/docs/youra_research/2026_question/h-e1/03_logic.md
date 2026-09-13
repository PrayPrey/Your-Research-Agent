# Logic Design: h-e1 SEDP Existence Validation

**Applied**: sklearn-logistic-regression-probe pattern (OATML/semantic-entropy-probes)
**Applied**: Standard PyTorch hidden state extraction pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design, no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Setup & Data Loading [Complexity: 6]

### API Signatures

```python
# config.py
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    dataset_name: str = "truthfulqa/truthful_qa"
    dataset_config: str = "generation"
    test_size: float = 0.2
    seed: int = 42
    llm_name: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    n_responses: int = 20
    temperature: float = 0.7
    max_new_tokens: int = 100
    layer_idx: int = 25
    nli_model_name: str = "microsoft/deberta-v3-large-mnli"
    entailment_threshold: float = 0.5
    probe_C: float = 1.0
    probe_max_iter: int = 1000
    cache_dir: str = "h-e1/cache"
    figures_dir: str = "h-e1/figures"
    results_path: str = "h-e1/04_validation.md"
```

---

## A-2: Response Generation & Hidden State Extraction [Complexity: 16, Budget: 4 subtasks]

### API Signatures

```python
# data_pipeline.py
import numpy as np
from typing import Optional

class DataPipeline:
    def __init__(self, config: ExperimentConfig) -> None:
        """Initialize with config, load tokenizer + model lazily."""
        ...

    def load_dataset(self) -> tuple[list[str], list[str]]:
        """Load TruthfulQA, split 80/20 seed=42. Returns (train_qs, test_qs)."""
        ...

    def generate_responses(
        self,
        questions: list[str],
    ) -> tuple[np.ndarray, list[list[str]]]:
        """Generate N=20 responses per question, extract layer-25 TBG hidden states.

        Returns:
            hidden_states: np.ndarray  # [N, 4096]
            responses:     list[list[str]]  # [N][n_responses=20]
        """
        ...

    def load_or_generate(
        self,
        questions: list[str],
        split: str,  # "train" | "test"
    ) -> tuple[np.ndarray, list[list[str]]]:
        """Cache-aware wrapper. Loads .npy/.json from cache_dir or calls generate_responses."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| hidden_states | [N, 4096] | Layer 25, TBG token, float16 -> float32 |
| responses | [N][20] | list of lists of strings |

### Pseudo-code: generate_responses

```
For each question q in questions:
    prompt = format_chat_template(q)
    input_ids = tokenizer(prompt)

    For i in range(n_responses=20):
        with torch.no_grad():
            output = model.generate(input_ids, temperature=0.7,
                                    max_new_tokens=100,
                                    output_hidden_states=True,
                                    return_dict_in_generate=True)

        # TBG = last token of prompt (index -1 of input_ids)
        tbg_hidden = output.hidden_states[0][layer_idx=25][:, -1, :]  # [1, 4096]
        responses_q.append(decode(output.sequences[0, len(input_ids):]))

    hidden_states[q_idx] = tbg_hidden.squeeze().cpu().float().numpy()  # use first response TBG
    all_responses[q_idx] = responses_q

Save: np.save(cache/hidden_states_{split}.npy, hidden_states)
Save: json.dump(cache/responses_{split}.json, all_responses)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Model Loading | Load Llama-3-8B-Instruct with output_hidden_states=True, float16 |
| L-2-2 | TBG Extraction | Extract layer-25 hidden state at last-prompt-token position |
| L-2-3 | Generation Loop | N=20 responses per question with temperature=0.7 sampling |
| L-2-4 | Cache I/O | Save/load hidden_states_{split}.npy + responses_{split}.json |

---

## A-3: SE Label Generation [Complexity: 15, Budget: 4 subtasks]

### API Signatures

```python
# se_labels.py
class SELabelGenerator:
    def __init__(self, config: ExperimentConfig) -> None:
        """Load DeBERTa-v3-large-mnli tokenizer + model."""
        ...

    def check_entailment(self, premise: str, hypothesis: str) -> bool:
        """Run NLI, return True if entailment class probability > threshold=0.5."""
        ...

    def get_semantic_clusters(self, responses: list[str]) -> list[int]:
        """Bidirectional NLI clustering.

        Args:
            responses: list[str]  # length n_responses=20
        Returns:
            cluster_ids: list[int]  # length n_responses, cluster ids 0..K-1
        """
        ...

    def compute_se(self, responses: list[str]) -> float:
        """H_SE = -sum(p_i * log(p_i)) over semantic clusters.

        Returns:
            se: float  # semantic entropy value >= 0
        """
        ...

    def compute_se_labels(
        self,
        all_responses: list[list[str]],
    ) -> tuple[np.ndarray, np.ndarray]:
        """Compute SE for all questions; binarize at median.

        Returns:
            se_continuous: np.ndarray  # [N,] float SE values
            se_binary:     np.ndarray  # [N,] int {0,1} high/low (1=high SE)
        """
        ...

    def load_or_compute(
        self,
        all_responses: list[list[str]],
        split: str,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Cache wrapper: loads se_labels_{split}.npy or calls compute_se_labels."""
        ...
```

### Pseudo-code: SE Computation

```
# Bidirectional NLI clustering
get_semantic_clusters(responses):
    cluster_ids = [-1] * len(responses)
    next_cluster = 0

    For i, r_i in enumerate(responses):
        if cluster_ids[i] == -1:
            cluster_ids[i] = next_cluster
            next_cluster += 1
        For j in range(i+1, len(responses)):
            if cluster_ids[j] == -1:
                fwd = check_entailment(r_i, responses[j])
                bwd = check_entailment(responses[j], r_i)
                if fwd and bwd:
                    cluster_ids[j] = cluster_ids[i]

    Return cluster_ids

# SE entropy formula
compute_se(responses):
    cluster_ids = get_semantic_clusters(responses)
    counts = Counter(cluster_ids)
    total = len(responses)
    probs = [c / total for c in counts.values()]
    H_SE = -sum(p * log(p) for p in probs if p > 0)
    Return H_SE

# Binarization at median
compute_se_labels(all_responses):
    se_vals = [compute_se(r) for r in all_responses]  # [N]
    se_continuous = np.array(se_vals)
    median = np.median(se_continuous)
    se_binary = (se_continuous > median).astype(int)
    Return se_continuous, se_binary
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | NLI Model | Load DeBERTa-v3-large-mnli, check_entailment with threshold=0.5 |
| L-3-2 | Clustering | Bidirectional NLI clustering, assign cluster ids |
| L-3-3 | SE Formula | H_SE = -sum(p_i * log(p_i)) over cluster proportions |
| L-3-4 | Binarize + Cache | Median threshold binarization; save se_labels_{split}.npy |

---

## A-4: Similarity Feature Computation [Complexity: 10]

### API Signatures

```python
# similarity_features.py
class SimilarityFeatureExtractor:
    def __init__(self, config: ExperimentConfig) -> None:
        """Load sentence-transformers model (all-MiniLM-L6-v2)."""
        ...

    def embed_responses(self, responses: list[str]) -> np.ndarray:
        """Embed responses via sentence-transformers.

        Returns:
            embeddings: np.ndarray  # [n_responses, embed_dim=384]
        """
        ...

    def compute_similarity_stats(self, embeddings: np.ndarray) -> np.ndarray:
        """Pairwise cosine similarity upper-triangle stats.

        Args:
            embeddings: np.ndarray  # [n_responses, embed_dim]
        Returns:
            stats: np.ndarray  # [4,] = [mean, std, min, max]
        """
        ...

    def extract_features(self, all_responses: list[list[str]]) -> np.ndarray:
        """Extract similarity stats for all questions.

        Returns:
            sim_features: np.ndarray  # [N, 4]
        """
        ...

    def load_or_extract(
        self,
        all_responses: list[list[str]],
        split: str,
    ) -> np.ndarray:
        """Cache wrapper: loads sim_features_{split}.npy or calls extract_features."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| embeddings | [20, 384] | Per question, sentence-transformers |
| sim_matrix | [20, 20] | Cosine similarity pairwise |
| sim_features | [N, 4] | [mean, std, min, max] upper-triangle per question |

---

## A-5: Probe Training [Complexity: 9]

### API Signatures

```python
# model.py
class SEProbe:
    """Baseline: logistic regression on hidden states only."""

    def __init__(self, config: ExperimentConfig) -> None: ...

    def fit(self, hidden_states: np.ndarray, labels: np.ndarray) -> None:
        """Fit LogisticRegression(C=1.0, max_iter=1000, solver='lbfgs').

        Args:
            hidden_states: np.ndarray  # [N, 4096]
            labels:        np.ndarray  # [N,] int {0,1}
        """
        ...

    def predict_proba(self, hidden_states: np.ndarray) -> np.ndarray:
        """Returns positive class probabilities.

        Args:
            hidden_states: np.ndarray  # [N, 4096]
        Returns:
            proba: np.ndarray  # [N,]
        """
        ...


class SEDProbe:
    """Proposed: logistic regression on hidden states + similarity features."""

    def __init__(self, config: ExperimentConfig) -> None: ...

    def fit(
        self,
        hidden_states: np.ndarray,  # [N, 4096]
        sim_features: np.ndarray,   # [N, 4]
        labels: np.ndarray,         # [N,]
    ) -> None:
        """Concatenate [hidden_states || sim_features] -> [N, 4100], then fit."""
        ...

    def predict_proba(
        self,
        hidden_states: np.ndarray,  # [N, 4096]
        sim_features: np.ndarray,   # [N, 4]
    ) -> np.ndarray:
        """Concatenate -> predict. Returns [N,] probabilities."""
        ...


# train.py
def train_sep(
    config: ExperimentConfig,
    hidden_states_train: np.ndarray,  # [N_train, 4096]
    labels_train: np.ndarray,         # [N_train,]
) -> SEProbe: ...

def train_sedp(
    config: ExperimentConfig,
    hidden_states_train: np.ndarray,  # [N_train, 4096]
    sim_features_train: np.ndarray,   # [N_train, 4]
    labels_train: np.ndarray,         # [N_train,]
) -> SEDProbe: ...
```

---

## A-6: Evaluation & Visualization [Complexity: 11]

### API Signatures

```python
# evaluate.py
def compute_metrics(
    probe_proba: np.ndarray,    # [N,] predicted probabilities
    se_continuous: np.ndarray,  # [N,] true SE values
    se_binary: np.ndarray,      # [N,] true binary labels
) -> dict:
    """Returns {'spearman_rho': float, 'p_value': float, 'auroc': float}."""
    ...

def plot_gate_metrics(
    sep_metrics: dict,
    sedp_metrics: dict,
    save_path: str,  # h-e1/figures/gate_metrics.png
) -> None:
    """Bar chart: rho for SEP vs SEDP, horizontal line at 0.3."""
    ...

def plot_scatter(
    sep_proba: np.ndarray,   # [N,]
    sedp_proba: np.ndarray,  # [N,]
    se_true: np.ndarray,     # [N,]
    save_path: str,          # h-e1/figures/scatter.png
) -> None: ...

def plot_roc_curves(
    sep_proba: np.ndarray,   # [N,]
    sedp_proba: np.ndarray,  # [N,]
    se_binary: np.ndarray,   # [N,]
    save_path: str,          # h-e1/figures/roc_curves.png
) -> None: ...

def save_results(
    sep_metrics: dict,
    sedp_metrics: dict,
    output_path: str,  # h-e1/04_validation.md
) -> None:
    """Write markdown table with rho, p_value, auroc for both probes."""
    ...
```

---

## RunExperiment Orchestration

### API Signatures

```python
# run_experiment.py
def run(config: ExperimentConfig) -> dict:
    """End-to-end pipeline. Returns final metrics dict.

    Pipeline order:
    1. load_dataset -> train_qs, test_qs
    2. load_or_generate(train_qs, "train") -> hidden_train [N_train,4096], responses_train
    3. load_or_generate(test_qs,  "test")  -> hidden_test  [N_test,4096],  responses_test
    4. load_or_compute(responses_train, "train") -> se_cont_train [N_train,], se_bin_train [N_train,]
    5. load_or_compute(responses_test,  "test")  -> se_cont_test  [N_test,],  se_bin_test  [N_test,]
    6. load_or_extract(responses_train, "train") -> sim_train [N_train, 4]
    7. load_or_extract(responses_test,  "test")  -> sim_test  [N_test,  4]
    8. train_sep(config, hidden_train, se_bin_train)              -> sep_model
    9. train_sedp(config, hidden_train, sim_train, se_bin_train)  -> sedp_model
    10. sep_proba  = sep_model.predict_proba(hidden_test)              # [N_test,]
    11. sedp_proba = sedp_model.predict_proba(hidden_test, sim_test)   # [N_test,]
    12. sep_metrics  = compute_metrics(sep_proba,  se_cont_test, se_bin_test)
    13. sedp_metrics = compute_metrics(sedp_proba, se_cont_test, se_bin_test)
    14. plot_gate_metrics / plot_scatter / plot_roc_curves -> figures/
    15. save_results -> h-e1/04_validation.md
    Return {'sep': sep_metrics, 'sedp': sedp_metrics, 'gate_pass': sedp_metrics['spearman_rho'] >= 0.3}
    """
    ...

if __name__ == "__main__":
    config = ExperimentConfig()
    results = run(config)
```

---

## Data Flow Summary

| Step | Input Shape | Output Shape | Note |
|------|-------------|--------------|------|
| generate_responses | list[str] N | [N, 4096] + [N][20] | Layer 25 TBG token |
| compute_se_labels | [N][20] str | [N,] float + [N,] int | Median binarization |
| extract_features | [N][20] str | [N, 4] | Cosine sim stats |
| SEProbe.fit | [N, 4096] | - | 4096 features |
| SEDProbe.fit | [N, 4096] + [N, 4] | - | 4100 features concatenated |
| predict_proba | [N, 4096(+4)] | [N,] | Probabilities |
| compute_metrics | [N,] + [N,] | dict | spearman_rho, auroc |
