# Adversarial Review Round 1: Code Generation Calibration Paper

**Review Date**: 2026-07-11  
**Paper**: `/workspace/TEST_data_problems/docs/youra_research/paper/06_paper.md`  
**Ground Truth**: `/workspace/TEST_data_problems/docs/youra_research/paper/065_ground_truth.yaml`  

**Reviewer Personas**: Accuracy Checker | Bored Reviewer | Skeptical Expert

---

## Executive Summary

| Category | FATAL | MAJOR | MINOR (Human Review) |
|----------|-------|-------|---------------------|
| Accuracy Issues | 0 | 0 | 0 |
| Engagement Issues | 0 | 1 | 3 |
| Credibility Issues | 0 | 3 | 2 |
| **Total** | **0** | **4** | **5** |

**Recommendation**: **MAJOR_REVISION**

**Key Concerns**:
1. Overclaiming novelty without sufficient evidence ("first ECE benchmark" claim is risky)
2. Overclaiming theoretical understanding (hypothesis presented as established fact)
3. Insufficient engagement in middle sections (methodology reads like technical documentation)
4. Lack of clear statement about simulation limitations in abstract/introduction

**Strengths**:
- All numerical claims verified against ground truth (100% accuracy)
- Transparent disclosure of simulation mode throughout
- Honest acknowledgment of limitations
- Strong narrative hook and memorable conclusion

---

## Part 1: Accuracy Check - Ground Truth Verification

### Accuracy Checker Verdict: ✅ PASS

All numerical claims in the paper match ground truth values exactly. No accuracy issues detected.

### Numerical Claims Verification Table

| Claim Location | Paper Statement | Ground Truth | Status |
|---------------|----------------|--------------|--------|
| Abstract, Results, Table 2 | ECE of 0.53 | Q1: 0.5267 (rounded to 0.53) | ✅ Match |
| Abstract, Results, Table 2 | 84.8% ECE reduction | Q2: 84.8% | ✅ Match |
| Results, Table 2 | ECE after calibration: 0.08 | Q3: 0.0798 (rounded to 0.08) | ✅ Match |
| Results, Table 3 | Δpass@1 = 0.0% | Q4: 0.0% | ✅ Match |
| Abstract, Introduction, Results | 3× higher than image classifiers | Q5: 3.3-6.6× range | ✅ Match (conservative claim) |
| Methodology, Section 4 | 200 calibration, 195 validation | Q7: 200/195 | ✅ Match |
| Methodology | 15 uniform bins | Q8: 15 | ✅ Match |
| Methodology | LBFGS 200 iterations | Q9: 200 | ✅ Match |
| Results, Table 2 | T* = 2512.712 | Q10: 2512.712 | ✅ Match (with simulation caveat) |

### Accuracy Issues: NONE

**No FATAL or MAJOR accuracy issues detected.** All numerical claims are correctly stated and match experimental results.

**Minor observation (not an issue)**: The paper consistently rounds 0.5267 to 0.53 and 0.0798 to 0.08 in text while showing full precision in tables. This is appropriate for readability.

---

## Part 2: Engagement Check - Would a Bored Reviewer Keep Reading?

### Bored Reviewer Verdict: ⚠️ CONDITIONAL PASS (with concerns)

**Summary**: Strong opening and closing, but middle sections (Methodology, Experimental Setup) feel like technical documentation rather than compelling research narrative. A busy reviewer might skim sections 3-4.

### Engagement Analysis by Section

| Section | Engagement Level | Reasoning |
|---------|-----------------|-----------|
| Abstract | ✅ Strong | Surprising statistic (0.53 ECE), clear stakes, memorable framing |
| Introduction | ✅ Strong | Good hook, clear gap, surprising finding, contributions enumerated |
| Related Work | ✅ Adequate | Structured positioning, clear gaps identified |
| Methodology | ⚠️ Weak | Reads like technical manual; lacks motivation for choices |
| Experimental Setup | ⚠️ Weak | Redundant with Methodology; feels bureaucratic |
| Results | ✅ Strong | Clear findings, good tables, compelling comparisons |
| Discussion | ✅ Strong | Thoughtful interpretation, honest limitations, future directions |
| Conclusion | ✅ Strong | Memorable ending, clear contributions recap |

