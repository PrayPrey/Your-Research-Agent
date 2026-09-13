# Architecture: H-E1 AUROC Discriminative Degradation Analysis

**Applied**: HuggingFace AutoModelForCausalLM logit extraction pattern (outputs.logits[0, -1, :])

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing codebase
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; no base hypothesis folder to analyze.

---

## File Organization

- `h-e1/code/config.py` - experiment constants and model registry
- `h-e1/code/data.py` - MMLU loading and prompt formatting
- `h-e1/code/inference.py` - model loading and logit extraction
- `h-e1/code/metrics.py` - AUROC + bootstrap CI + secondary metrics
- `h-e1/code/visualize.py` - figures (bar chart, KDE, forest plot)
- `h-e1/code/run_experiment.py` - orchestration, checkpoint/resume, results output

---

## Modules

### Config (`h-e1/code/config.py`)

**Dependencies**: none

```python
SEED: int = 42
BOOTSTRAP_N: int = 1000
CHECKPOINT_INTERVAL: int = 1000
DTYPE = torch.float16
DEVICE: str = "cuda"

MODEL_PAIRS: dict[str, tuple[str, str]] = {
    "qwen":    ("Qwen/Qwen2.5-7B", "Qwen/Qwen2.5-7B-Instruct"),
    "llama":   ("meta-llama/Llama-2-7b-hf", "meta-llama/Llama-2-7b-chat-hf"),
    "mistral": ("mistralai/Mistral-7B-v0.1", "mistralai/Mistral-7B-Instruct-v0.2"),
}

RESULTS_DIR: str = "h-e1/results"
FIGURES_DIR: str = "h-e1/figures"
CACHE_DIR: str = "h-e1/cache"

PROMPT_TEMPLATE: str = (
    "Question: {question}\n"
    "A. {a}\nB. {b}\nC. {c}\nD. {d}\nAnswer:"
)
```

---

### DataModule (`h-e1/code/data.py`)

**Dependencies**: config

```python
def load_mmlu_test() -> Dataset: ...
    # loads cais/mmlu "all" test split, validates structure

def format_prompt(sample: dict) -> str: ...
    # applies PROMPT_TEMPLATE to question + choices

def get_dataloader(dataset: Dataset, start_idx: int = 0) -> Iterator[dict]: ...
    # yields samples from start_idx onward (resume support)
```

---

### InferenceModule (`h-e1/code/inference.py`)

**Dependencies**: config

```python
def load_model(model_id: str) -> tuple[AutoModelForCausalLM, AutoTokenizer]: ...
    # loads with torch_dtype=float16, device_map="cuda", sets pad token

def unload_model(model: AutoModelForCausalLM) -> None: ...
    # del model, torch.cuda.empty_cache()

def get_choice_token_ids(tokenizer: AutoTokenizer) -> list[int]: ...
    # encode(" A"," B"," C"," D") -> list of token IDs

def extract_choice_logits(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    prompt: str,
    choice_ids: list[int],
) -> np.ndarray: ...
    # returns shape (4,) float array of last-token logits for A/B/C/D

def compute_margin(logits: np.ndarray) -> float: ...
    # sorted_logits[0] - sorted_logits[1]

def run_model_inference(
    model_id: str,
    dataset: Dataset,
    cache_path: str,
    start_idx: int = 0,
) -> tuple[np.ndarray, np.ndarray]: ...
    # returns (margins, correctness), saves .npy checkpoints every CHECKPOINT_INTERVAL
```

---

### MetricsModule (`h-e1/code/metrics.py`)

**Dependencies**: config

```python
def compute_auroc_with_ci(
    margins: np.ndarray,
    correctness: np.ndarray,
    n_bootstrap: int = BOOTSTRAP_N,
    seed: int = SEED,
) -> dict[str, float]: ...
    # returns {"auroc": float, "ci_lower": float, "ci_upper": float}

def compute_conditional_margins(
    margins: np.ndarray,
    correctness: np.ndarray,
) -> dict[str, float]: ...
    # returns {"mean_correct": float, "mean_incorrect": float}

def compute_i2_statistic(
    deltas: list[float],
    ci_lowers: list[float],
    ci_uppers: list[float],
) -> float: ...
    # I² heterogeneity for meta-analysis across families

def evaluate_gate_criteria(results: dict) -> dict[str, bool]: ...
    # checks AUROC_base > AUROC_instruct and CI_lower(delta) > 0 per family
    # returns {"qwen": bool, "llama": bool, "mistral": bool, "all_pass": bool}
```

