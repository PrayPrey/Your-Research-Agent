# Adversarial Review — Round 1
**Paper**: "Language-Family Retention Bias from Global CCNet Perplexity Thresholding: A Calibrated Measurement on RedPajama-V2"
**Round**: R1 — Accuracy and Engagement
**Personas**: Accuracy Checker · Bored Reviewer · Skeptical Expert
**Generated**: 2026-07-30 (UNATTENDED mode)

---

## Ground Truth Summary (Pre-loaded)

| Claim | Ground Truth Value | Source |
|-------|-------------------|--------|
| Cramér's V range | 0.40–0.57 (k10=0.4021, k20=0.5193, k30=0.5629, k40=0.5696, k50=0.5293) | 04_validation.md |
| n documents | 208,262 | 04_validation.md |
| es retention at k=30 | 86.4% | 04_validation.md |
| en retention at k=30 | 16.3% | 04_validation.md |
| de retention at k=30 | 13.7% | 04_validation.md |
| Max-min gap at k=30 | 72.7pp (es 86.4% − de 13.7%) | 04_validation.md |
| Spanish saturation at k=40 | 100.0% | 04_validation.md |
| All Holm p | ≈ 0 (machine epsilon) | 04_validation.md |
| Prior estimate range | V ∈ [0.29, 0.41] | 065_ground_truth.yaml |
| Underestimation ratio | 25–40% | 065_ground_truth.yaml |
| Runtime | ~35 seconds CPU-only | 04_validation.md |
| Languages | de, en, es, fr, it | 04_validation.md |

All 8 ground-truth claims (C1–C8) pre-verified as `match: true` in 065_ground_truth.yaml.

---

## Executive Summary

| Severity | Count | Notes |
|----------|-------|-------|
| FATAL | 0 | No fundamental contradictions found |
| MAJOR | 2 | Overclaim + misleading statistic |
| MINOR (human review) | 6 | Style/clarity only |

**Persuasiveness**: PASSED (abstract is compelling, hook is effective, novelty is clear)
**Recommendation**: Proceed to R2 after R1 revision

---

## PERSONA 1: Accuracy Checker

### Ground Truth Verification Log

| Claim ID | Paper Location | Paper Value | Ground Truth | Match |
|----------|---------------|-------------|--------------|-------|
| C1 | Abstract, Intro | es=86%, en=16% at k=30 | es=0.864, en=0.163 | ✅ |
| C2 | Abstract, Table 1 | V=0.40–0.57 | [0.4021, 0.5193, 0.5629, 0.5696, 0.5293] | ✅ |
| C3 | Abstract, Results | Holm p ≈ 0 | machine epsilon | ✅ |
| C4 | Abstract, Results | 72.7pp gap at k=30 | 72.7pp (0.864−0.137) | ✅ |
| C5 | Intro, Discussion | Prior V ∈ [0.29,0.41]; actual 25–40% larger | [0.29,0.41] → [0.40,0.57] | ✅ |
| C6 | Results | es>fr>it>en>de all k | Confirmed all 5 k | ✅ |
| C7 | Results 5.4 | es=100% at k=40 | es_k40=1.000 | ✅ |
| C8 | Abstract, Setup | n=208,262 | 208,262 | ✅ |

**Table 1 numbers** (paper vs ground truth):
| k | Paper V | GT V | Match |
|---|---------|------|-------|
| 10 | 0.4021 | 0.4021 | ✅ |
| 20 | 0.5193 | 0.5193 | ✅ |
| 30 | 0.5629 | 0.5629 | ✅ |
| 40 | 0.5696 | 0.5696 | ✅ |
| 50 | 0.5293 | 0.5293 | ✅ |

**Chi² values** match ground truth exactly. All PPL thresholds (175.0, 224.0, 261.7, 295.1, 328.9) match.

**Per-language retention Table 2** vs ground truth: all 25 cells match (5 languages × 5 k values).

**Accuracy Checker verdict: PASS — no numerical discrepancies found.**

---

### ACCURACY ISSUES FOUND

**ACC-MAJOR-001 [MAJOR]: Misleading "first to" claim in Introduction**

