# Adversarial Review - Round 1

**Paper:** The Coordinate System, Not the Symmetry Group: Graph-Based SSL for Cross-Architecture Weight Space Transfer
**Reviewed:** 2026-08-05
**Reviewer:** Adversary Agent v2

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy | 0 | 3 | Numbers mostly verified; key inconsistency in EquiSSL R² across tables; +221% vs +219% discrepancy; unverified citation used causally |
| Engagement | 0 | 1 | Hook works; abstract too long; novelty buried in introduction |
| Credibility | 0 | 4 | SANE SOTA claim needs qualification; n=53 single-seed claims overstated in contributions; unverified citation overclaimed; Table 1 vs Table 2 different-run distinction insufficient |
| **TOTAL** | **0** | **8** | Needs revision before NeurIPS/ICML submission |

**Recommendation:** MAJOR_REVISION

---

## Ground Truth Verification Table

| Claim | Paper | Ground Truth | Match? |
|-------|-------|--------------|--------|
| EquiSSL-perm R² (Table 1, h-m1) | 0.231 | 0.23050326 | YES (rounded) |
| SANE R² | 0.072 | 0.07214606 | YES (rounded) |
| +221% improvement over SANE | 221% | (0.231-0.072)/0.072 = 220.8% | YES (rounds to 221%) |
| +219% in h-m1 validation report | 219% | 219.5% actual | YES (h-m1 report says +219%; paper says +221%; both round correctly from slightly different decimal precision) |
| EquiSSL R² (Table 1, h-m1) | 0.210 | 0.20980585 | YES (rounded) |
| EquiSSL R² (Table 2, h-m2) | 0.185 | 0.18456625 | YES (rounded) |
| EquiSSL-perm R² (Table 2, h-m2) | 0.327 | 0.32737555 | YES (rounded) |
| ΔR² Table 2 (h-m2) | +0.143 | 0.14280929 | YES (rounded) |
| 3x improvement claim | "3x" | 0.231/0.072 = 3.19x | YES (conservative, acknowledged) |
| SANE latent std | 0.0014 | 0.0014 | YES |
| MMD_SANE | 0.849 | 0.8487 | YES (rounded) |
| MMD_EquiSSL | 2.348 | 2.3484 | YES (rounded) |
| MMD ratio (EquiSSL/SANE) | "2.77x higher" | 2.348/0.849 = 2.765 | YES |
| EquiSSL-perm MMD | 0.203 | 0.20343995 | YES |
| acc_latent | 0.100 | 0.100 | YES |
| acc_ws | 0.125 | 0.12516028 | YES (rounded) |
| mean_delta | -0.025 | -0.02516028 | YES (rounded) |
| t-statistic | -24.52 | -24.52021797 | YES |
| p-value | ~9.0e-88 | 9.012e-88 | YES |
| Cohen's d | -1.10 | -1.09657748 | YES (rounded) |
| % pairs positive | 9.4% | 9.381% | YES |
| n_vit_models | 53 | 53 | YES |
| Training models | ~3,000 CNN | 2,999 actual | YES |
| Interpolation pairs | 501 | 501 | YES |

---

## Part 1: Accuracy Check (Persona 1)

### FATAL Issues - Accuracy

None found. All numerical claims verified against ground truth.

### MAJOR Issues - Accuracy

**ACC-MAJOR-001: EquiSSL R² inconsistency between Table 1 and Table 2 is under-explained**

Table 1 (h-m1) shows EquiSSL R²=0.210. Table 2 (h-m2) shows EquiSSL R²=0.185. Same method (EquiSSL scale+perm), same seed (0), same test set (53 ViT-S/16), but different absolute values. Table 2 has a caption note: *"h-m2 uses a fresh training run (seed 0 from scratch) which explains the higher absolute R² values."* This explains EquiSSL-perm's difference (0.231 vs 0.327) but does NOT explain why EquiSSL drops from 0.210 (h-m1) to 0.185 (h-m2) in the fresh run. A fresh run producing LOWER EquiSSL performance while HIGHER EquiSSL-perm performance is a non-trivial inconsistency that needs explicit acknowledgment. A skeptical reviewer will question whether the Tables are cherry-picked to show favorable orderings from different runs.

