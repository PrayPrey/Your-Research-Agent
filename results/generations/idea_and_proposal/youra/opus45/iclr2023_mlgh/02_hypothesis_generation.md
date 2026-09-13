# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-SCE-SisterRegion-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under conditions of data scarcity at pandemic outbreak onset, if Socioeconomic Context Embeddings (SCE) are pre-trained on census/ACS data and combined with multi-criteria sister-region transfer learning, then pandemic outcome predictions (cases, hospitalizations, deaths) will be significantly more accurate than models using raw socioeconomic features, because SCE captures transferable community vulnerability profiles that enable knowledge transfer from data-rich to data-sparse regions.

**Alternative Hypothesis (H0):**
Pre-trained Socioeconomic Context Embeddings with sister-region transfer provide no statistically significant improvement over models using raw socioeconomic features or clinical-only baselines for pandemic outcome prediction.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| SCE Integration | Independent | Binary: SCE-enhanced model vs. raw feature baseline; embedding dimension (64-256), fusion method (concatenation vs. attention) | Embedding dim: 128 (default), Fusion: cross-attention preferred |
| Sister-Region Transfer | Independent | Multi-criteria matching: socioeconomic similarity (cosine distance), geographic proximity (km), healthcare infrastructure similarity (beds/capita); k=5-20 similar regions | k=10 (default), weighted matching |
| Prediction Accuracy | Dependent | RMSE and MAPE for 7/14/21-day forecasts of cases, hospitalizations, deaths at county/tract level | MAPE: 15-30% baseline, target <20% |
| Equity Performance | Dependent | Performance parity across demographic subgroups (income quintiles, racial composition); max performance gap | Gap target: <5% between subgroups |
| Clinical Features | Controlled | Standardized epidemiological inputs: case counts, test positivity, hospitalization rates; fixed temporal window | 14-day lookback window |
| Geographic Granularity | Controlled | County or census tract level; fixed across comparisons | County-level primary |

### 1.3 Causal Mechanism

**3-Step Causal Chain:**

```
Step 1: Pre-training SCE on Census Data
    ↓ (Contrastive learning encodes SDOH structure)
Step 2: Sister-Region Matching
    ↓ (Multi-criteria identification of analogous regions)
Step 3: Attention-Based Fusion
    ↓ (Context-appropriate SDOH weighting)
Outcome: Improved Pandemic Predictions
```

**Detailed Mechanism:**

1. **Step 1 → Step 2:** Pre-trained SCE embeddings capture community vulnerability structure from census/ACS data. Contrastive learning objective forces socioeconomically similar communities to cluster in embedding space. This enables semantic similarity computation for sister-region identification.

2. **Step 2 → Step 3:** Sister-region matching uses multi-criteria similarity (socioeconomic profile via SCE distance + geographic proximity + healthcare infrastructure) to identify k most analogous regions. Knowledge from data-rich sister regions (epidemic curves, intervention responses) transfers to inform predictions for data-sparse target regions.

3. **Step 3 → Outcome:** Cross-attention mechanism fuses SCE representations with clinical/epidemiological features. Attention weights learn context-appropriate influence of socioeconomic factors based on outbreak phase, local conditions, and data availability.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Kagho & Pougala (2025) | Spatial embeddings + socioeconomic features reduce prediction uncertainty vs. traditional features alone | Strong |
| Step 1 → Step 2 | Santosh (2020) | 6 unexploited SDOH factors available in census data directly impact COVID-19 outcomes | Strong |
| Step 2 → Step 3 | Kagho & Pougala (2025) | Sister-region paradigm successfully transfers behavioral patterns between geographically distant but similar regions | Medium |
| Step 3 → Outcome | Hashtarkhani et al. (2024) | Multi-source data integration (clinical + socioeconomic + geographic) with XAI improves health outcome prediction | Strong |

**Key Tension:**
- **Tension:** Kagho & Pougala (2025) demonstrate sister-region transfer for activity/behavioral patterns, but disease dynamics may be influenced by unmeasured biological and intervention factors not captured in socioeconomic profiles.
- **Resolution:** Phase 2B will explicitly test whether socioeconomic similarity correlates with disease dynamic similarity by comparing sister-region-based predictions against geographic-only and random-region transfers.

### 1.4 Key Assumptions

1. **Census/ACS data adequately captures SDOH at tract/county level**
   - Evidence: Santosh (2020) identifies 6 key factors in public census data
   - Consequence if violated: SCE embeddings will fail to capture disease-relevant structure → Step 1 breaks

2. **Socioeconomically similar regions exhibit similar disease dynamics**
   - Evidence: Kagho & Pougala (2025) sister-region behavioral prediction success
   - Consequence if violated: Knowledge transfer produces misleading predictions → Step 2 breaks

