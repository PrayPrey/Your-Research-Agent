# Architecture: h-e1 — Semantic-Structural UQ Existence Verification

**Hypothesis**: EXISTENCE (PoC)
**Date**: 2026-05-20

Applied: modular-inference-pipeline, bootstrap-CI-evaluation, checkpoint-resume-pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project: no existing codebase to analyze. Serena analysis skipped.
**Analyzed Path**: N/A
**Findings**: New implementation from scratch

---

## File Organization

```
h-e1/
  code/
    config.py          # YAML dataclass config loader
    data_loader.py     # Dataset loading + few-shot prompt formatting
    model_loader.py    # Llama-3-8B/70B + DeBERTa loading
    generate.py        # Sampling, greedy decode, logit/hidden-state extraction
    uq_methods.py      # All 6 UQ methods (TP, SE, KLE, SelfCheckGPT-BS, SelfCheckGPT-NLI, SEPs)
    evaluate.py        # AUROC, bootstrap CI, gate check, persistence
    visualize.py       # 4 required figures
    run_experiment.py  # Main orchestration script
  config/
    h-e1.yaml          # Single experiment config
  figures/             # Output figures
  results/             # JSON + pickle outputs
```

---

## Module Structure

### Config (`h-e1/code/config.py`)

**Dependencies**: PyYAML, dataclasses

```python
@dataclass
class SamplingConfig:
    n_samples: int
    temperature: float
    top_p: float
    seed: int
    max_new_tokens: int
    n_few_shot: int

@dataclass
class ModelConfig:
    hf_id: str
    dtype: str
    quantization: Optional[str]
    device_map: str

@dataclass
class ExperimentConfig:
    hypothesis_id: str
    sampling: SamplingConfig
    models: Dict[str, ModelConfig]
    datasets: Dict[str, Any]
    evaluation: Dict[str, Any]
    output: Dict[str, str]

def load_config(path: str) -> ExperimentConfig: ...
```

---

### DataLoader (`h-e1/code/data_loader.py`)

**Dependencies**: datasets, config.py

```python
def load_trivia_qa() -> Dataset: ...
def load_natural_questions() -> Dataset: ...
def load_truthful_qa() -> Dataset: ...

def format_few_shot_prompt(question: str, examples: List[Dict], n_shot: int = 5) -> str: ...
def normalize_answer(answer: str) -> str: ...
def compute_exact_match(prediction: str, gold_answers: List[str]) -> int: ...

def get_dataset(name: str) -> Tuple[Dataset, List[int]]:
    """Returns (dataset, correctness_labels) after EM evaluation."""
    ...
```

---

### ModelLoader (`h-e1/code/model_loader.py`)

**Dependencies**: transformers, bitsandbytes, config.py

```python
def load_llama_8b(cfg: ModelConfig) -> Tuple[AutoModelForCausalLM, AutoTokenizer]: ...
def load_llama_70b(cfg: ModelConfig) -> Tuple[AutoModelForCausalLM, AutoTokenizer]: ...
def load_deberta_nli() -> Tuple[AutoModelForSequenceClassification, AutoTokenizer]: ...

def get_model(model_key: str, cfg: ModelConfig) -> Tuple[Any, Any]:
    """Dispatcher: returns (model, tokenizer) for given model_key."""
    ...
```

---

### Generator (`h-e1/code/generate.py`)

**Dependencies**: torch, transformers, model_loader.py, config.py

```python
@dataclass
class GenerationResult:
    question_id: str
    prompt: str
    greedy_text: str
    greedy_log_likelihood: float
    sampled_texts: List[str]           # N=10 samples
    sampled_log_likelihoods: List[float]
    hidden_states_last: Optional[np.ndarray]  # for SEPs

def generate_for_query(
    model: Any,
    tokenizer: Any,
    prompt: str,
    cfg: SamplingConfig,
    extract_hidden: bool = False,
) -> GenerationResult: ...

def generate_dataset(
    model: Any,
    tokenizer: Any,
    dataset: Dataset,
    cfg: SamplingConfig,
    batch_size: int,
    checkpoint_path: str,
    checkpoint_every: int = 500,
) -> List[GenerationResult]:
    """Batched generation with checkpointing every 500 queries."""
    ...

def load_checkpoint(checkpoint_path: str) -> Optional[List[GenerationResult]]: ...
def save_checkpoint(results: List[GenerationResult], checkpoint_path: str) -> None: ...
```

---

### UQMethods (`h-e1/code/uq_methods.py`)

**Dependencies**: torch, numpy, scipy, transformers, sklearn, generate.py

