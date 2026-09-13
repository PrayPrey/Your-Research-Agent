# Configuration Schema: h-e1

**Date:** 2026-08-24
**Hypothesis ID:** h-e1 (EXISTENCE)
**Author:** Phase 3 Configuration Agent

---

## Codebase Analysis (Serena)

**Project Type:** green-field (new hypothesis)
**Status:** New config design based on archived h-m1 patterns
**Config Files Found:** Referenced `/docs/youra_research/_archive/20260824T090636_routing_recovery/h-m1/code/config.py`
**Pattern Used:** dataclass (nested structure)

---

## Configuration Overview

Single dataclass-based configuration for data curation filter transfer experiment. All values from 02c_experiment_brief.md training protocol.

---

## A-1: Curation Configuration

**Applied:** C4 pipeline patterns (dedup=0.8, perplexity=100)

```python
from dataclasses import dataclass

@dataclass
class CurationConfig:
    """Data curation filter configuration."""
    
    # Deduplication (MinHash LSH)
    dedup_threshold: float = 0.8
    minhash_num_perm: int = 128
    
    # Perplexity filtering (KenLM)
    perplexity_cutoff: float = 100.0
    kenlm_model_path: str = "data/h-e1/en.arpa.bin"
    
    # Variant selection
    variant: str = "transferred"  # Options: "baseline", "transferred", "stage_tuned"
```

---

## A-2: Training Configuration

**Applied:** Standard LLaMA fine-tuning defaults (Alpaca paper)

```python
@dataclass
class TrainingConfig:
    """Fine-tuning hyperparameters."""
    
    # Optimizer
    optimizer: str = "adamw"
    learning_rate: float = 2e-5
    betas: tuple = (0.9, 0.999)
    weight_decay: float = 0.01
    
    # Batch size
    batch_size: int = 128
    micro_batch_size: int = 4
    gradient_accumulation_steps: int = 32
    
    # Training duration
    epochs: int = 3
    
    # Loss computation
    loss_type: str = "causal_lm"
    mask_instruction_tokens: bool = True
    
    # Reproducibility
    seed: int = 42
    deterministic: bool = True
```

---

## A-3: Model Configuration

**Applied:** LLaMA-2-7B HuggingFace defaults

```python
@dataclass
class ModelConfig:
    """Model architecture and checkpoint configuration."""
    
    model_name: str = "meta-llama/Llama-2-7b-hf"
    tokenizer_name: str = "meta-llama/Llama-2-7b-hf"
    
    # Fine-tuning strategy
    full_finetuning: bool = True
    
    # Memory optimization
    gradient_checkpointing: bool = False  # Enable if OOM
    fp16: bool = False
    bf16: bool = True
```

---

## A-4: Dataset Configuration

**Applied:** Alpaca-52k standard preprocessing

```python
@dataclass
class DatasetConfig:
    """Dataset loading and preprocessing configuration."""
    
    # Source
    dataset_name: str = "tatsu-lab/alpaca"
    dataset_split: str = "train"
    
    # Splits
    train_split: float = 0.9
    val_split: float = 0.1
    
    # Preprocessing
    prompt_template: str = "### Instruction:\n{instruction}\n\n### Input:\n{input}\n\n### Response:\n{output}"
    max_length: int = 512
    
    # Caching
    cache_dir: str = "~/.cache/huggingface/"
```

---

## A-5: Evaluation Configuration

**Applied:** lm-evaluation-harness standard settings

```python
@dataclass
class EvaluationConfig:
    """Evaluation tasks and metrics configuration."""
    
    # Tasks
    tasks: list = field(default_factory=lambda: ["mmlu", "hellaswag"])
    num_fewshot: int = 0
    
    # Evaluation settings
    eval_batch_size: int = 8
    
    # Success criteria
    gate_type: str = "MUST_WORK"
    gate_threshold: float = 0.01  # ≤1% delta for transfer robustness
    benefit_threshold: float = 0.02  # ≥2% improvement for curation benefit
```

---

