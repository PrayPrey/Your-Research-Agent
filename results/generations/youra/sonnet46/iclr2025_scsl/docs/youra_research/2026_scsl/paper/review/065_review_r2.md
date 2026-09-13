# Phase 6.5 Adversarial Review — Round 2
**Paper:** Gradient Norms as Label-Free Minority Proxies: A Mechanistic Study of the Prediction-Residual Signal for Spurious Correlation Robustness (R1 revision)
**Round:** R2 — Verification and Credibility
**Date:** 2026-03-16
**Personas:** Accuracy Checker, Skeptical Expert

---

## Serena MCP Verification Log

All Serena tool calls performed in this round:

| Call # | Tool | Arguments | Result |
|--------|------|-----------|--------|
| 1 | `mcp__serena__activate_project` | project=TEST_scsl | Activated successfully |
| 2 | `mcp__serena__find_file` | file_mask=04_validation.md, relative_path=docs/youra_research/20260315_scsl | Found 5 files; primary: h-e1/04_validation.md |
| 3 | `mcp__serena__list_dir` | docs/youra_research/20260315_scsl, recursive=false | Confirmed h-e1 directory and experiment_results.json present |
| 4 | `mcp__serena__list_dir` | docs/youra_research/20260315_scsl/h-e1, recursive=false | Found experiment_results.json, 04_validation.md, 04_checkpoint.yaml |
| 5 | `mcp__serena__search_for_pattern` | pattern=AUC\|ratio\|balance_deviation\|h_norm in h-e1/04_validation.md | Confirmed: ratio=8.805, AUC=0.914, balance_deviation=0.379, h_norm_std_ratio≈0.10; full epoch table confirmed |
| 6 | `mcp__serena__search_for_pattern` | pattern=8.805\|0.914\|0.379\|8.509\|... in h-e1/04_validation.md | All epoch values confirmed: epoch 1 (6.513, 0.952, 0.400), epoch 3 (7.493, 0.912, 0.404), epoch 5 (8.805, 0.914, 0.379), epoch 10 (8.509, 0.888, 0.374) |
| 7 | `mcp__serena__search_for_pattern` | pattern=G0\|G1\|G2\|G3\|g_tilde\|0.022\|... in h-e1/04_validation.md | Per-group values confirmed: G0=0.02209, G1=0.31256, G2=0.43279, G3=0.09360 |
| 8 | Read `experiment_results.json` | Full per-epoch, per-group data with full precision | Raw ground truth confirmed |
| 9 | `mcp__serena__search_for_pattern` | pattern=NHT\|Khanh\|UNVERIFIED\|92.9\|DFR.*WGA\|competitive WGA in 06_paper_r1.md | NHT: ABSENT. UNVERIFIED: ABSENT. DFR 92.9%: ABSENT. R1 FATAL fixes confirmed applied. |
| 10 | `mcp__serena__search_for_pattern` | pattern=JTT\|estimated AUC.*JTT in 06_paper_r1.md | JTT +21pp still present; "estimated AUC ≈ 0.70–0.80" language REMOVED in R1 |
| 11 | `mcp__serena__search_for_pattern` | pattern=GNR-LLR\|two-stage\|Stage 2\|Stage 1 in 06_paper_r1.md | GNR-LLR retained in Section 3.4 and YAML metadata; Stage 2 clearly labeled "future work — not evaluated in this paper" |

---

## Ground Truth Verification Table (R2)

All values verified against `experiment_results.json` (primary ground truth) and `h-e1/04_validation.md`.

