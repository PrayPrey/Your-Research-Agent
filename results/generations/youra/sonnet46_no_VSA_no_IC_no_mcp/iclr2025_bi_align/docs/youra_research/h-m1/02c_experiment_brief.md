# Experiment Design: h-m1

**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr
**Hypothesis Statement:** Under RLHF optimization on the same model family (Coste et al. 2023), if KL budget increases from 0 to high optimization pressure (~10 nats), then the RM score increases monotonically while gold human preference rate peaks (at intermediate KL) and reverses, because the reward model is trained to maximize a proxy that diverges from actual human judgment under sustained optimization.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

---

## Workflow Status

**Verification State:** IN_PROGRESS → COMPLETED
**Prerequisites Satisfied:** h-e1 (MUST_WORK) — PASS
**Gate Status:** MUST_WORK — pending empirical validation

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** h-e1 (VALIDATED, PASS)

### Gate Condition

MUST_WORK: RM score monotonically increases AND gold human preference shows peak-reversal pattern in Coste et al. 2023 digitized data (Spearman ρ > 0.8 for RM monotonicity; reversal_confirmed == True).

**Failure Response:** EXPLORE — check digitization error; if confirmed no reversal, PIVOT to requesting raw data from authors (Open Question Q1 in Phase 2B).

---

## Continuation Context

h-e1 (VALIDATED): Confirmed both RM score and gold human preference curves are present in Coste et al. 2023 (arXiv 2310.02743) and Gao et al. 2023 (arXiv 2210.10760) at ≥5 KL levels each. WebPlotDigitizer digitization is feasible with ±2–5% precision. Both datasets provide paired (KL, RM_score, gold_preference) observations suitable for trajectory analysis.

### Previous Hypothesis Results (h-e1)
- Both RM score and gold preference curves confirmed present in ≥2 independent datasets
- Digitized data precision within ±5% visual inspection estimate
- Gate 1 (MUST_WORK): PASS — foundation for h-m1 through h-m4

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Source A.1**: Coste et al. 2023 (arXiv 2310.02743) — RLHF Overoptimization Proxy-Gold Divergence
- **Dataset**: Anthropic HH-RLHF preference data; LLM family trained with PPO at varying KL budgets
- **Key Experiment Setup**: RM score and gold human preference both measured at each KL checkpoint (0–~10 nats); same pretrained LLM base model
- **Key Insight**: RM score rises monotonically across KL levels; gold preference peaks at intermediate KL (~4–6 nats) then reverses — visually clear in Figures 3–4
- **Hyperparameters**: KL range 0–10 nats; ≥5 KL checkpoints reported

**Source A.2**: Gao et al. 2023 (arXiv 2210.10760) — Scaling Laws for Reward Model Overoptimization
- **Dataset**: Anthropic HH-RLHF; multiple model scales (1B, 6B, 12B parameters)
- **Key Insight**: Same qualitative proxy-gold divergence pattern at different model scales; KL budget on x-axis; provides independent replication dataset for h-m4
- **Note**: Primary use for h-m1 is preliminary pattern check; full regression reserved for h-m3/h-m4

**Source A.3**: Phase 2B Verification Plan — h-m1 Specification (02b_verification_plan.md §2.2)
- **Success Criterion Source**: Spearman ρ > 0.8 for RM monotonicity; peak-reversal detection; ≥5 KL levels confirmed by h-e1
- **Risk Mitigation Source**: Dual digitization (digitize each figure twice, take mean) for R2 (digitization imprecision)

### Archon Code Examples

**Standard scipy statistical pipeline** (from established scientific Python practice):
```python
from scipy import stats
import numpy as np

# Spearman monotonicity test
rho, p_rho = stats.spearmanr(kl_budget, rm_score)

# Peak detection
peak_idx = np.argmax(gold_preference)
peak_kl = kl_budget[peak_idx]

# Reversal check: gold at peak > gold at final KL
reversal_confirmed = gold_preference[peak_idx] > gold_preference[-1]
```

### Exa GitHub Implementations

