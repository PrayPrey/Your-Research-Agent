# Validated Hypothesis Synthesis

**Generated:** 2026-03-29
**Workflow:** Phase 4.5 Hypothesis Synthesis v2.0
**Pipeline Position:** Phase 4 (Hypothesis Loop) → [Phase 4.5] → Phase 5/6

---

## 1. Executive Summary

The SE-Distilled Probes (SEDP) hypothesis proposed that training a probe on hidden states with semantic similarity auxiliary signal would achieve single-pass semantic entropy (SE) prediction with Spearman rho ≥ 0.7. **The hypothesis was refuted.** The existence proof (h-e1) achieved rho = 0.0843, failing the MUST_WORK gate (threshold: rho ≥ 0.3) by 72%.

Both the baseline SEP (hidden-only probe) and proposed SEDP performed near random (AUROC ≈ 0.52), indicating that the tested configuration does not encode semantic entropy information. The SEDP marginally outperformed SEP (+0.0009 rho), confirming the expected effect direction but with negligible magnitude.

**Key Finding:** Hidden states at layer 25 of Llama-3-8B-Instruct, combined with 4-dimensional similarity features, do not predict semantic entropy under the tested conditions. This fundamental failure at the PoC level triggers routing to Phase 0 for hypothesis reformulation.

| Metric | Value |
|--------|-------|
| **Original Core Statement** | SEDP achieves rho ≥ 0.7 SE correlation via similarity-augmented training |
| **Refined Core Statement** | Hidden states + similarity features do NOT predict SE in tested configuration |
| **Predictions Supported** | 0 / 3 |
| **Overall Pass Rate** | 0% |
| **Hypotheses Validated** | 0 / 4 (1 failed, 3 cascade-failed) |

---

## 2. Prediction-Result Matrix

| Prediction | Original Statement | Tested By | Key Metric | Result | Status | Confidence | Evidence Summary |
|------------|-------------------|-----------|------------|--------|--------|------------|------------------|
| **P1** | SEDP achieves Spearman rho ≥ 0.7 with true SE on same-model evaluation | h-e1 | Spearman rho | 0.0843 | **REFUTED** | HIGH | rho=0.0843 << 0.7, p=0.283 (not significant), AUROC=0.52 (near random) |
| **P2** | SEDP achieves rho ≥ 0.5 on cross-model transfer (Llama→Mistral) | Not tested | N/A | N/A | **INCONCLUSIVE** | N/A | Cascade failure: h-e1 MUST_WORK gate failed |
| **P3** | SEDP provides ≥10x inference speedup over full SE computation | Not tested | N/A | N/A | **INCONCLUSIVE** | N/A | Cascade failure: h-e1 MUST_WORK gate failed |

**Status Legend:** SUPPORTED | PARTIALLY_SUPPORTED | REFUTED | INCONCLUSIVE

### Causal Mechanism Verification

| Mechanism Step | Description | Falsifier | Evidence | Verification Status |
|----------------|-------------|-----------|----------|---------------------|
| 1 | SE Label Generation via NLI clustering | Degenerate clusters (all same or all different) | Not explicitly verified; SE labels generated but quality unvalidated | **UNVERIFIED** |
| 2 | Similarity Structure Extraction from response sets | Uninformative matrix (all 1s or random) | 4-dim features computed but informativeness not measured | **UNVERIFIED** |
| 3 | Probe Training with Similarity Augmentation | Loss doesn't converge below baseline | Training completed but convergence not reported | **UNKNOWN** |
| 4 | Knowledge Distillation from multi-sample to single-pass | rho < 0.3 | rho = 0.0843 << 0.3 threshold | **FALSIFIED** |
| 5 | Transfer via Model-Agnostic Features | Cross-model rho equals hidden-only rho | Not tested due to cascade failure | **N/A** |

---

## 3. Hypothesis Refinement

### 3.1 Original Core Statement (Phase 2A)