| Claim in R1 Paper | Location | Ground Truth (JSON) | Match? | Status |
|-------------------|----------|---------------------|--------|--------|
| AUC = 0.914 at T_id=5 | Abstract, Table main results | 0.9139910354921332 | MATCH (rounds to 0.914) | OK |
| ratio = 8.805 at T_id=5 | Table main results | 8.805025018040832 | MATCH (rounds to 8.805) | OK |
| ratio = 8.8x (abstract) | Abstract | 8.805 | MATCH | OK |
| ratio ≈ 8.5x at epoch 10 | Section 5.3, Table 2 | 8.509033721031399 | MATCH | OK |
| AUC = 0.952 at epoch 1 | Table 2 | 0.952338090010977 | MATCH | OK |
| AUC = 0.912 at epoch 3 | Table 2 | 0.9116126966703257 | MATCH (rounds to 0.912) | OK |
| AUC = 0.888 at epoch 10 | Table 2 | 0.8880918404683499 | MATCH | OK |
| ratio = 6.513 at epoch 1 | Table 2 | 6.512530686124351 | MATCH (rounds to 6.513) | OK |
| ratio = 7.493 at epoch 3 | Table 2 | 7.492674093257632 | MATCH | OK |
| h_norm_std_ratio ≈ 0.10 | Abstract, Table 3 | 0.10511806968501876 (epoch 5) | MATCH (≈0.10) | OK |
| G0 g̃ mean = 0.022 | Table 1 | 0.02208908647298813 | MATCH | OK |
| G1 g̃ mean = 0.313 | Table 1 | 0.31256386637687683 | MATCH | OK |
| G2 g̃ mean = 0.433 | Table 1 | 0.43279364705085754 | MATCH | OK |
| G3 g̃ mean = 0.094 | Table 1 | 0.09360451251268387 | MATCH | OK |
| G0 g_raw mean = 0.553 | Table 1 | 0.5531572699546814 | MATCH | OK |
| G1 g_raw mean = 8.100 | Table 1 | 8.099581718444824 | MATCH | OK |
| G2 g_raw mean = 10.487 | Table 1 | 10.487095832824707 | MATCH | OK |
| G3 g_raw mean = 2.350 | Table 1 | 2.349942922592163 | MATCH | OK |
| balance_deviation = 0.379 | Table main results | 0.37935034802784223 | MATCH | OK |
| features_count = 4795 | Table 3 | 4795 (all epochs) | MATCH | OK |
| NHT removed | Body | ABSENT from R1 | CONFIRMED FIXED | OK |
| DFR 92.9% removed | Body | ABSENT from R1 | CONFIRMED FIXED | OK |
| [UNVERIFIED] tags removed | Body | ABSENT from R1 | CONFIRMED FIXED | OK |
| JTT +21pp WGA | Section 2.2 | External claim — Liu et al. 2021 ICML published paper | UNVERIFIED (external) | ACCEPTABLE |
| "estimated AUC ≈ 0.70–0.80" of JTT | Section 5.1 Key Obs. 1 | REMOVED from R1 | CONFIRMED FIXED | OK |
| Stage 2 / GNR-LLR framing | Section 3.4, YAML | Present but clearly labeled "future work — not evaluated" | PARTIAL FIX | SEE BELOW |
| Estimated minority recall ≥90% | Section 5.2 | Not directly measured; estimated from per-group means | UNVERIFIED (estimate) | MAJOR |

---

## Mathematical Validity Assessment

### 1. Ratio = 8.805: Internal Consistency Check

**Claim:** ratio = mean_g̃(minority) / mean_g̃(majority) = 8.805 at T_id=5

**Independent computation from Table 1 values:**

- Minority = G1 ∪ G2: n_G1 = 184, n_G2 = 56, total = 240
- Majority = G0 ∪ G3: n_G0 = 3498, n_G3 = 1057, total = 4555
- Combined minority mean = (184 × 0.31256 + 56 × 0.43279) / 240
  = (57.5110 + 24.2362) / 240
  = 81.7472 / 240
  = **0.34061**
- Combined majority mean = (3498 × 0.02209 + 1057 × 0.09360) / 4555
  = (77.267 + 98.923) / 4555
  = 176.190 / 4555
  = **0.038681**
- Ratio = 0.34061 / 0.038681 = **8.806**

