# Adversarial Review - Round 1

**Paper:** Post-Optimizer Sampling for Accurate Lightweight GPU Memory Profiling
**Reviewed:** 2026-07-10T20:30:00+00:00
**Reviewer:** Adversary Agent v2

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy | 1 | 3 | CRITICAL |
| Engagement | 0 | 2 | NEEDS_WORK |
| Credibility | 0 | 5 | NEEDS_WORK |
| **TOTAL** | **1** | **10** | **MAJOR_REVISION** |

**Recommendation:** MAJOR_REVISION

**Critical Issue:** One FATAL numerical contradiction between ground truth data and paper claims requires immediate correction. Ten MAJOR issues span accuracy problems (incorrect statistical claims, missing data), engagement problems (buried problem statement, unclear novelty positioning), and credibility issues (overclaiming tone disproportionate to n=4 PoC, missing essential limitations).

---

## Part 1: Accuracy Check (Persona 1)

### Ground Truth Verification

| Metric | Paper Claims | Ground Truth | Match? |
|--------|--------------|--------------|--------|
| Median error | 2.6% | 2.6% | ✓ |
| VeritasEst baseline | 5.46% | 5.46% | ✓ |
| Reduction percentage | 52% | 52% | ✓ |
| P95 error | 6.1% | 6.1% | ✓ |
| ResNet-18+Adam error | 0.62% | 0.62% | ✓ |
| ResNet-34+Adam error | 0.00% | 0.00% | ✓ |
| ResNet-18+SGD error | 4.60% | **6.38%** | **✗ FATAL** |
| ResNet-34+SGD error | 6.40% | **4.57%** | **✗ FATAL** |
| Adam average error | 0.31% | 0.31% | ✓ |
| SGD average error | 5.5% | 5.475% | ✓ (rounded) |
| Configs tested | 4 | 4 | ✓ |
| Timeline: forward MB | 130MB | 130MB | ✓ |
| Timeline: backward MB | 175MB | 175MB | ✓ |
| Timeline: post-opt MB | 280MB | 280MB | ✓ |

### FATAL Issues - Accuracy

#### FATAL-ACC-001: SGD Error Values Swapped Between Architectures
**Location:** Table 1 (Section 5.4), Appendix B, Abstract (line 9)
**Issue:** ResNet-18+SGD and ResNet-34+SGD error values are swapped between ground truth and paper.
**Evidence:** 
- Paper claims: ResNet-18+SGD = 4.60%, ResNet-34+SGD = 6.40%
- Ground truth (065_ground_truth.yaml lines 156-163): ResNet-18+SGD = 6.38%, ResNet-34+SGD = 4.57%
**Impact:** This is FATAL because:
1. It reverses the architectural trend (paper shows larger model = higher error; ground truth shows opposite)
2. Affects narrative about consistency (Section 5.3 claims all configs <7%; ResNet-34+SGD at 4.57% is much safer margin than 6.40%)
3. SGD average (5.475%) is correct but derived from wrong per-config values
4. Abstract claims "all tested configurations remain below 7% error" which is still true, but the data supporting it is incorrect
**Required Fix:** 
1. Correct Table 1 values: ResNet-18+SGD → 6.38%, ResNet-34+SGD → 4.57%
2. Update Appendix B table with same corrections
3. Review Section 5.4 narrative to reflect correct architectural scaling trend
4. Verify no downstream claims depend on the incorrect ordering

### MAJOR Issues - Accuracy

#### MAJOR-ACC-001: Memory Timeline Values Missing Ground Truth Match
**Location:** Section 5.2, Figure 2 description (lines 276-279)
**Issue:** Paper reports "Post-backward: 175 MB" but ground truth shows "t2_backward_mb: 175" which is correct. However, paper reports "150MB allocation" during optimizer.step (280-130=150) while ground truth shows workspace_allocation_mb: 150 (280-130). The calculation is correct but not transparently linked to ground truth schema.
**Evidence:** Ground truth lines 171-177 provide full timeline; paper cherry-picks specific values without showing complete sequence.
**Suggested Fix:** Add Appendix section mapping Figure 2 values to ground truth measurements with complete timeline (t0=45MB, t1=130MB, t2=175MB, t3=280MB) to enable full verification.

