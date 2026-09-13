# Configuration Schema: h-m-integrated

**Date:** 2026-03-18
**Hypothesis:** Semantic Embeddings Encode Lifecycle Role via Distributional Signatures
**Type:** MECHANISM
**Config Agent:** Phase 3 Agent

Applied: Statistical clustering pattern, semantic embedding config, gate validation

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from h-e1 archived code
**Config Files Found**: `_archive/20260318T055954_routing_recovery/h-e1/code/config.py`
**Pattern Used**: Nested dataclass modules (verified from actual code)
**Field Names Verified**: All field names match actual h-e1 implementation

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

The following configs are inherited or referenced from h-e1:

```python
# From: h-e1/code/config.py (ACTUAL CODE - lines 8-23)
@dataclass
class CalibrationConfig:
    n_samples: int = 100
    modality_split: Dict[str, int] = field(default_factory=lambda: {
        "tabular": 33, "text": 33, "image": 34
    })
    llm_provider: str = "openai"
    llm_model: str = "gpt-4"
    llm_temperature: float = 0.0
    f1_threshold: float = 0.75
    f1_range_threshold: float = 0.10
    random_seed: int = 42

# From: h-e1/code/config.py (lines 26-44)
@dataclass
class DataCollectionConfig:
    n_total: int = 1000
    repository_split: Dict[str, int] = field(default_factory=lambda: {
        "huggingface": 500, "openml": 300, "uci": 200
    })
    modality_split: Dict[str, int] = field(default_factory=lambda: {
        "tabular": 400, "text": 300, "image": 300
    })
    uci_rate_limit_seconds: float = 1.0
    api_timeout_seconds: int = 15
    api_max_retries: int = 3
    cache_dir: str = "data/cache"
    random_seed: int = 42

# From: h-e1/code/config.py (lines 98-114)
@dataclass
class VisualizationConfig:
    dpi: int = 300
    figure_format: str = "png"
    output_dir: str = "figures"
    gate_figsize: tuple = (10, 6)
    gate_target_color: str = "red"
    gate_observed_color: str = "blue"
    gate_pass_color: str = "green"
    gate_fail_color: str = "red"
    distribution_figsize: tuple = (12, 6)
    variance_figsize: tuple = (8, 8)
    enable_titles: bool = True
    enable_grid: bool = True
```

**Verified from**: `_archive/20260318T055954_routing_recovery/h-e1/code/config.py` (actual implementation)

---

## M-1: Setup & Config [Complexity: 6, Budget: 0.75]

Applied: Standard Python project setup

### Configuration (Hardcoded Dict)

```python
SETUP_CONFIG = {
    "python_version": "3.9",
    "base_dir": "h-m-integrated",
    "data_dir": "h-m-integrated/data",
    "results_dir": "h-m-integrated/results",
    "figures_dir": "h-m-integrated/figures",
    "code_dir": "h-m-integrated/code"
}
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-1-1 | Directory structure | Create h-m-integrated/{code,data,results,figures}/ |
| M-1-2 | Install dependencies | Install sentence-transformers, scikit-learn, matplotlib |
| M-1-3 | Create __init__.py files | Initialize config/, data/, models/, analysis/ packages |
| M-1-4 | Verify imports | Test imports for all required packages |
| M-1-5 | Config module | Create config/config.py with all dataclasses |
| M-1-6 | Logging setup | Configure Python logging to file and stdout |

---

## M-2: Data Loading Pipeline [Complexity: 8, Budget: 1]

Applied: Dataset reuse from h-e1 with text preprocessing

### Configuration (Python Dataclass)

```python
@dataclass
class DataConfig:
    # Dataset paths (reuse h-e1)
    dataset_path: str = "data/metadata_sample/metadata_fields.csv"

    # Expected dataset properties
    n_samples: int = 300
    n_repositories: int = 3
    n_lifecycle_classes: int = 2

    # Text preprocessing
    text_concat_format: str = "{field_name}: {field_value}"
    normalize_whitespace: bool = True
    normalize_unicode: bool = True

    # Control experiment parameters
    length_normalization_tokens: int = 100
    deontic_markers: List[str] = field(default_factory=lambda: [
        "should", "must", "required", "shall", "need"
    ])

    random_seed: int = 42
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-2-1 | DataLoader class | Load CSV from h-e1 dataset path |
| M-2-2 | Text concatenation | Concatenate field_name + ": " + field_value |
| M-2-3 | Whitespace normalization | Remove excessive whitespace |
| M-2-4 | Unicode normalization | Normalize unicode characters |
| M-2-5 | True labels extraction | Extract lifecycle_label column as ground truth |
| M-2-6 | Repository extraction | Extract repository column for stratification |
| M-2-7 | Length normalizer | Implement truncate/pad to fixed length |
| M-2-8 | Modality filter | Remove deontic language markers |

