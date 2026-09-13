# Phase 2B Context: H-E1

**Hypothesis ID:** H-E1
**Type:** EXISTENCE
**Gate:** MUST_WORK

## Statement

Crystallization zone exists as localized training phase where WGA decline accelerates.

Full: Under standard SGD training on spurious-correlation benchmarks, if we track worst-group accuracy, then we will observe a localized training phase where WGA decline accelerates, because simplicity bias creates initial spurious feature advantage.

## Rationale

Foundation hypothesis. Must establish crystallization zone exists as detectable phenomenon before testing mechanism. This validates the core claim of temporal localization.

## Variables

- **Independent:** Training epoch (1 to N)
- **Dependent:** Worst-group accuracy (WGA), d²WGA/dt²
- **Controlled:** Architecture (ResNet-50), batch size (128), optimizer (SGD)

## Verification Protocol

1. Train ResNet-50 on Waterbirds/CelebA/ColoredMNIST with epoch-level checkpointing (full train sets, standard splits)
2. Compute WGA at each checkpoint across all minority-group samples (n>500 per benchmark)
3. Apply 5-epoch rolling average smoothing to WGA curve
4. Compute second derivative d²WGA/dt²
5. Test for statistically significant (p<0.05) negative peak

## Success Criteria (PoC: Direction-based)

- **Primary:** Significant negative d²WGA/dt² peak in first 50% of training
- **Secondary:** Effect present in at least 2/3 benchmarks

## Failure Response

IF fails: PIVOT to alternative crystallization detection (gradient norm analysis)

## Experimental Setup

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Waterbirds (primary), CelebA, ColoredMNIST | Standard spurious correlation benchmarks with group annotations enabling WGA computation |
| **Model** | ResNet-50 | Standard architecture used in group robustness literature |

**Dataset Details:**
- Source: WILDS benchmark suite (p-lambda/wilds)
- Path: Downloaded via wilds.get_dataset()

**Model Details:**
- Type: CNN
- Source: torchvision.models.resnet50(pretrained=True)

## Prerequisites

None (foundation hypothesis)

## Dependencies

None

## Gate Condition

MUST_WORK: If this fails, the entire research program stops.

## Risks

- R1: WGA proxy validity
- R2: Detection method failure
- R4: Architecture specificity
- R5: Benchmark representativeness
