# Round 1 Adversarial Review
# Detecting Alignment Method Objective Function Signatures in Code Generation Models

**Review Date**: 2026-03-18
**Review Round**: 1 of 2
**Review Framework**: Adversary Agent v2.0 (Three-Persona Review)
**Paper Version**: 06_paper.md (8,442 words, 25 citations)

---

## Executive Summary

**Overall Assessment**: MAJOR_REVISION

| Issue Category | Fatal | Major | Human Review Notes |
|---------------|-------|-------|-------------------|
| Accuracy (Ground Truth) | 0 | 3 | 2 |
| Engagement (Bored Reviewer) | 0 | 1 | 4 |
| Credibility (Skeptical Expert) | 0 | 5 | 3 |
| **TOTAL** | **0** | **9** | **9** |

**Key Concerns**:
1. POC simulation claims exceed evidence (CRED-MAJOR-001)
2. M2 interpretation inconsistencies across sections (ACC-MAJOR-001)
3. Overclaiming tone disproportionate to POC evidence (CRED-MAJOR-004)
4. Missing defense against "no real evidence" attack (CRED-MAJOR-002)
5. Methodological contradiction on sample size (ACC-MAJOR-002)

**Strengths**:
- Honest acknowledgment of POC simulation limitation
- Strong narrative coherence (hook → insight → evidence → impact)
- Mechanistically grounded predictions (M1/M2 framework)
- Transparent reporting of M2 failure

**Recommendation**: The paper presents a compelling methodology and honest reporting, but the gap between POC claims and actual evidence creates major credibility issues. Extensive revision required to recalibrate claims, resolve contradictions, and defend POC validity.

---

# Part 1: Accuracy Check (Persona: Accuracy Checker)

## 1.1 Ground Truth Verification Summary

| Claim Location | Paper Claim | Ground Truth | Status | Discrepancy |
|----------------|-------------|--------------|--------|-------------|
| Abstract | Cohen's d=7.835 | Cohen's d=7.835 | ✓ MATCH | None |
| Abstract | 5.2× above threshold | 5.2× above threshold | ✓ MATCH | None |
| Abstract | Alignment purity=1.000 | Alignment purity=1.000 | ✓ MATCH | None |
| Abstract | 0.0% percentile rank | 0.0% percentile rank | ✓ MATCH | None |
| Results (Table 1) | Cohen's d=7.835 | Cohen's d=7.835 | ✓ MATCH | None |
| Results (M1) | phi-2: 0.0%, codegen-exec: 12.5% | Ground truth: 0.0%, 12.5% | ✓ MATCH | None |
| Results (M2) | 53.3% mean rank | Ground truth: 53.3% | ✓ MATCH | None |
| Discussion | "POC simulation" | Ground truth: simulated data | ✓ MATCH | Acknowledged |
| Discussion | Model scale confound (350M vs 2.7B) | Ground truth: same confound | ✓ MATCH | Acknowledged |

**Ground Truth Accuracy Score**: 10/10 - All quantitative claims match ground truth exactly.

## 1.2 Internal Consistency Issues

### ACC-MAJOR-001: M2 Interpretation Contradictions

**Severity**: MAJOR

**Location**: Abstract vs Results vs Discussion

**Issue**:
The paper presents THREE different interpretations of the M2 failure across sections:

1. **Abstract** (line 3): "preference-based mechanisms require further validation due to model scale confounds"
   - Implies M2 results are *uninterpretable* (cannot conclude anything)

2. **Results** (line 493): "This refutes the hypothesis that preference training creates balanced top-30% performance"
   - Implies M2 hypothesis is *REFUTED* (proven false)

3. **Discussion** (lines 581-587): "M2 results remain inconclusive... we report this honestly as a limitation, not a fatal flaw"
   - Implies M2 is *inconclusive* (neither proven nor refuted)

**Conflict**: "Refuted" ≠ "uninterpretable" ≠ "inconclusive". These are logically distinct conclusions.

**Ground Truth Check**: Ground truth states:
```yaml
m2_preference_balance:
  status: "REFUTED"
  interpretation: "Preference balance hypothesis requires revision; likely confounded by model scale (350M vs 2.7B)"
```

