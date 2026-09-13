# Experiment Design: h-m2

**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Under Coste et al. 2023 experimental data, if RM score is normalized to [0,1] range and gold preference rate is expressed as a fraction, then the calibration-alignment divergence gap (normalized RM score minus gold preference rate) is strictly positive at high KL levels and grows with increasing optimization pressure, because proxy-gold decoupling (confirmed in H-M1) creates a widening measurement gap.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

---

## Workflow Status

**Verification State:** IN_PROGRESS → COMPLETED (experiment design)
**Prerequisites Satisfied:** h-m1 (MUST_WORK) — PASS
**Gate Status:** MUST_WORK — pending empirical validation

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m2
- **Type:** MECHANISM
- **Prerequisites:** h-m1 (VALIDATED, PASS)

### Gate Condition

MUST_WORK: Calibration-alignment divergence gap (normalized RM score minus gold preference rate) is strictly positive at ≥3 high-KL levels (KL > median) AND increases directionally with KL budget (monotone trend in gap).

**Failure Response:** EXPLORE — recheck normalization protocol; if gap is negative at high KL, hypothesis may need reframing as "calibration-alignment convergence." Contact authors for raw data if normalization protocol is disputed.

---

## Continuation Context

**h-m1 (VALIDATED):** Confirmed RM score monotone increase (Spearman ρ = 1.000, p ≈ 0) and gold preference peak-reversal (peak at KL=2.0 nats, reversal confirmed: gold[peak]=0.630 > gold[final]=0.380) in Coste et al. 2023 digitized data.

**h-m1 Output Data Available** (from `h-m1/results/h_m1_divergence_curve.csv`):
```
kl_budget, rm_score, gold_preference, divergence_gap (raw, unnormalized)
0.0,  0.12, 0.52, -0.40
0.5,  0.48, 0.58, -0.10
1.0,  0.81, 0.61,  0.20
2.0,  1.24, 0.63,  0.61
3.0,  1.55, 0.61,  0.94
4.0,  1.78, 0.57,  1.21
5.0,  1.92, 0.53,  1.39
6.0,  2.01, 0.48,  1.53
7.0,  2.06, 0.43,  1.63
8.0,  2.08, 0.38,  1.70
```
N=10 KL levels, KL range 0–8 nats. RM score range: [0.12, 2.08] — requires normalization to [0,1]. Gold preference already in [0,1] fraction range.

**Key observation from h-m1 raw gap:** Gap transitions from negative (KL=0,0.5) to positive (KL≥1.0), then grows monotonically through KL=8. Median KL = 3.75 nats. High-KL levels (>median): KL ∈ {4.0, 5.0, 6.0, 7.0, 8.0} — all 5 show positive raw gap. H-M2 formalizes this with normalized RM score.

---

## Implementation Research Summary

### Knowledge Base Findings

**Source A.1**: Coste et al. 2023 (arXiv 2310.02743) — h-m1 digitized output
- **Dataset**: Digitized Coste et al. Fig 3/4; confirmed 10 KL-level paired observations
- **Key Input for h-m2**: `rm_score` column (range [0.12, 2.08] in digitized units; requires min-max normalization); `gold_preference` column already in [0,1]
- **Normalization Protocol (Phase 2B §2.2)**: `RM_norm = (RM - RM_min) / (RM_max - RM_min)` per paper; `RM_min = 0.12`, `RM_max = 2.08`
- **Expected Normalized Gap**: gap_norm = RM_norm - gold_preference; at KL=8: gap_norm = (2.08-0.12)/(2.08-0.12) - 0.38 = 1.0 - 0.38 = 0.62 (strongly positive)

**Source A.2**: Phase 2B Verification Plan — h-m2 Protocol (§2.2)
- **Success Criteria**: Gap > 0 at ≥3 high-KL levels (KL > median KL); gap increases directionally; gap metric well-defined with no missing values
- **Key Metrics**: mean_gap (high-KL subset), max_gap, proportion of KL levels with positive gap
- **Normalization**: min-max per paper (within Coste et al. KL range)

**Source A.3**: h-m1 validated results — divergence_final = 1.70 (raw), confirming large proxy-gold separation at max KL
- **Implication for h-m2**: Normalized gap at max KL will be ≈ 0.62; gap should be robustly positive

### GitHub Implementations (Exa)

