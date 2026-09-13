# Experiment Design: H-M1

**Date:** 2026-08-04
**Author:** Anonymous
**Hypothesis Statement:** Under ERM training on Waterbirds, ERM Phase I spurious feature exploitation creates differential confidence trajectories: p_minority(t*)∈[0.3,0.7] (boundary condition) and p_majority(t*)>0.80 (saturation) in ≥4/5 seeds, because SGD provably learns spurious features first (LaBonte & Muthukumar 2026), creating differential confidence trajectories.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Experiment** — Verifies causal root of trace asymmetry. No new training — reuses H-E3 checkpoints.

---

## Workflow Status

**Verification State:** H-E3 VALIDATED (PASS). H-M1 IN_PROGRESS.
**Prerequisites Satisfied:** H-E3 MUST_WORK gate PASSED (4/5 seeds)
**Gate Status:** MUST_WORK — failure routes to Phase 0 (mechanism collapse)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E3 (VALIDATED — 4/5 seeds, AUROC(t*)≥0.85)

### Gate Condition
MUST_WORK: p_minority(t*) ∈ [0.3, 0.7] in ≥4/5 seeds.
Failure → STOP, route to Phase 0 (mechanism collapses; trace asymmetry loses mechanistic basis).

---

## Continuation Context

H-M1 is a **continuation experiment** building directly on H-E3 validated results:

| Component | Status | Reuse |
|-----------|--------|-------|
| Waterbirds dataset | Confirmed | Same dataset, same path |
| ResNet-50 checkpoints | Saved at t∈{0,1,5,10,20,50} × 5 seeds | Full reuse — no new training |
| t* per seed | Seed1=t20, Seed2=t50, Seed3=t50, Seed4=t20, Seed5=t5 | From H-E3 04_validation.md |
| Hyperparameters | lr=3e-3, mom=0.9, wd=1e-4, bs=32 | Inherited — controlled comparison |
| data.py, evaluate_trajectory.py | Validated | Extend with confidence extraction |

### Previous Hypothesis Results (H-E3)
- AUROC(t*): Seeds 1-5 = [0.850, 0.885, 0.897, 0.903, 0.890] — 4/5 PASS
- Epoch-0 AUROC: All seeds < 0.70 (confirms ERM emergence)
- Hutchinson CV: All seeds < 5% (K=50 stable)
- R(t) at t*: Mean_min/Mean_maj consistently > 1 at optimal checkpoint
- **Gate: PASSED** — proceed to H-M1

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: ERM spurious correlation minority confidence trajectory**
- Archon KB does not contain domain-relevant results for this research area (diffusion model content indexed). No useful findings.

**Query 2: Waterbirds group robustness ERM evaluation benchmark**
- No domain-relevant results in Archon KB.

**Note:** Archon KB is indexed with diffusion/generative model content. All relevant implementation patterns found via Exa GitHub search below.

### Archon Code Examples

**Query: Waterbirds confidence prediction minority majority groups**
- No domain-relevant code examples in Archon KB.

### Exa GitHub Implementations

**Query 1: Waterbirds ERM training confidence trajectory minority majority groups PyTorch**

**Repository 1**: PolinaKirichenko/deep_feature_reweighting
- **URL**: https://github.com/polinakirichenko/deep_feature_reweighting
- **Relevance**: Official DFR implementation with Waterbirds train_classifier.py; eval_freq=1 pattern; group-wise evaluation at each checkpoint; 5-seed protocol
- **Architecture**: ResNet-50, pretrained, torchvision
- **Key Config**:
  - Optimizer: SGD, lr=1e-3 (their default; H-E3 validated lr=3e-3)
  - Batch size: 32
  - Epochs: 100 (H-E3 uses 50)
- **Dataset**: Waterbirds v1.0 (same path/format)
- **Group eval**: per-group accuracy at each checkpoint — pattern directly adaptable for confidence extraction

**Repository 2**: kohpangwei/group_DRO (generate_waterbirds.py)
- **URL**: https://github.com/kohpangwei/group_DRO
- **Relevance**: Canonical Waterbirds dataset construction; confirms group sizes: G0=3498, G1=184, G2=56, G3=1057; group index mapping (y∈{0,1} × background∈{land,water})
- **Key Insight**: minority_mask = (group ∈ {1, 2}) i.e., misaligned background samples — exactly what H-M1 needs

