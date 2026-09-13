# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-26T12:00:00+00:00
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Independent-Controller Ablation)
- **Gap ID**: gap-2
- **Gap Title**: Cross-Paradigm Spurious Feature Encoding Comparison (Supervised vs SSL vs Contrastive)
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 10

---

## Research Dialogue Context

**Participants**: Dr. Nova (Creative Novelty Explorer), Prof. Vera (Rigorous Validation Architect), Dr. Sage (Research Impact Evaluator), Prof. Pax (Feasibility & Reality Checker), Dr. Ally (Hypothesis Strengthening Champion), Prof. Rex (Hypothesis Stress-Test Master)

**Total Exchanges**: 10

**Convergence Reason**: All 6 criteria met — SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS addressed

### Key Insights
- The conventional assumption that SSL reduces spurious feature reliance may be backwards for visually prominent spurious attributes that are instance-discriminative
- Contrastive learning (SimCLR) may *amplify* background encoding on Waterbirds because background texture is stable across standard augmentations and visually distinct across images
- The spurious/task probe accuracy ratio is a more discriminative paradigm comparator than raw probe accuracy
- Targeted augmentation design (background-replacement augmentation) may suppress spurious feature encoding without group annotations

### Breakthrough Moments
- Dr. Nova (Exchange 1): Flipped the conventional assumption — contrastive learning may encode MORE spurious features, not fewer, for visually prominent spurious attributes
- Prof. Rex (Exchange 6): Proposed ratio metric (spurious/task probe accuracy) as improvement over raw accuracy, and identified three specific failure modes with mitigations
- Dr. Nova (Exchange 7): Proposed augmentation ablation (SimCLR-NoBackground) as causal mechanism test — converts correlational paradigm comparison into mechanistic experiment

---

## Final Hypothesis

### Title
Spurious Feature Encoding Differs Across Pretraining Paradigms Due to Objective-Determined Augmentation Invariance

### Hypothesis ID
H-SPEnc-v1

### Core Claim
Under ImageNet-scale pretraining with identical ResNet-50 backbone architecture, if we compare four training paradigms (supervised ERM, SimCLR contrastive, DINO self-distillation, BarlowTwins non-contrastive SSL), then the spurious/task probe accuracy ratio on frozen representations will differ significantly across at least one paradigm pair (≥ 2%, p < 0.05) on Waterbirds and CelebA group-annotated benchmarks, because the training objective determines which visual features become instance-discriminative and thus preferentially encoded — specifically, contrastive objectives encode visually prominent spurious features (Waterbirds background) more strongly than supervised ERM because background texture is highly instance-discriminative but not invariant under standard augmentation sets.

### Mechanism
1. **Training objective selects instance-discriminative features**: Contrastive objectives maximize agreement between augmented views — features stable across augmentations AND distinct across images are preferentially encoded.
2. **Standard augmentations preserve visually prominent spurious features**: Waterbirds background (land vs water) is stable across random crop/color jitter/blur AND visually distinct across images — making it instance-discriminative for contrastive learning but not for ERM.
3. **Higher spurious encoding → larger worst-group accuracy gap**: When a linear head is trained on biased (95% spurious-correlated) data, higher spurious encoding in backbone features leads to higher spurious reliance in the head and worse worst-group accuracy.

---

## Predictions

### P1 (Primary — Existence Gate)
At least one paradigm pair will show a statistically significant difference in spurious/task probe accuracy ratio on Waterbirds balanced test split (p < 0.05, t-test across 5 seeds, ≥ 2% ratio difference).

**Success criterion**: max(ratio_difference) ≥ 0.02 AND min(p-value) < 0.05 across 6 paradigm pairs
**Falsification**: All 6 pairwise t-tests p > 0.05 OR max ratio difference < 0.02

### P2 (Directional — Contrastive vs ERM)
SimCLR representations will show the highest spurious/task ratio on Waterbirds (background is instance-discriminative) but not on CelebA (hair color is less augmentation-stable).

