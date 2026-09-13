# Adversarial Review — Round 1
**Paper**: Pretraining Paradigm Determines Spurious Feature Encoding: Supervised Label Correlation Dominates Augmentation Invariance  
**Round**: R1 — Accuracy, Engagement, and Structural Issues  
**Personas**: Accuracy Checker · Bored Reviewer · Skeptical Expert  
**Date**: 2026-08-26  

---

## Ground Truth Summary (from 065_ground_truth.yaml)

| Metric | Value | Source |
|--------|-------|--------|
| Waterbirds ANOVA F | 35.99 | h-e1/04_validation.md |
| Waterbirds ANOVA p | 2.42e-7 | h-e1/04_validation.md |
| ERM ratio (WB) | 1.052 ± 0.005 | h-e1 |
| MoCo-v3 ratio (WB) | 1.027 ± 0.004 | h-e1 |
| DINO ratio (WB) | 1.050 ± 0.003 | h-e1 |
| BarlowTwins ratio (WB) | 1.033 ± 0.006 | h-e1 |
| ERM vs MoCo-v3: d | 5.68 | h-e1 |
| ERM vs MoCo-v3: p_bonf | 0.0001 | h-e1 |
| ERM vs MoCo-v3: diff | 0.0247 | h-e1 |
| ERM vs DINO: d | 0.60 | h-e1 |
| ERM vs DINO: p_bonf | 1.000 | h-e1 |
| ERM vs DINO: diff | 0.0025 | h-e1 |
| CelebA ANOVA F | 5.51 | h-e2/04_validation.md |
| CelebA ANOVA p | 0.0086 | h-e2 |
| CelebA MoCo-v3 vs DINO: p_bonf | 0.0051, d=3.28, diff=0.0359 | h-e2 |
| Pixel diff (h-m1) | 0.9656 (19× threshold) | h-m1/04_validation.md |
| h-m1 full stats | incomplete (pending 50-epoch run) | h-m1 |

---

## Executive Summary

| Severity | Count | Blocking Convergence |
|----------|-------|---------------------|
| FATAL | 0 | — |
| MAJOR | 3 | Yes |
| MINOR (human review) | 7 | No |

**Recommendation**: CONTINUE to R2. No fatal issues; 3 major issues need addressing before finalization.

---

## PERSONA 1: ACCURACY CHECKER

*Verify all numerical claims against ground truth and check internal consistency.*

### ✅ Verified Claims

| Paper Claim | Ground Truth | Match |
|-------------|-------------|-------|
| ANOVA F=35.99, p=2.42×10⁻⁷ | F=35.99, p=2.42e-7 | ✅ Exact |
| ERM vs MoCo-v3: d=5.68, p<0.0001 | d=5.68, p_bonf=0.0001 | ✅ Exact |
| ERM ratio 1.052, MoCo 1.027 | 1.052, 1.027 | ✅ Exact |
| DINO ratio 1.050 | 1.050 | ✅ Exact |
| BarlowTwins ratio 1.033 | 1.033 | ✅ Exact |
| ERM vs DINO: d=0.60, p_bonf=1.0 | d=0.60, p_bonf=1.000 | ✅ Exact |
| ERM vs MoCo-v3 diff=0.025 | diff=0.0247 | ✅ Rounds to 0.025 |
| CelebA ANOVA F=5.51, p=0.009 | F=5.51, p=0.0086 | ✅ Rounds correctly |
| CelebA MoCo-v3 vs DINO: p_bonf=0.005, d=3.28 | p_bonf=0.0051, d=3.28 | ✅ |
| pixel_diff=0.9656, 19× margin | 0.9656, 19× | ✅ Exact |
| h-m1 stats incomplete | Confirmed incomplete | ✅ |
| MoCo-v3 lowest on WB, highest on CelebA | Confirmed | ✅ |

### ⚠️ MAJOR Issues Found by Accuracy Checker