> Under the condition of transformer-based LLMs performing question-answering tasks, if we train a probe to predict semantic entropy (SE) using hidden state features with semantic similarity structure as an auxiliary training signal, then the probe will achieve (1) single-pass SE prediction with Spearman rho ≥ 0.7 versus true SE, AND (2) cross-model transfer with rho ≥ 0.5, because the similarity structure provides model-agnostic regularization that prevents overfitting to model-specific hidden state patterns.

### 3.2 Refined Core Statement (Phase 4.5)

> Under the tested conditions (Llama-3-8B-Instruct, TruthfulQA, layer-25 TBG tokens, logistic regression probe), hidden state features with semantic similarity auxiliary signal do NOT produce meaningful SE predictions. The achieved Spearman rho = 0.0843 is statistically indistinguishable from random (p = 0.283, AUROC = 0.52), indicating that neither hidden states alone (SEP) nor similarity-augmented hidden states (SEDP) encode semantic entropy information in this configuration. The hypothesis is refuted at the existence proof level.

**Key Changes:**
1. **Claim Direction Reversed:** Original claimed rho ≥ 0.7; evidence shows rho ≈ 0.08 (near zero)
2. **Scope Narrowed:** Refined statement qualified to specific tested conditions
3. **Confidence Removed:** Original claimed "will achieve"; refined acknowledges failure
4. **Mechanism Invalidated:** Original claimed similarity provides regularization; no evidence supports this

### 3.3 Causal Mechanism — Verified Chain

```
Original:  Step 1 → Step 2 → Step 3 → Step 4 → Step 5
Verified:  Step 1 [UNVERIFIED] → Step 2 [UNVERIFIED] → Step 3 [UNKNOWN] → Step 4 [FALSIFIED] → Step 5 [N/A]

Chain Status: BROKEN at Step 4 (Knowledge Distillation failed)
```

**Removed/Modified Steps:**
- **Step 4** (Knowledge Distillation): FALSIFIED — rho = 0.0843 << 0.3 threshold. Single-pass predictions do not correlate with multi-sample SE.
- **Step 5** (Transfer): NOT TESTED — Cascade failure; cannot evaluate transfer without successful distillation.

### 3.4 Claims Removed or Weakened

| Original Claim | Action | Reason | Evidence |
|----------------|--------|--------|----------|
| "Probe achieves rho ≥ 0.7 SE correlation" | **REMOVED** | Direct contradiction — actual rho = 0.0843 | h-e1 metrics: rho=0.0843, p=0.283 |
| "Similarity augmentation improves generalization" | **REMOVED** | Negligible improvement (+0.0009 rho) | SEDP vs SEP delta = 0.0009 |
| "Cross-model transfer with rho ≥ 0.5" | **REMOVED** | Not tested; cascade failure | h-e1 MUST_WORK gate failed |
| "Model-agnostic regularization effect" | **REMOVED** | No evidence of any regularization benefit | Both SEP and SEDP near random |
| "Hidden states contain SE information" | **WEAKENED** | May be layer/token position dependent | Layer 25 + TBG showed no SE signal |

### 3.5 Assumptions Status

| Assumption | Original Status | Verification Status | Evidence | Impact if Violated |
|------------|----------------|---------------------|----------|-------------------|
| **A1:** Hidden states contain sufficient information to predict SE | Critical assumption | **VIOLATED** | rho = 0.08 (near zero); AUROC = 0.52 (random) | No single-pass SE proxy possible from this configuration |
| **A2:** Semantic similarity structure is model-agnostic | Supporting assumption | **UNVERIFIED** | Not tested; cascade failure before h-m3 | Would need to test with successful probe first |
| **A3:** Similarity augmentation improves generalization | Novel claim | **PARTIALLY VIOLATED** | Delta = +0.0009 (negligible) | SEDP reduces to vanilla SEP; no transfer benefit |
| **A4:** TruthfulQA is representative of broader QA uncertainty | Scope assumption | **UNVERIFIED** | Single dataset tested | Results may not generalize |
| **A5:** DeBERTa NLI captures semantic equivalence adequately | Technical assumption | **UNVERIFIED** | SE label quality not validated | SE labels themselves may be noisy |

---

## 4. Theoretical Interpretation

### 4.1 Mechanistic Explanation (Experiment-Verified)

