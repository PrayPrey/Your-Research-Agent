# Experiment Design: h-m2

**Date:** 2026-08-09
**Author:** Anonymous
**Hypothesis Statement:** On low-entropy subset (H_L < 25th percentile), trajectory metrics achieve AUROC > 0.55 with 95% CI LB > 0.50
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Tests whether trajectory metrics provide incremental signal beyond entropy in confident-but-wrong cases.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-e1 (VALIDATED - Mean AUROC 0.5657)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-e1 (VALIDATED)

### Gate Condition
SHOULD_WORK: If fails, continue workflow but log limitation. Tests trajectory signal specifically in low-entropy (confident) cases where output entropy alone is uninformative.

---

## Continuation Context

Building on h-e1 validation: NTI demonstrated discriminative signal for hallucination detection (AUROC 0.5657 > 0.55 threshold). This hypothesis tests whether trajectory metrics work specifically on the "hard" subset - cases where the model is confident (low H_L) but wrong.

### Previous Hypothesis Results
- **h-e1 VALIDATED**: Mean AUROC 0.5657 > 0.55 threshold
- All 5 folds > 0.52 falsification boundary
- NTI metric demonstrates discriminative signal for hallucination detection
- Reusing: NTI extraction code, layer range 24-32, TruthfulQA MC1 dataset

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "trajectory instability hallucination detection AUROC"**
- Limited direct matches in KB
- Related: arxiv.org/abs/2402.19159 on LLM evaluation
- Key insight: AUROC is standard metric for binary detection tasks

**Query 2: "TruthfulQA LLM evaluation uncertainty"**
- Source: hf.co/papers/2305.14314
- Key insight: TruthfulQA standard for hallucination evaluation
- 817 questions, binary correctness labels

**Query 3: "low entropy subset evaluation bootstrap confidence interval"**
- Standard approach: Bootstrap resampling for CI estimation
- sklearn.metrics or scipy.stats for implementation

### Archon Code Examples

Limited directly relevant code examples in KB. Key pattern found:
- PyTorch standard installation verified
- Scaled dot-product attention reference for understanding transformer internals

### Exa GitHub Implementations

**Repository 1: khurramkhalil/GhostTrack** (High relevance)
- **URL**: https://github.com/khurramkhalil/GhostTrack
- **Relevance**: Trajectory tracking for hallucination detection on TruthfulQA
- **AUROC**: 98.5% (GPT-2-124M)
- **Key Insight**: "Tracking competition between hypotheses is key to detecting hallucinations"
- **Features Used**: entropy_std (11%), stability_mean (10.6%), dominance_mean (10.2%)
- **Architecture**: Sparse Autoencoders for semantic decomposition + multi-object tracking

**Repository 2: chang-sx/TraceDet** (High relevance)
- **URL**: https://github.com/chang-sx/TraceDet
- **Relevance**: Entropy-based hallucination detection via generation traces
- **Key Components**:
  - `step_entropy_ave.py` - Entropy analysis utility
  - `TimeHalu.py` - Temporal hallucination detection model
- **Pipeline**: Generate outputs → Extract entropy traces → Train detector
- **Evaluation**: TriviaQA, HotpotQA, CommonsenseQA

**Repository 3: radiolab-ntu/ars_icml2026** (Medium relevance)
- **URL**: https://github.com/radiolab-ntu/ars_icml2026
- **Relevance**: ICML 2026 paper on reasoning trajectories
- **TruthfulQA Performance**: CCS 66.85 → 86.64 with ARS shaping
- **Key Method**: Answer-agreement Representation Shaping

**Repository 4: Tuned Lens Library** (Tool reference)
- **URL**: https://tuned-lens.readthedocs.io/
- **Relevance**: Standard library for layer-wise hidden state analysis
- **Pretrained lenses**: GPT-2, Pythia, OPT, LLaMA-3-8B
- **Note**: LLaMA-2-7B may need fresh fitting

**Repository 5: koppula/TruthfulQA** (Dataset reference)
- **URL**: https://github.com/koppula/TruthfulQA
- **MC1 Task**: Given question + 4-5 choices, select correct answer
- **Metric**: Simple accuracy (log-probability based selection)

### 🎯 Implementation Priority Assessment

**CRITICAL: This is a continuation experiment building on h-e1 validated code**

**Implementation Hierarchy:**
1. **h-e1 validated code** - Reuse NTI extraction and evaluation pipeline
2. **GhostTrack entropy features** - entropy_std, stability patterns relevant
3. **Tuned Lens library** - For layer-wise analysis if needed