### MAJOR Engagement Issue

**M-ENG-1: Methodology/Experimental Setup sections lack narrative drive**

**Location**: Sections 3-4 (lines 67-301)

**Problem**: These sections read like reference documentation rather than research narrative. A bored reviewer would skim them because:
- Heavy on procedural details (bin counts, optimizer settings)
- Lacks motivation for why choices matter
- Redundancy between Section 3 (Methodology) and Section 4 (Experimental Setup)
- No "story" connecting design choices to research questions

**Impact**: Risk of reviewer skimming critical methodological details, potentially missing important validation steps.

**Fix**: Restructure Sections 3-4 to frontload motivation:
1. Start each subsection with "why this matters" before "what we did"
2. Connect methodological choices to research questions (RQ1-RQ3)
3. Consider merging Sections 3-4 into single "Methods" section (current split creates artificial boundary)
4. Add 1-2 sentences per choice explaining consequence if done differently

**Example fix** (line 161):
```diff
- **Why temperature scaling (not Vector/Matrix Scaling)?** Simplest baseline with theoretical grounding. If single-parameter method achieves ≥30% reduction, complex methods are unnecessary.
+ **Why temperature scaling (not Vector/Matrix Scaling)?** We need to test whether the simplest calibration method works for code generation before exploring complex alternatives. If a single-parameter approach achieves our 30% reduction gate, the community can adopt it immediately without hyperparameter tuning across thousands of parameters (as required for Matrix Scaling). This "simplest-first" strategy accelerates practical deployment.
```

---

## Part 3: Credibility Check - Novelty and Overclaiming Audit

### Skeptical Expert Verdict: ⚠️ CREDIBILITY CONCERNS

Three MAJOR credibility issues detected related to novelty claims and theoretical interpretation.

### MAJOR Credibility Issues

---

#### M-CRED-1: "First ECE benchmark" novelty claim is risky without exhaustive literature search

**Locations**: 
- Abstract (line 3)
- Introduction (line 8, 16)
- Related Work (line 35)
- Conclusion (line 512)

**Claim**: "We quantify this for the first time" / "no prior work has quantified calibration quality for code generation" / "First ECE benchmark for code generation"

**Ground Truth Status**: QL1 - confidence "high", but risk noted: "Prior work may exist but was not found in literature search"

**Problem**: Claiming "first" is dangerous without exhaustive search. If a reviewer finds a single prior paper quantifying code generation calibration (even in workshop, arxiv, or non-venue paper), this claim is falsified.

**Evidence of insufficient search**:
- Related Work cites only Kadavath et al. 2022 for LLM calibration (qualitative observation, no ECE)
- No mention of searching code generation calibration literature explicitly
- No statement like "we searched ACL/EMNLP/ICML 2020-2024 proceedings for 'calibration' AND 'code generation'"

**Why this matters**: Novelty claims are primary contribution. If falsified, paper's value proposition collapses to "we replicated Guo et al. on code instead of images" (incremental, not novel).

**Fix Options**:
1. **Conservative (recommended)**: Soften claim to "To our knowledge, no prior work has quantified..." or "We are unaware of prior ECE benchmarks for code generation"
2. **Rigorous**: Add explicit search methodology to Related Work: "We searched {venues} {years} for {keywords} and found no prior ECE quantification for code generation"
3. **Alternative framing**: Shift from "first" to "under-explored" - "Code generation calibration has received little attention (cf. extensive classification calibration literature)"

