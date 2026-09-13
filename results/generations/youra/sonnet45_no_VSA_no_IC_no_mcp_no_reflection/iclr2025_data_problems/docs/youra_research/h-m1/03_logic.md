# Logic Specification: H-M1
# Data Curation Causally Increases Information Density

**Version**: 1.0  
**Created**: 2026-08-28  
**Hypothesis ID**: h-m1  
**Type**: EXISTENCE (PoC)  
**Budget**: 9 subtasks allocated

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)  
**Status**: API signatures verified from base code  
**Analyzed Path**: `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_data_problems/docs/youra_research/h-e1/code/`  
**Relevant Symbols**:
- `C4SubsetSampler.__init__(output_dir, subset_size_gb, seed)` - verified
- `C4SubsetSampler.sample_subset(dimension, level)` - verified
- `InformationDensityComputer.compute_token_entropy(texts)` - verified
- `CONFIG` dict structure - verified

**Note**: h-e1 uses post-hoc measurement (no active curation), h-m1 adds MinHash dedup + perplexity filtering.

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

```python
# From: h-e1/code/data/prepare_subsets.py (ACTUAL CODE)
class C4SubsetSampler:
    def __init__(self, output_dir: str, subset_size_gb: int = 10, seed: int = 42):
        """Initialize sampler."""
        ...

    def sample_subset(self, dimension: str, level: str) -> str:
        """Sample single subset. Returns: path to JSONL file."""
        ...

# From: h-e1/code/metrics/density.py
class InformationDensityComputer:
    def __init__(self, embedder_name: str = "all-MiniLM-L6-v2"):
        """Load sentence embedder."""
        ...

    def compute_token_entropy(self, texts: List[str]) -> float:
        """Unigram entropy. Returns: normalized H(X)."""
        ...

# From: h-e1/code/config.py
CONFIG = {
    "dataset_name": "allenai/c4",
    "subset_size_gb": 10,
    "seed": 42,
    ...
}
```

**Verified from**: h-e1/code/ (actual implementation)

---

## M-1: Curation Infrastructure [Complexity: 14, Budget: 4]

**Applied**: MinHash LSH pattern (PyTorch ecosystem standard), streaming deduplication

### API Signatures

```python
from typing import List, Dict, Optional
from datasketch import MinHash, MinHashLSH

class DataCurator:
    def __init__(
        self,
        dedup_ratio: float,
        filter_level: int,
        domain_mix: int,
        seed: int = 42
    ):
        """Initialize curation pipeline.
        
        Args:
            dedup_ratio: Target dedup (0.0=none, 0.95=aggressive)
            filter_level: 0=none, 1=median, 2=top25%
            domain_mix: 0=uniform, 1=quality_weighted
        """
        ...

    def deduplicate_minhash(
        self,
        texts: List[str],
        num_perm: int = 128,
        threshold: float = 0.8
    ) -> List[str]:
        """MinHash LSH dedup. texts: [N] -> [N*dedup_ratio]"""
        ...

    def filter_by_perplexity(
        self,
        texts: List[str],
        threshold: Optional[float] = None
    ) -> List[str]:
        """Filter by GPT-2 perplexity. texts: [N] -> [N*filter_ratio]"""
        ...

    def resample_domains(
        self,
        texts: List[str],
        urls: List[str]
    ) -> List[str]:
        """Resample by domain quality. texts: [N] -> [N] (resampled)"""
        ...

    def curate_subset(
        self,
        c4_stream,
        target_gb: int = 50
    ) -> List[Dict[str, str]]:
        """Pipeline: stream -> dedup -> filter -> mix. Returns: [{"text": ..., "url": ...}]"""
        ...
```

### Pseudo-code

```
curate_subset(c4_stream):
    texts, urls = [], []
    for sample in c4_stream:
        texts.append(sample["text"])
        urls.append(sample["url"])
        if len_gb(texts) >= target_gb:
            break
    
    if dedup_ratio > 0:
        texts = deduplicate_minhash(texts)
    
    if filter_level > 0:
        threshold = compute_perplexity_threshold(texts, filter_level)
        texts = filter_by_perplexity(texts, threshold)
    
    if domain_mix == 1:
        texts = resample_domains(texts, urls)
    
    return [{"text": t, "url": u} for t, u in zip(texts, urls)]
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | MinHash dedup | LSH with 128 perms, Jaccard 0.8 |
| L-1-2 | Perplexity filter | GPT-2 scoring, dynamic thresholds |
| L-1-3 | Domain resampler | Quality-weighted multinomial |
| L-1-4 | Pipeline integration | Compose: dedup -> filter -> mix |

---

## M-2: Density Analyzer [Complexity: 11, Budget: 3]

**Applied**: PyTorch training hooks, gradient-based FIM approximation

### API Signatures

```python
import torch
import torch.nn as nn
from torch import Tensor
from typing import Tuple

