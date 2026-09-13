# Architecture Specification
# Hypothesis H-M1: Data Curation Causally Increases Information Density

**Version**: 1.0  
**Created**: 2026-08-28  
**Hypothesis ID**: h-m1  
**Type**: MECHANISM (extending h-e1)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Extending h-e1 validated implementation  
**Analyzed Path**: `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_data_problems/docs/youra_research/h-e1/code/`  
**Findings**: H-E1 implements C4 subset sampling with quality metrics computation. H-M1 adds active curation manipulation (MinHash dedup, perplexity filtering, domain resampling) + information density tracking (entropy, Fisher info) during training.

---

## Design Patterns Applied

Applied: Training-time metric computation (entropy/FIM hooks)  
Applied: Fractional factorial experimental design (9 conditions)

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| C4SubsetSampler | `import sys; sys.path.append('../h-e1/code'); from data.prepare_subsets import C4SubsetSampler` | `h-e1/code/data/prepare_subsets.py` |
| CONFIG | `from h_e1_code.config import CONFIG` | `h-e1/code/config.py` |

**Note**: H-E1 code is reusable for subset sampling infrastructure but not for actual curation logic (h-e1 used post-hoc measurement, h-m1 requires active manipulation).

---

## Module Structure

### CurationPipeline (`data/curate.py`)

**Dependencies**: datasets, datasketch, transformers

```python
class DataCurator:
    def __init__(self, dedup_ratio: float, filter_level: int, domain_mix: int): ...
    def deduplicate_minhash(self, texts: List[str]) -> List[str]: ...
    def filter_by_perplexity(self, texts: List[str], threshold: float) -> List[str]: ...
    def resample_domains(self, texts: List[str], urls: List[str]) -> List[str]: ...
    def curate_subset(self, c4_stream) -> List[str]: ...

def generate_all_conditions(output_dir: str) -> List[str]: ...
```

---

### InformationDensityAnalyzer (`metrics/density_analyzer.py`)

**Dependencies**: torch, transformers

```python
class InformationDensityAnalyzer:
    def __init__(self, model, vocab_size: int): ...
    def compute_entropy(self, logits: torch.Tensor) -> float: ...
    def compute_fisher_trace(self, model) -> float: ...
    def forward(self, input_ids: torch.Tensor, labels: torch.Tensor) -> Tuple[torch.Tensor, float, float]: ...
```

---

### TrainingPipeline (`train.py`)

**Dependencies**: transformers, InformationDensityAnalyzer

```python
class GPT2Trainer:
    def __init__(self, model_name: str, analyzer: InformationDensityAnalyzer): ...
    def train_condition(self, dataset_path: str, output_dir: str, steps: int): ...
    def log_metrics(self, step: int, loss: float, entropy: float, fisher: float): ...
    def save_checkpoint(self, step: int): ...

def train_all_conditions(condition_paths: List[str]): ...
```

---

### EvaluationMetrics (`evaluate.py`)

**Dependencies**: numpy, pandas, matplotlib

```python
def compute_entropy_reduction(baseline_entropy: float, curated_entropy: float) -> float: ...
def compute_fisher_increase(baseline_fisher: float, curated_fisher: float) -> float: ...
def check_monotonicity(condition_entropies: Dict[str, float]) -> bool: ...
def evaluate_all_conditions(metrics_log: pd.DataFrame) -> Dict: ...
def plot_gate_metrics(results: Dict, save_path: str): ...
```

---

## File Structure

```
h-m1/
├── code/
│   ├── data/
│   │   └── curate.py          # MinHash dedup + filtering + domain mix
│   ├── metrics/
│   │   └── density_analyzer.py # Entropy + Fisher info computation
│   ├── train.py                # GPT-2 training loop per condition
│   ├── evaluate.py             # Gate metrics + plots
│   ├── config.py               # Hyperparameters + conditions
│   └── run_experiment.py       # Orchestrator
├── data/
│   ├── curated/                # 9 × 50GB JSONL files
│   └── condition_metadata.json
├── results/
│   ├── checkpoints/            # Per-condition model checkpoints
│   ├── metrics_log.csv         # Entropy/Fisher trajectories
│   ├── gate_results.json
│   └── plots/                  # 6 figures
└── config.py
```