Ground truth confirms: h-m1 EquiSSL=0.2098, h-m2 EquiSSL=0.1846 — the same encoder trained fresh produces lower R² for EquiSSL but higher for EquiSSL-perm. This is plausible with single-seed stochasticity but must be explicitly flagged.

**ACC-MAJOR-002: Relative improvement stated inconsistently across paper and validation report**

The paper states "+221% improvement" in Section 5.1, Table 1, and Conclusion. The h-m1 validation report (04_validation.md) states "+219%". Ground truth: (0.23050326 - 0.07214606) / 0.07214606 * 100 = 219.5%. The paper rounds 219.5% to 221% (incorrect rounding — 219.5% rounds to 220% or should be stated as approximately 220%). This is a minor but real arithmetic error. The correct value is approximately 220%, not 221%.

Precise check: 0.159/0.072 * 100 = 220.8% using rounded paper values; using exact values: 219.5%. Neither rounds to 221%. The 221% figure appears to use 0.231 and 0.072 with full precision: (0.231-0.072)/0.072 = 220.8% ≈ 221% — this IS a valid rounding. However the validation report states 219% using exact values. The paper should clarify which computation it uses and be consistent with the validation report.

**ACC-MAJOR-003: Unverified citation [Anonymous2025LayerNorm] used as causal mechanism support**

The paper cites [Anonymous2025LayerNorm] / arXiv:2510.08300 as providing "theoretical support" and "consistent with recent theoretical analysis" for the LayerNorm gauge-fixing claim. Ground truth confirms this citation is marked [UNVERIFIED] — could not be verified in Semantic Scholar. The paper uses this citation in three places: Abstract, Introduction (Section 1), and Related Work (Section 2.4), as well as Methodology (Section 3.4).

The problem is not the citation itself (it is flagged [UNVERIFIED] in the references section) but the framing: "consistent with recent theoretical analysis [Anonymous2025LayerNorm]" implies an established result, when the paper cannot confirm the citation exists or supports the specific claim. The LayerNorm argument stands on its own empirical merits (EquiSSL underperforms EquiSSL-perm); the citation should be demoted from "support" to "see also if verifiable" or removed until verified.

---

## Part 2: Engagement Check (Persona 2)

*Bored reviewer with 5 papers, scanning at a conference.*

### Bored Reviewer Verdict Table

| Checkpoint | Verdict | Notes |
|------------|---------|-------|
| Title scan | CONTINUE | Title is specific and intriguing — "coordinate system not symmetry group" is memorable |
| Abstract (30 sec) | CONTINUE | Opens with the actual result not a motivation sentence. No "X is important" opener. Good. |
| Abstract completeness | CONCERN | 150 words, but "3x R² improvement" without stating the base R² values. A reviewer wonders: 3x of what? 0.001? 0.72? Numbers missing from abstract. |
| Introduction paragraph 1 | CONTINUE | Hook paragraph is strong — counterintuitive claim in first sentence, key insight in second. Executes the blueprint strategy correctly. |
| Contributions list | SLOW DOWN | Four contributions; contribution (3) mentions "R²=0.231–0.327" with a range that requires understanding two separate experiments. This will confuse a first-pass reader. |
| Related work | SKIM | Section is clean and focused. Passes the "anti-survey" check. Each paragraph ends with a gap statement. |
| Results tables | CONCERN | Table 1 and Table 2 have different absolute values for EquiSSL-perm (0.231 vs 0.327). A reviewer skimming tables will notice this immediately and be confused before reaching the caption explanation. |
| At what point attention lost | Section 5.3 | The t-SNE visualization section describes figures that are not embedded in the paper text, only referenced by filename. Without actually seeing the figures, the qualitative claims are unverifiable and the section feels like filler. |