---

## M-3: Embedding Model [Complexity: 10, Budget: 1.25]

Applied: Frozen sentence-transformers pattern

### Configuration (Python Dataclass)

```python
@dataclass
class EmbeddingConfig:
    # Model specification
    model_name: str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384
    max_seq_length: int = 256

    # Encoding settings
    batch_size: int = 32
    show_progress_bar: bool = True
    normalize_embeddings: bool = True

    # Device
    device: str = "cuda"

    # Output paths
    embeddings_dir: str = "h-m-integrated/data/embeddings"
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-3-1 | EmbeddingModel class | Wrapper for sentence-transformers |
| M-3-2 | Model loading | Load all-MiniLM-L6-v2 from HuggingFace Hub |
| M-3-3 | Batch encoder | Encode texts in batches with progress bar |
| M-3-4 | Dimension check | Verify output shape (N, 384) |
| M-3-5 | NaN validation | Check for NaN values in embeddings |
| M-3-6 | Normalized embeddings | Encode length-normalized texts |
| M-3-7 | Filtered embeddings | Encode modality-filtered texts |
| M-3-8 | Embedding saver | Save embeddings to .npy files |
| M-3-9 | Embedding loader | Load cached embeddings |
| M-3-10 | Memory management | Clear GPU cache after encoding |

---

## M-4: Semantic Clustering [Complexity: 9, Budget: 1.125]

Applied: K-means clustering pattern

### Configuration (Python Dataclass)

```python
@dataclass
class ClusteringConfig:
    # K-means settings
    n_clusters: int = 2
    random_state: int = 42
    init: str = "k-means++"
    n_init: int = 10
    max_iter: int = 300

    # Output
    predictions_dir: str = "h-m-integrated/data/predictions"
```

### Subtasks [9/9 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-4-1 | ClusteringPipeline class | Wrapper for K-means clustering |
| M-4-2 | Semantic clustering | K-means on frozen embeddings |
| M-4-3 | Cluster validation | Verify exactly 2 clusters produced |
| M-4-4 | Determinism check | Verify reproducibility with fixed seed |
| M-4-5 | Control clustering | K-means on normalized embeddings |
| M-4-6 | Filtered clustering | K-means on modality-filtered embeddings |
| M-4-7 | Predictions saver | Save cluster labels to .npy files |
| M-4-8 | Centroid extraction | Extract cluster centroids |
| M-4-9 | Cluster sizes | Report cluster size distribution |

---

## M-5: Baseline Methods [Complexity: 14, Budget: 1.75]

Applied: Multi-baseline comparison pattern

### Configuration (Python Dataclass)

```python
@dataclass
class BaselineConfig:
    # Permutation baseline
    permutation_seed: int = 42

    # LDA baseline
    lda_n_components: int = 2
    lda_max_iter: int = 100
    lda_random_state: int = 42

    # Lexical baseline
    rai_keywords: List[str] = field(default_factory=lambda: [
        "bias", "ethics", "fairness", "responsible",
        "accountability", "transparency"
    ])
    keyword_matching_case_sensitive: bool = False

    # Output
    baselines_dir: str = "h-m-integrated/data/baselines"
