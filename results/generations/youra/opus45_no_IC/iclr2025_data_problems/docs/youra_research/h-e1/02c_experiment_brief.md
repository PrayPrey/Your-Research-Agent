# Experiment Design: H-E1

**Date:** 2026-08-10
**Author:** Anonymous
**Hypothesis Statement:** A statistically significant positive correlation (Spearman r > 0.2) exists between cumulative 13-gram benchmark overlap percentage and benchmark score inflation residual across Pythia model checkpoints.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites)
**Gate Status:** MUST_WORK - foundation hypothesis

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
**Gate Type:** MUST_WORK
- If fails: ABANDON entire transfer function approach (no correlation means no transfer function possible)
- Success threshold: Spearman r > 0.2 with p < 0.05 (minimum), r > 0.5 (primary target)

---

## Continuation Context

**First hypothesis in sequence** - No previous context to inherit.

### Previous Hypothesis Results (if applicable)
N/A - This is the foundation hypothesis (H-E1).

---

## Implementation Research Summary

### Archon Knowledge Base Findings

No direct contamination-related results from Archon KB search. General PyTorch/HuggingFace patterns available.

### Archon Code Examples

N/A - Archon KB does not contain specific contamination detection code.

### Exa GitHub Implementations

**Key Findings:**

1. **lm-evaluation-harness Decontamination Module** (EleutherAI)
   - Source: `github.com/EleutherAI/lm-evaluation-harness/blob/main/docs/decontamination.md`
   - 13-gram overlap detection based on GPT-3 Appendix C methodology
   - Implementation: `lm_eval/decontaminate.py` + `lm_eval/decontamination/`
   - Process: Build n-gram dictionaries → scan training set → mark contaminated docs

2. **Pythia Checkpoints** (EleutherAI)
   - Source: `github.com/eleutherai/pythia`
   - 154 checkpoints per model (steps 0,1,2,4,8,16,32,64,128,256,512,1000,then every 1000)
   - 16 models total (70M to 12B), trained on The Pile in same order
   - Evaluation via lm-eval-harness with revision flag: `--model_args pretrained=EleutherAI/pythia-160m,revision=step100000`

3. **lm-checkpoints Library**
   - Source: `pypi.org/project/lm-checkpoints/`
   - Python wrapper for iterating Pythia checkpoints
   - Built-in lm-eval integration: `evaluate(ckpts, tasks=[...], output_dir="results")`

4. **Contamination Detection Papers**
   - Deng et al. 2024: Retrieval-based overlap detection + TS-Guessing
   - Singh et al. 2024: "When does contamination matter?" analysis
   - Fu et al. 2025: Survey of MIA-based detection methods

### 🎯 Implementation Priority Assessment

**CRITICAL: For contamination correlation study, use official EleutherAI tools**

**Recommended Implementation Path:**
- Primary: lm-evaluation-harness + lm-checkpoints for evaluation
- Fallback: Direct HuggingFace model loading with custom evaluation loop
- Justification: lm-eval-harness is the standard evaluation framework used in Pythia paper; built-in decontamination support; checkpoint versioning via revision flag

### Code Analysis (Serena MCP)

Not applicable - This experiment uses analysis pipeline, not model architecture modification. No codebase to analyze with Serena.

---

## Experiment Specification

### Dataset

**Benchmarks (Evaluation Targets):**
| Benchmark | Samples | Type | Source |
|-----------|---------|------|--------|
| MMLU | ~14,042 | Multiple choice QA | HuggingFace `cais/mmlu` |
| ARC-Challenge | 1,172 | Multiple choice QA | HuggingFace `allenai/ai2_arc` |
| HellaSwag | 10,042 | Sentence completion | HuggingFace `Rowan/hellaswag` |
| WinoGrande | 1,267 | Coreference | HuggingFace `allenai/winogrande` |

**Total evaluation samples:** ~26,500 (full standard test sets)

**Training Corpus (Contamination Source):**
- **Name:** The Pile
- **Type:** standard
- **Source:** EleutherAI
- **Size:** 825GB text
- **N-gram Index:** Pre-computed 13-gram index from lm-eval-harness scripts

**OOD Capability Measure:**
- **Name:** WikiText-103
- **Type:** standard
- **Source:** HuggingFace `wikitext`
- **Purpose:** Perplexity for capability detrending (separate from The Pile)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Datasets + lm-eval-harness tasks
- Identifier: `lm_eval --tasks mmlu,arc_challenge,hellaswag,winogrande,wikitext`
- Code:
```python
# Benchmarks via lm-eval-harness
from lm_eval import evaluator
results = evaluator.simple_evaluate(
    model="hf",
    model_args=f"pretrained=EleutherAI/pythia-{size},revision=step{step}",
    tasks=["mmlu", "arc_challenge", "hellaswag", "winogrande", "wikitext"],
    batch_size="auto"
)

# Or via lm-checkpoints
from lm_checkpoints import evaluate, PythiaCheckpoints
ckpts = PythiaCheckpoints(size=[410, 1000, 1400, 2800, 6900, 12000], 
                          step=[0, 1000, 2000, ..., 143000])
evaluate(ckpts, tasks=["mmlu", "arc_challenge", "hellaswag", "winogrande"])
```

### Models

#### Baseline Model