### FATAL Issues - Engagement

None.

### MAJOR Issues - Engagement

**ENG-MAJOR-001: Abstract missing base R² context for the "3x" claim**

The abstract states "achieving a 3x R² improvement over SANE without any ViT training data." A reader cannot assess this without knowing SANE's baseline R². The abstract should include something like: "SANE achieves R²=0.072 (near noise) while EquiSSL-perm achieves R²=0.231 — a 3x improvement." Currently a reviewer must read to Section 5.1 to understand the magnitude. For a NeurIPS/ICML abstract, the base value must be stated.

---

## Part 3: Credibility Check (Persona 3)

*Ten-year domain expert in weight-space SSL and equivariant GNNs.*

### Novelty Claims Audit Table

| Claim | Paper's Framing | Assessment |
|-------|----------------|------------|
| "First use of graph SSL for cross-architecture transfer to ViTs" | "No prior work demonstrates SSL-based weight representation transfer...to ViT" | PLAUSIBLE — Ballerini 2025 (NeRF SSL) is cited as most related; the paper's scope (general architectures, ViTs) is distinct. Claim is supportable if precisely stated. |
| "Establishes a new baseline for cross-architecture SSL transfer" | Introduction Contribution (2) | PROPORTIONATE given caveats, though see CRED-MAJOR-003 |
| LayerNorm gauge-fixing = causal explanation | "We attribute this to LayerNorm's gauge-fixing property" | OVERSTATED as currently written — this is a hypothesis, not a proven mechanism (acknowledged in limitations, but not clearly marked as hypothesis in results section) |
| Scale equivariance "reversal" | "The most striking result" | PLAUSIBLE but single seed — a 0.143 difference on 53 models with 1 seed is directionally interesting, not definitively striking |

### Baseline Fairness Audit Table

| Baseline | Fairness Issue | Severity |
|----------|---------------|----------|
| SANE described as "current state of the art" | SANE (ICML 2024) is likely appropriate SOTA for weight-space SSL. However, the paper should note that SANE was designed for within-family SSL, not cross-architecture — calling it "cross-architecture SSL SOTA" is slightly unfair since that's not SANE's design goal | MINOR |
| SANE + VICReg fix | Adding VICReg to prevent SANE collapse is reasonable. However, the paper trains SANE with its flat tokenizer on CNN data and evaluates on ViT data — this is indeed SANE's intended usage. The VICReg fix is disclosed. Fair. | OK |
| EquiSSL (ScaleGMN) as "ablation baseline" | Calling ScaleGMN an "ablation baseline" is technically correct (it's a variant of the authors' approach), but ScaleGMN is also an independent published method. The framing is slightly self-serving. | MINOR |
| Absence of supervised cross-architecture baselines | Kofinas 2024 achieves R²=0.71 in SUPERVISED cross-arch transfer (MLP→CNN). No comparison to supervised methods is made. The paper is SSL-only, but reviewers will ask: does EquiSSL-perm at R²=0.231 vs supervised at R²=0.71 tell us anything about the SSL overhead? | MAJOR — see below |

### FATAL Issues - Credibility

None.

### MAJOR Issues - Credibility

**CRED-MAJOR-001: Contribution (3) presents EquiSSL R² range "0.231–0.327" without explaining these come from different training runs**

In Introduction Contribution (3): "EquiSSL achieves R²=0.185, underperforming EquiSSL-perm (R²=0.231–0.327)." A range 0.231–0.327 is presented as a single method's performance range, but these are actually from two different training runs (h-m1 and h-m2 respectively). This is not the range across seeds — it is stochastic variation across independently trained checkpoints. Presenting them as a range without this clarification is misleading. A reviewer will interpret this as a 95% CI or seed range, neither of which is correct.

**CRED-MAJOR-002: The SANE comparison is potentially unfair without noting SANE R²=0.72 in its intended setting**