Location: Introduction paragraph 3: "no prior work provides a calibrated baseline measurement of how large this disparity is, using a standard associativity metric across multiple threshold levels on a real multilingual dataset."

Issue: The paper claims novelty on the intersection of: (a) global k-th percentile, (b) ccnet_perplexity specifically, (c) RedPajama-V2 specifically, (d) Cramér's V, (e) multiple k values. While this specific combination may indeed be novel, the claim as written could be read as claiming priority on quantitative V measurement of any quality-signal retention bias — which is broader than what the paper actually demonstrates.

Assessment: This is **not FATAL** because the claim is carefully scoped to the specific dataset+signal+threshold combination. However, it needs slight tightening to make the scope unmistakably clear.

Suggested fix: Add qualifier "...for this specific combination of dataset (RedPajama-V2), quality signal (ccnet_perplexity), and threshold type (global k-th percentile)."

**ACC-MINOR-001 [MINOR → human review]: Section 5.5 pipeline introspection**

Location: Results 5.5: "This recalibration required three gate iterations during the research pipeline (h-e1 predicted V ∈ [0.29, 0.41], observed V partially outside range; h-e1-v3 used the same gate and obtained the same result; h-e1-v3-v4 updated the gate to the empirically observed range V ∈ [0.40, 0.57] and achieved all five indicators passing)."

Issue: This exposes internal pipeline hypothesis IDs (h-e1, h-e1-v3, h-e1-v3-v4) in a submitted paper, which reads as technical debt of the research system rather than scientific content. An academic reader does not need to know the experiment versioning history to understand the finding. The key content — that three runs were needed to calibrate the gate — can be expressed without pipeline-internal identifiers.

Severity: MINOR (style/narrative clarity) → human review

---

## PERSONA 2: Bored Reviewer

*"I have 5 papers to review today. Would I continue reading this one?"*

### First Impression Assessment

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | ✅ PASS | "86% Spanish vs 16% English" is concrete and surprising. Would continue. |
| Problem clear in 1 minute? | ✅ PASS | Paragraph 1 of Introduction states the problem cleanly with numbers. |
| Novelty clear in 2 minutes? | ✅ PASS | Four contributions listed clearly in Introduction. |
| Figure 1 self-explanatory? | ✅ PASS | Caption describes V with gate bounds and n; title should be in the figure itself. |
| Hook avoids "X is important"? | ✅ PASS | Opens with concrete finding, not "multilingual NLP is important." |

### Engagement Assessment

| Check | Result |
|-------|--------|
| Would continue reading? | YES |
| Attention lost at? | Section 5.5 (pipeline introspection breaks narrative) |
| False novelty claims? | 0 |
| Unfair baseline comparisons? | 0 (no baselines — measurement paper) |
| Overclaims found? | 1 (see BR-MAJOR-001 below) |
| Missing limitations? | NO — all 4 limitations present and honest |

### BORED REVIEWER ISSUES FOUND

**BR-MAJOR-001 [MAJOR]: Overclaiming "first to" in Abstract**

Location: Abstract: "the consequences of applying a single global threshold to per-language perplexity scores have never been precisely quantified."

Issue: "Never been precisely quantified" is a strong absolute claim. While the authors may be correct that *Cramér's V applied to ccnet_perplexity on RedPajama-V2 at these k values* has not been done, the statement as written claims that no prior work has precisely quantified retention consequences of global thresholding in any perplexity filtering context. This overclaim is attackable by a reviewer who can cite any retention disparity measurement in any quality-filtered multilingual corpus.

Note: The more precise version appears in the Related Work section (Section 2.5): "Our work is the first to quantify the language-group retention disparity (Cramér's V) from global ccnet_perplexity thresholding on RedPajama-V2." The Abstract should match this specificity.

Severity: MAJOR — an overstatement in the Abstract that contradicts the more precise claim in Related Work Section 2.5.

Suggested fix: Replace Abstract sentence with: "...but the magnitude of this effect for ccnet_perplexity on RedPajama-V2 has not been precisely quantified using a standard association metric." OR align to the precise language of Section 2.5.

