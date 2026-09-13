# Adversarial Review Round 2 — Numerical Verification
## Paper: Humans Accommodate to Better AI: Tier-Scalable Semantic Alignment in RLHF Conversations (R1 Revision)
## Date: 2026-03-15

---

## Files Read and Verification Log

The following files were read in full for this review:

- `paper/06_paper_r1.md` — R1 revised paper
- `paper/065_ground_truth.yaml` — ground truth values extracted from Phase 0–5 artifacts
- `h-e1/04_validation.md` — Phase 4 validation report for hypothesis h-e1
- `h-m1/04_validation.md` — Phase 4 validation report for hypothesis h-m1
- `h-m2/04_validation.md` — Phase 4 validation report for hypothesis h-m2
- `h-m3/04_validation.md` — Phase 4 validation report for hypothesis h-m3
- `h-m4/04_validation.md` — Phase 4 validation report for hypothesis h-m4
- `paper/review/065_review_r1.md` — Round 1 review (to avoid re-raising fixed issues)

Verification approach: For each numerical claim in the paper, the value was traced to the Phase 4 validation source file and checked for arithmetic consistency. Mathematical plausibility checks were computed directly. The R1 issues AC-1 (d-range fix) and BR-4/M-1 (causal language) were checked for resolution status.

---

## R1 Fix Status Check

| R1 Issue | Fix Required | Fixed in R1? |
|----------|-------------|--------------|
| AC-1: d range 0.13–0.41 → 0.061–0.41 | Abstract, §1, §6.1, §7.1, Table 6 | YES — R1 abstract, §1, §5.3, §6.1 all now say "d = 0.061–0.41" |
| M-1: Causal language → associational | Abstract final sentence, RQ2, §5.2, §6.1, §6.3, §7.3 | PARTIAL — Abstract now says "Causal identification is limited by cross-sectional design; see §6.2." RQ2 now framed as "associated with differences." Some §6.1/§7.3 language softened. Residual instances remain (not re-raised here). |
| M-2: IPW balance diagnostics | §3.4/§4.4 | PARTIAL — §3.5 now says "Post-reweighting balance diagnostics... are available in our replication repository; not reported in-paper due to space constraints." Acceptable deferral. |

---

## Ground Truth Verification Table

