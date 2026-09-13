# Product Requirements Document: H-M1
## GroupDRO Minority Group Upweighting Creates Group-Balanced Gradient Signal — Mechanism Theory Confirmation

**stepsCompleted:** [1, 2, 3, 4, 5, 6, 7]
**hypothesis_id:** h-m1
**hypothesis_type:** MECHANISM
**tier:** FULL
**generated_at:** 2026-08-05T17:00:00Z
**source:** 02c_experiment_brief.md

---

## 1. Executive Summary

Implement a lightweight theoretical mechanism verification experiment to confirm that GroupDRO's worst-group loss objective (Sagawa et al. 2019, arXiv:1911.08731) creates a group-balanced gradient signal by exponentially upweighting minority groups during training. This is a BUILD_ON hypothesis: no new model training is required. The experiment consists of:

1. **Waterbirds group distribution analysis** — confirm minority groups (group_array ∈ {1, 2}) constitute <10% of training data, establishing the imbalance that motivates GroupDRO upweighting.
2. **GroupDRO mechanism code analysis** — verify `LossComputer` exponentiated gradient ascent on group weights from `kohpangwei/group_DRO` (also used by `izmailovpavel/spurious_feature_learning`).
3. **WGA proxy evidence** — report GroupDRO (0.88) vs ERM (0.72) WGA from Izmailov 2022 Table 1.
4. **Visualization** — group distribution pie chart, weight evolution schematic, causal chain diagram.

**Gate:** MUST_WORK — GroupDRO mechanism confirmed via Sagawa 2019 derivation + code analysis AND minority_fraction < 0.10. Failure means H-M2 (gradient propagation) is unmotivated and the pipeline stops.

---

## 2. Problem Statement

The BSER pipeline's causal chain (GroupDRO signal → backbone gradient → reduced spurious encoding) rests on the assumption that GroupDRO's worst-group loss produces a qualitatively different gradient signal than ERM's uniform sample weighting. H-M1 verifies this first step: does GroupDRO actually upweight minority groups (background-atypical examples) to create a group-balanced effective loss?

This is established theory (Sagawa 2019), but we must confirm:
- The specific minority group identity in Waterbirds (groups 1 and 2 are background-atypical)
- That the implementation in izmailovpavel/spurious_feature_learning uses the `is_robust=True` path with exponentiated gradient ascent
- That the empirical WGA gap (GroupDRO > ERM) is consistent with the mechanism prediction

---

## 3. Objectives and Success Criteria

### Primary Objective
Confirm GroupDRO worst-group loss mechanism creates group-balanced gradient signal via theoretical derivation, code analysis, and empirical proxy evidence.

### Success Criteria (GATE: MUST_WORK)

| Check | Method | Expected Result | Gate |
|-------|--------|----------------|------|
| Minority group fraction | `np.bincount(group_array)[[1,2]].sum() / N_train` | < 0.10 (~5%) | MUST_WORK |
| GroupDRO upweighting mechanism | Code review: LossComputer `is_robust=True` | group_weights increase for high-loss groups | MUST_WORK |
| Mathematical derivation | Sagawa 2019 Algorithm 1 | `q'_g = q_g * exp(η_q * L_g)`, minority → high weight | MUST_WORK |
| WGA proxy evidence | Izmailov 2022 Table 1 | GroupDRO WGA=0.88 > ERM WGA=0.72 | MUST_WORK |

**Combined Gate:** ALL four checks must pass → H-M2 proceeds.

### Secondary Criteria (Non-blocking)
- Runtime < 5 minutes (analysis only, no GPU required)
- Figures generated: group pie chart, weight evolution schematic, causal chain diagram
- Report saved to `h-m1/04_validation.md`

### Failure Contingency
If GroupDRO code analysis fails (no `is_robust=True` path found) → Pipeline STOPS. H-M2, H-M3, H-P2 are unmotivated and must be redesigned from Phase 2A.

---

## 4. Data Specification

### Primary Dataset

