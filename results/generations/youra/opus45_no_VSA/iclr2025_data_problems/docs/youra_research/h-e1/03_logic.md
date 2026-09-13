# Logic: H-E1 (EXISTENCE PoC)

Allocated tasks: A-3 (Model + TRAK attribution), A-4 (Training loop). Budget: 2 subtasks each.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design, no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-3: Model + TRAK attribution [Complexity: 10, Budget: 2]

**Applied**: Standard PyTorch + TRAK library (`traker` package) attribution pattern

### API Signatures

```python
# model.py
from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedModel, PreTrainedTokenizer
from traker import TRAKer
import numpy as np

def load_model_and_tokenizer(cfg: Config) -> tuple[PreTrainedModel, PreTrainedTokenizer]:
    """Load Pythia-1B model + tokenizer to GPU."""
    ...

class Attributor:
    def __init__(self, model: PreTrainedModel, train_set_size: int, save_dir: str = "trak_results"):
        """Wrap TRAKer; train_set_size = len(corpus) for this injection run."""
        self.traker = TRAKer(model=model, task="text_generation",
                              train_set_size=train_set_size, save_dir=save_dir)

    def featurize_train(self, corpus: list[str], tokenizer: PreTrainedTokenizer, batch_size: int = 16) -> None:
        """Compute + save TRAK features for full training corpus. No return."""
        ...

    def score(self, benchmark: list[dict], tokenizer: PreTrainedTokenizer) -> np.ndarray:
        """Score MMLU benchmark samples against train set.
        Returns: [len(benchmark), train_set_size] attribution matrix."""
        ...

def compute_ccr(scores: np.ndarray, injected_positions: list[int]) -> float:
    """CCR = mean attribution mass on injected_positions / total attribution mass.
    scores: [n_benchmark, train_set_size]; injected_positions: indices into train_set_size dim.
    Returns: float in [0, 1]."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| scores | [n_benchmark, train_set_size] | TRAK attribution matrix |
| injected_positions | list[int], len = round(rate * len(corpus)) | indices into train_set_size axis |

### Pseudo-code

```
compute_ccr(scores, injected_positions):
  contaminated_mass = abs(scores[:, injected_positions]).sum()
  total_mass = abs(scores).sum()
  return contaminated_mass / total_mass
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A3-1 | Model load + TRAKer init | `load_model_and_tokenizer`, `Attributor.__init__`, `featurize_train` |
| L-A3-2 | Scoring + CCR | `Attributor.score`, `compute_ccr` |

---

## A-4: Training loop [Complexity: 9, Budget: 2]

**Applied**: Standard PyTorch AdamW fine-tune loop with gradient accumulation

### API Signatures

```python
# train.py
from transformers import PreTrainedModel
from torch.optim import AdamW

def train_one_run(cfg: Config, corpus: list[str], injection_rate: float) -> tuple[PreTrainedModel, list[int]]:
    """Fine-tune fresh Pythia-1B on corpus (with injected samples at injection_rate).
    Returns: (trained_model, injected_positions)."""
    ...

def _make_dataloader(corpus: list[str], tokenizer, batch_size: int, seed: int):
    """Tokenize + batch corpus. Yields input_ids: [B, seq_len]."""
    ...

def _train_step(model: PreTrainedModel, batch: dict, optimizer: AdamW, grad_accum: int, step: int) -> float:
    """One fwd/bwd/step w/ grad accumulation. Returns loss (float)."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, seq_len] | B=cfg.batch_size / grad_accum per micro-step |
| logits | [B, seq_len, vocab] | CausalLM output |
| loss | scalar | CE loss, accumulated over grad_accum micro-steps |

### Pseudo-code

```
train_one_run(cfg, corpus, injection_rate):
  corpus_c, injected_positions = inject_benchmark(corpus, benchmark, injection_rate, cfg.seed)
  model, tok = load_model_and_tokenizer(cfg)
  optimizer = AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay, betas=cfg.betas)
  loader = _make_dataloader(corpus_c, tok, cfg.batch_size // cfg.grad_accum, cfg.seed)
  for step in range(cfg.train_steps):
      batch = next(loader)
      _train_step(model, batch, optimizer, cfg.grad_accum, step)
  return model, injected_positions
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A4-1 | Dataloader + optimizer setup | `_make_dataloader`, AdamW init in `train_one_run` |
| L-A4-2 | Train step loop | `_train_step`, main loop in `train_one_run` |
