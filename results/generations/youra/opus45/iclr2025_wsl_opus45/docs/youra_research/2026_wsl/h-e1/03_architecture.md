# Architecture Document: H-E1

**Hypothesis**: LoRA Adapter Geometric Signatures Existence Proof
**Type**: EXISTENCE (PoC)
**Date**: 2026-04-13

Applied: PoC-minimal-architecture pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. All modules designed fresh.

---

## File Structure

- `code/config.py` - single fixed configuration
- `code/data.py` - dataset loading and preprocessing
- `code/train.py` - LoRA adapter training pipeline
- `code/analyze.py` - Grassmann distance computation + statistical analysis
- `code/visualize.py` - figure generation
- `code/run_experiment.py` - top-level orchestration entry point

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies**: none

```python
DATASETS = {
    "gsm8k":        ("gsm8k", "main"),
    "arc":          ("allenai/ai2_arc", "ARC-Challenge"),
    "logiqa":       ("lucasmccabe/logiqa", None),
    "strategyqa":   ("wics/strategy-qa", None),
    "mnli":         ("nyu-mll/multi_nli", None),
    "qqp":          ("SetFit/qqp", None),
    "sst2":         ("SetFit/sst2", None),
    "mrpc":         ("SetFit/mrpc", None),
}
TASK_CATEGORIES = {
    "gsm8k": "reasoning", "arc": "reasoning",
    "logiqa": "reasoning", "strategyqa": "reasoning",
    "mnli": "nlu", "qqp": "nlu", "sst2": "nlu", "mrpc": "nlu",
}
BASE_MODEL_ID = "meta-llama/Llama-3.2-1B-Instruct"
LORA_CONFIG = dict(r=32, lora_alpha=64, lora_dropout=0.05, bias="none",
    target_modules=["q_proj","k_proj","v_proj","o_proj","up_proj","down_proj","gate_proj"])
TRAIN_CONFIG = dict(lr=2e-4, epochs=3, batch_size=8, warmup_ratio=0.1,
    weight_decay=0.01)
PRIMARY_SEED = 42
CONTROL_SEEDS = [42, 43, 44, 45, 46]
ADAPTERS_PER_TASK = 20
HYPOTHESIS_FOLDER = "docs/youra_research/20260413_wsl/h-e1"
```

---

### DataModule (`code/data.py`)

**Dependencies**: config

```python
def load_and_format_dataset(task_name: str, max_samples: int = 2000) -> Dataset: ...
def format_example(task_name: str, example: dict) -> str: ...
def tokenize_dataset(dataset: Dataset, tokenizer, max_length: int = 512) -> Dataset: ...
```

---

### TrainingPipeline (`code/train.py`)

**Dependencies**: config, data

```python
def verify_base_model_sha256(model_id: str) -> str: ...
def load_base_model(model_id: str) -> tuple[AutoModelForCausalLM, AutoTokenizer]: ...
def build_lora_model(base_model, lora_cfg: dict) -> PeftModel: ...
def set_deterministic(seed: int) -> None: ...
def train_single_adapter(task_name: str, seed: int, output_dir: str) -> dict: ...
def run_training_pipeline(hypothesis_folder: str) -> list[dict]: ...
```

---

### GrassmannAnalyzer (`code/analyze.py`)

**Dependencies**: config

```python
def extract_b_matrices(adapter_path: str) -> dict[str, np.ndarray]: ...
    # Returns {layer_name: B_matrix} for all target_modules

def compute_orthonormal_basis(B: np.ndarray) -> np.ndarray: ...
    # QR decomposition -> Q (d_out x r)

def grassmann_distance(B1: np.ndarray, B2: np.ndarray) -> float: ...
    # subspace_angles -> sqrt(sum(theta^2))

def compute_pairwise_matrix(adapter_paths: list[str]) -> np.ndarray: ...
    # Aggregated across layers, returns (n_adapters x n_adapters)

def split_within_between(distance_matrix: np.ndarray,
                         adapter_meta: list[dict]) -> tuple[np.ndarray, np.ndarray]: ...
    # Returns (within_distances, between_distances) based on TASK_CATEGORIES

def compute_cohens_d(group1: np.ndarray, group2: np.ndarray) -> float: ...

def run_statistical_tests(within: np.ndarray, between: np.ndarray) -> dict: ...
    # Mann-Whitney U, Cohen's d, 95% CI, effect direction
    # Returns {"p_value", "cohens_d", "ci_95", "within_mean", "between_mean", "passed"}

def run_analysis(hypothesis_folder: str) -> dict: ...
```

---

### Visualizer (`code/visualize.py`)

**Dependencies**: config, analyze

```python
def plot_cluster_bar(stats: dict, out_dir: str) -> None: ...
    # Bar chart: within vs between means with error bars

def plot_distance_distributions(within: np.ndarray,
                                between: np.ndarray, out_dir: str) -> None: ...
    # KDE/histogram overlay

def plot_distance_heatmap(distance_matrix: np.ndarray,
                          adapter_meta: list[dict], out_dir: str) -> None: ...
    # Annotated heatmap with category color blocks

def plot_per_category_boxplot(distance_matrix: np.ndarray,
                              adapter_meta: list[dict], out_dir: str) -> None: ...

def generate_all_figures(hypothesis_folder: str, stats: dict,
                         distance_matrix: np.ndarray,
                         adapter_meta: list[dict]) -> None: ...
```

---

### Orchestrator (`code/run_experiment.py`)

**Dependencies**: config, data, train, analyze, visualize

```python
def main() -> None: ...
    # 1. run_training_pipeline(hypothesis_folder)
    # 2. run_analysis(hypothesis_folder)
    # 3. generate_all_figures(...)
    # 4. print gate pass/fail summary

if __name__ == "__main__":
    main()
```

---

## Data Flow

- `run_experiment.py` calls `train.py` -> writes adapters to `{hypothesis_folder}/adapters/{task}_{seed}/`
- `analyze.py` reads adapter dirs -> writes `{hypothesis_folder}/results/pairwise_distances.npy`, `statistical_results.json`
- `visualize.py` reads results -> writes `{hypothesis_folder}/figures/*.png`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment & Config | Setup project structure, install deps, write config.py, verify GPU/HF token | 6 | 2+1+1+2 |
| A-2 | Dataset Preparation | Implement data.py: load 8 HF datasets, format prompts per task type, tokenize | 10 | 2+2+3+3 |
| A-3 | LoRA Training Pipeline | Implement train.py: model load+SHA256, PEFT LoraConfig, deterministic training loop, save 200 adapters | 17 | 4+4+4+5 |
| A-4 | Grassmann Distance Computation | Implement analyze.py: extract B matrices, QR basis, pairwise distance matrix (200x200) | 14 | 3+3+4+4 |
| A-5 | Statistical Analysis | within/between split, Mann-Whitney U, Cohen's d, 95% CI, JSON results | 11 | 3+2+3+3 |
| A-6 | Visualization & Gate Check | Implement visualize.py: 4 figures, gate pass/fail print in run_experiment.py | 9 | 2+2+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3, A-4], Medium(9-13): [A-2, A-5, A-6], Low(4-8): [A-1]

---

*Generated by Phase 3 Architecture Workflow | Anonymous Research Pipeline*