The paper repeatedly characterizes SANE as "current SOTA" achieving "near-chance R²=0.072" on ViT transfer. Ground truth (Related Work): SANE achieves R²=0.72 on heterogeneous model zoo prediction within its intended setting. The paper acknowledges this in the Related Work section, but the Main Results section and Abstract do not. A reviewer will ask: "Is SANE failing because it's a bad method, or because it's being tested outside its design envelope?" The paper argues the latter (flat tokenization is the root cause), but this argument needs to be stated more prominently in the results section, not just in Related Work. Otherwise the paper appears to be reporting SANE's failure on an out-of-distribution task without disclosing that SANE is not designed for this task.

**CRED-MAJOR-003: "Establishing a new baseline" claim is disproportionate to n=53, single seed, proof-of-concept evidence**

Introduction Contribution (2) states: "establishing a new baseline for cross-architecture SSL transfer." The Limitations section appropriately qualifies these as "proof-of-concept results" with "directional findings" only. However, the Contributions section — which reviewers read first — does not carry this qualifier. A baseline claim implies reproducibility and reliability. With n=1 seed and n=53 test models (of 250 available), the claim "establishing a new baseline" overstates the maturity. The qualifier "proof-of-concept baseline" or "initial evidence for a new baseline" would be accurate; "establishing" is not.

**CRED-MAJOR-004: The unverified citation is used to frame the LayerNorm argument as theoretically grounded rather than an empirical hypothesis**

Section 3.4 title is "Why Permutation-Only: The LayerNorm Gauge Argument" and opens: "This 'gauge fixing' [arXiv:2510.08300] eliminates the scale degree of freedom." Section 2.4 states: "Anonymous [2025, arXiv:2510.08300] argues that LayerNorm...fixes the gauge degree of freedom." The citation is marked [UNVERIFIED] in the References, but in the body text it is presented as established theoretical support.

This creates a credibility problem: if arXiv:2510.08300 does not exist or does not support this specific claim, the "theoretical grounding" for the paper's key mechanism evaporates, leaving only the empirical observation (which is valid on its own). The LayerNorm gauge argument should be reframed as: "We hypothesize that LayerNorm eliminates the scale degree of freedom [cite if verified], which predicts the observed reversal. The reversal itself is empirically confirmed." Currently the unverified citation is doing structural load-bearing work in the argument.

---

## Part 4: Human Review Notes

(Typos, grammar, style — NOT counted in FATAL/MAJOR totals)

| # | Location | Issue | Suggested Fix |
|---|----------|-------|---------------|
| H1 | Section 2, Related Work, paragraph 3 | Citation "[Navon et al., 2026]" — 2026 is in the future relative to the paper date; likely a typo or speculative future survey. The main paper references Navon 2023 (ICML) correctly in the References section. | Verify year — likely should be 2023 or 2025 |
| H2 | Section 2, Related Work, paragraph 3 | "ViT Model Zoo of [Zhu et al., 2025]" — but the References list cites Falk et al. 2025 (arXiv:2504.10231). The author name "Zhu et al." appears only in the Related Work section file (02_related_work.md), not in the compiled paper (06_paper.md) which correctly cites Falk et al. If the section file is the source of truth, this is an incorrect author attribution that did not propagate to the full paper. | Verify section file vs full paper consistency; if section files are used for final paper, fix to "Falk et al." |
| H3 | Section 3.6 / Methodology | SANE reference numbering: paper body uses [Schurholt2024Towards] (full paper) while Related Work section file uses [Schürholt et al., 2024] with umlaut. Different citation styles between sections — likely a compilation artifact. | Standardize citation keys |
| H4 | Section 5.1 | "Figure 4 vs Figure 5 (tsne_equissl_seed0.png vs tsne_sane_seed0.png)" — but later Section 5.3 describes "Figure 5 (fig3_tsne.png)" as a 4-panel t-SNE. Figure numbers are inconsistent between sections. Section 5.3 also references "Figure 5 (fig3_tsne.png)" while Section 5.1 references "Figure 4 vs Figure 5" with different filenames. The Appendix describes these as "Figure 4 vs Figure 5 (tsne_equissl_seed0.png and tsne_sane_seed0.png)" with "Figure 5 (fig3_tsne.png)". | Resolve figure numbering — appears to be a compilation inconsistency between section files and the full paper |
| H5 | References | [Anonymous2025LayerNorm] is listed with "[UNVERIFIED]" tag inline in the references — this is appropriate for a draft but must be removed or resolved before submission | Verify or remove citation before submission |
| H6 | Section 4, Datasets | "53 ViT-S/16 ImageNet checkpoint" — missing plural "checkpoints" | Fix to "checkpoints" |