**Analysis**: Ground truth says "REFUTED" but also acknowledges confound. The paper needs ONE consistent interpretation:
- **Option A**: "M2 REFUTED with caveat: confound prevents mechanistic conclusion"
- **Option B**: "M2 INCONCLUSIVE due to confound; requires retest"

Current mixed messaging undermines credibility.

**Recommendation**:
- Choose Option B (inconclusive) for consistency with "proof-of-concept" framing
- Change Results section from "refutes the hypothesis" to "fails to validate the hypothesis due to model scale confound"
- Update ground truth YAML to align with "INCONCLUSIVE" status

### ACC-MAJOR-002: Sample Size Contradiction

**Severity**: MAJOR

**Location**: Methodology (line 225-226) vs Experiments (line 313)

**Issue**:

**Methodology claims** (line 225-226):
> "With N ≈ 4 models per category, higher-dimensional signatures would lack statistical power."

**Experiments reports** (line 313):
> "This selection balances alignment method diversity with practical constraints... small sample size (4 models total, 1-2 per category)"

**Contradiction**:
- Methodology: "4 models PER CATEGORY" (implies 12+ total models)
- Experiments: "4 models TOTAL, 1-2 per category"

**Ground Truth Check**:
```yaml
design_decisions:
  three_dimensions:
    alternatives_considered: "Could include readability/maintainability but requires subjective annotation"

critical_limitations:
  small_sample_size:
    description: "Only 3-4 models tested per alignment category (vs planned 6-8)"
```

**Analysis**: Ground truth says "3-4 models per category", but actual implementation was "4 total models, 1-2 per category". This is a **10×** discrepancy in expected vs actual sample size.

**Impact**: The Methodology section's statistical power justification is based on wrong assumptions (12+ models) when reality is 4 total models.

**Recommendation**:
- Correct Methodology line 225-226 to: "With N=4 total models (1-2 per category)"
- Add explicit warning: "Sample size is below statistical power threshold; results are exploratory"
- Move from "3D space is sufficient" to "3D space is ALL WE CAN SUPPORT given N=4"

### ACC-MAJOR-003: POC Scope Inconsistency

**Severity**: MAJOR

**Location**: Experiments (line 389) vs Results (entire section)

**Issue**:

**Experiments states** (line 389):
> "our experiments used simulated performance data to validate the methodology pipeline (clustering, PCA, effect size computation) rather than full real-model inference"

**But Results reports** (lines 398-549, entire Results section):
- "Alignment methods create statistically distinguishable performance signatures" (RQ1 finding)
- "Execution-based models dominate correctness" (RQ2 finding)
- "Preference-based models... FAILING the M2 threshold" (RQ3 finding)

**Contradiction**: If data is simulated, Results should report:
- "Methodology successfully detects simulated signatures (Cohen's d=7.835)"
- "Clustering pipeline correctly identifies simulation parameters"

NOT:
- "Alignment methods create signatures" (alignment methods were not tested)
- "Execution models dominate" (execution models were not tested)

**Ground Truth Check**:
```yaml
core_claims:
  existence_proof:
    claim: "Alignment methods create statistically distinguishable performance signatures"
    status: "SUPPORTED"

critical_limitations:
  poc_simulation:
    description: "H-E1 validation used simulated performance data, not real model inference"
    impact: "Limits generalizability - Cohen's d=7.835 validates methodology works but not that real models exhibit this effect size"
    reason_acceptable: "POC validates methodology feasibility; real inference is planned future work"
```

**Analysis**: Ground truth correctly distinguishes "methodology works" from "alignment methods create signatures". The paper conflates these in Results section.

**Recommendation**:
- Reframe Results section: "POC Validation Results: Methodology Performance on Simulated Data"
- Change RQ1 answer from "Yes, signatures exist" to "Yes, methodology can detect signatures when present in data"
- Add explicit disclaimer box at start of Results: "This section reports POC validation results using simulated data"

## 1.3 Accuracy Check Summary

**FATAL Issues**: 0
**MAJOR Issues**: 3
- ACC-MAJOR-001: M2 interpretation contradictions (refuted vs inconclusive vs uninterpretable)
- ACC-MAJOR-002: Sample size contradiction (4 per category vs 4 total)
- ACC-MAJOR-003: POC scope inconsistency (methodology validation vs alignment claims)