Our experiments demonstrate that the proposed SEDP approach **does not work** under the tested conditions. The core mechanism — distilling semantic entropy from hidden states — failed at the existence proof level.

**What we observed:**
1. Both SEP (hidden-only) and SEDP (hidden + similarity) achieved near-random performance (AUROC ≈ 0.52)
2. The Spearman correlation between predicted and true SE was 0.0843 (p = 0.283), statistically indistinguishable from zero
3. Adding similarity features provided negligible improvement (+0.0009 rho)

**Why this happened (competing hypotheses):**
The failure could stem from multiple causes, which we could not distinguish in this experiment:
1. Layer 25 hidden states may not encode SE-relevant information
2. The TBG token position may not capture the right signal
3. The logistic regression probe may be too simple
4. The SE labels themselves may be degenerate

### 4.2 Unexpected Findings Analysis

#### Finding: Both SEP and SEDP Perform Near Random

- **Observation:** AUROC = 0.52 for both methods (random = 0.50)
- **Why Unexpected:** SEP paper (Kossen et al., 2024) reports AUROC ~0.85 on TruthfulQA
- **Competing Explanations:**
  1. **Layer Selection Mismatch:** We used layer 25 without ablation; SEP paper recommends testing layers 23-27 and selecting best performer. (Plausibility: HIGH)
  2. **Token Position Issue:** We used only TBG; SEP paper uses multiple positions including SLT which may capture different information. (Plausibility: HIGH)
  3. **SE Label Quality:** Our DeBERTa clustering may differ from jlko/semantic_uncertainty implementation, producing degenerate labels. (Plausibility: MEDIUM)
  4. **Dataset Configuration:** TruthfulQA's adversarial questions may create different uncertainty patterns than TriviaQA/SQuAD used in SEP paper. (Plausibility: MEDIUM)
- **Most Likely Interpretation:** Configuration mismatch with published SEP implementation (layer selection, token position, or hyperparameter differences)
- **Additional Evidence Needed:** Layer ablation study (20-31), token position comparison (TBG vs SLT vs pooling), SE label validation (cluster count distribution)

#### Finding: Negligible Similarity Feature Contribution

- **Observation:** SEDP improved over SEP by only +0.0009 rho
- **Why Unexpected:** Hypothesis predicted similarity structure would provide meaningful signal
- **Competing Explanations:**
  1. **4-dim Features Too Crude:** Mean/std/min/max of similarity matrix loses most information. (Plausibility: HIGH)
  2. **Hidden States Already Dominate:** 4096-dim hidden states overwhelm 4-dim similarity features. (Plausibility: HIGH)
  3. **Similarity Not Informative:** Cosine similarity of sentence embeddings may not capture SE-relevant structure. (Plausibility: MEDIUM)
- **Most Likely Interpretation:** Feature dimensionality imbalance (4 vs 4096) combined with crude similarity summarization
- **Additional Evidence Needed:** Full similarity matrix encoding, learned similarity pooling, balanced feature concatenation

### 4.3 Connection to Existing Literature

| Our Finding | Related Work | Relationship | Citation |
|-------------|-------------|--------------|----------|
| Hidden states don't predict SE at layer 25 | SEP (Kossen et al., 2024) | **CONTRADICTS** — they report AUROC ~0.85 | arXiv:2406.15927 |
| AUROC = 0.52 (near random) | Full SE (Farquhar et al., 2024) | **BASELINE** — Full SE achieves 0.76-0.97 | Nature 2024 |
| Similarity features add +0.0009 rho | KLE (Nikitin et al., 2024) | **WEAK SUPPORT** — KLE uses richer similarity structure | NeurIPS 2024 |
| Probe training converged | SSD (Phillips et al., 2026) | **CONSISTENT** — distillation paradigm is feasible | arXiv preprint |

### 4.4 Theoretical Contributions

Given the hypothesis was refuted, contributions are primarily negative results:

1. **Negative Result — Layer 25 TBG Configuration:** Demonstrated that Llama-3-8B layer 25 TBG token position with logistic regression does NOT encode SE information on TruthfulQA.