**Success criterion**: SimCLR ratio > ERM ratio on Waterbirds (p < 0.05) AND no significant difference on CelebA
**Falsification**: SimCLR ≤ ERM ratio on Waterbirds OR SimCLR > ERM ratio on CelebA as well

### P3 (Mechanism — Augmentation Ablation, Exploratory)
SimCLR-NoBackground (background-replacement augmentation) will show ≥ 5% lower spurious/task ratio than SimCLR-Original on Waterbirds.

**Success criterion**: SimCLR_NoBackground ratio < SimCLR_Original ratio (p < 0.05, difference ≥ 0.05)
**Falsification**: No significant ratio reduction (p > 0.05 or difference < 0.02)

---

## Novelty

**What's new**: 4-paradigm controlled spurious attribute linear probe comparison on identical ResNet-50 backbone with group-annotated balanced test splits, combined with augmentation ablation as causal mechanism test.

**How it differs from prior work**:
- *DomainBed*: compares average accuracy across domain shifts, not spurious attribute probes; does not freeze backbone
- *WILDS*: evaluates fine-tuned models; does not probe for spurious attribute specifically
- *DFR (Kirichenko 2022)*: shows ERM features are sufficient; does not compare to SSL paradigms
- *Group DRO (Sagawa 2020)*: robustification method, not pretraining comparison

---

## Experimental Design

**Backbone**: ResNet-50 (frozen) for all 4 paradigms
- ERM: `torchvision.models.resnet50(pretrained=True)`
- SimCLR: SimCLR-v2 PyTorch or MoCo-v3 (`torch.hub.load`) — use MoCo-v3 if SimCLR TF conversion is problematic
- DINO: `torch.hub.load('facebookresearch/dino:main', 'dino_resnet50')`
- BarlowTwins: `torch.hub.load('facebookresearch/barlowtwins:main', 'resnet50')`

**Primary Dataset**: Waterbirds (WILDS package)
- Spurious attribute: background type (land vs water)
- Task label: bird species
- Group-balanced probe train split; balanced test split (50% spurious, 50% anti-spurious)
- Must use `group_balanced_sample=True` in WILDS dataloader for probe training

**Secondary Dataset**: CelebA (torchvision)
- Spurious attribute: gender (Male)
- Task label: hair color (Blond_Hair)
- Group splits from group_DRO repo

**Probes**: Single linear layer (logistic regression) for (a) spurious attribute label and (b) task label, separately

**Primary Metric**: Spurious/task ratio = spurious_probe_acc / task_probe_acc on balanced test split

**Secondary Metric**: Pearson correlation between spurious/task ratio and worst-group accuracy gap

**Augmentation Ablation**: Train SimCLR from scratch on Waterbirds train split under 2 conditions (5 seeds each, 20 epochs):
- SimCLR-Original: standard augmentations (crop + color jitter + gaussian blur)
- SimCLR-NoBackground: adds random background replacement from Places365

---

## Limitations

- All checkpoints pretrained on ImageNet; pretraining data distribution may affect spurious encoding
- Cannot distinguish augmentation-invariance from objective differences without the ablation experiment
- 5 seeds may have insufficient power for detecting effects < 2% ratio difference
- Results may not generalize to ViT backbones (different attention mechanism)
- Linear probe measures encoding, not utilization — secondary WGA correlation needed to confirm downstream impact

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Hypothesis ID** | H-SPEnc-v1 |
| **Discussion Exchanges** | 10 |
| **Convergence** | All 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | SimCLR checkpoint format (use MoCo-v3 fallback); WILDS group_balanced_sample=True verification |
| **Phase 2B Ready** | Yes |

---

*Phase: 2A - Dialogue (Self-Contained Tikitaka Loop)*
*Architecture: Independent-Controller Ablation (no external orchestrator)*
*Generated: 2026-08-26*