| Claim | Location in Paper | Paper Value | Phase 4 File Value | Ground Truth YAML | Match? | Notes |
|-------|------------------|-------------|-------------------|-------------------|--------|-------|
| C_sem = 0.329 | Abstract, §5.1, §6.1 | 0.329 | h-e1: C_sem = 0.3292 | 0.329 | MATCH (rounded) | See Check A — definition issue |
| 95% CI [0.328, 0.330] | Abstract, §5.1 | [0.328, 0.330] | h-e1: CI = [0.3280, 0.3304] | [0.328, 0.330] | MATCH (rounded) | — |
| n = 155,362 | Abstract, §3.1, §5.1 | 155,362 | h-e1: 155,362 | 155,362 | EXACT MATCH | — |
| cos_actual = 0.3534 | Table 1, §5.1 | 0.3534 | h-e1: 0.3534 | 0.3534 | EXACT MATCH | — |
| cos_KNN = 0.2688 | Table 1, §5.1 | 0.2688 | h-e1: 0.2688 | 0.2688 | EXACT MATCH | — |
| cos_random = 0.0241 | Table 1, §5.1 | 0.0241 | h-e1: 0.0241 | 0.0241 | EXACT MATCH | — |
| Cohen's d actual vs random = 1.998 | Abstract, Table 1, §5.1 | 1.998 | h-e1: 1.998 | 1.998 | EXACT MATCH | — |
| Cohen's d actual vs KNN = 0.417 | Table 1, §5.1 | 0.417 | h-e1: 0.417 | 0.417 | EXACT MATCH | — |
| T1 all-MiniLM = 0.3036 | Table 2 | 0.3036 | h-m1: 0.3036 | 0.3036 | EXACT MATCH | See Check A — may be raw cosine |
| T2 all-MiniLM = 0.3367 | Table 2 | 0.3367 | h-m1: 0.3367 | 0.3367 | EXACT MATCH | — |
| T3 all-MiniLM = 0.3678 | Table 2 | 0.3678 | h-m1: 0.3678 | 0.3678 | EXACT MATCH | — |
| T1 paraphrase = 0.2714 | Table 2 | 0.2714 | h-m1: 0.2714 | 0.2714 | EXACT MATCH | — |
| T2 paraphrase = 0.3068 | Table 2 | 0.3068 | h-m1: 0.3068 | 0.3068 | EXACT MATCH | — |
| T3 paraphrase = 0.3456 | Table 2 | 0.3456 | h-m1: 0.3456 | 0.3456 | EXACT MATCH | — |
| T1 mpnet = 0.3138 | Table 2 | 0.3138 | h-m1: 0.3138 | 0.3138 | EXACT MATCH | — |
| T2 mpnet = 0.3483 | Table 2 | 0.3483 | h-m1: 0.3483 | 0.3483 | EXACT MATCH | — |
| T3 mpnet = 0.3820 | Table 2 | 0.3820 | h-m1: 0.3820 | 0.3820 | EXACT MATCH | — |
| J-T p = 0.001, 3/3 models | Abstract, Table 2, §5.2 | 0.001, 3/3 | h-m1: p=0.0010 all 3 | 0.001, 3/3 | EXACT MATCH | — |
| Cohen's d T1→T3 all-MiniLM = 0.183 | Table 2, §5.2 | 0.183 | h-m1: 0.1826 | 0.183 | MATCH (rounded) | — |
| Cohen's d T1→T3 paraphrase = 0.254 | Table 2 | 0.254 | h-m1: 0.2545 | 0.254 | MATCH (rounded) | — |
| Cohen's d T1→T3 mpnet = 0.238 | Table 2 | 0.238 | h-m1: 0.2378 | 0.238 | MATCH (rounded) | — |
| h-m2 minilm T1: H←A=0.0853, A←H=0.0395, d=0.37 | Table 3 | 0.0853, 0.0395, 0.37 | h-m2: 0.0853, 0.0395, 0.3735 | 0.37 | MATCH | — |
| h-m2 minilm T2: H←A=0.0923, A←H=0.0535, d=0.33 | Table 3 | 0.0923, 0.0535, 0.33 | h-m2: 0.0923, 0.0535, 0.3303 | 0.33 | MATCH | — |
| h-m2 minilm T3: d=0.13 | Table 3 | 0.13 | h-m2: 0.1333 | 0.13 | MATCH (rounded) | — |
| h-m2 paraphrase T1: d=0.41 | Table 3 | 0.41 | h-m2: 0.4053 | 0.41 | MATCH (rounded) | — |
| h-m2 paraphrase T2: d=0.35 | Table 3 | 0.35 | h-m2: 0.3853 | 0.35 | MISMATCH — see NV-1 | 0.385 rounds to 0.39, not 0.35 |
| h-m2 paraphrase T3: d=0.20 | Table 3 | 0.20 | h-m2: 0.2049 | 0.20 | MATCH (rounded) | — |
| h-m2 mpnet T1: H←A=0.0838, A←H=0.0422, d=0.33 | Table 3 | 0.0838, 0.0422, 0.33 | h-m2: 0.0826, 0.0422, 0.3338 | 0.33 | MINOR — see NV-2 | H←A: 0.0826 (Phase4) vs 0.0838 (paper) |
| h-m2 mpnet T2: d=0.27 | Table 3 | 0.27 | h-m2: 0.2611 | 0.27 | MATCH (rounded) | — |
| h-m2 mpnet T3: d=0.061, p=0.004 | §5.3, Table 3 | 0.061, 0.004 | h-m2: 0.0606, 0.00412 | 0.061, 0.004 | MATCH (rounded) | — |
| h-m2 d range = 0.061–0.41 | Abstract, §1, §5.3, §6.1 | 0.061–0.41 | Phase4 min=0.0606, max=0.4053 | 0.061–0.41 | MATCH (R1 fix confirmed) | — |
| 9/9 cells pass h-m2 | Abstract, §5.3 | 9/9 | h-m2: 3 models × 3 tiers all pass | 9/9 | MATCH | — |
| h-m3 25/27 cells Δ < 0 | Abstract, §5.4 | 25/27 | h-m3: confirmed 25/27 | 25/27 | MATCH | — |
| h-m3 strongest T3-OP1 d = −0.74 | §5.4 | −0.74 | h-m3 T3 raw d = −0.716, length_matched d = −0.738 | d = −0.738 | MINOR — see NV-3 | Paper says OP1 (raw) but −0.738 is OP2 |
| h-m3 n_pairs T1=14,426 | §5.4 | 14,426 | h-m3: helpful-base n=31,013; helpful-online n=14,426 | 14,426 | MISMATCH — see NV-4 | T1 should be helpful-base=31,013 |
| h-m3 n_pairs T2=22,847 | §5.4 | 22,847 | h-m3: helpful-RS n=35,665 | 22,847 | MISMATCH — see NV-4 | Neither Phase4 tier has 22,847 |
| h-m3 n_pairs T3=35,665 | §5.4 | 35,665 | h-m3: helpful-RS n=35,665; helpful-online n=14,426 | 35,665 | MISMATCH — see NV-4 | T3 should be helpful-online=14,426 |
| β_PM all-MiniLM = −1.46e−05 | Table 5 | −1.46e−05 | h-m4: −1.46e−05 | −1.46e−05 | EXACT MATCH | — |
| β_PM paraphrase = −1.26e−06 | Table 5 | −1.26e−06 | h-m4: −1.26e−06 | −1.26e−06 | EXACT MATCH | — |
| β_PM mpnet = +6.76e−05 | Table 5 | +6.76e−05 | h-m4: +6.76e−05 | +6.76e−05 | EXACT MATCH | — |
| p = 0.9982 (all-MiniLM) | Table 5 | 0.9982 | h-m4: 0.9982 | 0.9982 | EXACT MATCH | — |
| p = 0.9998 (paraphrase) | Table 5 | 0.9998 | h-m4: 0.9998 | 0.9998 | EXACT MATCH | — |
| p = 0.9914 (mpnet) | Table 5 | 0.9914 | h-m4: 0.9914 | 0.9914 | EXACT MATCH | — |
| R² ≈ 0.008 all-MiniLM | Table 5 | 0.008 | h-m4: 0.0071 | 0.008 | MINOR — see NV-5 | 0.0071 rounds to 0.007, paper says 0.008 |
| R² ≈ 0.007 paraphrase | Table 5 | 0.007 | h-m4: 0.0122 | 0.007 | MISMATCH — see NV-5 | Phase4=0.0122 but YAML/paper=0.007 |
| R² ≈ 0.012 mpnet | Table 5 | 0.012 | h-m4: 0.0101 | 0.012 | MINOR — see NV-5 | 0.0101 rounds to 0.010, paper says 0.012 |
| n ≈ 3,000 per model regression | §5.5 | ~3,000 | h-m4: n=3,000 | ~3,000 | EXACT MATCH | — |

