# Experiment Design: H-E1

**Date:** 2026-08-12
**Author:** Anonymous
**Hypothesis Statement:** Onset delay d_i differs systematically between minority and majority group samples
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites)
**Gate Status:** MUST_WORK - Pending verification

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
**Type:** MUST_WORK  
**Criteria:** Precision > 0.5 AND Recall > 0.3 for minority detection  
**Failure Action:** ABANDON entire hypothesis

---

## Continuation Context

This is the foundation hypothesis (H-E1) with no prior hypotheses to build upon.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis in verification chain.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct matches in KB. Found general training loop patterns from diffusers examples but no specific per-sample loss tracking implementations.

### Archon Code Examples

No directly relevant code examples for per-sample loss tracking or spurious correlation detection in indexed sources.

### Exa GitHub Implementations

**Primary Sources Found:**

1. **JTT (Just Train Twice)** - https://github.com/anniesch/jtt
   - Official implementation from Liu et al. (ICML 2021)
   - Waterbirds dataset handling with metadata.csv
   - ERM training with per-epoch loss tracking
   - ResNet-50 architecture, SGD optimizer
   - Key insight: T=50 epochs for identification, upweight factor λ=50-100

2. **SPARE** - https://github.com/BigML-CS-UCLA/SPARE
   - Yang et al. (AISTATS 2024)
   - Identifies spurious biases early in training via simplicity bias
   - Importance sampling for minority group balancing
   - Up to 12x faster than JTT with 21.1% WGA improvement

3. **Group DRO** - https://github.com/kohpangwei/group_DRO
   - Sagawa et al. baseline implementation
   - Waterbirds dataset download: https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz
   - LossComputer class for per-group loss tracking
   - ResNet-50, SGD momentum=0.9, 300 epochs

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Source | Rationale |
|----------|--------|-----------|
| 1 | kohpangwei/group_DRO | Official Waterbirds dataset + ERM baseline |
| 2 | anniesch/jtt | Per-sample loss tracking methodology |
| 3 | BigML-CS-UCLA/SPARE | Simplicity bias detection (theory support) |

**Recommended Implementation Path:**
- Primary: Adapt kohpangwei/group_DRO for per-sample loss logging + onset delay computation
- Fallback: Custom PyTorch training loop based on JTT patterns
- Justification: group_DRO provides canonical Waterbirds handling; JTT demonstrates per-sample identification; our contribution is onset delay d_i metric

### Code Analysis (Serena MCP)

*Serena analysis skipped - no local codebase to analyze for this new experiment.*

Relevant patterns from Exa search:
- `LossComputer` class tracks per-group losses
- Per-sample loss stored in CSV during training
- Waterbirds metadata.csv contains group labels (y, place, split)

---

## Experiment Specification

### Dataset

**Name:** Waterbirds
**Type:** standard
**Source:** https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz (Sagawa et al., 2019)

| Split | Size | Purpose |
|-------|------|---------|
| Train | 4,795 | ERM training with per-sample loss logging |
| Val | 1,199 | Balanced groups for threshold tuning |
| Test | 5,794 | Final evaluation |

**Group Structure:**
- Majority: landbird+land (3,498), waterbird+water (1,057)
- Minority: waterbird+land (56), landbird+water (184)
- Spurious correlation: 95%

**Preprocessing:**
- Resize to 224×224
- Normalize: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
- No augmentation (follow group_DRO baseline)

**Loading Information** (for Phase 4 download):
- Method: Direct download + custom Dataset class
- Identifier: waterbird_complete95_forest2water2
- Code:
```python
# Download
wget https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz
tar -xzf waterbird_complete95_forest2water2.tar.gz

# Load with group_DRO style
from data.cub_dataset import CUBDataset
dataset = CUBDataset(root_dir='./data', target_name='waterbird_complete95', 
                     confounder_names=['forest2water2'], model_type='resnet50')
```

### Models

#### Baseline Model

**Architecture:** ResNet-18 (pretrained on ImageNet)
**Configuration:**
- Input: 224×224×3
- Output: 2 classes (waterbird/landbird)
- Final layer: nn.Linear(512, 2)

**Rationale:** ResNet-18 is standard for Waterbirds benchmarks (Phase 2B specification); lighter than ResNet-50 for PoC.

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: resnet18
- Code:
```python
import torchvision.models as models
model = models.resnet18(pretrained=True)
model.fc = nn.Linear(512, 2)  # Waterbirds: 2 classes
```

#### Proposed Model

**Architecture:** ResNet-18 + Per-Sample Loss Tracking + Onset Delay Computation

This is NOT a model modification but an analysis framework. The "proposed" approach adds:
1. Per-sample loss logging every epoch
2. Onset delay d_i computation
3. Minority detection via thresholding

**Core Mechanism Implementation:**

