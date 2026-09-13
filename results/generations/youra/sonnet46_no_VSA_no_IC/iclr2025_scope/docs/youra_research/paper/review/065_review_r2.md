# Adversarial Review Round 2

**Reviewer:** Adversary Agent — Numerical Verification Focus
**Paper:** Entropy-Guided Selective Sliding Window Attention Conversion in Llama-2-7B (R1 revision)
**Round:** R2 — deep numerical and credibility audit following R1 fixes

---

## Ground Truth Verification Table

| Claim | Paper Value | Ground Truth | Match | Notes |
|-------|------------|--------------|-------|-------|
| Gini coefficient (mean) | 0.6829 | 0.6829 | MATCH | Abstract, Intro, Table 1, Results, Conclusion all consistent |
| Gini std | 0.0117 | 0.0117 | MATCH | Table 1 and Introduction |
| Gini n | 200 | n=200 | MATCH | Stated in Table 1 header and contribution (1) |
| Gini satisfaction rate | 100% (200/200) | 100% (200/200) | MATCH | Table 1 and Contribution (1) |
| Top-10% token share (mean) | 0.7172 | 0.7172 | MATCH | Table 1: "0.7172" — correctly NOT written as "71.72%" in table |
| Top-10% token share as % in prose | "71.72%" | 0.7172 × 100 = 71.72% | MATCH | Abstract, Intro, and Conclusion all state 71.72% consistently |
| Top-10% std | 0.0196 | 0.0196 | MATCH | Table 1 |
| Head-mean Gini | 0.681 | 0.681 | MATCH | Table 3, prose throughout |
| Head-max Gini | 0.466 | 0.466 | MATCH | Table 3 |
| 32% relative reduction formula | (0.681−0.466)/0.681 = 31.6% ≈ 32% | 31.6% ≈ 32% | MATCH | Table 3 footnote added in R1 is correct |
| 46.1% framing | (0.681−0.466)/0.466 = 46.1% | 46.1% | MATCH | Both framings now present in Table 3 footnote |
| Table 3 "Relative difference" row label | "−32% (head-max vs head-mean)" | head-mean denominator = 32% ✓ | MATCH | Prose and table now consistent |
| k=4 layers / 32 layers = 12.5% | 12.5% | 4/32 = 12.5% ✓ | MATCH | Section 3.3: "Conservatively converting 12.5% of layers (4 of 32)" |
| Calibration: 100 sequences | 100 | 100 | MATCH | Multiple sections |
| Calibration: 2048 tokens | 2048 | 2048 | MATCH | Section 3.2.2, 4.2 |
| Calibration source | WikiText-103 validation split | WikiText-103 validation split | MATCH | |
| Subset A indices | 0–99 | 0–99 | MATCH | Section 3.2.2, 4.2 |
| Subset B indices | 100–199 | 100–199 | MATCH | Section 4.2 |
| Subset C indices | 200–299 | 200–299 | MATCH | Section 4.2 |
| QA F1: entropy | −0.43 pp | −0.43 pp | MATCH | Section 5.4 |
| QA F1: random | −0.67 pp | −0.67 pp | MATCH | Section 5.4 |
| QA F1 p-value | 0.4507 | 0.4507 | MATCH | Section 5.4 |
| QA F1 N | 200 | 200 | MATCH | Section 5.4 |
| Spearman ρ gate result | ≥ 0.8 (all pairs) | ≥ 0.8 gate PASS | MATCH | But exact values still not reported — see MAJOR-001 below |
| h-e2/h-m1/h-m2 status | "Pending execution" / "NOT EXECUTED" | NOT EXECUTED | MATCH | Correctly framed throughout |
| SWA window | 512 | 512 | MATCH | |
| GPU-minutes per subset | "≈ 20–30 GPU-minutes" | Not independently verified | FLAG | See mathematical validity below |

---

## Mathematical Validity Analysis

### 1. GPU-time consistency: "≈ 20–30 GPU-minutes per subset" vs "< 1 GPU-hour for all three"