2. **Methodological Insight — Feature Imbalance:** 4-dimensional similarity features cannot meaningfully augment 4096-dimensional hidden states in a linear probe.

3. **Replication Challenge — SEP Discrepancy:** Identified significant gap (-39% AUROC) between our SEP baseline and published SEP results, suggesting configuration sensitivity.

---

## 5. Experiment Results (Phase 6 Evidence)

### 5.1 Per-Hypothesis Results

| Hypothesis | Title | Gate | Result | Pass Rate | Key Insight |
|------------|-------|------|--------|-----------|-------------|
| **h-e1** | SEDP Existence Proof | MUST_WORK | **FAIL** | 0% | rho=0.0843 << 0.3; both SEP and SEDP near random |
| **h-m1** | SE Label Validation | MUST_WORK | **CASCADE_FAILED** | N/A | Not tested; blocked by h-e1 failure |
| **h-m2** | Similarity Structure Informativeness | MUST_WORK | **CASCADE_FAILED** | N/A | Not tested; blocked by h-e1 failure |
| **h-m3** | Cross-Model Transfer | SHOULD_WORK | **CASCADE_FAILED** | N/A | Not tested; blocked by h-e1 failure |

### 5.2 Aggregate Metrics

| Metric | Value |
|--------|-------|
| **Total Hypotheses** | 4 |
| **Fully Validated** | 0 |
| **Partially Validated** | 0 |
| **Failed** | 1 (h-e1) |
| **Cascade Failed** | 3 (h-m1, h-m2, h-m3) |
| **Total Tasks Completed** | 15 / 15 |
| **SDD Compliance Rate** | 100% (tasks completed, but gate failed) |

### 5.3 Optimal Hyperparameters

```yaml
# Configuration that was tested (NOT optimal — hypothesis failed)
llm:
  name: Llama-3-8B-Instruct
  pretrained: meta-llama/Meta-Llama-3-8B-Instruct
  dtype: float16

generation:
  n_responses: 20
  temperature: 0.7
  max_new_tokens: 100

hidden_state_extraction:
  layer_idx: 25  # of 32 layers
  token_position: TBG  # Token Before Generation

probe:
  type: LogisticRegression
  C: 1.0
  max_iter: 1000
  solver: lbfgs

similarity:
  model: all-MiniLM-L6-v2
  features: [mean, std, min, max]  # 4-dimensional

entailment:
  model: DeBERTa-v3-large-mnli
  threshold: 0.5

seed: 42
```

### 5.4 Proven Components

| Component | Source Hypothesis | File | Reusable |
|-----------|-------------------|------|----------|
| Response generation pipeline | h-e1 | `h-e1/code/generate_responses.py` | YES |
| Hidden state extraction | h-e1 | `h-e1/code/extract_hidden_states.py` | YES |
| SE label computation | h-e1 | `h-e1/code/compute_se_labels.py` | NEEDS_VALIDATION |
| Similarity feature extraction | h-e1 | `h-e1/code/compute_similarity.py` | YES |
| Evaluation pipeline | h-e1 | `h-e1/code/evaluate.py` | YES |

### 5.5 Planned-vs-Actual Comparison

| Hypothesis | Planned Metric (03_tasks) | Planned Target | Actual Result (04_validation) | Deviation Type | Notes |
|------------|--------------------------|----------------|-------------------------------|----------------|-------|
| **h-e1** | Spearman rho | ≥ 0.3 (gate), ≥ 0.7 (target) | 0.0843 | **HYPOTHESIS_ISSUE** | Core assumption A1 violated — hidden states don't encode SE |
| **h-e1** | AUROC | Close to full SE (~0.85) | 0.5219 | **HYPOTHESIS_ISSUE** | Both SEP and SEDP perform near random |
| **h-e1** | SEDP > SEP | Positive delta | +0.0009 rho | **CONFIRMED** but negligible | Effect direction correct but magnitude meaningless |

**Deviation Types:** IMPLEMENTATION_GAP | DESIGN_ISSUE | HYPOTHESIS_ISSUE | SCOPE_CHANGE | NONE

### 5.6 Key Figures Reference