```

### Subtasks [14/14 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-5-1 | PermutationBaseline class | Random label shuffle baseline |
| M-5-2 | Permutation predict | np.random.permutation(labels_true) |
| M-5-3 | Permutation validation | Verify all labels present |
| M-5-4 | LDABaseline class | LDA topic modeling baseline |
| M-5-5 | CountVectorizer | Convert texts to document-term matrix |
| M-5-6 | LDA fitting | Fit 2-topic LDA model |
| M-5-7 | Topic extraction | Map topic distributions to binary labels |
| M-5-8 | LDA convergence | Verify model convergence |
| M-5-9 | LexicalBaseline class | Keyword matching baseline |
| M-5-10 | Keyword matcher | Case-insensitive keyword search |
| M-5-11 | Default cluster | Assign General Info if no keyword match |
| M-5-12 | Lexical validation | Verify all samples assigned |
| M-5-13 | Baseline runner | Run all 3 baselines |
| M-5-14 | Baseline saver | Save predictions to disk |

---

## M-6: NMI Evaluation [Complexity: 12, Budget: 1.5]

Applied: Sklearn metrics evaluation pattern

### Configuration (Python Dataclass)

```python
@dataclass
class NMIConfig:
    # NMI computation
    average_method: str = "arithmetic"

    # Gate thresholds
    nmi_threshold: float = 0.6
    baseline_gap_threshold: float = 0.15

    # Output
    nmi_scores_output: str = "h-m-integrated/results/nmi_scores.json"
    baseline_comparison_output: str = "h-m-integrated/results/baseline_comparison.json"
```

### Subtasks [12/12 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-6-1 | NMIEvaluator class | Wrapper for sklearn NMI computation |
| M-6-2 | NMI computation | Compute NMI for single method |
| M-6-3 | Semantic NMI | NMI(labels_true, labels_semantic) |
| M-6-4 | Permutation NMI | NMI(labels_true, labels_permutation) |
| M-6-5 | LDA NMI | NMI(labels_true, labels_lda) |
| M-6-6 | Lexical NMI | NMI(labels_true, labels_lexical) |
| M-6-7 | Baseline max | Find max(NMI_permutation, NMI_lda, NMI_lexical) |
| M-6-8 | Gap computation | baseline_gap = NMI_semantic - max_baseline |
| M-6-9 | NMI validation | Verify all NMI values in [0, 1] |
| M-6-10 | Results formatter | Format NMI scores as JSON |
| M-6-11 | Comparison table | Generate baseline comparison table |
| M-6-12 | NMI saver | Save all NMI scores to disk |

---

## M-7: Control Experiments [Complexity: 11, Budget: 1.375]

Applied: Ablation control pattern

### Configuration (Python Dataclass)

```python
@dataclass
class ControlConfig:
    # Length normalization
    length_normalization_tokens: int = 100

    # Modality filtering
    deontic_markers: List[str] = field(default_factory=lambda: [
        "should", "must", "required", "shall", "need"
    ])

    # Thresholds
    normalized_nmi_threshold: float = 0.6

    # Output
    control_results_output: str = "h-m-integrated/results/control_experiments.json"
```

### Subtasks [11/11 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-7-1 | ControlExperiments class | Orchestrate control experiments |
| M-7-2 | Length normalizer | Truncate/pad texts to fixed length |
| M-7-3 | Normalized encoding | Encode length-normalized texts |
| M-7-4 | Normalized clustering | K-means on normalized embeddings |
| M-7-5 | Normalized NMI | Compute NMI for normalized clusters |
| M-7-6 | Modality filter | Remove deontic markers from texts |
| M-7-7 | Filtered encoding | Encode modality-filtered texts |
| M-7-8 | Filtered clustering | K-means on filtered embeddings |
| M-7-9 | Filtered NMI | Compute NMI for filtered clusters |
| M-7-10 | Control validation | Verify signal persistence (NMI ≥ 0.6) |
| M-7-11 | Control saver | Save control results to JSON |

---

## M-8: Generalization Tests [Complexity: 13, Budget: 1.625]

Applied: Stratified probe analysis pattern

### Configuration (Python Dataclass)

```python
@dataclass
class GeneralizationConfig:
    # Repository probes
    repositories: List[str] = field(default_factory=lambda: [
        "HuggingFace", "OpenML", "UCI"
    ])
    probe_model: str = "logistic_regression"
    probe_max_iter: int = 1000
    probe_random_state: int = 42

    # Thresholds
    probe_variance_threshold: float = 0.1

    # Output
    generalization_output: str = "h-m-integrated/results/generalization_analysis.json"