**Check:** 3 subsets × 30 GPU-min (upper bound) = 90 GPU-minutes = 1.5 GPU-hours > 1 GPU-hour.

If the upper bound is 30 min/subset, the claim "< 1 GPU-hour" for all three is incorrect.

However, if the typical runtime is ~20 min (lower bound), then 3 × 20 = 60 min = exactly 1 GPU-hour. The paper says "approximately 20–30 GPU-minutes per subset" (Section 3.2.2 and Section 4.5). The "< 1 GPU-hour" claim appears in the Introduction ("< 1 GPU-hour") and in Section 3.6 ("completing calibration (h-e1) in < 1 GPU-hour").

**Verdict:** The "<1 GPU-hour" claim holds only if typical runtime is closer to ~20 min/subset. At the stated upper bound of 30 min, it is borderline or slightly over. This is a credibility-damaging inconsistency when a reviewer computes 3 × 30 = 90 min. The R1 review flagged this as MINOR (M1) but it was NOT fixed in the R1 revision. This remains a live issue.

### 2. 32% footnote added in R1 (Table 3)

(0.681 − 0.466) / 0.681 = 0.215 / 0.681 = 0.3157 ≈ 31.6% ≈ 32% ✓

The footnote is mathematically correct and resolves the FATAL-001 from R1.

### 3. 46.1% companion framing in Table 3 footnote

(0.681 − 0.466) / 0.466 = 0.215 / 0.466 = 0.4614 ≈ 46.1% ✓

Both framings in the Table 3 footnote are arithmetically correct.

### 4. k=4 / 32 = 12.5%

4 / 32 = 0.125 = 12.5% ✓

### 5. Gini formula stated in Section 4.4

The paper gives: Gini = (∑_{i,j} |w_i − w_j|) / (2 × n × ∑_i w_i)

This is the standard Gini coefficient formula. For normalized probability distributions where ∑w_i = 1, the denominator simplifies to 2 × n, which is the standard form. The formula is correct. However, the paper notes "w_i are the per-token attention weights (summed across heads and head positions to produce a per-token scalar)" — this aggregation is reasonable but nonstandard. The formula is applied to a derived per-token scalar, not directly to the attention matrix. This is not an error but is an implementation choice that should be precisely stated (MINOR).

### 6. Top-10% token share: "71.72%" as a percentage of 0.7172

0.7172 × 100 = 71.72% ✓ — All five occurrences of this percentage in the paper are consistent.

### 7. "Pmlr 2026" citation (Section 2.4)

Still present: "calibration quality analysis approaches [Pmlr 2026]" — This is a non-functional bibliographic key with no author, title, or paper ID. It was flagged as M3 in R1 and has NOT been fixed. The citation is used to support "Spearman rank correlation for stability validation follows calibration quality analysis approaches [Pmlr 2026]." While used in a supporting (non-central) position, it is a placeholder citation that would not survive peer review. It must be replaced with a real reference or removed.

### 8. StreamingLLM citation (Xiao 2024)

Xiao et al. arXiv:2309.17453 — Ground truth flags as UNVERIFIED. The citation appears in Section 2.3 as supporting evidence for local attention patterns ("StreamingLLM [Xiao et al., 2024] exploits sink token attention patterns"). This arXiv paper is real (it is a well-known paper from Guangxuan Xiao, Song Han et al. on attention sinks for streaming inference). The paper ID 2309.17453 is from domain knowledge and is very likely correct. The year 2024 (vs the 2023 arXiv submission date) is slightly off — the arXiv paper is from September 2023, though it was published at ICLR 2024. This is a low-severity discrepancy but should be verified before submission.

---

## FATAL Issues

**None confirmed in R2.** FATAL-001 from R1 (32% vs 46.1% inconsistency) has been resolved in the R1 revision by adding a proper footnote to Table 3 that explains both framings with denominator context. The prose now consistently uses the 32% head-mean-denominator framing, and Table 3 retains the "−32%" label while the footnote explains the 46.1% alternative.