---

## Mathematical Validity Analysis

### Check A: C_sem Definition Consistency

**The central question:** Is C_sem = 0.329 mathematically consistent with the stated formula C_sem = E[cos(actual)] - E[cos(KNN)]?

**Finding: C_sem = 0.329 is NOT cos(actual) - cos(KNN). It is cos(actual) - cos(random).**

Arithmetic:
- cos(actual) - cos(KNN) = 0.3534 - 0.2688 = **0.0846** ≠ 0.329
- cos(actual) - cos(random) = 0.3534 - 0.0241 = **0.3293** ≈ 0.3292 (Phase 4 C_sem) ✓

The Phase 4 h-e1 validation file reports `C_sem = 0.3292` alongside `cos_actual_mean = 0.3534`, `cos_topic_mean = 0.2688`, and `cos_random_mean = 0.0241`. The arithmetic demonstrates that the value labeled "C_sem" in the Phase 4 experiment is computed as (cos_actual - cos_random), not (cos_actual - cos_KNN) as stated in the paper's §3.2 formula.

**Additional evidence confirming the inconsistency:**

The h-m2 validation file reports per-tier, per-direction "C_sem" values (e.g., C_sem^H←A(T1, MiniLM) = 0.0853, C_sem^A←H(T1, MiniLM) = 0.0395). These values (range ~0.04–0.09) are clearly (cos_actual - cos_KNN)-scale, consistent with 0.0846 at the aggregate level. Yet the h-m1 validation reports tier values of 0.3036–0.3678 for the "C_sem" column — values that match the scale of raw cosine similarities to actual partners, not baseline-subtracted differences.