---

## Configuration Schema

```yaml
dataset:
  name: "allenai/c4"
  split: "en"
  subset_size_gb: 50
  num_conditions: 9

curation_conditions:
  # Fractional factorial (3^3 -> 9)
  baseline:        {dedup: 0.0,  filter: 0, mix: 0}
  dedup_low:       {dedup: 0.5,  filter: 0, mix: 0}
  dedup_high:      {dedup: 0.95, filter: 0, mix: 0}
  filter_med:      {dedup: 0.0,  filter: 1, mix: 0}
  filter_high:     {dedup: 0.0,  filter: 2, mix: 0}
  mix_only:        {dedup: 0.0,  filter: 0, mix: 1}
  dedup_filter:    {dedup: 0.95, filter: 2, mix: 0}
  dedup_mix:       {dedup: 0.95, filter: 0, mix: 1}
  full_curation:   {dedup: 0.95, filter: 2, mix: 1}

deduplication:
  method: "minhash_lsh"
  num_perm: 128
  jaccard_threshold: 0.8

filtering:
  model: "gpt2"
  levels:
    0: null               # No filtering
    1: "median"           # Median perplexity threshold
    2: "top25"            # Top 25% by perplexity

domain_mix:
  0: "uniform"            # Equal sampling across domains
  1: "quality_weighted"   # Resample by perplexity score

training:
  model: "gpt2"
  batch_size: 256
  micro_batch: 32
  gradient_accumulation: 8
  learning_rate: 6e-4
  warmup_steps: 2000
  total_steps: 50000
  optimizer: "adamw"
  adam_beta1: 0.9
  adam_beta2: 0.95
  adam_eps: 1e-8
  weight_decay: 0.1
  grad_clip: 1.0
  dropout: 0.1
  seed: 42
  log_interval: 100
  checkpoint_interval: 5000

evaluation:
  entropy_reduction_threshold: 0.20
  fisher_increase_threshold: 0.15
  monotonicity_required: true

compute:
  device: "cuda"
  gpu_per_condition: 1
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Curation Infrastructure | MinHash dedup, perplexity filter, domain resampler | 14 | 4+3+3+4 (dedup+filter+mix+integration) |
| M-2 | Density Analyzer | Entropy/Fisher info hooks, training wrapper | 11 | 3+3+3+2 (entropy+fisher+wrapper+logging) |
| M-3 | Dataset Generation | Generate 9 curated C4 subsets (50GB each) | 9 | 2+3+2+2 (sample+curate+validate+save) |
| M-4 | Training Pipeline | GPT-2 training loop, metric logging, checkpoints | 12 | 3+3+3+3 (loop+logging+checkpoints+per-condition) |
| M-5 | Condition Execution | Train all 9 conditions (orchestration) | 10 | 2+3+3+2 (setup+parallel+monitor+aggregate) |
| M-6 | Gate Evaluation | Entropy reduction, Fisher increase, monotonicity | 13 | 3+3+3+4 (entropy+fisher+monotonic+plots) |

**Distribution**: High(14-17): [M-1], Medium(9-13): [M-2, M-3, M-4, M-5, M-6]

**Complexity Scores**:
- M-1: Module_Size(4) + Dependencies(3) + Algorithm(3) + Integration(4) = 14
- M-2: Module_Size(3) + Dependencies(3) + Algorithm(3) + Integration(2) = 11
- M-3: Module_Size(2) + Dependencies(3) + Algorithm(2) + Integration(2) = 9
- M-4: Module_Size(3) + Dependencies(3) + Algorithm(3) + Integration(3) = 12
- M-5: Module_Size(2) + Dependencies(3) + Algorithm(3) + Integration(2) = 10
- M-6: Module_Size(3) + Dependencies(3) + Algorithm(3) + Integration(4) = 13

---

## Data Flow

```
C4 Stream (50GB)
  → DataCurator (9 conditions: dedup × filter × mix)
    → Curated Subsets (9 × 50GB JSONL)
      → GPT2Trainer + InformationDensityAnalyzer
        → Training Loop (50k steps per condition)
          → Metrics Log (entropy, Fisher trace, perplexity)
            → Gate Evaluation (reduction %, increase %, monotonicity)
              → PASS/PARTIAL/FAIL