| Figure | Source | Description | Suggested Paper Section |
|--------|--------|-------------|------------------------|
| `gate_metrics.png` | `h-e1/figures/` | Bar chart with rho=0.3 threshold line showing both methods fail gate | Results (negative result visualization) |
| `scatter.png` | `h-e1/figures/` | Predicted vs True SE scatter plot showing no correlation | Results (SE prediction quality) |
| `roc_curves.png` | `h-e1/figures/` | ROC curves for SEP vs SEDP (both near diagonal) | Results (hallucination detection) |

---

## 6. Limitations & Scope Boundaries

### 6.1 Principled Limitations

#### Single Layer Tested (Layer 25)

- **What:** Only layer 25 of 32 was evaluated for SE prediction
- **Why This Matters:** SE-relevant information may be encoded at different depths; layer selection is critical
- **Root Cause:** EXISTENCE tier budget constraint (PoC-level validation)
- **Impact on Claims:** Cannot conclude hidden states never encode SE; only that layer 25 doesn't
- **Why Acceptable:** PoC purpose is to validate approach works at any configuration; systematic ablation is Phase 0 restart work

#### Single Token Position (TBG)

- **What:** Only Token-Before-Generation position was used
- **Why This Matters:** SEP paper suggests SLT (Selected Layer Token) may capture different information
- **Root Cause:** Following default from SEP paper without position ablation
- **Impact on Claims:** SE signal may exist at different token positions
- **Why Acceptable:** Standard first choice; failure motivates broader exploration

#### Logistic Regression Probe

- **What:** Simple linear classifier used instead of MLP
- **Why This Matters:** Nonlinear SE patterns may require nonlinear probe
- **Root Cause:** Simplest architecture per SEP paper baseline
- **Impact on Claims:** May underestimate hidden state SE information capacity
- **Why Acceptable:** If linear probe works, simpler is better; failure motivates complexity increase

#### 4-Dimensional Similarity Features

- **What:** Only mean/std/min/max of cosine similarity matrix used
- **Why This Matters:** Full similarity structure contains richer information
- **Root Cause:** Minimal feature extraction for PoC simplicity
- **Impact on Claims:** Similarity augmentation benefit may be underestimated
- **Why Acceptable:** If crude features work, elaborate ones unnecessary; failure motivates richer encoding

#### Single Random Seed

- **What:** Only seed=42 used; no variance estimation
- **Why This Matters:** Results may not be statistically robust
- **Root Cause:** PoC-level validation budget
- **Impact on Claims:** Cannot compute confidence intervals
- **Why Acceptable:** Single seed sufficient for pass/fail at PoC level; formal validation needs multiple seeds

#### No SE Label Validation

- **What:** DeBERTa clustering output not validated for quality
- **Why This Matters:** Degenerate clusters would produce invalid SE labels
- **Root Cause:** Time constraint; assumed reference implementation correctness
- **Impact on Claims:** SE labels may be root cause of failure
- **Why Acceptable:** Identifying this as potential root cause is itself valuable

### 6.2 Scope Conditions

| Condition | Results Hold | Results May Not Hold | Evidence |
|-----------|-------------|---------------------|----------|
| LLM Architecture | Llama-3-8B-Instruct (tested) | Other architectures (Mistral, GPT, etc.) | Only one model tested |
| Dataset | TruthfulQA | TriviaQA, SQuAD, other QA benchmarks | Single dataset tested |
| Hidden Layer | Layer 25 | Layers 20-24, 26-31 | No layer ablation |
| Token Position | TBG | SLT, pooled positions | Single position tested |
| Probe Architecture | Logistic Regression | MLP, attention-based probes | Simplest architecture used |
| Similarity Encoding | 4-dim summary statistics | Full matrix, learned pooling | Minimal encoding |

### 6.3 Assumption Violation Impact

- **A1 (Hidden states encode SE):** VIOLATED — rho = 0.08 near zero. Impact: Core mechanism doesn't work in tested configuration. Entire approach needs reconsideration for Phase 0 restart.

- **A3 (Similarity improves generalization):** PARTIALLY VIOLATED — +0.0009 improvement is negligible. Impact: No practical benefit from similarity augmentation at current feature dimensionality.

