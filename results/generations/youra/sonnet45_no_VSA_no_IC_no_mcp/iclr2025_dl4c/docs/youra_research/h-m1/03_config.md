# Configuration Specification: h-m1

**Date:** 2026-08-25
**Hypothesis:** h-m1 (MECHANISM)
**Type:** PoC - Minimal config for mechanism validation

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Extends h-e1 infrastructure (config verified from base code)
**Config Files Found:** h-e1/03_config.md
**Pattern Used:** Python dataclass (inherited from h-e1)

---

## Inherited Configuration (Base Hypothesis)

The following configs are reused from h-e1 (verified from actual implementation):

```python
# From: h-e1 ExperimentConfig (REUSED)
model_name: str = "Salesforce/codegen-350M-mono"  # Changed from 16B for faster inference
temperature: float = 0.8
max_tokens: int = 512
batch_size: int = 8
random_seed: int = 42
timeout_seconds: float = 5.0
reward_model: str = "gpt-3.5-turbo"
bootstrap_iterations: int = 1000
alpha: float = 0.05
```

**Change from h-e1:** Using 350M instead of 16B model (faster inference, same architecture family).

---

## Configuration Schema

Single dataclass extending h-e1 config. No hyperparameter grid for PoC mechanism validation.

```python
"""Configuration for h-m1 disagreement analysis experiment."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

@dataclass
class DisagreementAnalysisConfig:
    """PoC configuration for specification completeness mechanism validation."""
    
    # Experiment metadata
    hypothesis_id: str = "h-m1"
    random_seed: int = 42
    
    # Dataset configuration
    humaneval_sample_size: int = 50  # Reuse from h-e1
    mbpp_sample_size: int = 50       # Reuse from h-e1
    swebench_sample_size: int = 100  # New data
    swebench_source: str = "princeton-nlp/SWE-bench_Lite"
    swebench_split: str = "test"
    
    # Code generation (reuse h-e1 settings)
    model_name: str = "Salesforce/codegen-350M-mono"
    temperature: float = 0.8
    top_p: float = 0.95
    max_tokens: int = 512
    batch_size: int = 8
    
    # Execution feedback
    timeout_seconds: float = 5.0
    swebench_timeout_seconds: float = 300.0  # Repo tests take longer
    
    # AI feedback
    reward_model: str = "gpt-3.5-turbo"
    
    # Human feedback (simulated for PoC)
    human_rating_scale: int = 5
    noise_level: float = 0.2
    
    # Disagreement extraction
    disagreement_threshold: float = 3.0  # 5-point scale midpoint
    min_disagreements_per_dataset: int = 10
    
    # Qualitative coding
    intent_dimensions: List[str] = field(default_factory=lambda: [
        "correctness",
        "edge_cases",
        "readability",
        "efficiency",
        "maintainability",
        "security"
    ])
    
    # Statistical analysis
    bootstrap_iterations: int = 1000
    alpha: float = 0.05
    
    # Gate thresholds
    min_effect_size: float = 2.0  # SWE-bench / HumanEval ratio
    max_pvalue: float = 0.05
    
    # Paths (absolute)
    base_dir: Path = field(default_factory=lambda: Path("/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_dl4c/docs/youra_research/h-m1"))
    h_e1_dir: Path = field(default_factory=lambda: Path("/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_dl4c/docs/youra_research/h-e1"))
    
    # Visualization
    figure_dpi: int = 300
    figure_format: List[str] = field(default_factory=lambda: ["png", "pdf"])
    
    def __post_init__(self):
        """Initialize derived paths."""
        self.output_dir = self.base_dir / "outputs"
        self.figures_dir = self.base_dir / "figures"
        self.cache_dir = self.base_dir / "cache"
        self.h_e1_outputs = self.h_e1_dir / "outputs"
        
        for d in [self.output_dir, self.figures_dir, self.cache_dir]:
            d.mkdir(exist_ok=True, parents=True)
```

---

## Non-Standard Value Rationale

**swebench_timeout_seconds = 300.0**: Repo-level tests require Docker container setup and multi-file test execution. Standard 5s timeout used for HumanEval/MBPP would cause false failures.

**disagreement_threshold = 3.0**: Midpoint of 5-point scale (1-5). Exec PASS + human <3 OR exec FAIL + human >3 indicates clear disagreement. Lower threshold (2.5) captures noise; higher (3.5) misses valid cases.

**min_effect_size = 2.0**: Mechanism hypothesis requires SWE-bench (underspecified) to show 2× missed dimension rate vs HumanEval (fully specified). Smaller effect (1.5×) could be noise; larger (3×) is overly strict for PoC.

---

## Compute Requirements

- **GPU:** 1x NVIDIA A100 40GB
- **RAM:** 64GB
- **Storage:** 10GB (5GB SWE-bench repos + 2GB patches + 3GB cache)
- **Runtime:** 4-6 hours
  - SWE-bench generation: 2h (100 samples × ~1min/sample)
  - Feedback collection: 1h
  - Qualitative coding: 2-3h (manual)

---

## File Outputs

```
docs/youra_research/h-m1/
├── outputs/
│   ├── swebench_samples.jsonl           # 100 generated patches
│   ├── unified_feedback.json            # 200 samples (50+50 reused, 100 new)
│   ├── disagreement_cases.json          # Extracted disagreements
│   ├── coded_results.json               # Manual coding results
│   └── statistical_results.json         # Chi-square, effect size, CI
├── figures/
│   ├── missed_dimensions_by_task.png/pdf
│   ├── disagreement_types.png/pdf
│   ├── intent_dimension_heatmap.png/pdf
│   └── qualitative_examples.png/pdf
└── cache/
    ├── codegen_350m_mono/               # Model weights
    └── swebench_repos/                  # Cloned repositories
```

---

## Reproducibility

All randomness controlled by seeds:
- Dataset sampling: `random_seed=42`
- SWE-bench selection: `shuffle(seed=42).select(range(100))`
- Human simulation: `random_seed=42`
- Bootstrap CI: `np.random.seed(42)`

Pinned versions:
- Model: `Salesforce/codegen-350M-mono` (HuggingFace checkpoint)
- Datasets: `princeton-nlp/SWE-bench_Lite` (HuggingFace dataset)
- h-e1 data: Snapshot from `h-e1/outputs/` (immutable)

---

## Environment Variables

```bash
# Required for OpenAI API (reward model)
export OPENAI_API_KEY="sk-..."

# Optional: Docker for SWE-bench harness
# docker pull princeton-nlp/swe-bench:latest
```

---

**Self-Validation:**
- [x] ONE format only (dataclass)
- [x] No ASCII diagrams
- [x] No KB search logs
- [x] Rationale only for non-standard values (3 params)
- [x] Total length < 400 lines (168 lines)
- [x] Codebase Analysis section included
- [x] Base hypothesis verification (h-e1 config checked)
- [x] PoC mode: no variations, no ablations