```

---

## Core Mechanism Pseudo-code

```python
class InformationDensityAnalyzer:
    """Training-time entropy and Fisher info tracker."""
    
    def forward(self, input_ids, labels):
        # Standard forward
        outputs = self.model(input_ids, labels=labels)
        loss = outputs.loss
        
        # Entropy (before backward)
        with torch.no_grad():
            probs = F.softmax(outputs.logits, dim=-1)
            log_probs = F.log_softmax(outputs.logits, dim=-1)
            entropy = -(probs * log_probs).sum(dim=-1).mean().item()
        
        # Backward
        loss.backward()
        
        # Fisher trace (after backward)
        fisher_trace = sum((p.grad ** 2).sum().item() 
                          for p in self.model.parameters() 
                          if p.grad is not None)
        
        return loss, entropy, fisher_trace


class DataCurator:
    """Active curation manipulation."""
    
    def deduplicate_minhash(self, texts):
        from datasketch import MinHash, MinHashLSH
        lsh = MinHashLSH(threshold=0.8, num_perm=128)
        unique = []
        for i, text in enumerate(texts):
            m = MinHash(num_perm=128)
            for word in text.split():
                m.update(word.encode('utf8'))
            if not lsh.query(m):
                lsh.insert(f"doc_{i}", m)
                unique.append(text)
        return unique
    
    def filter_by_perplexity(self, texts, threshold):
        # Score with GPT-2, keep below threshold
        scores = [self.compute_perplexity(t) for t in texts]
        return [t for t, s in zip(texts, scores) if s < threshold]
    
    def resample_domains(self, texts, urls):
        # Weight by quality metric, resample
        weights = self.compute_quality_weights(urls)
        return random.choices(texts, weights=weights, k=len(texts))
```

---

## Success Criteria Implementation

```python
def check_gate(metrics_log: pd.DataFrame) -> str:
    """MUST_WORK gate decision."""
    # Extract final step metrics
    baseline = metrics_log[metrics_log['condition'] == 'baseline'].iloc[-1]
    full_curation = metrics_log[metrics_log['condition'] == 'full_curation'].iloc[-1]
    
    # Primary metrics
    entropy_reduction = 100 * (baseline['entropy'] - full_curation['entropy']) / baseline['entropy']
    fisher_increase = 100 * (full_curation['fisher_trace'] - baseline['fisher_trace']) / baseline['fisher_trace']
    
    # Monotonicity check
    dedup_conditions = metrics_log[metrics_log['condition'].str.contains('dedup')]
    dedup_monotonic = dedup_conditions['entropy'].is_monotonic_decreasing
    
    filter_conditions = metrics_log[metrics_log['condition'].str.contains('filter')]
    filter_monotonic = filter_conditions['entropy'].is_monotonic_decreasing
    
    mix_conditions = metrics_log[metrics_log['condition'].str.contains('mix')]
    mix_monotonic = len(mix_conditions) < 2 or mix_conditions['entropy'].iloc[-1] < baseline['entropy']
    
    monotonicity = dedup_monotonic and filter_monotonic and mix_monotonic
    
    # Gate decision
    if entropy_reduction > 20 and fisher_increase > 15 and monotonicity:
        return "PASS"
    elif entropy_reduction > 10 or fisher_increase > 10:
        return "PARTIAL"
    else:
        return "FAIL"
```

---

## Risk Mitigations

**Dedup removes too much**: Monitor dataset size, fallback Jaccard 0.7 if <5GB remaining  
**Fisher computation unstable**: Gradient clipping at 1.0, NaN checks, log scale  
**Compute budget exceeded**: Early stopping at 30k steps if >60 GPU-hours  
**Small effect size**: 1 modification attempt (increase curation strength 10%)

---

## External Dependencies

```
torch>=2.0
transformers>=4.30
datasets>=2.12
datasketch
numpy
pandas
matplotlib
seaborn
nltk
```

---

**END OF ARCHITECTURE**