class InformationDensityAnalyzer(nn.Module):
    def __init__(self, model: nn.Module, vocab_size: int):
        """Wrap GPT-2 with density tracking."""
        super().__init__()
        self.model = model
        self.vocab_size = vocab_size

    def compute_entropy(self, logits: Tensor) -> float:
        """Shannon entropy from logits. logits: [B, L, V] -> scalar"""
        ...

    def compute_fisher_trace(self) -> float:
        """Diagonal FIM trace. Returns: sum(grad^2)"""
        ...

    def forward(
        self,
        input_ids: Tensor,
        labels: Tensor
    ) -> Tuple[Tensor, float, float]:
        """Forward + backward + metrics.
        
        Args:
            input_ids: [B, L]
            labels: [B, L]
        
        Returns:
            loss: scalar tensor
            entropy: float (bits/token)
            fisher_trace: float
        """
        ...
```

### Pseudo-code

```
forward(input_ids, labels):
    # Standard forward
    outputs = self.model(input_ids, labels=labels)
    loss = outputs.loss
    
    # Entropy (before backward)
    with torch.no_grad():
        probs = F.softmax(outputs.logits, dim=-1)  # [B, L, V]
        log_probs = F.log_softmax(outputs.logits, dim=-1)
        entropy = -(probs * log_probs).sum(dim=-1).mean().item()
    
    # Backward
    loss.backward()
    
    # Fisher trace (after backward)
    fisher_trace = sum(
        (p.grad ** 2).sum().item()
        for p in self.model.parameters()
        if p.grad is not None
    )
    
    return loss, entropy, fisher_trace
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Entropy hook | Softmax-based H(X) from logits |
| L-2-2 | Fisher trace | Diagonal FIM via grad squares |
| L-2-3 | Training wrapper | Inject into forward/backward |

---

## M-3: Dataset Generation [Complexity: 9, Budget: 2]

**Applied**: HuggingFace streaming, fractional factorial design

### API Signatures

```python
from typing import List, Dict

def generate_all_conditions(
    output_dir: str,
    base_config: Dict
) -> List[str]:
    """Generate 9 curated C4 subsets.
    
    Returns: List of JSONL file paths (one per condition)
    """
    ...

def validate_condition(
    jsonl_path: str,
    expected_dedup: float,
    expected_filter: int
) -> bool:
    """Check subset matches target params."""
    ...
```

### Tensor Shapes

N/A (data preprocessing)

### Pseudo-code

```
generate_all_conditions(output_dir):
    conditions = [
        {"dedup": 0.0, "filter": 0, "mix": 0},   # baseline
        {"dedup": 0.5, "filter": 0, "mix": 0},   # dedup_low
        {"dedup": 0.95, "filter": 0, "mix": 0},  # dedup_high
        {"dedup": 0.0, "filter": 1, "mix": 0},   # filter_med
        {"dedup": 0.0, "filter": 2, "mix": 0},   # filter_high
        {"dedup": 0.0, "filter": 0, "mix": 1},   # mix_only
        {"dedup": 0.95, "filter": 2, "mix": 0},  # dedup_filter
        {"dedup": 0.95, "filter": 0, "mix": 1},  # dedup_mix
        {"dedup": 0.95, "filter": 2, "mix": 1},  # full_curation
    ]
    
    paths = []
    for i, cond in enumerate(conditions):
        curator = DataCurator(**cond)
        c4_stream = load_dataset("allenai/c4", "en", streaming=True)
        curated = curator.curate_subset(c4_stream, target_gb=50)
        
        path = f"{output_dir}/condition_{i}.jsonl"
        save_jsonl(curated, path)
        paths.append(path)
    
    return paths
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Condition generator | Loop over 9 fractional factorial |
| L-3-2 | Validation | Check dedup/filter ratios match |

---

## M-4: Training Pipeline [Complexity: 12, Budget: 0]

**Applied**: HuggingFace Trainer API

### API Signatures

```python
from transformers import GPT2LMHeadModel, TrainingArguments, Trainer
from typing import Dict