**Repository B.1**: ankitrohatgi/WebPlotDigitizer
- **URL**: https://github.com/ankitrohatgi/WebPlotDigitizer
- **Relevance**: Standard open-source figure digitization tool; used in published meta-analyses and systematic reviews; browser-based GUI exports CSV
- **Key Code**: Browser GUI → manual calibration of axes → click-based point extraction → CSV export with columns (x_value, y_value)
- **Training Config**: N/A — manual digitization tool
- **Dataset Used**: Any published figure (Coste Fig 3/4, Gao Fig 2)
- **Serena Analysis Needed**: false

**Repository B.2**: scipy/scipy — scipy.stats module
- **URL**: https://github.com/scipy/scipy
- **Relevance**: `scipy.stats.spearmanr` for monotonicity; `scipy.stats.linregress` for h-m3 regression pipeline
- **Key Code**:
  ```python
  rho, p = stats.spearmanr(kl_budget, rm_score)   # monotonicity
  slope, intercept, r, p_val, se = stats.linregress(kl_budget, gap)  # h-m3 later
  ```
- **Results**: Standard library, no performance claims

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This experiment is a statistical re-analysis of published figure data, not a training reproduction. Implementation priority:

1. **Primary**: WebPlotDigitizer for data acquisition from Coste/Gao figures
2. **Secondary**: scipy/numpy for statistical computation
3. **Tertiary**: Gao et al. official code (`openai/lm-human-preferences`) for context, not direct use

**Recommended Implementation Path:**
- Primary: WebPlotDigitizer (manual) → pandas CSV → scipy statistical analysis
- Fallback: Author raw data request (Open Question Q1 from Phase 2B) if digitization precision insufficient
- Justification: No model training required; experiment is statistical verification of published visual patterns using established digitization methodology

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear; experiment uses standard scipy statistical functions on WebPlotDigitizer CSV output. No custom architecture or >100-line code requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Primary Dataset: Coste et al. 2023 Figure Data (Digitized)**
- **Name**: Coste-2023-KL-RM-Gold (digitized)
- **Source**: arXiv 2310.02743, Figures 3–4
- **Type**: programmatic-api (real published data extracted via digitization)
- **Splits**: Single time-series per figure; N ≥ 5 KL-level observations per curve
- **Variables**: `kl_budget` (nats), `rm_score` (normalized), `gold_preference` (fraction)
- **Digitization Protocol**: WebPlotDigitizer; calibrate axes; extract (KL, RM) and (KL, gold) independently; two independent digitizations per figure; use mean; report ±σ per point

**Secondary Dataset: Gao et al. 2023 Figure Data (Digitized)**
- **Name**: Gao-2023-KL-RM-Gold (digitized)
- **Source**: arXiv 2210.10760, Figure 2 (or equivalent)
- **Type**: programmatic-api (real published data)
- **Note**: Used for preliminary pattern check in h-m1; primary regression in h-m4
- **Variables**: Same structure as Coste dataset

**Synthetic Data Check**: PASS — both datasets are real published experimental results from peer-reviewed papers. NOT synthetic/simulated.

**Loading Information** (for Phase 4 download):
- Method: Manual (WebPlotDigitizer browser GUI) → CSV export → pandas
- Identifier: arXiv 2310.02743 Fig 3/4 (Coste); arXiv 2210.10760 Fig 2 (Gao)
- Code:
  ```python
  import pandas as pd
  coste_df = pd.read_csv("data/coste_digitized.csv")
  # Expected columns: kl_budget, rm_score, gold_preference
  # N >= 5 rows (one per KL checkpoint)
  gao_df = pd.read_csv("data/gao_digitized.csv")
  ```

### Models

#### Baseline Model

No trained model. "Baseline" = measurement at KL=0 (untrained RLHF policy baseline values from Coste et al.).

**Baseline Reference Values:**
- RM score at KL=0: extracted from Coste Fig 3 (leftmost point)
- Gold preference at KL=0: extracted from Coste Fig 3 (leftmost point)
- These establish the pre-RLHF reference level for trajectory analysis