**Three distinct interpretations of "C_sem" appear to co-exist in the pipeline artifacts:**

1. **h-e1 C_sem = 0.3292**: Appears to be cos_actual - cos_random (confirmed by arithmetic above).
2. **h-m1 tier C_sem values (0.3036–0.3678)**: Appear to be raw cosine to actual partner (same scale as cos_actual = 0.3534).
3. **h-m2 per-cell C_sem values (0.0395–0.0923)**: Appear to be cos_actual - cos_KNN (consistent with 0.0846 aggregate).

**Impact on the paper:**

The paper's §3.2 formula defines C_sem as (actual - KNN baseline). However, the paper then says "Baseline-adjusted C_sem = 0.329" in §5.1, and reports tier values of 0.3036–0.3678 in Table 2 as "C_sem." If C_sem = actual - KNN, the correct values would be approximately 0.0846 (aggregate) and 0.08–0.09 (per tier, from h-m2). The paper's Table 2 values (0.3036–0.3678) cannot be (actual - KNN) since those differences would be much smaller.

**Weighted average check:** Using h-m1 tier pair counts (T1=63,830, T2=65,359, T3=26,173) and "C_sem" values (0.3036, 0.3367, 0.3678): weighted average = 0.3283, close to the reported overall 0.3292. This confirms that the h-m1 tier values are internally consistent with h-e1's C_sem = 0.3292 **if all are interpreted as raw cosine to actual partner (not KNN-subtracted)**. The KNN-subtracted values would give a weighted average near 0.0846, not 0.3292.

**Conclusion for Check A:** There is a systematic naming inconsistency. The metric reported as "C_sem" throughout the paper is computed as (cos_actual - cos_random) in h-e1 and as raw cos_actual per tier in h-m1. The stated formula in §3.2 (actual - KNN) does not match the computed values. The paper is internally consistent in its reported numbers, but the formula description in §3.2 and the interpretation in §5.1 ("baseline-adjusted by KNN") are arithmetically incompatible with the actual values. This constitutes a **definitional inconsistency** — a MAJOR issue.

**Note:** The direction of the main results (monotonicity, partner-specificity ordering) is not affected by this definitional issue. The existence finding (accommodation > 0) holds regardless. But the claim that "C_sem subtracts the KNN baseline" when the reported values are (actual - random) scale is a substantive misrepresentation of the metric.

---

### Check B: Cohen's d = 1.998 Plausibility (actual vs random)

- Difference: 0.3534 - 0.0241 = 0.3293
- d = 1.998 implies pooled SD = 0.3293 / 1.998 = **0.1648**
- Typical SBERT cosine similarity distributions have SD ≈ 0.10–0.20 in dialogue corpora. SD = 0.165 is fully plausible.
- **Result: PASS — d = 1.998 is mathematically plausible.**

---

### Check C: Cohen's d = 0.417 (actual vs KNN) Cross-Check

- Difference: 0.3534 - 0.2688 = 0.0846
- d = 0.417 implies pooled SD = 0.0846 / 0.417 = **0.2029**
- Check B gives implied SD ≈ 0.165; Check C gives implied SD ≈ 0.203.
- The discrepancy (~0.04) is expected: the random shuffle distribution has lower variance (uniformly low cosines) than the KNN distribution (already similar to actual, with compressed range). Different pooled SDs are mathematically legitimate.
- **Result: PASS — no mathematical impossibility. Minor SD divergence is physically justified.**

---

### Check D: h-m3 N_pairs Discrepancy

**Finding: The paper reports h-m3 n_pairs in ascending order (T1=14,426; T2=22,847; T3=35,665), but Phase 4 validation shows the opposite ordering.**

Phase 4 h-m3 validation explicitly states:
- helpful-base (T1): n=31,013
- helpful-rejection-sampled (T2): n=35,665
- helpful-online (T3): n=14,426

The paper reports T1=14,426 and T3=35,665. The value the paper assigns to T1 (14,426) exactly matches Phase 4's helpful-online count (T3). The value the paper assigns to T3 (35,665) matches Phase 4's helpful-rejection-sampled count (T2). The paper's T2 value (22,847) does not match any Phase 4 tier count.