## A-6: Threshold Tuning Configuration (Stage-Tuned Variant)

**Applied:** Coarse grid search for PoC

```python
@dataclass
class ThresholdTuningConfig:
    """Grid search configuration for stage-tuned variant."""
    
    # Deduplication thresholds to test
    dedup_grid: list = field(default_factory=lambda: [0.6, 0.7, 0.8, 0.9])
    
    # Perplexity cutoffs to test
    perplexity_grid: list = field(default_factory=lambda: [50, 75, 100, 150, 200])
    
    # Tuning validation split
    tuning_val_split: float = 0.05
    
    # Selection criterion
    selection_metric: str = "validation_perplexity"
```

---

## A-7: Resource Configuration

**Applied:** Single A100 GPU setup

```python
@dataclass
class ResourceConfig:
    """Hardware and compute resource configuration."""
    
    # Device
    device: str = "cuda"
    gpu_device: int = 0
    
    # Mixed precision
    use_amp: bool = True
    amp_dtype: str = "bfloat16"
    
    # Parallelism
    num_workers: int = 4
    pin_memory: bool = True
```

---

## A-8: Path Configuration

**Applied:** Standard hypothesis folder structure

```python
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class PathConfig:
    """Directory paths for data, checkpoints, and outputs."""
    
    # Base directories
    hypothesis_dir: Path = field(default_factory=lambda: Path("docs/youra_research/h-e1"))
    data_dir: Path = field(default_factory=lambda: Path("data/h-e1"))
    
    # Data paths
    cache_dir: Path = field(default_factory=lambda: Path("~/.cache/huggingface/"))
    curated_data_dir: Path = field(default_factory=lambda: Path("data/h-e1/curated"))
    
    # Output paths
    output_dir: Path = field(default_factory=lambda: Path("docs/youra_research/h-e1/results"))
    checkpoint_dir: Path = field(default_factory=lambda: Path("docs/youra_research/h-e1/checkpoints"))
    figures_dir: Path = field(default_factory=lambda: Path("docs/youra_research/h-e1/figures"))
    
    # Figure settings
    figure_format: str = "png"
    figure_dpi: int = 300
    
    def __post_init__(self):
        """Create directories if they don't exist."""
        for path in [self.hypothesis_dir, self.data_dir, self.curated_data_dir,
                     self.output_dir, self.checkpoint_dir, self.figures_dir]:
            Path(path).expanduser().mkdir(parents=True, exist_ok=True)
```

---

## A-9: Logging Configuration

**Applied:** Standard Python logging

```python
@dataclass
class LoggingConfig:
    """Logging and monitoring configuration."""
    
    log_level: str = "INFO"
    log_file: str = "docs/youra_research/h-e1/experiment.log"
    
    # Training logging
    log_interval: int = 10  # Log every N steps
    save_interval: int = 500  # Save checkpoint every N steps
    
    # Verbose output
    verbose: bool = True
```

---

## Master Configuration

**Applied:** Nested dataclass pattern from h-m1

```python
from dataclasses import dataclass, field, asdict
import json
from pathlib import Path

@dataclass
class ExperimentConfig:
    """Master configuration for h-e1 experiment."""
    
    curation: CurationConfig = field(default_factory=CurationConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    threshold_tuning: ThresholdTuningConfig = field(default_factory=ThresholdTuningConfig)
    resources: ResourceConfig = field(default_factory=ResourceConfig)
    paths: PathConfig = field(default_factory=PathConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # Experiment metadata
    hypothesis_id: str = "h-e1"
    experiment_name: str = "curation_filter_transfer"
    
    def to_dict(self):
        """Convert config to dictionary."""
        return asdict(self)
    
    def save(self, path: Path):
        """Save configuration to JSON file."""
        with open(path, 'w') as f:
            json.dump(asdict(self), f, indent=2, default=str)
    
    @classmethod
    def load(cls, path: Path):
        """Load configuration from JSON file."""
        with open(path, 'r') as f:
            config_dict = json.load(f)
        return cls(**config_dict)
```