**Result:** Computed ratio ≈ 8.806, reported value = 8.805 (difference < 0.001 due to rounding of Table 1 values). Using full-precision JSON values would yield exactly 8.805025. **VERIFIED — internally consistent.**

### 2. AUC=0.914 vs. Per-Group Mean Consistency

**Claim:** AUC = 0.914 at T_id=5

**Analysis:**
- G0 (majority, n=3498): g̃ mean = 0.022
- G1 (minority, n=184): g̃ mean = 0.313
- G2 (minority, n=56): g̃ mean = 0.433
- G3 (majority, n=1057): g̃ mean = 0.094

The means show clean two-cluster separation: minority group means (0.313, 0.433) are well above majority group means (0.022, 0.094), with a natural boundary near g̃ ≈ 0.2. However, G3 majority mean (0.094) is meaningfully higher than G0 majority mean (0.022), and both G1 and G2 are continuous distributions — some overlap between the G3 upper tail and G1 lower tail is expected.

**Is AUC=0.914 consistent with these means?**

AUC < 1.0 is consistent with: (a) distributional overlap between G3's upper tail and G1's lower tail, and (b) the epoch-10 data confirms this — at epoch 10, G1 mean drops to 0.140 and G3 mean to 0.044, and the AUC falls to 0.888, indicating the G1/G3 boundary becomes less clean over time. At epoch 1 (before majority full saturation), AUC=0.952 with larger absolute separation. AUC=0.914 at epoch 5 is **internally consistent** with the per-group mean structure.

**Decision boundary g̃≈0.2:** The paper claims this separates all minority means from all majority means. Verified: G0=0.022 < 0.2, G3=0.094 < 0.2, G1=0.313 > 0.2, G2=0.433 > 0.2. **Correct for group means.** However, this boundary applies to *means*, not all samples. Individual samples from G3 (upper tail) and G1 (lower tail) will cross this boundary, producing imperfect AUC < 1.0. AUC=0.914 is fully credible given this structure.

**VERDICT: AUC=0.914 is internally consistent with per-group data.**

### 3. Estimated Minority Recall ≥90%: Defensibility Assessment

**Claim (Section 5.2):** "estimated minority recall in the top-25% subset is ≥90%"

**Analysis:**
- Top-25% = top 1,199 of 4,795 samples by g̃
- Total minority samples: 184 + 56 = 240
- The paper argues all minority samples have g̃ substantially exceeding the top-25% threshold

**Is this defensible?**

The threshold for inclusion in top-25% is the 75th percentile of the g̃ distribution across all 4,795 samples. With majority distribution heavily concentrated near zero (G0 mean=0.022, G3 mean=0.094, total 4,555 majority samples), the 75th percentile of the full dataset would be determined primarily by the majority distribution. The 75th percentile of 4,795 samples is the 3,597th-highest value. Given G0 (3,498 samples, mean=0.022) already constitutes 72.9% of data, the top-25% threshold is approximately in the upper range of the G3 distribution (mean=0.094).

The critical question is: what fraction of G1 and G2 samples have g̃ above this threshold? With G1 mean=0.313 and G2 mean=0.433, both substantially above the estimated threshold (which is in the G3 range, ~0.094–0.2), a high minority recall is plausible. AUC=0.914 confirms strong discriminability, which supports high recall at reasonable thresholds.

**However, the paper cannot claim ≥90% without computing it directly.** The estimate relies on the assumption that the G1 and G2 distributions are tightly concentrated above the threshold. This may or may not hold — G1 in particular, with mean=0.313 and unknown variance, could have a lower tail below the threshold. At epoch 10, G1 mean drops to 0.140 — below the implied threshold — confirming the distribution is not entirely above 0.2.

**VERDICT: The ≥90% estimate is plausible but not verified. The paper correctly labels this as "estimated" and acknowledges it as Limitation 3. The claim is defensible as an estimate but would not survive direct scrutiny without the actual computation. This remains a MAJOR gap in the paper's central application claim.**

