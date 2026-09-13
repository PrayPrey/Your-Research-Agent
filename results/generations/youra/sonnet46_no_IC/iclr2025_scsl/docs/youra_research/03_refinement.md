# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-05T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Loop (Claude-only, IC-ablation)
- **Gap ID**: gap_1
- **Gap Title**: Per-Method Spurious Attribute Linear Probe Accuracy Not Measured in Existing Work
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15
- **Recursive Entry**: v5 (4 prior archives)

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15 (natural convergence at min_exchanges=15)

**Convergence Reason**: All 6 criteria PASS (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS). All 6 personas participated with genuine adversarial contributions.

### Key Insights
1. **DFR backbone identity** (Prof. Pax, Exchange 4): DFR shares the ERM backbone by construction — the meaningful comparison for backbone-level effects is ERM vs GroupDRO vs SAM, not ERM vs DFR.
2. **Both outcomes contribute** (Dr. Sage, Exchanges 7, 14): whether GroupDRO reduces spurious encoding (H-P1 confirmed) or not (H-P1 rejected), the result clarifies the mechanism of WGA improvement.
3. **WGA correlation** (Dr. Sage, Exchange 14): if spurious probe accuracy predicts WGA, it becomes a diagnostic metric usable without group-labeled validation sets.
4. **Tiered success criteria** (Dr. Ally, Exchange 9): CONFIRMED/SUGGESTIVE/REJECTED with Cohen's d addresses n=3 power limitation honestly.
5. **Confound resolved** (Dr. Ally, Exchange 11): "dilution through feature diversity" vs "active suppression" — both reduce probe accuracy, and both are consistent with the mechanism we claim.

### Breakthrough Moments
- **Exchange 4 (Prof. Pax)**: Identified DFR ≡ ERM backbone architecturally — restructured entire comparison from flat 4-method to backbone-changing vs backbone-preserving distinction.
- **Exchange 12 (Prof. Rex)**: Made DFR backbone identity an empirically testable prediction (H-P0) rather than an assumption — cosine similarity check required.
- **Exchange 13 (Prof. Vera)**: Formalized complete pre-registered 4-part hypothesis structure with branching logic dependent on H-P0 outcome.

---

## Final Hypothesis

### Title
**Backbone Spurious Encoding Reduction (BSER): GroupDRO Training Reduces Linear Decodability of Spurious Background Attributes in ResNet-50 Layer4 Features**

### Hypothesis ID: H-BSER-v1

### Core Claim (Under-If-Then-Because)
Under ResNet-50 checkpoints from izmailovpavel/spurious_feature_learning (3 seeds × 4 methods, fully trained on Waterbirds WILDS), if we compare GroupDRO-trained backbones to ERM-trained backbones using sklearn L-BFGS linear probe accuracy predicting background attribute (land/water, group_array%2) from frozen layer4 features (D=2048) on the full Waterbirds test set, then GroupDRO backbones exhibit significantly lower spurious probe accuracy (paired one-sided t-test, p<0.05, n=3 seeds), because GroupDRO's group-balanced worst-group loss forces gradient updates through all layers to reduce reliance on spurious background features, while DFR (head-only retraining) leaves backbone spurious encoding unchanged relative to ERM (validated by H-P0 sanity check).

### Mechanism
1. GroupDRO training upweights minority groups (background-atypical examples), creating group-balanced gradient signal through all backbone layers
2. Group-balanced gradient propagates through layer4, modifying weights to reduce discriminative utility of spurious background features
3. Reduced spurious gradient → lower linear decodability of background from layer4 features → lower probe accuracy vs ERM

DFR, by construction (frozen backbone), bypasses the mechanism entirely — backbone probe accuracy ≡ ERM.

---

## Predictions