---

## Usage Example

```python
# Create default configuration
config = ExperimentConfig()

# Override for specific variant
config.curation.variant = "transferred"  # or "baseline", "stage_tuned"

# Save to file
config.save(Path("docs/youra_research/h-e1/config.json"))

# Load from file
config = ExperimentConfig.load(Path("docs/youra_research/h-e1/config.json"))
```

---

## Variant-Specific Configurations

### Baseline Variant (No Curation)

```python
baseline_config = ExperimentConfig()
baseline_config.curation.variant = "baseline"
baseline_config.curation.dedup_threshold = 1.0  # No deduplication
baseline_config.curation.perplexity_cutoff = float('inf')  # No filtering
```

### Transferred Variant (C4 Thresholds)

```python
transferred_config = ExperimentConfig()
transferred_config.curation.variant = "transferred"
transferred_config.curation.dedup_threshold = 0.8
transferred_config.curation.perplexity_cutoff = 100.0
```

### Stage-Tuned Variant (Optimized Thresholds)

```python
stage_tuned_config = ExperimentConfig()
stage_tuned_config.curation.variant = "stage_tuned"
# Thresholds set after grid search completes
# stage_tuned_config.curation.dedup_threshold = TUNED_VALUE
# stage_tuned_config.curation.perplexity_cutoff = TUNED_VALUE
```

---

## Validation Constraints

### Curation Parameters
- `dedup_threshold`: [0.0, 1.0]
- `perplexity_cutoff`: (0.0, inf)
- `variant`: {"baseline", "transferred", "stage_tuned"}

### Training Parameters
- `learning_rate`: (0.0, 1.0)
- `epochs`: [1, 10]
- `batch_size`: Multiple of `micro_batch_size * gradient_accumulation_steps`

### Evaluation Parameters
- `num_fewshot`: {0, 1, 5}
- `gate_threshold`: (0.0, 1.0)

---

## Configuration Dependencies

**Curation → Dataset:**
- `variant` selection determines which dataset split to load
- `dedup_threshold` and `perplexity_cutoff` applied during preprocessing

**Training → Model:**
- `gradient_checkpointing` must match model memory requirements
- `fp16`/`bf16` must be compatible with GPU architecture

**Dataset → Training:**
- `max_length` affects memory usage (adjust `micro_batch_size` if needed)

**Evaluation → Checkpoints:**
- Evaluation runs on all three variant checkpoints

---

## PRD Traceability

| Requirement | Config Section |
|-------------|----------------|
| FR-1.1 (MinHash LSH deduplication) | CurationConfig.dedup_threshold |
| FR-1.2 (KenLM perplexity filtering) | CurationConfig.perplexity_cutoff |
| FR-1.3 (Three curation variants) | CurationConfig.variant |
| FR-2.1 (LLaMA-2-7B loading) | ModelConfig.model_name |
| FR-2.2 (AdamW fine-tuning) | TrainingConfig (all fields) |
| FR-3.1 (MMLU evaluation) | EvaluationConfig.tasks |
| FR-3.2 (HellaSwag evaluation) | EvaluationConfig.tasks |
| FR-3.4 (Gate condition verification) | EvaluationConfig.gate_threshold |
| FR-5.1 (Dedup threshold grid) | ThresholdTuningConfig.dedup_grid |
| FR-5.2 (Perplexity cutoff grid) | ThresholdTuningConfig.perplexity_grid |
| NFR-1 (Reproducibility) | TrainingConfig.seed, deterministic |
| NFR-2 (Resource constraints) | ResourceConfig, ModelConfig.gradient_checkpointing |

---

## Notes

**EXISTENCE (PoC) Simplifications:**
- Single seed (no multi-run averaging)
- Fixed learning rate (no scheduling)
- 0-shot evaluation only (no few-shot)
- Coarse grid search (25 combinations max)

**Phase 4 Usage:**
Copy entire config.py to hypothesis code folder. Instantiate `ExperimentConfig()` and override `variant` field to run each experiment arm.