```python
def compute_token_probability(result: GenerationResult) -> float:
    """Negative log-likelihood of greedy decode."""
    ...

def compute_semantic_entropy(
    result: GenerationResult,
    nli_model: Any,
    nli_tokenizer: Any,
) -> Tuple[float, int]:
    """Returns (SE score, cluster count K)."""
    ...

def compute_kle(
    result: GenerationResult,
    nli_model: Any,
    nli_tokenizer: Any,
) -> Optional[float]:
    """EigValLaplacian via lm-polygraph; returns None if unavailable."""
    ...

def compute_selfcheck_bertscore(result: GenerationResult) -> float: ...
def compute_selfcheck_nli(result: GenerationResult, nli_model: Any, nli_tokenizer: Any) -> float: ...
def compute_seps(result: GenerationResult, probe_model: Optional[Any] = None) -> Optional[float]: ...

def compute_all_uq(
    results: List[GenerationResult],
    nli_model: Any,
    nli_tokenizer: Any,
) -> Dict[str, np.ndarray]:
    """Returns dict: method_name -> uncertainty scores array."""
    ...

def verify_se_mechanism(
    uq_scores: Dict[str, np.ndarray],
    cluster_counts: List[int],
    n_samples: int,
) -> Tuple[bool, Dict[str, Any]]: ...
```

---

### Evaluator (`h-e1/code/evaluate.py`)

**Dependencies**: sklearn, numpy, json, pickle, config.py

```python
def compute_auroc(uncertainty_scores: np.ndarray, correctness_labels: np.ndarray) -> float: ...

def bootstrap_auroc_ci(
    uncertainty_scores: np.ndarray,
    correctness_labels: np.ndarray,
    n_resamples: int = 1000,
    alpha: float = 0.05,
    seed: int = 42,
) -> Tuple[float, float, float]:
    """Returns (mean_auroc, ci_low, ci_high)."""
    ...

def run_gate_check(auroc_results: Dict[str, Any]) -> Tuple[bool, Dict[str, bool]]:
    """Checks all 4 MUST_WORK gate conditions (SE > TP, CI excludes zero)."""
    ...

def save_results(
    auroc_results: Dict[str, Any],
    output_dir: str,
) -> None:
    """Saves auroc_results.json, uncertainty_scores_*.pkl, correctness_labels_*.pkl."""
    ...

def evaluate_all(
    uq_scores: Dict[str, np.ndarray],
    correctness_labels: np.ndarray,
    cfg: ExperimentConfig,
    dataset_name: str,
    model_key: str,
) -> Dict[str, Any]: ...
```

---

### Visualizer (`h-e1/code/visualize.py`)

**Dependencies**: matplotlib, seaborn, numpy, evaluate.py

```python
def plot_auroc_bar(auroc_results: Dict[str, Any], out_path: str) -> None:
    """FR8.1: Bar chart AUROC per method x scale x dataset with CI error bars."""
    ...

def plot_auroc_difference(auroc_results: Dict[str, Any], out_path: str) -> None:
    """FR8.2: AUROC_SE - AUROC_TP per scale per dataset with CI."""
    ...

def plot_roc_curves(
    uq_scores: Dict[str, np.ndarray],
    correctness_labels: np.ndarray,
    out_path: str,
) -> None:
    """FR8.3: ROC curves SE vs TP at 8B and 70B on TriviaQA."""
    ...

def plot_bootstrap_distribution(bootstrap_data: Dict[str, Any], out_path: str) -> None:
    """FR8.4: Bootstrap AUROC histograms SE vs TP per scale."""
    ...

def generate_all_figures(auroc_results: Dict, uq_scores: Dict, correctness: Dict, figures_dir: str) -> None: ...
```

---

### RunExperiment (`h-e1/code/run_experiment.py`)

**Dependencies**: all modules

```python
def run_model_dataset(
    model_key: str,
    dataset_name: str,
    cfg: ExperimentConfig,
) -> Dict[str, Any]:
    """Full pipeline: load model -> generate -> compute UQ -> evaluate."""
    ...

def main(config_path: str) -> None:
    """Orchestrates all model x dataset combinations, gate check, visualization."""
    ...

if __name__ == "__main__":
    main("h-e1/config/h-e1.yaml")
```

---

## Epic Tasks

### Epic E1: Project Setup and Data Loading
**Complexity:** 6/20 (Module_Size:2 + Dependencies:1 + Algorithm:1 + Integration:2)
**Description:** Create config system, load all 3 datasets via HuggingFace, implement few-shot prompt formatting and exact-match normalization.
**Files:** `config.py`, `data_loader.py`, `h-e1/config/h-e1.yaml`
**Inputs:** HuggingFace dataset IDs, few-shot prompt templates
**Outputs:** `ExperimentConfig`, formatted datasets with correctness labels

