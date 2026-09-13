# Adversarial Review - Round 1

**Paper:** Geometric Signatures of Spurious Correlation Robustness  
**Reviewed:** 2026-04-24T20:15:00Z  
**Reviewer Version:** Adversary Agent v2.0

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy | 0 | 1 | OK |
| Engagement | 0 | 2 | NEEDS_WORK |
| Credibility | 0 | 3 | NEEDS_WORK |
| **TOTAL** | **0** | **6** | **NEEDS_WORK** |

**Recommendation:** MINOR_REVISION

**Overall Assessment:** The paper is factually accurate with excellent numerical integrity and honest limitation disclosure. However, it suffers from engagement failures (weak hook, unclear novelty within 2 minutes) and credibility issues (overclaiming scope, misleading "label-free" framing, and disproportionate language given proof-of-concept limitations). No fatal flaws prevent acceptance, but significant improvements needed for competitive acceptance at ICML.

---

## Part 1: Accuracy Check (Persona 1)

### Ground Truth Summary

| Metric | Paper Claims | Ground Truth | Match? |
|--------|--------------|--------------|--------|
| ERM Alignment | 72% (0.7234) | 0.7234 | ✓ |
| DRO Alignment | 32% (0.3156) | 0.3156 | ✓ |
| Delta (pp) | 41 pp (Abstract), 40.8 pp (Results) | 40.78 pp | ✓ (minor rounding) |
| Cohen's d | 1.87 | 1.87 | ✓ |
| p-value | 0.0023 | 0.0023 | ✓ |
| Outlier increase | 53% | 53.33% | ✓ |
| ERM outliers | 23 | 23 | ✓ |
| DRO outliers | 15 | 15 | ✓ |
| SGD bias | 0.15 | 0.15 | ✓ |
| SGD bias p-value | 0.023 | 0.023 | ✓ |
| ERM WGA | 72.3% | 72.3% | ✓ |
| DRO WGA | 88.7% (Intro), 88% (Intro) | 88.7% | ✓ (one rounded) |
| H-M2 status | "untested with random basis" | UNTESTED (random basis) | ✓ |
| H-M4 status | "refuted" (ρ=0.045, p=0.85) | REFUTED (ρ=0.0447, p=0.8517) | ✓ |

**Integrity Score: EXCELLENT** — All numerical claims verified. The paper accurately represents experimental results with appropriate rounding and honest limitation disclosure.

### FATAL Issues - Accuracy

**None identified.** All numerical claims match ground truth within acceptable rounding precision.

### MAJOR Issues - Accuracy

**MAJOR-ACC-01: Inconsistent WGA claim in Introduction**

- **Location:** Introduction, paragraph 1 (line 31)
- **Issue:** "a model trained with robust optimization achieves 88% worst-group accuracy"
- **Evidence:** Ground truth shows DRO WGA = 88.7%. Paper rounds to 88% in Introduction but uses 88.7% correctly in Table 1 and Section 5.4.
- **Impact:** Minor inconsistency creates confusion about actual baseline performance. While 88% vs 88.7% is trivial numerically, consistency matters for reader trust.
- **Suggested Fix:** Use 88.7% consistently throughout, or use "~89%" if rounding is necessary for readability.

---

## Part 2: Engagement Check (Persona 2)

### Bored Reviewer Verdict

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | ✗ | Technical jargon-heavy, no clear "wow" insight until sentence 5 |
| Problem clear in 1 min? | ✓ | Yes — spurious correlations harm worst-group accuracy |
| Novelty clear in 2 min? | ✗ | Buried as "Marchenko-Pastur-defined alignment" — requires ML background to parse |
| Figure 1 self-explanatory? | ✗ | No Figure 1 in main text (referenced as "Figure 1" but shows spectra, not insight) |
| Would continue reading? | ✓ | Barely — problem is relevant, but introduction feels like a methods paper, not an insight paper |

**Attention Lost At:** Section 2.1 Related Work — reads like a literature review, not positioning a novel contribution

**Reading Time Estimates:**
- Abstract: 2 min 15 sec — too long, too dense
- Introduction (to understand problem): 4 min — acceptable
- Introduction (to understand novelty): 8 min — too long, requires re-reading

### FATAL Issues - Engagement

**None identified.** Paper is readable and coherent, though not exciting.

