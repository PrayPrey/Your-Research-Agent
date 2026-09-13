# Logic: H-E1 Structural Enumeration Preference

**Hypothesis Type**: EXISTENCE (PoC)
**Applied**: Standard PyTorch ABC pattern, HuggingFace AutoModel loading

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code found
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-3: Multi-RM Inference [Complexity: 15, Budget: 4 subtasks]

**Applied**: HuggingFace AutoModel with trust_remote_code, sequential load/unload pattern

### API Signatures

```python
# code/inference/reward_models.py

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
import torch
from torch import Tensor

class BaseRewardModel(ABC):
    """Abstract base for all reward model adapters."""

    model_id: str  # HuggingFace model identifier

    @abstractmethod
    def load(self, device: str, use_4bit: bool = False) -> None:
        """Load model and tokenizer onto device."""
        ...

    @abstractmethod
    def score(self, prompt: str, response: str) -> float:
        """Score single (prompt, response) pair. Returns raw scalar."""
        ...

    def score_batch(
        self,
        pairs: List[Tuple[str, str]],
        batch_size: int = 16,
    ) -> List[float]:
        """Batch score. pairs: List of (prompt, response). Returns List[float] len=N."""
        # N = len(pairs); processes in chunks of batch_size
        ...

    def normalize_scores(self, scores: List[float]) -> List[float]:
        """Min-max normalize to [0, 1]. Returns List[float] len=N."""
        ...

    def unload(self) -> None:
        """Delete model/tokenizer and free GPU memory."""
        ...


class ArmoRM(BaseRewardModel):
    """RLHFlow/ArmoRM-Llama3-8B-v0.1 - Llama3 + MoE gating head."""

    model_id: str = "RLHFlow/ArmoRM-Llama3-8B-v0.1"

    def load(self, device: str, use_4bit: bool = False) -> None:
        # AutoModelForSequenceClassification.from_pretrained(..., trust_remote_code=True)
        ...

    def score(self, prompt: str, response: str) -> float:
        # Tokenize chat template; forward pass; extract scalar logit
        # Input token ids: [1, seq_len] -> output scalar
        ...


class UltraRM(BaseRewardModel):
    """openbmb/UltraRM-13b - Llama + scalar regression head."""

    model_id: str = "openbmb/UltraRM-13b"

    def load(self, device: str, use_4bit: bool = False) -> None:
        # If use_4bit: BitsAndBytesConfig(load_in_4bit=True)
        ...

    def score(self, prompt: str, response: str) -> float:
        # Input token ids: [1, seq_len] -> scalar reward
        ...


class StarlingRM(BaseRewardModel):
    """berkeley-nest/Starling-RM-7B-alpha - Llama2-7B-Chat reward head."""

    model_id: str = "berkeley-nest/Starling-RM-7B-alpha"

    def load(self, device: str, use_4bit: bool = False) -> None: ...

    def score(self, prompt: str, response: str) -> float:
        # Input token ids: [1, seq_len] -> scalar
        ...


class PairRM(BaseRewardModel):
    """llm-blender/PairRM - DeBERTa-v3-large pairwise comparator."""

    model_id: str = "llm-blender/PairRM"

    def load(self, device: str, use_4bit: bool = False) -> None:
        # llm_blender.LLMBlender(); blender.loadranker("llm-blender/PairRM")
        ...

    def score(self, prompt: str, response: str) -> float:
        # Single-response mode: compare against empty/null baseline
        # Returns win-probability scalar in [0, 1]
        ...

    def score_pair(
        self, prompt: str, response_a: str, response_b: str
    ) -> float:
        # Pairwise mode: P(A > B). response_b = synthesized baseline.
        # Returns float in [0, 1]
        ...

    def score_batch(
        self,
        pairs: List[Tuple[str, str]],
        batch_size: int = 16,
    ) -> List[float]:
        # Override: uses blender.rank() API for batch pairwise scoring
        ...


def load_all_models(config: "InferenceConfig") -> dict[str, BaseRewardModel]:
    """Instantiate all 4 RM adapters. Does NOT call .load() - caller manages lifecycle."""
    # Returns {"armo": ArmoRM(), "ultra": UltraRM(), "starling": StarlingRM(), "pairrm": PairRM()}
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, seq_len] | Single pair tokenized |
| input_ids (batch) | [B, max_seq_len] | Padded batch, B <= 16 |
| logits / reward | [1] or scalar | Raw reward score |
| normalized scores | [N] | N = total pairs scored |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | BaseRewardModel ABC | Abstract interface + score_batch loop + normalize_scores |
| L-3-2 | ArmoRM + UltraRM adapters | Load with trust_remote_code/4bit; score via chat template |
| L-3-3 | StarlingRM + PairRM adapters | StarlingRM standard; PairRM via llm_blender API |
| L-3-4 | Sequential lifecycle + load_all_models | unload(), VRAM management, load_all_models factory |

---

## A-2: Stimulus Generation [Complexity: 13, Budget: 2 subtasks]

**Applied**: Standard dataclass + factory pattern

### API Signatures

```python
# code/data/stimulus_generator.py