**Repository 3**: deeplearning-wisc/vit-spurious-robustness
- **URL**: https://github.com/deeplearning-wisc/vit-spurious-robustness
- **Relevance**: checkpoint loading + per-group evaluation pattern (evaluate.py)
- **Key Pattern**: load checkpoint → forward pass → extract softmax → compute per-group statistics

**Query 2: LaBonte Muthukumar SGD spurious feature learning phase transitions**

**Paper**: "SGD Provably Prioritizes a Shortcut Spurious Feature in the XOR Model" (LaBonte & Muthukumar 2026, arXiv:2606.30444)
- **URL**: https://arxiv.org/abs/2606.30444
- **Relevance**: Direct theoretical basis for H-M1. Proves SGD learns spurious feature first (exponentially fast). Phase I: spurious feature drives majority margin growth → saturation. Phase II: majority margin large → minority learning suppressed. Predicts: majority high confidence, minority remains near boundary.
- **Key Theorem (3.2)**: Acc_majority → 1, Acc_minority → 0 as d→∞ under Phase I dynamics
- **Phase structure**: Phase Ia (sign alignment) → Phase Ib (spurious growth) → Phase II (majority saturation, minority suppressed)

**Paper**: "The Group Robustness is in the Details: Revisiting Finetuning Under Spurious Correlations" (LaBonte et al., NeurIPS 2024)
- **URL**: https://mlanthology.org/neurips/2024/labonte2024neurips-group/
- **Relevance**: Spectral imbalance finding — minority covariance matrices have larger spectral norm than majority (conditioned on class). Empirically validates on Waterbirds with ResNet-50. Supports H-M1 mechanism.

**Paper**: "The Silent Majority: Demystifying Memorization Effect in the Presence of Spurious Correlations" (arXiv:2501.00961)
- **URL**: https://arxiv.org/html/2501.00961v1
- **Relevance**: Directly shows training/test accuracy gap: majority groups G0, G3 show minimal train-test gap; minority groups G1, G2 show significant gap. Waterbirds ResNet-50 empirical evidence. Fig 1 demonstrates differential dynamics.

**Serena Analysis Needed**: false — code is straightforward (forward pass → softmax → group-wise statistics). No complex new mechanism to analyze; reusing validated H-E3 code.

### 🎯 Implementation Priority Assessment

**For H-M1, this is NOT a paper reproduction experiment but a continuation experiment.**

**Implementation Priority:**
- Primary: Extend H-E3 validated code (evaluate_trajectory.py) with confidence extraction
- Rationale: H-E3 checkpoints already exist; data.py already provides minority_mask; only new operation is extracting softmax confidences at each checkpoint

**Recommended Implementation Path:**
- Primary: Extend `docs/youra_research/h-e3/code/evaluate_trajectory.py` with confidence metrics
- Fallback: Write standalone `compute_confidence.py` using same data.py and checkpoint loading
- Justification: Minimal new code — confidence extraction is simpler than Hutchinson trace

### Code Analysis (Serena MCP)

*Skipped* — Code from search results (H-E3 validated code) is sufficiently clear. No complex new mechanism; confidence extraction via `torch.softmax(logits, dim=1)` is standard.

---

## Experiment Specification

### Dataset

**Dataset**: Waterbirds v1.0
**Type**: standard (real dataset, NOT synthetic)
**Source**: Sagawa et al. 2019; kohpangwei/group_DRO
**Path**: /home/PrayPrey/data/waterbirds_v1.0/ (confirmed present in H-E3)

**Statistics**:
- Train: 4795 samples total
  - G0 (landbird-land): 3498 (majority)
  - G1 (landbird-water): 184 (minority)
  - G2 (waterbird-land): 56 (minority)
  - G3 (waterbird-water): 1057 (majority)
- Minority total: G1+G2 = 240 samples (5%)
- Majority total: G0+G3 = 4555 samples (95%)

**Group Definitions for H-M1**:
- minority_mask: group ∈ {1, 2} (misaligned background)
- majority_mask: group ∈ {0, 3} (aligned background)