---

## MAJOR Issues

### R2-MAJOR-001: Exact Spearman ρ values still absent (INHERITED from R1-MAJOR-001, NOT FIXED)

**Status: UNRESOLVED from R1.**

Table 2 continues to report only "≥ 0.8" for all three pairs (A vs B, A vs C, B vs C). The R1 review explicitly required: "Report exact ρ values for each pair. If unavailable, re-run the entropy scoring — it is < 1 GPU-hour." No exact values appear in the R1 revision. The footnote to Table 2 still reads: "Gate criterion satisfied (min ρ ≥ 0.8 confirmed). Individual ρ values from implementation confirm this bound; point estimates were not separately tabulated in h-e1 results reporting — only the gate outcome was recorded."

This is the foundational stability claim of the paper. Reporting only the gate threshold ("≥ 0.8") reads as an attempt to pass without showing the score. If the values are ρ = 0.80, 0.81, 0.82, the stability claim is much weaker than if ρ = 0.94, 0.96, 0.93. A reviewer cannot distinguish these cases. This remains a critical gap.

**Impact:** The stability claim (Contribution 3) cannot be fully evaluated without exact values. Reviewers at ICML will reject on this point.

**Fix:** Re-run entropy scoring (< 1 GPU-hour), extract exact per-pair ρ values, and populate Table 2. This is the highest-priority unresolved issue from R1.

### R2-MAJOR-002: "Pmlr 2026" phantom citation still unresolved (INHERITED from R1-M3, upgraded to MAJOR)

**Status: UNRESOLVED from R1 (was MINOR M3, now upgraded).**

The citation "[Pmlr 2026]" in Section 2.4 is a non-functional placeholder. In R1 it was flagged as MINOR (M3). However, re-examining the usage: "The use of Spearman rank correlation for stability validation follows calibration quality analysis approaches [Pmlr 2026] that assess how consistently a given measurement criterion ranks model components across different data subsets." This citation is used to justify the methodological choice of Spearman ρ as the stability metric. If a reviewer searches for "Pmlr 2026" in the references, they will not find an entry — because none exists. This creates the appearance of a fabricated reference. This is a credibility-destroying issue that could result in desk rejection. Upgraded from MINOR to MAJOR.

**Fix:** Either find the actual paper this refers to (it may be a PMLR proceedings paper, e.g., from ICML or AISTATS 2026) and insert proper citation, or remove the citation and state the methodological choice is standard without reference, or cite a well-known source for Spearman ρ in model stability analysis.

### R2-MAJOR-003: GPU-time arithmetic inconsistency (INHERITED from R1-M1, upgraded to MAJOR)

**Status: UNRESOLVED from R1 (was MINOR M1, now upgraded after re-analysis).**

"≈ 20–30 GPU-minutes per subset" × 3 subsets = 60–90 GPU-minutes. The upper bound (90 min = 1.5 GPU-hours) exceeds the claimed "< 1 GPU-hour" for all three subsets. The claim appears in:
- Introduction: "< 1 GPU-hour"
- Section 3.2.2: "≈ 20–30 GPU-minutes for 100 forward passes through Llama-2-7B on a single H100"
- Section 4.5: "approximately 20–30 minutes per subset on H100. Total calibration: approximately 1 GPU-hour for all three subsets."

Section 4.5 actually says "approximately 1 GPU-hour" (not "< 1 GPU-hour"), which is consistent with 3 × 20 min = 60 min ≈ 1 hour. However, the Introduction states "< 1 GPU-hour" as the key selling point. A reviewer reading "30 min per subset × 3 = 90 min > 1 hour" will immediately flag this. Either: (a) the upper bound should be reduced to "~20 GPU-minutes per subset" (eliminating the 30-min upper end), or (b) the Introduction claim should say "~1 GPU-hour" rather than "< 1 GPU-hour."

**Fix:** Tighten either the per-subset range to "~20 GPU-minutes" or the total claim to "approximately 1 GPU-hour." These must be mutually consistent.