### MAJOR Issues - Engagement

**MAJOR-ENG-01: Abstract lacks accessible hook**

- **Location:** Abstract, sentences 1-3
- **Issue:** Opens with problem statement, but no compelling statistic or concrete example. "Deep neural networks often exploit spurious correlations" is generic. Compare to Introduction's "89% average but 72% worst-group" — much more concrete.
- **Why this matters:** ICML reviewers read 50+ papers. Abstract needs to grab attention in first 15 seconds.
- **Suggested Fix:** Lead with concrete failure: "Deep networks achieve 89% accuracy on Waterbirds but fail on 28% of minority samples—exploiting spurious background correlations instead of learning core features."

**MAJOR-ENG-02: Novelty claim requires decoding**

- **Location:** Abstract sentence 3, Introduction paragraph 4
- **Issue:** "Marchenko-Pastur-defined curvature subspace alignment" — jargon barrier for non-specialists. The key insight ("spurious features create sharp curvature that SGD avoids") is buried.
- **Why this matters:** Reviewers should understand "what's new" in 30 seconds, not 5 minutes. Current framing requires knowing MP theory.
- **Suggested Fix:** Lead with insight first: "We show that spurious correlations create measurable geometric signatures—sharp curvature in specific loss landscape directions—detectable via Marchenko-Pastur analysis."

---

## Part 3: Credibility Check (Persona 3)

### Novelty Claims Audit

| Claim | Location | Verified? | Prior Work |
|-------|----------|-----------|------------|
| "First geometric diagnostic framework using MP-defined alignment" | Abstract, Conclusion | ✓ | Sagun 2017 used MP for Hessian analysis (general), not spurious correlations |
| "Label-free detection without requiring group labels" | Abstract, Intro | ⚠️ Misleading | Requires minority group identification for gradient computation (acknowledged in ground truth line 418-421) |
| "Partial mechanistic validation" | Throughout | ✓ | Honest scope — 3/5 validated |

### Baseline Fairness Audit

| Baseline | Our Number | Literature | Fair? |
|----------|------------|------------|-------|
| Group-DRO WGA | 88.7% | Sagawa 2020: 75-80% | ✓ (actually better than literature) |
| ERM WGA | 72.3% | Sagawa 2020: 60-75% | ✓ (within expected range) |

### FATAL Issues - Credibility

**None identified.** Core claims are supported by large effect sizes and honest limitations.

### MAJOR Issues - Credibility

**MAJOR-CRED-01: "Label-free" claim is misleading**

- **Location:** Abstract (line 25), Introduction (line 41), Conclusion (line 393)
- **Issue:** Paper claims "label-free detection without group labels" but Methodology Section 3.3 explicitly requires "minority-group samples" to compute g_minority. Ground truth (line 418-421) acknowledges this is "label-free at inference time, not fully unsupervised."
- **Why this matters:** "Label-free" in ML typically means no annotation required. Here, it means "not during training" but still requires knowing which samples are minority for gradient computation.
- **Evidence:** Section 3.3 (line 105): "We compute per-sample gradients g(x) on a batch of minority-group samples."
- **Suggested Fix:** Replace "label-free" with "inference-time label-free" or "training-label-free" throughout. Explicitly state in Abstract: "requires minority group identification for diagnostic computation but not during training."

**MAJOR-CRED-02: Proof-of-concept limitations understated relative to claims**

- **Location:** Abstract, Conclusion contributions
- **Issue:** Abstract claims "this work provides the first label-free geometric diagnostic" (definitive language) but Limitations 6.3 reveals: 1 seed for H-E1, 5-epoch checkpoints for H-M4, single dataset, single architecture, random basis for H-M2.
- **Why this matters:** "Provides the first" implies production-ready contribution. The actual validation is proof-of-concept demonstrating feasibility, not comprehensive validation.
- **Evidence:** Ground truth line 275-281 shows H-M4 training was insufficient (WGA: ERM 32.3% vs expected 72%, DRO 9.8% vs expected 88%). This is acknowledged in Limitations but framed as "why acceptable" rather than "significant scope constraint."
- **Suggested Fix:** Abstract should use "establishes feasibility of" or "demonstrates proof-of-concept for" rather than "provides." Alternatively, acknowledge PoC status explicitly: "We demonstrate a geometric diagnostic framework (proof-of-concept validation on Waterbirds, d=1.87)..."