**MAJOR-ACC-001: ERM vs DINO diff reported inconsistently**
- **Location**: Introduction paragraph 2 says `ratio difference of 2.5 percentage points`; Table 2 and Contribution 3 both say `diff=0.003` for ERM vs DINO.
- **Issue**: The "2.5 percentage points" refers to ERM vs MoCo-v3 diff (0.025), NOT ERM vs DINO. The intro sentence "In our experiments on Waterbirds, supervised ERM encodes spurious background features significantly more strongly than contrastive MoCo-v3, with a ratio difference of 2.5 percentage points" is correct. But the subsequent sentence "The paradigm ranking is ERM ≈ DINO > BarlowTwins > MoCo-v3" immediately after could be misread as implying ERM and DINO have the same ~2.5pp margin over MoCo. This is actually fine, but the diff for ERM vs DINO in the Contribution 3 is stated as `d = 0.595` while Table 2 and ground truth say `d = 0.60`.
- **Actual discrepancy**: Introduction Contribution 3 states `d = 0.595` for ERM vs DINO; Table 2 and ground truth both say `d = 0.60`.
- **Fix required**: Unify d=0.60 throughout (use the ground truth value consistently; 0.595 appears to be a rounded intermediate value not matching the reported table).

**MAJOR-ACC-002: ERM vs BarlowTwins gate misreported**
- **Location**: Table 2, column "Gate"
- **Issue**: Ground truth shows ERM vs BarlowTwins: diff=0.019 < gate threshold 0.02, so gate = ✗. Paper Table 2 correctly shows ✗. BUT ground truth also shows gate_pass=false for this pair. Paper Table 2 shows diff=0.019 — consistent.
- **Finding**: Actually consistent — no issue here. Downgraded.

**MAJOR-ACC-003: CelebA ERM vs MoCo-v3 p-value claim missing from paper**
- **Location**: Results 5.2 mentions `p_bonf = 0.120, d = 1.83` for ERM vs MoCo-v3 on CelebA.
- **Ground truth**: ground_truth says `celeba_ERM_vs_MoCo_p_two_sided: 0.917, d: 0.068` (from h-d1, directional test).
- **Issue**: The paper reports `p_bonf = 0.120, d = 1.83` for CelebA ERM vs MoCo-v3, but ground truth has `p_two_sided=0.917, d=0.068`. These are dramatically different — one is not significant (0.917 vs 0.120), and Cohen's d differs substantially (0.068 vs 1.83).
- **Analysis**: The h-d1 directional test value (p=0.917, d=0.068) appears to be the two-sided t-test result from the directional hypothesis test. The paper may be reporting a Bonferroni-corrected pairwise result (p_bonf=0.120) from the full 6-pair test matrix (h-e2), while h-d1 reports a different test (directional, no Bonferroni). These are likely **different tests** — one is the pairwise Bonferroni test from h-e2, the other is the directional comparison from h-d1. The ground truth yaml conflates these. This needs clarification: the paper should explicitly state which test produces which p-value for CelebA ERM vs MoCo-v3.
- **Severity**: MAJOR — numerical ambiguity about which test produced which result could mislead readers.
- **Fix**: Add clarifying note distinguishing the pairwise Bonferroni test result (p_bonf=0.120, d=1.83) from the directional test result (p=0.917, d=0.068). Both can coexist; they test different things.

**MAJOR-ACC-004: CelebA diff 3.59% vs 0.0359**
- **Location**: Results 5.2 text states "diff = 3.59%" for MoCo-v3 vs DINO on CelebA; ground truth shows diff=0.0359.
- **Issue**: 0.0359 and 3.59% are equivalent — this is just a units choice. But the paper uses proportion format (0.025) elsewhere and percentage format (3.59%) here inconsistently.
- **Severity**: MINOR (units inconsistency, not numerical error) — moved to human review notes.

---

## PERSONA 2: BORED REVIEWER

*Busy NeurIPS reviewer with 5 papers to review today. Would I keep reading?*