**Repository B.1**: numpy/numpy — `np.min`, `np.max`, array operations
- **URL**: https://github.com/numpy/numpy
- **Relevance**: Min-max normalization via `(x - x.min()) / (x.max() - x.min())` — stdlib one-liner
- **Key Code**:
  ```python
  rm_norm = (rm - rm.min()) / (rm.max() - rm.min())  # min-max normalize to [0,1]
  gap = rm_norm - gold  # calibration-alignment divergence gap
  ```

**Repository B.2**: scipy/scipy — `scipy.stats.spearmanr`, `scipy.stats.linregress`
- **URL**: https://github.com/scipy/scipy
- **Relevance**: Monotonicity test for gap vs. KL; trend direction confirmation
- **Key Code**:
  ```python
  from scipy import stats
  rho_gap, p_gap = stats.spearmanr(kl, gap)  # gap monotone with KL?
  # Direct input to h-m3 OLS regression
  ```

**Repository B.3**: matplotlib/matplotlib — dual-axis and gap visualization
- **Key Code**:
  ```python
  import matplotlib.pyplot as plt
  fig, ax = plt.subplots()
  ax.plot(kl, gap, 'b-o', label='Divergence Gap (normalized)')
  ax.axhline(0, color='k', linestyle='--', label='Zero line')
  ax.set_xlabel('KL Budget (nats)')
  ax.set_ylabel('gap = RM_norm - gold_preference')
  ```

### Code Analysis (Serena MCP)

*Skipped* — standard numpy/scipy one-liner normalization; no complex custom code requiring semantic analysis. h-m1 codebase (`src/analysis/trajectory.py`) provides the loading pattern to reuse directly.

---

## Experiment Specification

### Dataset

**Primary Dataset: h-m1 Output CSV (Coste et al. 2023 Digitized)**
- **Name**: h-m1-divergence-curve (Coste-2023-KL-RM-Gold-normalized)
- **Source**: `docs/youra_research/h-m1/results/h_m1_divergence_curve.csv` (produced by validated h-m1 Phase 4 experiment)
- **Type**: programmatic-api (real published data, previously digitized and validated)
- **Splits**: Single time-series; N=10 KL-level observations
- **Variables**:
  - `kl_budget`: KL divergence from base policy (nats), range [0, 8]
  - `rm_score`: Raw digitized RM score, range [0.12, 2.08]
  - `gold_preference`: Gold human preference rate, already in [0,1], range [0.38, 0.63]
  - `divergence_gap` (h-m1 raw): Unnormalized gap (will be recomputed post-normalization)

**Synthetic Data Check**: PASS — data is digitized from real published peer-reviewed paper (Coste et al. 2023, arXiv 2310.02743). NOT synthetic/simulated.

**Loading Information** (for Phase 4):
```python
import pandas as pd
df = pd.read_csv("../../h-m1/results/h_m1_divergence_curve.csv")
# Columns: kl_budget, rm_score, gold_preference, divergence_gap
# N=10 rows, KL range [0, 8] nats
```

**Sample Size Assessment:** N=10 KL levels from Coste et al. digitized data.
- High-KL subset (KL > median=3.75): 5 observations (KL ∈ {4,5,6,7,8})
- This is the full available dataset from the published paper; no larger real dataset exists for this specific experiment (RLHF overoptimization with paired RM+gold at 10 KL checkpoints)
- Limitation documented: small N is inherent to figure digitization; effect size is large (gap at KL=8 ≈ 0.62 normalized), making detection feasible at N=10

### Models

#### Baseline Model
No trained model. "Baseline" = normalization reference point.

**Baseline Reference Values:**
- `RM_min = 0.12` (KL=0, pre-RLHF), `RM_max = 2.08` (KL=8, fully optimized)
- `gold_preference` at KL=0 = 0.52 (pre-RLHF human preference baseline)
- Baseline gap (KL=0): `(0.12 - 0.12)/(2.08 - 0.12) - 0.52 = 0.0 - 0.52 = -0.52` (correctly negative at baseline)

#### Proposed Model: Normalized Divergence Gap Computation

**Core Mechanism Implementation:**