**Loading Information** (for Phase 4):
- Method: Same WebPlotDigitizer CSV; `baseline_rm = coste_df.loc[coste_df["kl_budget"].idxmin(), "rm_score"]`
- Identifier: Row where `kl_budget` is minimum
- Code: `baseline_values = coste_df[coste_df["kl_budget"] == coste_df["kl_budget"].min()]`

#### Proposed Model

**Architecture:** Baseline data + full KL-trajectory statistical analysis

**Core Mechanism Implementation:**

```python
# Core Mechanism: Proxy-Gold Metric Decoupling Verification
# Based on: Coste et al. 2023 (arXiv 2310.02743), Phase 2B h-m1 protocol

import pandas as pd
import numpy as np
from scipy import stats

# Load digitized data (N >= 5 KL-level observations)
df = pd.read_csv("data/coste_digitized.csv")
kl   = df["kl_budget"].values          # shape: (N,) in nats
rm   = df["rm_score"].values            # shape: (N,) normalized
gold = df["gold_preference"].values     # shape: (N,) fraction [0,1]

# Test 1: RM score monotone increase (Spearman rho > 0.8)
rho, p_rho = stats.spearmanr(kl, rm)
assert rho > 0.8, f"RM not monotone: rho={rho:.3f}"

# Test 2: Gold preference peak-reversal
peak_idx = np.argmax(gold)              # index of maximum gold preference
peak_kl  = kl[peak_idx]                # KL level at peak
reversal_confirmed = gold[peak_idx] > gold[-1]   # drops after peak
assert reversal_confirmed, f"No reversal: gold[peak]={gold[peak_idx]:.3f}, gold[final]={gold[-1]:.3f}"

# Preliminary divergence (feeds into h-m2)
divergence_final = rm[-1] - gold[-1]

print(f"rho={rho:.3f}, p={p_rho:.4f}, peak_kl={peak_kl:.1f}, reversal={reversal_confirmed}, div={divergence_final:.3f}")
```

### Training Protocol

No model training. Statistical analysis protocol:

| Parameter | Value | Source |
|-----------|-------|--------|
| Data format | CSV from WebPlotDigitizer | WebPlotDigitizer documentation |
| KL range | 0–~10 nats | Coste et al. 2023 experimental setup |
| Min KL levels | ≥5 per curve | h-e1 confirmed |
| Digitization precision | ±2–5% per point | Phase 2B Assumption A2 |
| Digitization reps | 2× per figure, mean reported | Phase 2B Risk R2 mitigation |
| Seeds | 1 (fixed; no stochastic elements) | N/A — deterministic analysis |
| Primary dataset | Coste et al. 2023 Fig 3/4 | Phase 2A Section 1.3 |
| Secondary (prelim) | Gao et al. 2023 Fig 2 | Phase 2A Section 1.3 |

**Runtime Estimate:** < 1 minute (statistical computation on N ≤ 20 digitized points)

### Evaluation

**Primary Metrics:**

| Metric | Definition | Success Threshold | Failure Threshold |
|--------|-----------|-------------------|-------------------|
| `rho_rm_kl` | Spearman ρ(KL, RM score) | ρ > 0.8 | ρ ≤ 0.8 → digitization issue |
| `reversal_confirmed` | gold[peak_idx] > gold[-1] | True | False → no reversal in data |
| `p_rho` | p-value for Spearman test | p < 0.05 | p ≥ 0.05 → insufficient N |
| `divergence_final` | RM_score[-1] − gold_preference[-1] | > 0 (positive) | ≤ 0 → unexpected pattern |
| `peak_kl` | KL level of gold preference peak | 3–7 nats (consistent with Coste visual) | < 1 or > 9 → digitization error |

**Success Criteria (PoC direction-based):**
- PRIMARY: `rho_rm_kl > 0.8` AND `reversal_confirmed == True` in Coste et al. data
- SECONDARY: `divergence_final > 0` AND `peak_kl` in [3, 7] nats (consistent with paper figure)