**Recommended Implementation Path:**
- Primary: Extend h-e1 code to filter low-entropy subset before evaluation
- Fallback: Reference GhostTrack entropy analysis patterns
- Justification: Controlled comparison requires same pipeline, only subset filtering changes

### Code Analysis (Serena MCP)

*Skipped* - Code from Exa search results was sufficiently clear. Key patterns:
- Bootstrap CI: scipy.stats.bootstrap or sklearn resample
- AUROC: sklearn.metrics.roc_auc_score
- Low-entropy filtering: np.percentile(H_L, 25)

---

## Experiment Specification

### Dataset

**Name**: TruthfulQA MC1 (Low-Entropy Subset)
**Type**: standard
**Source**: HuggingFace datasets (`truthful_qa`)
**Full Size**: 817 questions
**Subset Size**: ~204 samples (25th percentile of H_L)

**Subset Definition:**
- Compute H_L (mean output entropy over layers 24-32) for all 817 samples
- Filter to samples where H_L < 25th percentile (~204 samples)
- These represent "confident but potentially wrong" cases

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `truthful_qa`
- Code:
```python
from datasets import load_dataset
ds = load_dataset("truthful_qa", "multiple_choice")
# MC1 task: single correct answer selection
```

### Models

#### Baseline Model

**Architecture**: H_L-only classifier (entropy baseline)
**Description**: Logistic regression using only mean output entropy H_L
**Purpose**: Demonstrate that entropy alone fails on low-entropy subset

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `meta-llama/Llama-2-7b-hf`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
```

#### Proposed Model

**Architecture**: Baseline + Trajectory Metrics (NTI)
**Description**: Uses NTI computed from h-e1 validated pipeline on low-entropy subset

**Core Mechanism Implementation:**

```python
# Core Mechanism: Low-Entropy Subset Evaluation
# Based on: h-e1 validated NTI pipeline + GhostTrack entropy analysis

import numpy as np
from scipy import stats
from sklearn.metrics import roc_auc_score

def filter_low_entropy_subset(H_L_all, labels_all, nti_all, percentile=25):
    """
    Filter to low-entropy samples where H_L < 25th percentile.
    These are "confident" samples where entropy-based detection fails.
    
    Args:
        H_L_all: (N,) array of mean output entropy per sample
        labels_all: (N,) binary correctness labels
        nti_all: (N,) NTI scores from h-e1 pipeline
        percentile: cutoff percentile (default 25)
    
    Returns:
        Filtered arrays for low-entropy subset
    """
    threshold = np.percentile(H_L_all, percentile)
    mask = H_L_all < threshold
    return H_L_all[mask], labels_all[mask], nti_all[mask], mask

def compute_auroc_with_ci(scores, labels, n_bootstrap=1000, ci=0.95):
    """
    Compute AUROC with bootstrap confidence interval.
    
    Returns:
        auroc: point estimate
        ci_lower: lower bound of CI
        ci_upper: upper bound of CI
    """
    auroc = roc_auc_score(labels, scores)
    
    # Bootstrap CI
    bootstrap_aucs = []
    n = len(labels)
    for _ in range(n_bootstrap):
        idx = np.random.choice(n, n, replace=True)
        try:
            auc_i = roc_auc_score(labels[idx], scores[idx])
            bootstrap_aucs.append(auc_i)
        except ValueError:
            continue
    
    alpha = (1 - ci) / 2
    ci_lower = np.percentile(bootstrap_aucs, alpha * 100)
    ci_upper = np.percentile(bootstrap_aucs, (1 - alpha) * 100)
    
    return auroc, ci_lower, ci_upper

# Integration: Reuse h-e1 NTI extraction, apply to low-entropy subset
```

### Training Protocol

**Note**: This is an evaluation-only experiment (no training required)

**Procedure:**
1. Load h-e1 computed features (H_L, NTI, labels) for all 817 samples
2. Filter to low-entropy subset (H_L < 25th percentile)
3. Compute AUROC of NTI on filtered subset
4. Compute bootstrap 95% CI

**Computational Requirements:**
- No GPU training required
- Bootstrap: 1000 iterations
- Single seed: 42

### Evaluation

**Primary Metrics:**
- AUROC on low-entropy subset
- 95% confidence interval (bootstrap, 1000 iterations)

**Success Criteria:**
- AUROC > 0.55 on low-entropy subset
- 95% CI lower bound > 0.50

**Falsification Criteria:**
- 95% CI includes 0.50 (cannot reject random chance)

**Expected Performance (from h-e1):**
- Full dataset AUROC: 0.5657
- Low-entropy subset: Potentially lower but still > 0.55

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary classification (hallucination detection)
- Library: sklearn.metrics, scipy.stats
- Code:
```python
from sklearn.metrics import roc_auc_score
import numpy as np