---

### Epic E2: Model Loading (8B + 70B + DeBERTa)
**Complexity:** 9/20 (Module_Size:2 + Dependencies:3 + Algorithm:1 + Integration:3)
**Description:** Load Llama-3-8B in bfloat16, Llama-3-70B with bitsandbytes 8-bit quantization (device_map=auto), and DeBERTa-large-mnli for NLI. Verify logit access for all variants.
**Files:** `model_loader.py`
**Inputs:** HuggingFace model IDs, BitsAndBytesConfig
**Outputs:** (model, tokenizer) pairs ready for inference

---

### Epic E3: Answer Generation with Checkpointing
**Complexity:** 12/20 (Module_Size:3 + Dependencies:3 + Algorithm:2 + Integration:4)
**Description:** Generate N=10 samples + 1 greedy decode per query with log-likelihood and hidden state extraction. Batched processing (16 queries for 8B, 4 for 70B) with checkpoint save/resume every 500 queries to prevent data loss on long runs (TriviaQA = 17,944 queries).
**Files:** `generate.py`
**Inputs:** model, tokenizer, dataset, SamplingConfig
**Outputs:** `List[GenerationResult]` pickled as checkpoint files

---

### Epic E4: UQ Method Implementations
**Complexity:** 16/20 (Module_Size:4 + Dependencies:4 + Algorithm:5 + Integration:3)
**Description:** Implement all 6 UQ methods: token-probability (greedy NLL), Semantic Entropy (NLI clustering + entropy), KLE (lm-polygraph EigValLaplacian with fallback), SelfCheckGPT-BERTScore, SelfCheckGPT-NLI, SEPs (linear probe on hidden states). Include SE mechanism verification (cluster count K < N).
**Files:** `uq_methods.py`
**Inputs:** `List[GenerationResult]`, DeBERTa NLI model
**Outputs:** `Dict[method_name -> np.ndarray]` uncertainty scores per query

---

### Epic E5: AUROC Evaluation, Bootstrap CI, Gate Check
**Complexity:** 11/20 (Module_Size:3 + Dependencies:2 + Algorithm:3 + Integration:3)
**Description:** Compute AUROC per method per model per dataset. Run 1000-resample bootstrap CI. Execute all 4 MUST_WORK gate checks (SE > TP at 8B/70B on TriviaQA/NQ, CI excludes zero). Persist results as JSON and pickle.
**Files:** `evaluate.py`
**Inputs:** uncertainty score arrays, correctness labels
**Outputs:** `auroc_results.json`, `uncertainty_scores_*.pkl`, `correctness_labels_*.pkl`, gate PASS/FAIL

---

### Epic E6: Visualization (4 Required Figures)
**Complexity:** 8/20 (Module_Size:2 + Dependencies:2 + Algorithm:1 + Integration:3)
**Description:** Generate all 4 required figures: AUROC bar chart, AUROC difference plot, ROC curves, bootstrap distribution histograms. Save to `h-e1/figures/`.
**Files:** `visualize.py`
**Inputs:** `auroc_results`, bootstrap samples, uq_scores arrays
**Outputs:** `auroc_comparison_bar.png`, `auroc_difference.png`, `roc_curves.png`, `bootstrap_distribution.png`

---

### Epic E7: Main Orchestration and End-to-End Integration
**Complexity:** 10/20 (Module_Size:2 + Dependencies:4 + Algorithm:1 + Integration:3)
**Description:** Wire all modules into single `run_experiment.py`: loop over model_key x dataset_name combinations, resume from checkpoints, collect results, run gate check, trigger visualization, write `run_config.json` with all hyperparameters and versions.
**Files:** `run_experiment.py`
**Inputs:** `h-e1/config/h-e1.yaml`
**Outputs:** Complete results directory, gate verdict, all figures

---

**Distribution**: VeryHigh(18-20): [], High(14-17): [E4], Medium(9-13): [E3, E5, E7], Low(4-8): [E1, E2, E6]

---

## External Dependencies (Base Hypothesis)

None — green-field project. No base hypothesis code to import.

---

## Data Flow

```
h-e1.yaml
  -> load_config()
  -> [DataLoader] datasets + correctness_labels
  -> [ModelLoader] (model, tokenizer) per model_key
  -> [Generator] List[GenerationResult] (checkpointed every 500)
  -> [UQMethods] Dict[method -> scores]
  -> [Evaluator] auroc_results.json + gate PASS/FAIL
  -> [Visualizer] 4 PNG figures
```

---

*Generated by Architecture Agent — Phase 3 step-03*
*Hypothesis: h-e1 | Type: EXISTENCE (PoC) | Tier: LIGHT*
