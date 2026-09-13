# Experiment Design: H-M2

**Date:** 2026-04-14
**Author:** Anonymous
**Hypothesis Statement:** If trajectory divergence reflects spurious-feature conflict specifically, then AUROC will attenuate >0.10 under GroupDRO training but <0.05 under variance-matched random reweighting, because GroupDRO targets spurious reliance while random reweighting only smooths gradients generically.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing spurious-specificity via controlled intervention comparison.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 COMPLETED (PASS, AUROC=0.9452)
**Gate Status:** SHOULD_WORK (not blocking if fails)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED, PASS)

### Gate Condition
- **Gate Type:** SHOULD_WORK
- **Pass Condition:** AUROC_ERM - AUROC_GroupDRO > 0.10 AND AUROC_ERM - AUROC_Random < 0.05
- **Fail Action:** EXPLORE generic hardness explanation (document finding but continue pipeline)

---

## Continuation Context

This experiment builds on H-E1's validated infrastructure and findings:
- **H-E1 Result:** AUROC = 0.9452 ± 0.0072 for trajectory-based minority detection
- **Key Finding:** Initial loss (L₁) is most discriminative feature
- **Infrastructure:** Loss tracking, feature extraction, and evaluation pipeline validated

### Previous Hypothesis Results (if applicable)
- **H-E1 (PASS):** Trajectory features successfully predict minority group membership with AUROC=0.9452
- **H-M1 (FAIL):** Curvature timing hypothesis failed (timing gap = 0.20 ± 0.40 epochs, target ≥3)
  - Lesson: Curvature stabilizes early (epoch 2-3) for both groups
  - Implication: H-M2 should focus on AUROC attenuation, not curvature timing

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Search Queries Executed:**
1. "GroupDRO spurious correlation experiment" → No relevant results (diffusion models)
2. "loss trajectory divergence training dynamics" → No relevant results (diffusion training)
3. "Waterbirds benchmark group robustness" → No relevant results

**Assessment:** Archon KB is specialized for generative AI (diffusion models). No directly applicable content for:
- GroupDRO implementation patterns
- Spurious correlation detection
- Waterbirds benchmark experiments
- Sample reweighting strategies

**Fallback:** Experiment design relies on:
- Exa GitHub search for official implementations (Step 03)
- Phase 2B verification plan (documented protocol)
- H-E1 validated infrastructure (trajectory extraction pipeline)

### Archon Code Examples

**Search Queries Executed:**
1. "GroupDRO PyTorch training loop" → No relevant results
2. "sample reweighting training loss" → Generic training loop patterns only

**Relevant Generic Pattern Found:**
```python
# Generic training loop pattern (adaptable for GroupDRO)
while training:
    loss = compute_loss(model, batch)  # Will use GroupDRO loss
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
```

**Note:** GroupDRO-specific implementation will be sourced from official repos via Exa search.

### Exa GitHub Implementations

**Query 1: GroupDRO Official Implementation (Sagawa et al.)**