**Dataset:** Waterbirds WILDS v1.0
**Source:** WILDS benchmark (Koh et al. 2021); originally constructed in Sagawa et al. 2019
**Download:** Pre-cached at `/home/PrayPrey/.wilds_cache/waterbirds_v1.0` (do NOT re-download — verified by H-P0)
**Manual download required:** NO — cache already present
**Loading library:** `wilds` package

```python
from wilds import get_dataset
import numpy as np

dataset = get_dataset(dataset='waterbirds', download=False,
                      root_dir='/home/PrayPrey/.wilds_cache')
train_data = dataset.get_subset('train')
group_array = train_data.metadata_array[:, 0].numpy()  # group_ids
# Group encoding:
# 0 = landbird + land background (majority, spurious-consistent)
# 1 = landbird + water background (minority, background-atypical) ~184 train
# 2 = waterbird + land background (minority, background-atypical) ~56 train
# 3 = waterbird + water background (majority, spurious-consistent) ~1057 train
```

**Full training split:** ~4795 images (all groups).
- H-M1 uses ALL training samples to compute group statistics — no subset needed.

### Group Structure

| group_array | Bird | Background | Type | Approx Train Size |
|-------------|------|------------|------|-------------------|
| 0 | Landbird | Land | Majority (spurious-consistent) | ~3498 |
| 1 | Landbird | Water | **Minority** (background-atypical) | ~184 |
| 2 | Waterbird | Land | **Minority** (background-atypical) | ~56 |
| 3 | Waterbird | Water | Majority (spurious-consistent) | ~1057 |

**Minority groups (H-M1 focus):** group_array ∈ {1, 2} — these are the background-atypical examples that GroupDRO exponentially upweights.

**Spurious attribute:** `background_label = group_array % 2` (0=land, 1=water)

### No Preprocessing Required
H-M1 accesses only `metadata_array` (group labels), not image pixels. No image loading or preprocessing needed.

---

## 5. Model Specification

### Checkpoints (Reference — No Inference Required)

**Source:** izmailovpavel/spurious_feature_learning (NeurIPS 2022)
**Access:** Pre-cached at `/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scsl/docs/youra_research/_archive/20260805T130336_routing_recovery/h-e1/checkpoints`
**Architecture:** ResNet-50, GroupDRO-trained × 3 seeds + ERM-trained × 3 seeds
**Used for:** WGA proxy evidence reporting only (Izmailov 2022 Table 1 values, no new inference)

**No new inference performed** — H-M1 is a theoretical mechanism verification. The checkpoints are referenced only to establish that they were trained with `is_robust=True` (GroupDRO).

### GroupDRO Training Configuration (Historical — Documented from izmailovpavel repo)

| Parameter | Value | Source |
|-----------|-------|--------|
| Optimizer | SGD (momentum=0.9) | kohpangwei/group_DRO/train.py |
| Learning rate | 0.001 | Izmailov 2022 Appendix B |
| Weight decay | 0.001 | Izmailov 2022 Appendix B |
| Batch size | 32 | Izmailov 2022 Appendix B |
| Epochs | 300 (early stop on worst-group val acc) | Izmailov 2022 |
| GroupDRO step size (γ) | 0.01 | Sagawa 2019 default |
| Seeds | 3 (seed1, seed2, seed3) | Pre-trained checkpoints |
| Loss | GroupDRO worst-group (LossComputer, is_robust=True) | kohpangwei/group_DRO |

---

## 6. Functional Requirements

### FR-1: Waterbirds Group Distribution Analysis
- Load Waterbirds WILDS training split metadata (no image loading)
- Compute `np.bincount(group_array, minlength=4)` for all 4 groups
- Compute `minority_fraction = group_counts[[1,2]].sum() / N_train`
- Verify minority_fraction < 0.10

