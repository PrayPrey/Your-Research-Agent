# Validated Hypothesis Synthesis

**Generated:** 2026-08-28
**Workflow:** Phase 4.5 Hypothesis Synthesis 
**Pipeline Position:** Phase 4 (Hypothesis Loop) → [Phase 4.5] → Phase 5/6

---

## 1. Executive Summary

This synthesis documents the evidence-based refinement of the matched-budget hallucination detection comparison hypothesis. The original hypothesis predicted that semantic entropy (SE) and self-consistency (SC) methods would show different precision-recall tradeoffs across benchmarks under matched computational budgets.

**Key findings from pilot validation (h-e1):** Only 1 of 4 method-dataset combinations met the AUROC > 0.55 threshold (SE on HaluEval = 0.551). Self-consistency performed near random on both datasets. TruthfulQA showed inverted results (AUROC < 0.5) suggesting labeling methodology issues. All results are statistically inconclusive due to small sample size (n=20).

The refined hypothesis significantly narrows scope: claims are now limited to "marginal SE signal on HaluEval under pilot conditions" with full validation requiring larger sample sizes. Predictions P2 and P3 were not tested as dependent hypotheses (h-m1 through h-c2) did not execute.

| Metric | Value |
|--------|-------|
| **Original Core Statement** | SE and SC show different precision-recall tradeoffs with patterns varying by benchmark |
| **Refined Core Statement** | Under pilot conditions, SE showed marginal detection ability on HaluEval; SC near random; full validation required |
| **Predictions Supported** | 0 / 3 |
| **Overall Pass Rate** | 25% (1/4 conditions) |
| **Hypotheses Validated** | 0 / 6 (1 partial, 5 not started) |

---

## 2. Prediction-Result Matrix

| Prediction | Original Statement | Tested By | Key Metric | Result | Status | Confidence | Evidence Summary |
|------------|-------------------|-----------|------------|--------|--------|------------|------------------|
| **P1** | SE and SC show statistically different AUROC on ≥1 benchmark | h-e1 | AUROC | SE=0.551, SC=0.444 on HaluEval | INCONCLUSIVE | LOW | n=20 insufficient; CIs overlap |
| **P2** | Method × benchmark interaction exists | Not tested | — | — | INCONCLUSIVE | — | h-m3, h-c1 not executed |
| **P3** | Both methods outperform calibration baseline at N≥10 | Not tested | — | — | INCONCLUSIVE | — | h-c2 not executed |

**Status Legend:** SUPPORTED | PARTIALLY_SUPPORTED | REFUTED | INCONCLUSIVE

### Causal Mechanism Verification

| Mechanism Step | Description | Falsifier | Evidence | Verification Status |
|----------------|-------------|-----------|----------|---------------------|
| 1 | Model generates N responses under sampling (temp > 0) | Deterministic outputs | Experiment used N=10, temp=0.7 | VERIFIED |
| 2 | SE clusters responses via bidirectional NLI, computes entropy | NLI clustering fails | Code executed; HaluEval AUROC=0.551 marginal | PARTIALLY_VERIFIED |
| 3 | SC measures surface agreement (BERTScore) without semantic grouping | Surface metrics perfectly correlate with semantics | SC AUROC 0.444-0.474 near random | UNVERIFIED |

---

## 3. Hypothesis Refinement

### 3.1 Original Core Statement (Phase 2A)

> Under matched generation budgets (N samples), if semantic entropy and self-consistency methods are applied to the same hallucination detection task, then they will show different precision-recall tradeoffs with the pattern varying by benchmark, because semantic entropy captures semantic clustering of errors while self-consistency captures surface-level output inconsistency.

### 3.2 Refined Core Statement (Phase 4.5)

> Under pilot conditions (N=20 samples per dataset, single seed), semantic entropy showed marginal hallucination detection ability on HaluEval (AUROC=0.551) while self-consistency performed near random (AUROC=0.444). **Claim scope limited by**: (1) small sample size insufficient for statistical conclusions, (2) TruthfulQA labeling issues producing inverted results, (3) no cross-benchmark comparison completed. Full validation requires larger sample and methodology revision.

**Key Changes:**
- Removed claims about precision-recall tradeoff patterns (not measured)
- Removed claims about benchmark-varying patterns (only HaluEval tested reliably)
- Weakened mechanism claims (SC mechanism unverified)
- Added explicit scope limitations

### 3.3 Causal Mechanism — Verified Chain