**Root cause:** The n_pairs ordering in the paper appears to have been transcribed in ascending order (perhaps to suggest "increasing data across tiers"), but the actual dataset has more chosen/rejected pairs in helpful-base than in helpful-online. The h-m3 n_pairs are a subset of total pairs (restricted to conversations with both chosen and rejected responses available), so they differ from h-e1's total pair counts (63,830; 65,359; 26,173 per tier), but the tier ordering (base > online) should be preserved.

**Impact:** The n_pairs values cited in §5.4 are wrong for T1 and T3. This is a factual error, though it does not affect the h-m3 conclusions (which depend on effect sizes and directions, not n_pairs).

**Result: FAIL — n_pairs in §5.4 are incorrect. See NV-4.**

---

## Baseline Fairness Assessment

### Internal Controls (Random and KNN baselines)

The paper has no external model comparisons (it is a measurement study). Internal controls:

1. **Random baseline**: Randomly sampled AI turns from the same tier. Correctly described. The cosine 0.0241 is plausible as a near-zero value for random SBERT pairs across dialogue corpora.

2. **KNN baseline (K=5)**: Top-5 cosine-similar AI turns from the same tier, excluding the actual partner. The exclusion of self is stated explicitly ("excluding the actual partner" in §3.2 and §4.3). K=5 is stated and motivated (topical diversity balance). **FAIR.**

3. **Chosen/rejected pairs for h-m3**: Within-prompt pairs, same conversation context. The design is correctly motivated: testing whether H_next is more similar to A_chosen than A_rejected within the same prompt. **FAIR.**

