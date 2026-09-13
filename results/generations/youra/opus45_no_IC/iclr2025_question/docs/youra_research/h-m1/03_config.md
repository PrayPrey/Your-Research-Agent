# Configuration: H-M1 (Semantic Entropy / Error Correlation)

**Format**: Python Dataclasses

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass

Applied: Standard PyTorch/HF inference-pipeline config pattern (dataclass groups, no training loop config since inference-only)

---

## A-1: Data Pipeline [Complexity: 8, Budget: 8]

```python
@dataclass
class DataConfig:
    dataset_name: str = "trivia_qa"
    dataset_subset: str = "rc"
    split: str = "validation"
    sample_size: int = 1000
    seed: int = 42
    f1_correctness_threshold: float = 0.5  # used by CorrectnessLabeler (A-5)
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | load_dataset | HF `trivia_qa` rc validation load |
| C-1-2 | shuffle_sample | shuffle(seed) + select(range(sample_size)) |
| C-1-3 | normalize_answer | lowercase, strip punctuation |
| C-1-4 | filter_single_answer | drop multi/ambiguous-answer rows |

---

## A-2: Response Generation [Complexity: 14, Budget: 14]

```python
@dataclass
class ModelConfig:
    model_name: str = "meta-llama/Llama-2-7b-chat-hf"
    dtype: str = "float16"
    device_map: str = "auto"
    context_length: int = 4096

@dataclass
class GenerationConfig:
    temperature: float = 0.7       # Kuhn 2023
    n_samples: int = 10
    max_new_tokens: int = 50
    do_sample: bool = True
    top_p: float = 1.0
    return_dict_in_generate: bool = True
    output_scores: bool = True     # required for token logprobs
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-2-1 | load_model | Load Llama-2-7B-Chat fp16 + tokenizer |
| C-2-2 | batched_sampling | N=10 sampling per question, batched across questions |
| C-2-3 | logprob_capture | Token-level logprobs, length-normalized mean |
| C-2-4 | output_schema | `{"text","logprob","token_logprobs"}` per response |

---

## A-3: Entailment Clustering [Complexity: 15, Budget: 15]

```python
@dataclass
class NLIConfig:
    model_name: str = "microsoft/deberta-v3-large-mnli"
    entailment_threshold: float = 0.5
    batch_size: int = 32
    prepend_question: bool = True  # per Farquhar 2024
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-3-1 | load_nli_model | Load DeBERTa-v3-large-mnli |
| C-3-2 | pairwise_entailment | Batched bidirectional A⊨B / B⊨A prob computation |
| C-3-3 | greedy_clustering | Assign response to first matching cluster (≤45 pairs/question) |
| C-3-4 | cluster_output | Return `list[list[int]]` cluster index groups |

---

## A-4: Semantic Entropy Computation [Complexity: 9, Budget: 9]

```python
@dataclass
class EntropyConfig:
    entropy_unit: str = "nats"
    length_normalize_logprobs: bool = True  # mean token logprob per generation
```

### Subtasks [3/3 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-4-1 | cluster_prob_agg | Sum exp(logprob) per cluster, normalize |
| C-4-2 | shannon_entropy | scipy.stats.entropy on normalized cluster probs |
| C-4-3 | validate_range | Assert entropy >= 0, finite |

---

## A-5: Correctness Labeling [Complexity: 6, Budget: 6]

Uses `DataConfig.f1_correctness_threshold` (no new config needed).

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-5-1 | token_f1 | Token-level F1 vs gold aliases |
| C-5-2 | is_correct | exact match OR F1 > threshold |

---

## A-6: Statistical Evaluation [Complexity: 8, Budget: 8]

```python
@dataclass
class EvaluationConfig:
    p_value_threshold: float = 0.05
    cohens_d_threshold: float = 0.3
    alternative: str = "greater"  # incorrect > correct
    auroc_secondary_threshold: float = 0.65
```

### Subtasks [3/3 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-6-1 | mann_whitney | One-sided U test, incorrect > correct |
| C-6-2 | cohens_d_auroc | Effect size + AUROC computation |
| C-6-3 | gate_check | `p < threshold AND d > threshold` -> gate_passed bool |

---

## A-7: Visualization Suite [Complexity: 7, Budget: 7]

No new config; reuses `EvaluationConfig` outputs and fixed output paths (`h-m1/figures/`).

### Subtasks [3/3 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-7-1 | gate_bar_chart | REQUIRED: mean entropy bar chart w/ error bars, p, d |
| C-7-2 | violin_plot | Entropy distribution correct vs incorrect |
| C-7-3 | roc_curve | ROC curve for entropy predictor |

---

## A-8: Pipeline Orchestration [Complexity: 10, Budget: 10]

```python
@dataclass
class ExperimentConfig:
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    nli: NLIConfig = field(default_factory=NLIConfig)
    entropy: EntropyConfig = field(default_factory=EntropyConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    output_dir: str = "h-m1/results"
    figures_dir: str = "h-m1/figures"
    seed: int = 42
```

### Subtasks [3/3 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-8-1 | wire_pipeline | load -> generate -> cluster+entropy -> label -> stats -> figures |
| C-8-2 | persist_results | Save results.json (metrics + per-question entropy/label) |
| C-8-3 | logging | Progress logging per 100 questions |

---

## A-9: Ablation Studies [Complexity: 12, Budget: 12]

```python
@dataclass
class AblationConfig:
    temperatures: list[float] = field(default_factory=lambda: [0.5, 0.7, 1.0])   # A1
    sample_counts: list[int] = field(default_factory=lambda: [5, 10, 15])         # A2
    entailment_thresholds: list[float] = field(default_factory=lambda: [0.3, 0.5, 0.7])  # A3
```

### Subtasks [3/3 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-9-1 | temp_ablation | Rerun A-2/A-6 per temperature in list |
| C-9-2 | n_ablation | Rerun A-2/A-6 per sample_count in list |
| C-9-3 | threshold_ablation | Rerun A-3/A-6 per entailment_threshold in list |

---

## Full YAML (defaults, for reference/override)

```yaml
data:
  dataset_name: trivia_qa
  dataset_subset: rc
  split: validation
  sample_size: 1000
  seed: 42
  f1_correctness_threshold: 0.5
model:
  model_name: meta-llama/Llama-2-7b-chat-hf
  dtype: float16
  device_map: auto
  context_length: 4096
generation:
  temperature: 0.7
  n_samples: 10
  max_new_tokens: 50
  do_sample: true
  top_p: 1.0
nli:
  model_name: microsoft/deberta-v3-large-mnli
  entailment_threshold: 0.5
  batch_size: 32
entropy:
  entropy_unit: nats
  length_normalize_logprobs: true
evaluation:
  p_value_threshold: 0.05
  cohens_d_threshold: 0.3
  alternative: greater
  auroc_secondary_threshold: 0.65
ablation:
  temperatures: [0.5, 0.7, 1.0]
  sample_counts: [5, 10, 15]
  entailment_thresholds: [0.3, 0.5, 0.7]
seed: 42
output_dir: h-m1/results
figures_dir: h-m1/figures
```