```python
from wilds import get_dataset
import numpy as np

dataset = get_dataset('waterbirds', download=False, root_dir='/home/PrayPrey/.wilds_cache')
train_data = dataset.get_subset('train')
group_array = train_data.metadata_array[:, 0].numpy()
group_counts = np.bincount(group_array, minlength=4)
minority_fraction = group_counts[[1, 2]].sum() / len(group_array)
print(f"Group counts: {group_counts}")  # Expected: ~[3498, 184, 56, 1057]
print(f"Minority fraction: {minority_fraction:.4f}")  # Expected: ~0.050
assert minority_fraction < 0.10, f"Minority fraction {minority_fraction} >= 0.10"
```

### FR-2: GroupDRO Mechanism Documentation
- Document the `LossComputer` exponentiated gradient ascent mechanism from `kohpangwei/group_DRO`
- Verify that izmailovpavel uses `is_robust=True` flag (confirmed from Exa GitHub search in Phase 2C)
- Include the mathematical derivation from Sagawa 2019 Algorithm 1:
  - `q'_g = q_g * exp(η_q * L(θ; S_g))` then normalize
  - Minority groups (high loss early in training) receive exponentially higher weights
  - `objective = group_losses @ q` (weighted dot product dominated by minority losses)

```python
# GroupDRO Weight Update (from kohpangwei/group_DRO/train.py)
# Implements Sagawa 2019 Algorithm 1 - Exponentiated Gradient Ascent on group weights

class GroupDROLossComputer:
    def __init__(self, n_groups=4, step_size=0.01):
        self.group_weights = torch.ones(n_groups) / n_groups  # uniform init
        self.step_size = step_size  # γ in Sagawa 2019

    def compute_loss(self, per_sample_losses, group_ids):
        # Step 1: Per-group average losses
        group_losses = torch.zeros(self.n_groups)
        for g in range(self.n_groups):
            mask = (group_ids == g)
            if mask.any():
                group_losses[g] = per_sample_losses[mask].mean()
        # Step 2: Weighted objective (minority groups dominate if high loss)
        objective = group_losses @ self.group_weights
        # Step 3: Exponentiated gradient ascent on weights
        self.group_weights = self.group_weights * torch.exp(
            self.step_size * group_losses.detach())
        self.group_weights = self.group_weights / self.group_weights.sum()
        return objective
    # Result: Groups 1,2 (minorities, high-loss early) receive exponentially higher weights
    # → backbone gradient reflects their loss signal → backbone reduces spurious reliance
```

### FR-3: WGA Proxy Evidence Reporting
- Report GroupDRO WGA=0.88 vs ERM WGA=0.72 from Izmailov 2022 Table 1
- Note: +0.16 WGA improvement is consistent with mechanism prediction (minority group upweighting forces backbone to handle atypical examples)

### FR-4: Mechanism Confirmation Report
- Summarize all 4 gate checks with PASS/FAIL status
- Generate `h-m1/04_validation.md` with:
  - Group distribution table (actual counts from dataset)
  - GroupDRO weight update pseudo-code + mathematical derivation
  - WGA evidence table
  - Gate verdict: PASS or FAIL

### FR-5: Visualization
- **Required:** GroupDRO vs ERM WGA bar chart (0.88 vs 0.72) with mechanism annotation
- **Required:** Waterbirds group distribution pie chart (showing ~5% minority fraction)
- **Optional:** GroupDRO weight evolution schematic (illustrative, based on Sagawa 2019 Figure 1)
- **Optional:** Causal chain diagram: H-M1 → H-M2 → H-M3 (mechanism flow)
- Save all figures to `h-m1/figures/`

### FR-6: Results Logging
- Save structured results to `h-m1/results.json`:
  ```json
  {
    "minority_fraction": 0.050,
    "group_counts": [3498, 184, 56, 1057],
    "mechanism_confirmed": true,
    "wga_groupdro": 0.88,
    "wga_erm": 0.72,
    "gate_result": "PASS"
  }
  ```

---

## 7. Non-Functional Requirements

