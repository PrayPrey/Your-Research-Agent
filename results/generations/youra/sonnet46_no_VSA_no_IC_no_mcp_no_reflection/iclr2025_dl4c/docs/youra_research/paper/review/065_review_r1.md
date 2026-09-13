# Adversarial Review — Round 1 (R1): Accuracy and Engagement

**Paper:** When Reward Granularity Matters: Mechanistic Analysis of Ratio vs. Binary Reward in GRPO Post-Training for Code LLMs  
**Review Round:** R1 — Structural Issues, Accuracy, and Engagement  
**Date:** 2026-08-31  
**Personas:** Accuracy Checker, Bored Reviewer, Skeptical Expert  

---

## Ground Truth Summary

| Claim ID | Value | Source |
|----------|-------|--------|
| C1 | Binary adv. var. = 0.0000 for [0,0,1,2,0,3,0,0] | h-e1/04_validation.md §3.1 |
| C2 | Ratio adv. var. = 0.0475 for [0,0,1,2,0,3,0,0] | h-e1/04_validation.md §3.1 |
| C6 | 987/1000 (98.7%) groups binary=0 variance | h-e1/04_validation.md §3.1 |
| C11 | h-e1: 17/17 unit tests pass | h-e1/04_validation.md §1 |
| C12 | h-m1: 18/18 unit tests pass | h-m1/04_validation.md §1 |
| C13 | Total: 35/35 unit tests pass | Derived |
| C14 | h-m1 reward_mean = 0.0000 at all steps | h-m1/04_validation.md §6 |
| C15 | h-m1 clipped_ratio = 1.0000 at all steps | h-m1/04_validation.md §6 |
| C16 | h-m1 fraction_partial = NaN | h-m1/04_validation.md §6 |
| C17 | Grad norm CI: mean +0.000730, 95%CI [−0.000253, +0.002561] | 045_validated_hypothesis.md §4.2 |
| C18 | 208 logged steps total | h-m1/04_validation.md §3.1 |
| C20 | APPS ≥5 test cases: n=1,789 | h-e1/04_validation.md §2 |

---

## Executive Summary

| Severity | Count | Resolved |
|----------|-------|---------|
| FATAL | 1 | 0 |
| MAJOR | 3 | 0 |
| MINOR (human review) | 6 | 0 |

**Recommendation:** MAJOR_REVISION — One FATAL issue (max_new_tokens configuration discrepancy) and three MAJOR issues require resolution before acceptance.

---

## PERSONA 1: ACCURACY CHECKER

*Role: Fact-checker and claim verifier. Verifying all numerical claims against ground_truth.*

### FATAL Issues

**FATAL-001: max_new_tokens Inconsistency — h-e1 config vs. paper claim**

- **Location:** Section 3.5 (Table: Training Configuration), Section 5.3, Section 3.3
- **Paper claims:** max_new_tokens = 512 in Table 3.5 (Training Configuration), and Section 3.4 ("max_new_tokens=512").
- **Ground truth (h-e1/04_validation.md §1.2):** "GRPOTrainer: generation_kwargs={'max_new_tokens': 256}"
- **Discrepancy:** The h-e1 smoke test was run with max_new_tokens=256, NOT 512. The paper's Training Configuration table lists max_new_tokens=512 as the unified value, which is incorrect for h-e1.
- **Why FATAL:** This is a direct factual error in the reported experimental configuration. Gradient norms in §5.3 ("steps 1–3 in range [3×10⁻⁴, 7×10⁻⁴]") were measured under a 256-token limit, not 512. A reviewer verifying the smoke test cannot reproduce it using the published configuration.
- **Fix required:** Either (a) add a separate row for h-e1 configuration (max_new_tokens=256) vs. h-m1 configuration (max_new_tokens=512), or (b) clarify in §3.3 or §5.3 that the smoke test used max_new_tokens=256 with a footnote.

---

### MAJOR Issues (Accuracy Checker)

**MAJOR-ACC-001: Figure 2 claims show reward trajectory for h-m1, but Figure description mixes h-e1 context**

- **Location:** Section 5.2, "Figure 2 (mean_reward.png) shows reward_mean trajectories for both conditions across the h-m1 training run."
- **Issue:** Figure 2 caption placement is in §5.2 "Scale of the Dead Zone: 1,000-Group Simulation" — a section about the h-e1 simulation. The figure actually shows h-m1 data. This creates confusion about which experiment produced which figure.
- **Severity:** MAJOR — A reviewer reading §5.2 will be confused about whether Figure 2 belongs to the simulation or the training run.
- **Fix:** Move Figure 2 reference to §5.4 (h-m1 results), or add clarifying text: "Figure 2 (shown in §5.4) shows..."

**MAJOR-ACC-002: Table 2 grad_norm row uses "~10⁻³" — inconsistent with CI reported in text**