---

### VisualizeModule (`h-e1/code/visualize.py`)

**Dependencies**: config, metrics output dict

```python
def plot_auroc_comparison(
    results: dict,
    save_path: str,
) -> None: ...
    # grouped bar chart: 3 families, base vs instruct, with CI error bars

def plot_margin_distributions(
    margins_by_model: dict[str, np.ndarray],
    correctness: np.ndarray,
    save_path: str,
) -> None: ...
    # KDE plots: correct vs incorrect per model (base and instruct overlay)

def plot_forest(
    results: dict,
    save_path: str,
) -> None: ...
    # forest plot: AUROC delta per family + pooled estimate with CI

def save_all_figures(results: dict, margins_by_model: dict, figures_dir: str) -> None: ...
    # calls all three plot functions, saves to figures_dir
```

---

### Orchestrator (`h-e1/code/run_experiment.py`)

**Dependencies**: config, data, inference, metrics, visualize

```python
def load_or_run_inference(
    family: str,
    variant: str,
    model_id: str,
    dataset: Dataset,
) -> tuple[np.ndarray, np.ndarray]: ...
    # checks cache; if hit returns cached arrays; else calls run_model_inference

def run_family(family: str, dataset: Dataset) -> dict: ...
    # loads base + instruct sequentially (unload between),
    # calls load_or_run_inference for each, returns per-family results dict

def save_results(all_results: dict, results_dir: str) -> None: ...
    # writes auroc_results.yaml

def generate_validation_report(all_results: dict, gate: dict, output_path: str) -> None: ...
    # writes 04_validation.md

def main() -> None: ...
    # sets seed, loads dataset, iterates families, aggregates, saves results/figures/report
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1 | Setup & Config | Project scaffold, config.py, directory creation, deps | 5 | 1+1+1+2 |
| E2 | Data Loading | MMLU load, prompt formatting, dataloader with resume | 7 | 2+1+2+2 |
| E3 | Inference Engine | Model load/unload, token mapping, logit extraction, .npy caching | 14 | 3+3+4+4 |
| E4 | Metrics | AUROC, bootstrap CI, conditional margins, I² statistic, gate eval | 12 | 3+2+4+3 |
| E5 | Visualization | Bar chart, KDE, forest plot, save all figures | 9 | 2+2+3+2 |
| E6 | Orchestration | Checkpoint/resume, family loop, results YAML, validation report | 11 | 3+3+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [E3], Medium(9-13): [E4, E6, E5], Low(4-8): [E1, E2]

**Total tasks**: 6 (within EXISTENCE 4-8 range, well within 15-task LIGHT budget)

---

## Data Flow

- `run_experiment.py` calls `data.py` to load MMLU test split
- For each family: calls `inference.py` to run base model then instruct model
- Each model run writes `.npy` cache; on re-run, cache is loaded directly
- `metrics.py` computes AUROC + CI + secondary metrics per model pair
- `visualize.py` consumes aggregated results dict and per-model margin arrays
- `run_experiment.py` writes `results/auroc_results.yaml` and `04_validation.md`

## External Libraries

| Library | Version | Usage |
|---------|---------|-------|
| transformers | >=4.35.0 | AutoModelForCausalLM, AutoTokenizer |
| torch | >=2.0.0 | float16 inference |
| datasets | >=2.14.0 | cais/mmlu loading |
| scikit-learn | >=1.3.0 | roc_auc_score |
| numpy | >=1.24.0 | array ops, bootstrap |
| matplotlib | >=3.7.0 | figures |
| seaborn | >=0.12.0 | KDE plots |
| pyyaml | any | results serialization |