**Preprocessing** (inherited from H-E3):
- Resize: (256, 256) → CenterCrop(224)
- Normalize: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
- No augmentation for evaluation pass

**Loading Information** (for Phase 4):
- Method: custom (already implemented in H-E3 code/data.py)
- Identifier: /home/PrayPrey/data/waterbirds_v1.0/
- Code: `from data import WaterbirdsDataset; dataset = WaterbirdsDataset(root=cfg.DATA_DIR)`

### Models

#### Baseline Model

**Architecture**: ResNet-50 (CNN, pretrained ImageNet)
**Loading Information** (for Phase 4):
- Method: torchvision (already trained; load from H-E3 checkpoints)
- Identifier: H-E3 checkpoint files `checkpoint_seed{s}_epoch{t}.pt`
- Code: `model.load_state_dict(torch.load(ckpt_path)); model.eval()`

**Configuration** (from H-E3 04_validation.md):
- Input: (B, 3, 224, 224)
- Output: (B, 2) logits
- Last-fc: Linear(2048, 2)
- Pretrained: ImageNet IMAGENET1K_V1

#### Proposed Model

**Architecture:** Same ResNet-50 checkpoints + confidence extraction at each t

**Core Mechanism Implementation:**

```python
# Core Mechanism: Per-Sample Confidence Extraction at Checkpoint t
# Based on: H-E3 validated evaluate_trajectory.py

import torch
import torch.nn.functional as F

def extract_confidence_by_group(model, loader, minority_mask, device):
    """
    Extract per-sample predicted confidence (in true class) for each sample.
    Args:
        model: ResNet-50 at checkpoint t (eval mode)
        loader: Waterbirds train DataLoader (no shuffle)
        minority_mask: bool tensor [N], True for G1∪G2 samples
        device: cuda
    Returns:
        p_per_sample: tensor [N], confidence in true label per sample
        minority_conf: mean confidence for minority samples
        majority_conf: mean confidence for majority samples
    """
    model.eval()
    all_confs = []
    all_labels = []
    with torch.no_grad():
        for x, y, g in loader:
            x, y = x.to(device), y.to(device)
            logits = model(x)  # (B, 2)
            probs = F.softmax(logits, dim=1)  # (B, 2)
            # confidence in true class
            conf = probs[torch.arange(len(y)), y]  # (B,)
            all_confs.append(conf.cpu())
            all_labels.append(y.cpu())
    p_per_sample = torch.cat(all_confs)  # (N,)
    p_minority = p_per_sample[minority_mask].mean().item()
    p_majority = p_per_sample[~minority_mask].mean().item()
    return p_per_sample, p_minority, p_majority

# Gate check per seed:
def check_h_m1_gate(p_min_at_tstar, p_maj_at_tstar):
    primary = 0.3 <= p_min_at_tstar <= 0.7   # boundary condition
    secondary = p_maj_at_tstar > 0.80          # saturation condition
    return primary, secondary
```

### Training Protocol

**No new training required.** H-M1 reuses H-E3 checkpoints.

**Evaluation Protocol** (inherited from H-E3, extended with confidence):

**Inherited from H-E3 04_validation.md (optimal, reusing for controlled experiment):**
- Optimizer: SGD — Parameters: lr=3e-3, momentum=0.9, weight_decay=1e-4 (training already done)
- Batch Size: 32 (evaluation batch size)
- Epochs: Already trained — checkpoints at t∈{0,1,5,10,20,50}
- Seeds: {1, 2, 3, 4, 5}

**Evaluation Steps:**
1. For each seed s ∈ {1,2,3,4,5}:
   a. Identify t* from H-E3 results: [Seed1=t20, Seed2=t50, Seed3=t50, Seed4=t20, Seed5=t5]
   b. For each checkpoint t ∈ {0,1,5,10,20,50}:
      - Load checkpoint_seed{s}_epoch{t}.pt
      - Run full training set forward pass (4795 samples)
      - Extract p_minority(t), p_majority(t) via extract_confidence_by_group()
   c. At t*: check gate conditions

**Seeds**: 5 (same seeds as H-E3 for matched comparison)