- **Location:** Section 5.4, Table 2 row "grad_norm (mean, steps 1–136) | ~10⁻³ | ~10⁻³"
- **Issue:** Ground truth C17 gives specific values: mean diff = +0.000730 (≈ 7.3×10⁻⁴), CI [−0.000253, +0.002561]. The table uses "~10⁻³" which is correct as an order of magnitude but is imprecise compared to what the paper later reports in text.
- **Severity:** MAJOR — The table should use the actual measured values, not an approximation, especially since precise values are available and reported elsewhere in the same section. Using "~10⁻³" in the table while citing exact CIs in the text creates an apparent inconsistency.
- **Fix:** Update Table 2 grad_norm row to show the actual measured mean values (e.g., "0.00123 ± ... " or reference the CI directly), or at minimum align the precision.

---

## PERSONA 2: BORED REVIEWER

*Role: Busy NeurIPS reviewer with 5 papers to review today. Would I continue reading?*

### Persuasiveness Assessment

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | **PASS** | Opens with striking "98.7% zero gradient" stat + one-line fix. Immediately compelling. |
| Problem clear in 1 minute? | **PASS** | GRPO dead zone explained clearly in §1 paragraph 2. |
| Novelty clear in 2 minutes? | **PASS** | Contribution list in §1 is concrete and falsifiable. |
| Figure 1 self-explanatory? | **UNCERTAIN** | No actual figure rendered; caption says "reward_histograms.png" — cannot verify without figure. |
| Would continue reading? | **YES** | The hook is strong. Mathematical guarantee + null result framing is compelling. |
| Attention lost at? | "§6.3 Honest Limitations" | This section is excellent but the subsection "Real training gradient norm CI was pending at analysis time" is vague and could trigger skepticism. |

### MAJOR Issues (Bored Reviewer)

**MAJOR-ENG-001: Hook uses "Every published paper" — overclaiming scope**

- **Location:** Abstract, line 1: "Every published paper on reinforcement learning with execution feedback (RLEF) for code LLMs uses binary pass/fail reward"
- **Issue:** "Every published paper" is a very strong claim. The paper only cites CodeRL, PPOCoder, RLEF/Gehring, and DAPO. While probably true for major works, a reviewer can likely find counterexamples or edge cases (e.g., papers using partial-credit proxies). This claim is not verified in the literature review and is stated as fact.
- **Severity:** MAJOR (credibility) — A skeptical reviewer will immediately question this and may reject the paper if they find a counterexample.
- **Fix:** Qualify to: "Every major published paper we are aware of..." or "All four benchmark RLEF papers for code LLMs (CodeRL, PPOCoder, RLEF/Gehring, DAPO) use binary pass/fail reward." The §2 Related Work already names these four — match the abstract's scope to what is actually reviewed.

---

## PERSONA 3: SKEPTICAL EXPERT

*Role: Domain expert looking for holes in claims.*

### Novelty Assessment

The core novelty claim — formal analysis of the GRPO dead zone and ratio reward's mathematical guarantee — is genuine and not found in the cited prior work. DAPO [Yu et al., 2025] is the closest prior work and explicitly does not quantify the dead zone. The claim is defensible.

### MAJOR Issues (Skeptical Expert)

**MAJOR-SKE-001: §6.3 "Real training gradient norm CI was pending at analysis time" is an unresolved limitation**

- **Location:** Section 6.3, third bullet: "Real training gradient norm CI was pending at analysis time. The mechanistic proof served as primary evidence for h-e1; the numerical CI from the 150-step background run is supplementary."
- **Issue:** This statement creates a significant credibility problem. The paper reports gradient norm CIs in §5.4 (C17: mean +0.000730, CI [−0.000253, +0.002561]), yet §6.3 says this CI "was pending at analysis time." This implies the CI in §5.4 may have been added post-hoc or the limitation section was not updated after results arrived. A reviewer will ask: if the CI is now available and reported in §5.4, why does §6.3 still say it was "pending"?
- **Severity:** MAJOR — This internal inconsistency makes the paper appear incomplete or hastily assembled. 
- **Fix:** Remove or rewrite the §6.3 bullet. If the CI is now available and reported in §5.4, the limitation no longer holds. Replace with: "The gradient norm analysis is based on steps 1–136 of the h-m1 run; a longer run may show different patterns."

### Missing Limitations Assessment

- **PRESENT:** Dataset limitation (single APPS dataset) — ✓ acknowledged in §6.3
- **PRESENT:** Model scale limitation (single 6.7B model) — ✓ acknowledged in §6.3
- **MISSING:** No acknowledgment that the 1,000-group simulation uses synthetic groups (p_pass=0.1 assumed), not actual model outputs. Real early-training distributions may differ.
- **MISSING:** No acknowledgment that the h-e1 smoke test used max_new_tokens=256 while h-m1 used 512 — this affects the generalizability of the smoke test's gradient norms to the h-m1 training regime.