### 4. Outer-Product Decomposition Mathematical Validity

**Claim:** ‖∇_W ℓᵢ‖_F = ‖pᵢ − yᵢ_onehot‖ · ‖h(xᵢ)‖

**Mathematical verification:**
For W ∈ ℝ^(C×d) and the outer product ∇_W ℓᵢ = (pᵢ − yᵢ_onehot) ⊗ h(xᵢ) ∈ ℝ^(C×d):

‖A ⊗ b‖_F = ‖a‖₂ · ‖b‖₂ for vectors a ∈ ℝ^C and b ∈ ℝ^d

This is a standard property: ‖uv^T‖_F = ‖u‖₂ · ‖v‖₂.

Therefore: ‖∇_W ℓᵢ‖_F = ‖pᵢ − yᵢ‖₂ · ‖h(xᵢ)‖₂ is **mathematically correct.**

The normalization g̃ᵢ = ‖∇_W ℓᵢ‖_F / ‖h(xᵢ)‖ = ‖pᵢ − yᵢ‖₂ is also **correct.**

**VERDICT: Outer-product decomposition is mathematically valid.**

### 5. h_norm_std_ratio Interpretation

**Claim:** h_norm_std_ratio ≈ 0.10 across groups validates BatchNorm feature equalization.

**From JSON data:**
- Epoch 5: h_norm_mean values — G0=25.248, G1=25.681, G2=25.562, G3=26.412
- These are remarkably uniform: range = 26.412 − 25.248 = 1.164 over a mean of ~25.7
- Coefficient of variation across group means ≈ 1.164/25.7 ≈ 0.045 (4.5%)
- The h_norm_std_ratio=0.10 refers to within-group std/mean, confirmed from validation file

**VERDICT: Feature norm equalization claim is fully supported by data. The claim that g̃ reflects prediction-error residuals rather than feature-scale artifacts is mathematically valid and empirically confirmed.**

---

## R1 Fix Verification

| R1 Fix Required | Fix Applied? | Evidence |
|-----------------|--------------|----------|
| FATAL-1: Remove NHT citations from body | YES — CONFIRMED | Serena search for "NHT\|Khanh" returned no results in paper body |
| FATAL-1: Remove [UNVERIFIED] tags from references | YES — CONFIRMED | No [UNVERIFIED] tags found in R1 paper |
| FATAL-1: Rescope title away from GNR-LLR | PARTIAL | Title changed: "A Mechanistic Study of the Prediction-Residual Signal" — no longer implies complete method. But GNR-LLR still named in Section 3.4 and YAML hypothesis_id |
| FATAL-1: Rewrite abstract to remove WGA implication | YES — CONFIRMED | Abstract ends: "Stage 2 WGA evaluation... constitutes future work." No WGA claim made. |
| FATAL-2: Remove NHT theoretical grounding, replace with self-contained analysis | YES — CONFIRMED | Section 2.3 now uses outer-product decomposition + ERM dynamics without NHT |
| MAJOR-1: Remove "estimated AUC ≈ 0.70–0.80 of JTT" | YES — CONFIRMED | Section 5.1 Key Obs. 1 no longer includes the JTT AUC estimate; retains only the theoretical argument about binary vs. continuous signals |
| MAJOR-2: Remove DFR 92.9% WGA comparison | YES — CONFIRMED | "92.9%" does not appear anywhere in R1 paper |
| MAJOR-2: Remove "motivates the expectation of competitive WGA" | YES — CONFIRMED | Not present in R1 |
| MAJOR-3: Verify/remove unverified citations | PARTIAL | [UNVERIFIED] tags removed; citations retained but verification status of Nam, GEORGE remains undocumented |
| MAJOR-4: Add direct minority recall measurement | NOT DONE | Still reported as "estimated ≥90%" with direct computation deferred to h-e1-v2 |
| MAJOR-5: Add EL2N and data-centric related work | YES — CONFIRMED | Section 2.4 "Data-Centric Training Signals" added; EL2N discussed, distinguished from g̃ |
| MAJOR-6: Add single-seed limitation | YES — CONFIRMED | Limitation 5 explicitly states seed=42 only; multi-seed pending h-m4 |