**Architecture:** Pythia Model Family (EleutherAI)
**Sizes:** 410M, 1B, 1.4B, 2.8B, 6.9B, 12B
**Checkpoints per size:** 12 key checkpoints (steps 0, 1000, 2000, ..., 143000)
**Total data points:** 72 (6 sizes × 12 checkpoints)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `EleutherAI/pythia-{size}` with revision
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "EleutherAI/pythia-410m",
    revision="step100000",  # specific checkpoint
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("EleutherAI/pythia-410m")
```

#### Proposed Model

**Architecture:** N/A - This is a correlation analysis experiment, not a model modification experiment.

**Core Mechanism Implementation:**

This experiment measures correlation between contamination and performance, not model architecture changes.

```python
# Core Analysis Pipeline (NOT a model, but analysis code)
# Based on: GPT-3 Appendix C (13-gram decontamination), lm-eval-harness

import numpy as np
from scipy.stats import spearmanr
from collections import defaultdict

def compute_contamination_correlation(checkpoints_data):
    """
    Compute Spearman correlation between contamination and inflation.
    
    Args:
        checkpoints_data: List of dicts with keys:
            - step: training step
            - size: model size
            - contamination_pct: 13-gram overlap percentage
            - benchmark_score: raw benchmark accuracy
            - wikitext_ppl: WikiText-103 perplexity
    
    Returns:
        (spearman_r, p_value, inflation_residuals)
    """
    # Step 1: Fit capability regression (score ~ log(1/perplexity))
    capability = np.log(1 / np.array([d['wikitext_ppl'] for d in checkpoints_data]))
    scores = np.array([d['benchmark_score'] for d in checkpoints_data])
    
    # Linear regression for expected score given capability
    coeffs = np.polyfit(capability, scores, deg=1)
    expected_scores = np.polyval(coeffs, capability)
    
    # Step 2: Compute inflation residuals
    inflation_residuals = scores - expected_scores
    
    # Step 3: Spearman correlation with contamination
    contamination = np.array([d['contamination_pct'] for d in checkpoints_data])
    r, p = spearmanr(contamination, inflation_residuals)
    
    return r, p, inflation_residuals

# Integration: Run after lm-eval-harness evaluation completes
```

### Training Protocol

**N/A - This is an analysis experiment, not a training experiment.**

The Pythia models are pre-trained. This experiment:
1. Loads existing checkpoints (no training)
2. Evaluates on benchmarks (inference only)
3. Computes contamination overlap (n-gram matching)
4. Analyzes correlation (statistics)

**Compute Requirements:**
- Evaluation: ~2 GPU-hours per checkpoint × 72 checkpoints = ~144 GPU-hours
- N-gram extraction: ~48 CPU-hours (one-time)
- Correlation analysis: <1 minute (CPU)

**Seeds:** 1 (deterministic evaluation, no training randomness)

### Evaluation

**Primary Metrics:**
- **Spearman r:** Correlation coefficient between contamination % and inflation residual
- **p-value:** Statistical significance of correlation

**Success Criteria (PoC):**
- proposed_metric > baseline_metric equivalent: **r > 0.2 with p < 0.05**
- Primary target: r > 0.5 (strong correlation)

**Expected Baseline Performance** (from research):
- Prior work (Yang et al. 2023): 8-18% overlap in RedPajama
- Expected: Positive correlation exists but magnitude unknown
- Source: Phase 2B verification plan

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: correlation analysis
- Library: scipy.stats
- Code:
```python
from scipy.stats import spearmanr
r, p = spearmanr(contamination_percentages, inflation_residuals)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Scatter plot of contamination % vs inflation residual with regression line and r/p values

#### Additional Figures (LLM Autonomous)

1. **Contamination by Benchmark:** Bar chart showing 13-gram overlap % for each benchmark (MMLU, ARC, HellaSwag, WinoGrande)
2. **Checkpoint Trajectory:** Line plot of benchmark scores across training steps, colored by model size
3. **Capability Detrending:** Scatter of WikiText-103 perplexity vs benchmark score with regression line
4. **Residual Distribution:** Histogram of inflation residuals with mean and CI

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (all 72 checkpoints evaluated)
2. Spearman r > 0.2 AND p < 0.05 (correlation exists)

---

## Appendix: Reference Implementations

### Primary References

1. **lm-evaluation-harness Decontamination**
   - URL: https://github.com/EleutherAI/lm-evaluation-harness/blob/main/docs/decontamination.md
   - Purpose: 13-gram contamination detection methodology
   - Key code: `lm_eval/decontaminate.py`

2. **Pythia: A Suite for Analyzing Large Language Models**
   - URL: https://github.com/EleutherAI/pythia
   - Paper: Biderman et al. 2023 (ICML)
   - Purpose: Model checkpoints and training data reconstruction

3. **lm-checkpoints Library**
   - URL: https://pypi.org/project/lm-checkpoints/
   - Purpose: Checkpoint iteration and evaluation automation

4. **GPT-3 Appendix C (Contamination)**
   - Reference: Brown et al. 2020, "Language Models are Few-Shot Learners"
   - Purpose: Original 13-gram decontamination methodology (N=8-13)

### Related Papers

5. **Yang et al. 2023**: RedPajama overlap analysis (8-18% found)
6. **Deng et al. 2024**: "Investigating Data Contamination in Modern Benchmarks" - retrieval + TS-Guessing
7. **Singh et al. 2024**: "When does evaluation data contamination matter?"
8. **Oren et al. 2024**: Verbatim completion on contaminated data

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-10

### Workflow History for This Hypothesis
- 2026-08-10: Hypothesis h-e1 set to IN_PROGRESS (Phase 2C start)
- 2026-08-10: Experiment design completed (Phase 2C)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