### R2-MAJOR-004: Contribution 4 ("Entropy-Guided Selective SWA Framework") framing ambiguity (PARTIALLY RESOLVED from R1-MAJOR-003)

**Status: PARTIALLY RESOLVED — improved but still problematic.**

The R1 revision reframed Contribution 4 in the introduction as "framework design" rather than validated outcome, and added the explicit scope disclaimer: "This contribution documents the framework design, not a validated outcome." This is an improvement. The abstract now clearly scopes the paper as a "complete, confirmatory study of the entropy criterion's validity as a layer characterization tool" rather than a framework validation.

However, the paper remains formatted as ICML2025 while openly stating 4/5 hypotheses are pending. The fundamental structural problem (an interim paper in a complete-paper venue format) persists. The abstract still describes k=4 conversion and SWA as if they were executed ("we design a zero-shot framework... converting the k=4 highest-entropy layers to SWA(w=512)"), which could mislead a rushed reviewer.

**Remaining issue:** The Introduction's contribution list presents Contribution 4 alongside three confirmed contributions, giving the impression of four equivalent contributions. Contribution 4 is categorically different — it is a design document, not an experimental result. Consider visually differentiating confirmed vs. pending contributions (e.g., a footnote or a "(Design, Pending Validation)" tag consistently applied).

### R2-MAJOR-005: "Architectural invariant" claim overshoots the evidence (NEW)

**Severity: MAJOR**

Section 5.1 states: "This universality suggests attention concentration is an architectural invariant of Llama-2-7B's trained weights, not an artifact of specific input sequences." Section 6.1 repeats: "If attention concentration is architecturally grounded rather than input-driven, then the entropy criterion may generalize across input domains."

The evidence base: n=200 evaluation examples from WikiText-103. This is a single domain (English Wikipedia-style text), a single model, evaluated on one split of one benchmark. The 100% satisfaction rate is striking — but calling it an "architectural invariant" on the basis of 200 in-domain examples is an overreach. An architectural invariant should hold across domains, but the paper itself admits "Cross-domain calibration stability remains an open question" (L2, Section 6.3). A skeptical reviewer will immediately ask: what if code text, dialogue, or mathematical text shows different Gini profiles? If the "invariant" claim fails cross-domain, the paper's practical value (practitioners can calibrate on any data) is reduced.

The paper acknowledges this limitation in Section 6.3 (L2). But the strong claim "architectural invariant" in Section 5.1 and 6.1 contradicts the limitation acknowledgment — if it is an open question whether it is invariant, calling it an invariant in the results section is overconfident language.

**Fix:** Replace "architectural invariant" with "stable structural property (within WikiText-103 domain)" in Sections 5.1 and 6.1. Keep the speculation about invariance as a hypothesis in Section 6.1 with explicit hedging: "This suggests — but does not confirm — that concentration may be an architectural invariant."

---

## MINOR Issues (for human review only)

**R2-M1 (INHERITED from R1-M5):** Xiao2024StreamingLLM citation is flagged as UNVERIFIED in the reference list. The arXiv ID 2309.17453 is from domain knowledge and likely correct (ICLR 2024 paper), but year 2024 vs. arXiv submission 2023 may need adjustment. Verify before submission.

**R2-M2 (NEW):** Section 4.4 defines Gini using "w_i are the per-token attention weights (summed across heads and head positions to produce a per-token scalar)." This is an implementation choice — summing across all heads and positions before computing Gini — that is not the same as computing Gini over raw attention weight entries. The formula is presented as standard, but the derived quantity (aggregated per-token weight) is specific. This should be stated more precisely to enable reproducibility.

**R2-M3 (NEW):** Section 7 (Conclusion) states: "head-mean Gini is 32% higher than head-max Gini relative to head-mean." This phrasing is awkward and slightly self-referential. "32% higher relative to head-mean" means head-mean is the denominator, so the claim is "(head-mean − head-max) / head-mean = 32%", which is correct but the phrase "32% higher relative to head-mean" is unusual and could confuse readers. Consider: "head-mean Gini (0.681) exceeds head-max Gini (0.466) by 32% relative to head-mean."