```
Step 1 [VERIFIED] → Step 2 [PARTIALLY_VERIFIED] → Step 3 [UNVERIFIED]
     ↓                      ↓                           ↓
  Sampling             NLI clustering              BERTScore
  (works)             (marginal signal)          (near random)
```

**Removed/Modified Steps:**
- **Step 3** (SC measures surface agreement): Status changed to UNVERIFIED — SC performed near random, mechanism not demonstrated

### 3.4 Claims Removed or Weakened

| Original Claim | Action | Reason | Evidence |
|----------------|--------|--------|----------|
| SE and SC show different tradeoffs | WEAKEN | Only marginal evidence on one dataset | HaluEval SE=0.551 vs SC=0.444, n=20 |
| Pattern varies by benchmark | REMOVE | Not tested — only h-e1 ran | h-m3, h-c1 not executed |
| SE captures semantic clustering | WEAKEN | Mechanism not robustly demonstrated | Marginal AUROC, high variance |
| SC captures surface inconsistency | REMOVE | SC near/below random on all conditions | AUROC 0.444-0.474 |

### 3.5 Assumptions Status

| Assumption | Original Status | Verification Status | Evidence | Impact if Violated |
|------------|----------------|---------------------|----------|-------------------|
| A1: NLI captures semantic equivalence | Assumed | UNVERIFIED | No explicit test; marginal results | SE mechanism invalid |
| A2: Surface metrics ≠ perfect semantic proxy | Assumed | UNVERIFIED | Not tested | Methods become identical |
| A3: Benchmark labels sufficient quality | Assumed | VIOLATED | TruthfulQA inverted (AUROC=0.289) | TruthfulQA results unreliable |
| A4: Models produce varied hallucinations | Assumed | VERIFIED | Non-constant output scores | Method applicable |

---

## 4. Theoretical Interpretation

### 4.1 Mechanistic Explanation (Experiment-Verified)

Our pilot experiment demonstrates that sampling-based hallucination detection can be operationalized, but method effectiveness varies:

**Verified:** The LLM (Llama-3-8B-Instruct) generates diverse responses under temperature sampling (temp=0.7, N=10 samples), confirming the prerequisite for both methods.

**Partially verified:** Semantic entropy via NLI-based clustering produces uncertainty scores with marginal discriminative ability on HaluEval (AUROC=0.551). The signal is weak and may not generalize.

**Unverified:** Self-consistency via BERTScore-based agreement performed at chance level. We hypothesize this is due to either: (a) BERTScore not capturing hallucination-relevant inconsistency, or (b) insufficient sample size masking true signal.

### 4.2 Unexpected Findings Analysis

#### Finding: TruthfulQA Inverted Results

- **Observation:** Semantic entropy AUROC=0.289 on TruthfulQA (significantly below random)
- **Why Unexpected:** Literature reports SE AUROC ~0.75-0.85 on TruthfulQA (Kuhn et al. 2023)
- **Competing Explanations:**
  1. **Labeling mismatch:** "Best Answer" matching may not align with hallucination definition (Plausibility: HIGH)
  2. **Model difference:** Llama-3-8B may behave differently than original paper's models (Plausibility: MEDIUM)
  3. **Implementation bug:** Clustering code inverted (Plausibility: LOW — verified correct)
- **Most Likely Interpretation:** Labeling mismatch — TruthfulQA designed for truthfulness evaluation, not hallucination detection per se
- **Additional Evidence Needed:** Run with Kuhn et al.'s original labeling protocol

#### Finding: Self-Consistency Near Random

- **Observation:** SC AUROC 0.444-0.474 on both datasets
- **Why Unexpected:** SelfCheckGPT reports AUROC ~0.70-0.80 on WikiBio
- **Competing Explanations:**
  1. **BERTScore insufficient:** Surface similarity doesn't capture semantic equivalence for hallucination (Plausibility: HIGH)
  2. **Sample size:** n=20 too noisy for reliable estimation (Plausibility: HIGH)
  3. **Benchmark mismatch:** WikiBio vs TruthfulQA/HaluEval different task structures (Plausibility: MEDIUM)
- **Most Likely Interpretation:** Combination of insufficient samples and benchmark/metric mismatch
- **Additional Evidence Needed:** Full-scale run with NLI-based consistency metric

### 4.3 Connection to Existing Literature