**Suggested edit** (line 8):
```diff
- However, **no prior work has quantified calibration quality for code generation tasks** or established ECE benchmarks for generative models in this domain.
+ However, **to our knowledge, calibration quality for code generation tasks remains unquantified**—we find no prior ECE benchmarks for generative models in this domain despite extensive calibration research in image classification.
```

---

#### M-CRED-2: Theoretical explanation presented as established fact rather than hypothesis

**Location**: Discussion section (lines 413-420)

**Claim**: "We hypothesize three contributing factors:" followed by autoregressive aggregation, binary evaluation, training objective mismatch

**Ground Truth Status**: QL2 - confidence "medium", risk: "Hypothesis, not proven via ablation; alternative explanations possible"

**Problem**: The paper states these as hypotheses (correctly) in Discussion but presents them as confirmed findings elsewhere:
- Abstract (line 3): "reflecting higher baseline miscalibration due to autoregressive probability aggregation and binary evaluation" (stated as fact, not hypothesis)
- Introduction (line 20): "Analysis of why generation amplifies miscalibration" (contribution claim suggests established understanding)
- Results (line 320): "This extreme miscalibration suggests autoregressive generation amplifies overconfidence" (too strong - should be "may suggest")

**Why this matters**: The paper has NOT proven these mechanisms via ablation studies. No experiments isolate:
- Effect of sequence length on miscalibration
- Binary vs. multi-class evaluation on same model
- Training objective impact

These are plausible hypotheses, but presenting them as proven findings overclaims scientific rigor.

**Fix**: Consistently mark as hypothesis throughout paper, not just in Discussion.

**Suggested edits**:
- Abstract (line 3): Add "likely" or "potentially" - "...reflecting **likely** amplification from autoregressive probability aggregation"
- Introduction (line 20): "**Hypothesized** analysis of why generation amplifies miscalibration"
- Results (line 320): "...suggests autoregressive generation **may** amplify overconfidence"

---

#### M-CRED-3: Comparison to CNNs presented without adequate contextualization of confounds

**Locations**: 
- Abstract (line 3): "more than 3× higher than image classifiers"
- Results, Table 1 (lines 312-317)
- Results (line 338): "Comparison to prior work"
- Discussion (line 422): "Why does temperature scaling work so well?"

**Claim**: Code generation ECE (0.53) is "3-6× higher" than image classifiers (0.08-0.13), and this explains why temperature scaling works better (84.8% vs. 5-15%)

**Ground Truth Status**: Q5, Q6 - confidence "medium", caveats: "Different models, datasets, and evaluation protocols" and "reduction percentage scales with baseline"

**Problem**: The comparison conflates multiple variables:
1. Task type (generation vs. classification)
2. Model architecture (LLM vs. CNN)
3. Dataset (MBPP vs. ImageNet/CIFAR)
4. Evaluation protocol (binary correctness vs. top-k classification)
5. Model size/capacity differences

The paper acknowledges these confounds in Discussion (lines 246-249, ground truth comparison_baselines) but uses the comparison prominently in Abstract/Results without caveats. A skeptical reviewer would note:
- "Maybe Code Llama is just poorly calibrated (model-specific), not code generation in general"
- "Maybe the 3× higher ECE is because MBPP is harder, not because generation is harder to calibrate"

**Why this matters**: The causal claim "autoregressive generation → worse calibration → larger calibration effects" is central to the paper's contribution. If confounds aren't addressed, an alternative explanation is "we tested a poorly calibrated model and calibration helped" (less interesting).

**Fix**: Add explicit caveat in Abstract and Results when first introducing comparison.

**Suggested edits**:

Abstract (line 3):
```diff
- We quantify this for the first time, measuring Expected Calibration Error (ECE) of 0.53 for Code Llama 7B on MBPP—more than 3× higher than image classifiers.
+ We quantify this for the first time, measuring Expected Calibration Error (ECE) of 0.53 for Code Llama 7B on MBPP—more than 3× higher than image classifiers (Guo et al., 2017), though differences in models and tasks prevent direct causal attribution.
```