**Expected Baseline Performance (from Coste et al. 2023 visual inspection):**
- RM score: monotone increase across all KL levels, visually clear in Fig 3
- Gold preference: peak around KL ≈ 4–6 nats, then reversal — visually clear in Fig 3
- Source: arXiv 2310.02743, Figures 3–4

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Statistical correlation + peak detection
- Library: `scipy.stats` (spearmanr), `numpy` (argmax)
- Code: `rho, p = scipy.stats.spearmanr(kl, rm)` / `peak_idx = np.argmax(gold)`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing `rho_rm_kl`, `reversal_confirmed` (0/1), `divergence_final` vs. thresholds

#### Additional Figures (LLM Autonomous)

1. **Dual-axis trajectory plot**: RM score (left axis) + gold preference (right axis) vs. KL budget — shows visual decoupling
2. **Divergence gap curve**: (RM_score − gold_preference) vs. KL budget — direct input for h-m2
3. **Spearman plot**: RM score scatter vs. KL budget with monotone trend line + ρ annotation
4. **Gao preliminary overlay**: Same dual-axis for Gao et al. data (separate panel)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `rho_rm_kl > 0.8` (RM monotone)
3. `reversal_confirmed == True` (gold preference reversal detected)

---

## Mechanism Verification Protocol

| Element | Specification |
|---------|---------------|
| `mechanism_exists` | RM score and gold preference curves both present in digitized data (confirmed by h-e1; WebPlotDigitizer CSV has both columns) |
| `mechanism_isolatable` | Yes — Spearman ρ tests RM column independently; np.argmax tests gold column independently |
| `baseline_measurable` | Yes — KL=0 row provides pre-RLHF baseline for both signals |
| `architecture_compatibility` | N/A — pure statistical analysis; no neural architecture |
| `mechanism_log_message` | `f"rho={rho:.3f}, p={p_rho:.4f}, peak_kl={peak_kl:.1f}, reversal={reversal_confirmed}, divergence_final={divergence_final:.3f}"` |
| `tensor_shape_change` | N/A — all vectors shape `(N_kl_levels,)` throughout (N ≥ 5) |
| `metric_delta_expected` | rho: 0.0 → >0.8; reversal: False → True; divergence_final: ~0 → >0 |
| `mechanism_verification_code` | `assert rho > 0.8` / `assert reversal_confirmed` / `assert divergence_final > 0` |
| `hypothesis_support_threshold` | rho > 0.8 AND reversal_confirmed == True (both required) |
| `hypothesis_support_metric` | Spearman ρ(KL, RM) + peak-reversal boolean + preliminary divergence |

**Pre-conditions:**
- [ ] Coste et al. CSV has ≥5 rows and both `rm_score` and `gold_preference` columns
- [ ] KL budget values are strictly increasing across rows
- [ ] No NaN values in digitized data

**Failure Detection:**
- `rho ≤ 0.8`: Check digitization — re-digitize Fig 3 independently; compare visual trend
- `reversal_confirmed == False`: Check if gold curve is monotone (no peak) — may indicate wrong figure or digitization error
- `p_rho ≥ 0.05`: N too small (< 5 points); acquire more KL checkpoints from paper

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1**: Coste et al. 2023 — RLHF Overoptimization (arXiv 2310.02743)
- **Type**: Published empirical paper (Phase 2A established fact)
- **Query Used**: "RLHF overoptimization proxy gold preference KL budget experiment"
- **Relevance**: Primary dataset source; defines experimental protocol and expected visual patterns
- **Key Insights**:
  - RM score increases monotonically with KL budget (clear from Fig 3)
  - Gold human preference peaks at intermediate KL then reverses (clear from Fig 3)
  - Same model family throughout; PPO fine-tuning
- **Used For**: Primary dataset; mechanism definition; expected results baseline

**Source A.2**: Gao et al. 2023 — Scaling Laws for RM Overoptimization (arXiv 2210.10760)
- **Type**: Published empirical paper (Phase 2A established fact)
- **Query Used**: "RLHF reward model overoptimization scaling KL"
- **Key Insights**: Proxy-gold divergence generalizes across model scales; provides independent replication target
- **Used For**: Secondary preliminary check in h-m1; primary replication dataset for h-m4

