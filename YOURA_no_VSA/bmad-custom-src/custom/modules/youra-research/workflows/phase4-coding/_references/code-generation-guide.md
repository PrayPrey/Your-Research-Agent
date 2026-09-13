# Code Generation Guide

> **Reference Document** - Used by step-02-coder-loop.md
---

## 0. Spec-Driven Code Generation (SDD Foundation)

### Core Principle: Understand Specs → Generate Code Dynamically

```
┌─────────────────────────────────────────────────────────────────────┐
│ ❌ WRONG: Copy template → Replace variables (mechanical) │
│ ✅ CORRECT: Read specs → Understand → Generate appropriate code │
└─────────────────────────────────────────────────────────────────────┘
```

> 💡 **TIP: Pydantic for Data Integrity Validation**
> After extracting information from spec files, you MAY use Pydantic models
> to validate the extracted data. This helps catch errors early:
> - Validate tensor shape formats (e.g., "[B, N, F]" is valid)
> - Ensure config field types are correct
> - Verify required fields are present
> This is optional but recommended for robust code generation.

### Spec Files to Read and Understand

| File | What to Extract | Use For |
|------|-----------------|---------|
| **03_logic.md** | Class names, method signatures, tensor shapes | API implementation |
| **03_config.md** | Dataclass fields, defaults, types | Config classes |
| **03_architecture.md** | File paths, dependencies, module structure | File organization |
| **02c_experiment_brief.md** | Dataset loading, reality tests, success criteria | Experiment code |

### How to Analyze Specs (Dynamic, Not Template!)

```python
# FOR EACH Task:

# 1. Read ALL spec files
logic_content = Read(logic_file) # 03_logic.md
config_content = Read(config_file) # 03_config.md
arch_content = Read(architecture_file) # 03_architecture.md
experiment_content = Read(experiment_brief) # 02c_experiment_brief.md

# 2. UNDERSTAND what this specific task requires:

# From 03_logic.md - find the relevant class/function:
# - "class AttentionLayer(nn.Module)" → implement this class
# - "forward(x: Tensor[B,N,D], mask: Tensor[B,N]) -> Tensor[B,N,D]" → this signature
# - tensor_shapes: {"input": "[B,N,D]", "output": "[B,N,D]"} → validate these

# From 03_config.md - find the relevant config:
# - "@dataclass class AttentionConfig" → create this config
# - "num_heads: int = 8" → use this default

# From 03_architecture.md - find file location:
# - "models/attention.py" → write to this path
# - "depends on: torch, base_model" → ensure these imports

# From 02c_experiment_brief.md - find experiment requirements:
# - "dataset: Cora via torch_geometric" → use this dataset
# - "reality_tests: [determinism, sensitivity]" → include these tests

# 3. Generate code that matches YOUR UNDERSTANDING of the specs
# NOT by filling in a template!
```

### Example: Understanding → Generation

```python
# After reading 03_logic.md, you understand:
# "AttentionLayer needs forward(x, mask) that returns same shape as input"

# Then you generate (this is an EXAMPLE, not a template!):
class AttentionLayer(nn.Module):
    def __init__(self, config: AttentionConfig):
        super().__init__()
        self.num_heads = config.num_heads
        # ... implementation based on your understanding

    def forward(self, x: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        # Signature matches 03_logic.md: forward(x: [B,N,D], mask: [B,N]) -> [B,N,D]
        B, N, D = x.shape
        # ... implementation
        return output # shape: [B, N, D] as specified
```

---

## 1. Code Structure Standards

### File Header Template

```python
# {filename}.py
# Phase 4 Generated Code for Hypothesis: {hypothesis_id}
# Generated: {date}
# Task: {task_id} - {task_title}

import torch
import torch.nn as nn
from typing import Optional, Dict, List, Tuple
```

### Type Hints (MANDATORY - Critical for Serena MCP!)

**Why Type Hints Are Required:**

| Reason | Impact |
|--------|--------|
| **Serena MCP Compatibility** | `find_symbol`, `get_symbols_overview` work better with typed code |
| **Validator Accuracy** | API matching against 03_logic.md is more precise |
| **Coder-Validator Loop** | Error detection and fix suggestions are more accurate |
| **Code Quality** | Self-documenting, IDE support, runtime type checking |

```python
# ✅ CORRECT - All functions have type hints (Serena-friendly!)
def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
    ...

def compute_loss(self, predictions: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
    ...

# ❌ WRONG - Missing type hints (Serena analysis degraded!)
def forward(self, x, mask=None):
    ...
```

**Type Hint Checklist:**
- [ ] All function parameters have type hints
- [ ] All function return types specified
- [ ] Class attributes typed in `__init__` or as class variables
- [ ] Use `Optional[T]` for nullable parameters
- [ ] Use `Tuple`, `List`, `Dict` from `typing` module

### Docstrings (MANDATORY)

```python
def forward(self, x: torch.Tensor) -> torch.Tensor:
    """Forward pass of the model.

    Args:
        x: Input tensor of shape (B, C, H, W) for images
           or (B, seq_len, dim) for sequences

    Returns:
        Output tensor of shape (B, num_classes)
    """
```

---

## 2. Standard DL Module Patterns

### Model Pattern (nn.Module)

```python
class MyModel(nn.Module):
    """Model description from 03_logic.md."""

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int = 128,
        output_dim: int = 10,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.encoder = nn.Linear(input_dim, hidden_dim)
        self.classifier = nn.Linear(hidden_dim, output_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass. x: [B, input_dim] -> [B, output_dim]"""
        h = self.dropout(torch.relu(self.encoder(x)))
        return self.classifier(h)
```

### Dataset Pattern

