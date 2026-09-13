# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-TSFM-KnowledgeAttribution-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under conditions where time series forecasting tasks vary in contextual richness (semantic content) and temporal complexity, if we apply probing classifiers to measure semantic vs temporal information content in TSFM intermediate representations, then we can predict which model type (LLM-adapted vs native TSFM) will perform better, because the relative information content reflects the knowledge type that each architecture captures more effectively.

**Alternative Hypothesis (H0):**
There is no systematic relationship between the semantic-to-temporal information ratio in TSFM representations and model type performance advantage. Model selection based on probing analysis performs no better than random selection.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Semantic Information Content | Independent | Linear probe accuracy on predicting metadata, domain context, textual descriptions from intermediate representations | 0.0 - 1.0 (accuracy) |
| Temporal Information Content | Independent | Linear probe accuracy on predicting next-step values, periodicity patterns, trend direction from intermediate representations | 0.0 - 1.0 (accuracy) |
| Task Context Richness | Independent | Metadata completeness score: availability of domain descriptors, textual labels, cross-domain signals | 0-100% completeness |
| Model Selection Accuracy | Dependent | Percentage of correct predictions where recommended model type achieves lower forecasting error | Target: >65% (vs 50% random) |
| Forecasting Performance | Dependent | MSE, MAE, CRPS metrics on held-out test sets | Domain-dependent baselines |
| Model Parameter Count | Controlled | Compare models of similar parameter counts (Chronos-Base ~200M vs Time-LlaMA-7B-LoRA ~300M effective) | Fixed per experiment |
| Training Data Size | Controlled | Same training data split across all evaluations | Fixed per benchmark |
| Evaluation Protocol | Controlled | Standardized zero-shot evaluation on public benchmarks (Monash, FinTSB, GIFT-Eval) | Fixed protocol |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Probing Analysis
    ↓ (Linear probes extract information from TSFM representations)
Step 2: Information Quantification
    ↓ (MI estimation reveals semantic vs temporal content)
Step 3: Knowledge Type Characterization
    ↓ (Ratio determines model recommendation)
