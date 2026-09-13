# Configuration: H-M1 (Attention Entropy Task Discrimination)

**Type:** MECHANISM | **Format:** Python Dataclass

**Applied**: No relevant KB config pattern found — standard dataclass config.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (H-M1 reuses only H-E1's `cluster_labels.json` JSON artifact, not its config code — no dataclass to inherit)
**Config Files Found**: None
**Pattern Used**: dataclass

---

## A-1: Config + Data Loading [Complexity: 7, Budget: 7]

**Applied**: Standard PyTorch/HF defaults.

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field

TASK_CATEGORIES: dict[str, str] = {
    # Single-Doc QA
    "narrativeqa": "single_doc_qa",
    "qasper": "single_doc_qa",
    "multifieldqa_en": "single_doc_qa",
    "multifieldqa_zh": "single_doc_qa",
    # Multi-Doc QA
    "hotpotqa": "multi_doc_qa",
    "2wikimqa": "multi_doc_qa",
    "musique": "multi_doc_qa",
    "dureader": "multi_doc_qa",
    # Summarization
    "gov_report": "summarization",
    "qmsum": "summarization",
    "multi_news": "summarization",
    "vcsum": "summarization",
    # Few-shot
    "trec": "few_shot",
    "triviaqa": "few_shot",
    "samsum": "few_shot",
    "lsht": "few_shot",
    # Synthetic
    "passage_count": "synthetic",
    "passage_retrieval_en": "synthetic",
    "passage_retrieval_zh": "synthetic",
    # Code
    "lcc": "code",
    "repobench-p": "code",
}

TASKS: list[str] = list(TASK_CATEGORIES.keys())  # 21 tasks


@dataclass
class DataConfig:
    dataset_name: str = "THUDM/LongBench"
    samples_per_task: int = 10
    n_probe_tokens: int = 100
    seed: int = 42
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | TASK_CATEGORIES + TASKS | Define 21-task -> 6-category mapping |
| C-1-2 | DataConfig | samples_per_task, n_probe_tokens, seed |
| C-1-3 | load_task/sample_task | LongBench loading (reuse h-e1 pattern) |
| C-1-4 | tokenize_probe | Truncate to first n_tokens |

---

## A-2: Model Loading + Mechanism Verification [Complexity: 10, Budget: 10]

**Applied**: Standard HF `from_pretrained` defaults (fp16 + device_map=auto per PRD FR-2).

### Configuration (Python Dataclass)

```python
@dataclass
class ModelConfig:
    model_name: str = "meta-llama/Llama-2-7b-hf"
    torch_dtype: str = "float16"
    device_map: str = "auto"
    output_attentions: bool = True
    n_layers: int = 32
    n_heads: int = 32
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-2-1 | load_model | AutoModelForCausalLM + AutoTokenizer, fp16, device_map=auto |
| C-2-2 | verify_mechanism shape checks | assert 32 layers, 4D tensor, 32 heads |
| C-2-3 | verify_mechanism numeric checks | finite, non-negative entropy |
| C-2-4 | logging | print "Mechanism verification PASSED" |

---

## A-3: Entropy Computation [Complexity: 12, Budget: 12]

**Applied**: Standard entropy over softmax attention (bertology.py / entropy-guided-attention-llm pattern).

### Configuration (Python Dataclass)

```python
@dataclass
class EntropyConfig:
    eps: float = 1e-10  # numerical stability (PRD risk mitigation)
    output_shape: tuple = (32, 32)  # (n_layers, n_heads)
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-3-1 | compute_attention_entropy | Shannon entropy per head, eps=1e-10 |
| C-3-2 | extract_task_entropy | Loop samples -> stack (n_samples, 32, 32) |
| C-3-3 | batched extraction across 21 tasks | Iterate TASKS, accumulate entropy_by_task dict |
| C-3-4 | save entropy_matrix.npy | Save concatenated (n_total, 32, 32) array |

---

## A-4: Statistical Analysis [Complexity: 9, Budget: 9]

**Applied**: `scipy.stats.f_oneway` one-way ANOVA (standard).

### Configuration (Python Dataclass)

```python
@dataclass
class GateConfig:
    significance_threshold: float = 0.05
    effect_size_threshold: float = 0.10  # eta^2, secondary metric (PRD success criteria)
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-4-1 | aggregate_task_means | Mean entropy per task across samples/layers/heads |
| C-4-2 | compute_variance_ratio | Group by category, `f_oneway` -> (F, p) |
| C-4-3 | compute_eta_squared | SS_between / SS_total |
| C-4-4 | evaluate_gate + save stats_results.json | PASS if p < threshold |

---

## A-5: Visualization Suite [Complexity: 8, Budget: 8]

**Applied**: Standard matplotlib defaults.

### Configuration (Python Dataclass)

```python
@dataclass
class ExperimentConfig:
    output_dir: str = "h-m1"
    figure_dir: str = "h-m1/figures"
    save_artifacts: bool = True
    dpi: int = 150
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-5-1 | plot_gate_metrics | F-stat/p-value bar with threshold line (mandatory) |
| C-5-2 | plot_entropy_heatmap | 21 tasks x 32 layers |
| C-5-3 | plot_category_boxplot + plot_layer_discrimination | Entropy distribution per category; per-layer discrimination |
| C-5-4 | plot_cluster_correlation | Read `h-e1/cluster_labels.json`, correlate vs task_means |

---

## A-6: Pipeline Orchestration [Complexity: 6, Budget: 6]

**Applied**: Standard sequential pipeline, no config needed beyond above.

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| C-6-1 | run_pipeline load+verify | load_model, verify_mechanism |
| C-6-2 | run_pipeline extract | per-task sample/tokenize/extract, save entropy_matrix.npy |
| C-6-3 | run_pipeline stats | aggregate/F-test/eta^2, save stats_results.json |
| C-6-4 | main() | evaluate_gate, call visualize.main() |

---

## NFR Mapping

| NFR | Config Field |
|-----|--------------|
| GPU memory < 16GB | `ModelConfig.torch_dtype="float16"`, `device_map="auto"` |
| Runtime < 1hr | `DataConfig.samples_per_task=10` (210 total forward passes) |
| Reproducible | `DataConfig.seed=42` |