#### MAJOR-ACC-002: Table 1 Memory Values Inconsistent with Ground Truth Schema
**Location:** Table 1 (Section 5.4), lines 298-304
**Issue:** Table 1 shows "Ground Truth (MB)" values that don't precisely match ground truth yaml (e.g., Table shows 280.1 MB for ResNet-18+Adam, ground truth shows 282.09 MB; Table shows 538.2 MB for ResNet-34+Adam, ground truth shows 474.93 MB).
**Evidence:**
- Ground truth line 142: ResNet-18+Adam ground_truth_mb: 282.09 (Paper Table 1: 280.1)
- Ground truth line 148: ResNet-34+Adam ground_truth_mb: 474.93 (Paper Table 1: 538.2)
- Ground truth line 154: ResNet-18+SGD ground_truth_mb: 206.43 (Paper Table 1: 193.4)
- Ground truth line 160: ResNet-34+SGD ground_truth_mb: 325.61 (Paper Table 1: 370.8)
**Impact:** ALL memory values in Table 1 are incorrect. This suggests Table 1 was created from a different data source than the ground truth yaml. Relative errors may still be approximately correct if predicted values are also scaled proportionally, but this breaks reproducibility.
**Suggested Fix:** 
1. Regenerate Table 1 using exact values from ground truth yaml lines 141-163
2. Verify predicted_mb values match ground truth (predicted_mb: 280.34 for ResNet-18+Adam, etc.)
3. Recalculate absolute errors to ensure consistency

#### MAJOR-ACC-003: Missing Explicit Acknowledgment of n=4 Statistical Invalidity
**Location:** Section 6.2, lines 329-331
**Issue:** Paper states "p=0.0625, n=4" and "underpowered test" but doesn't explicitly state that p>0.05 means the null hypothesis (no difference between methods) CANNOT be rejected. The paper's framing "large effect size provides conceptual evidence" is technically correct but obscures that the results are not statistically significant by conventional standards.
**Evidence:** Ground truth line 102 explicitly states "Statistical significance unestablished (p=0.0625, n=4)" with severity: MEDIUM and mitigation plan. Paper acknowledges underpowered test but doesn't clearly state "our results do not achieve statistical significance."
**Suggested Fix:** Add explicit statement in Section 6.2: "With p=0.0625 (>0.05 threshold), we cannot reject the null hypothesis that post-optimizer and pre-optimizer sampling produce equivalent errors. However, the large effect size (52% relative reduction) and consistent directional findings across all 4 configurations provide conceptual evidence supporting our mechanism. Formal statistical confirmation requires the full 48-configuration validation."

---

## Part 2: Engagement Check (Persona 2)

