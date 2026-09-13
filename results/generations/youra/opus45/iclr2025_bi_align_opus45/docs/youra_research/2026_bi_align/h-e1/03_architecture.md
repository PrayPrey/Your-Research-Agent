# Architecture: H-E1 Structural Enumeration Preference in RLHF-Trained Reward Models

**Applied**: HuggingFace AutoModel loading with trust_remote_code pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No prior code exists under h-e1/. All four reward models have well-documented HuggingFace model cards serving as implementation reference.

---

## Overview

Behavioral probing experiment (no model training). Pipeline: generate controlled stimuli → score with 4 reward models → compute effect sizes → visualize results.

**Hypothesis type**: EXISTENCE (PoC)
**Gate**: Cohen's d >= 0.3 in >= 2 architecturally distinct RMs

---

## File Organization

- `code/`
  - `config.py` - experiment configuration (single fixed config)
  - `data/stimulus_generator.py` - stimulus generation + validation
  - `inference/reward_models.py` - unified RM interface for all 4 models
  - `analysis/stats.py` - Cohen's d, CI, t-test, pooled effect
  - `analysis/visualize.py` - forest plot, violin, interaction, gate metrics
  - `run_experiment.py` - main pipeline orchestrator
- `data/` - output data artifacts (stimuli.json, raw_scores.json, etc.)
- `figures/` - PNG/PDF outputs

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies**: none

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class StimulusConfig:
    n_prompts: int = 75
    factors: List[str] = field(default_factory=lambda: ["structure", "correctness", "completeness"])
    length_tolerance: float = 0.02
    seed: int = 42

@dataclass
class InferenceConfig:
    batch_size: int = 16
    device: str = "cuda"
    dtype: str = "bfloat16"
    use_4bit: bool = False

@dataclass
class ExperimentConfig:
    stimulus: StimulusConfig = field(default_factory=StimulusConfig)
    inference: InferenceConfig = field(default_factory=InferenceConfig)
    output_dir: str = "data"
    figures_dir: str = "figures"
    rm_ids: List[str] = field(default_factory=lambda: ["armo", "ultra", "starling", "pairrm"])
```

---

### StimulusGenerator (`code/data/stimulus_generator.py`)

**Dependencies**: Config

```python
from dataclasses import dataclass
from typing import List, Dict
import json

@dataclass
class StimulusPair:
    id: str
    prompt: str
    enumerated: str
    synthesized: str
    correctness: str   # "high" | "low"
    completeness: str  # "complete" | "partial"

class EnumerationClassifier:
    def classify(self, text: str) -> bool: ...
    def validate_accuracy(self, labeled_samples: List[Dict]) -> float: ...

class StimulusGenerator:
    def __init__(self, config: StimulusConfig): ...
    def generate_prompts(self) -> List[str]: ...
    def generate_variants(self, prompt: str) -> List[StimulusPair]: ...
    def validate_length_match(self, pairs: List[StimulusPair]) -> bool: ...
    def validate_cross_contamination(self, pairs: List[StimulusPair]) -> Dict[str, float]: ...
    def generate_and_save(self, output_path: str) -> List[StimulusPair]: ...
    def load(self, path: str) -> List[StimulusPair]: ...
```

---

### RewardModels (`code/inference/reward_models.py`)

**Dependencies**: Config

```python
from abc import ABC, abstractmethod
from typing import List, Tuple
import torch

class BaseRewardModel(ABC):
    @abstractmethod
    def load(self, device: str, use_4bit: bool = False) -> None: ...
    @abstractmethod
    def score(self, prompt: str, response: str) -> float: ...
    def score_batch(self, pairs: List[Tuple[str, str]], batch_size: int = 16) -> List[float]: ...
    def normalize_scores(self, scores: List[float]) -> List[float]: ...

class ArmoRM(BaseRewardModel):
    model_id: str = "RLHFlow/ArmoRM-Llama3-8B-v0.1"
    def load(self, device: str, use_4bit: bool = False) -> None: ...
    def score(self, prompt: str, response: str) -> float: ...

class UltraRM(BaseRewardModel):
    model_id: str = "openbmb/UltraRM-13b"
    def load(self, device: str, use_4bit: bool = False) -> None: ...
    def score(self, prompt: str, response: str) -> float: ...

class StarlingRM(BaseRewardModel):
    model_id: str = "berkeley-nest/Starling-RM-7B-alpha"
    def load(self, device: str, use_4bit: bool = False) -> None: ...
    def score(self, prompt: str, response: str) -> float: ...

class PairRM(BaseRewardModel):
    model_id: str = "llm-blender/PairRM"
    def load(self, device: str, use_4bit: bool = False) -> None: ...
    def score(self, prompt: str, response: str) -> float: ...
    def score_pair(self, prompt: str, response_a: str, response_b: str) -> float: ...

def load_all_models(config: InferenceConfig) -> dict[str, BaseRewardModel]: ...
```

---

### Stats (`code/analysis/stats.py`)

**Dependencies**: none (scipy, numpy, pandas)

```python
import numpy as np
import pandas as pd
from typing import Tuple, Dict, List