**R2-M4 (INHERITED from R1-M10, partially):** Section 6.3 L4 cites SWARR [Liu et al., 2026] as context for fine-tuning-free conversion challenges. The paper now correctly states "SWARR demonstrates that SFT alone is insufficient after SWA conversion — this underscores the challenge of fine-tuning-free conversion." This is an accurate reading of the citation. R1 concern is resolved.

**R2-M5 (INHERITED from R1-M2):** Section 3.6 code structure lists h-e2/code/ with full file listing (swa.py, eval.py, verify.py, run.py), tagged as "[designed; execution pending]." This is fine as a design artifact, but presenting a full code module structure for unexecuted code could mislead reviewers into thinking the code has been tested.

---

## Baseline Fairness Assessment

Section 4.3 describes three baselines: full-attention (k=0), random-k=4, and last-k=4. The section ends with: "Note: these comparisons are designed for h-m1 and have not yet been executed; no superiority claims are made at this stage."

**Assessment: FAIR.** The baselines section explicitly disclaims execution. No superiority claims appear in the paper — the Introduction, Abstract, and Conclusion are all careful to say the accuracy-preservation comparison is pending. Section 5.4 (exploratory QA F1 probe) correctly labels the directional result as non-significant and non-confirmatory. Section 6.2 explicitly states: "No superiority claim is made at this stage."

**Remaining risk:** The exploratory QA F1 result (Section 5.4) reports entropy degrading F1 by 0.43 pp vs random's 0.67 pp. Even though the paper repeatedly disclaims significance (p=0.4507), the mere presentation of this as a "directional advantage" could be read by a reviewer as cherry-picking a metric that happened to show a positive trend. The framing is technically honest but strategically borderline. Placing this result in Section 5 (Results) rather than Discussion remains a credibility risk (this was R1-MAJOR-007, which was fixed by the revision — verify Table 4 is no longer in Section 5). **Check:** Table 4 is not visible in Section 5 of the R1 revision — Section 5.4 contains the QA F1 discussion inline, labeled "Exploratory Selection Criterion Probe," without a standalone results table. This is an improvement, but the content still appears in the Results section. Moving it to Discussion would be cleaner.

---

## Persuasiveness Re-Check

| Check | R1 Result | R2 Result | Change |
|-------|-----------|-----------|--------|
| Abstract compelling? | PASS | PASS | Stable — numbers are tight, problem is clear |
| FATAL-001 (32% vs 46.1%) resolved? | FAIL | PASS | Fixed via Table 3 footnote |
| Table 1 matches ground truth? | PASS | PASS | All five values verified |
| GPU-time arithmetic consistent? | BORDERLINE (M1) | MAJOR-003 | Not fixed, upgraded severity |
| Spearman ρ exact values reported? | FAIL (MAJOR-001) | FAIL | Still unresolved |
| Contribution 4 framing improved? | FAIL (MAJOR-003) | PARTIAL | Better but venue mismatch persists |
| "Pmlr 2026" citation fixed? | FAIL (M3) | MAJOR-002 | Not fixed, upgraded severity |
| Figure 6 labeled as placeholder? | FAIL (MAJOR-004) | PASS | R1 revision labels it "schematic illustration... placeholder figure" |
| Baseline fairness | PASS | PASS | Stable |
| QA F1 table moved from Results? | FAIL (MAJOR-007) | PARTIAL | Now inline, still in Section 5 |
| "Architectural invariant" claim hedged? | — | FAIL (NEW) | New issue identified in R2 |

---

## Skeptical Expert Verdict

### Would accept or reject at ICML?

**Verdict: REJECT (Major Revision required before resubmission)**

**Reasoning:**

The paper has made genuine progress from R1 to R1-revision: the FATAL 32%/46.1% inconsistency is resolved, Figure 6 is properly labeled as a placeholder, and Contribution 4 is reframed as "framework design." These are meaningful improvements.