```python
from torch.utils.data import Dataset, DataLoader

class MyDataset(Dataset):
    """Dataset for {task_name}."""

    def __init__(self, data_path: str, split: str = "train"):
        self.data = self._load_data(data_path, split)

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.data[idx]

    def _load_data(self, path: str, split: str):
        # Load from 03_logic.md specified source
        # NO synthetic fallback!
        ...
```

### Training Loop Pattern

```python
def train_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
) -> Dict[str, float]:
    """Train for one epoch."""
    model.train()
    total_loss = 0.0

    for batch in dataloader:
        x, y = batch[0].to(device), batch[1].to(device)

        optimizer.zero_grad()
        output = model(x)
        loss = criterion(output, y)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    return {"loss": total_loss / len(dataloader)}
```

### Evaluation Pattern

```python
@torch.no_grad()
def evaluate(
    model: nn.Module,
    dataloader: DataLoader,
    device: torch.device,
) -> Dict[str, float]:
    """Evaluate model on dataset."""
    model.eval()
    predictions, targets = [], []

    for batch in dataloader:
        x, y = batch[0].to(device), batch[1].to(device)
        output = model(x)
        predictions.append(output.argmax(dim=-1))
        targets.append(y)

    predictions = torch.cat(predictions)
    targets = torch.cat(targets)
    accuracy = (predictions == targets).float().mean().item()

    return {"accuracy": accuracy}
```

---

## 3. Test Generation

> **See `test-generation-guide.md` for detailed SDD test generation process.**

Key points:
- Generate tests BEFORE implementation (SDD TEST phase)
- Read specs → Understand → Generate tests dynamically
- Minimum 3 tests per task
- No placeholder tests (`pass`, `...`, `assert True` FORBIDDEN)

---

## 4. Error-Resistant Patterns

### Optional Library Import

```python
# For OPTIONAL libraries only (NOT for data!)
try:
    import wandb
    HAS_WANDB = True
except ImportError:
    HAS_WANDB = False
    wandb = None

# Usage
if HAS_WANDB and wandb is not None:
    wandb.log({"loss": loss})
```

### Device Handling

```python
def get_device() -> torch.device:
    """Get best available device."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")
```

### Reproducibility

```python
def set_seed(seed: int = 42):
    """Set random seeds for reproducibility."""
    import random
    import numpy as np

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
```

---

## 5. CRITICAL: Research Data Policy (NO FALLBACK!)

**Research data MUST NEVER use synthetic fallback!**

### Fallback Policy Matrix

| Type | Fallback Allowed? | Examples |
|------|-------------------|----------|
| Optional libraries | ✅ Allowed | wandb, tqdm, tensorboard |
| Utility features | ✅ Allowed | colorama, rich, progress bars |
| **Research datasets** | ❌ **FORBIDDEN** | Any dataset in 03_logic.md |
| **Experiment data** | ❌ **FORBIDDEN** | Any data for hypothesis validation |

### Correct Data Loading Pattern

```python
# ❌ FORBIDDEN - SYSTEM FAILURE!
def load_data():
    try:
        return load_real_data()
    except:
        return create_synthetic_data() # ABSOLUTELY FORBIDDEN!

# ✅ CORRECT
def load_data():
    try:
        return load_real_data()
    except Exception as e:
        raise DataLoadError(
            f"Data loading failed. Synthetic fallback FORBIDDEN.\n"
            f"Cause: {e}\n"
            f"Solution: Use Exa MCP to find solution"
        )
```

### Data Loader Checklist

- [ ] Use ONLY datasets specified in 03_logic.md
- [ ] Explicitly specify real dataset source
- [ ] NO synthetic/random data generation as fallback
- [ ] Clear error message on load failure

---

## 6. Cross-File Dependencies

### Import Pattern (Dynamic - from 03_architecture.md!)

```
┌─────────────────────────────────────────────────────────────────────┐
│ ❌ WRONG: Use fixed import structure │
│ ✅ CORRECT: Read 03_architecture.md → Use defined module paths │
└─────────────────────────────────────────────────────────────────────┘
```

**How to determine imports:**

1. Read `03_architecture.md` for module structure
2. Identify which modules depend on each other
3. Generate imports that match the architecture

```python
# Example: If 03_architecture.md defines:
# - models/encoder.py depends on config/encoder_config.py
# Then generate:
from config.encoder_config import EncoderConfig

# If architecture uses relative imports within package:
from .base import BaseModel
```

### File Structure (Dynamic - from 03_architecture.md!)

```
DO NOT use a fixed file structure!

Read 03_architecture.md to understand:
- Which directories are defined
- Which files belong where
- Module dependencies and Epic groupings

The file structure varies per hypothesis based on:
- Hypothesis requirements
- Epic definitions in architecture
- Module dependencies
```

---

## Quick Reference Checklist

### Before Writing Code
- [ ] Read 03_logic.md for API signatures
- [ ] Search Archon KB for patterns
- [ ] Check 03_config.md for configuration schema

### While Writing Code
- [ ] Type hints on all functions (Serena MCP compatibility!)
- [ ] Return type hints on all functions
- [ ] Class attributes typed
- [ ] Docstrings with Args/Returns/tensor shapes
- [ ] Match 03_logic.md signatures exactly
- [ ] Use config values, not hardcoded constants

### After Writing Code
- [ ] Generate test file (minimum 3 tests)
- [ ] Tests have real assertions (no placeholders)
- [ ] Imports resolve correctly
- [ ] Test Gate will verify before review transition

### Serena MCP Verification (Validator will check!)
- [ ] `mcp__serena__find_symbol` can locate all public functions
- [ ] `mcp__serena__get_symbols_overview` returns typed signatures
- [ ] API signatures match 03_logic.md exactly
