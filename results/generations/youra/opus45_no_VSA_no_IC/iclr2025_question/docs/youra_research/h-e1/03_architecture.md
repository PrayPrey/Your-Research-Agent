# Architecture: h-e1 (EXISTENCE PoC)

**Hypothesis:** SEP AUROC within 0.05 of multi-sample SE, 3 model families, TruthfulQA
**Tier:** LIGHT (4-8 epic tasks)

Applied: linear-probe-on-frozen-hidden-states pattern (OATML/semantic-entropy-probes methodology, from experiment brief research — Archon KB had no directly relevant DL architecture results for this domain, general search returned unrelated diffusion-model pages).

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field project - no existing code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch, following OATML/semantic-entropy-probes reference methodology described in experiment brief.

---

## File Structure (EXISTENCE minimal)

- `h-e1/code/config.py` — fixed config (models, layers, seed, paths)
- `h-e1/code/data.py` — TruthfulQA loading + split
- `h-e1/code/models.py` — model loading + hidden state extraction
- `h-e1/code/semantic_entropy.py` — multi-sample SE baseline (generation, NLI clustering, entropy)
- `h-e1/code/sep.py` — SemanticEntropyProbe (linear probe)
- `h-e1/code/train.py` — orchestration: run per-model pipeline, train probes
- `h-e1/code/evaluate.py` — AUROC computation + gap comparison
- `h-e1/code/visualize.py` — bar chart generation
- `h-e1/figures/` — output figures
- `h-e1/results/` — metrics JSON output

---

## Modules

### Config (`config.py`)

**Dependencies**: none

```python
SEED = 42
MODELS = {
    "llama3-8b": {"id": "meta-llama/Meta-Llama-3-8B-Instruct", "n_layers": 32, "hidden_dim": 4096},
    "mistral-7b": {"id": "mistralai/Mistral-7B-Instruct-v0.2", "n_layers": 32, "hidden_dim": 4096},
    "qwen2-7b": {"id": "Qwen/Qwen2-7B-Instruct", "n_layers": 28, "hidden_dim": 3584},
}
NLI_MODEL_ID = "microsoft/deberta-v3-large-mnli"
N_SAMPLES = 5
TEMPERATURE = 0.7
TRAIN_SPLIT = 0.8
LAYER_FRACTION = 2 / 3  # candidate layer depth for SEP
RESULTS_DIR = "h-e1/results"
FIGURES_DIR = "h-e1/figures"
```

### Data (`data.py`)

**Dependencies**: config

```python
def load_truthfulqa() -> "datasets.Dataset": ...
def split_train_val(dataset, train_frac: float, seed: int) -> tuple["Dataset", "Dataset"]: ...
```

### ModelWrapper (`models.py`)

**Dependencies**: config

```python
class ModelWrapper:
    def __init__(self, model_id: str): ...
    def load(self) -> None:
        """Load AutoModelForCausalLM (fp16, device_map=auto) + tokenizer."""
    def generate(self, prompt: str, n_samples: int, temperature: float) -> list[str]: ...
    def get_hidden_states(self, input_ids, attention_mask) -> "Tensor":
        """Forward with output_hidden_states=True, return all layer states."""
```

### SemanticEntropyBaseline (`semantic_entropy.py`)

**Dependencies**: models.ModelWrapper, config

```python
class SemanticEntropyBaseline:
    def __init__(self, nli_model_id: str): ...
    def cluster_responses(self, responses: list[str]) -> list[int]:
        """NLI-based semantic equivalence clustering -> cluster id per response."""
    def compute_entropy(self, cluster_ids: list[int]) -> float:
        """H_SE = -sum p(c) log p(c)."""
    def compute_se_scores(self, model: "ModelWrapper", questions: list[str]) -> list[float]:
        """Full pipeline: generate -> cluster -> entropy, per question."""
    def binarize(self, se_scores: list[float]) -> list[int]:
        """Threshold at median."""
```

### SemanticEntropyProbe (`sep.py`)

**Dependencies**: models.ModelWrapper

```python
class SemanticEntropyProbe:
    def __init__(self, layer_idx: int, token_position: str = "last"): ...
    def extract_hidden_state(self, model, input_ids, attention_mask) -> "np.ndarray": ...
    def fit(self, hidden_states: "np.ndarray", se_labels: list[int]) -> None: ...
    def predict_proba(self, hidden_states: "np.ndarray") -> "np.ndarray": ...
```

### Evaluate (`evaluate.py`)

**Dependencies**: sklearn.metrics

```python
def compute_auroc(y_true: list[int], y_pred_proba: "np.ndarray") -> float: ...
def compute_gap(auroc_sep: float, auroc_se: float) -> float: ...
def check_success(gaps: dict[str, float]) -> dict:
    """gap<=0.05 for >=2/3 families AND gap<=0.10 for all -> pass/fail."""
```

### Visualize (`visualize.py`)

**Dependencies**: matplotlib, evaluate results

```python
def plot_auroc_comparison(results: dict[str, dict[str, float]], out_path: str) -> None:
    """Bar chart: SEP vs SE AUROC per model family -> figures/auroc_comparison.png."""
```

### Train / Orchestration (`train.py`)

**Dependencies**: all modules above

```python
def run_pipeline_for_model(model_key: str, train_data, val_data) -> dict:
    """Load model -> compute SE labels (train+val) -> extract hidden states ->
    fit SEP -> eval both methods on val -> return {auroc_sep, auroc_se, gap}."""

def main() -> None:
    """Loop over MODELS, aggregate results, save JSON, call visualize + evaluate.check_success."""
```

---

## External Dependencies

None (green-field). Standard libs only: transformers, datasets, torch, sklearn, numpy, matplotlib.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup + data loading | config.py, data.py, TruthfulQA load/split | 6 | 2+1+1+2 |
| A-2 | Model loading + hidden state extraction | models.py, 3 model families, output_hidden_states | 10 | 3+3+2+2 |
| A-3 | Multi-sample SE baseline | semantic_entropy.py: generation, NLI clustering, entropy calc | 13 | 3+3+4+3 |
| A-4 | SEP probe implementation | sep.py: hidden state extraction + LogisticRegression fit/predict | 8 | 2+2+2+2 |
| A-5 | Pipeline orchestration | train.py: per-model run, label binarization, probe training loop | 11 | 3+4+2+2 |
| A-6 | Evaluation + AUROC comparison | evaluate.py: AUROC, gap, success check | 5 | 1+1+1+2 |
| A-7 | Visualization | visualize.py: bar chart of SEP vs SE AUROC | 4 | 1+1+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3, A-5], Low(4-8): [A-1, A-4, A-6, A-7]