### Bored Reviewer Verdict

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | ✓ | Quantitative hook (52% reduction) is strong; "timing matters as much as count" is intriguing |
| Problem clear in 1 min? | ✗ | Abstract leads with "OOM failures waste GPU-hours" (general problem) but doesn't explain why existing 5.46% error is insufficient until line 8 |
| Novelty clear in 2 min? | ✗ | Introduction paragraph 3 (lines 20-22) buries the novelty: "sampling timing within iterations has been underexplored" appears AFTER two paragraphs of prior work praise |
| Figure 1 self-explanatory? | ✓ | "2.6% vs 5.46%" comparison is clear (though Figure 1 not provided, description suggests it's interpretable) |
| Would continue reading? | ✓ | Hook is strong enough; quantitative claims (52%, 10×) create curiosity |

**Attention Lost At:** Introduction paragraph 2 (lines 20-22) — two paragraphs praising VeritasEst before stating the gap makes me wonder "is this just an incremental tweak?"

### MAJOR Issues - Engagement

#### MAJOR-ENG-001: Problem Statement Buried Under Prior Work Praise
**Location:** Introduction, lines 15-23
**Issue:** First two paragraphs extensively praise VeritasEst (84% error reduction, CPU-based simulation, segment-level fragmentation) and Kang et al. (8.7% MAPE, factorization) before stating the problem in paragraph 3. For a bored reviewer skimming, this reads like "existing work is great" → "why am I reading this paper?"
**Suggested Fix:** Restructure Introduction:
1. Paragraph 1: Hook with quantitative finding (current)
2. Paragraph 2: Explain why 5.46% error is insufficient (e.g., "1 in 7 predictions exceeds 10% → unacceptable for production")
3. Paragraph 3: "Prior work made progress BUT missed timing window" (flips structure)
4. Paragraph 4: Our insight (current paragraph starting line 24)

#### MAJOR-ENG-002: Figure 2 Description Too Technical for Visual Intuition
**Location:** Section 3, lines 138-147; Section 5.2, lines 274-285
**Issue:** Memory timeline is described with raw numbers (130MB, 175MB, 280MB) but lacks a visual analogy to make the "rush hour" concept concrete. The highway analogy appears only in Conclusion (line 365), too late for readers who need intuition during Methodology.
**Suggested Fix:** Add analogy in Section 3 (Methodology) or Section 5.2 (Results) when first presenting timeline: "Like measuring highway traffic at 3 PM (post-backward: 175MB) versus 5 PM rush hour (post-optimizer: 280MB), sampling before optimizer.step() misses the peak allocation moment."

---

## Part 3: Credibility Check (Persona 3)

### Novelty Claims Audit

| Claim | Location | Verified? | Notes |
|-------|----------|-----------|-------|
| "First work to optimize sampling timing within iterations" | Intro line 241, Contributions para | ✓ | Supported by literature review; VeritasEst focused on iteration count, not timing |
| "First empirical demonstration of optimizer-specific profiling accuracy" | Intro line 33, Contrib #2 | ✓ | Ground truth confirms 10× difference; no prior work cited on this |
| "52% error reduction vs state-of-the-art" | Abstract, Intro, Results | ✓ | Calculation verified (5.46% → 2.6% = 52.4% reduction) |
| "Production-ready accuracy (<3% error)" | Abstract line 9, Intro line 241 | QUESTIONABLE | n=4 CNNs only; "production-ready" overclaims scope |
| "All tested configurations <7% error" | Abstract line 9, Results 5.3 | ✓ | Ground truth confirms (after fixing FATAL-ACC-001) |

### Baseline Fairness Audit

**VeritasEst Comparison:** Paper correctly describes VeritasEst as pre-optimizer sampling (Section 2, lines 50-54) and positions post-optimizer as complementary timing optimization. Comparison is fair—both use allocator simulation, same ground truth method (10-iteration stabilization). ✓

**No Other Baselines:** Paper only compares against VeritasEst. Tensor-sum methods are mentioned but dismissed as "known failures" (Section 4, line 248) without quantitative comparison. This is acceptable given VeritasEst is SOTA, but limits context. Acceptable but noted.

### MAJOR Issues - Credibility

#### MAJOR-CRED-001: "Production-Ready" Overclaim for n=4 PoC Scope
**Location:** Abstract (line 10 "production-ready"), Introduction (line 241 "production-ready memory profiling"), Contributions (line 34 "production-grade")
**Issue:** Paper repeatedly uses "production-ready" and "production-grade" language for a 4-configuration proof-of-concept scoped to CNNs with synthetic data. This is tone overclaiming: results demonstrate *feasibility* of accurate profiling, not *production readiness*.
**Evidence:**
- n=4 (not statistically significant)
- 0/8 transformer architectures tested (ground truth line 99)
- Synthetic data only (no DataLoader overhead validated)
- No real dataset validation
**Impact:** This language creates false confidence that the method is deployable in production settings. Reviewers will question: "If it's production-ready, why only 4 configs? Why no transformers?"
**Suggested Fix:** Replace "production-ready" with:
- Abstract: "achieving 2.6% median error—accuracy suitable for pre-training OOM prediction in CNN training scenarios"
- Introduction: "validates the existence of accurate lightweight memory profiling for CNNs"
- Contributions: "enables production-grade memory profiling [for CNNs]" → "establishes feasibility of sub-3% error profiling"

#### MAJOR-CRED-002: Missing Critical Limitation - Dual-Axis Integration Incomplete
**Location:** Section 6.2 (Limitations), Conclusion
**Issue:** Ground truth yaml (line 117) explicitly lists "Dual-axis integration incomplete (h-e2 throughput profiling deferred)" as a limitation with severity: LOW. Paper completely omits this limitation from Section 6.2 and never mentions that the broader hypothesis (dual-axis memory+throughput routing) is incomplete.
**Evidence:** 
- Ground truth line 119: "Paper scoped to memory profiling only (h-e1); throughput profiling (h-e2) is separate hypothesis"
- Narrative blueprint line 18 hypothesis_title includes "Post-Optimizer Sampling" but doesn't reference dual-axis
- Paper scope (line 36-37) mentions transformers, statistical power, synthetic data but not dual-axis
**Impact:** Omitting this limitation creates false impression that memory profiling alone solves OOM prediction. If the original hypothesis was dual-axis (memory+throughput), readers deserve to know throughput is unaddressed.
**Suggested Fix:** Add limitation to Section 6.2: "Dual-axis integration with throughput profiling (hypothesis h-e2) remains incomplete. This work addresses memory profiling only; joint memory-throughput prediction for comprehensive OOM avoidance is future work."

#### MAJOR-CRED-003: Transformer Limitation Framed Too Optimistically
**Location:** Section 6.2, lines 327-329
**Issue:** Paper states transformers are "a natural extension, not a fundamental barrier" and "architecture-agnostic at the allocator level." This is defensive framing that minimizes a critical scope limitation: 0/8 planned architectures tested.
**Evidence:**
- Ground truth line 99 lists 8 transformer architectures as unvalidated (BERT, GPT-2, T5, DistilBERT, RoBERTa, ALBERT, DeBERTa, ViT)
- Transformers have O(n²) attention scaling, variable-length sequences, and stratified sampling complexity explicitly noted in ground truth
- Narrative blueprint line 327 acknowledges transformers introduce "architectural complexity" that "may interact with post-optimizer timing in unexplored ways"
**Impact:** Framing this as "acceptable limitation" for an "initial validation" understates that transformers represent >50% of modern deep learning workloads (LLMs, vision transformers). A reviewer might ask: "If the mechanism is architecture-agnostic, why didn't you test even 1 transformer?"
**Suggested Fix:** Reframe limitation more honestly in Section 6.2: "Transformer architectures remain unvalidated (0/8 planned). While post-optimizer sampling is allocator-level and should generalize, transformers' O(n²) attention scaling and variable-length sequences introduce complexity requiring empirical validation. This is a significant scope limitation given transformers' prevalence in modern ML."

#### MAJOR-CRED-004: SGD Mystery Not Flagged as Research Question
**Location:** Section 5.4 (lines 305-309), Section 6.4 Future Work (line 349)
**Issue:** Paper presents SGD's 10× higher error as "surprising finding" (line 295) and proposes explanations (lines 305-308) but doesn't explicitly acknowledge this as a *failure* to understand the mechanism. If post-optimizer timing is the "critical factor" (line 319), why does it fail for SGD?
**Evidence:**
- Ground truth lines 55-58 list "Why does SGD achieve higher error despite smaller workspace?" as open_questions
- SGD achieves 5.5% error (vs Adam 0.31%)—this is a 17× difference, not 10× (ground truth line 168 notes "rounded to 10× for readability")
- Paper proposes "SGD's momentum buffer allocation timing may differ" but provides no evidence
**Impact:** The unexplained SGD result undermines the mechanistic claim. If the mechanism is "workspace allocation timing," the protocol should work equally well for any optimizer once you identify its allocation timing. The fact that it doesn't suggests the mechanism is incomplete or Adam-specific.
**Suggested Fix:** 
1. Section 5.4: Add explicit acknowledgment: "This finding challenges our mechanistic explanation: if post-optimizer timing captures workspace allocations, why doesn't it work equally well for SGD? This suggests optimizer-specific timing profiles require investigation."
2. Section 6.4: Elevate SGD investigation to high-priority: "Understanding SGD's allocation timing is critical to validate whether post-optimizer sampling is a general mechanism or Adam-specific optimization."

#### MAJOR-CRED-005: "Definitive Answer" Overclaim in Conclusion
**Location:** Conclusion (line 356)
**Issue:** Conclusion states "Our results provide a definitive answer—post-optimizer timing achieves 52% error reduction... demonstrating that sampling timing is as critical as iteration count." The word "definitive" overclaims for n=4 with p=0.0625 (not statistically significant).
**Evidence:**
- p=0.0625 > 0.05 (no statistical significance)
- n=4 provides ~40% statistical power (ground truth line 180)
- Limited to CNNs only
**Impact:** "Definitive" implies conclusive proof. This is not supported by underpowered statistics and narrow scope.
**Suggested Fix:** Replace "definitive answer" with "compelling directional evidence" or "strong conceptual support": "Our results provide compelling directional evidence—post-optimizer timing achieves 52% error reduction across 4 CNN configurations, demonstrating that sampling timing is as critical as iteration count for accurate memory profiling. Formal statistical confirmation requires broader validation."

#### MAJOR-CRED-006: Abstract Mentions "AdamW" But Not Validated
**Location:** Abstract (line 7), Experimental Setup (line 206)
**Issue:** Abstract lists "Adam, AdamW, and SGD optimizers" but paper never presents AdamW results. Table 1 (Section 5.4) shows only Adam and SGD. Appendix B shows only Adam and SGD.
**Evidence:**
- Ground truth line 208 lists optimizers as "Adam, AdamW, SGD" in validated_scope
- Ground truth results_table (lines 141-163) shows only ResNet-18/34 + Adam/SGD (4 configs, not 6)
- Paper Experimental Setup (line 206) mentions AdamW but no results appear
**Impact:** This is misleading—readers expect AdamW results based on Abstract. If AdamW wasn't tested, don't claim it in Abstract.
**Suggested Fix:** 
- Option 1: Remove AdamW from Abstract and Experimental Setup
- Option 2: Add footnote: "AdamW results similar to Adam (both allocate 2× parameter memory); presented results focus on Adam vs SGD contrast"

---

## Part 4: Human Review Notes

> Minor issues for human review during final polish (NOT auto-fixed)

| Location | Note | Type |
|----------|------|------|
| Line 10 (Abstract) | "95th percentile error" → "P95 error" for consistency with rest of paper | style |
| Line 22 (Intro) | "factorization into model parameters (M_param), gradients (M_grad)..." → italics inconsistent, use math mode or remove | formatting |
| Line 54 (Related Work) | "VeritasEst's 2-iteration protocol samples memory after the first forward pass and again after the second full training iteration" → wordy, consider "samples memory after iteration 1 forward pass and iteration 2 completion" | clarity |
| Line 89 (Method) | "Iteration 1: Forward-Only Pass" heading style inconsistent with rest of section (bold vs sentence case) | formatting |
| Line 142 (Method) | Timeline bullets use em-dash, other lists use bullet points—pick one style | formatting |
| Line 224 (Exp Setup) | "torch.cuda.max_memory_allocated()" → code formatting missing (should be monospace) | formatting |
| Line 266 (Results) | "Figure 1: Memory Accuracy Comparison" → Figure caption not provided, only described in text | missing element |
| Line 274 (Results) | "Figure 2: Post-Optimizer Memory Timeline" → Figure caption not provided | missing element |
| Line 287 (Results) | "Figure 3: Error Distribution" → Figure caption not provided | missing element |
| Line 298 (Results) | Table formatting: consider adding units (MB) to column headers instead of repeating in every cell | clarity |
| Line 356 (Conclusion) | "definitive answer" → overclaim (see MAJOR-CRED-005) but flagging as tone issue | tone |
| Line 375 (Conclusion) | "Key references:" section has inconsistent citation format vs main text | formatting |
| Appendix C | Code snippet missing comments explaining timing-critical steps beyond "CRITICAL" comment | clarity |

---

## Part 5: Persuasiveness Analysis (from Narrative Blueprint)

### Narrative Coherence Check

| Element | Status | Notes |
|---------|--------|-------|
| Hook → Conclusion callback | ✓ | "When matters as much as how many" (Intro) → "3PM misses 5PM rush hour" (Conclusion) effective |
| Key insight emphasized | ✓ | "Post-optimizer timing" appears in Abstract, Intro, Method, Results, Discussion consistently |
| Claims supported by evidence | ✓ | Main claims (52% reduction, mechanism, consistency) all have corresponding Results sections |
| Surprising finding handled | ✓ | SGD 10× difference acknowledged and discussed, though mechanism unexplained |
| Limitations acknowledged | Partial | Transformers, statistical power, synthetic data acknowledged; dual-axis integration omitted (see MAJOR-CRED-002) |

### Persuasiveness Strengths

1. **Quantitative hooks effective:** 52% reduction, 10× optimizer difference, 2.6% error—all create concrete takeaways
2. **Counterintuitive finding compelling:** "Timing matters as much as count" challenges reader assumptions
3. **Mechanism validation strong:** Memory timeline (130→280MB) provides visual evidence of workspace capture
4. **Honest about scope:** Paper explicitly scopes to CNNs, synthetic data, small n (though tone overclaims in places)

### Persuasiveness Weaknesses

1. **Overclaiming tone disproportionate to evidence:** "Production-ready" for n=4 PoC; "definitive answer" for p=0.0625
2. **Novelty positioning defensive:** Extensive VeritasEst praise before stating gap (see MAJOR-ENG-001)
3. **SGD mystery unresolved:** 10× difference unexplained—undermines "timing is critical factor" claim
4. **Transformer limitation too optimistic:** "Natural extension, not fundamental barrier" minimizes 0/8 architectures tested

---

## Summary for Revision Agent

### Priority Fix List

1. **FATAL-ACC-001:** Swap ResNet-18+SGD and ResNet-34+SGD error values in Table 1, Appendix B — MUST FIX
2. **MAJOR-ACC-002:** Regenerate Table 1 with correct ground truth memory values from yaml — MUST FIX
3. **MAJOR-CRED-001:** Remove "production-ready" language; replace with "establishes feasibility" — SHOULD FIX
4. **MAJOR-CRED-006:** Remove AdamW from Abstract or explain why no results shown — SHOULD FIX
5. **MAJOR-ACC-003:** Add explicit "p>0.05 means not statistically significant" statement in Section 6.2 — SHOULD FIX
6. **MAJOR-CRED-002:** Add dual-axis integration limitation to Section 6.2 — SHOULD FIX
7. **MAJOR-CRED-003:** Reframe transformer limitation more honestly (not "natural extension") — SHOULD FIX
8. **MAJOR-CRED-004:** Acknowledge SGD mystery as mechanism failure, not just "surprising finding" — SHOULD FIX
9. **MAJOR-CRED-005:** Replace "definitive answer" with "compelling evidence" in Conclusion — SHOULD FIX
10. **MAJOR-ENG-001:** Restructure Introduction to state problem before praising prior work — SHOULD FIX
11. **MAJOR-ENG-002:** Add "highway rush hour" analogy earlier (Method or Results, not just Conclusion) — SHOULD FIX

### Key Concerns

1. **Data integrity issue:** Table 1 memory values don't match ground truth yaml—suggests data was copied from wrong source or manually entered with errors. This breaks reproducibility and must be fixed with yaml-sourced values.

2. **Tone-evidence mismatch:** Language ("production-ready," "definitive answer") overclaims relative to n=4 PoC scope. This is NOT a style preference—it's a credibility issue. n=4 with p=0.0625 is a feasibility study, not a production-validated system.

3. **Unexplained mechanism gap:** SGD's 10× higher error contradicts the "timing is critical factor" narrative. If the mechanism were complete, the protocol should work for any optimizer once you identify its timing. The paper needs to either (a) explain SGD's timing difference with evidence, or (b) acknowledge this as a limitation/research question, not a "surprising finding."

4. **Missing limitations:** Dual-axis integration (h-e2 incomplete) not mentioned despite being in ground truth. Transformer limitation framed too optimistically given 0/8 tested.

### What's Working

1. **Quantitative results:** 2.6% median error, 52% reduction, 10× optimizer difference—all strong, concrete findings
2. **Mechanistic evidence:** Memory timeline (130→280MB) provides clear visual proof of workspace capture
3. **Honest about scope boundaries:** Paper explicitly scopes to CNNs, synthetic data, n=4 (even if tone overclaims)
4. **Novelty claim justified:** "First to optimize sampling timing within iterations" is well-supported by literature review
5. **Fast validation methodology:** 4 seconds for 4 configs is genuinely valuable for research velocity

### Recommendation Rationale

**MAJOR_REVISION** because:
- 1 FATAL numerical error (SGD values swapped) requires data correction
- Table 1 memory values don't match ground truth (data integrity issue)
- Tone overclaims ("production-ready," "definitive") disproportionate to n=4 PoC evidence
- Missing critical limitations (dual-axis integration, transformer scope)
- SGD mechanism gap unexplained

These issues are fixable without new experiments—mostly require reframing tone, correcting data, and acknowledging limitations more honestly. Core contributions (post-optimizer timing, 52% reduction, optimizer-specific accuracy) are valid and valuable.

**NOT CONDITIONAL_ACCEPT** because tone overclaiming and data integrity issues would raise red flags in peer review. Fix these issues first, then paper is strong.

**NOT REJECT** because core scientific contribution is sound: post-optimizer timing does capture workspace allocations better than pre-optimizer sampling, demonstrated on 4 CNN configs with clear mechanistic explanation. Scope limitations are acceptable for initial validation; tone just needs calibration.