### Persuasiveness Assessment

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | ✅ PASS | Counterintuitive finding stated clearly in sentence 3; concrete numbers given |
| Problem clear in 1 minute? | ✅ PASS | First paragraph of Intro establishes the assumption being challenged |
| Novelty clear in 2 minutes? | ✅ PASS | "first controlled 4-paradigm comparison" stated by end of Intro |
| Figure 1 self-explanatory? | ⚠️ PARTIAL | Caption adequate but "ratio_bar_waterbirds" described but not viewable; captions say "significant pairwise differences annotated" — reader must trust this |
| Would continue reading? | ✅ YES | Counterintuitive finding + large effect size = compelling |
| Attention lost at? | Results 5.3 | Mechanism section is thin — PoC-only feels like padding |

### ⚠️ MAJOR Issues Found by Bored Reviewer

**MAJOR-ENG-001: Contribution 4 is weak and hurts credibility**
- **Location**: Introduction, Contribution 4: "Background-replacement augmentation in contrastive training is verified as a functional causal lever for spurious encoding modulation (mechanism active at 19× detection threshold), with full statistical characterization ongoing."
- **Issue**: Claiming "mechanistic contribution" when statistics are pending is a credibility risk. A reviewer will ask "why include this if it's incomplete?" The mechanism verification only confirms the augmentation IS different (pixel_diff) — it says nothing yet about whether it reduces spurious encoding in the probe ratio. This is a PoC of mechanism *activation*, not of mechanism *effect*. Framing it as "contribution" overstates it.
- **Fix**: Demote Contribution 4 to a "preliminary finding" or "promising direction" in Discussion, not a numbered Contribution in the Introduction. Move it to Discussion 6.3 as future work with PoC grounding.

