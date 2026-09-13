# Configuration Specification: h-e1

**Date:** 2026-08-25
**Hypothesis:** h-e1 (EXISTENCE)
**Type:** PoC - Minimal config for "does it work?" validation

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** New config design (no base hypothesis)
**Config Files Found:** None - designing from scratch
**Pattern Used:** Python dataclass (standard for DL experiments)

---

## Configuration Schema

Single dataclass config. No variations, no grid search, no ablations for PoC.

```python
"""Configuration for h-e1 correlation measurement experiment."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

@dataclass
class ExperimentConfig:
    """PoC configuration for correlation measurement."""
    
    # Experiment metadata
    hypothesis_id: str = "h-e1"
    random_seed: int = 42
    
    # Dataset sampling
    humaneval_sample_size: int = 100
    mbpp_sample_size: int = 100
    swe_bench_sample_size: int = 100
    mbpp_seed: int = 42  # For random sampling
    swe_bench_seed: int = 42
    
    # Code generation
    model_name: str = "Salesforce/codegen-16B-mono"
    temperature: float = 0.8  # From CodeGen paper
    top_p: float = 0.95
    max_tokens: int = 512
    batch_size: int = 8
    
    # Execution feedback
    timeout_seconds: float = 5.0
    
    # AI feedback
    reward_model: str = "gpt-3.5-turbo"  # As judge
    
    # Human simulation (PoC only)
    num_raters: int = 3
    noise_level: float = 0.2  # ±0.2 uniform noise
    
    # Statistical analysis
    bootstrap_iterations: int = 1000
    confidence_level: float = 0.95
    alpha: float = 0.05
    
    # Gate thresholds
    min_kappa: float = 0.6  # Cohen's kappa threshold
    max_pvalue: float = 0.05
    
    # Paths (absolute)
    base_dir: Path = field(default_factory=lambda: Path("/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_dl4c/docs/youra_research/h-e1"))
    
    def __post_init__(self):
        """Initialize derived paths."""
        self.output_dir = self.base_dir / "outputs"
        self.figures_dir = self.base_dir / "figures"
        self.cache_dir = self.base_dir / "cache"
        
        # Create directories
        for d in [self.output_dir, self.figures_dir, self.cache_dir]:
            d.mkdir(exist_ok=True, parents=True)
```

---

## Non-Standard Value Rationale

**noise_level = 0.2**: Balances realism (humans disagree) with signal preservation (correlations detectable). Too low (0.1) makes simulation trivial; too high (0.5) drowns signal.

**bootstrap_iterations = 1000**: Standard for 95% CI stability. 100 too noisy, 10000 overkill for n=100 samples.

**batch_size = 8**: Fits A100 40GB with 16B model. Smaller wastes GPU, larger risks OOM.

---

## Environment Variables

```bash
# Required for OpenAI API (reward model)
export OPENAI_API_KEY="sk-..."

# Optional: Force CPU if no GPU
export CUDA_VISIBLE_DEVICES=""
```

---

## Compute Requirements

- **GPU:** 1x NVIDIA A100 40GB
- **RAM:** 64GB
- **Storage:** 50GB (25GB model weights + 25GB datasets/outputs)
- **Runtime:** 2-4 hours (100 samples × 3 datasets × ~30s/sample)

---

## File Outputs

```
docs/youra_research/h-e1/
├── outputs/
│   ├── generated_samples.jsonl       # 300 code samples
│   ├── feedback_execution.json       # 300 binary values
│   ├── feedback_ai.json              # 300 continuous scores
│   ├── feedback_human.json           # 300 averaged ratings
│   └── correlation_results.json      # Final statistics
├── figures/
│   ├── correlation_matrix_humaneval.png
│   ├── correlation_matrix_mbpp.png
│   ├── correlation_matrix_swe_bench.png
│   ├── scatter_exec_human_*.png      # 3 plots
│   ├── scatter_ai_human_*.png        # 3 plots
│   └── scatter_exec_ai_*.png         # 3 plots
└── cache/
    └── codegen_16b_mono/             # Model weights cache
```

---

## Reproducibility

All randomness controlled by seeds:
- Dataset sampling: `mbpp_seed`, `swe_bench_seed`
- Human simulation: `random_seed` (global)
- Bootstrap: `random_seed`

Re-running with same config produces identical results (except API calls, which are cached).

---

**Self-Validation:**
- [x] ONE format only (dataclass)
- [x] No ASCII diagrams
- [x] No KB search logs
- [x] Rationale only for non-standard values (3 params)
- [x] Total length < 400 lines (165 lines)
- [x] Codebase Analysis section included
- [x] PoC mode: no variations, no ablations