**MAJOR-CRED-03: Overclaiming tone in contributions framing**

- **Location:** Introduction lines 39-46, Conclusion lines 391-397
- **Issue:** Contribution 1 claims "reliably distinguishes ERM from robust training" based on 1-seed validation. Contribution 2 claims "partial mechanism validation" but 2/5 hypotheses incomplete (H-M2 untested, H-M4 refuted). Language is definitive despite PoC scope.
- **Why this matters:** v2.0 rule — hype disproportionate to evidence is MAJOR-CRED issue, not style. With 1 seed, single dataset, and incomplete mechanism, "reliably" is overclaim.
- **Evidence:** 
  - Ground truth line 281: "justification: Large effect size (d=1.87) makes single-seed demonstration sufficient" — this is PoC justification, not production reliability claim.
  - Verification state shows H-M2 result actually contradicts ground truth: verification_state.yaml line 401 shows "minority alignment (0.844) > majority (0.155)" marked as PASS, but ground truth line 262 shows "Both ~1e-06 (random basis limitation)" marked UNTESTED. This is a data integrity issue in verification_state.yaml.
- **Suggested Fix:** Tone down contributions to match validation scope:
  - Contribution 1: "We demonstrate that MP alignment *can* distinguish ERM from DRO with large effect size (d=1.87) on Waterbirds, establishing feasibility for a geometric diagnostic framework."
  - Contribution 2: "We validate *three components* of a five-step mechanistic chain..."

---

## Part 4: Human Review Notes

> Minor issues for human polish. NOT fixed by Revision Agent.

| Location | Note | Type |
|----------|------|------|
| Abstract, line 25 | "post-training without annotation costs" — awkward phrasing | style |
| Introduction, line 47 | "shifts the focus from 'how to fix'" — informal phrasing for academic paper | style |
| Section 2.5, line 81 | "Positioning Our Contribution" — heading is meta-commentary, unusual for Related Work | clarity |
| Section 3.2, line 95 | "avoiding full eigendecomposition, which is O(M³)" — parenthetical breaks flow | style |
| Section 5.1, Table 1 | Missing column header explanation (what does "Difference" row represent?) | clarity |
| Section 5.6.1, line 286 | "This failure has three potential explanations" — numbered list would be clearer | formatting |
| Figure references | Figures 1-3 referenced in text but actual figure numbers don't match captions (fig2_spectra is called "Figure 1" in text) | numbering |
| Section 6.3, Limitation 4 | "estimated 20-30 hours" — inconsistent with other time estimates (uses hours, others use weeks) | consistency |
| References section | "See 06_references.bib" — placeholder text, needs actual formatted references | incomplete |
| Throughout | Inconsistent hyphenation: "worst-group" vs "worst group" | style |

---

## Summary for Revision Agent

### Priority Fix List

1. **MAJOR-CRED-01:** Replace "label-free" with "inference-time label-free" throughout, clarify minority group identification required - SHOULD FIX
2. **MAJOR-CRED-02:** Tone down "provides the first" to "demonstrates proof-of-concept" in Abstract - SHOULD FIX
3. **MAJOR-CRED-03:** Soften contributions framing to match PoC validation scope - SHOULD FIX
4. **MAJOR-ENG-01:** Strengthen Abstract hook with concrete statistics upfront - SHOULD FIX
5. **MAJOR-ENG-02:** Clarify novelty earlier with insight-first framing - SHOULD FIX
6. **MAJOR-ACC-01:** Fix WGA inconsistency (88% vs 88.7%) in Introduction - SHOULD FIX

### Key Concerns

**Scope-Claim Mismatch:** The paper presents proof-of-concept validation (1 seed, single dataset, incomplete mechanism) with production-ready language ("provides the first", "reliably distinguishes", "label-free"). This creates expectation-reality gap for reviewers. Either strengthen validation (multi-seed, cross-dataset) or soften claims to match PoC scope.

**Label-Free Framing:** The "label-free" claim is technically correct (no labels during training) but misleading (requires minority identification for diagnostic). This will trigger skeptical reviewers who notice Section 3.3's requirement. Preemptively clarify scope.

**Engagement Gap:** Problem is well-motivated but novelty is buried under technical machinery. Reviewers may miss the key insight (spurious correlations → sharp curvature → geometric diagnostic) if they're lost in MP theory details.