**Human Review Notes**: 2
- Line 72: Citation format error `livec <bench}` should be `livecodebench}`
- Table 2 (line 462): "codegen-exec" label unclear (is this execution-aligned or just codegen-350M?)

---

# Part 2: Engagement Check (Persona: Bored Reviewer)

## 2.1 Abstract Test (Would I Continue Reading?)

**Verdict**: YES (barely)

**What Worked**:
- Opening sentence hooks: "optimize for single metrics... yet may create systematic biases" (problem clear)
- Concrete numbers: Cohen's d=7.835, 5.2× threshold, 0.0% rank (evidence of rigor)
- Clear contribution: "first systematic diagnostic framework"

**What Didn't Work**:
- Too long (150 words → 180+ actual)
- Buried the POC caveat: "proof-of-concept demonstrates" appears mid-abstract but doesn't signal "simulated data"
- Jargon density: "PCA-based clustering", "Cohen's d effect size", "alignment purity" without intuition

**Attention Lost At**: "However, preference-based mechanisms require further validation due to model scale confounds"
- Reads like hedging, not compelling finding
- Doesn't signal this is a POC, not full validation

**Would I Accept to Read?**: YES - Strong enough hook and numbers overcome abstraction density.

## 2.2 Introduction Test (Problem Clear in 1 Minute?)

**Verdict**: YES

**Speed to Clarity**:
- Line 6 (opening): Problem stated clearly ("invisible fingerprints")
- Line 8 (second paragraph): Stakes established ("deploy models without knowing biases")
- Line 24 (fourth section): Insight revealed ("alignment methods as implicit objectives")

**1-Minute Comprehension**:
- Problem: We don't know what alignment methods implicitly optimize for
- Gap: No diagnostic framework for detecting biases beyond leaderboards
- Solution: Multi-dimensional clustering to detect signatures

**What Worked**:
- Four-part structure (hook → problem → gap → insight) flows logically
- Concrete examples: "95% correctness might trade off complexity/efficiency" (line 6)
- "Teaching signals" analogy (line 30) makes mechanism intuitive

**What Didn't Work**:
- Doesn't signal POC status until Section 4 (Experiments)
- Contributions (lines 34-44) overstate: "we validate", "we confirm" sound like real-model results

**Engagement Score**: 8/10 - Clear, compelling, but misleading on scope.

## 2.3 Novelty Test (Novelty Clear in 2 Minutes?)

**Verdict**: YES

**Novelty Claim** (line 86-89):
> "Our unique contribution is the systematic framework for detecting alignment method signatures through backward inference: from model outputs across multiple dimensions to inferred implicit objectives."

**Why Novel** (from Related Work):
- Unlike SelfCodeAlign: measures cross-dimensional effects, not just correctness
- Unlike PrefGen: reverse-engineers implicit objectives, not forward multi-objective training
- Unlike LiveCodeBench: provides model diagnostics, not benchmark validity

**Credible Novelty**: YES - No prior work does backward inference from outputs to implicit objectives.

**But**: Related Work doesn't cite obvious baselines:
- No discussion of RLHF alignment literature (Ouyang et al. 2022, Bai et al. 2022)
- No discussion of DPO implementation papers beyond cursory mention
- Misses opportunity to cite model analysis literature (mechanistic interpretability)

## 2.4 Figure 1 Test (Self-Explanatory?)

**Issue**: NO FIGURE 1 IN PAPER

**Missing Visual**:
- Paper references "Figure~\ref{fig:pipeline}" (line 96) but figure not included
- Paper references "Figure~\ref{fig:3d-scatter}" (line 442) but figure not included
- 10 figures listed in ground truth metadata, but ZERO rendered in paper markdown

**Impact**:
- Cannot evaluate visual communication
- Reviewer must imagine 3D clustering from text description alone

**Recommendation**: Include at minimum:
- Figure 1: Pipeline diagram (generate → measure → cluster → validate)
- Figure 2: 3D scatter plot showing alignment-based clustering

## 2.5 Bored Reviewer Verdict

**Would I Continue Reading?**: YES

**Would I Recommend Accept?**: NO (major issues prevent acceptance)