Outcome: Model Selection Prediction
```

**Step 1 → Step 2: Probing Analysis → Information Quantification**
- Mechanism: Train linear probes on intermediate representations to predict semantic features (metadata) vs temporal features (patterns)
- Evidence: Choi et al. 2023 (ICASSP 2024) connects linear probing to variational bounds of MI
- Falsification: Probe accuracy at chance level (<55%) indicates information cannot be extracted

**Step 2 → Step 3: Information Quantification → Knowledge Type Characterization**
- Mechanism: Compute I(representation; semantic_features) vs I(representation; temporal_features) using probe-based MI estimation
- Evidence: MI estimation provides theoretically grounded information measurement (Choi et al. 2023)
- Falsification: If MI estimates are unreliable or representations are entangled, characterization fails

**Step 3 → Outcome: Knowledge Type Characterization → Model Selection Prediction**
- Mechanism: High semantic-to-temporal ratio → recommend LLM-adapted model; Low ratio → recommend native TSFM
- Evidence: Riachi et al. 2025 shows LLMs bring unique transferable knowledge (non-vanishing gap)
- Falsification: Model selection accuracy ≤50% (no better than random)

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Choi et al. 2023 (ICASSP) | Linear probing connected to MI variational bounds | Strong |
| Step2 → Step3 | Belinkov & Glass 2019 | Probing reveals linguistic structure in representations | Strong |
| Step3 → Outcome | Riachi et al. 2025 | Non-vanishing transfer gap shows LLM knowledge transfers | Medium |

**Key Tension:**
- Tension: Choi et al. 2023 shows MI-probe connection for speech/language models, but time series representations may differ structurally from language representations
- Resolution: This verification plan tests whether the MI-probe connection holds for time series foundation models specifically

### 1.4 Key Assumptions

1. **Semantic-Temporal Separability:** Semantic and temporal information are approximately separable in TSFM representations
   - Evidence: NLP probing literature (Belinkov & Glass 2019) shows different linguistic properties are separable
   - Consequence if violated: Probing analysis produces mixed/uninformative signals; need to explore non-linear probes or disentanglement methods

2. **Linear Probe Sufficiency:** Linear probes can capture meaningful information content without overparameterization
   - Evidence: Choi et al. 2023 proves linear probing equals fine-tuning under MI framework
   - Consequence if violated: Must use more complex probes (MLP), increasing computational cost and risk of memorization

3. **Probe-Performance Correlation:** The relative probe accuracy ratio correlates with forecasting performance advantage
   - Evidence: Novel claim - requires empirical validation
   - Consequence if violated: Main hypothesis fails; need to explore alternative selection criteria

4. **Architecture-Knowledge Specialization:** LLM-adapted models encode more semantic information; native TSFMs encode more temporal information
   - Evidence: Riachi et al. 2025 shows LLMs bring transferable knowledge distinct from random init
   - Consequence if violated: Model architecture may not determine knowledge type; selection rule invalid

### 1.5 Scope & Boundaries

**Applies to:**
- Time series forecasting tasks with available contextual metadata (domain labels, textual descriptions)
- Domains with diverse context richness: finance (news + prices), healthcare (patient history + vitals), retail (product metadata + sales)
- Comparison between LLM-adapted TSFMs (Time-LlaMA, ChatTime) and native TSFMs (Chronos, Lag-Llama)

**Does NOT Apply to:**
- Purely numerical time series without any contextual metadata (e.g., synthetic benchmarks)
- Classification or anomaly detection tasks (forecasting focus only)
- Real-time streaming scenarios (batch evaluation assumed)

**Known Limitations:**
- Probe design requires validation for each new TSFM architecture
- MI estimation may not generalize equally to all representation dimensions
- Computational overhead of probing analysis (~10-20% of inference time)

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Model Selection Accuracy):**
The probing-based model selection framework will achieve model selection accuracy > 65% across diverse benchmarks.

*Measurement*:
- Model Selection Accuracy = (Correct recommendations / Total tasks) × 100%
- Correct = recommended model type achieves lower MSE than alternative
- Statistical test: One-sample t-test against 50% baseline, p < 0.05

*Basis*:
Random selection achieves 50%. A meaningful improvement requires >15% absolute gain.

*Success Criteria for Phase 2B*:
- Primary: Accuracy > 65% (p < 0.05)
- Falsification: Accuracy ≤ 55% (not significantly better than random)

**Secondary Predictions:**

**P2 (Semantic Probe Validation):**
If a task has high semantic probe accuracy (>70% on metadata prediction), then LLM-adapted models will outperform native TSFMs by >5% relative improvement on that task.

**P3 (Temporal Probe Validation):**
If a task has high temporal probe accuracy (>70% on pattern prediction), then native TSFMs will outperform LLM-adapted models by >5% relative improvement on that task.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure**: Model selection accuracy ≤ 55%
   (Not statistically better than random selection)

2. **Mechanism Failure**: Probes cannot distinguish semantic from temporal features
   (Both probe types achieve similar accuracy, difference < 10%)

3. **Prediction Failure**: P2 and P3 do not hold
   (High semantic probe does not predict LLM advantage; high temporal probe does not predict TSFM advantage)

### 1.7 SOTA Baseline (Optional)

*Not applicable - This research focuses on methodology development rather than SOTA performance comparison.*

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's h for proportions): 0.30 (65% vs 50%)
- Required sample size: n ≥ 88 task-model pairs
- Statistical power: 0.80

**Test Specification:**
- Primary: One-sample proportion test (H0: p = 0.50)
- Secondary: Paired comparisons within task groups
- Significance level: α = 0.05 (two-tailed)
- Report format: Selection accuracy %, 95% CI, p-value

**Experimental Design:**
- Benchmarks: Monash (diverse domains), FinTSB (financial), GIFT-Eval (general)
- Models: Chronos, Lag-Llama (native) vs Time-LlaMA, ChatTime (LLM-adapted)
- Probing: Linear probes trained on layer-wise representations
- Cross-validation: 5-fold for probe training, held-out test for model evaluation

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Can probing classifiers reliably distinguish semantic from temporal information in TSFM representations?"
- Verification: Train probes, measure accuracy gap between semantic and temporal prediction tasks
- Success: Accuracy gap > 10% indicates separable information types
- Priority: HIGHEST - Foundation for all subsequent hypotheses

**SH2 (Mechanism):**
"Is the probe-based knowledge characterization the actual mechanism for predicting model performance advantage?"
- Will decompose into 3 sub-hypotheses (H-M1 to H-M3):
  - H-M1: Probing → Information Quantification (probe reliability)
  - H-M2: Information Quantification → Knowledge Characterization (MI estimation validity)
  - H-M3: Knowledge Characterization → Model Selection (prediction accuracy)
- Verification: Causal analysis with ablations and mediator tests
- Priority: HIGH - Core mechanism validation

**SH3 (Comparison):**
"Does probing-based selection outperform baseline selection strategies?"
- Baselines: Random selection (50%), Always-LLM, Always-TSFM, Oracle (upper bound)
- Verification: Comparative evaluation on held-out tasks
- Success: Probing-based > 65% AND > all non-oracle baselines
- Priority: MEDIUM - Practical value demonstration

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-TSFM-KnowledgeAttribution-v1
- [x] Confidence level specified: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence (8 variables)
- [x] Causal mechanism has evidence at each step (N=3 steps, evidence table complete)
- [x] Causal chain length (N=3) determined and stored
- [x] Key tension identified: MI-probe connection tested on language, needs validation for time series
- [x] Key assumptions list consequences if violated (4 assumptions)
- [x] At least 2 testable predictions exist (3 predictions: P1 primary, P2, P3 secondary)
- [x] Falsification criteria are defined (3 criteria)
- [x] Baselines are identified for comparison (Chronos, Lag-Llama, Time-LlaMA, ChatTime)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Data Availability:** Do standard benchmarks (Monash, FinTSB) include sufficient metadata for semantic probing, or do we need to augment with external context?

2. **Probe Architecture:** Should we use single linear layer or shallow MLP (2 layers) for probes? Linear preferred for interpretability, but MLP may capture more information.

3. **Layer Selection:** Which TSFM layers should be probed? Early layers (low-level patterns) vs late layers (high-level semantics) may show different information profiles.

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-13*