def cohens_d(group1: np.ndarray, group2: np.ndarray) -> float: ...
def cohens_d_ci(d: float, n1: int, n2: int, alpha: float = 0.05) -> Tuple[float, float]: ...
def paired_ttest(group1: np.ndarray, group2: np.ndarray) -> Tuple[float, float]: ...
def pooled_effect_size(effect_sizes: List[float], ns: List[int]) -> Tuple[float, float]: ...
def heterogeneity_test(effect_sizes: List[float], ns: List[int]) -> Dict[str, float]: ...

def compute_per_rm_stats(scores_df: pd.DataFrame) -> pd.DataFrame:
    """Returns DataFrame with columns: rm, cohens_d, ci_low, ci_high, p_value, n"""
    ...

def compute_aggregate_stats(per_rm_df: pd.DataFrame) -> Dict: ...
def check_gate_condition(per_rm_df: pd.DataFrame, d_threshold: float = 0.3, min_models: int = 2) -> bool: ...
def export_results(per_rm_df: pd.DataFrame, agg: Dict, output_dir: str) -> None: ...
```

---

### Visualize (`code/analysis/visualize.py`)

**Dependencies**: Stats (for data shapes)

```python
import pandas as pd
import matplotlib.pyplot as plt
from typing import Optional

def plot_forest(per_rm_df: pd.DataFrame, output_dir: str) -> None:
    """FR-4.1: Per-RM effect size forest plot with 95% CI"""
    ...

def plot_violin(scores_df: pd.DataFrame, output_dir: str) -> None:
    """FR-4.2: Score distribution violin per RM (enumerated vs synthesized)"""
    ...

def plot_interaction(scores_df: pd.DataFrame, output_dir: str) -> None:
    """FR-4.3: Factorial interaction plot (Structure x Correctness x Completeness)"""
    ...

def plot_gate_metrics(per_rm_df: pd.DataFrame, gate_threshold: float, output_dir: str) -> None:
    """FR-4.4: Gate metrics comparison bar chart"""
    ...

def generate_all_figures(scores_df: pd.DataFrame, per_rm_df: pd.DataFrame,
                         gate_threshold: float, output_dir: str) -> None: ...
```

---

### run_experiment (`code/run_experiment.py`)

**Dependencies**: Config, StimulusGenerator, RewardModels, Stats, Visualize

```python
import argparse
from config import ExperimentConfig
from data.stimulus_generator import StimulusGenerator, StimulusPair
from inference.reward_models import load_all_models
from analysis.stats import compute_per_rm_stats, compute_aggregate_stats, check_gate_condition, export_results
from analysis.visualize import generate_all_figures

def run_stimulus_generation(cfg: ExperimentConfig) -> list[StimulusPair]: ...
def run_inference(stimuli: list[StimulusPair], cfg: ExperimentConfig) -> "pd.DataFrame": ...
def run_analysis(scores_df: "pd.DataFrame", cfg: ExperimentConfig) -> tuple: ...
def main(cfg: ExperimentConfig) -> None: ...

if __name__ == "__main__":
    ...
```

---

## Data Flow

- `run_experiment.py` calls StimulusGenerator -> saves `data/stimuli.json`
- loads all 4 RewardModels sequentially (one at a time to conserve VRAM)
- scores all 600 pairs per model -> accumulates to `scores_df`
- saves `data/raw_scores.json`
- Stats module computes per-RM Cohen's d, CI, t-test -> `data/effect_sizes.json`, `data/summary_stats.csv`
- Visualize module generates 4 figures -> `figures/`
- gate check printed to stdout + written to `04_validation.md`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Create file structure, config.py, requirements.txt | 5 | 1+1+1+2 |
| A-2 | Stimulus Generation | StimulusGenerator with LLM calls, EnumerationClassifier, length validation, cross-contamination check | 13 | 3+2+4+4 |
| A-3 | Multi-RM Inference | BaseRewardModel + 4 concrete adapters (ArmoRM, UltraRM, StarlingRM, PairRM), batching, score normalization | 15 | 4+3+4+4 |
| A-4 | Statistical Analysis | Cohen's d, CI, paired t-test, pooled effect, gate condition check, export | 10 | 2+2+4+2 |
| A-5 | Visualization Suite | 4 figures (forest, violin, interaction, gate), save PNG+PDF | 9 | 2+2+3+2 |
| A-6 | Pipeline Integration + Validation | run_experiment.py orchestration, checkpoint/resume, 04_validation.md report | 11 | 2+3+3+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3], Medium(9-13): [A-2, A-4, A-5, A-6], Low(4-8): [A-1]

---

## Notes

- Models are loaded sequentially (not simultaneously) to stay within VRAM budget. Each model is unloaded after scoring its batch.
- UltraRM-13b falls back to 4-bit quantization if VRAM < 16GB (controlled via `InferenceConfig.use_4bit`).
- PairRM pairwise mode: synthesized response treated as the comparison baseline for each enumerated response.
- Random seed 42 fixed throughout; all models run in `.eval()` mode with dropout disabled.
- Stimulus generation requires LLM API calls (75 prompts x 8 variants); Phase 4 must handle API key setup or use cached `stimuli.json`.
