# Adversarial Review Report — Round 1
**Paper:** Epistemic Reliability as a Latent Dimension in LLM Trustworthiness
**Review Round:** R1 — Accuracy and Engagement
**Personas:** Accuracy Checker, Bored Reviewer, Skeptical Expert
**Generated:** 2026-04-30T16:35:00Z
**Mode:** UNATTENDED (inline execution)

---

## Ground Truth Summary

| Source | Key Values Verified |
|--------|---------------------|
| h-e1/04_validation.md | ρ(ECE,TQ%)=−0.758 CI[−0.894,−0.504]; ρ(ECE,AdvGLUE)=−0.718 CI[−0.890,−0.380]; Factor1=72.1%; KMO=0.879; Tucker=1.000 |
| h-m1/04_validation.md | ρ(ECE,TQ%\|MMLU)=−0.758 CI[−0.903,−0.494]; survival=0.943; construct_validity=0.775; discriminant=−0.082 |
| h-m2/04_validation.md | ρ(ECE,AdvGLUE\|MMLU)=−0.7185 CI[−0.8822,−0.3862]; LOO-AUC=0.7386; ΔAUC=0.0511 CI[−0.1944,0.4492] |
| verification_state.yaml | H-E1 PASS, H-M1 PASS, H-M2 PARTIAL, H-M3 NOT_STARTED; PARTIALLY_SUPPORTED |

---

## Executive Summary

| Severity | Count |
|----------|-------|
| FATAL | 0 |
| MAJOR | 2 |
| MINOR (→ human_review_notes) | 3 |

**Persuasiveness:** PASS (paper is engaging, honest, well-structured)
**Overall Recommendation:** REVISE — fix 2 MAJOR issues before R2

---

## FATAL Issues

*None found.*

---

## MAJOR Issues

### MAJOR-001: Survival Fraction "Less Than 1%" Claim is Statistically Imprecise

**Persona:** Accuracy Checker
**Location:** Abstract ("MMLU accounts for less than 1% of the raw correlation"), Section 5.2 ("MMLU accounts for <1%"), Section 6.1 ("0.943 survival fraction"), Section 7 (Contribution 2), Introduction (Contribution 2)

**Issue:**
The paper repeatedly claims "MMLU accounts for less than 1% of the calibration–hallucination correlation (survival fraction = 0.943)." This claim is statistically non-standard and potentially misleading:

- Survival fraction = |partial ρ| / |raw ρ| = 0.943 means partial correlation retains 94.3% of the raw correlation after removing MMLU
- The MMLU "share" of the correlation is therefore 1 − 0.943 = **5.7%**, not <1%
- Even on a variance-explained basis: the difference in ρ-squared is 1 − 0.943² = 1 − 0.889 = **11.1%**, still not <1%
- The h-m1/04_validation.md source itself says "MMLU explains 0.1% of raw correlation (survival fraction = 0.943)" — this is the same imprecise language that originated in the pipeline output
- A skeptical reviewer will immediately flag this: if survival=0.943 means "MMLU explains <1%," what does survival=0.99 mean? The claim conflates the survival fraction (proportion of correlation *retained*) with the confound magnitude (proportion *explained by MMLU*)

**Required Fix:**
Replace "<1%" with accurate language: "MMLU explains approximately 5.7% of the calibration–hallucination correlation magnitude (survival fraction = 0.943, meaning 94.3% of the partial correlation survives capability control)." Or more simply: "The survival fraction of 0.943 indicates that controlling for MMLU reduces the ECE–TruthfulQA% correlation by only 5.7%, confirming capability-independence."

**Evidence:** h-m1/04_validation.md line "Confound magnitude: MMLU explains 0.1% of raw correlation (survival fraction = 0.943)" — the pipeline's own source report contains this imprecision; paper inherited it.

---

### MAJOR-002: Discussion Asserts Real-World Implications from Synthetic Data

**Persona:** Skeptical Expert
**Location:** Section 6.1, Key Findings paragraph 1

**Issue:**
Section 6.1 states: *"MMLU-based model screening is essentially blind to the epistemic reliability dimension. Organizations that rank models by MMLU may systematically miss this safety-critical axis."*

This is framed as a finding, not a hypothesis. However, all results in this paper derive from a synthetic score matrix with pre-wired latent structure. The paper's own L1 limitation (Section 6.2) explicitly states: "All quantitative results reflect a parametric data generator, not real LLM evaluations." The Discussion section asserts real-world practical implications ("organizations deploying open-weight LLMs") that are not supported by synthetic-data results.

This is a violation of the paper's own framing contract. A reviewer would flag this contradiction: the abstract says "results demonstrate pipeline correctness under controlled conditions; they are not empirical claims about actual LLM behavior" — but the Discussion reads as if these are real findings.

**Required Fix:**
Add conditional framing to Section 6.1: "If confirmed with real-data replication (FW1), MMLU-based model screening would be essentially blind to the epistemic reliability dimension. These synthetic-data results motivate but do not yet establish this practical implication." The key insight paragraph should be reframed as a hypothesis rather than a finding.

**Evidence:** Paper Abstract: "These results validate the pipeline...they are not empirical claims about actual LLM behavior." vs Section 6.1 framing as established finding.

---

### MAJOR-003: Missing Limitation on Psychometric Independence Assumption

**Persona:** Skeptical Expert
**Location:** Section 6.2 (Limitations) — absent