**BR-MINOR-001 [MINOR → human review]: Section 6.2 header mismatch**

The paper's Discussion section has: 6.1 Key Findings, 6.2 Connection to Prior Work, 6.3 Limitations, 6.4 Broader Impact. But the filed `06_discussion.md` has this labeled as "6.2 Connection to Prior Work" while the full paper `06_paper.md` labels the same content identically. No actual discrepancy — just noting the organization is slightly unusual (prior work discussion in Discussion section rather than Discussion → Interpretation → Prior → Limits → Impact). No action needed if journal style OK.

**BR-MINOR-002 [MINOR → human review]: Section 5.5 narrative interruption**

The pipeline versioning IDs (h-e1, h-e1-v3, h-e1-v3-v4) break the paper's narrative flow. Bored reviewer would be puzzled by these internal identifiers. Recommend replacing with: "The measurement required three experimental iterations to calibrate: initial estimates predicted V ∈ [0.29, 0.41], but empirical results consistently fell above the predicted ceiling, ultimately yielding V = 0.40–0.57 across all five threshold levels."

---

## PERSONA 3: Skeptical Expert

*"Is this actually novel? Are the claims fair? What's missing?"*

### Novelty Assessment

**Novel aspects:**
1. Cramér's V measurement specifically on ccnet_perplexity field in RedPajama-V2 — not done before (plausible, since RedPajama-V2 is recent, 2024)
2. Multiple k-values tested with Holm correction — careful statistical approach
3. Prior estimate recalibration finding — genuinely useful to community
4. 25-40% underestimation finding is empirically grounded

**Potentially weak novelty claim:**
- The general phenomenon of global quality thresholds producing per-language bias is documented qualitatively (Caswell 2021, Adelani 2023). The paper's contribution is specifically the *quantification* with V and the specific dataset+signal+k combination. This is clearly stated and well-justified. No false novelty claims.

### Baseline Fairness

No method baselines present (measurement-only paper). No unfair comparisons found. The comparison to "literature-derived estimates [0.29, 0.41]" is honest — labeled as Phase 2B prior estimates, not claimed as a competitor's published number.

### Missing Limitations Assessment

| Limitation | Present in Paper? | Location |
|------------|------------------|----------|
| Existence-only scope (no correction tested) | ✅ YES | 6.3 L1 |
| Sample scope (208k vs 113B) | ✅ YES | 6.3 L2 |
| Document-length confound | ✅ YES | 6.3 L3 |
| Five European languages only | ✅ YES | 6.3 L4 |

All limitations honestly present. Discussion is appropriately candid.

**Additional missing limitation (MAJOR):**

**SE-MAJOR-001 [MAJOR]: Contingency table dimensions not stated accurately**

Location: Methodology Section 3.4: "we construct a 2×5 contingency table (language × retained/removed)"

Issue: The description says "2×5 contingency table" but then shows a table with rows=languages (5), columns=retained/removed (2). The contingency table is therefore 5×2 (languages × decision), not 2×5 (decision × languages). This is a minor transposition but the formula uses min(r, c) where r=5 languages and c=2 outcomes. The description writes "r = 5 languages, c = 2 (retained/removed)" which is correct but conflicts with calling it a "2×5" table in the same sentence.

Severity: MAJOR — a methodological description error. A reviewer will immediately flag: "you said 2×5 table but then min(r,c) with r=5 languages and c=2. Which is it?" The correct description is "5×2 contingency table (5 languages × 2 outcomes: retained/removed)."

Suggested fix: Change "2×5 contingency table" → "5×2 contingency table" throughout (appears once in Section 3.4 and once in Results 5.1 reference). 

Note: The formula and computation are correct — only the table dimension description is inverted.

**SE-MINOR-001 [MINOR → human review]: Methodology Section 3.6 reproducibility claim**

"confirming identical V values across runs (V = 0.4021–0.5696 for k=10–k=40, V = 0.5293 for k=50)"

The parenthetical is slightly confusing — it lists V=0.4021–0.5696 as the range for k=10 to k=40, and V=0.5293 for k=50 separately. But V=0.5293 is *not outside* the range 0.4021–0.5696 (it is within the range 0.40–0.57). The sentence should read: "confirming identical V values across runs (V ranges from 0.4021 at k=10 to 0.5696 at k=40, then 0.5293 at k=50)." Minor clarity issue.