3. **Contrastive learning can encode meaningful socioeconomic structure**
   - Evidence: Established in NLP/vision; Hashtarkhani (2024) multi-source integration
   - Consequence if violated: Embeddings no better than raw features → Step 1 breaks

4. **Monthly employment/mobility data captures temporal dynamics**
   - Evidence: High-frequency economic indicators track pandemic impacts
   - Consequence if violated: Static embeddings become stale during outbreak → temporal degradation

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Pandemic outcome prediction at county/census tract level
- US context with available census/ACS data
- Data-sparse outbreak onset conditions (first 2-4 weeks)
- Respiratory disease pandemics with socioeconomic exposure gradients

**Where Hypothesis Does NOT Apply:**
- Individual-level clinical predictions
- Non-US contexts without equivalent census infrastructure
- Diseases without socioeconomic exposure gradients (e.g., genetic conditions)
- Long-term endemic prediction (where local data becomes abundant)

**Known Limitations:**
- Ecological fallacy risk: tract-level predictions don't imply individual outcomes
- Privacy considerations: detailed socioeconomic data requires careful handling
- Census data latency: annual/decennial updates may miss rapid demographic shifts
- Adaptation required for different healthcare systems and data availability

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Accuracy vs. Baselines):**
SCE-enhanced model with sister-region transfer will achieve MAPE < 20% for 14-day case forecasts, representing >15% relative improvement over raw-feature baselines (expected MAPE 25-30%).

*Measurement*:
- MAPE < 20% with p < 0.05 (paired t-test vs. baseline)
- Statistical test: Paired t-test, n ≥ 25 counties with varying data availability
- Baseline: LSTM with raw socioeconomic features, COVID Forecast Hub ensemble

*Success Criteria for Phase 2B*:
- Primary: MAPE < 20% with significant improvement (p < 0.05)
- Falsification: MAPE ≥ 25% (no improvement over baselines)

**Secondary Predictions:**

**P2 (Sister-Region Transfer Validity):**
Predictions using sister-region transfer will outperform geographic-proximity-only transfer by >5% MAPE reduction, validating that socioeconomic similarity matters beyond physical proximity.

**P3 (Equity Performance):**
Performance gap between highest and lowest income quintile counties will be <5% MAPE, demonstrating equitable prediction across socioeconomic strata (vs. typical 10-15% gap in baseline models).

**Falsification Criteria:**
The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure:** MAPE ≥ 25% (no improvement over baselines)
2. **Mechanism Failure:** Sister-region transfer performs equal to or worse than random-region transfer
3. **Fusion Failure:** Attention weights show no meaningful variation (SCE ignored by model)
4. **Equity Failure:** Performance gap between demographic subgroups exceeds baseline gaps

### 1.7 SOTA Baseline (Optional)

*Not applicable - targeting absolute performance improvement.*

**Reference Baselines:**
- COVID Forecast Hub ensemble: MAPE 25-35%
- LSTM with raw features: MAPE 30-40%
- XGBoost with socioeconomic features: MAPE 25-35%

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 25 counties, effect size d=0.6, power=0.8
**Statistical Test:** Paired t-test, α=0.05 (one-tailed)
**Report Format:** Mean MAPE difference, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Do pre-trained SCE embeddings capture meaningful socioeconomic structure that clusters similar communities?"
- Verification: Embedding visualization + cluster analysis
- Critical: MUST PASS for mechanism to operate

**SH2 (Mechanism):**
"Is sister-region transfer the actual mechanism enabling improved predictions?"
- Will decompose into 3 sub-hypotheses (H-M1 to H-M3):
  - H-M1: SCE pre-training captures SDOH structure
  - H-M2: Sister-region matching identifies valid analogues
  - H-M3: Attention fusion learns meaningful weights
- Verification: Ablation studies, causal analysis

**SH3 (Comparison):**
"Does SCE + sister-region outperform baselines?"
- Verification: Comparative empirical evaluation

**Total Sub-Hypotheses for Phase 2B:** 5 (SH1 + 3×SH2 + SH3)

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-SCE-SisterRegion-v1
- [x] Confidence level: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] All variables operationalized
- [x] Causal mechanism with evidence (3 steps)
- [x] Key tension identified with resolution
- [x] Assumptions with consequences
- [x] Testable predictions (3) with falsification criteria
- [x] Baselines identified (3)
- [x] SH1, SH2, SH3 defined

### Open Questions

1. **Data Availability:** Which COVID-19 outcome datasets (JHU, CDC, state health departments) have sufficient temporal granularity for validation?

2. **Sister-Region Validation:** How to validate epidemiological similarity beyond socioeconomic similarity?

3. **Dynamic Update Feasibility:** Can monthly employment/mobility data integrate with acceptable latency?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