### What's Working

**Numerical Integrity:** Perfect match between claims and ground truth. No cherry-picking, no statistical errors, appropriate rounding.

**Honest Limitations:** Section 6.3 is exemplary — acknowledges H-M2 untested, H-M4 refuted, single-seed PoC, with "why acceptable" justifications. This builds trust.

**Partial Mechanism Framing:** Unlike papers that hide failures, this work explicitly positions contribution as "3/5 validated" — intellectually honest and scientifically sound.

**Effect Size:** Cohen's d = 1.87 is genuinely impressive. The geometric signature is not a subtle effect — this is the paper's strongest asset.

**Comparison Fairness:** Baselines (ERM vs Group-DRO) are standard, well-implemented, and results match literature expectations.

---

## Quality Checklist

- [x] All three personas applied
- [x] Ground truth compared for ALL numerical claims (100% match)
- [x] Engagement check with time limits enforced (Abstract: 2:15, Intro novelty: 8:00)
- [x] Novelty claims audited (MP application novel, label-free claim misleading)
- [x] All MAJOR issues have suggested fixes
- [x] Human review notes separated (10 items)
- [x] Review is constructive (emphasizes strengths, provides specific fixes)

---

## Detailed Issue Breakdown

### Accuracy Issues (1 MAJOR, 0 FATAL)

The paper demonstrates excellent numerical integrity with one minor inconsistency. All core metrics verified against ground truth with appropriate rounding. Statistical claims (p-values, Cohen's d, effect sizes) are accurate. Limitation disclosure matches actual experimental constraints. This is model scientific practice.

### Engagement Issues (2 MAJOR, 0 FATAL)

The paper suffers from "methods-first, insight-second" presentation. Abstract and Introduction prioritize technical machinery (Marchenko-Pastur theory, Hessian eigenvalues) over the core insight (spurious correlations create geometric signatures). A busy ICML reviewer may miss the novelty because it's framed as "we apply MP theory to spurious correlations" rather than "we discover that spurious correlations have geometric signatures (measurable via MP theory)."

The Abstract hook is weak — generic problem statement rather than concrete failure statistics. Compare: "DNNs exploit spurious correlations" (generic) vs "89% average, 72% minority — spurious background shortcuts" (concrete). The latter is in Introduction but should open Abstract.

### Credibility Issues (3 MAJOR, 0 FATAL)

The core credibility concern is scope-claim mismatch. The validation is proof-of-concept (1 seed, single dataset, 5-epoch checkpoints for failed hypothesis) but language is production-ready ("provides the first", "reliably distinguishes"). Ground truth acknowledges this ("large effect size makes single-seed demonstration sufficient") but frames it as PoC justification, not reliability claim.

The "label-free" framing will trigger skeptical reviewers. Section 3.3 requires minority-group samples for gradient computation — this is not truly label-free, just "no labels during training." The distinction matters: label-free typically means no human annotation required, but this method still needs to identify minority samples somehow.

The tone in contributions is slightly inflated given limitations. "Partial mechanism validation" is honest, but "reliably distinguishes" overstates 1-seed evidence. These are not fatal (effect size d=1.87 is robust) but reduce credibility with skeptical experts.

---

## Recommendation Rationale

**MINOR_REVISION** because:

1. **No fatal flaws:** All numerical claims verified, methodology sound, limitations honestly disclosed
2. **Strong core contribution:** d=1.87 effect size, novel MP application, honest 3/5 mechanism validation
3. **Fixable weaknesses:** Engagement and credibility issues addressable via reframing (not re-experimentation)

**NOT CONDITIONAL_ACCEPT** because:

- 6 MAJOR issues across engagement and credibility domains require attention
- Scope-claim mismatch needs resolution (either strengthen validation or soften claims)
- "Label-free" framing is misleading and needs clarification

**Path to acceptance:** Revise Abstract/Introduction for engagement (concrete hook, insight-first), clarify "label-free" scope, and tone down contributions to match PoC validation. Core science is sound — presentation needs refinement.

---

**Review Completed:** 2026-04-24T20:15:00Z  
**Reviewer:** Adversary Agent v2.0 (Three-Persona Protocol)  
**Total Issues:** 6 MAJOR, 0 FATAL, 10 Human Review Notes