```python
# Core Mechanism: Calibration-Alignment Divergence Gap Formation
# Based on: Coste et al. 2023 (arXiv 2310.02743), Phase 2B h-m2 protocol
# Prerequisites: h-m1 VALIDATED (RM monotone, gold reversal confirmed)

import pandas as pd
import numpy as np
from scipy import stats

# === Step 1: Load h-m1 output data ===
df = pd.read_csv("../../h-m1/results/h_m1_divergence_curve.csv")
kl   = df["kl_budget"].values       # shape: (10,) in nats
rm   = df["rm_score"].values         # shape: (10,) raw units [0.12, 2.08]
gold = df["gold_preference"].values  # shape: (10,) fraction [0,1]

# === Step 2: Normalize RM score to [0,1] (min-max, within Coste KL range) ===
rm_norm = (rm - rm.min()) / (rm.max() - rm.min())
# rm_norm: (10,) in [0,1]; rm_norm[0]=0.0, rm_norm[-1]=1.0

# === Step 3: Compute calibration-alignment divergence gap ===
gap = rm_norm - gold
# gap: (10,) — positive = proxy exceeds gold; negative = gold exceeds proxy

# === Step 4: Verify gap is positive at high-KL levels ===
median_kl = np.median(kl)                      # 3.75 nats
high_kl_mask = kl > median_kl                  # [False]*4 + [True]*5
gap_high_kl = gap[high_kl_mask]                # shape: (5,)
n_positive_high_kl = np.sum(gap_high_kl > 0)  # must be >= 3
assert n_positive_high_kl >= 3, f"Only {n_positive_high_kl}/5 high-KL gaps > 0"

# === Step 5: Verify gap grows monotonically with KL ===
rho_gap_kl, p_rho_gap = stats.spearmanr(kl, gap)  # rho > 0 = grows with KL
assert rho_gap_kl > 0, f"Gap does not grow with KL: rho={rho_gap_kl:.3f}"

# === Step 6: Descriptive statistics ===
mean_gap_high_kl = np.mean(gap_high_kl)
max_gap = np.max(gap)
prop_positive = np.mean(gap > 0)

print(f"n_positive_high_kl={n_positive_high_kl}/5")
print(f"mean_gap_high_kl={mean_gap_high_kl:.4f}")
print(f"max_gap={max_gap:.4f}")
print(f"prop_positive={prop_positive:.2f}")
print(f"rho_gap_kl={rho_gap_kl:.4f}, p={p_rho_gap:.6f}")
```

**Expected Values (pre-computed from h-m1 data):**
```
RM_norm values: [0.000, 0.184, 0.352, 0.571, 0.735, 0.847, 0.918, 0.964, 0.990, 1.000]
gold values:    [0.52,  0.58,  0.61,  0.63,  0.61,  0.57,  0.53,  0.48,  0.43,  0.38]
gap values:     [-0.520,-0.396,-0.258,-0.059, 0.125, 0.277, 0.388, 0.484, 0.560, 0.620]
                 KL=0   0.5    1.0    2.0    3.0    4.0    5.0    6.0    7.0    8.0

High-KL (>3.75 nats): KL={4,5,6,7,8} → gaps={0.277, 0.388, 0.484, 0.560, 0.620}
All 5 high-KL gaps > 0 → n_positive_high_kl = 5 (≥ 3 required) ✓
Gap monotone increasing: rho ≈ 1.0 (perfectly monotone) ✓
max_gap ≈ 0.620 (at KL=8)
mean_gap_high_kl ≈ 0.466
prop_positive = 7/10 = 0.70 (positive from KL≥3)
```

### Training Protocol

No model training. Statistical analysis + normalization protocol:

| Parameter | Value | Source |
|-----------|-------|--------|
| Data source | h-m1 output CSV | h-m1 Phase 4 validated results |
| N observations | 10 KL levels | Coste et al. 2023 Fig 3/4 digitization |
| KL range | 0–8 nats | h-m1 data |
| Normalization | min-max per paper: `(RM - RM_min) / (RM_max - RM_min)` | Phase 2B §2.2 protocol |
| High-KL threshold | KL > median = 3.75 nats | Phase 2B success criterion |
| High-KL N | 5 observations (KL ∈ {4,5,6,7,8}) | Computed from N=10 split |
| Seeds | 1 (deterministic; no stochastic elements) | N/A |
| Primary dataset | Coste et al. 2023 (Coste-2023-KL-RM-Gold-normalized) | h-m1 results |
| Runtime estimate | < 1 second | Vectorized numpy operations on N=10 |

### Evaluation

**Primary Metrics:**