---

## Summary for Revision Agent

### Priority Fix List (ordered by severity and impact)

1. **[CRED-MAJOR-004 + ACC-MAJOR-003] Unverified citation handling** — arXiv:2510.08300 is used as load-bearing theoretical support but marked [UNVERIFIED]. Either: (a) verify the citation exists and supports the claim, then remove the [UNVERIFIED] tag; or (b) reframe the LayerNorm gauge argument as an empirical hypothesis supported by the data, with the citation as an optional "see also if verifiable." Do not present an unverified citation as established theory in the body text.

2. **[CRED-MAJOR-001] EquiSSL R² range "0.231–0.327" in Contribution (3)** — This range spans two different training runs, not seeds. Replace with: "R²=0.185 (h-m2 ablation run)" or add explicit parenthetical: "(0.231 in main run Table 1; 0.327 in ablation run Table 2 — both seed 0, both confirming the ordering)."

3. **[ACC-MAJOR-001] Table 1 vs Table 2 EquiSSL inconsistency** — Add a clear note to both tables explaining that EquiSSL R² differs between tables (0.210 in Table 1 vs 0.185 in Table 2) because they come from independent training runs. The note in Table 2's caption only explains the EquiSSL-perm difference, not the EquiSSL direction reversal (h-m1 EquiSSL=0.210 > h-m2 EquiSSL=0.185 despite a "fresh" run). Acknowledge this explicitly.

4. **[CRED-MAJOR-003] "Establishing a new baseline" in Contribution (2)** — Downgrade to "provide initial proof-of-concept evidence for a new baseline" or "propose a new baseline" to match the stated limitations (n=1 seed, n=53 models, single GPU).

5. **[ENG-MAJOR-001] Abstract missing base R² values** — Insert: "SANE achieves R²=0.072 on held-out ViT models; EquiSSL-perm achieves R²=0.231 — a 3x improvement." Currently readers cannot evaluate the "3x" claim without reading Section 5.1.

6. **[CRED-MAJOR-002] SANE comparison context** — Add a brief statement in Results Section 5.1 noting that SANE achieves R²=0.72 in its intended within-architecture setting, so the R²=0.072 on ViT transfer reflects the cross-architecture distribution shift failure, not the method's general capability. This protects against the obvious reviewer attack: "of course SANE fails on ViT, that's not what it was designed for."

7. **[ACC-MAJOR-002] +221% vs +219% consistency** — Decide on one number: exact computation gives 219.5%; using rounded inputs (0.231-0.072)/0.072 * 100 = 220.8% ≈ 221%. Pick one (recommend 220%) and use it consistently in Abstract, Introduction, Results, and Conclusion.

8. **[H1] Citation year "[Navon et al., 2026]"** — Verify; likely should be 2023 or remove if speculative.

9. **[H2] "Zhu et al." vs "Falk et al." for ViT Model Zoo** — Reconcile between section files and full paper. Correct attribution is Falk et al. 2025 (arXiv:2504.10231).

10. **[H4] Figure number inconsistencies** — Section 5.1 references "Figure 4 vs Figure 5" with specific filenames that conflict with Section 5.3's "Figure 5 (fig3_tsne.png)". Audit all figure references against the actual generated figure files.