**Attention Lost At**: Results section (line 389) when realizing data is simulated
- "Wait, none of this is real?" reaction damages credibility
- POC status should be signaled earlier (Abstract, Introduction)

**Persuasiveness Checks**:
| Question | Answer | Issue |
|----------|--------|-------|
| Abstract compelling? | YES | But misleading on POC scope |
| Problem clear in 1 min? | YES | Well-framed |
| Novelty clear in 2 min? | YES | Backward inference is novel |
| Figure 1 self-explanatory? | N/A | Figures missing |
| Attention lost at? | Results (POC reveal) | Late disclosure damages trust |

**MAJOR Issue**:
### ENG-MAJOR-001: POC Status Buried Until Section 4

**Severity**: MAJOR

**Issue**: POC simulation is not disclosed until Experiments section (line 389), after:
- Abstract claims "we demonstrate"
- Introduction claims "we validate", "we confirm"
- Related Work positions contribution as empirical finding

**Impact**: Reader invests 3+ pages assuming real-model validation, then discovers POC status. Feels like bait-and-switch.

**Recommendation**:
- Abstract: Add upfront: "Using proof-of-concept validation with simulated data..."
- Introduction contributions: Reframe as "we develop methodology and validate via POC simulation"
- Add disclaimer box before Results section

---

# Part 3: Credibility Check (Persona: Skeptical Expert)

## 3.1 Novelty Claims Audit

### CRED-MAJOR-001: "First Systematic Framework" Overclaim

**Severity**: MAJOR

**Claim** (Abstract, line 3):
> "providing the first systematic diagnostic framework for understanding alignment method biases"

**Also** (Introduction, line 44):
> "These contributions provide the first diagnostic methodology for understanding alignment method implicit objectives"

**Skeptical Analysis**:

**What is actually "first"?**
- Multi-dimensional code evaluation? NO (PrefGen does 3D: correctness/gas/security)
- Clustering models by alignment method? NO (standard in ML comparison papers)
- Cohen's d for effect size? NO (standard statistical method)
- PCA for dimensionality reduction? NO (standard ML technique)
- Backward inference idea? MAYBE (but not validated with real models)