### NFR-1: No Model Training
- H-M1 is analysis-only; no training, no backward pass, no GPU required
- Runtime: < 5 minutes (metadata loading + numpy operations)

### NFR-2: Reproducibility
- Group distribution is deterministic (fixed dataset) — no random seed needed
- Results are identical on any run

### NFR-3: Resource Constraints
- GPU: NOT required (metadata-only analysis)
- Memory: < 100 MB (numpy arrays of group labels)
- Storage: < 1 MB (results.json + 04_validation.md + figures)

### NFR-4: Reuse from H-P0
- Waterbirds WILDS local cache path: `/home/PrayPrey/.wilds_cache/waterbirds_v1.0` (verified by H-P0)
- Checkpoint directory: `/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scsl/docs/youra_research/_archive/20260805T130336_routing_recovery/h-e1/checkpoints` (for reference only)

---

## 8. Dependencies

### 8.1 Python Packages

```
wilds          # Waterbirds dataset loading
numpy          # Group distribution computation
matplotlib     # Visualization
torch          # For group_weights tensor operations (optional, numpy sufficient)
```

### 8.2 External Repositories (Reference — No Download Required)

| Repository | URL | Purpose |
|------------|-----|---------|
| kohpangwei/group_DRO | https://github.com/kohpangwei/group_DRO | Sagawa 2019 official GroupDRO implementation |
| izmailovpavel/spurious_feature_learning | HuggingFace Hub | Source of pre-trained GroupDRO checkpoints |

### 8.3 Pre-conditions

- H-P0 COMPLETED and PASS (DFR ≡ ERM backbone confirmed) ✓
- Waterbirds WILDS cache at `/home/PrayPrey/.wilds_cache/waterbirds_v1.0` ✓ (verified by H-P0)
- Python packages: `wilds`, `numpy`, `matplotlib` installed
- No GPU required

---

## 9. Evaluation Criteria

### Primary Metrics (Gate: MUST_WORK)

| Metric | Definition | Target | GATE |
|--------|-----------|--------|------|
| minority_fraction | `group_counts[[1,2]].sum() / N_train` | < 0.10 | MUST_WORK |
| mechanism_confirmed | LossComputer `is_robust=True` path verified | True | MUST_WORK |
| math_derivation | Sagawa 2019 Algorithm 1 exponentiated gradient ascent | Documented | MUST_WORK |
| wga_gap_positive | GroupDRO WGA > ERM WGA | True (0.88 > 0.72) | MUST_WORK |

### Secondary Metrics (Non-blocking)

| Metric | Expected |
|--------|---------|
| group_counts[1] (landbird-water) | ~184 train samples |
| group_counts[2] (waterbird-land) | ~56 train samples |
| Runtime | < 5 minutes |

---

## 10. Out of Scope

- New model training or inference (pre-trained checkpoints referenced only for WGA values)
- Linear probe experiments (H-M3 scope)
- Gradient flow analysis (H-M2 scope)
- Statistical hypothesis testing (theoretical mechanism, not empirical)
- Comparison to SAM or DFR training objectives (H-M3 scope)
- Downloading new checkpoints (reuse H-P0 cache)

---

## 11. Implementation Notes

- **Minimal experiment:** H-M1 is a 2-5 minute analysis script; do not over-engineer
- **Theory-first approach:** The mechanism is established in Sagawa 2019; this experiment documents and confirms, not discovers
- **Group distribution access:** Use `train_data.metadata_array[:, 0]` not `train_data.y_array` (y_array is bird species, not group)
- **minority_fraction expected:** ~0.050 (groups 1+2 total ~240 out of ~4795 training samples)
- **H-M1 is INCREMENTAL:** Builds on H-P0 confirmed checkpoints and dataset cache

---

*Generated from: h-m1/02c_experiment_brief.md*
*Pipeline position: Phase 3 (Implementation Planning)*
*Gate: MUST_WORK — GroupDRO mechanism confirmed AND minority_fraction < 0.10*
*Base hypothesis: H-P0 (COMPLETED, PASS)*