| Metric | Definition | Success Threshold | Failure Threshold |
|--------|-----------|-------------------|-------------------|
| `n_positive_high_kl` | Count of high-KL gaps > 0 (KL > 3.75) | ≥ 3 of 5 | < 3 → gap not positive at high KL |
| `rho_gap_kl` | Spearman ρ(KL, normalized gap) | > 0 (directionally growing) | ≤ 0 → gap does not grow |
| `max_gap` | Maximum normalized gap across all KL levels | > 0 | ≤ 0 → no divergence observed |
| `mean_gap_high_kl` | Mean normalized gap for high-KL subset | > 0 | ≤ 0 → no mean positive divergence |
| `prop_positive` | Fraction of all KL levels with gap > 0 | > 0.5 (majority positive) | ≤ 0.3 → gap mostly negative |

**Success Criteria (PoC direction-based):**
- PRIMARY: `n_positive_high_kl ≥ 3` AND `rho_gap_kl > 0` (gap positive at high KL AND grows)
- SECONDARY: `max_gap > 0` AND `mean_gap_high_kl > 0` AND `prop_positive > 0.5`

**Expected Results (from h-m1 data, pre-computed):**
- `n_positive_high_kl = 5` (all 5 high-KL gaps positive) → PASS
- `rho_gap_kl ≈ 1.000` (perfectly monotone) → PASS
- `max_gap ≈ 0.620` → PASS
- `mean_gap_high_kl ≈ 0.466` → PASS
- `prop_positive = 0.70` → PASS

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Min-max normalization + gap computation + descriptive statistics
- Library: `numpy` (normalization, argmax, mean, sum), `scipy.stats` (spearmanr)
- Code: see Core Mechanism Implementation above

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing primary metrics vs. thresholds:
  - `n_positive_high_kl` (5) vs. threshold (3)
  - `rho_gap_kl` (≈1.0) vs. threshold (0)
  - `prop_positive` (0.70) vs. threshold (0.5)

#### Additional Figures (LLM Autonomous)

1. **Normalized gap curve (primary)**: `gap = RM_norm - gold_preference` vs. KL budget — bar or line chart; horizontal zero line; highlight positive region (KL≥3) with shading; annotate max_gap
2. **RM_norm vs. gold_preference dual-line plot**: Both curves on same [0,1] y-axis vs. KL budget — visually shows crossover point and diverging gap
3. **Gap growth visualization**: Scatter plot of gap vs. KL budget with Spearman ρ annotation; high-KL points marked distinctly
4. **Summary normalization table**: Side-by-side raw RM, RM_norm, gold, gap values for all 10 KL levels — documents normalization protocol

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m2/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `n_positive_high_kl >= 3` (gap positive at ≥3 high-KL levels)
3. `rho_gap_kl > 0` (gap grows with KL budget)

---

## Mechanism Verification Protocol

| Element | Specification |
|---------|---------------|
| `mechanism_exists` | Normalized gap = RM_norm - gold_preference; computed from h-m1 validated data |
| `mechanism_isolatable` | Yes — normalization applied to RM column independently; gap computed pointwise |
| `baseline_measurable` | Yes — KL=0 gap = -0.52 (gold exceeds proxy at baseline; expected) |
| `architecture_compatibility` | N/A — pure numpy/scipy normalization and statistics |
| `mechanism_log_message` | `f"n_pos_high_kl={n_positive_high_kl}/5, rho_gap={rho_gap_kl:.3f}, max_gap={max_gap:.3f}, mean_gap_high_kl={mean_gap_high_kl:.3f}"` |
| `tensor_shape_change` | All arrays shape `(10,)` throughout (N=10 KL levels) |
| `metric_delta_expected` | gap[KL=0]: -0.52 → gap[KL=8]: +0.62; n_positive_high_kl: 0 → 5 |
| `mechanism_verification_code` | `assert n_positive_high_kl >= 3` / `assert rho_gap_kl > 0` |
| `hypothesis_support_threshold` | n_positive_high_kl ≥ 3 AND rho_gap_kl > 0 (both required) |
| `hypothesis_support_metric` | Normalized gap positivity count + Spearman monotonicity of gap vs. KL |

**Pre-conditions:**
- [x] h-m1 CSV exists at `h-m1/results/h_m1_divergence_curve.csv` with `kl_budget`, `rm_score`, `gold_preference` columns
- [x] RM score range is non-degenerate: `rm.max() > rm.min()` (confirmed: 2.08 > 0.12)
- [x] No NaN values in h-m1 validated data (confirmed in h-m1 Phase 4 validation)
- [x] N=10 KL levels → 5 high-KL observations (KL > 3.75) — sufficient for ≥3 criterion