4. **Fairness concern (minor):** The KNN baseline uses K=5 neighbors drawn from the *same tier* as the actual pair. This means the KNN baseline varies by tier (T3 conversations have a different neighbor pool than T1). This is the correct design (tier-matched KNN ensures the baseline is calibrated to each tier's semantic space), but it could cause the tier monotonicity of "C_sem" (as defined in h-m1) to be partially explained by tier differences in the KNN baseline similarity rather than tier differences in actual partner similarity. The paper does not explicitly discuss this confound.

Overall: **Baseline design is sound and fairly described.** No material fairness violations identified.

---

## Issues Found

### FATAL Issues

None. The main existence, monotonicity, directionality, and mechanism results are internally consistent and directionally robust despite the definitional issues below.

---

### MAJOR Issues

**NV-M1: C_sem definition inconsistency between formula and reported values**

- **Description:** The paper's §3.2 formula defines C_sem = E[cos(actual)] - E[cos(KNN_topic_matched)]. However, the Phase 4 h-e1 experiment reports C_sem = 0.3292 for the same run, while cos_actual = 0.3534 and cos_KNN = 0.2688. The formula result would be 0.3534 - 0.2688 = 0.0846. The value 0.3292 = 0.3534 - 0.0241 = cos_actual - cos_random, not cos_actual - cos_KNN. The h-m1 tier "C_sem" values (0.3036–0.3678) are similarly on the scale of raw cosine to actual partner, not KNN-subtracted differences. The h-m2 per-cell values (0.0395–0.0923) are on the correct KNN-subtracted scale (~0.08–0.09). The paper uses "C_sem" to refer to at least two different quantities (raw cos_actual in h-m1, and cos_actual - cos_random in h-e1), while the formula states it should be cos_actual - cos_KNN.

- **Locations:** §3.2 (formula), §5.1 (C_sem = 0.329 reported as baseline-adjusted), Table 2 (tier C_sem values labeled as C_sem), Table 1 (implied by juxtaposition of 0.329 with 0.2688 KNN row)

- **Impact:** This is the most technically serious issue in the paper. A reviewer performing the same arithmetic check as this review will immediately notice 0.3534 - 0.2688 = 0.0846 ≠ 0.329. The paper will be rejected or require major revision if this is not clarified. The paper is internally consistent in its numbers (the weighted average of h-m1 tier values matches the h-e1 overall value), but the formula description does not match the computed values.

- **Fix options:**
  1. If C_sem is intended to be cos_actual - cos_random: revise the §3.2 formula to match. Clarify that "matched-shuffle" refers to random shuffle (not KNN) for the primary C_sem computation, and that KNN comparison is provided separately as a stricter control. Revise §5.1 "Baseline-adjusted C_sem = 0.329" to "Accommodation above random baseline C_sem = 0.329." Report d = 0.417 above KNN as an additional specificity check.
  2. If C_sem is intended to be cos_actual - cos_KNN: revise all Table 2 values, the h-e1 aggregate C_sem = 0.329, and the CI to reflect ~0.08 values. This would substantially change all reported C_sem numbers.
  3. If h-m1 tier values are raw cosine to actual partner (not C_sem): relabel Table 2 column as "Mean cosine to actual partner" and add a C_sem column with the KNN-subtracted values (consistent with h-m2's 0.08-scale values). This requires new calculations for the tier C_sem values.

---

**NV-M2: h-m3 n_pairs incorrectly assigned to tiers**

- **Description:** The paper §5.4 reports h-m3 sample sizes as T1=14,426; T2=22,847; T3=35,665. Phase 4 h-m3 validation shows helpful-base (T1)=31,013 pairs, helpful-RS (T2)=35,665 pairs, and helpful-online (T3)=14,426 pairs. The paper has assigned T1 the value that belongs to T3 (14,426 = online tier), and T3 the value that belongs to T2 (35,665 = RS tier). T2's value (22,847) does not match any Phase 4 tier count. The paper's numbers imply T3 has the most chosen/rejected pairs, when the actual data (and overall dataset structure: helpful-online has ~22,007 conversations, fewer than helpful-base's ~43,835) implies T3 should have the fewest.

- **Location:** §5.4, and ground truth YAML (which propagated the error)

- **Impact:** Factual error in reported sample sizes. Does not affect conclusions (h-m3 FAILS regardless of which tier has how many pairs), but a reviewer examining the numbers will notice T3 (online PPO, typically the smallest tier) cannot plausibly have more chosen/rejected pairs than T1 (base SFT, typically the largest tier). Requires correction.

- **Fix:** Replace §5.4 n_pairs with correct values: T1 (helpful-base) ≈ 31,013; T2 (helpful-RS) ≈ 35,665; T3 (helpful-online) ≈ 14,426. Note that T3 has the fewest pairs, consistent with the dataset structure.

---

### MINOR Issues

**NV-1: paraphrase-MiniLM T2 Cohen's d value in Table 3**

- **Description:** Table 3 reports paraphrase-MiniLM T2 Cohen's d = 0.35. Phase 4 h-m2 validation shows the actual value is 0.3853. The value 0.3853 rounds to 0.39, not 0.35. The discrepancy (0.035) is larger than rounding and appears to be a transcription error from the ground truth YAML (which also says 0.35, suggesting the error originated in YAML construction, not the paper itself).

- **Location:** Table 3, paraphrase-MiniLM row, T2 column; ground truth YAML (directional_asymmetry.paraphrase_minilm_T2.cohen_d)

- **Impact:** Minor numerical inaccuracy. The conclusion (H←A > A←H) is unaffected since the effect is significant regardless. But 0.39 vs 0.35 is a reportable numerical discrepancy.

- **Fix:** Update Table 3 paraphrase T2 d from 0.35 to 0.39 (rounding 0.3853). Update ground truth YAML accordingly.

---

**NV-2: mpnet T1 H←A value in Table 3 (minor)**

- **Description:** Table 3 and ground truth YAML report mpnet T1 C_sem^H←A = 0.0838. Phase 4 h-m2 validation reports 0.0826. The difference (0.0012) is small but represents a minor transcription discrepancy.

- **Location:** Table 3, all-mpnet-base-v2 row, T1 H←A value

- **Impact:** Negligible on conclusions. Worth noting for reproducibility.

---

**NV-3: h-m3 strongest falsification operationalization label**

- **Description:** The ground truth YAML and paper §5.4 state "strongest falsification: T3-OP1, d = −0.738." Phase 4 h-m3 validation shows: T3 (helpful-online) raw (OP1) d = −0.716, and T3 length_matched (OP2) d = −0.738. The value −0.738 corresponds to OP2 (length_matched), not OP1 (raw). The strongest OP1 cell is actually −0.716.

- **Location:** §5.4 discussion, ground truth YAML (within_prompt_delta.strongest_falsification)

- **Impact:** Minor operationalization mislabeling. The strongest effect across all 27 cells is d = −0.738 (this is correct), but it is OP2, not OP1.

- **Fix:** Update to "strongest falsification: T3-OP2 (length-matched), d = −0.738."

---

**NV-4 (already described as NV-M2 above — see MAJOR issues)**

---

**NV-5: h-m4 R² values — minor rounding and one transcription error**

- **Description:** Three issues:
  1. all-MiniLM R² = 0.0071 (Phase 4). Paper/YAML reports 0.008. The value 0.0071 rounds to 0.007, not 0.008. This is a marginal rounding discrepancy.
  2. paraphrase R² = 0.0122 (Phase 4). Paper/YAML reports 0.007. This is a material transcription error (0.012 ≠ 0.007). The ground truth YAML appears to have the paraphrase and mpnet R² values transposed or one was incorrectly transcribed.
  3. mpnet R² = 0.0101 (Phase 4). Paper/YAML reports 0.012. The value 0.0101 rounds to 0.010, not 0.012.

- **Location:** Table 5, R² column; ground truth YAML (mediation_regression values)

- **Impact:** The null conclusion (β_PM ≈ 0, p ≈ 0.99) is entirely unaffected by R² discrepancies. All R² values are so low (all below 0.013) that the conclusion holds with certainty regardless of which specific value is correct. However, Table 5 contains numerically inaccurate values that a reviewer may catch.

- **Fix:** Update Table 5 R² to: all-MiniLM=0.007, paraphrase=0.012, mpnet=0.010 (direct Phase 4 values, rounded to 3 decimal places). The conclusion footnote "R² ≤ 0.012" remains valid.

---

## Summary for Revision Agent

```
fatal_count: 0
major_count: 2
minor_count: 4
numerical_discrepancies_found: 8
mathematical_impossibilities: 0
baseline_fairness_issues: 0

key_findings:

  NV-M1 [MAJOR]: C_sem definitional inconsistency.
    The formula in §3.2 states C_sem = cos(actual) - cos(KNN_topic_matched).
    But Phase 4 arithmetic confirms: the value reported as C_sem = 0.329 equals
    cos_actual(0.3534) - cos_random(0.0241) = 0.3293, NOT cos_actual - cos_KNN = 0.0846.
    h-m1 tier values (0.3036-0.3678) are raw cosine to actual partner.
    h-m2 per-cell values (0.08-0.09 scale) are the true (actual - KNN) quantities.
    The paper uses C_sem as a label for multiple different computations.
    Requires either: (a) formula correction to match reported values,
    or (b) a thorough relabeling of Tables 1 and 2 to separate raw cosines from
    KNN-adjusted C_sem values.

  NV-M2 [MAJOR]: h-m3 n_pairs incorrectly assigned.
    Paper §5.4 T1=14,426; T2=22,847; T3=35,665.
    Phase 4: T1(helpful-base)=31,013; T2(helpful-RS)=35,665; T3(helpful-online)=14,426.
    The paper has assigned T3's count to T1 and T2's count to T3.
    Correct: T1≈31,013, T2≈35,665, T3≈14,426.

  NV-1 [MINOR]: paraphrase T2 d=0.35 in Table 3 should be d=0.39 (Phase4: 0.3853).
  NV-2 [MINOR]: mpnet T1 H←A=0.0838 in Table 3; Phase 4 shows 0.0826 (difference 0.0012).
  NV-3 [MINOR]: strongest h-m3 falsification labeled OP1 but it is OP2 (d=-0.738 = length_matched).
  NV-5 [MINOR]: h-m4 R² values have transcription errors (paraphrase: paper=0.007 vs Phase4=0.012;
    all-MiniLM: paper=0.008 vs Phase4=0.007; mpnet: paper=0.012 vs Phase4=0.010).
    Null conclusion unaffected. Correct to: all-MiniLM=0.007, paraphrase=0.012, mpnet=0.010.

already_fixed_from_r1:
  - AC-1 (d range 0.13-0.41 → 0.061-0.41): CONFIRMED FIXED throughout paper
  - M-1 (causal language): SUBSTANTIALLY FIXED; abstract now hedged, RQ2 softened
  - M-2 (IPW diagnostics): DEFERRED to replication repository — acceptable

recommendation: REVISE_BEFORE_FINALIZATION
  NV-M1 (C_sem definition) must be resolved — it is the most technically dangerous
  issue and will be caught by any reviewer who checks §3.2 formula against Table 1 values.
  NV-M2 (h-m3 n_pairs) must be corrected — easily fixable factual error.
  Minor issues NV-1 through NV-5 should be corrected but do not block.
```