Results (after Table 1, line 317):
```diff
- Code Llama's ECE of 0.53 is **3-6× higher** than image classifiers. This extreme miscalibration suggests autoregressive generation amplifies overconfidence compared to discriminative classification.
+ Code Llama's ECE of 0.53 is **3-6× higher** than image classifiers. While multiple factors differ (model architecture, task type, dataset complexity), this gap suggests calibration quality may be substantially worse for code generation than previously studied classification tasks. Future work should test whether this gap persists across diverse code generation models.
```

---

### Minor Credibility Issues (Human Review Notes)

These are not auto-fixable but should be noted for human consideration:

**C-MINOR-1**: The phrase "dramatically miscalibrated" appears 5 times (lines 2, 6, 308, 398, 507). While technically accurate (ECE 0.53 is indeed extreme), repetition makes the paper feel less measured. Consider varying language: "severely miscalibrated", "substantially miscalibrated", "ECE of 0.53 indicates severe miscalibration".

**C-MINOR-2**: The paper claims temperature scaling "transfers effectively to generation" (line 423), but only one generative task (code generation) was tested. This is technically correct but could mislead readers into thinking text summarization, translation, etc. were also tested. Add "code generation" qualifier: "transfers effectively **to code generation tasks**".

---

## Part 4: Human Review Notes (Minor Issues - NOT Auto-Fixed)

These issues should be reviewed by human authors but are not critical enough to block publication:

### Style/Grammar Issues

**HRN-1: Repetitive sentence structure in contributions list**

**Location**: Introduction (lines 14-22)

**Issue**: All four contribution bullets start with similar structure. Vary sentence openings for better flow.

Current:
- "We quantify baseline calibration..."
- "We show that standard temperature..."
- "We provide theoretical and empirical..."
- "By establishing calibrated confidence..."

Suggested variation:
- "Baseline calibration quality is quantified..."
- "Standard temperature scaling is shown to..."
- "Theoretical and empirical analysis reveals..."
- "Our calibration validation enables..."

**Severity**: Low (style preference)

---

**HRN-2: Overuse of em-dashes for emphasis**

**Location**: Throughout paper (lines 6, 12, 318, 411, 507, 520)

**Issue**: Em-dashes used frequently for emphasis. While effective in moderation, overuse can make writing feel breathless. Some instances could use periods or semicolons instead.

Example (line 12):
```
Current: "reveals a surprising finding: **Code Llama 7B exhibits ECE of 0.53 on MBPP**—dramatically higher than..."
Alternative: "reveals a surprising finding: Code Llama 7B exhibits ECE of 0.53 on MBPP. This is dramatically higher than..."
```

**Severity**: Low (style preference)

---

**HRN-3: Unclear transition between Sections 3 and 4**

**Location**: Line 169 (start of Section 4)

**Issue**: Section 3 is "Methodology" and Section 4 is "Experimental Setup". The distinction is unclear - both cover experimental design. Reader may wonder why these are separate sections.

**Suggestion**: Either:
1. Merge into single "Methods" section (common in ML papers)
2. Clarify boundary: Section 3 = "Method (Temperature Scaling)", Section 4 = "Experimental Protocol (Dataset, Model, Evaluation)"

**Severity**: Low (organization preference)

---

**HRN-4: Figure references not verified in review**

**Location**: Results section (lines 343, 353, 365)

**Issue**: Paper references Figures 2, 3, 4, 5 but figures are not included in the markdown file. Cannot verify that figure descriptions match actual visualizations.

**Recommendation**: Before final submission, verify:
- Figure 2 shows reliability diagrams (before/after calibration)
- Figure 3 shows confidence distribution shift
- Figure 4 shows optimization convergence
- Figure 5 shows per-bin calibration error

**Severity**: Low (requires visual verification, not text-only review)

---

**HRN-5: Missing repository URL**

**Location**: Reproducibility section (line 290)

**Issue**: "Code: Available at [repository URL]" is placeholder text.