**SE-MINOR-002 [MINOR → human review]: Jansen et al. 2022 citation accuracy**

Location: Section 2.3: "Jansen et al. [2022] find that standard perplexity filtering breaks down on multilingual heterogeneous data."

The Jansen et al. 2022 paper ("Perplexed by Quality") is primarily about adult/harmful content detection using perplexity, not about multilingual retention bias. The cited finding "breaks down on multilingual heterogeneous data" may be an overgeneralization of their actual conclusions. This citation should be verified against the actual paper to ensure the summary accurately represents their claims.

**SE-MINOR-003 [MINOR → human review]: Related Work reference to Singh et al. 2026**

Section 2.3 cites "Singh et al. [2026]" but the full paper reference list at the bottom does not include this citation. Check if this was accidentally omitted from the References section.

---

## Consolidated Issue List

### FATAL Issues: 0

### MAJOR Issues: 2

| ID | Persona | Location | Issue | Fix Required |
|----|---------|----------|-------|--------------|
| BR-MAJOR-001 | Bored Reviewer | Abstract | "never been precisely quantified" overclaims beyond dataset+signal+threshold scope; contradicts more precise claim in Sec 2.5 | Narrow abstract claim to match Sec 2.5 specificity |
| SE-MAJOR-001 | Skeptical Expert | Sec 3.4, 5.1 | "2×5 contingency table" should be "5×2 contingency table" (rows=languages, columns=retained/removed) | Fix dimension description (computation is correct) |

### MINOR Issues (Human Review): 6

| ID | Persona | Location | Issue |
|----|---------|----------|-------|
| ACC-MINOR-001 | Accuracy Checker | Results 5.5 | Pipeline IDs (h-e1, h-e1-v3, h-e1-v3-v4) should be removed from submitted paper |
| BR-MINOR-001 | Bored Reviewer | Discussion 6.2 | Section header ordering (minor style) |
| BR-MINOR-002 | Bored Reviewer | Results 5.5 | Pipeline versioning narrative interrupts reader flow |
| SE-MINOR-001 | Skeptical Expert | Methodology 3.6 | Reproducibility parenthetical V range confusing |
| SE-MINOR-002 | Skeptical Expert | Related Work 2.3 | Jansen et al. 2022 citation accuracy needs verification |
| SE-MINOR-003 | Skeptical Expert | Related Work 2.3 | Singh et al. 2026 missing from References |

---

## Persuasiveness Summary

| Check | Result |
|-------|--------|
| Abstract compelling | ✅ PASS |
| Problem clear in 1 minute | ✅ PASS |
| Novelty clear in 2 minutes | ✅ PASS |
| Figure 1 self-explanatory | ✅ PASS |
| Would continue reading | ✅ YES |
| Attention lost at | Section 5.5 (pipeline introspection) |
| Overall persuasiveness | **PASSED** |

---

## Summary for Revision Agent

**Fix immediately (MAJOR):**

1. **BR-MAJOR-001**: Abstract sentence "the consequences of applying a single global threshold to per-language perplexity scores have never been precisely quantified" — narrow to match the precise scope in Sec 2.5: "...the magnitude of this effect for ccnet_perplexity on RedPajama-V2 has not been precisely quantified using a standard association metric."

2. **SE-MAJOR-001**: Change "2×5 contingency table" → "5×2 contingency table" in Sec 3.4. Also verify any mention in Results 5.1 that references the table dimensions.

**Collect for human review (MINOR):**
- Sec 5.5 pipeline IDs removal (ACC-MINOR-001 + BR-MINOR-002)
- Singh et al. 2026 missing from References (SE-MINOR-003)
- Jansen et al. 2022 citation accuracy verification (SE-MINOR-002)
- Reproducibility parenthetical clarity fix (SE-MINOR-001)

**Do NOT change:**
- All numerical values (verified correct)
- All limitations (all present and honest)
- Narrative structure (effective)
- Hook and callback (both present and work)