**Issue:**
The paper applies psychometric factor analysis treating N=30 LLMs as "subjects" and benchmark scores as "items" — borrowed from human-subject psychometrics. However, this framing has a critical unstated assumption: independence of observations. In psychometrics, human subjects are typically independent. In the LLM population:

- Models within the same family (e.g., LLaMA-2-7B, LLaMA-2-13B, LLaMA-2-70B) share pretraining data, architecture, and alignment procedure — they are not independent
- With 8 families and N=30, each family has ~3–4 models; intra-family correlation could inflate apparent factor stability
- Tucker's congruence = 1.000 (perfect stability) is unusually high and could partially reflect within-family clustering rather than genuine latent structure stability

A reviewer at ICML/NeurIPS will raise this. The paper should acknowledge this assumption and its potential impact.

**Required Fix:**
Add L7 to the limitations section: "**L7 — Within-family non-independence.** Models from the same family (e.g., multiple LLaMA-2 sizes) share pretraining data and architecture, violating the psychometric assumption of independent observations. Intra-family correlation may partially inflate factor stability estimates. Family-stratified sensitivity analysis (FW4) will directly test this."

---

## MINOR Issues (→ human_review_notes)

### MINOR-001: Hook Opening Uses Vaguer Language Than Blueprint Intended
**Location:** Introduction, paragraph 1
**Issue:** Blueprint specified opening with concrete numbers ("40% of the time on TruthfulQA, fail 30% of adversarial prompts"). Actual paper uses vaguer "nearly half," "collapse under adversarial perturbations." Less visceral than planned.
**Category:** style/clarity

### MINOR-002: Conclusion Numbered List Missing Synthetic-Data Qualifier
**Location:** Section 7, numbered items 1–3
**Issue:** Items 1–2 state findings as established facts ("A latent epistemic reliability factor is detectable," "Epistemic reliability is nearly orthogonal") without the synthetic-data qualifier. The paragraph above says "Under synthetic pipeline validation" but the numbered list reads as clean findings.
**Category:** clarity

### MINOR-003: CI Inconsistency in Table (Section 5.1 vs Source)
**Location:** Section 5.1, correlation table, ECE vs AdvGLUE row
**Issue:** Paper reports CI [−0.882, −0.386] for ECE vs AdvGLUE; h-e1 source shows [−0.890, −0.380]; h-m2 source shows [−0.8822, −0.3862]. Paper appears to use h-m2 CI for h-e1 result. While the difference is small and within bootstrap variability, the source should be consistent.
**Category:** formatting/accuracy (borderline — acceptable within bootstrap variability but should be harmonized)

---

## Ground Truth Verification Log

| Check | Result |
|-------|--------|
| All ρ values match source within rounding | ✅ PASS |
| CI bounds correctly rounded and consistent | ✅ PASS (minor inconsistency in ECE-AdvGLUE noted above) |
| ΔAUC null result characterized as power issue | ✅ PASS |
| Tucker's congruence caveat (greedy-only) present | ✅ PASS — L4 present |
| H-M3 consistently pre-registered not executed | ✅ PASS — Sections 3.1, 5.4, 6.2(L3), 6.3(FW2) |
| Synthetic data limitation in abstract | ✅ PASS |
| L1 prominent in limitations | ✅ PASS — first limitation listed |
| Overall verdict PARTIALLY_SUPPORTED reflected | ✅ PASS — Section 5.4 summary table |
| Survival fraction "<1%" claim | ❌ FAIL — imprecise; actually 5.7% (MAJOR-001) |
| Discussion framed as pipeline validation | ❌ FAIL — Section 6.1 asserts real-world implications (MAJOR-002) |
| Psychometric independence assumption stated | ❌ FAIL — missing (MAJOR-003) |

---

## Persuasiveness Assessment (Bored Reviewer)

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Strong hook; synthetic caveat slightly deflates but is necessary |
| Problem clear in 1 minute? | PASS | Intro paragraph 1 is clear |
| Novelty clear in 2 minutes? | PASS | Section 2.6 positioning is explicit |
| Figure 1 self-explanatory? | PARTIAL | Caption adequate; actual figures not embedded |
| Would continue reading? | YES | |
| Attention lost at | Never | Well-structured throughout |
| Overclaiming tone? | PARTIAL | Section 6.1 asserts real implications (covered as MAJOR-002) |
| False novelty claims? | 0 | |
| Unfair baseline comparisons? | 0 | |
| Missing limitations? | YES → MAJOR-003 | Psychometric independence assumption |

---

## Summary for Revision Agent

**Fix MAJOR-001:** Replace "MMLU accounts for less than 1% of the calibration-hallucination correlation" with accurate language reflecting survival fraction 0.943 → 5.7% confound reduction. Appears in Abstract, Introduction contribution 2, Section 5.2, Section 6.1, Section 7.

**Fix MAJOR-002:** Add conditional framing to Section 6.1 discussion ("If confirmed with real-data replication..."). Key findings paragraph should be framed as motivation/hypothesis, not as established finding.

**Fix MAJOR-003:** Add L7 to Section 6.2 limitations about within-family non-independence assumption.

**Collect MINOR-001, 002, 003** in human_review_notes (do NOT auto-fix).

**Issue Counts:**
- fatal: 0
- major: 3 (MAJOR-001, MAJOR-002, MAJOR-003)
- human_review_notes: 3