class GPT2TrainerWithMetrics:
    def __init__(
        self,
        model_name: str = "gpt2",
        analyzer: InformationDensityAnalyzer = None
    ):
        """Initialize GPT-2 + density analyzer."""
        ...

    def train_condition(
        self,
        dataset_path: str,
        output_dir: str,
        total_steps: int = 50000
    ) -> Dict[str, float]:
        """Train single condition. Returns: final metrics"""
        ...

    def log_metrics(
        self,
        step: int,
        loss: float,
        entropy: float,
        fisher: float
    ) -> None:
        """Write to CSV + Tensorboard."""
        ...
```

### Subtasks [0/0 used]

Budget consumed by M-1, M-2, M-3. Use stdlib `Trainer` API.

---

## M-5: Condition Execution [Complexity: 10, Budget: 0]

**Applied**: Parallel execution pattern (stdlib multiprocessing)

### API Signatures

```python
def train_all_conditions(
    condition_paths: List[str],
    base_config: Dict
) -> pd.DataFrame:
    """Train 9 conditions in parallel. Returns: metrics_log DataFrame"""
    ...
```

### Subtasks [0/0 used]

Use stdlib `subprocess` or `multiprocessing.Pool`.

---

## M-6: Gate Evaluation [Complexity: 13, Budget: 0]

**Applied**: Statistical validation (NumPy/Pandas)

### API Signatures

```python
import pandas as pd
from typing import Dict

def compute_entropy_reduction(
    metrics_log: pd.DataFrame
) -> float:
    """(baseline - full_curation) / baseline * 100"""
    ...

def compute_fisher_increase(
    metrics_log: pd.DataFrame
) -> float:
    """(full_curation - baseline) / baseline * 100"""
    ...

def check_monotonicity(
    metrics_log: pd.DataFrame
) -> Dict[str, bool]:
    """Check dedup/filter/mix dimensions."""
    ...

def evaluate_gate(
    metrics_log: pd.DataFrame
) -> str:
    """PASS/PARTIAL/FAIL decision."""
    ...

def plot_gate_metrics(
    results: Dict,
    save_path: str
) -> None:
    """Bar chart: entropy reduction %, Fisher increase %"""
    ...
```

### Subtasks [0/0 used]

Use Pandas aggregations + matplotlib.

---

## Subtask Budget Summary

| Task | Budget | Used | Remaining |
|------|--------|------|-----------|
| M-1  | 4      | 4    | 0         |
| M-2  | 3      | 3    | 0         |
| M-3  | 2      | 2    | 0         |
| M-4  | 0      | 0    | 0         |
| M-5  | 0      | 0    | 0         |
| M-6  | 0      | 0    | 0         |
| **Total** | **9** | **9** | **0** |

---

## Configuration (from h-e1 base)

```python
# Reuse h-e1 base config, extend for h-m1
CONFIG = {
    **h_e1_CONFIG,  # Inherit dataset, seed, device
    
    # Curation params
    "dedup_num_perm": 128,
    "dedup_jaccard_threshold": 0.8,
    "perplexity_model": "gpt2",
    "filter_levels": {
        0: None,
        1: "median",
        2: "top25"
    },
    
    # Training (fixed hyperparams)
    "model": "gpt2",
    "batch_size": 256,
    "micro_batch": 32,
    "gradient_accumulation": 8,
    "learning_rate": 6e-4,
    "warmup_steps": 2000,
    "total_steps": 50000,
    "grad_clip": 1.0,
    
    # Gate thresholds
    "entropy_reduction_threshold": 20.0,  # percent
    "fisher_increase_threshold": 15.0,    # percent
}
```

---

## Key Design Decisions

1. **MinHash LSH over n-gram exact matching**: O(N) vs O(N^2), scales to 50GB
2. **Diagonal FIM only**: O(d) vs O(d^2), 125M params tractable
3. **Streaming dataset**: Avoid 50GB RAM load per condition
4. **Fixed seed, single run**: PoC budget (multi-seed in follow-up)
5. **Fractional factorial**: 9 conditions vs 27 full factorial (3^3)

---

**END OF LOGIC SPECIFICATION**