| ID | Statement | Test | Success Criterion | Gate |
|----|-----------|------|-------------------|------|
| P0 | DFR layer4 features ≡ ERM layer4 features at same seed | Mean cosine similarity for 50 test images | ≥ 0.9999 | PREREQUISITE |
| P1 | GroupDRO spurious probe acc < ERM spurious probe acc | Paired one-sided t-test, n=3 seeds | p<0.05 AND Cohen's d>0 | PRIMARY |
| P1b | SAM spurious probe acc < ERM spurious probe acc (exploratory) | Same test | Report direction + Cohen's d only | EXPLORATORY |
| P2 | Pearson r(probe_acc, WGA) < -0.5 across 9 checkpoints | Pearson r + bootstrap CI (n=1000) | r<-0.5 AND CI upper bound <0 | SECONDARY |
| P3 | GroupDRO core probe acc ≥ ERM core probe acc | Directional check, n=3 | GroupDRO mean ≥ ERM mean | PRESERVATION |

**Success Tiers (H-P1):**
- **CONFIRMED**: p<0.05 one-sided AND Cohen's d>0
- **SUGGESTIVE**: p<0.10 one-sided AND Cohen's d>0.5
- **REJECTED**: direction wrong OR (p≥0.10 AND d<0.2)

---

## Novelty

**Key Innovation**: First per-method, per-seed spurious attribute linear probe accuracy measurement with pre-registered statistical testing and mechanistic prediction about which robustification methods change backbone encoding.

**What's new vs prior work:**
- Izmailov 2022: used s-DFR proxy (background as head retraining target) — different task; did not report per-method, per-seed values
- Kirichenko 2022: used WGA — indirect measure of backbone quality
- Park 2025 SCER: regularizes spurious representation directions (interventional); we diagnose whether existing methods implicitly achieve this

---

## Experimental Design

**Dataset**: Waterbirds WILDS at `/home/PrayPrey/.wilds_cache/waterbirds_v1.0`
- Spurious label: `group_array % 2` → 0=land background, 1=water background
- Core label: bird species (waterbird/landbird)

**Model**: ResNet-50 (12 checkpoints from izmailovpavel/spurious_feature_learning)
- Feature extraction: `model.layer4` → `AdaptiveAvgPool2d(1,1)` → flatten → D=2048
- All extractions: `model.eval()` + `torch.no_grad()`

**Probe**: `sklearn.LogisticRegression(solver='lbfgs', C=1e9, max_iter=1000, random_state=42)`

**Statistical Tests**:
- H-P1: `scipy.stats.ttest_rel(ERM_acc, GroupDRO_acc, alternative='greater')` (one-sided: ERM > GroupDRO)
- H-P2: `scipy.stats.pearsonr(probe_acc_array, wga_array)` + 1000-sample bootstrap

---

## Limitations

1. **n=3 seeds**: ~55% power at Cohen's d=0.8 (one-sided t-test). All results reported with tiered criteria.
2. **Layer4 only**: spurious encoding at earlier layers not measured (Phase 1 Gap 3 — secondary, interpretability only if layer4 shows null result).
3. **WGA correlation n=9**: small sample for Pearson r; bootstrap CI required.
4. **DFR treatment**: contingent on H-P0 outcome. If backbone ≠ ERM, interpretation changes.
5. **Waterbirds/ResNet-50 specific**: generalizability to other benchmarks or architectures not claimed.

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Hypothesis ID** | H-BSER-v1 |
| **Discussion Convergence** | Natural at exchange 15 (min=15) |
| **Clarity Verified** | Yes |
| **All Personas Participated** | Yes (6/6) |
| **Genuine Adversarial Discussion** | Yes (Prof. Pax: DFR identity; Prof. Rex: confound + power) |
| **Remaining Objections** | 3 (n=3 power, H-P0 verification, H-P2 bootstrap) — all mitigated |
| **Phase 2B Ready** | READY |

---

*Generated by Phase 2A Self-Play Loop (Claude-only, IC-ablation). No external LLM used.*
*Discussion transcript: discussion_log.md | Convergence audit: 01_round_table/convergence_checks.md*