**Repository 1**: [kohpangwei/group_DRO](https://github.com/kohpangwei/group_DRO) ⭐ Official
- **URL**: https://github.com/kohpangwei/group_DRO
- **Relevance**: Official implementation from ICLR 2020 paper authors (Sagawa, Koh, Hashimoto, Liang)
- **Architecture**: ResNet-50 pretrained on ImageNet
- **Key Code**:
  ```bash
  # GroupDRO on Waterbirds
  python run_expt.py -s confounder -d CUB -t waterbird_complete95 -c forest2water2 \
    --lr 0.001 --batch_size 128 --weight_decay 0.0001 --model resnet50 \
    --n_epochs 300 --reweight_groups --robust --gamma 0.1
  ```
- **Training Config**:
  - Optimizer: SGD with momentum 0.9
  - Learning rate: 0.001 (Waterbirds)
  - Batch size: 128
  - Epochs: 300
  - Weight decay: 0.0001 (or 1.0 for strong regularization)
  - GroupDRO gamma: 0.1
- **Dataset**: Waterbirds (waterbird_complete95_forest2water2), available via WILDS
- **Results**: ~92% worst-group accuracy with proper regularization

**Repository 2**: [coastalcph/fairlex](https://github.com/coastalcph/fairlex/blob/main/algorithms/groupDRO.py)
- **URL**: https://github.com/coastalcph/fairlex
- **Relevance**: Clean GroupDRO implementation in modular format
- **Key Code**:
  ```python
  class GroupDRO(SingleModelAlgorithm):
      def __init__(self, config, d_out, grouper, loss, metric, n_train_steps, is_group_in_train):
          self.group_weights_step_size = config.group_dro_step_size
          self.group_weights = torch.zeros(grouper.n_groups)
          self.group_weights[is_group_in_train] = 1
          self.group_weights = self.group_weights/self.group_weights.sum()
      
      def objective(self, results):
          group_losses, _, _ = self.loss.compute_group_wise(
              results['y_pred'], results['y_true'],
              results['g'], self.grouper.n_groups, return_dict=False)
          return group_losses @ self.group_weights
  ```
- **Pattern**: Weighted average of group losses, with dynamic weight updates

**Query 2: Sample Reweighting for Variance-Matched Control**

**Repository 3**: [danieltan07/learning-to-reweight-examples](https://github.com/danieltan07/learning-to-reweight-examples)
- **URL**: https://github.com/danieltan07/learning-to-reweight-examples
- **Relevance**: Meta-learning approach to sample reweighting (⭐355)
- **Key Pattern**:
  ```python
  # Weighted loss computation
  cost = F.binary_cross_entropy_with_logits(y_f_hat, labels, reduce=False)
  l_f = torch.sum(cost * w)  # w = sample weights
  ```

**PyTorch WeightedRandomSampler** (for random reweighting baseline):
```python
from torch.utils.data import WeightedRandomSampler

# Variance-matched random weights (same variance as GroupDRO gradient variance)
weights = compute_variance_matched_weights(training_data)
sampler = WeightedRandomSampler(weights=weights, num_samples=len(dataset), replacement=True)
```

**Serena Analysis Needed**: false (Code patterns are clear)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Assessment:**
1. ⭐⭐⭐ **kohpangwei/group_DRO** - Official implementation, exact hyperparameters from paper
2. ⭐⭐ **coastalcph/fairlex** - Clean modular GroupDRO class, good for understanding
3. ⭐ **PyTorch WeightedRandomSampler** - Standard tool for random reweighting baseline

**Recommended Implementation Path:**
- Primary: Fork kohpangwei/group_DRO, add trajectory logging from H-E1
- Fallback: Implement GroupDRO loss wrapper using coastalcph/fairlex pattern
- Justification: Official repo has exact hyperparameters (lr=0.001, gamma=0.1, epochs=300) validated to achieve 92% WGA on Waterbirds. H-E1 trajectory infrastructure can be directly integrated.

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. GroupDRO implementation pattern is well-documented in official repo (kohpangwei/group_DRO) and modular implementation (coastalcph/fairlex). No complex custom architectures requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Dataset**: Waterbirds
**Type**: standard (benchmark)
**Source**: Sagawa et al. (2020) "Distributionally Robust Neural Networks for Group Shifts"

**Statistics**:
- Total samples: 4,795 training, 1,199 validation, 5,794 test
- Classes: 2 (waterbird, landbird)
- Groups: 4 (bird_type × background)
  - Group 0: landbird on land (majority)
  - Group 1: landbird on water (minority)
  - Group 2: waterbird on land (minority)
  - Group 3: waterbird on water (majority)
- Spurious correlation: 95% train, balanced test

**Preprocessing**:
- Resize to 224×224
- Center crop
- Normalize: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]

**Augmentation** (training):
- Random horizontal flip
- Random resized crop (scale=0.7-1.0)

**Loading Information** (for Phase 4 download):
- Method: WILDS library or direct download
- Identifier: `waterbird_complete95_forest2water2`
- Code:
```python
# Option 1: WILDS library
from wilds import get_dataset
dataset = get_dataset(dataset='waterbirds', download=True)

# Option 2: Direct from group_DRO repo
# Download: https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz
# Extract to: {root_dir}/cub/data/waterbird_complete95_forest2water2/
```

**Continuation Note**: Reusing dataset from H-E1 (validated, cache available at `/home/anonymous/YouRA_results_new_4_sonnet45/TEST_scsl_opus45_4/docs/youra_research/20260414_scsl/.data_cache/datasets/waterbirds/`)

### Models

#### Baseline Model

**Architecture**: ResNet-50 (pretrained on ImageNet)
**Type**: CNN classifier
**Source**: torchvision.models

**Configuration**:
- Input: 224×224×3 RGB images
- Output: 2 classes (waterbird, landbird)
- Final layer: Replace fc with nn.Linear(2048, 2)
- Pretrained: ImageNet weights

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: `resnet50`
- Code:
```python
import torchvision.models as models
model = models.resnet50(pretrained=True)
model.fc = nn.Linear(model.fc.in_features, 2)  # 2 classes
```

**Continuation Note**: Same architecture as H-E1, enabling controlled comparison

#### Proposed Model

**Architecture:** ResNet-50 + Trajectory Feature Extraction (from H-E1) under 3 Training Regimes
**Integration Point:** Per-sample loss logging integrated into training loop
**Modification:** Training loop wrapper that tracks per-sample losses and computes trajectory features

**Core Mechanism Implementation:**

```python
# Core Mechanism: GroupDRO Attenuation Test
# Based on: kohpangwei/group_DRO (official), H-E1 trajectory infrastructure

class TrainingRegimeComparator:
    """
    Compare trajectory divergence AUROC across 3 training regimes:
    1. ERM (baseline) - standard cross-entropy
    2. GroupDRO - worst-group loss minimization
    3. Random Reweighting - variance-matched control
    """
    def __init__(self, model, train_loader, group_counts, gamma=0.1):
        self.model = model
        self.gamma = gamma  # GroupDRO step size
        # Initialize group weights for GroupDRO
        self.group_weights = torch.ones(4) / 4  # 4 groups in Waterbirds
        # Compute variance-matched random weights
        self.random_weights = self._compute_variance_matched_weights(group_counts)
    
    def erm_loss(self, logits, labels, sample_idx):
        """Standard ERM: equal weight per sample"""
        per_sample_loss = F.cross_entropy(logits, labels, reduction='none')
        self.log_trajectory(sample_idx, per_sample_loss)  # From H-E1
        return per_sample_loss.mean()
    
    def groupdro_loss(self, logits, labels, groups, sample_idx):
        """GroupDRO: upweight worst-performing group"""
        per_sample_loss = F.cross_entropy(logits, labels, reduction='none')
        self.log_trajectory(sample_idx, per_sample_loss)
        # Compute group losses
        group_losses = torch.zeros(4)
        for g in range(4):
            mask = (groups == g)
            if mask.sum() > 0:
                group_losses[g] = per_sample_loss[mask].mean()
        # Update group weights (exponentiated gradient)
        self.group_weights = self.group_weights * torch.exp(self.gamma * group_losses)
        self.group_weights = self.group_weights / self.group_weights.sum()
        return (group_losses * self.group_weights).sum()
    
    def random_reweight_loss(self, logits, labels, sample_idx):
        """Random reweighting: variance-matched control"""
        per_sample_loss = F.cross_entropy(logits, labels, reduction='none')
        self.log_trajectory(sample_idx, per_sample_loss)
        weights = self.random_weights[sample_idx]
        return (per_sample_loss * weights).sum() / weights.sum()

# Gate condition: AUROC_ERM - AUROC_GroupDRO > 0.10 AND AUROC_ERM - AUROC_Random < 0.05
```

### Training Protocol

**Three Training Regimes** (each trained independently):

| Regime | Loss Function | Purpose |
|--------|---------------|---------|
| ERM | Standard cross-entropy | Baseline AUROC |
| GroupDRO | Worst-group weighted loss | Test spurious-specific attenuation |
| Random Reweighting | Variance-matched sample weights | Control for generic gradient smoothing |

**Shared Configuration** (from H-E1 + kohpangwei/group_DRO):
- **Optimizer**: SGD with momentum=0.9
- **Learning Rate**: 0.001 (Waterbirds optimal from official repo)
- **Schedule**: None (constant LR for Waterbirds)
- **Batch Size**: 128
- **Epochs**: 20 (sufficient for trajectory features, H-E1 validated)
- **Weight Decay**: 0.0001 (ERM) / 1.0 (GroupDRO, strong regularization)
- **Seeds**: 3 (for statistical reliability on mechanism test)

**GroupDRO-Specific**:
- **Gamma** (group weight step size): 0.1
- **Reweight Groups**: True
- **Robust**: True
- **Generalization Adjustment**: 0

**Random Reweighting Control**:
- Match gradient variance to GroupDRO by sampling weights from same distribution
- Verify: Var(∇L_random) ≈ Var(∇L_groupdro)

**Source**: kohpangwei/group_DRO official implementation, H-E1 validated configuration

### Evaluation

**Primary Metrics**:
1. **AUROC_ERM**: Trajectory-based minority detection under ERM (from H-E1: 0.9452)
2. **AUROC_GroupDRO**: Trajectory-based minority detection under GroupDRO
3. **AUROC_Random**: Trajectory-based minority detection under random reweighting
4. **ΔAUROC_GroupDRO**: AUROC_ERM - AUROC_GroupDRO (target: > 0.10)
5. **ΔAUROC_Random**: AUROC_ERM - AUROC_Random (target: < 0.05)

**Success Criteria** (Gate: SHOULD_WORK):
- **Primary**: ΔAUROC_GroupDRO > 0.10 (GroupDRO significantly attenuates divergence)
- **Secondary**: ΔAUROC_Random < 0.05 (Random reweighting does NOT attenuate)
- **Interpretation**: If both conditions met → divergence is spurious-specific, not generic hardness

**Failure Interpretation**:
- If ΔAUROC_GroupDRO ≤ 0.10: GroupDRO does not specifically reduce trajectory divergence
- If ΔAUROC_Random ≥ 0.05: Divergence reflects generic sample hardness, not spurious-specific conflict

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification (minority vs majority group prediction)
- Library: sklearn.metrics
- Code:
```python
from sklearn.metrics import roc_auc_score
auroc = roc_auc_score(y_true=group_labels, y_score=trajectory_predictions)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing ΔAUROC_GroupDRO vs ΔAUROC_Random with threshold lines at 0.10 and 0.05

#### Additional Figures (LLM Autonomous)
- **AUROC Comparison**: Bar chart of AUROC_ERM, AUROC_GroupDRO, AUROC_Random with error bars
- **Training Loss Trajectories**: Per-group loss curves under each training regime (3 panels)
- **Group Weight Evolution**: GroupDRO group weights across epochs
- **Gradient Variance Verification**: Histogram comparing gradient variance of GroupDRO vs Random Reweighting

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists**: Yes - GroupDRO loss and random reweighting are well-defined algorithms
- **mechanism_isolatable**: Yes - Each training regime runs independently
- **baseline_measurable**: Yes - H-E1 established AUROC_ERM = 0.9452

### Architecture Compatibility
- **Compatibility Check**: ResNet-50 + trajectory logging validated in H-E1
- **Integration Point**: Training loop loss computation (wrapper around standard loss)
- **No Architecture Change**: Same model, different loss functions

### Activation Indicators
- **GroupDRO Active**: `[GroupDRO] Group weights updated: [w0, w1, w2, w3]` logged each epoch
- **Random Reweighting Active**: `[RandomReweight] Applied variance-matched weights, var={variance}` logged
- **Trajectory Logging Active**: Per-sample losses recorded (same as H-E1)

### Mechanism Verification Code
```python
def verify_mechanism_activation(training_log):
    """Verify mechanisms are actually activated, not just code running."""
    # Check GroupDRO weight updates
    groupdro_weights = extract_group_weights(training_log)
    assert not torch.allclose(groupdro_weights[-1], torch.ones(4)/4), \
        "GroupDRO weights should diverge from uniform"
    
    # Check variance matching
    groupdro_grad_var = compute_gradient_variance(training_log, 'groupdro')
    random_grad_var = compute_gradient_variance(training_log, 'random')
    assert abs(groupdro_grad_var - random_grad_var) / groupdro_grad_var < 0.2, \
        "Random reweighting gradient variance should match GroupDRO within 20%"
    
    return True
```

### Success Criteria (Gate: SHOULD_WORK)

**PoC Pass Condition:**
1. Code runs without error
2. ΔAUROC_GroupDRO = AUROC_ERM - AUROC_GroupDRO > 0.10 (spurious-specific attenuation)
3. ΔAUROC_Random = AUROC_ERM - AUROC_Random < 0.05 (control shows no effect)
4. Mechanism verification checks pass (weights update, variance matched)

**Hypothesis Support Threshold**: Both conditions (2) AND (3) must be met
**Hypothesis Support Metric**: ΔAUROC differential between GroupDRO and Random

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Note**: Archon KB is specialized for diffusion models. No directly relevant results for GroupDRO/spurious correlation research.

**Query 1**: "GroupDRO spurious correlation experiment"
- **Result**: No relevant results (returned diffusion model content)
- **Action**: Relied on Exa GitHub search for primary sources

**Query 2**: "loss trajectory divergence training dynamics"
- **Result**: No relevant results
- **Action**: Used H-E1 validated infrastructure

### B. GitHub Implementations (Exa)

**Repository 1**: [kohpangwei/group_DRO](https://github.com/kohpangwei/group_DRO) ⭐ Official
- **URL**: https://github.com/kohpangwei/group_DRO
- **Query Used**: "Sagawa GroupDRO official implementation GitHub Waterbirds"
- **Relevance**: Official ICLR 2020 paper implementation by Sagawa, Koh et al.
- **Key Code**:
  ```bash
  # Official command for Waterbirds
  python run_expt.py -s confounder -d CUB -t waterbird_complete95 -c forest2water2 \
    --lr 0.001 --batch_size 128 --weight_decay 0.0001 --model resnet50 \
    --n_epochs 300 --reweight_groups --robust --gamma 0.1
  ```
- **Configuration Extracted**: lr=0.001, batch_size=128, weight_decay=0.0001/1.0, gamma=0.1
- **Their Results**: ~92% worst-group accuracy on Waterbirds
- **Used For**: GroupDRO training configuration, loss function design

**Repository 2**: [coastalcph/fairlex](https://github.com/coastalcph/fairlex)
- **URL**: https://github.com/coastalcph/fairlex/blob/main/algorithms/groupDRO.py
- **Query Used**: "GroupDRO PyTorch distributionally robust optimization"
- **Relevance**: Clean modular GroupDRO implementation
- **Key Code**:
  ```python
  def objective(self, results):
      group_losses, _, _ = self.loss.compute_group_wise(
          results['y_pred'], results['y_true'],
          results['g'], self.grouper.n_groups, return_dict=False)
      return group_losses @ self.group_weights
  ```
- **Used For**: GroupDRO loss computation pattern

**Repository 3**: [danieltan07/learning-to-reweight-examples](https://github.com/danieltan07/learning-to-reweight-examples)
- **URL**: https://github.com/danieltan07/learning-to-reweight-examples
- **Query Used**: "sample reweighting importance weighting PyTorch"
- **Relevance**: Sample reweighting implementation pattern (⭐355)
- **Key Code**:
  ```python
  cost = F.binary_cross_entropy_with_logits(y_f_hat, labels, reduce=False)
  l_f = torch.sum(cost * w)  # w = sample weights
  ```
- **Used For**: Random reweighting loss function design

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear. GroupDRO and sample reweighting patterns are well-documented in official repos.

### D. Previous Hypothesis Context

**Source**: H-E1 Phase 4 Validation (PASS)
- **File**: `h-e1/04_checkpoint.yaml`, `h-e1/code/outputs/results.json`
- **Reused Components**:
  - Dataset: Waterbirds (verified, cached)
  - Model: ResNet-50 (pretrained)
  - Trajectory Infrastructure: Per-sample loss logging, feature extraction
  - Baseline AUROC: 0.9452 ± 0.0072
- **Why Reused**: Enables controlled experiment - only training regime changes

**Source**: H-M1 Phase 4 Validation (FAIL)
- **Lesson Learned**: Curvature timing not discriminative (gap = 0.20 epochs)
- **Implication**: Focus on AUROC attenuation, not temporal patterns

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (Waterbirds) | H-E1 + Phase 2B | Validated cache, 02b_verification_plan.md |
| Model (ResNet-50) | H-E1 + torchvision | H-E1 checkpoint |
| GroupDRO loss | Exa GitHub | kohpangwei/group_DRO, coastalcph/fairlex |
| GroupDRO config | Exa GitHub | kohpangwei/group_DRO (lr=0.001, gamma=0.1) |
| Random reweighting | Exa GitHub | danieltan07/learning-to-reweight-examples |
| Trajectory features | H-E1 | H-E1 validated infrastructure |
| AUROC baseline | H-E1 | 0.9452 ± 0.0072 |
| Gate condition | Phase 2B | ΔAUROC > 0.10 (GroupDRO), < 0.05 (Random) |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-04-14T10:25:00Z

### Workflow History for This Hypothesis
- 2026-04-14T10:05:49Z: Hypothesis h-m2 set to IN_PROGRESS (External loop starting Phase 2C → 3 → 4)
- 2026-04-14T10:25:00Z: Phase 2C experiment design COMPLETED

### Quality Validation
- ✅ All hyperparameters justified
- ✅ Dataset choice justified
- ✅ Mechanism grounded in code
- ✅ No unsupported assumptions
- ✅ Full traceability

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