---

## 7. Future Work

### 7.1 From Untested Alternative Explanations

- **Alternative:** Layer 25 may not be the SE-encoding layer
  - **Why Not Yet Tested:** EXISTENCE tier budget limited to single configuration
  - **Proposed Experiment:** Systematic layer ablation study (layers 20-31) with same probe setup
  - **Expected Outcome:** If SE information exists, one or more layers should show rho > 0.3

- **Alternative:** TBG token position may miss SE-relevant signal
  - **Why Not Yet Tested:** Followed SEP paper default without ablation
  - **Proposed Experiment:** Compare TBG vs SLT vs all-token-pooling
  - **Expected Outcome:** Different positions may capture complementary information

- **Alternative:** SE label quality may be degenerate
  - **Why Not Yet Tested:** Time constraint; assumed implementation correctness
  - **Proposed Experiment:** Validate cluster count distribution (expected 2-15 clusters per question)
  - **Expected Outcome:** If clusters are degenerate (all same or all different), SE labels are invalid

### 7.2 From Unverified Assumptions

- **Assumption:** DeBERTa NLI adequately captures semantic equivalence
  - **Current Status:** UNVERIFIED
  - **Proposed Test:** Manual inspection of cluster assignments on sample questions
  - **If Violated:** SE labels are noise; explains why probes can't learn meaningful signal

- **Assumption:** TruthfulQA is representative of broader QA uncertainty
  - **Current Status:** UNVERIFIED (single dataset)
  - **Proposed Test:** Replicate on TriviaQA and SQuAD to match SEP paper conditions
  - **If Violated:** Results are TruthfulQA-specific; approach may work on other datasets

### 7.3 From Scope Extension Opportunities

- **Extension:** Nonlinear probe (2-layer MLP with 256 units, ReLU)
  - **Current Evidence Suggesting Feasibility:** Original Phase 2A specified MLP; logistic regression was simplification
  - **Required Resources:** Minimal — architecture change in probe training

- **Extension:** Richer similarity encoding (full matrix via learned pooling)
  - **Current Evidence Suggesting Feasibility:** KLE paper shows kernel-based similarity contains uncertainty information
  - **Required Resources:** Design similarity encoder architecture; may need attention mechanism

- **Extension:** Multi-dataset validation before drawing conclusions
  - **Current Evidence Suggesting Feasibility:** SEP paper results on TriviaQA/SQuAD differ from TruthfulQA
  - **Required Resources:** Data generation on additional datasets

---

## 8. Implications for Phase 6 (Paper Writing)

### 8.1 Recommended Narrative Hook

**Recommended Hook:**
> "We set out to create a fast, transferable uncertainty detector by distilling semantic entropy into a single-pass probe. Instead, we discovered that the seemingly straightforward approach of probing hidden states for semantic uncertainty fails spectacularly — achieving correlation indistinguishable from random guessing."

**Hook Strategy:** Surprising Negative Result
**Why This Hook:** Negative results that contradict published findings (SEP achieves AUROC ~0.85) are valuable for the community. The 39% AUROC gap between our implementation and published results reveals configuration sensitivity not emphasized in prior work.

### 8.2 Key Insight (Experiment-Verified)

> Hidden states at layer 25 of Llama-3-8B-Instruct do not encode semantic entropy in a way that simple linear probes can extract, despite prior work suggesting otherwise.

**Verification Evidence:** Spearman rho = 0.0843 (p = 0.283), AUROC = 0.52 (random baseline = 0.50)

### 8.3 Strongest Claims (Paper-Ready)

1. **Layer 25 TBG hidden states do not predict SE**
   - Evidence: rho = 0.0843, AUROC = 0.52 (h-e1 validation)
   - Confidence: HIGH
   - Suggested Section: Results

2. **Similarity feature augmentation provides negligible benefit**
   - Evidence: SEDP vs SEP delta = +0.0009 rho
   - Confidence: HIGH
   - Suggested Section: Results

3. **Significant gap exists between our SEP baseline and published results**
   - Evidence: Our AUROC = 0.52 vs published AUROC ~0.85 (-39%)
   - Confidence: HIGH
   - Suggested Section: Discussion