**Rationale**: Optimal hyperparameters in H-E3, reusing for controlled experiment (only confidence metrics added).

### Evaluation

**Primary Metrics**:
- `p_minority(t*)`: mean confidence of minority (G1∪G2) samples in true class at t*
  - Gate: must be in [0.3, 0.7]
- `p_majority(t*)`: mean confidence of majority (G0∪G3) samples in true class at t*
  - Gate: must be > 0.80

**Per-Checkpoint Metrics** (for trajectory visualization):
- `p_minority(t)` at each t ∈ {0,1,5,10,20,50}
- `p_majority(t)` at each t ∈ {0,1,5,10,20,50}

**Success Criteria**:
- Primary (gate): p_minority(t*) ∈ [0.3, 0.7] in ≥4/5 seeds
- Secondary: p_majority(t*) > 0.80 in ≥4/5 seeds

**Expected Values** (from LaBonte & Muthukumar 2026 theory + JTT/DFR empirical literature):
- p_minority at t*: ≈0.4-0.65 (near decision boundary under 95% spuriosity; ERM Phase I saturation not complete for minority)
- p_majority at t*: ≈0.85-0.99 (majority converges rapidly due to spurious feature alignment, LaBonte 2026 Theorem 3.2)
- Source: LaBonte & Muthukumar 2026 arXiv:2606.30444 (Acc_majority→1, Acc_minority→0 under Phase I); empirical support from "Silent Majority" (arXiv:2501.00961) Fig 1

**Metrics Loading Information** (for Phase 4):
- Task Type: binary classification confidence measurement
- Library: torch.nn.functional (softmax) — no external metrics library needed
- Code: `probs = F.softmax(logits, dim=1); conf = probs[range(B), y_true]`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: p_minority(t*) and p_majority(t*) per seed with gate thresholds [0.3, 0.7] and 0.80 overlaid

#### Additional Figures (LLM Autonomous)
Based on MECHANISM hypothesis type and confidence trajectory variables:
1. **Confidence Trajectory Plot**: p_minority(t) and p_majority(t) vs t for each seed (show divergence)
2. **Confidence Distribution**: Box plot of per-sample confidence at t* for minority vs majority
3. **Boundary Fraction Plot**: Fraction of minority samples with p∈[0.3,0.7] at each t (shows boundary retention)

> Phase 4 Coder MUST include figure generation logic. All figures saved to `docs/youra_research/h-m1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error on full Waterbirds training set (4795 samples)
2. p_minority(t*) ∈ [0.3, 0.7] in ≥4/5 seeds (primary gate)
3. p_majority(t*) > 0.80 in ≥4/5 seeds (secondary gate)

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions (Must be TRUE before experiment)

| Check | Description | Status |
|-------|-------------|--------|
| Mechanism Exists | H-E3 checkpoints available at all t∈{0,1,5,10,20,50} × 5 seeds | TRUE — confirmed in 04_validation.md |
| Mechanism Isolatable | Confidence extraction is separate from Hessian trace; can compare with/without | TRUE |
| Baseline Measurable | Epoch-0 confidence (t=0) provides pre-training baseline for differential | TRUE |

### Architecture Compatibility Check

ResNet-50 with 2-class linear head (2048→2) is fully compatible:
- `torch.softmax(model(x), dim=1)` produces valid probability vector summing to 1
- Binary classification: p_i = prob of correct class ∈ (0,1)
- No special layers required; standard forward pass suffices

**Required Features:**
- Standard softmax output layer (linear → softmax)
- Access to predicted logits per sample

**Incompatible Architectures:**
- Models without interpretable confidence scores (e.g., SVM, tree ensembles)

### Mechanism Activation Indicators

| Indicator Type | Expected Signal | Code Location |
|---------------|-----------------|---------------|
| Log Message | "p_minority_mean=X.XX, p_majority_mean=X.XX at t=T" | compute_confidence.py |
| Tensor Shape | p_per_sample shape = (4795,); minority subset shape = (240,) | extract_confidence_by_group() |
| Metric Delta | p_majority(t*) - p_minority(t*) ≥ 0.15 (differential gap expected) | evaluate_confidence.py |

**Activation Verification Code (Phase 4 must implement):**

```python
def verify_mechanism_activated(results_per_seed):
    """
    Verify H-M1 mechanism: differential confidence trajectories exist.
    Args:
        results_per_seed: dict {seed: {t: {'p_min': float, 'p_maj': float}}}
    Returns:
        (bool, dict) — mechanism activated, detailed indicators
    """
    indicators = {}
    for seed, traj in results_per_seed.items():
        tstar = traj['tstar']
        p_min = traj[tstar]['p_min']
        p_maj = traj[tstar]['p_maj']
        indicators[seed] = {
            'minority_boundary': 0.3 <= p_min <= 0.7,   # primary gate
            'majority_saturated': p_maj > 0.80,           # secondary gate
            'gap': p_maj - p_min,                          # differential
            'both_pass': (0.3 <= p_min <= 0.7) and (p_maj > 0.80)
        }
    n_pass = sum(v['both_pass'] for v in indicators.values())
    mechanism_active = n_pass >= 4  # ≥4/5 seeds
    return mechanism_active, indicators
