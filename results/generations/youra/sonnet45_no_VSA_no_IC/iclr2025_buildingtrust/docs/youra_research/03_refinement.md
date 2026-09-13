# Hypothesis Refinement Summary: h-c1

**Generated:** 2026-08-19  
**Phase:** 2A-Dialogue (Tikitaka Self-Contained Loop)  
**Status:** Refined and Ready for Phase 2B

---

## Executive Summary

**Hypothesis:** LLMs exhibit model-specific behavioral coupling patterns across trustworthiness dimensions, measurable via co-occurrence analysis on existing benchmarks using API-only access.

**Reframed Contribution:** From "universal coupling discovery" to "model-specific coupling fingerprints" - architectures/training approaches manifest distinct coupling signatures, enabling evidence-based model selection for deployment.

**Convergence:** Achieved after 2 rounds (12 persona exchanges). All 6 convergence criteria met. Average confidence: 92%.

---

## Core Statement

LLMs exhibit **model-specific behavioral coupling patterns** across trustworthiness dimensions (truthfulness, robustness, fairness, safety, privacy). When models fail on one dimension, they show statistically significant co-occurrence of failures on other dimensions due to shared underlying behavioral vulnerabilities.

**Key Insight:** Coupling patterns are NOT universal but model-specific, reflecting architectural and training differences. GPT-4 may couple truthfulness-robustness strongly, while Claude 3 couples truthfulness-fairness. These distinct patterns serve as **model fingerprints**.

---

## Why This Matters

### Deployment Value

Current practice evaluates dimensions independently (pass TruthfulQA, pass AdvBench, ship it). If failures couple, we're missing **compound risk**. A model scoring 85% on truthfulness and 82% on robustness independently may have 15% overlap failing BOTH - the most critical instances for safety.

### Model Selection Tool