```python
# Core Mechanism: Onset Delay Detection for Minority Identification
# Based on: JTT (Liu et al., 2021), SPARE (Yang et al., 2024)

class OnsetDelayTracker:
    """
    Track per-sample loss and compute onset delay d_i.
    d_i = min{epoch t : L_i(t) < 0.9 * L_i(0)}
    """
    def __init__(self, n_samples, threshold=0.9):
        self.n_samples = n_samples
        self.threshold = threshold  # 10% loss reduction
        self.initial_loss = None    # L_i(0) for each sample
        self.onset_epoch = np.full(n_samples, np.inf)  # d_i
        
    def update(self, epoch, sample_indices, losses):
        """Called after each batch with per-sample losses."""
        if epoch == 0:
            # Record initial losses
            self.initial_loss[sample_indices] = losses
        else:
            # Check onset condition: L_i(t) < 0.9 * L_i(0)
            threshold_losses = self.threshold * self.initial_loss[sample_indices]
            onset_mask = (losses < threshold_losses) & (self.onset_epoch[sample_indices] == np.inf)
            self.onset_epoch[sample_indices[onset_mask]] = epoch
    
    def predict_minority(self, T_early=20):
        """Predict minority samples: high onset delay at T_early."""
        return self.onset_epoch > T_early

# Integration: Wrap standard ERM training loop
# Log per-sample losses; compute d_i at T_early; evaluate precision/recall
```

### Training Protocol

**Optimizer:** SGD
- momentum: 0.9
- weight_decay: 1e-4
- Source: kohpangwei/group_DRO, anniesch/jtt

**Learning Rate:** 1e-3
- Source: group_DRO Waterbirds config

**Schedule:** None (constant LR for PoC)

**Batch Size:** 64
- Source: JTT Waterbirds experiments

**Epochs:** 100
- T_early = 20 (onset delay detection cutoff)
- Source: Phase 2B specification

**Loss Function:** CrossEntropyLoss (per-sample, unreduced)
```python
criterion = nn.CrossEntropyLoss(reduction='none')  # Per-sample losses
```

**Seeds:** 1 (fixed for PoC)

> ⚠️ **EXISTENCE (PoC)**: Single run sufficient. No multiple seeds.

### Evaluation

**Primary Metrics:**
- Precision@T_early: Fraction of samples with d_i > T_early that are truly minority
- Recall@T_early: Fraction of minority samples detected by d_i > T_early

**Success Criteria (PoC):**
- Precision > 0.5 AND Recall > 0.3
- Mann-Whitney U test p < 0.05 (minority d_i > majority d_i)

**Expected Baseline Performance** (from research):
- JTT achieves ~60% precision in identifying minority samples
- Source: Liu et al. (2021) Table 1

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary_classification (minority detection)
- Library: sklearn.metrics
- Code:
```python
from sklearn.metrics import precision_score, recall_score
from scipy.stats import mannwhitneyu

# Minority detection metrics
precision = precision_score(y_true=is_minority, y_pred=predicted_minority)
recall = recall_score(y_true=is_minority, y_pred=predicted_minority)

# Distribution test
stat, pvalue = mannwhitneyu(d_i_minority, d_i_majority, alternative='greater')
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Precision/Recall bar chart vs thresholds (0.5/0.3)

#### Additional Figures (LLM Autonomous)

1. **Onset Delay Distribution**: Histogram of d_i for minority vs majority groups (overlaid)
2. **d_i vs Group Membership**: Scatter plot with group labels colored
3. **Loss Trajectories**: Sample of 20 trajectories colored by group (10 minority, 10 majority)
4. **Precision-Recall Curve**: As T_early varies from 1 to 50

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### Primary References

1. **kohpangwei/group_DRO** (Sagawa et al., 2019)
   - URL: https://github.com/kohpangwei/group_DRO
   - Purpose: Waterbirds dataset, ERM baseline, LossComputer
   - Key files: `train.py`, `data/cub_dataset.py`, `loss.py`

2. **anniesch/jtt** (Liu et al., ICML 2021)
   - URL: https://github.com/anniesch/jtt
   - Purpose: Per-sample misclassification tracking, error set identification
   - Key files: `generate_downstream.py`, `process_training.py`
   - Paper: https://arxiv.org/pdf/2107.09044

3. **BigML-CS-UCLA/SPARE** (Yang et al., AISTATS 2024)
   - URL: https://github.com/BigML-CS-UCLA/SPARE
   - Purpose: Early simplicity bias detection theory
   - Paper: https://proceedings.mlr.press/v238/yang24c.html

### Waterbirds Dataset

- Download: https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz
- Alternative: WILDS package (`wilds.get_dataset("waterbirds")`)
- Metadata: `metadata.csv` with columns [img_id, img_filename, y, place, split]

### Key Hyperparameters from Literature

| Source | Epochs | LR | Batch | WD | T_early |
|--------|--------|-----|-------|-----|---------|
| JTT | 300 | 1e-5 | 64 | 1.0 | 50 |
| Group DRO | 300 | 1e-3 | 128 | 1e-4 | N/A |
| **Ours (PoC)** | 100 | 1e-3 | 64 | 1e-4 | 20 |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-12

### Workflow History for This Hypothesis
- 2026-08-12T13:22: Hypothesis h-e1 set to IN_PROGRESS
- 2026-08-12: Phase 2C experiment design initiated
- 2026-08-12: MCP research completed (Archon KB, Exa GitHub)
- 2026-08-12: Experiment specification synthesized (Level 1.5)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