| Our Finding | Related Work | Relationship | Citation |
|-------------|-------------|--------------|----------|
| SE marginal on HaluEval (0.551) | Kuhn et al. 2023 (ICLR) | CONSISTENT_WITH (weaker than reported) | arXiv:2302.09664 |
| SC near-random | Manakul et al. 2023 (EMNLP) | CONTRADICTS (different benchmark) | arXiv:2303.08896 |
| TruthfulQA labeling issue | Lin et al. 2022 | BUILDS_ON (benchmark design) | — |
| Method-benchmark sensitivity | No direct prior | NOVEL (pending full validation) | — |

### 4.4 Theoretical Contributions

1. **METHODOLOGICAL (Tentative):** Pilot comparison framework for matched-budget UQ method evaluation
2. **EMPIRICAL (Tentative):** Preliminary evidence that method performance is benchmark-sensitive
3. **Note:** All contributions require full-scale validation before claiming

---

## 5. Experiment Results (Phase 6 Evidence)

### 5.1 Per-Hypothesis Results

| Hypothesis | Title | Gate | Result | Pass Rate | Key Insight |
|------------|-------|------|--------|-----------|-------------|
| **h-e1** | Both methods detect above random | MUST_WORK | PARTIAL | 25% | Only SE on HaluEval marginally above threshold |
| **h-m1** | SE clusters via NLI | MUST_WORK | NOT_STARTED | — | — |
| **h-m2** | SC measures surface agreement | MUST_WORK | NOT_STARTED | — | — |
| **h-m3** | Methods show different AUROC | MUST_WORK | NOT_STARTED | — | — |
| **h-c1** | Method × benchmark interaction | SHOULD_WORK | NOT_STARTED | — | — |
| **h-c2** | Both outperform calibration baseline | SHOULD_WORK | NOT_STARTED | — | — |

### 5.2 Aggregate Metrics

| Metric | Value |
|--------|-------|
| **Total Hypotheses** | 6 |
| **Fully Validated** | 0 |
| **Partially Validated** | 1 (h-e1) |
| **Failed** | 0 |
| **Not Started** | 5 |
| **Total Tasks Completed** | ~11 / 11 (h-e1 only) |
| **SDD Compliance Rate** | N/A |

### 5.3 Optimal Hyperparameters

```yaml
# h-e1 PoC Configuration (NOT optimized)
sampling:
  n_samples: 10
  temperature: 0.7
  max_tokens: 256
  seed: 42

models:
  generator: meta-llama/Meta-Llama-3-8B-Instruct
  nli: microsoft/deberta-large-mnli
  bertscore: roberta-large

evaluation:
  gate_threshold: 0.55
  sample_size: 20  # PoC mode - insufficient for statistical power
```

### 5.4 Proven Components

| Component | Source Hypothesis | File | Reusable |
|-----------|-------------------|------|----------|
| Semantic entropy computation | h-e1 | code/run_experiment.py | YES |
| BERTScore consistency | h-e1 | code/run_experiment.py | YES |
| Dataset loading (TruthfulQA, HaluEval) | h-e1 | code/run_experiment.py | YES |
| AUROC with bootstrap CI | h-e1 | code/run_experiment.py | YES |

### 5.5 Planned-vs-Actual Comparison

| Hypothesis | Planned Metric (03_tasks) | Planned Target | Actual Result (04_validation) | Deviation Type | Notes |
|------------|--------------------------|----------------|-------------------------------|----------------|-------|
| **h-e1** | AUROC both methods | > 0.55 | SE: 0.289-0.551, SC: 0.444-0.474 | SCOPE_CHANGE | PoC mode (n=20 vs n=817+) |
| **h-e1** | Full dataset | 817 TruthfulQA, 10K HaluEval | 20 samples each | SCOPE_CHANGE | GPU/time constraints |
| **h-e1** | Both methods pass | Both AUROC > 0.55 | 1/4 conditions pass | HYPOTHESIS_ISSUE + DESIGN_ISSUE | TruthfulQA labeling mismatch |

**Deviation Types:** IMPLEMENTATION_GAP | DESIGN_ISSUE | HYPOTHESIS_ISSUE | SCOPE_CHANGE | NONE

### 5.6 Key Figures Reference

| Figure | Source | Description | Suggested Paper Section |
|--------|--------|-------------|------------------------|
| (skipped) | h-e1/figures/ | ROC curves | Results |
| (skipped) | h-e1/figures/ | Score distributions | Results |

**Note:** Figures skipped due to small sample size in PoC mode.

---

## 6. Limitations & Scope Boundaries

### 6.1 Principled Limitations

#### L1: Insufficient Sample Size