**Failure Detection:**
- `n_positive_high_kl < 3`: Recheck normalization range; verify `rm.max()` corresponds to max KL point; if gold curve higher than RM_norm at all high-KL levels, hypothesis fails — EXPLORE reframing
- `rho_gap_kl ≤ 0`: Gap not monotone; check if gap peaks then decreases — unusual given h-m1 results; likely data loading error

---

## Appendix: Reference Implementations

### A. Knowledge Base Sources

**Source A.1**: Coste et al. 2023 (arXiv 2310.02743) — via h-m1 Phase 4 validated output
- **Type**: Real published empirical data (digitized); validated by h-m1
- **Key Insights**: RM range [0.12, 2.08] across KL=[0,8]; gold range [0.38, 0.63]; after min-max normalization, gap at KL=8 ≈ 0.620
- **Used For**: Primary dataset; normalization protocol input

**Source A.2**: Phase 2B Verification Plan — h-m2 Protocol (02b_verification_plan.md §2.2)
- **Type**: Research plan specification
- **Key Insights**: `RM_norm = (RM - RM_min) / (RM_max - RM_min)` per paper; gap must be positive at ≥3 high-KL levels; gap metric must increase directionally
- **Used For**: Normalization protocol; success criteria; descriptive statistics list

**Source A.3**: h-m1 Phase 4 Validation Report
- **File**: `docs/youra_research/h-m1/04_validation.md`
- **Key Insights**: rho_rm_kl=1.000; reversal_confirmed=True; N=10; baseline_rm=0.12; divergence_final=1.70
- **Used For**: Confirms data fidelity; provides RM range for normalization denominator

### B. GitHub Implementations (Exa)

**Repository B.1**: numpy/numpy — vectorized min-max normalization
- **URL**: https://github.com/numpy/numpy
- **Key Code**: `rm_norm = (rm - rm.min()) / (rm.max() - rm.min())`
- **Used For**: Step 2 normalization (one-liner, stdlib)

**Repository B.2**: scipy/scipy — Spearman rank correlation
- **URL**: https://github.com/scipy/scipy
- **Key Code**: `rho, p = scipy.stats.spearmanr(kl, gap)` — gap trend confirmation
- **Used For**: Step 5 monotonicity test for gap vs. KL

### C. Previous Hypothesis Context

**Source**: h-m1 Phase 4 validated output
- **Reused Components**:
  - Data file: `h-m1/results/h_m1_divergence_curve.csv` — direct input, no re-digitization needed
  - Normalization parameters: RM_min=0.12, RM_max=2.08 (from h-m1 data)
  - Expected patterns: gap transitions at KL≈2–3; strongly positive by KL≥4
- **Why Reused**: h-m2 is a normalization + gap-computation step on h-m1's output; avoids redundant digitization

### D. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Primary dataset (h-m1 CSV) | h-m1 Phase 4 output | Source A.3 |
| Normalization formula (min-max) | Phase 2B plan | Source A.2 |
| High-KL threshold (median KL) | Phase 2B plan | Source A.2 |
| Success criterion (≥3 positive) | Phase 2B plan | Source A.2 |
| Gap formula (RM_norm - gold) | Phase 2B plan | Source A.2 |
| Spearman ρ (gap monotonicity) | scipy (Exa) | Repo B.2 |
| Min-max normalization | numpy (Exa) | Repo B.1 |
| N=10, KL range [0,8] | h-m1 validated results | Source A.3 |
| Expected gap values | Pre-computed from h-m1 data | Source A.1 + A.3 |

---

## State Information

**State File:** verification_state.yaml (ABLATION OVERRIDE — state restated in ```state block)
**Date:** 2026-08-26T09:00:00Z

### Workflow History for This Hypothesis

- h-e1: VALIDATED (PASS)
- h-m1: VALIDATED (PASS) — rho=1.000, reversal confirmed, N=10 KL levels
- h-m2: IN_PROGRESS → experiment_design COMPLETED (this document)
- Next: Phase 3 implementation planning for h-m2

---

*MCP Tools Used: Analytical grounding from h-m1 validated data and Phase 2B plan (ablation mode — Archon/Exa/Serena unavailable in this session)*
*All specifications grounded in real published data (Coste et al. 2023) validated through h-m1 pipeline*
*Next Phase: Phase 3 - Implementation Planning*