---

## MINOR Issues (Collected for Human Review — NOT Auto-fixed)

1. **Style/Clarity — §3.5 Table caption missing:** The Training Configuration table has no caption. Suggest adding: "Table 3: Training configuration for h-e1 and h-m1 experiments."
2. **Grammar — §5.4:** "mean = +0.000730" — the "+" sign before a positive mean value is non-standard; typically reported as "0.000730."
3. **Clarity — §4.4:** "binary: GPU 3; ratio: GPU 4" — not clear these are absolute GPU indices vs. relative CUDA device indices. State: "CUDA device 3 (binary) and CUDA device 4 (ratio)."
4. **Formatting — Abstract:** "reward_mean = 0" and "clipped_ratio = 1.0" in abstract should use math mode or consistent code formatting throughout.
5. **Clarity — §3.4 gate criterion:** "Ratio HumanEval pass@1 − binary ≥ 0.03 with 95% bootstrap CI excluding 0" — should specify this is for the h-m1 gate, not h-e1. Readers may confuse the two gates.
6. **Typo — §1:** "codeparrot/apps (h-e1: ≥5 test cases, n=1,789; h-m1: ≥1 test case)" appears in §3.5 but h-e1 in §4.3 says "codeparrot/apps (≥5 test cases, n=1,789)" which matches. However, §2 Related Work says "APPS dataset" without specifying the filter — add the ≥5 test case filter mention in §2 for completeness.

---

## Ground Truth Verification Log

| Claim | Paper Value | Ground Truth | Match | Notes |
|-------|-------------|--------------|-------|-------|
| Binary adv. var. (illustrative group) | 0.0000 | C1: 0.0000 | ✓ | Exact |
| Ratio adv. var. (illustrative group) | 0.0475 | C2: 0.0475 | ✓ | Exact |
| Simulation: 987/1000 groups | 987/1000 (98.7%) | C6: 987 | ✓ | Exact |
| h-e1 unit tests | 17/17 | C11: 17/17 | ✓ | Exact |
| h-m1 unit tests | 18/18 | C12: 18/18 | ✓ | Exact |
| Total unit tests | 35/35 | C13: 35/35 | ✓ | Exact |
| reward_mean at all steps | 0.0000 | C14: 0.0 | ✓ | Exact |
| clipped_ratio at all steps | 1.0000 | C15: 1.0 | ✓ | Exact |
| fraction_partial | NaN | C16: NaN | ✓ | Exact |
| Steps logged | 208 | C18: 208 | ✓ | Exact |
| APPS dataset size (h-e1) | n=1,789 | C20: 1789 | ✓ | Exact |
| Smoke test gradient norms | [3×10⁻⁴, 7×10⁻⁴] | C9: [0.0003, 0.0007] | ✓ | Exact |
| Smoke test duration | ~54 sec/step | C10: ~54s | ✓ | Approximate, labeled as such |
| **max_new_tokens (h-e1 smoke)** | **512 (Table 3.5)** | **h-e1/04_validation §1.2: 256** | **✗ MISMATCH** | FATAL-001 |
| Grad norm CI (h-m1) | mean +0.000730, CI [−0.000253, +0.002561] | C17: exact match | ✓ | Exact |
| Engineering issues | 9 | C19: 9 | ✓ | Exact |

---

## Summary for Revision Agent

### MUST FIX (FATAL):
1. **FATAL-001:** max_new_tokens discrepancy — h-e1 used 256, paper reports 512 uniformly. Add separate h-e1 row in Table 3.5 or footnote in §5.3.

### MUST FIX (MAJOR):
2. **MAJOR-ACC-001:** Move Figure 2 reference to §5.4 or add disambiguation text.
3. **MAJOR-ACC-002:** Update Table 2 grad_norm values from "~10⁻³" to actual measured values.
4. **MAJOR-ENG-001:** Qualify "Every published paper" to the four papers actually reviewed.
5. **MAJOR-SKE-001:** Rewrite §6.3 bullet about "pending CI" — CI is now available in §5.4, limitation is stale.

### COLLECT FOR HUMAN REVIEW (MINOR):
- Items 1–6 listed above in MINOR Issues section.

### Return Summary

```yaml
agent: adversary_r1
round: R1
status: COMPLETED
fatal_count: 1
major_count: 4
minor_count: 6
ground_truth_discrepancies: 1  # FATAL-001 (max_new_tokens)
key_conflicts:
  - "max_new_tokens: h-e1 used 256 in implementation, paper reports 512"
  - "§6.3 limitation about pending CI contradicts §5.4 which reports the CI"
  - "'Every published paper' scope overclaim"
recommendation: MAJOR_REVISION
persuasiveness_passed: true  # Abstract and hook are strong despite issues
```