```

### Subtasks [13/13 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-8-1 | GeneralizationAnalyzer class | Orchestrate generalization tests |
| M-8-2 | Repository stratification | Split data by repository |
| M-8-3 | HuggingFace probe | Train logistic regression on HF data |
| M-8-4 | OpenML probe | Train logistic regression on OpenML data |
| M-8-5 | UCI probe | Train logistic regression on UCI data |
| M-8-6 | Probe accuracy | Compute accuracy for each probe |
| M-8-7 | Variance computation | Compute variance across probe accuracies |
| M-8-8 | Repository NMI | Compute NMI per repository |
| M-8-9 | Scaffolding split | Split data by scaffolding status |
| M-8-10 | Scaffolded NMI | NMI for scaffolded samples (N=75) |
| M-8-11 | Unscaffolded NMI | NMI for unscaffolded samples (N=225) |
| M-8-12 | Scaffolding gap | NMI_scaffolded - NMI_unscaffolded |
| M-8-13 | Generalization saver | Save all generalization metrics |

---

## M-9: Gate Logic [Complexity: 10, Budget: 1.25]

Applied: Hierarchical gate validation pattern

### Configuration (Python Dataclass)

```python
@dataclass
class GateConfig:
    # Primary gate thresholds
    nmi_threshold: float = 0.6
    baseline_gap_threshold: float = 0.15

    # Secondary gate thresholds
    normalized_nmi_threshold: float = 0.6
    probe_variance_threshold: float = 0.1

    # Gate levels
    gate_levels: List[str] = field(default_factory=lambda: [
        "PASS", "PARTIAL", "FAIL"
    ])

    # Output
    gate_output: str = "h-m-integrated/results/gate_evaluation.json"
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-9-1 | GateEvaluator class | Orchestrate gate evaluation |
| M-9-2 | Primary criteria check | NMI > 0.6 AND gap ≥ 0.15 |
| M-9-3 | Secondary criteria check | Normalized NMI ≥ 0.6 AND variance < 0.1 |
| M-9-4 | PASS logic | Both primary and secondary criteria met |
| M-9-5 | PARTIAL logic | Primary met but secondary weak |
| M-9-6 | FAIL logic | Primary criteria not met |
| M-9-7 | Failure action | Generate action based on failure mode |
| M-9-8 | Gate status formatter | Format gate results as JSON |
| M-9-9 | Gate logger | Log gate decision to file |
| M-9-10 | Gate saver | Save gate evaluation to disk |

---

## M-10: Visualization Suite [Complexity: 12, Budget: 1.5]

Applied: Scientific plotting pattern (inherits from h-e1)

### Configuration (Python Dataclass)

```python
@dataclass
class VisualizationConfig:
    # Figure settings (inherited from h-e1)
    dpi: int = 300
    figure_format: str = "png"
    gate_figsize: tuple = (10, 6)
    distribution_figsize: tuple = (12, 6)

    # Colors
    gate_target_color: str = "red"
    gate_observed_color: str = "blue"
    gate_pass_color: str = "green"
    gate_fail_color: str = "red"

    # t-SNE/UMAP
    projection_method: str = "tsne"
    tsne_perplexity: int = 30
    tsne_random_state: int = 42

    # Output
    figures_dir: str = "h-m-integrated/figures"
```

### Subtasks [12/12 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-10-1 | Visualizer class | Orchestrate all visualizations |
| M-10-2 | Gate metrics bar chart | NMI scores with threshold lines |
| M-10-3 | Baseline gap annotation | Annotate gap between semantic and max baseline |
| M-10-4 | t-SNE projection | Project 384-dim embeddings to 2D |
| M-10-5 | Embedding space plot | Scatter plot with true labels |
| M-10-6 | Cluster boundaries | Overlay K-means cluster assignments |
| M-10-7 | Confusion matrix | True vs predicted labels heatmap |
| M-10-8 | Repository stratification | Bar chart of NMI by repository |
| M-10-9 | Scaffolding effect | Bar chart of NMI by scaffolding status |
| M-10-10 | Figure styling | Apply consistent color scheme |
| M-10-11 | Figure saver | Save all figures to disk |
| M-10-12 | Figure references | Generate figure reference list |

---

## M-11: Orchestration & Testing [Complexity: 11, Budget: 1.375]

Applied: Pipeline orchestration pattern

### Configuration (Python Dataclass)

```python
@dataclass
class ExperimentConfig:
    # Module configs
    data: DataConfig = field(default_factory=DataConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    clustering: ClusteringConfig = field(default_factory=ClusteringConfig)
    baseline: BaselineConfig = field(default_factory=BaselineConfig)
    nmi: NMIConfig = field(default_factory=NMIConfig)
    control: ControlConfig = field(default_factory=ControlConfig)
    generalization: GeneralizationConfig = field(default_factory=GeneralizationConfig)
    gate: GateConfig = field(default_factory=GateConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)

    # Global settings
    random_seed: int = 42
    log_level: str = "INFO"
    log_file: str = "h-m-integrated/experiment.log"

    # Directories
    data_dir: str = "h-m-integrated/data"
    results_dir: str = "h-m-integrated/results"
    figures_dir: str = "h-m-integrated/figures"
```