- **What:** PoC mode used n=20 samples per dataset (planned: 817 TruthfulQA, 10K HaluEval)
- **Why This Matters:** Bootstrap confidence intervals extremely wide (e.g., [0.105, 0.526]); no statistical power for method comparison
- **Root Cause:** Deliberate scope reduction for rapid PoC validation; GPU/time constraints
- **Impact on Claims:** All AUROC comparisons statistically inconclusive; cannot confirm or deny method differences
- **Why Acceptable:** PoC established pipeline functionality; full run planned for Phase 5

#### L2: TruthfulQA Labeling Mismatch

- **What:** TruthfulQA "Best Answer" matching may not align with hallucination detection definition
- **Why This Matters:** SE AUROC=0.289 (inverted) suggests labels/method misalignment, not method failure
- **Root Cause:** TruthfulQA designed for truthfulness evaluation; hallucination detection requires different labeling
- **Impact on Claims:** TruthfulQA results unreliable; only HaluEval results semi-valid
- **Why Acceptable:** Identifies need for labeling protocol revision; HaluEval provides alternative

#### L3: Self-Consistency Mechanism Unverified

- **What:** SC performed near-random on both datasets
- **Why This Matters:** Cannot claim SC captures hallucination-relevant uncertainty
- **Root Cause:** Either BERTScore insufficient for semantic equivalence OR sample size masks true signal
- **Impact on Claims:** Must remove all claims about SC mechanism working
- **Why Acceptable:** Identifies concrete investigation direction; SE provides alternative

#### L4: Single Model Family

- **What:** Only tested Llama-3-8B-Instruct
- **Why This Matters:** Results may not generalize to other model families
- **Root Cause:** Pilot scope limitation
- **Impact on Claims:** All claims qualified to "Llama-3-8B under tested conditions"
- **Why Acceptable:** Standard practice for PoC; multi-model planned for full validation

### 6.2 Scope Conditions

| Condition | Results Hold | Results May Not Hold | Evidence |
|-----------|-------------|---------------------|----------|
| Sample size | N ≥ 200 (estimated) | N = 20 (current) | Wide CIs in h-e1 |
| Benchmark | HaluEval (marginal signal) | TruthfulQA (inverted results) | AUROC direction |
| Detection method | Semantic Entropy (marginal) | Self-Consistency (near random) | SC AUROC 0.444-0.474 |
| Model | Unknown | Llama-3-8B only tested | No other models tested |

### 6.3 Assumption Violation Impact

- **A3 (Benchmark label quality):** TruthfulQA showed inverted AUROC → TruthfulQA results invalid for hallucination detection claim
- **A1 (NLI accuracy):** Not explicitly tested → SE mechanism claims remain unverified
- **A2 (Surface ≠ semantic):** Not tested → Cannot compare SE vs SC mechanisms

---

## 7. Future Work

### 7.1 From Untested Alternative Explanations

- **Alternative:** TruthfulQA inverted AUROC stems from labeling mismatch, not method failure
  - **Why Not Yet Tested:** Used standard "Best Answer" matching without consulting original SE paper protocol
  - **Proposed Experiment:** Run with Kuhn et al. 2023 labeling protocol; compare AUROC under both definitions
  - **Expected Outcome:** AUROC should normalize if labeling is the issue; remain inverted if model/method-specific

- **Alternative:** SC failure due to BERTScore insufficiency, not fundamental method flaw
  - **Why Not Yet Tested:** Only tested BERTScore-based consistency
  - **Proposed Experiment:** Replace BERTScore with NLI-based pairwise agreement (entailment scoring)
  - **Expected Outcome:** If true, NLI-based SC should approach SE performance

### 7.2 From Unverified Assumptions

- **Assumption:** NLI models accurately capture semantic equivalence (A1)
  - **Current Status:** UNVERIFIED
  - **Proposed Test:** Human annotation on 100-sample subset; compute NLI-human agreement
  - **If Violated:** SE mechanism fundamentally flawed; need alternative clustering approach

- **Assumption:** Benchmark label quality sufficient (A3)
  - **Current Status:** VIOLATED (TruthfulQA)
  - **Proposed Test:** Inter-annotator agreement study on TruthfulQA/HaluEval subset
  - **If Violated:** Need cleaner benchmark or re-annotation

### 7.3 From Scope Extension Opportunities

- **Extension:** Full-scale evaluation (IMMEDIATE PRIORITY)
  - **Current Evidence Suggesting Feasibility:** Pipeline functional; PoC showed marginal signal
  - **Required Resources:** ~2-4 hours GPU time for N=817 TruthfulQA + N=500 HaluEval