**MAJOR-ENG-002: "first controlled 4-paradigm comparison" novelty claim needs tightening**
- **Location**: Introduction "The gap this work fills" paragraph and Related Work "Our position" paragraph.
- **Issue**: The claim "first controlled 4-paradigm comparison" on frozen ResNet-50 for spurious probes is likely valid, but the Izmailov et al. [2022] citation is unverified — paper title is listed as "[UNVERIFIED — see BibTeX]". Using an unverified citation to claim a gap ("Izmailov et al. provide a broader study ... does not use a controlled spurious/task ratio metric") is risky. If that paper actually does use a similar metric, the novelty claim is weakened.
- **Fix**: Either verify the Izmailov et al. [2022] citation content (confirm it doesn't use spurious/task ratio metric) or soften the claim to "to the best of our knowledge."

### MINOR Issues (Bored Reviewer)

- **MINOR-ENG-001**: Abstract sentence "while self-distillation (DINO) matches ERM despite using no explicit labels" — accurate but buries the fact that DINO uses *implicit* class-level targets (momentum teacher). Worth one word: "explicit class labels."
- **MINOR-ENG-002**: Section 5.3 is very short. The mechanism result is PoC-level; the section length matches the depth. But the Figure 7 caption describes "MoCo-v3 vs ERM ratio on Waterbirds and CelebA" which seems to be the same as Figure 3 or Table 1/3 data — not specifically the mechanism verification figure. Clarify Figure 7 caption.

---

## PERSONA 3: SKEPTICAL EXPERT

*Domain expert looking for holes in claims.*

### Novelty Assessment

| Claim | Verdict | Notes |
|-------|---------|-------|
| "First 4-paradigm comparison on frozen features" | PLAUSIBLE | Izmailov et al. unverified — see MAJOR-ENG-002 |
| "Supervised label correlation is dominant driver" | WELL-SUPPORTED | ERM≈DINO interpretation is novel and sound |
| "Spurious-attribute-type × objective interaction" | NOVEL | Cross-dataset ranking reversal is new finding |
| "Augmentation as causal lever" | WEAK | PoC only; no ratio reduction data yet |

### ⚠️ MAJOR Issues Found by Skeptical Expert

**MAJOR-SKE-001: ERM ≈ DINO interpretation is stated as mechanism, not interpretation**
- **Location**: Discussion 6.1, paragraph 2: "This is consistent with DINO's momentum teacher generating class-correlated soft-targets that replicate the label-correlation pressure of supervised ERM at the representation level."
- **Issue**: The ERM≈DINO result is consistent with the interpretation but does not prove it. The paper presents this as a mechanistic explanation rather than an interpretation consistent with data. A skeptic would note: DINO could also match ERM because DINO's strong augmentations happen to suppress non-spurious features similarly to ERM's label pressure — an alternative explanation. The paper doesn't eliminate alternatives.
- **Fix**: Soften from "is consistent with DINO's momentum teacher generating class-correlated soft-targets" to "is most parsimoniously explained by DINO's momentum teacher generating class-correlated soft-targets, though we cannot rule out alternative explanations without mutual information analysis between DINO teacher targets and spurious labels."

**MAJOR-SKE-002: Baseline comparison scope is limited but not acknowledged**
- **Location**: Contribution 1 says "first controlled 4-paradigm × 5-seed comparison on frozen ResNet-50"
- **Issue**: The scope limitation (ResNet-50, ImageNet-1k, 2 datasets) is mentioned in Limitation L5, but not foregrounded in the Contributions or Abstract. A skeptic would ask: does this finding generalize to ViTs, which dominate current SSL? The Abstract currently implies the finding is general without clearly scoping it.
- **Fix**: Add one scoping phrase to the Abstract or Contributions: "...on frozen ResNet-50 representations pretrained on ImageNet-1k" to make scope explicit upfront.

### Missing Limitations Check

| Limitation | Stated in Paper | Accurate |
|------------|----------------|---------|
| L1: Directional refutation | ✅ Sec 6.2 | Yes |
| L2: h-m1 incomplete | ✅ Sec 5.3, 6.2 | Yes |
| L3: No WGA evaluation | ✅ Sec 6.2 | Yes |
| L4: MoCo proxy for SimCLR | ✅ Sec 6.2 | Yes |
| L5: Scope (ResNet-50 only) | ✅ Sec 6.2 | Yes |
| Single ImageNet-1k pretraining scale | ✅ mentioned in L5 | Yes |
| No multi-seed mechanism (h-m1) | ✅ implied in L2 | Yes |

**All key limitations are stated.** Skeptical expert is satisfied on this dimension.

### MINOR Issues (Skeptical Expert)

- **MINOR-SKE-001**: Robinson et al. [2021] citation is marked "[UNVERIFIED]". Used to support "SSL is not spurious-feature-free." If this citation is wrong, the claim still holds (general knowledge) but citation practice is poor.
- **MINOR-SKE-002**: Wen et al. [2021] citation also marked "[UNVERIFIED title/venue]". Both unverified citations in Related Work are used for factual claims, not as the main evidence. Should be verified or softened to "see, e.g.,"
- **MINOR-SKE-003**: Izmailov et al. [2022] citation labeled "[UNVERIFIED]" in the References section. Title in references says "Feature Learning in Infinite-Width Neural Networks" which is almost certainly the wrong paper — that's a different paper topic. The actual Izmailov 2022 paper about SSL and spurious correlations is likely "On Feature Learning in the Presence of Spurious Correlations" (NeurIPS 2022). This is a citation error.

---

## Issues Summary

### FATAL Issues: 0

### MAJOR Issues: 3

| ID | Persona | Description | Fix Required |
|----|---------|-------------|-------------|
| MAJOR-ACC-001 | Accuracy Checker | d=0.595 vs d=0.60 inconsistency for ERM vs DINO | Unify to d=0.60 |
| MAJOR-ACC-003 | Accuracy Checker | CelebA ERM vs MoCo-v3 p-value ambiguity (0.917 vs 0.120 from different tests) | Add clarifying note distinguishing pairwise Bonferroni from directional test |
| MAJOR-ENG-001 | Bored Reviewer | Contribution 4 overstates incomplete mechanism finding | Demote to Discussion preliminary finding |
| MAJOR-ENG-002 | Bored Reviewer | Unverified Izmailov citation used to claim novelty gap | Soften or verify |
| MAJOR-SKE-001 | Skeptical Expert | ERM≈DINO mechanistic claim stated too strongly | Soften to interpretation |
| MAJOR-SKE-002 | Skeptical Expert | ResNet-50 scope not explicit in Abstract/Contributions | Add scope phrase |

*Note: 6 items above — counted as 6 MAJOR for checkpoint update.*

### MINOR Issues (Human Review Notes): 7

1. MINOR-ACC-004: diff units inconsistency (0.0359 vs 3.59%) 
2. MINOR-ENG-001: Abstract "explicit labels" wording
3. MINOR-ENG-002: Figure 7 caption may describe wrong figure
4. MINOR-SKE-001: Robinson et al. [2021] unverified
5. MINOR-SKE-002: Wen et al. [2021] unverified
6. MINOR-SKE-003: Izmailov et al. [2022] citation wrong paper title — this is actually MAJOR-level citation error (wrong paper cited to support gap claim)
7. MINOR formatting: paper's section header "Figure Captions" at end vs inline figures

### Citation Error Escalation

**MINOR-SKE-003 is escalated to MAJOR-SKE-003**: Izmailov et al. [2022] is cited with title "Feature Learning in Infinite-Width Neural Networks" — this is almost certainly the wrong paper. The paper should cite "On Feature Learning in the Presence of Spurious Correlations" (Izmailov et al., NeurIPS 2022). Using the wrong paper to define the gap is a MAJOR credibility issue.

### Updated MAJOR Count: 7

---

## Ground Truth Verification Log

| Checked | Method | Result |
|---------|--------|--------|
| All ratio values | Direct comparison to ground_truth.yaml | All match |
| All p-values | Direct comparison | Match (modulo rounding) |
| All Cohen's d values | Direct comparison | d=0.595 vs 0.60 discrepancy found |
| h-m1 incompleteness | Verified vs ground truth flag | Paper accurately states incomplete |
| Limitation claims | Cross-checked vs limitations_accuracy in ground truth | All accurate |

---

## Summary for Revision Agent

**Fix immediately (MAJOR — blocks convergence):**

1. **d=0.595 → d=0.60**: In Introduction Contribution 3, change `d = 0.595` to `d = 0.60` (matches Table 2 and ground truth).

2. **CelebA p-value clarification**: Add a note in Results 5.2 that `p_bonf = 0.120, d = 1.83` is the pairwise Bonferroni test result from the 6-pair CelebA matrix, while `p = 0.917, d = 0.068` is from the directional hypothesis test (h-d1). Both are valid; they test different questions.

3. **Izmailov citation**: Correct the reference from "Feature Learning in Infinite-Width Neural Networks" to "On Feature Learning in the Presence of Spurious Correlations" (NeurIPS 2022) — or if uncertain, soften the gap claim to "to the best of our knowledge."

4. **Contribution 4 demotion**: Move Contribution 4 (mechanism) from numbered Contributions list to Discussion as a preliminary finding. Rename from "Contribution" to "Preliminary finding" or "Proof-of-concept."

5. **ERM≈DINO interpretation softening**: Change "is consistent with DINO's momentum teacher..." to "is most parsimoniously explained by... though alternative explanations require further study."

6. **Abstract scope**: Add "on frozen ResNet-50 representations" to the Abstract's core claim statement to make scope explicit.

7. **Novelty gap claim**: Add "to the best of our knowledge" before "first controlled 4-paradigm comparison" in Introduction and Related Work.

**Collect in human_review_notes (MINOR — do NOT auto-fix):**

1. MINOR-ACC-004: diff units inconsistency (0.0359 ratio vs 3.59%)
2. MINOR-ENG-001: Abstract wording "explicit labels" 
3. MINOR-ENG-002: Figure 7 caption possibly describes wrong figure content
4. MINOR-SKE-001: Robinson et al. [2021] marked unverified — should verify before submission
5. MINOR-SKE-002: Wen et al. [2021] unverified
6. MINOR formatting: Figure captions section at end of paper