**Summary:** 8 of 12 required fixes confirmed applied. 2 partial fixes. 2 not done (minority recall direct measurement; GEORGE/Nam verification documentation).

---

## FATAL Issues (New in R2)

**None identified.**

The two R1 FATAL issues (NHT unverified citation; systematic GNR-LLR framing mismatch) have been adequately addressed. No new FATAL issues were found.

---

## MAJOR Issues (New in R2)

### MAJOR-R2-1: Minority Recall ≥90% Remains Uncomputed (Carried From R1 MAJOR-4)

**Status:** Not resolved in R1. Still present in R2.

**Location:** Section 5.2, Limitation 3

**Issue:** The paper's central application claim — that the top-25% subset is strongly minority-enriched — depends on minority recall. The paper claims "estimated minority recall ≥90%" but acknowledges this is not directly computed. The epoch-10 data reveals G1 mean drops to 0.140, suggesting a non-trivial fraction of G1 samples may fall below any fixed threshold. Without the actual computation, the ≥90% estimate is unverified.

**Concreteness of the gap:** This is a single computation on already-saved data (sort epoch-5 g̃ values, find 75th percentile, count G1∪G2 samples above it, divide by 240). The paper has explicitly deferred this to h-e1-v2, labeling it Limitation 3 — which is honest — but a reviewer would reasonably demand it before acceptance.

**Severity:** MAJOR (unchanged from R1). The paper's subset enrichment claim is central to motivating the Stage 2 future work.

---

### MAJOR-R2-2: GNR-LLR Name Retained in Methodology — Residual Framing Risk

**Status:** New in R2 (partial fix of R1 FATAL-1 leaves a residual issue).

**Location:** Section 3.4 heading "Proposed Pipeline: Last-Layer Retraining (Future Work)"; Section 3.4 body: "The full two-stage pipeline — hereafter referred to as GNR-LLR (Gradient-Norm-Informed Last-Layer Retraining) — proceeds as follows:"; YAML header: `hypothesis_id: "H-GNR-LLR-v1"`; Conclusion Section 7 reference to "GNR-LLR pipeline"

**Issue:** The title has been appropriately de-scoped to a "mechanistic study" formulation that does not imply Stage 2 execution. However, GNR-LLR is still formally *named and defined* in the methodology section (Section 3.4), and Stage 2 hyperparameters are still fully specified (SGD, lr=0.01, 100 epochs). A reviewer who reaches Section 3.4 will encounter a fully specified two-stage method with unexecuted Stage 2, which can still create the impression of an incomplete paper rather than a deliberate scope-limited contribution.

**Distinction from R1 FATAL-1:** The R1 fix substantially reduced this risk by (a) re-scoping the title, (b) removing all WGA implication from the abstract, and (c) clearly labeling Stage 2 as "future work — not evaluated in this paper." The residual issue is framing, not a factual error. The paper is now defensible as a "Stage 1 mechanistic study with Stage 2 as future work." However, whether a venue accepts this framing will depend on program committee norms.

**Severity:** MAJOR (reviewer-facing risk, not a factual error). A shorter paper without Section 3.4's full Stage 2 specification would be cleaner and less ambiguous.

---

### MAJOR-R2-3: JTT +21pp WGA Cited as Published Result — Not Independently Verified

**Status:** Present in R1 (carried from R1 MAJOR-3). Not addressed.

**Location:** Section 2.2

**Issue:** "achieving +21pp WGA on Waterbirds" is attributed to Liu et al. [2021], a published ICML 2021 paper. The R1 ground truth flags this as UNVERIFIED. This is a citation to a published, peer-reviewed paper — not an extraordinary claim — and is different in kind from the NHT citation to a potentially non-existent 2026 preprint. However, the R1 review flagged the specific number (+21pp) as unconfirmed.