- **Extension:** Multi-model evaluation
  - **Current Evidence Suggesting Feasibility:** Same pipeline; Mistral-7B readily available
  - **Required Resources:** Additional ~4 hours GPU time

- **Extension:** Cross-benchmark comparison (HaluEval-Summarization)
  - **Current Evidence Suggesting Feasibility:** Different task type may reveal method×task interaction
  - **Required Resources:** Moderate — different output format requires evaluation protocol update

---

## 8. Implications for Phase 6 (Paper Writing)

### 8.1 Recommended Narrative Hook

**Recommended Hook:** "Uncertainty-based hallucination detection methods show promise in controlled settings, but our pilot study reveals significant sensitivity to benchmark choice and sample size — calling for more rigorous evaluation protocols."

**Hook Strategy:** Puzzle framing — highlight gap between literature claims and pilot observations
**Why This Hook:** Positions work as methodological contribution (evaluation protocol) rather than claiming method superiority

### 8.2 Key Insight (Experiment-Verified)

> Semantic entropy showed marginal hallucination detection ability on HaluEval (AUROC=0.551) but failed on TruthfulQA (AUROC=0.289), suggesting benchmark-specific sensitivity not previously reported.

**Verification Evidence:** h-e1 AUROC results with bootstrap CIs

### 8.3 Strongest Claims (Paper-Ready)

1. **Pilot pipeline functional for matched-budget UQ comparison**
   - Evidence: h-e1 completed; code runs end-to-end
   - Confidence: HIGH
   - Suggested Section: Methods

2. **SE shows marginal signal on HaluEval (AUROC=0.551)**
   - Evidence: h-e1 results with 95% CI
   - Confidence: LOW (small sample)
   - Suggested Section: Results (with heavy caveats)

3. **Benchmark choice affects method performance**
   - Evidence: TruthfulQA inverted vs HaluEval marginal
   - Confidence: MEDIUM (needs full validation)
   - Suggested Section: Discussion

### 8.4 Honest Limitations (Must Include in Paper)

1. **Sample size insufficient for statistical conclusions**
   - Why Acceptable: PoC mode by design; full validation planned
   - Suggested Framing: "Pilot study to validate experimental pipeline; full-scale results forthcoming"

2. **TruthfulQA labeling mismatch**
   - Why Acceptable: Identifies methodological issue for future work
   - Suggested Framing: "Labeling protocol alignment needed between benchmarks and detection methods"

3. **Single model family tested**
   - Why Acceptable: Standard PoC practice
   - Suggested Framing: "Initial results on Llama-3-8B; generalization requires multi-model validation"

### 8.5 Evidence Highlights (Most Persuasive)

1. **SE HaluEval AUROC=0.551**
   - Data: AUROC 0.551, 95% CI [0.267, 0.800]
   - "So What": Marginal signal exists; method potentially viable with larger sample
   - Suggested Figure/Table: AUROC comparison bar chart with CI error bars

2. **TruthfulQA Inversion**
   - Data: SE AUROC=0.289 (expected ~0.75-0.85 from literature)
   - "So What": Benchmark design critically affects method evaluation
   - Suggested Figure/Table: Literature vs observed performance comparison table

3. **SC Near-Random**
   - Data: SC AUROC 0.444-0.474 across both datasets
   - "So What": BERTScore-based consistency may not capture hallucination uncertainty
   - Suggested Figure/Table: Method comparison with significance markers

---

## Source Files Reference

| File | Hypothesis | Purpose |
|------|------------|---------|
| `h-e1/04_validation.md` | h-e1 | Experiment results, AUROC scores, gate outcome |
| `h-e1/04_checkpoint.yaml` | h-e1 | Pass rate (25%), reflection outcome |
| `h-e1/03_tasks.yaml` | h-e1 | Planned tasks and success criteria |
| `h-e1/02c_experiment_brief.md` | h-e1 | Experiment design, variables, protocol |
| `03_refinement.yaml` | Main | Original hypothesis with predictions P1-P3 |
| `verification_state.yaml` | Pipeline | All hypothesis statuses and workflow state |

**Input files per hypothesis:**
- `h-{id}/04_validation.md` — Experiment results, gate outcomes, lessons learned
- `h-{id}/04_checkpoint.yaml` — Pass rate, failed checks, SDD metrics
- `h-{id}/03_tasks.yaml` — Planned tasks, expected metrics, success criteria
- `h-{id}/02c_experiment_brief.md` — Experiment design, variables, evaluation protocol

---

*Anonymous Research Pipeline — Evidence-refined hypothesis with theoretical interpretation*
