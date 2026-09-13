# H-M4 Architecture: Scale Transfer Validation

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Scale Transfer Pipeline                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────────────────┐│
│  │ RedPajama-v2 │────▶│ DataPipeline │────▶│ Filtered Token Streams   ││
│  │   (source)   │     │  (filter)    │     │ • p44.5 (optimal)        ││
│  └──────────────┘     └──────────────┘     │ • default threshold      ││
│                              │              └───────────┬──────────────┘│
│                              │                          │               │
│                              ▼                          ▼               │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                       ModelTrainer                                │  │
│  │  ┌─────────────────────┐    ┌─────────────────────┐              │  │
│  │  │ GPT-2 125M (10B tok)│    │ GPT-2 1B (20B tok)  │              │  │
│  │  │ • optimal threshold │    │ • optimal threshold │              │  │
│  │  │ • default threshold │    │ • default threshold │              │  │
│  │  └──────────┬──────────┘    └──────────┬──────────┘              │  │
│  └─────────────┼────────────────────────────┼────────────────────────┘  │
│                │                            │                           │
│                ▼                            ▼                           │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                        Evaluator                                  │  │
│  │    lm-eval-harness: hellaswag, arc_easy, piqa, winogrande        │  │
│  └──────────────────────────────────┬───────────────────────────────┘  │
│                                     │                                   │
│                                     ▼                                   │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      ScaleAnalyzer                                │  │
│  │    Compare threshold effectiveness: 125M vs 1B                    │  │
│  │    Hypothesis: p44.5 transfers across scales                      │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. DataPipeline

**Purpose:** Filter RedPajama-v2 at configurable perplexity thresholds

| Input | Output |
|-------|--------|
| `RedPajama-v2 raw shards` | `TokenizedDataset` (streaming) |

```python
class DataPipeline:
    def __init__(self, threshold: float, tokenizer: str = "gpt2")
    def filter(self, shard: Shard) -> Iterator[Document]  # PPL <= threshold
    def tokenize(self, docs: Iterator[Document]) -> TokenizedDataset
    def stream(self, target_tokens: int) -> DataLoader
```

**Configurations:**
- `threshold_optimal = 44.5` (from h-m1)
- `threshold_default = 100.0` (baseline)

### 2. ModelTrainer

**Purpose:** Train GPT-2 variants from scratch

| Input | Output |
|-------|--------|
| `TokenizedDataset`, `ModelConfig` | `TrainedCheckpoint` |

```python
class ModelTrainer:
    def __init__(self, model_size: Literal["125M", "1B"], config: TrainConfig)
    def train(self, dataset: TokenizedDataset) -> Checkpoint
    def save_checkpoint(self, path: str) -> None
```

**Training specs:**
| Scale | Tokens | Batch | LR |
|-------|--------|-------|-----|
| 125M | 10B | 256 | 6e-4 |
| 1B | 20B | 512 | 3e-4 |

### 3. Evaluator

**Purpose:** Benchmark via lm-eval-harness

| Input | Output |
|-------|--------|
| `Checkpoint` | `EvalResults` dict |

```python
class Evaluator:
    TASKS = ["hellaswag", "arc_easy", "piqa", "winogrande"]
    
    def evaluate(self, checkpoint: Checkpoint) -> dict[str, float]
    def compare(self, a: EvalResults, b: EvalResults) -> ComparisonReport
```

### 4. ScaleAnalyzer

**Purpose:** Test threshold transfer hypothesis

| Input | Output |
|-------|--------|
| `EvalResults` for all 4 runs | `TransferReport` |

```python
class ScaleAnalyzer:
    def compute_gain(self, optimal: EvalResults, default: EvalResults) -> float
    def test_transfer(self, gain_125m: float, gain_1b: float) -> TransferResult
    # Transfer confirmed if: gain_1b >= 0.5 * gain_125m
```

## Data Flow

```
RedPajama-v2
    │
    ├──[threshold=44.5]──▶ 10B tokens ──▶ GPT-2 125M ──▶ eval ──┐
    ├──[threshold=100 ]──▶ 10B tokens ──▶ GPT-2 125M ──▶ eval ──┤
    ├──[threshold=44.5]──▶ 20B tokens ──▶ GPT-2 1B   ──▶ eval ──┤
    └──[threshold=100 ]──▶ 20B tokens ──▶ GPT-2 1B   ──▶ eval ──┘
                                                                │
                                              ScaleAnalyzer ◀───┘
                                                    │
                                              TransferReport
```

## Interface Contracts

```python
# DataPipeline → ModelTrainer
class TokenizedDataset(Protocol):
    def __iter__(self) -> Iterator[torch.Tensor]: ...
    def __len__(self) -> int: ...  # total tokens

# ModelTrainer → Evaluator  
@dataclass
class Checkpoint:
    model_path: str
    config: dict
    metadata: dict  # tokens_seen, threshold, scale

# Evaluator → ScaleAnalyzer
@dataclass
class EvalResults:
    checkpoint: Checkpoint
    scores: dict[str, float]  # task → accuracy
    avg_score: float

# ScaleAnalyzer output
@dataclass
class TransferResult:
    hypothesis_confirmed: bool
    gain_125m: float
    gain_1b: float
    transfer_ratio: float  # gain_1b / gain_125m
```

## Epic-Level Task Breakdown

| Epic | Description | Deliverable |
|------|-------------|-------------|
| **E1: Data Preparation** | Set up RedPajama-v2 streaming, implement PPL filter at 44.5 and 100.0 thresholds | `DataPipeline` class, 4 dataset configs |
| **E2: 125M Training** | Train GPT-2 125M from scratch (2 runs: optimal + default threshold) | 2 checkpoints, training logs |
| **E3: 1B Training** | Train GPT-2 1B from scratch (2 runs: optimal + default threshold) | 2 checkpoints, training logs |
| **E4: Evaluation** | Run lm-eval-harness on all 4 checkpoints | `EvalResults` for each |
| **E5: Scale Analysis** | Compute gains, test transfer hypothesis | `TransferReport`, figures |
| **E6: Ablation** | Optional: test intermediate thresholds (30, 60, 80) at 1B | Sensitivity analysis |
| **E7: Documentation** | Write up results for Phase 5 | Final report markdown |

## Dependencies

```
E1 ──▶ E2 ──┐
            ├──▶ E4 ──▶ E5 ──▶ E7
E1 ──▶ E3 ──┘
            
E6 runs parallel with E5 (optional)
```

---

*Skipped: complex config system, checkpoint versioning, distributed training orchestration. Add when scaling beyond 1B or multi-node.*