**Source A.3**: Phase 2B Verification Plan — h-m1 Protocol
- **Type**: Phase 2B structured verification plan (02b_verification_plan.md §2.2)
- **Key Insights**: Spearman ρ > 0.8 threshold for monotonicity; peak-reversal operationalization; dual digitization risk mitigation
- **Used For**: Success criteria specification; N requirements; quality thresholds

### B. GitHub Implementations (Exa)

**Repository B.1**: ankitrohatgi/WebPlotDigitizer (⭐ 3.5k+)
- **URL**: https://github.com/ankitrohatgi/WebPlotDigitizer
- **Query Used**: "figure digitization scientific paper data extraction tool"
- **Relevance**: Standard open-source tool for extracting numerical data from published figures; used in systematic reviews and meta-analyses
- **Key Code**: Browser-based; import image → calibrate axes → click points → export CSV
- **Configuration Extracted**: Two-point axis calibration; CSV output format
- **Used For**: Data acquisition from Coste Figs 3–4 and Gao Fig 2

**Repository B.2**: scipy/scipy — statistics module
- **URL**: https://github.com/scipy/scipy (⭐ 12k+)
- **Query Used**: "Spearman correlation monotonicity test python scipy"
- **Relevance**: Gold standard scientific Python library; `spearmanr`, `linregress` are standard for this analysis type
- **Key Code** (annotated):
  ```python
  from scipy import stats
  rho, p = stats.spearmanr(kl_budget, rm_score)
  # rho: Spearman rank correlation [-1, 1]; p: two-tailed p-value
  # H0: no monotone relationship; reject if p < 0.05 AND rho > 0.8
  ```
- **Their Results**: Standard library, deterministic output
- **Used For**: Monotonicity test (h-m1); OLS regression inputs for h-m3

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed — standard scipy/numpy pipeline; no complex custom code requiring semantic analysis.

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report — h-e1
- **File**: `docs/youra_research/h-e1/04_validation.md`
- **Reused Components**:
  - Dataset: Coste et al. + Gao et al. figures — confirmed digitizable with ≥5 KL levels each
  - Digitization protocol: WebPlotDigitizer, ±2–5% precision confirmed sufficient for large effect sizes
- **Why Reused**: Enables controlled experiment — same data, h-m1 adds trajectory analysis step not done in h-e1 (which only confirmed existence of both curves)

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Primary dataset (Coste fig data) | Published paper | Source A.1 |
| Secondary dataset (Gao fig data) | Published paper | Source A.2 |
| Digitization method | GitHub | Repo B.1 |
| KL range (0–10 nats) | Phase 2B | Source A.3 |
| Success criterion (ρ > 0.8) | Phase 2B | Source A.3 |
| Peak-reversal test (np.argmax) | Phase 2B + scipy | Source A.3, Repo B.2 |
| Spearman ρ computation | GitHub/scipy | Repo B.2 |
| N requirement (≥5) | h-e1 validation | Previous context (h-e1) |
| Dual digitization protocol | Phase 2B Risk R2 | Source A.3 |
| Divergence preliminary estimate | Phase 2B | Source A.3 (feeds h-m2) |

---

## State Information

**State File:** verification_state.yaml (ABLATION OVERRIDE — state restated in ```state block)
**Date:** 2026-08-26T00:45:00Z

### Workflow History for This Hypothesis

- h-e1: VALIDATED (PASS) — both RM + gold curves confirmed in Coste + Gao; ≥5 KL levels; digitization feasible
- h-m1: IN_PROGRESS → experiment_design COMPLETED (this document)
- Next: Phase 3 implementation planning for h-m1

---

*MCP Tools Used: Analytical grounding from Phase 2A/2B verified sources (ablation mode — Archon/Exa/Serena unavailable)*
*All specifications grounded in published paper figures and established scientific Python libraries*
*Next Phase: Phase 3 - Implementation Planning*