**R2 assessment:** The Liu et al. 2021 paper is real and published. The +21pp claim is a specific number from the paper's results tables. A reviewer familiar with the JTT paper would know this number and would not flag it. The remaining risk is that the exact number may differ from what is reported (some papers report different Waterbirds variants). This is a pre-submission verification task (look up Table 1 of Liu et al. 2021), not a fundamental issue.

**Severity:** MAJOR (for submission completeness) but LOW risk of causing desk rejection. Should be verified against Liu et al. 2021 Table 1 before final submission.

---

## MINOR Issues (Human Review Notes — Do Not Auto-Fix)

1. **MINOR-R2-1 (Notation inconsistency):** The paper uses "ratio = 8.8x" (rounded to 1 decimal) in the abstract and introduction, but Table main results reports "8.805" (3 decimal places). This is not an error, but reviewers may note the inconsistency in precision across contexts. Suggest standardizing to "ratio = 8.8x" throughout narrative text and reserving "8.805" for tables.

2. **MINOR-R2-2 (Epoch-10 AUC slight non-monotonicity):** Table 2 shows AUC trajectory: 0.952 (epoch 1) → 0.912 (epoch 3) → 0.914 (epoch 5) → 0.888 (epoch 10). The AUC increases slightly between epoch 3 and 5 (0.912 → 0.914) after declining from epoch 1 to 3. This non-monotonicity is real (verified from JSON: 0.9116 → 0.9140) and is not discussed. A skeptical reviewer may ask whether AUC is truly a meaningful signal given this non-monotone behavior. The ratio is monotone increasing to epoch 5; the AUC behavior is slightly anomalous. Worth one sentence of acknowledgment.

3. **MINOR-R2-3 (G3 epoch-10 boundary issue):** At epoch 10, G2 mean = 0.211 (barely above 0.2), G1 mean = 0.140 (below 0.2). The claim "g̃ > 0.2 separates all minority means from all majority means" is stated as a general property in Section 6.1 Finding 1, but this holds only at epoch 5, not epoch 10. The paper should clarify this boundary claim is epoch-5-specific.

4. **MINOR-R2-4 (YAML metadata):** `hypothesis_id: "H-GNR-LLR-v1"` and `generated_by: "Anonymous Research Pipeline v2.0 — Phase 6"` in the YAML header must be removed before submission. These were flagged in R1 (MINOR-7) and remain. Not auto-fixed.

5. **MINOR-R2-5 (Citation year consistency):** Kirichenko et al. cited as "[2022]" but venue listed as "ICLR 2023." This inconsistency was flagged in R1 (MINOR-2) and remains. Should standardize to publication year (2022 preprint or 2023 ICLR).

6. **MINOR-R2-6 (h_norm_std_ratio precision):** The paper reports "h_norm_std_ratio ≈ 0.10" throughout. The actual values are: epoch 1 = 0.1018, epoch 3 = 0.0974, epoch 5 = 0.1051, epoch 10 = 0.1183. The epoch-10 value is 0.118 — approaching 0.12. While ≈0.10 is a reasonable characterization for epochs 1–5, for epoch 10 the approximation is slightly less accurate. Not a significant issue but worth noting.

7. **MINOR-R2-7 (Outer-product notation):** The paper uses both "⊗" (outer product, Section 3.1) and the notation ‖pᵢ − yᵢ_onehot‖ · ‖h(xᵢ)‖ (Section 2.3, Section 3.1). The outer product of two vectors a ⊗ b produces a matrix, and the Frobenius norm of this matrix equals ‖a‖·‖b‖. This is correct. However, the paper writes "∇_W ℓᵢ = (pᵢ − yᵢ_onehot) ⊗ h(xᵢ)" which is standard notation for the outer product. Some reviewers may prefer explicit notation "(pᵢ − yᵢ_onehot) h(xᵢ)^T" to avoid ambiguity with the Kronecker product. Minor stylistic point.