However, three blocking issues remain:

1. **Spearman ρ exact values (MAJOR-001):** Reporting only "≥ 0.8" for the stability claim — the paper's central gating criterion — without exact numerical values is not acceptable at a top-tier ML venue. This is fixable in < 1 GPU-hour. That it was flagged in R1 and not fixed is the most damaging signal.

2. **Phantom "Pmlr 2026" citation (MAJOR-002):** A non-resolvable citation key that produces no bibliography entry is, at minimum, a serious error and, at worst, appears fabricated. Peer reviewers will search for it and find nothing.

3. **Venue mismatch:** The paper remains formatted as ICML2025 while openly acknowledging 4/5 hypotheses are pending execution. For a workshop on efficiency, efficiency at inference, or a systems venue, this might be acceptable as a "work in progress" paper. For the ICML main track, the core hypothesis (P1: SWA conversion within 2pp) is entirely untested. The paper's genuine contributions (concentration characterization, pooling ablation, stability validation) are real but insufficient for a main-track paper at ICML without h-e2 results.

**Acceptance condition:** Execute h-e2 and h-m1, fix the Spearman table, resolve the Pmlr citation, and correct the GPU-time arithmetic. The underlying science is sound — the concentration finding (Gini = 0.6829, 100% satisfaction rate) is a real result, and the head-mean vs head-max ablation (32% relative gap) is a genuine methodological finding. This paper should not be abandoned — it needs h-e2 data.

**Where this paper would be accepted now:** NeurIPS 2025 or ICML 2026 Efficient LLM Systems workshop; ML Systems conference (MLSys) short paper track; possibly EMNLP findings as a characterization study. Not ICML main track without h-e2.

---

## Summary for Revision Agent R2

**Priority order:**

1. **R2-MAJOR-001 (CRITICAL):** Re-run entropy scoring, extract exact Spearman ρ for all three pairs (A-B, A-C, B-C), populate Table 2 with actual numbers. Runtime < 1 GPU-hour. This is the single highest-priority fix.

2. **R2-MAJOR-002 (HIGH):** Find or remove the "Pmlr 2026" citation. Either identify the actual PMLR paper (search for calibration stability + Spearman + PMLR proceedings 2025-2026), or remove the citation and state the methodological choice without it. Do not leave a phantom citation key.

3. **R2-MAJOR-003 (MEDIUM):** Reconcile GPU-time claim. Choose: either state "~20 GPU-minutes per subset, ~1 GPU-hour total" or "20–25 GPU-minutes per subset, < 2 GPU-hours total for three subsets." The current combination (30-min upper bound + "< 1 GPU-hour" total claim) is arithmetically inconsistent.

4. **R2-MAJOR-005 (MEDIUM):** Replace "architectural invariant" with "stable structural property (within the WikiText-103 evaluation domain)" in Sections 5.1 and 6.1. Keep the speculation about invariance hedged as an open question.

5. **R2-MAJOR-004 (LOW):** Consider visually differentiating Contribution 4 from Contributions 1–3 in the Introduction (e.g., a "(Design only, pending validation)" tag).

6. **R2-M1:** Verify StreamingLLM year (arXiv 2023, ICLR 2024) before submission.

7. **R2-M3:** Rephrase the awkward "32% higher relative to head-mean" sentence in the Conclusion.

**Issues resolved since R1:**
- FATAL-001 (32%/46.1% inconsistency): RESOLVED via Table 3 footnote
- MAJOR-004 (Figure 6 unlabeled): RESOLVED — now labeled as placeholder/schematic
- MAJOR-003 (Contribution 4 overclaim): PARTIALLY RESOLVED — improved framing

**Issues inherited unresolved from R1:**
- MAJOR-001 (Spearman exact values): UNRESOLVED → R2-MAJOR-001
- M3 (Pmlr 2026 citation): UNRESOLVED → R2-MAJOR-002 (upgraded)
- M1 (GPU-time arithmetic): UNRESOLVED → R2-MAJOR-003 (upgraded)