def bootstrap_auroc(y_true, y_score, n_bootstrap=1000):
    aucs = []
    for _ in range(n_bootstrap):
        idx = np.random.choice(len(y_true), len(y_true), replace=True)
        aucs.append(roc_auc_score(y_true[idx], y_score[idx]))
    return np.mean(aucs), np.percentile(aucs, [2.5, 97.5])
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing:
  - Target AUROC threshold (0.55)
  - Actual AUROC on low-entropy subset
  - 95% CI error bars
  - Horizontal line at 0.50 (chance level)

#### Additional Figures (LLM Autonomous)
- Distribution of H_L values with 25th percentile cutoff marked
- ROC curve for low-entropy subset
- Comparison: full dataset vs low-entropy subset AUROC

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Low-entropy subset correctly identified (~204 samples)
3. AUROC > 0.55 on low-entropy subset
4. 95% CI lower bound > 0.50

**Mechanism Verification:**
- Pre-condition: h-e1 features (H_L, NTI) available for all samples
- Activation indicator: Low-entropy mask correctly filters ~25% of samples
- Success metric: AUROC with CI on filtered subset

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1**: TruthfulQA Evaluation Paper
- **Type**: Knowledge base article
- **Query Used**: "TruthfulQA LLM evaluation uncertainty"
- **Relevance**: Dataset characteristics, evaluation methodology
- **Used For**: Dataset specification, metrics

### B. GitHub Implementations (Exa)

**Repository 1**: khurramkhalil/GhostTrack
- **URL**: https://github.com/khurramkhalil/GhostTrack
- **Query Used**: "LLM hallucination detection trajectory entropy AUROC TruthfulQA PyTorch"
- **Relevance**: Trajectory-based hallucination detection, entropy features
- **Key Insight**: entropy_std and stability metrics important for detection
- **Used For**: Feature design validation, expected performance reference

**Repository 2**: chang-sx/TraceDet
- **URL**: https://github.com/chang-sx/TraceDet
- **Query Used**: "LLM hallucination detection trajectory entropy AUROC TruthfulQA PyTorch"
- **Relevance**: Entropy trace analysis for hallucination detection
- **Used For**: Pipeline architecture reference

**Repository 3**: koppula/TruthfulQA
- **URL**: https://github.com/koppula/TruthfulQA
- **Query Used**: (from Exa results)
- **Relevance**: Official TruthfulQA benchmark implementation
- **Used For**: Dataset loading, MC1 task definition

**Repository 4**: tuned-lens documentation
- **URL**: https://tuned-lens.readthedocs.io/
- **Query Used**: "logit lens tuned lens hidden state analysis LLaMA"
- **Relevance**: Layer-wise hidden state analysis methodology
- **Used For**: Understanding trajectory extraction approach

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear.
Bootstrap CI and AUROC computation patterns well-established in sklearn/scipy.

### D. Previous Hypothesis Context

**Source**: h-e1 Validation Results
- **Status**: VALIDATED (Mean AUROC 0.5657)
- **Reused Components**:
  - NTI extraction pipeline
  - TruthfulQA MC1 dataset loading
  - LLaMA-2-7B model configuration
  - Layers 24-32 for analysis
- **Why Reused**: Enables controlled experiment - only subset filtering changes

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (TruthfulQA MC1) | Previous + GitHub | h-e1, koppula/TruthfulQA |
| Low-entropy filtering | Research design | 02b_verification_plan.md |
| NTI extraction | Previous hypothesis | h-e1 validated code |
| Bootstrap CI | Standard practice | sklearn, scipy docs |
| AUROC computation | Standard practice | sklearn.metrics |
| Success criteria | Phase 2B | 02b_verification_plan.md |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-09

### Workflow History for This Hypothesis
- Phase 2C experiment design started: 2026-08-09
- MCP searches completed: Archon (3 queries), Exa (2 queries)
- Serena analysis: Skipped (code clear)
- Experiment specification synthesized

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