from dataclasses import dataclass
from typing import List, Dict, Tuple
import json
import re

@dataclass
class StimulusPair:
    id: str                # "{prompt_idx}_{variant_idx}"
    prompt: str
    enumerated: str        # Bulleted/numbered response
    synthesized: str       # Prose-style equivalent
    correctness: str       # "high" | "low"
    completeness: str      # "complete" | "partial"


class EnumerationClassifier:
    """Regex-based classifier for detecting enumeration structure."""

    # Patterns: numbered lists (1. 2. 3.), bullets (- * •), header lines
    _ENUM_PATTERN: re.Pattern = re.compile(
        r"(^\s*[\d]+[\.\)]\s+|^\s*[-\*\u2022]\s+)", re.MULTILINE
    )

    def classify(self, text: str) -> bool:
        """Return True if text contains enumeration structure."""
        ...

    def validate_accuracy(self, labeled_samples: List[Dict]) -> float:
        """Compute agreement rate vs human labels. labeled_samples: List[{text, label}]."""
        # Returns float in [0, 1]; target > 0.95
        ...


class StimulusGenerator:
    """Generate 2x2x2 factorial stimulus pairs via LLM API calls."""

    def __init__(self, config: "StimulusConfig") -> None:
        # Sets seed, initializes LLM client
        ...

    def generate_prompts(self) -> List[str]:
        """Generate config.n_prompts diverse base prompts. Returns List[str] len=75."""
        ...

    def generate_variants(self, prompt: str) -> List[StimulusPair]:
        """Generate 8 variants for one prompt (2x2x2 factorial). Returns List[StimulusPair] len=8."""
        # Factors: structure (enum/synth) x correctness (high/low) x completeness (complete/partial)
        ...

    def validate_length_match(self, pairs: List[StimulusPair]) -> bool:
        """Check |len(enum) - len(synth)| / len(synth) <= tolerance for all pairs."""
        # Returns True if ALL pairs within config.length_tolerance (0.02)
        ...

    def validate_cross_contamination(
        self, pairs: List[StimulusPair]
    ) -> Dict[str, float]:
        """Compute Cohen's d for non-structure factors as contamination check."""
        # Returns {"correctness_d": float, "completeness_d": float}; target |d| < 0.2
        ...

    def generate_and_save(self, output_path: str) -> List[StimulusPair]:
        """Run full generation pipeline and serialize to JSON. Returns all pairs."""
        # 75 prompts x 8 variants = 600 StimulusPairs
        ...

    def load(self, path: str) -> List[StimulusPair]:
        """Deserialize stimuli.json. Returns List[StimulusPair] len=600."""
        ...
```

### Pseudo-code (variant generation - non-trivial factorial design)

```
generate_variants(prompt):
    pairs = []
    for correctness in ["high", "low"]:
        for completeness in ["complete", "partial"]:
            # Call LLM once with system prompt specifying both dimensions
            base_response = llm_call(prompt, correctness, completeness)
            # Derive enumerated version: reformat base_response into bullet/numbered list
            enum_response = llm_call(base_response, style="enumerated")
            # Derive synthesized version: reformat into prose
            synth_response = llm_call(base_response, style="synthesized")
            pairs.append(StimulusPair(...))
    return pairs  # len=8
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | StimulusPair + EnumerationClassifier | Dataclass definition + regex classifier + validate_accuracy |
| L-2-2 | StimulusGenerator core methods | generate_prompts, generate_variants, validate_length_match, validate_cross_contamination, generate_and_save, load |

---

## Stats API Reference (A-4, no budget allocation here)

```python
# code/analysis/stats.py

import numpy as np
import pandas as pd
from scipy import stats
from typing import Tuple, Dict, List

def cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """Pooled-SD Cohen's d. group1/group2: [N] arrays of scores."""
    ...

def cohens_d_ci(
    d: float, n1: int, n2: int, alpha: float = 0.05
) -> Tuple[float, float]:
    """Non-central t-distribution 95% CI for d. Returns (ci_low, ci_high)."""
    ...

def paired_ttest(
    group1: np.ndarray, group2: np.ndarray
) -> Tuple[float, float]:
    """scipy.stats.ttest_rel wrapper. Returns (t_stat, p_value)."""
    ...

def check_gate_condition(
    per_rm_df: pd.DataFrame, d_threshold: float = 0.3, min_models: int = 2
) -> bool:
    """Return True if >= min_models rows have cohens_d >= d_threshold."""
    # per_rm_df columns: [rm, cohens_d, ci_low, ci_high, p_value, n]
    ...
```