---

## Mathematical Validity Assessment Summary

| Check | Result | Verdict |
|-------|--------|---------|
| Ratio 8.805 internal consistency | Computed independently: 8.806 (rounds from full-precision to match) | VERIFIED |
| AUC=0.914 consistency with per-group means | Consistent with overlapping G1/G3 tails; not contradicted by data | VERIFIED |
| Outer-product decomposition correctness | Mathematically standard and correct | VERIFIED |
| h_norm_std_ratio ≈ 0.10 | Confirmed from JSON: 0.101 (ep1), 0.097 (ep3), 0.105 (ep5), 0.118 (ep10) | VERIFIED |
| Estimated minority recall ≥90% | Plausible but uncomputed; cannot be verified from available data | UNVERIFIED |
| Epoch-10 g̃ boundary (g̃>0.2 separates groups) | Fails at epoch 10: G1 mean=0.140 < 0.2 | PARTIAL — epoch-5 claim only |
| Per-group sample counts (G0=3498, G1=184, G2=56, G3=1057) | Matches standard Waterbirds metadata | VERIFIED |

**Overall mathematical validity: STRONG.** All computed values are internally consistent. The one unverified quantity (minority recall) is acknowledged as estimated. No fabricated or inconsistent numbers found.

---

## R2 Recommendation

**Recommendation: CONVERGE**

**Rationale:**

The R1 revision successfully addressed both FATAL issues:
- NHT unverified citation: fully removed, replaced with self-contained mechanistic analysis
- DFR 92.9% WGA false comparison: fully removed
- Systematic GNR-LLR title/abstract overclaim: substantially reduced; title re-scoped, abstract re-written, Stage 2 clearly labeled future work

No new FATAL issues were introduced in R1.

The remaining issues are:
- **2 MAJOR issues:** (1) minority recall ≥90% uncomputed (honest limitation, acknowledged in paper); (2) residual GNR-LLR framing in Section 3.4 (reduced but not eliminated). These are submission risks, not fundamental credibility failures.
- **1 MAJOR issue (carried):** JTT +21pp unverified against published paper — pre-submission verification task.
- **7 MINOR issues:** Notation, formatting, metadata — human review tasks.

The paper's core claims (AUC=0.914, ratio=8.8x, h_norm_std_ratio≈0.10, outer-product decomposition) are fully verified against ground truth and internally consistent. The mathematical validity is strong. The framing is honest about scope limitations.

The paper is ready for human review to assess: (a) whether the uncomputed minority recall is acceptable given explicit limitation disclosure; (b) whether venue norms accept a Stage-1-only mechanistic study with Stage 2 as future work.

**Final verdict: CONVERGE — no further adversarial rounds required. Route to human review.**

---

## Summary Return Values

```yaml
fatal_count: 0
major_count: 3  # MAJOR-R2-1 (minority recall uncomputed), MAJOR-R2-2 (GNR-LLR residual), MAJOR-R2-3 (JTT +21pp unverified)
minor_count: 7
persuasiveness_passed: true  # Core claims are verified; framing is honest; mathematical validity confirmed
recommendation: CONVERGE
key_issues_remaining:
  - "Minority recall ≥90% in top-25% subset: claimed as estimated, not computed; Limitation 3 acknowledged"
  - "GNR-LLR two-stage name retained in Section 3.4 with full Stage 2 spec — residual framing risk for reviewers"
  - "JTT +21pp WGA: cited external result, not independently verified against Liu et al. 2021 Table 1"
  - "g̃>0.2 boundary claim in Section 6.1 Finding 1 applies to epoch-5 only, not general"
```

---

*Review generated by Adversarial Agent — Phase 6.5 Round 2*
*Paper: 06_paper_r1.md | Date: 2026-03-16*
*Ground truth source: h-e1/experiment_results.json (verified via Serena MCP)*