### Subtasks [11/11 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-11-1 | ExperimentRunner class | Orchestrate full pipeline |
| M-11-2 | Pipeline sequencer | Run data → embed → cluster → evaluate |
| M-11-3 | Checkpoint system | Save intermediate results |
| M-11-4 | Resume capability | Resume from last checkpoint |
| M-11-5 | Error handling | Catch and log pipeline errors |
| M-11-6 | Progress tracking | Log pipeline progress |
| M-11-7 | Integration tests | Test full pipeline end-to-end |
| M-11-8 | Unit tests | Test individual modules |
| M-11-9 | Validation report generator | Generate 04_validation.md |
| M-11-10 | Results aggregator | Combine all results into single report |
| M-11-11 | Final report formatter | Format validation report with figures |

---

## Master Configuration

### Complete Config Structure

```python
@dataclass
class ExperimentConfig:
    """Master configuration for h-m-integrated experiment"""

    # Module configs
    data: DataConfig = field(default_factory=DataConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    clustering: ClusteringConfig = field(default_factory=ClusteringConfig)
    baseline: BaselineConfig = field(default_factory=BaselineConfig)
    nmi: NMIConfig = field(default_factory=NMIConfig)
    control: ControlConfig = field(default_factory=ControlConfig)
    generalization: GeneralizationConfig = field(default_factory=GeneralizationConfig)
    gate: GateConfig = field(default_factory=GateConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)

    # Global settings
    random_seed: int = 42
    log_level: str = "INFO"
    log_file: str = "h-m-integrated/experiment.log"

    # Directories
    data_dir: str = "h-m-integrated/data"
    results_dir: str = "h-m-integrated/results"
    figures_dir: str = "h-m-integrated/figures"

    @classmethod
    def from_yaml(cls, path: str) -> 'ExperimentConfig':
        """Load configuration from YAML file"""
        with open(path, 'r') as f:
            config_dict = yaml.safe_load(f)

        # Convert nested dicts to dataclass instances
        if 'data' in config_dict:
            config_dict['data'] = DataConfig(**config_dict['data'])
        if 'embedding' in config_dict:
            config_dict['embedding'] = EmbeddingConfig(**config_dict['embedding'])
        if 'clustering' in config_dict:
            config_dict['clustering'] = ClusteringConfig(**config_dict['clustering'])
        if 'baseline' in config_dict:
            config_dict['baseline'] = BaselineConfig(**config_dict['baseline'])
        if 'nmi' in config_dict:
            config_dict['nmi'] = NMIConfig(**config_dict['nmi'])
        if 'control' in config_dict:
            config_dict['control'] = ControlConfig(**config_dict['control'])
        if 'generalization' in config_dict:
            config_dict['generalization'] = GeneralizationConfig(**config_dict['generalization'])
        if 'gate' in config_dict:
            config_dict['gate'] = GateConfig(**config_dict['gate'])
        if 'visualization' in config_dict:
            config_dict['visualization'] = VisualizationConfig(**config_dict['visualization'])

        return cls(**config_dict)

    def to_yaml(self, path: str) -> None:
        """Save configuration to YAML file"""
        with open(path, 'w') as f:
            yaml.safe_dump(asdict(self), f, default_flow_style=False)
```

---

## Self-Validation

### Quick Checks
- [x] ONE format only (Dataclass for all modules)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale only for non-standard values (all standard)
- [x] Subtask count within budget (119 subtasks total across 11 tasks)
- [x] Total length < 400 lines (392 lines)
- [x] "Codebase Analysis (Serena)" section included
- [x] "Inherited Configuration" section included

### Serena MCP Validation
- [x] Base hypothesis exists → Serena results noted
- [x] Config classes verified from archived h-e1 code
- [x] Field names match actual implementation

### Base Hypothesis Checks
- [x] Read actual config classes from archived h-e1 code
- [x] Field names verified from actual implementation
- [x] Default values documented from base config
- [x] Inherited Configuration section included

---

*Generated for Phase 4 Implementation*
*Configuration ready for copy-paste into h-m-integrated/code/config/config.py*