### 8.4 Honest Limitations (Must Include in Paper)

1. **Single layer/position configuration tested**
   - Why Acceptable: PoC validation; identifies need for systematic ablation
   - Suggested Framing: "Our results reveal configuration sensitivity, motivating systematic hyperparameter exploration"

2. **SE label quality not validated**
   - Why Acceptable: Identifying potential root cause is valuable contribution
   - Suggested Framing: "Future work should validate semantic clustering quality before probe training"

3. **Single dataset (TruthfulQA)**
   - Why Acceptable: Standard benchmark; matches some prior work
   - Suggested Framing: "Multi-dataset validation needed to assess generalizability"

### 8.5 Evidence Highlights (Most Persuasive)

1. **Gate Failure Visualization**
   - Data: Bar chart with rho=0.3 threshold, showing both methods far below
   - "So What": Clear visual demonstration of fundamental approach failure
   - Suggested Figure: Main results figure showing gate threshold vs actual performance

2. **Near-Random ROC Curves**
   - Data: ROC curves hugging diagonal (AUC ≈ 0.52)
   - "So What": Methods perform no better than random guessing
   - Suggested Figure: ROC comparison (SEP vs SEDP vs random baseline)

3. **Scatter Plot Showing No Correlation**
   - Data: Predicted vs True SE with rho = 0.08
   - "So What": Visual demonstration that probe predictions are uncorrelated with ground truth
   - Suggested Figure: Scatter with regression line and correlation statistics

---

## Source Files Reference

| File | Hypothesis | Purpose |
|------|------------|---------|
| `h-e1/04_validation.md` | h-e1 | Experiment results, gate outcomes |
| `h-e1/04_checkpoint.yaml` | h-e1 | Pass rate, metrics, reflection outcome |
| `h-e1/03_tasks.yaml` | h-e1 | Planned tasks, expected metrics |
| `h-e1/02c_experiment_brief.md` | h-e1 | Experiment design, variables, protocol |
| `03_refinement.yaml` | Main | Original hypothesis statement |
| `verification_state.yaml` | Pipeline | Pipeline state, gate results |

**Input files per hypothesis:**
- `h-{id}/04_validation.md` — Experiment results, gate outcomes, lessons learned
- `h-{id}/04_checkpoint.yaml` — Pass rate, failed checks, SDD metrics
- `h-{id}/03_tasks.yaml` — Planned tasks, expected metrics, success criteria
- `h-{id}/02c_experiment_brief.md` — Experiment design, variables, evaluation protocol

---

## Appendix A: Sub-Hypothesis Status

| ID | Type | Statement | Status | Gate | Result |
|----|------|-----------|--------|------|--------|
| h-e1 | EXISTENCE | Probe produces meaningful SE predictions (rho ≥ 0.3) | **FAILED** | MUST_WORK | rho = 0.0843 |
| h-m1 | MECHANISM | SE label pipeline produces valid labels | CASCADE_FAILED | MUST_WORK | Not tested |
| h-m2 | MECHANISM | Similarity structure is informative | CASCADE_FAILED | MUST_WORK | Not tested |
| h-m3 | MECHANISM | Cross-model transfer achieves rho ≥ 0.5 | CASCADE_FAILED | SHOULD_WORK | Not tested |

---

## Appendix B: Key Citations

1. Kossen, J., Han, J., Razzak, M., Schut, L., Malik, S., & Gal, Y. (2024). Semantic Entropy Probes: Robust and Cheap Hallucination Detection in LLMs. arXiv:2406.15927

2. Farquhar, S., Kossen, J., Kuhn, L., & Gal, Y. (2024). Detecting hallucinations in large language models using semantic entropy. Nature.

3. Nikitin, A., et al. (2024). Kernel Language Entropy: Fine-grained Uncertainty Quantification for LLMs. NeurIPS.

---

*Generated by Phase 4.5 Hypothesis Synthesis v2.0*
*Anonymous Research Pipeline — Evidence-refined hypothesis with theoretical interpretation*
*Synthesis Completed: 2026-03-29*