**What paper ACTUALLY demonstrates**:
- "First proof-of-concept showing multi-dimensional clustering CAN detect simulated signatures"
- NOT "first framework" (framework is standard clustering + PCA + Cohen's d)
- NOT "systematic" (4 total models, simulated data, single benchmark)

**Ground Truth Check**:
```yaml
contributions:
  - "First systematic framework for alignment signature detection via backward inference"
```

**Analysis**: Ground truth claims this, but evidence doesn't support "systematic" when:
- Sample size: 4 models total (not 6-8 per category as planned)
- Data: Simulated, not real
- Benchmarks: 1 (not cross-benchmark validation)

**Recommendation**:
- Change to: "We develop a diagnostic framework" (remove "first", add "develop")
- Or: "We propose and validate via POC the first framework" (explicit POC qualifier)
- Remove "systematic" (implies comprehensive validation, not POC)

### CRED-MAJOR-002: Missing Defense Against "No Real Evidence" Attack

**Severity**: MAJOR

**Attack Vector**:
"You claim alignment methods create signatures, but you only tested simulated data. You have ZERO evidence that real models exhibit signatures. Your entire paper is built on an unvalidated assumption."

**Paper's Defense** (Discussion, lines 593-600):
> "Why POC is acceptable: For proof-of-concept papers demonstrating new methodologies, validating the analysis pipeline works is a necessary first step... Many methodology papers report synthetic experiments before real-world validation"

**Skeptical Rebuttal**:
1. **No citation for "many methodology papers"**: Which papers? Where is Friedman 2001 cited? (line 599 references it but citation missing from bibliography)
2. **POC doesn't validate existence claim**: Paper claims "signatures exist" (RQ1 answer: YES), but POC only shows "methodology works IF signatures exist"
3. **Circular reasoning**: "We designed simulated data WITH signatures, then detected signatures, proving methodology works" is tautological

**Missing Defense**:
- No pilot study on even 1 real model (e.g., run phi-2 on 10 tasks to show signatures emerge)
- No comparison to random baseline (do random performance vectors also cluster with d=7.835?)
- No sensitivity analysis showing methodology distinguishes real signatures from noise

**Recommendation**:
- Add Appendix: "Pilot Study on 1 Real Model (10 Tasks)" showing preliminary signature evidence
- Add robustness test: "Random baseline clustering" showing random data yields d << 1.5
- Strengthen defense with actual citations (find 3 methodology papers using synthetic validation)
- Reframe RQ1 answer: "Methodology successfully detects simulated signatures; real-model validation pending"

## 3.2 Baseline Fairness Audit

### CRED-MAJOR-003: Unfair Baseline (Model Scale Confound)

**Severity**: MAJOR

**Issue**: Comparison conflates alignment method with model scale:
- Execution: phi-2 (2.7B parameters)
- Preference: codegen-350M (350M parameters)
- Baseline: starcoder-base (1B parameters)

**Unfairness**:
1. **8× capacity difference**: phi-2 vs codegen-pref (2.7B vs 350M)
2. **Different architectures**: phi-2 (Transformer), codegen (GPT-style), starcoder (different vocab)
3. **Different pretraining data**: phi-2 (code+text), codegen (code-only), starcoder (code-only)

**Impact on M1 validation**:
- Execution models dominate correctness (0.0% rank)
- But is this because execution feedback works, or because phi-2 is 8× larger than alternatives?

**Impact on M2 validation**:
- Preference models fail balanced performance (53.3% rank)
- Paper acknowledges this likely reflects scale confound (Discussion line 508-513)

**Fair Comparison Would Require**:
- Same scale: 2B execution vs 2B preference vs 2B baseline
- Same architecture: All Llama-2B or all phi-2-variants
- Same pretraining data: All trained on Pile/Stack/similar corpus

**Paper's Defense** (line 612):
> "Model availability constraints. Few publicly released preference-aligned code models exist at 2B+ scale."

**Skeptical Rebuttal**:
- Then don't make claims about alignment methods until fair comparison possible
- Or acknowledge: "M1 validation is confounded; cannot distinguish alignment from scale"
- Current framing: M1 PASS, M2 FAIL is misleading when both are confounded

**Recommendation**:
- Downgrade M1 from "VERIFIED" to "SUGGESTIVE (confounded by scale)"
- Add explicit warning in Results: "M1 and M2 results conflate alignment with model scale; matched-scale validation required for mechanistic claims"
- Consider removing M1/M2 validation entirely, focusing only on existence (H-E1) with POC caveat

## 3.3 Overclaiming Audit

### CRED-MAJOR-004: Tone Overclaiming (Hype Disproportionate to POC Evidence)

**Severity**: MAJOR (NOT style issue - credibility issue per instructions)

**Examples of Overclaiming Tone**:

1. **Abstract** (line 3):
> "we demonstrate that alignment methods leave large, robust signatures"
- "Demonstrate" implies real evidence
- Should be: "we show via POC that signatures CAN BE detected when present"

2. **Introduction** (line 38):
> "we validate the existence of alignment signatures with strong experimental evidence"
- "Validate" + "strong evidence" overstates POC simulation
- Should be: "we develop methodology and validate pipeline via POC"

3. **Results** (line 398):
> "Alignment methods create statistically distinguishable performance signatures"
- States as fact, not POC finding
- Should be: "POC simulation confirms methodology detects signatures"

4. **Conclusion** (line 671):
> "Our results confirm: they do. Execution-based methods create strong correctness signatures"
- "Confirm" implies proven
- Should be: "POC suggests signatures are detectable; real validation pending"

5. **Conclusion** (line 687):
> "We provide the first systematic framework for detecting alignment method signatures"
- "Provide" sounds deliverable
- Should be: "We propose and validate via POC a framework"

**Cumulative Impact**: Paper reads like real-model validation despite POC status.

**Comparison to Ground Truth**:
```yaml
critical_limitations:
  poc_simulation:
    severity: "HIGH"
    reason_acceptable: "POC validates methodology feasibility; real inference is planned future work"
```

Ground truth correctly labels this HIGH severity, but paper tone doesn't match severity.

**Recommendation**:
- Global find-replace:
  - "we demonstrate" → "we develop and validate via POC"
  - "we validate" → "we propose and test via POC"
  - "alignment methods create signatures" → "POC suggests signatures are detectable"
  - "our results confirm" → "POC validation suggests"
- Add confidence qualifiers throughout: "preliminary evidence", "POC validation", "pending real-model validation"

### CRED-MAJOR-005: Missing Critical Limitation (Temperature Confound)

**Severity**: MAJOR

**Issue**: Paper uses T=0.8 for generation (line 328) but doesn't acknowledge this may CREATE artificial signatures.

**Why This Matters**:
- High temperature (T=0.8) increases diversity
- More diverse outputs → higher variance → easier clustering
- Low temperature (T=0.2) might show NO signatures (deterministic outputs)

**Missing Analysis**:
- What happens at T=0.2? T=0.5? T=1.0?
- Do signatures exist only at high temperatures, or persist across temperature ranges?
- Is d=7.835 artifact of T=0.8 choice?

**Ground Truth Check**:
```yaml
future_work:
  immediate:
    - "Test signature stability across temperature/sampling settings"
```

Ground truth lists this as FUTURE WORK, but current results may be temperature-dependent artifacts.

**Recommendation**:
- Add to Limitations (Section 6): "Temperature Confound: Results are at T=0.8; signature stability across temperatures untested"
- Acknowledge: "High temperature may artificially inflate signature detectability"
- Suggest: "Future work should validate signatures at T ∈ [0.2, 1.0] to rule out temperature artifacts"

## 3.4 Credibility Check Summary

**FATAL Issues**: 0
**MAJOR Issues**: 5
- CRED-MAJOR-001: "First systematic framework" overclaim (POC ≠ systematic validation)
- CRED-MAJOR-002: No defense against "no real evidence" attack (missing pilot study, citations)
- CRED-MAJOR-003: Unfair baseline (model scale confound affects both M1 and M2)
- CRED-MAJOR-004: Overclaiming tone throughout paper (hype >> evidence)
- CRED-MAJOR-005: Missing temperature confound limitation

**Human Review Notes**: 3
- Line 73: Citation incomplete `livec <bench}`
- Line 599: Friedman 2001 cited but not in bibliography
- Conclusion tone: "fingerprints confirmed" (line 671) too strong for POC

---

# Part 4: Human Review Notes

## 4.1 Typos and Grammar

1. **Line 73**: Citation malformed
   - Current: `livec <bench}`
   - Should be: `livecodebench`

2. **Line 599**: Missing bibliography entry
   - Cited: `friedman2001greedy`
   - Not in References section

## 4.2 Clarity Issues

3. **Table 2 (line 462)**: Model labels unclear
   - "codegen-exec" vs "codegen-pref" - are these the same model analyzed differently, or different checkpoints?
   - Need clarification in caption

4. **Line 328**: Sample size discrepancy
   - Text says k=30 samples
   - But line 138 (Methodology) says k=10 samples
   - Which is correct?

## 4.3 Style Suggestions

5. **Abstract**: Too long (180+ words vs 150 target)
   - Consider condensing methodology description
   - Remove "However, preference-based mechanisms..." sentence (defer to Discussion)

6. **Introduction**: Overly long (1,200+ words)
   - Consider moving Design Justification subsections to Methodology
   - Contributions list (lines 34-44) too detailed (save for body)

7. **Results Section**: Missing figure references
   - Lines 442, 434, 486, 536 reference figures not included
   - Either include figures or remove references

8. **Discussion**: Repetitive
   - Lines 576-588 repeat points from Results section
   - Consider condensing "Key Findings Interpretation" subsection

9. **Conclusion**: Overly long (700+ words)
   - Repetitive with Discussion
   - Consider cutting lines 673-683 (redundant with Discussion limitations)

---

# Part 5: Summary for Revision Agent

## 5.1 Critical Fixes Required (MAJOR Issues)

### Category 1: Accuracy (3 issues)

1. **ACC-MAJOR-001**: Resolve M2 interpretation contradictions
   - **Action**: Choose ONE interpretation (recommend: INCONCLUSIVE due to confound)
   - **Locations**: Abstract line 3, Results line 493, Discussion lines 581-587
   - **Fix**: Replace "refutes hypothesis" with "fails to validate due to confound"

2. **ACC-MAJOR-002**: Fix sample size contradiction
   - **Action**: Correct Methodology line 225-226 to "N=4 total models (1-2 per category)"
   - **Impact**: Weakens statistical power claims
   - **Fix**: Add explicit caveat about exploratory nature

3. **ACC-MAJOR-003**: Reframe Results section as POC validation
   - **Action**: Change RQ1 answer from "signatures exist" to "methodology detects simulated signatures"
   - **Locations**: Entire Results section (lines 398-549)
   - **Fix**: Add disclaimer box: "This section reports POC validation on simulated data"

### Category 2: Engagement (1 issue)

4. **ENG-MAJOR-001**: Disclose POC status earlier
   - **Action**: Move POC disclosure from Section 4 (line 389) to Abstract and Introduction
   - **Abstract fix**: Add "Using proof-of-concept validation with simulated data..."
   - **Introduction fix**: Reframe contributions as "we develop and POC-validate methodology"

### Category 3: Credibility (5 issues)

5. **CRED-MAJOR-001**: Remove "first systematic framework" overclaim
   - **Action**: Change to "we develop a framework" or "we propose and POC-validate"
   - **Remove**: "systematic" (implies comprehensive validation)

6. **CRED-MAJOR-002**: Add defense against "no real evidence" attack
   - **Action**: Add pilot study (even 1 model, 10 tasks) OR add random baseline clustering
   - **Action**: Find and cite 3 methodology papers using synthetic validation
   - **Action**: Reframe RQ1 as methodology validation, not existence proof

7. **CRED-MAJOR-003**: Acknowledge M1 confound
   - **Action**: Downgrade M1 from "VERIFIED" to "SUGGESTIVE (confounded)"
   - **Locations**: Results line 452, Discussion line 579
   - **Fix**: Add warning about scale confound affecting BOTH M1 and M2

8. **CRED-MAJOR-004**: Recalibrate tone throughout paper
   - **Action**: Global replacements:
     - "we demonstrate" → "we develop and POC-validate"
     - "we validate" → "we propose and test via POC"
     - "results confirm" → "POC suggests"
   - **Impact**: 50+ instances across paper

9. **CRED-MAJOR-005**: Add temperature confound limitation
   - **Action**: Add subsection in Discussion limitations
   - **Content**: "Results at T=0.8; signature stability across temperatures untested"
   - **Acknowledge**: High temperature may inflate detectability

## 5.2 High-Priority Human Review Items

10. **Fix citation error** (line 73): `livec <bench}` → `livecodebench`
11. **Add missing bibliography**: `friedman2001greedy` (cited line 599)
12. **Clarify Table 2**: Add caption explaining codegen-exec vs codegen-pref
13. **Resolve sample size**: k=10 (line 138) vs k=30 (line 328) - which is correct?
14. **Include figures**: Add Figure 1 (pipeline) and Figure 2 (3D scatter) or remove references

## 5.3 Structural Recommendations

15. **Add POC Disclaimer Box** before Results section:
```
┌─────────────────────────────────────────────────────────────┐
│ PROOF-OF-CONCEPT VALIDATION                                 │
│ This section reports methodology validation using simulated │
│ performance data. Real-model inference validation is future  │
│ work (Section 6.2). Claims are about methodology capability,│
│ not alignment method behavior.                               │
└─────────────────────────────────────────────────────────────┘
```

16. **Add Honest Assessment Earlier** (currently only in Discussion line 662):
- Move to Introduction after contributions
- "This paper presents proof-of-concept validation; real-model validation is future work"

17. **Reorganize Limitations** (Discussion Section 6.2):
- **Tier 1 (Fundamental)**: POC simulation, model scale confound
- **Tier 2 (Methodological)**: Small sample, single benchmark, temperature confound
- Current structure buries POC simulation among other limitations

## 5.4 Quantitative Fix Summary

| Fix Type | Count | Estimated Time |
|----------|-------|----------------|
| Major rewrites (Results, Abstract, Intro) | 3 sections | 2-3 hours |
| Global tone recalibration (50+ instances) | ~50 changes | 1-2 hours |
| New content (POC defense, temp confound) | 2 subsections | 1 hour |
| Citation/typo fixes | 5 fixes | 30 minutes |
| Table/figure updates | 3 items | 1 hour |
| **TOTAL REVISION TIME** | - | **5-7 hours** |

## 5.5 Decision Points for Revision Agent

**Decision 1**: M2 status
- Option A: INCONCLUSIVE (cannot conclude due to confound) [RECOMMENDED]
- Option B: REFUTED with caveat (hypothesis failed, confound explains why)

**Decision 2**: M1 credibility
- Option A: VERIFIED (accept phi-2 dominance as evidence) [CURRENT]
- Option B: SUGGESTIVE (acknowledge scale confound weakens claim) [RECOMMENDED]

**Decision 3**: POC framing
- Option A: Methodology validation paper (focus on framework, not findings) [RECOMMENDED]
- Option B: Preliminary findings paper (accept weak evidence, emphasize future validation)

**Decision 4**: Scope reduction
- Option A: Remove M1/M2 validation entirely, focus only on H-E1 (signature detection methodology)
- Option B: Keep M1/M2 but downgrade to "exploratory analysis" [RECOMMENDED]

---

# Appendix: Detailed Issue Checklist

## Issues Requiring Immediate Action (MAJOR)

- [ ] **ACC-MAJOR-001**: Fix M2 contradictions (refuted vs inconclusive vs uninterpretable)
- [ ] **ACC-MAJOR-002**: Correct sample size (4 per category → 4 total)
- [ ] **ACC-MAJOR-003**: Reframe Results as POC validation (not alignment findings)
- [ ] **ENG-MAJOR-001**: Disclose POC status in Abstract/Introduction (not Section 4)
- [ ] **CRED-MAJOR-001**: Remove "first systematic framework" overclaim
- [ ] **CRED-MAJOR-002**: Add defense vs "no real evidence" attack (pilot study or citations)
- [ ] **CRED-MAJOR-003**: Acknowledge M1 confound (scale + alignment conflated)
- [ ] **CRED-MAJOR-004**: Recalibrate overclaiming tone (50+ instances)
- [ ] **CRED-MAJOR-005**: Add temperature confound limitation

## Issues for Polishing (Human Review)

- [ ] Fix citation `livec <bench}` (line 73)
- [ ] Add missing biblio `friedman2001greedy` (line 599)
- [ ] Clarify Table 2 caption (codegen-exec vs codegen-pref)
- [ ] Resolve k=10 vs k=30 discrepancy (lines 138, 328)
- [ ] Include Figure 1 and Figure 2 or remove references
- [ ] Trim Abstract to 150 words (currently 180+)
- [ ] Condense Introduction (currently 1,200+ words)
- [ ] Reduce Discussion repetition (lines 576-588)
- [ ] Shorten Conclusion (currently 700+ words)

---

# Final Recommendation

**Verdict**: MAJOR_REVISION required before acceptance.

**Rationale**:
The paper presents valuable methodology (backward inference for signature detection) and demonstrates intellectual honesty (transparent POC acknowledgment, M2 failure reporting). However, the gap between POC claims and actual evidence creates major credibility issues that prevent acceptance in current form.

**Key Strengths to Preserve**:
1. Honest reporting of POC simulation and M2 failure
2. Strong narrative coherence (hook → insight → evidence)
3. Mechanistic grounding (feedback signal theory)
4. Transparent limitation discussion

**Key Weaknesses to Address**:
1. Overclaiming tone disproportionate to POC evidence (50+ instances)
2. Late POC disclosure (damages reader trust)
3. Internal contradictions (M2 status, sample size)
4. Missing defenses against obvious attacks ("no real evidence")

**Post-Revision Potential**: If major issues addressed, paper could be CONDITIONAL_ACCEPT for methodology track (not empirical findings track).

**Alternative Path**: If authors cannot address POC limitations (e.g., cannot run pilot study on 1 real model), consider reframing as:
- **Workshop paper**: "Proposed Methodology for Signature Detection (POC Validation)"
- **Short paper**: Focus on framework description, defer validation to future work
- **Technical report**: Release POC results without publication venue pressure

Current framing as full research paper creates expectations the POC evidence cannot meet.

---

**Review Completed**: 2026-03-18
**Reviewer**: Adversary Agent v2.0 (Three-Persona Framework)
**Next Step**: Pass to Revision Agent for MAJOR_REVISION implementation