Companies choosing between GPT-4 vs Claude 3 can ask: "Which coupling profile is safer for my healthcare chatbot?" If truthfulness-fairness coupling is critical, pick the model with LOWER coupling (failures don't cascade).

### Regulatory Transparency

AI audits could require coupling signature disclosure: "Your model shows phi = 0.5 truthfulness-robustness coupling - any mitigation?" Coupling becomes a transparency metric.

---

## Novelty

**First Contributions:**
1. **Coupling signature characterization:** No prior work quantifies behavioral coupling across trustworthiness dimensions
2. **Model comparison via coupling profiles:** Existing benchmarks provide independent scores, not coupling fingerprints
3. **Deployment-critical framing:** Coupling as model selection criterion, not just academic curiosity

**Prior Work Gaps Addressed:**
- Gap 1 (P0): Empirical co-occurrence data - we directly measure co-failures
- Multi-dimensional evaluation exists (MMTrustEval) but dimensions are independent - we add coupling layer
- Behavioral detection exists (TrustScore) but single-dimension - we extend to cross-dimensional patterns

---

## Testable Predictions

### Prediction 1: Coupling Exists
- **Expected:** ≥2 models show ≥3 dimension pairs with phi ≥ 0.3, p < 0.01
- **Measurement:** Phi coefficient (effect size), chi-square test (significance)
- **Falsification:** All dimension pairs show phi < 0.3 OR p > 0.05

### Prediction 2: Model-Specific Fingerprints
- **Expected:** Coupling matrices differ across models (Mantel test r < 0.7 for ≥1 model pair)
- **Measurement:** Mantel test for coupling matrix similarity
- **Falsification:** All model pairs show r > 0.9 (identical patterns)

### Prediction 3: Difficulty-Independent
- **Expected:** Partial phi ≥ 0.25 after controlling for model confidence
- **Measurement:** Partial correlation controlling for confidence scores
- **Falsification:** All partial phi < 0.2 (coupling was spurious difficulty correlation)

---

## Experimental Setup

### Phase 1 (Proof of Concept)

**Data Collection:**
- Use MMTrustEval framework to evaluate 500 instances × 3 models (GPT-4, Claude 3, Llama 3)
- Obtain binary failure labels (pass/fail) for 5 dimensions per instance per model
- Extract model confidence scores (logit probabilities) for difficulty control

**Analysis:**
- Construct 10 pairwise 2×2 contingency tables per model (5 dimensions = 10 pairs)
- Calculate phi coefficient and chi-square for each pair
- Perform Mantel test to compare coupling matrices across models
- Compute partial phi controlling for confidence scores

**Success Thresholds:**
- **Tier 1 (Full Success):** ≥2 models, ≥3 pairs, phi ≥ 0.3, p < 0.01, Mantel r < 0.7, partial phi ≥ 0.25
- **Tier 2 (Partial Success):** ≥1 model, ≥1 pair, phi ≥ 0.3, p < 0.01, partial phi ≥ 0.25
- **Tier 3 (Negative Result):** No coupling (still publishable as "dimensions are independent")

### Phase 2 (Extension - Conditional)
- Only proceed if Phase 1 achieves Tier 1 or Tier 2
- Cross-benchmark coupling using embedding-based semantic clustering (TruthfulQA × AdvBench)

---

## Key Assumptions & Validations

**A1: Behavioral coupling is real** (not random overlap)
- Validation: Difficulty control via partial correlation

**A2: Difficulty is measurable** (confidence scores proxy difficulty)
- Validation: Compare with human ratings if available (Phase 4)

**A3: Sample size is adequate** (500 instances sufficient)
- Validation: Power analysis confirms expected overlap ≥ 25 co-failures

**A4: MMTrustEval is representative** (5-dim evaluation captures trustworthiness)
- Validation: Cross-validate with other benchmarks in Phase 2 extension

**A5: API outputs are sufficient** (no internal states needed)
- Validation: TrustScore (19 citations) demonstrated API-only behavioral detection works

---

## ROUTE_TO_0 Compliance

**Learning from h-m1 Failure (Layer-wise bottleneck detection):**

1. ✅ **No layer-specific mechanisms** - behavioral analysis only, no architecture-dependent internal states
2. ✅ **Real data** - MMTrustEval benchmark with ground truth, not synthetic text
3. ✅ **Observable behaviors** - API outputs (binary pass/fail labels), not hidden representations
4. ✅ **Architecture-agnostic** - tests 3 model families (GPT-4, Claude 3, Llama 3) without assuming shared structure
5. ✅ **Existing benchmarks** - MMTrustEval framework already validated and publicly available

**Pipeline Feasibility Constraints:**
1. ✅ No new benchmarks required - uses existing MMTrustEval
2. ✅ No synthetic data - real benchmark instances
3. ✅ No human evaluation - automated binary labels
4. ✅ Testable immediately - framework, APIs, statistical tools exist

---

## Objections Addressed

### Difficulty Confound
- **Objection:** Hard prompts fail on ALL dimensions → spurious coupling
- **Resolution:** Partial correlation controlling for confidence + difficulty-stratified analysis
- **Status:** RESOLVED

### Sample Size Adequacy
- **Objection:** 90% accuracy → only 81 failures → insufficient for pairwise tests
- **Resolution:** Power analysis confirms 500 instances × 20% failure rate = 100 failures per dimension → 25 co-failures needed for phi = 0.3 detection
- **Status:** RESOLVED

### Cross-Model Generalization
- **Objection:** If models show different patterns, claim fails
- **Resolution:** Reframed to "model-specific fingerprints" - different patterns are FEATURE not BUG
- **Status:** RESOLVED → REFRAMED

### Cross-Benchmark Complexity
- **Objection:** TruthfulQA ≠ AdvBench → 'same input' requirement impossible
- **Resolution:** Within-benchmark coupling (MMTrustEval) Phase 1, cross-benchmark Phase 2 conditional
- **Status:** RESOLVED

### Causality Direction
- **Objection:** Don't know WHY coupling exists (shared vulnerability vs difficulty)
- **Resolution:** Difficulty control + qualitative validation (examine high-coupling instances)
- **Status:** PARTIALLY RESOLVED (observational study, no causal intervention)

---

## Persona Consensus

**Final Standings:**
- 🔭 Dr. Nova: STRONG SUPPORT (95%) - model fingerprinting reframe elevated hypothesis
- 🔬 Prof. Vera: SUPPORT WITH CONDITIONS (90%) - difficulty proxy needs empirical validation
- 🎯 Dr. Sage: STRONG SUPPORT (95%) - deployment-critical, regulatory value
- ⚙️ Prof. Pax: SUPPORT (92%) - technically validated, no fundamental barriers
- 🛡️ Dr. Ally: STRONG SUPPORT (93%) - synthesis complete, ROUTE_TO_0 compliant
- 🔍 Prof. Rex: CONDITIONAL SUPPORT (88%) - qualitative validation should be primary test

**Average Confidence:** 92%

**Unanimous Agreement:**
- Hypothesis is specific and well-defined
- Novelty claim is valid (first coupling signature characterization)
- Technical feasibility validated
- Deployment value clear

**Split Opinion:**
- Qualitative validation priority (post-hoc vs primary test) → Resolution: Pre-register criteria in Phase 2B

---

## Phase 2B Readiness

**Status:** ✅ READY

**Prerequisites Met:**
- ✅ Hypothesis refined with consensus (92% confidence)
- ✅ Core statement clear and specific
- ✅ 3 testable predictions with success/failure criteria
- ✅ Experimental methodology validated
- ✅ ROUTE_TO_0 compliance verified
- ✅ Pipeline feasibility constraints satisfied

**Critical Action Items for Phase 2B:**
1. Define pre-registered qualitative validation criteria (embedding similarity threshold)
2. Specify MMTrustEval version and benchmark subset (reproducibility)
3. Document difficulty proxy assumptions and validation plan
4. Clarify observational vs causal claims

**Expected Phase 2B Outputs:**
- Detailed verification protocol (statistical + qualitative gates)
- Experiment specification (benchmark, models, metrics, sample size)
- Success criteria matrix (Tier 1/2/3 with interpretations)
- Risk assessment (technical, statistical, interpretation risks)

---

## Discussion Evolution

**Round 1:** Universal coupling patterns → Major objections raised (difficulty confound, cross-model generalization, cross-benchmark complexity)

**Round 2:** Model-specific coupling fingerprints → All objections resolved or reframed, consensus achieved

**Breakthrough Moment:** Prof. Rex's challenge on cross-model generalization → Dr. Nova's reframing as model fingerprints (transformed potential weakness into key contribution)

---

**Next Phase:** Phase 2B - Research Planning (Verification Protocol Development)