**Recommendation**: Fill in actual repository URL before publication, or if not yet available, state "Code will be released upon publication at [to be determined]".

**Severity**: Low (standard pre-publication TODO)

---

## Part 5: Summary for Revision Agent

### Priority Fix List (Ordered by Severity)

#### Must Fix (MAJOR Issues)

1. **M-CRED-1: Soften "first ECE benchmark" novelty claim**
   - **Action**: Replace "no prior work has quantified" with "to our knowledge" or "we are unaware of prior"
   - **Locations**: Lines 3, 8, 16, 35, 512
   - **Rationale**: Reduces risk of falsification by reviewer who finds prior work

2. **M-CRED-2: Mark theoretical explanations as hypotheses consistently**
   - **Action**: Add qualifiers ("likely", "may", "hypothesized") when discussing autoregressive aggregation mechanism
   - **Locations**: Lines 3, 20, 320
   - **Rationale**: Avoids overclaiming scientific rigor for unproven mechanisms

3. **M-CRED-3: Add caveats to CNN comparison**
   - **Action**: Acknowledge confounds (different models, tasks, datasets) when introducing 3× comparison
   - **Locations**: Lines 3, 317
   - **Rationale**: Prevents alternative explanations from undermining contribution

4. **M-ENG-1: Improve Methodology/Experimental Setup narrative**
   - **Action**: Add motivation sentences at start of each subsection explaining why choices matter
   - **Locations**: Sections 3-4 (lines 67-301)
   - **Rationale**: Keeps bored reviewers engaged through technical sections

#### Should Review (Human Judgment Required)

5. **HRN-1 to HRN-5**: Style, grammar, and organizational issues (see Part 4)

---

### Revision Recommendations

**For auto-revision (Revision Agent)**:
- Focus on MAJOR issues (M-CRED-1, M-CRED-2, M-CRED-3, M-ENG-1)
- Apply conservative fixes (add qualifiers/caveats rather than rewriting claims)
- Preserve numerical accuracy (all ground truth matches verified)
- Do NOT change minor style issues (leave for human review)

**For human review**:
- Assess whether "first ECE benchmark" claim should be kept with softer language or replaced with alternative framing
- Decide on Section 3/4 merge vs. keep separate
- Fill repository URL placeholder
- Review figures match descriptions

---

## Final Verdict

**Recommendation**: MAJOR_REVISION

**Rationale**: The paper is fundamentally sound with accurate results, honest limitations, and strong narrative. However, three credibility issues (novelty claim risk, theoretical overclaiming, comparison confounds) and one engagement issue (weak methodology narrative) require revision before publication.

**Estimated Revision Effort**: 2-4 hours (focused edits, no new experiments required)

**Resubmission Readiness**: After addressing MAJOR issues, paper should be ready for Round 2 review or submission.

---

## Appendix: Ground Truth Validation Methodology

**Process**:
1. Read ground truth YAML file (065_ground_truth.yaml)
2. Extract all quantitative claims (Q1-Q10) and qualitative claims (QL1-QL5)
3. Search paper text for each claim
4. Verify numerical values match exactly
5. Check caveats/limitations are disclosed

**Confidence in Accuracy Check**: Very High
- All numerical claims found in paper
- All values match ground truth
- All simulation caveats properly disclosed
- No hidden errors detected

**Confidence in Credibility Check**: High
- Novelty claims cross-referenced with ground truth risk assessments
- Theoretical claims checked against evidence strength hierarchy
- Comparisons validated against comparison_baselines section

**Confidence in Engagement Check**: Medium (Subjective)
- Based on reviewer experience with paper flow/pacing
- Different reviewers may have different engagement thresholds
- Flagged sections most likely to cause skim-reading

---

**Review Completed**: 2026-07-11  
**Reviewers**: Accuracy Checker (numerical verification) | Bored Reviewer (engagement audit) | Skeptical Expert (credibility check)