```

### Mechanism Failure Detection

| Failure Mode | Detection Method | Action |
|--------------|------------------|--------|
| p_minority < 0.3 | Direct check at t* | FAIL: Minority confidently wrong → mechanism collapses → ABANDON, route Phase 0 |
| p_majority < 0.80 | Direct check at t* | EXPLORE: Majority not saturated → extend training window to epoch 100 |
| No trajectory divergence | p_majority - p_minority < 0.05 | INVESTIGATE: ERM not exploiting spurious features as predicted |
| Checkpoint load error | FileNotFoundError for H-E3 ckpt | FAIL: H-E3 code outputs missing — re-run H-E3 phase 4 |

### Success Criteria (Mechanism Level)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mechanism Activated | TRUE | ≥4/5 seeds pass boundary condition |
| Gap Measurable | p_maj - p_min > 0.10 | Before/after confidence comparison at t* |
| Hypothesis Supported | p_minority(t*) ∈ [0.3,0.7] AND p_majority(t*)>0.80 in ≥4/5 seeds | verify_mechanism_activated() returns True |

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Status**: Archon KB indexed with diffusion model content. No relevant sources for spurious correlation / confidence trajectory domain. All implementation grounding from Exa GitHub + theoretical papers.

### B. GitHub Implementations (Exa)

**Repository 1**: PolinaKirichenko/deep_feature_reweighting
- **URL**: https://github.com/polinakirichenko/deep_feature_reweighting
- **Query Used**: "Waterbirds ERM training confidence trajectory minority majority groups PyTorch"
- **Relevance**: Official DFR pipeline; group-wise evaluation pattern at each checkpoint; Waterbirds dataset loading; eval_freq=1 training loop structure
- **Key Pattern Extracted**:
  ```python
  # Per-checkpoint eval loop (adapted):
  for epoch in checkpoint_epochs:
      model.load_state_dict(torch.load(f'ckpt_seed{s}_epoch{epoch}.pt'))
      model.eval()
      with torch.no_grad():
          logits = model(x_batch)
          probs = F.softmax(logits, dim=1)
          conf = probs[range(B), y_true]
  ```
- **Used For**: Confidence extraction loop design; checkpoint loading pattern

**Repository 2**: kohpangwei/group_DRO (generate_waterbirds.py)
- **URL**: https://github.com/kohpangwei/group_DRO
- **Query Used**: "Waterbirds ERM confidence minority majority"
- **Relevance**: Canonical group index definition: G0=landbird-land(3498), G1=landbird-water(184), G2=waterbird-land(56), G3=waterbird-water(1057)
- **Used For**: minority_mask definition = (group ∈ {1, 2}); dataset group size constants

**Repository 3**: H-E3 validated codebase (docs/youra_research/h-e3/code/)
- **Relevance**: Direct predecessor — data.py, compute_traces.py, evaluate_trajectory.py all validated
- **Reuse plan**: extend evaluate_trajectory.py to also extract and store softmax confidences
- **Used For**: Core implementation template for H-M1

### C. Code Analysis (Serena)

Serena analysis not performed — code is sufficiently clear from Exa results and H-E3 validated code. Confidence extraction is a standard PyTorch forward pass operation with no complex architectural dependencies.

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report — H-E3 (docs/youra_research/h-e3/04_validation.md)
- **Reused Components**:
  - Checkpoints: `checkpoint_seed{s}_epoch{t}.pt` at all t∈{0,1,5,10,20,50} for seeds 1-5
  - data.py: WaterbirdsDataset with minority_mask (group ∈ {1,2})
  - evaluate_trajectory.py: checkpoint loading + evaluation loop structure
  - t* per seed: Seed1=t20, Seed2=t50, Seed3=t50, Seed4=t20, Seed5=t5
  - Hyperparameters: lr=3e-3, momentum=0.9, weight_decay=1e-4, batch_size=32
- **Why Reused**: Enables controlled experiment — only metric changes (trace→confidence), dataset/model/checkpoints identical

### E. Theoretical Sources

**LaBonte & Muthukumar 2026** (arXiv:2606.30444):
- "SGD Provably Prioritizes a Shortcut Spurious Feature in the XOR Model"
- Theorem 3.2: Acc_majority→1, Acc_minority→0 under Phase I dynamics
- Phase structure: Ia (sign alignment) → Ib (spurious growth) → II (majority saturation)
- Directly predicts: p_majority→1.0, p_minority→0 asymptotically; at finite t*, minority still in (0.3, 0.7)
- **Used For**: Expected values for p_minority(t*) and p_majority(t*); gate threshold justification

**LaBonte et al., NeurIPS 2024** (mlanthology.org/neurips/2024/labonte2024neurips-group):
- "The Group Robustness is in the Details: Revisiting Finetuning Under Spurious Correlations"
- Spectral imbalance: minority covariance has larger spectral norm than majority (conditioned on class)
- Empirically validated on Waterbirds ResNet-50
- **Used For**: Supporting evidence for differential feature statistics across groups

**"The Silent Majority"** (arXiv:2501.00961):
- Shows G0,G3 (majority) minimal train-test gap; G1,G2 (minority) large gap — both ResNet-50 and ViT-small
- Fig 1 directly demonstrates asymmetric confidence dynamics on Waterbirds
- **Used For**: Empirical baseline for expected confidence gap at training time

### F. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset: Waterbirds v1.0 | Previous hypothesis | H-E3 04_validation.md (confirmed path) |
| Group definitions (G0-G3) | GitHub | kohpangwei/group_DRO generate_waterbirds.py |
| Minority mask: G1∪G2 | GitHub | kohpangwei/group_DRO + H-E3 data.py |
| Confidence extraction: softmax | Standard PyTorch | torch.nn.functional.softmax |
| Checkpoint loading | GitHub + H-E3 | PolinaKirichenko/DFR + H-E3 code |
| Training protocol (inherited) | Previous hypothesis | H-E3 04_validation.md |
| t* per seed | Previous hypothesis | H-E3 04_validation.md results table |
| Expected p_minority ∈ [0.3,0.7] | Theory paper | LaBonte & Muthukumar 2026 Theorem 3.2 |
| Expected p_majority > 0.80 | Theory paper | LaBonte & Muthukumar 2026 Phase II analysis |
| Differential gap empirical evidence | Research paper | arXiv:2501.00961 Fig 1 |
| Gate condition ≥4/5 seeds | Previous hypothesis | H-E3 gate design (consistent) |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — no file write)
**Date:** 2026-08-04

### Workflow History for This Hypothesis
- H-E3 set to IN_PROGRESS: 2026-08-04T03:36:09
- H-E3 VALIDATED (PASS): 2026-08-04T05:35:00
- H-M1 set to IN_PROGRESS: 2026-08-04T05:24:43
- H-M1 experiment_design IN_PROGRESS: 2026-08-04 (this session)

---

*MCP Tools Used: Archon (no domain matches), Exa (GitHub + web search — 3 relevant repos, 3 papers)*
*All specifications grounded in: H-E3 validated code, LaBonte & Muthukumar 2026, LaBonte et al. NeurIPS 2024, Silent Majority (2501.00961)*
*Next Phase: Phase 3 - Implementation Planning*
