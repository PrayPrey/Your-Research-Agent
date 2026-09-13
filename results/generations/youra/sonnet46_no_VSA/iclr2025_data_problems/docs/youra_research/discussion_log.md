# Phase 2A Discussion Log: h-m1-v2

**Date:** 2026-07-30  
**Gap:** Gap 1 — No Prior Direct Comparison of Global vs. Per-Language Percentile Perplexity Thresholds on Cramér's V Retention Equity  
**Execution Mode:** UNATTENDED (Self-Contained Tikitaka Loop)  
**Architecture:** paper-reading-round0-only-then-mcp-search  

---

## Briefing

### Research Question

In RedPajama-v2 CommonCrawl quality signal metadata, does applying a **language-adaptive perplexity threshold** (τ_lang = k-th percentile of per-language perplexity distribution, for k ∈ {10, 20, 30, 40, 50}) produce a statistically significantly lower language-group retention disparity (Cramér's V) compared to the global perplexity threshold baseline — specifically, does ΔCramér's V ≥ 0.1 for at least 3 of 5 k values, with all group-level retention rates falling within [40%, 60%] of each other under the adaptive threshold?

### Key Context from Phase 1

- **Dataset:** RedPajama-V2 CommonCrawl quality signals (Parquet metadata), 5 languages (en/de/fr/es/it), 208,263 rows already processed in h-m1
- **Baseline established:** h-m1 confirmed Cramér's V = 0.29–0.41 under global CCNet threshold — English most excluded (3.7%–36.5% retention), Italian least excluded (18.2%–88.1%)
- **Core pattern:** CCNet trains per-language KenLM LMs on Wikipedia but applies global percentile bucket cutoffs → threshold-calibration artifact
- **Implementation:** `df.groupby('language')['ccnet_perplexity'].transform('quantile', k/100)` — 1 line of pandas
- **Constraint:** CPU-only, static Parquet files only, no HTTP APIs, no GPU, no model inference

### Available Papers (5 prepared)

- **P1:** arxiv_2411_12372 — RedPajama: Open Dataset for Training LLMs [Weber et al., 2024]
- **P2:** arxiv_2103_12028 — Quality at a Glance: Audit of Web-Crawled Multilingual Datasets [Caswell et al., 2021]
- **P3:** arxiv_1911_00359 — CCNet: Extracting High Quality Monolingual Datasets [Wenzek et al., 2019]
- **P4:** arxiv_2604_20549 — Toward Cross-Lingual Quality Classifiers [Turki et al., 2026]
- **P5:** arxiv_2212_10440 — Perplexed by Quality [Jansen et al., 2022]

---

## Previous Failure / Routing Context

**This is a recursive Phase 2A invocation.** Summary of prior hypothesis history:

| Hypothesis | Status | Root Cause | Direction for h-m1-v2 |
|---|---|---|---|
| h-e1 | FAIL (run1) | Corpus coverage insufficient (~0.05% of Pile) — NOT methodological | Avoid full-corpus streaming without pre-built index |
| h-c1 | LIMITATION | infini-gram API HTTP 403 IP-level block | Zero HTTP API dependencies |
| h-e2-v3 | LIMITATION | Pile-full infini-gram API blocked | Zero infini-gram API; local index only |
| h-m1 | SUPERSEDED | Direction inverted — English excluded MORE, not low-resource | Build on h-m1 finding: adaptive threshold to fix English-exclusion bias |
| h-m1 (run1) | FAIL / SYNTHETIC_DATA_INVALID | 4/5 Pythia model sizes synthetic | No synthetic data; all metrics from real static files |

**Key constraints for hypothesis redesign:**
1. NO infini-gram HTTP API
2. NO GPU/CUDA/model inference  
3. NO synthetic/generated data
4. NO new benchmarks or human evaluation
5. ALL data must be static pre-existing files (RedPajama-V2 Parquet)
6. h-m1 validated: global threshold Cramér's V = 0.29–0.41 (English disproportionately excluded)
7. h-m1 validated: pipeline infrastructure correct (208,263 rows, 27/27 tests pass)

**What showed promise (preserve):**
- RedPajama-V2 Parquet static analysis pipeline (full infrastructure valid)
- Cramér's V as the primary equity metric
- Holm-corrected chi-square for group retention significance
- 5 k-threshold sweep pattern (10th–50th percentile)

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, your hypothesis is crisp, but we must correct a factual premise before proceeding. In CCNet, perplexity thresholds are already **language-specific**: "Languages are split into three equal-sized terciles (head/middle/tail) by PPL (language-specific thresholds)" [Wenzek et al., 2019]. If your baseline uses a *global* `cutoff.csv` across languages, then you are not evaluating the original CCNet tercile design but a modified variant. The evidence suggests that the first step is definitional clarity: are we comparing (A) global percentile thresholds applied to all languages versus (B) per-language percentiles, or (B) versus (C) the exact CCNet implementation? Without this, any claimed novelty risks targeting a strawman.

Assuming your baseline truly uses global percentiles, the core hypothesis becomes testable: **H₁: Per-language percentile thresholding reduces association between language and retention (Cramér's V) relative to global percentile thresholding.** To avoid ambiguity, pre-register: (i) fixed k values (e.g., 10%, 30%, 50%), (ii) exact languages (≥5 with ≥1M docs to ensure power), and (iii) a success criterion such as ΔV ≥ 0.10 with bootstrap 95% CI excluding 0 for ≥3 k values. The evidence would disconfirm H₁ if ΔV < 0.05 or confidence intervals overlap zero across most k. Additionally, report absolute retention parity: max–min retention rate difference ≤5 percentage points would be a stronger criterion than Cramér's V alone.

However, what would disprove the deeper claim—that bias is purely a calibration artifact? If per-language percentile thresholds equalize retention but downstream quality diverges, then calibration is not the only factor. CCNet demonstrates that lower perplexity strata yield better embedding and BERT performance (e.g., English fastText analogy: head 77.9 vs tail 62.0; XNLI +3.3 avg for CCNet head over Wikipedia) [Wenzek et al., 2019]. Therefore, you must test whether recalibration preserves the monotonic quality gradient within each language. A critical falsifier would be: recalibration increases English retention to 40%+, but analogy/XNLI performance of the retained set drops ≥2 points relative to the original head tercile. That would indicate you are trading equity for quality.

Confounds must also be controlled. Deduplication order (Dedup → LID) materially affects language distribution, especially for low-resource languages [Wenzek et al., 2019]. If your experiment is conducted post-dedup but pre-LID confidence filtering, shifts in Cramér's V may reflect LID confidence artifacts rather than perplexity calibration. Fix the pipeline order and LID confidence threshold (>0.5) across all conditions. Additionally, perplexity scale differences may arise from tokenization (SentencePiece per language) and corpus size disparities in KenLM training. To test scale commensurability, compute z-scored perplexity within each language and compare distributional overlap; if z-normalization alone reduces V, then the issue is scale variance, not percentile choice.

Finally, design the experiment to fail. Include a synthetic control: randomly permute language labels before thresholding. If recalibration still reduces V under permutation, your metric is unstable. Include an extreme case: a language with highly skewed perplexity distribution (heavy tail). If percentile thresholding still yields unequal semantic quality strata, then percentiles are insufficient and quantile matching may need distribution-shape correction (e.g., matching entropy or variance).

If, after these controls, ΔCramér's V ≥ 0.10, retention parity improves, and downstream quality remains within ±1 point of original head performance, I will say: *This meets my standards.*

**Key Points:**
- Clarify baseline: CCNet already uses language-specific terciles; ensure the comparison is against a true global-threshold variant.
- Pre-register falsifiable criteria (ΔCramér's V, retention parity, downstream quality preservation) with bootstrap CIs.
- Control for pipeline confounds (Dedup→LID order, LID confidence, tokenization scale) and include synthetic/permutation tests to stress the metric.

---

### Exchange 4

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — this is getting sharper. But here's where this still breaks down.

First, the calibration claim is overstated. CCNet already uses **language-specific terciles by perplexity** [Wenzek et al., 2019, Methodology]. That means the original pipeline *does not* apply a global decision boundary. So if your baseline is a global percentile over RedPajama's stored `ccnet_perplexity`, you are not "fixing CCNet." You are comparing (A) a post-hoc global quantile on exported scores versus (B) the original per-language quantile design. That's fine — but say it clearly. The real hypothesis becomes: *when practitioners ignore CCNet's language-specific cutoffs and apply global thresholds to aggregated perplexity scores, they induce language skew that can be corrected by per-language percentile calibration.* That's narrower. It's also more defensible.

Second: you're assuming percentile matching addresses the right failure mode. Show me the evidence that cross-language perplexity distributions differ mainly in **location/scale** rather than **shape**. CCNet trains separate SentencePiece tokenizers and 5-gram Kneser–Ney LMs per language [Wenzek et al., 2019]. Tokenization granularity alone can distort perplexity magnitude. If English uses longer subword sequences on average than Italian, perplexity per token is not directly comparable — even before noise effects. Percentiles neutralize monotonic scaling differences, yes. But if distributions differ in kurtosis or multimodality, equal percentiles do *not* imply equal semantic quality strata. What would convince me is: Q–Q plots across languages, plus a test showing that z-scoring within language does *not* already eliminate most of ΔCramér's V. If z-normalization collapses the effect, your "percentile innovation" is just scale correction in disguise.

Third: your success criterion is too weak. A drop in Cramér's V of 0.10 sounds nice, but what does that mean in operational terms? CCNet processes billions of documents (e.g., 706M English docs post-filtering) [Wenzek et al., 2019, Results]. If your recalibration shifts English retention from 36% to 40%, that's tens of millions of documents. Is that shift concentrated in the long tail of high-perplexity noise, or are you pulling in borderline garbage? Without downstream evaluation, you can't assert this is "equity without quality loss." I accept Pax's compute constraint — but then reframe the claim. You are testing *distributional parity of selection*, not fairness of usable training signal. Be precise.

Fourth: pipeline confounds are non-negotiable. CCNet shows **Dedup → LID** materially changes language retention, especially for low-resource languages [Wenzek et al., 2019, Ablations]. If RedPajama's stored perplexities were computed before or after dedup/LID variants, your calibration effect may reflect upstream filtering artifacts. Fix LID confidence (>0.5, as in CCNet) and document whether perplexity was computed on pre- or post-dedup text. If you can't control that, your internal validity is compromised.

Now, here's how you make this bulletproof: (1) Pre-register three conditions: global percentile, per-language percentile, and per-language z-score threshold. (2) Report (a) Cramér's V, (b) max–min retention gap, and (c) KL divergence between language distributions before/after filtering. (3) Add the permutation control Vera suggested — and I want to see V ≈ 0 under permutation for both thresholding schemes. If adaptive still "improves" V under permuted labels, your metric is structurally biased.

If you show: (i) substantial V reduction under real labels, (ii) no reduction under permutation, and (iii) z-scoring does *not* explain away the effect — then I'll say you've isolated a genuine calibration artifact.

**Key Points:**
- Clarify you are correcting a practitioner-level global-threshold misuse, not CCNet's original design.
- Demonstrate that percentile gains are not reducible to simple scale normalization (test z-scoring, Q–Q plots).
- Strengthen validity with permutation controls, retention-gap metrics, and explicit pipeline alignment.

---

### Exchange 5

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Rex has sharpened this to the critical question: is this calibration artifact correction or distribution-shape correction? I want to evaluate both the significance and the publishability of this work given where the discussion has landed, and I'll draw on what Turki et al. [2026] explicitly say about retention rate tuning as the closest prior work.

Turki et al. [2026] at the DATA-FM Workshop (ICLR 2026) demonstrate that "refining the decision boundary through third quartile sampling (Q3) or tuning the retention rate is necessary to fully leverage the multilingual signal" [Key Contributions]. Their approach uses classifier scores (MLP on XLM-RoBERTa embeddings), not perplexity — but the finding is structurally identical: **global decision boundaries fail multilingual quality selection; per-language boundary tuning is necessary.** This means our hypothesis is not filling a gap in a vacuum — it's the perplexity-based analogue of an effect that Turki et al. confirmed for classifier-based filtering. That makes this publishable: we're showing the same principle holds for the simpler, more widely deployed CCNet perplexity pipeline.

The significance claim I'd make for a workshop paper (DATA-FM is the right venue): "Global perplexity thresholds in CCNet-derived pipelines (as used in RedPajama-V2) induce measurable language-group retention disparity (Cramér's V = 0.29–0.41); per-language k-th percentile calibration reduces this disparity by ≥ ΔV = 0.1 for ≥3 of 5 k values. This is the first direct measurement of this effect and provides actionable guidance for corpus curation practitioners." That's a clean, bounded claim. Prof. Rex's reframing — "distributional parity of selection" rather than "fairness of usable training signal" — is exactly right and actually makes the claim *more* defensible for a workshop venue: we are not asserting quality equivalence, only distributional equity of the selection process.

On the z-score vs. percentile question: I agree with Rex that we need both conditions. But here's the impact argument for including both: if z-scoring reduces Cramér's V MORE than percentile calibration, that actually opens a *second* publishable finding — that the bias is scale-variance, not median-location. That's a more nuanced result and richer for Phase 2B design. Three conditions (global percentile, per-language percentile, z-score normalization) is still 50 lines of pandas. We should run all three.

**Key Points:**
- Turki et al. [2026] provides the closest prior work — classifier-based retention rate tuning → our perplexity analog is the natural extension for simpler pipelines
- Reframe as "distributional parity of selection" per Rex's suggestion — strictly stronger claim, easier to defend without downstream evaluation
- Three-condition experiment (global percentile, per-language percentile, z-score) is feasible and opens richer findings

---

### Exchange 6

🔬 **Prof. Vera** (Rigorous Validation Architect) — Second Appearance:

The reframing is now appropriately constrained: we are not "fixing CCNet," which already applies **language-specific terciles by perplexity** [Wenzek et al., 2019, Methodology], but testing whether practitioners who apply a *global percentile threshold* to exported `ccnet_perplexity` scores induce measurable language–retention dependence. That is a precise and falsifiable claim. The evidence would suggest a calibration artifact if, under identical data and pipeline conditions, a global percentile induces substantial language–selection association (Cramér's V ≈ 0.3–0.4 as reported), and a per-language percentile reduces that association by a pre-registered margin (ΔV ≥ 0.1) across multiple k values.

However, I remain concerned that we have not yet isolated the mechanism. Percentile calibration corrects any monotonic transformation of scale. If cross-language perplexity differences are primarily **location/scale artifacts** arising from distinct SentencePiece tokenization and 5-gram KenLM training per language [Wenzek et al., 2019], then z-scoring within language should produce comparable parity improvements. Therefore, I require three pre-registered conditions: (1) Global k-th percentile (baseline misuse), (2) Per-language k-th percentile, (3) Per-language z-score threshold. The critical prediction is differential: if percentile calibration reduces Cramér's V significantly more than z-scoring, then distributional *shape* differences (skew/kurtosis) are implicated. If z-scoring collapses the effect to the same degree, then the "innovation" is merely variance normalization. What would disprove the stronger claim? If |ΔV_percentile − ΔV_zscore| ≤ 0.02 across k, we must conclude the effect is scale-driven.

We must also guard against structural metric bias. I endorse the permutation control: randomly permute language labels and recompute Cramér's V under all three thresholding schemes. Additionally, report absolute retention-gap metrics (max–min retention rate) and KL divergence between language distributions pre/post filtering. Finally, pipeline alignment: CCNet's retention properties are sensitive to **Dedup → LID ordering** and the **LID confidence > 0.5 threshold** [Wenzek et al., 2019]. If RedPajama's stored perplexities were computed before/after dedup/LID variants, that must be documented. Only then can we attribute any ΔV specifically to thresholding strategy.

**Key Points:**
- Pre-register three conditions (global percentile, per-language percentile, per-language z-score) with explicit falsification thresholds.
- Use permutation controls and complementary metrics (retention gap, KL divergence) to ensure Cramér's V reduction reflects true dependence changes.
- Document and fix upstream pipeline assumptions (Dedup → LID, confidence >0.5) to preserve internal validity.

---

### Exchange 7

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We've reached the point where the hypothesis has been pressure-tested from every angle and can now be articulated in its strongest form. Let me synthesize what has emerged from this discussion and formulate the consolidated hypothesis that can go forward.

**The Core Claim (refined):** In RedPajama-V2 CommonCrawl quality signal metadata, when practitioners apply a global k-th percentile threshold across all languages to pre-computed CCNet perplexity scores, they induce a measurable language-group retention disparity (Cramér's V = 0.29–0.41, established by h-m1). Applying a per-language k-th percentile threshold (computed within each language's perplexity distribution) reduces this disparity by ΔCramér's V ≥ 0.1 for at least 3 of 5 k values ∈ {10, 20, 30, 40, 50}, and this reduction is statistically significant (bootstrap 95% CI excluding zero). The reduction reflects a threshold-calibration artifact in the practitioner application of CCNet-derived scores, not a flaw in CCNet's original per-language tercile design.

**Three conditions to test (incorporating Prof. Vera's and Prof. Rex's requirements):**
1. Global k-th percentile (baseline — established by h-m1)
2. Per-language k-th percentile (primary intervention)
3. Per-language z-score normalization (disambiguation condition — isolates scale vs. shape effects)

**The z-score condition is the diagnostic key.** From Jansen et al. [2022], KenLM-based perplexity distributions for web text exhibit language-specific tail behavior. If per-language percentile calibration reduces ΔV MORE than z-scoring, we confirm the bias involves distributional *shape* (skew/kurtosis differences across languages). If they're equivalent, we confirm it's a scale artifact. Either result is publishable — the first is more novel.

**What we're NOT claiming** (to satisfy Prof. Rex): We are testing *distributional parity of selection*, not fairness of usable training signal. No claim about downstream LLM quality is made. The scope is strictly: on these 208,263 RedPajama-V2 documents, does per-language calibration produce more equitable retention rates across 5 languages?

**Permutation control** (Prof. Vera + Rex): Randomize language labels before applying each threshold — Cramér's V should approach 0 under permutation for all methods. This validates that the metric is measuring genuine language-retention dependence, not marginal distribution artifacts.

The hypothesis is now specific, mechanistic, falsifiable, novel, feasible, and bounded. I'm satisfied.

**Key Points:**
- Consolidated three-condition design: global percentile (baseline), per-language percentile (primary), z-score normalization (disambiguation)
- Permutation control included as validity check
- Reframed as "distributional parity of selection" — precise, defensible, avoids overreach on quality claims
- Core claim: ΔCramér's V ≥ 0.1 for ≥3/5 k values under per-language percentile, bootstrap CI excludes zero

---

### Exchange 8

🎯 **Dr. Sage** (Research Impact Evaluator) — Second Appearance:

The question we must ask is not "can we reduce Cramér's V?" but "what does reducing it teach the field about multilingual data construction?" If this work merely demonstrates that per-language percentile thresholds smooth retention disparities, then it is an implementation note. But if it establishes that widely reused *exported* quality signals (e.g., RedPajama's `ccnet_perplexity`) systematically induce language-dependent selection artifacts when globally thresholded, then we are identifying a reproducible failure mode in secondary dataset curation. That matters because much of the community does not re-run CCNet; they inherit its scores.

RedPajama-V2 is explicitly designed as a "foundation for future filtering research" — it releases 46 quality signals (including `ccnet_perplexity`) for practitioners to apply their own filtering strategies [Weber et al., 2024, Methodology]. This is precisely the reuse scenario we are targeting. Weber et al.'s ablation results show that full Gopher + fuzzy deduplication gives the strongest V2-derived recipe, but perplexity-based filtering is still widely used as a simpler alternative. The RedPajama paper provides no language-equity analysis of perplexity thresholding. Our work fills that gap directly.

On quality verification: we can proxy usable-text quality by examining *within-retention distributions of other Parquet quality signals* (terminal punctuation fraction, unique-word fraction, caps fraction) — secondary analysis on existing Parquet metadata, no GPU required, partially addresses "equity without quality loss."

The generalizability claim is the real contribution: **any language-aware quality score reused with a language-agnostic threshold may induce retention disparities.** This extends beyond CCNet to classifier logits, toxicity scores, or any metric trained on language-specific distributions.

**Key Points:**
- RedPajama-V2's design explicitly invites practitioner filtering with exported quality signals — this IS the real-world scenario
- Proxy quality check using within-retention Parquet quality signal distributions (no GPU needed)
- Generalizability: language-aware scores + language-agnostic thresholds → retention disparity

---

### Exchange 9

🔍 **Prof. Rex** (Hypothesis Stress-Test Master) — Second Appearance:

Two remaining weak points to address, then I endorse.

**Weak point 1: Scope.** Our 208,263-row sample is the RedPajama-V2 *sample subset*, not the full 84-snapshot corpus (14.5B docs, 20.8T tokens per Weber et al. [2024]). The scope must be stated: "On the RedPajama-V2 sample subset (208,263 documents, 5 languages), ..." No overreach to full corpus.

**Weak point 2: Z-score formulation.** "Per-language z-score threshold" needs precision: for each language l, compute μ_l and σ_l of ccnet_perplexity; retain where z_l = (ppl_i - μ_l)/σ_l ≤ z* where z* is selected iso-retention (same overall retain rate as global k-th percentile). This makes the z-score and percentile conditions directly comparable. If iso-retention z-score produces ΔV ≥ per-language percentile, the novelty claim collapses. If percentile produces larger ΔV, we've confirmed a shape effect. This is the critical test.

With those refinements, the three-condition experiment is clean. I endorse.

**Key Points:**
- Scope: RedPajama-V2 sample subset (208,263 docs, 5 languages) — explicit, no overreach
- Z-score: iso-retention formulation for direct comparability
- Hypothesis is rigorous and ready for Phase 2B

---

### Exchange 10

🔬 **Prof. Vera** (Rigorous Validation Architect) — Third Appearance:

The evidence suggests we now have a testable core claim. On the RedPajama-V2 sample subset (208,263 documents; 5 languages), applying a single global k-th percentile threshold on `ccnet_perplexity` yields Cramér's V ≈ 0.29–0.41 (h-m1 baseline). The hypothesis is that replacing this with per-language k-th percentiles — or iso-retention per-language z-score thresholds — will reduce Cramér's V by ≥0.10 for at least 3 of 5 k values. Falsification: ΔV < 0.05 across all k, or bootstrap 95% CIs for ΔV include 0 consistently.

Prof. Rex correctly specifies the z-score condition must be iso-retention: for each language l, compute μ_l and σ_l over its ccnet_perplexity distribution; retain documents with z_l ≤ z* where z* gives same total retained count as global k-th percentile. If z-score performs equivalently to percentiles, shape effect is negligible. If not, we have evidence of heavy-tailed or skew differences across languages.

Important negative control: CCNet's original design uses per-language terciles [Wenzek et al., 2019]. Include a CCNet-consistent condition: select lowest tercile within each language. If V ≈ 0 under that condition, the artifact hypothesis is strongly supported.

Quality preservation proxy: within each language, median retained PPL under adaptive thresholds must not exceed global-threshold median by >5%. This is computable from existing Parquet data.

**Key Points:**
- Explicit falsification: ΔV < 0.05 across all k OR bootstrap CIs include 0 → hypothesis rejected
- Add CCNet-tercile negative control (per-language lowest tercile) — expect V ≈ 0
- Quality preservation check: adaptive retained PPL median ≤ global median + 5% per language

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion) — Second Appearance:

We have reached a fully crystallized experimental design. Let me consolidate the final four-condition experiment and close the discussion with the complete hypothesis statement.

**Final Experimental Design (4 conditions):**
1. **Global k-th percentile** (baseline — reproduces h-m1 implementation): Single threshold across all languages. Expected Cramér's V = 0.29–0.41 (known from h-m1).
2. **Per-language k-th percentile** (primary intervention): `df.groupby('language')['ccnet_perplexity'].transform('quantile', k/100)`. Primary test.
3. **Iso-retention per-language z-score** (disambiguation): Retain z_l ≤ z* (z* chosen iso-retention to match global k). Tests whether effect is scale vs. shape.
4. **CCNet-consistent tercile** (negative control): Within-language lowest tercile selection. Should produce V ≈ 0 (per CCNet design intent).

**Permutation control:** Randomize language labels → all conditions should show V → 0.

**The hypothesis in its final form:** On the RedPajama-V2 sample subset (208,263 documents, 5 languages: en/de/fr/es/it), per-language k-th percentile thresholding of pre-computed `ccnet_perplexity` scores reduces language-group retention disparity (Cramér's V) relative to the global k-th percentile baseline by ΔCramér's V ≥ 0.10 for ≥3 of 5 k values ∈ {10, 20, 30, 40, 50}, with bootstrap 95% CI on ΔCramér's V excluding zero. Secondary: this reduction is not fully explained by iso-retention z-score normalization (|ΔV_percentile - ΔV_zscore| > 0.02 for ≥2/5 k), indicating distributional shape differences across languages contribute to the bias.

**Feasibility confirmed:** All four conditions are computable from static Parquet files with pandas/scipy in ~100 lines. No GPU, no API, no inference. Bootstrap CI ~1000 resamples on 208,263-row DataFrame is <60 seconds CPU.

The discussion has converged. All six criteria are met: SPECIFIC (exact ΔV threshold, k range, n conditions), MECHANISM (threshold-calibration artifact + shape vs. scale disambiguation), PREDICTIONS (ΔV ≥ 0.1 for ≥3/5 k; shape vs. scale test; V → 0 under permutation), NOVELTY (first measurement of practitioner global-threshold misuse effect on RedPajama-V2), FEASIBILITY (confirmed), OBJECTIONS (all addressed with negative controls, permutation, proxy quality check).

**Key Points:**
- Final 4-condition design: global percentile (baseline), per-language percentile (primary), iso-retention z-score (disambiguation), CCNet-tercile (negative control)
- Permutation control validates metric
- Complete hypothesis statement ready for Phase 2B

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master) — Third Appearance:

The design is tight, but three remaining gaps.

**Gap 1: Practical effect size.** ΔCramér's V ≥ 0.10 on 200k samples is statistically almost guaranteed. Pre-specify a practical effect: max–min language retention gap reduced by ≥15 percentage points at k=30. English at 3.7% retention moving to 18%+ is operationally massive; 36% to 41% is cosmetic. Cramér's V reduction alone doesn't tell you which case you're in.

**Gap 2: Quality preservation proxy.** Median PPL is tautological under percentile control (by definition, adaptive threshold retains the k-th percentile within each language, so median retained PPL = language k-th percentile). Instead: compare 90th percentile PPL among retained documents within each language before/after adaptive thresholding. If 90th percentile PPL increases substantially (>10%), quality dilution is occurring — you're retaining high-PPL documents you wouldn't have retained under global threshold.

**Gap 3: Distributional diagnostics.** Pre-register: compute skewness, kurtosis, and unimodality (Hartigan's dip test) per language. If distributions are strongly non-Gaussian (skew > 2), z-score is *expected* to underperform percentile — that makes the shape-vs-scale test interpretable rather than post hoc.

With these additions, the hypothesis becomes operationally grounded, not just statistically tidy.

**Key Points:**
- Add practical effect size criterion: ≥15pp reduction in max–min retention gap at k=30
- Replace median PPL with 90th percentile PPL retention check (non-tautological quality proxy)
- Pre-register distributional diagnostics (skewness, kurtosis, dip test) per language before running thresholding experiments

---

### Exchange 13

🎯 **Dr. Sage** (Research Impact Evaluator) — Third Appearance:

Prof. Rex's additions are right and all three are feasible on static Parquet. Let me make the final impact case and close.

The practical effect criterion (≥15pp reduction in max–min retention gap at k=30) is the right anchor because it translates the statistical result into operational terms practitioners can act on. If English retention moves from 3.7% to 18%+ at k=30, a practitioner using global thresholding on RedPajama-V2 is materially misrepresenting what fraction of English-language web text their model is exposed to. That is a dataset documentation gap, and our measurement closes it.

The distributional diagnostics (skewness, kurtosis, dip test per language) are ~10 lines of scipy and answer the fundamental question of whether perplexity scores are cross-linguistically commensurable. Jansen et al. [2022] show that harmful-content perplexity distributions exhibit bimodal clustering that standard thresholds exploit by happenstance — the analogous insight here is that CCNet perplexity distributions may exhibit language-specific tail structures that global percentiles cannot handle. Pre-registering the diagnostic condition makes the shape-vs-scale comparison interpretable: if German shows skew > 2 while Italian doesn't, we can predict differential behavior of the z-score condition.

On the 90th-percentile PPL quality check: this is an elegant falsifier. If adaptive thresholding increases 90th-percentile retained PPL within a language by >10%, we have evidence that the equity gain comes at the cost of admitting a tail of lower-quality documents. That would motivate hybrid approaches (per-language percentile with within-language tail trimming).

Everything required is in the existing Parquet data. The hypothesis is complete, rigorous, and publishable at DATA-FM / similar venues. I close my assessment: STRONG CONFIDENCE.

**Key Points:**
- Practical effect size (≥15pp retention gap reduction) translates statistics to operations — this is the publishable claim
- 90th-percentile PPL check is the falsifier for quality dilution — feasible from Parquet
- Distributional diagnostics pre-registered → shape-vs-scale test is interpretable, not post hoc
- Discussion converged — all criteria satisfied

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect) — Fourth Appearance:

The proposal is now close to scientifically defensible. The causal claim must be precise: **global thresholding introduces spurious association between language and retention due to cross-language scale and shape heterogeneity in PPL distributions.**

Pre-register both success AND failure criteria: Success = ≥15pp max–min retention gap reduction at k=30 AND V ≤ 0.10. Failure = gap remains >10pp AND V ≥ 0.20. Precision in both directions prevents post hoc interpretation.

Additional diagnostic: stratify by document length deciles before computing retention rates. Because PPL is averaged per token, shorter documents exhibit higher PPL variance. If adaptive thresholding disproportionately admits short documents in certain languages, the equity gain may be a length artifact. Compute Cramér's V within length strata and aggregate (Mantel-Haenszel-style weighting). If dependence disappears only without stratification, hypothesis is weakened.

**Key Points:**
- Pre-register both success (V ≤ 0.10, ≥15pp gap) and failure (V ≥ 0.20, >10pp gap) bounds
- Add length-stratified Cramér's V as doc-length confound check
- Permutation + bootstrap controls confirm metric stability

---

### Exchange 15

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion) — Final Consolidation:

This is the moment to lock the final hypothesis. Every concern has been addressed. The design is rigorous, feasible, and publishable. Here is the definitive consolidated statement.

**Hypothesis h-m1-v2: Language-Adaptive Perplexity Threshold Equity**

*Scope:* RedPajama-V2 CommonCrawl quality signal metadata (208,263-document sample, 5 languages: en/de/fr/es/it), pre-computed `ccnet_perplexity` scores (static Parquet files).

*Core Claim:* When practitioners apply a global k-th percentile threshold to pre-computed CCNet perplexity scores, they induce measurable language-group retention disparity (Cramér's V = 0.29–0.41, from h-m1). Per-language k-th percentile thresholding reduces this disparity by ΔCramér's V ≥ 0.10 and reduces the max–min per-language retention gap by ≥15 percentage points at k=30, with bootstrap 95% CI on ΔCramér's V excluding zero for ≥3 of 5 k values. This reflects a threshold-calibration artifact in practitioner reuse of language-aware quality scores with language-agnostic decision boundaries.

*Mechanism:* Cross-language heterogeneity in ccnet_perplexity distributions (different scale AND shape, due to per-language KenLM training on Wikipedia and language-specific SentencePiece tokenization) causes global percentile thresholds to systematically over-exclude high-perplexity languages (English) and under-exclude low-perplexity languages (Italian). Per-language percentile calibration removes the scale+shape confound.

*Four conditions:* (1) Global k-th percentile [baseline], (2) Per-language k-th percentile [primary], (3) Iso-retention per-language z-score [scale-vs-shape disambiguation], (4) CCNet-consistent per-language tercile [negative control, expect V ≈ 0].

*Pre-registered criteria:* SUCCESS = ΔV ≥ 0.10 for ≥3/5 k AND max–min gap reduction ≥15pp at k=30 AND bootstrap CI excludes 0. FAILURE = gap remains >10pp AND V ≥ 0.20. QUALITY CHECK = 90th-percentile retained PPL per language increase ≤10%. PERMUTATION = V → 0 under permuted labels for all conditions.

*Novelty:* First direct measurement of practitioner global-threshold reuse effect on RedPajama-V2 perplexity signals; first diagnostic comparing percentile vs. z-score calibration for multilingual corpus equity; extends Turki et al. [2026] retention-rate-tuning principle from classifiers to perplexity filtering.

The discussion has fully converged. All 6 convergence criteria are satisfied.

**Key Points:**
- Complete 4-condition experiment: global (baseline), per-language percentile (primary), iso-retention z-score (disambiguation), CCNet-tercile (negative control)
- All pre-registration criteria defined: success, failure, quality, permutation
- Hypothesis h-m1-v2 is ready for Phase 2B planning

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis identifies a genuine and previously unmeasured gap: practitioner reuse of language-aware perplexity scores (CCNet/RedPajama-V2) with language-agnostic thresholds induces cross-language selection disparity. The four-condition design (including iso-retention z-score as disambiguation arm) provides novel mechanistic decomposition of whether the bias is scale-driven or shape-driven — an insight that extends beyond CCNet to any language-specific quality score reused out of context. The connection to Turki et al. [2026] classifier-based retention tuning provides the natural prior that makes this finding generalizable.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Both success and failure criteria are pre-registered with quantitative bounds (ΔV ≥ 0.10, ≥15pp gap reduction, bootstrap CI excludes 0 for success; V ≥ 0.20, gap >10pp for failure). Permutation control validates metric stability. Length-stratified Cramér's V guards against doc-length confound. The CCNet-tercile negative control provides the strongest possible internal validity check — per-language terciles should yield V ≈ 0, directly confirming the artifact hypothesis.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** The real-world significance is clear: RedPajama-V2 is explicitly designed for practitioner filtering using its 46 quality signals, and `ccnet_perplexity` is the most widely understood. If global thresholding on these scores induces V = 0.29–0.41 disparity (4x the desired ≤0.10), practitioners are systematically misrepresenting multilingual corpus composition. The 90th-percentile PPL quality proxy and practical ≥15pp gap criterion translate the finding into actionable guidance. Publishable at DATA-FM Workshop / similar data-curation venues.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Full feasibility confirmed. All four conditions computable from static RedPajama-V2 Parquet files (208,263 rows). Core implementation: pandas groupby + scipy.stats + bootstrap CI. Additional checks (90th-pct PPL, skewness/kurtosis, Hartigan's dip, Mantel-Haenszel length stratification) are all scipy/numpy operations on the same DataFrame. Total implementation: ~150 lines Python, <60 seconds CPU execution. No GPU, no API, no model inference required.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on hypothesis **h-m1-v2: Language-Adaptive Perplexity Threshold Equity**. The core claim is: when practitioners apply a global k-th percentile threshold to pre-computed CCNet perplexity scores from RedPajama-V2 (as in h-m1), they introduce spurious language-group retention disparity (Cramér's V = 0.29–0.41) because cross-language perplexity distributions differ in scale AND shape. Per-language k-th percentile thresholding removes the scale+shape confound and reduces this disparity by ΔCramér's V ≥ 0.10 for ≥3 of 5 k values, with max–min retention gap reduction ≥15pp at k=30.

The four-condition experimental design is: (1) global k-th percentile [baseline], (2) per-language k-th percentile [primary], (3) iso-retention per-language z-score [scale-vs-shape disambiguation], (4) CCNet-consistent per-language tercile [negative control]. Permutation control, bootstrap CIs, 90th-percentile PPL quality proxy, distributional diagnostics (skewness, kurtosis, dip test), and length-stratified Cramér's V (Mantel-Haenszel) complete the validation framework.

The hypothesis builds on confirmed h-m1 findings (pipeline valid, Cramér's V = 0.29–0.41, English exclusion direction confirmed) while correcting the direction inversion: h-m1 confirmed the disparity exists; h-m1-v2 tests whether per-language calibration fixes it. The mechanism — threshold calibration artifact, not LM training artifact — is the new claim. The z-score arm provides mechanistic disambiguation within the same experiment. All data exists as static files. Implementation is ~150 lines of pandas/scipy. Novelty is confirmed: no prior paper measures ΔCramér's V under global vs. per-language perplexity thresholds on any corpus.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Length confound: even with Mantel-Haenszel stratification, doc-length effects on PPL may not be fully separable. If length distributions differ across languages, partial confounding is possible.
- Sample scope: results are on 208,263-document sample, not full RedPajama-V2 (113.3B docs). Generalization to full corpus requires explicit disclaimer.
- Z-score condition assumes finite variance: if any language exhibits infinite-variance tail behavior (extremely heavy tail), iso-retention z-score formulation breaks down.
- **Mitigation Strategy:** Document all three as limitations in Phase 6 paper. Scope claim to sample subset explicitly. Pre-register the condition for z-score breakdown (heavy tail defined as kurtosis > 10 → report z-score results with caveat for that language). Length confound addressed by reporting within-stratum Cramér's V separately.

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Vera raises a critical factual correction that we must resolve before anything else — but I believe the resolution actually *strengthens* the feasibility case. Let me work through this carefully using what we know from both CCNet [Wenzek et al., 2019] and Jansen et al. [Perplexed by Quality, 2022].

Prof. Vera is correct that CCNet's *original design* uses per-language tercile splits computed from within-language perplexity distributions (`cutoff.csv` has per-language rows). However, the key insight from h-m1 is that the RedPajama-V2 Parquet quality signals store pre-computed `ccnet_perplexity` scores — and h-m1's global threshold experiment applied a SINGLE k-th percentile across ALL languages on the pre-computed scores. This is methodologically equivalent to: "use the distribution of ALL documents' perplexity scores, compute the k-th percentile globally, and filter." That IS a global threshold baseline — not the original CCNet design. The comparison is valid: global-percentile (h-m1 implementation) vs. per-language-percentile (proposed h-m1-v2 implementation) on the same 208,263-row RedPajama-V2 sample.

From a feasibility standpoint, this is straightforwardly implementable on the existing data. Jansen et al. [2022] show that KenLM-based perplexity distributions for web text exhibit heavy tails and differ substantially across document types (Figure 1, Figure 2 in their paper — harmful vs. clean OSCAR distributions show bimodal clustering at certain perplexity values). This is crucial: it means the *shape* of perplexity distributions likely differs not just in scale but in skew across languages. Percentile matching handles scale differences well but may not fully equalize highly non-Gaussian shapes. Prof. Vera's concern about z-normalization vs. percentile choice is valid here — we should run z-scored perplexity as a secondary condition.

On the downstream quality concern: Prof. Vera's point is noted, but it's out of scope for this hypothesis given our compute constraints. We're testing EQUITY (Cramér's V) on STATIC data. No BERT/fastText evaluation is feasible without GPU. The feasibility-correct scope is: (1) compute adaptive threshold, (2) measure Cramér's V before/after, (3) bootstrap CI on ΔCramér's V. That's approximately 50 lines of pandas/scipy on data we already have. The downstream quality question is a limitation to document, not a gate to pass.

On Prof. Vera's permutation control suggestion: this is excellent AND feasible with static data. Randomly permute `language` labels → recompute Cramér's V under global and adaptive threshold → if Cramér's V drops under adaptive even under permutation, the metric is indeed unreliable. This is a 5-line addition. We should include it.

**Key Points:**
- The global-threshold baseline from h-m1 IS a valid baseline — it applied single cross-language percentile to pre-computed CCNet scores in RedPajama-V2 Parquet
- Full feasibility confirmed: pandas groupby + scipy + bootstrap CI, ~50 lines, CPU-only, static Parquet
- Add permutation control (Prof. Vera's suggestion) as 5-line addition — strongly supports rigor
- Downstream quality evaluation is out of scope given CPU constraint — document as limitation

---

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

The gap we're addressing here is genuinely elegant in its simplicity — and that's what makes it novel. Every paper in our briefing package acknowledges that CCNet's per-language KenLM models address WHAT gets scored, but nobody has tested whether the CUTOFF itself needs per-language calibration. Wenzek et al. [CCNet, 2019] established the pipeline: train one KenLM per language on Wikipedia, then apply global percentile bucket boundaries from `cutoff.csv`. The asymmetry is striking: the scoring model is language-aware, but the decision boundary is language-agnostic. That's the bug.

What makes this an interesting hypothesis is that h-m1 didn't just confirm the disparity — it showed us the direction. English has higher perplexity in CommonCrawl web text because English web text is noisier (more diverse domains, more informal language, more code-switching) relative to what Wikipedia-trained KenLM expects. Italian web text is more homogeneous in register. So when you apply a single global k-th percentile cutoff, you're applying an English-shaped distribution threshold to Italian documents — of course Italian documents get preferentially retained.

The hypothesis I want to propose is this: **if we compute the k-th percentile WITHIN each language's perplexity distribution and use that as the cutoff for that language's documents, the Cramér's V should drop substantially**. Mechanistically, this works because we're now comparing each document to its language-specific distribution rather than to a cross-language aggregate. The prediction is that ΔCramér's V ≥ 0.1 for ≥3 of 5 k values, with English retention rising from 3.7%–36.5% toward 40%+.

Three angles that make this scientifically interesting beyond just "fix the bug":
1. **Diagnostic angle**: If adaptive threshold reduces Cramér's V to ≤0.10, we've confirmed the bias is a *calibration artifact* (threshold, not LM). If it doesn't fully resolve, we need to look at whether the per-language KenLM perplexity scales are commensurable.
2. **Generalization angle**: Turki et al. [2026] showed retention rate tuning is necessary for multilingual quality classifiers, but used classifier scores. We're showing the same principle applies to perplexity-based filtering — and with a simpler fix.
3. **Counter-intuitive angle**: The "adaptive" approach may actually increase total corpus size or shift what gets included in ways that affect downstream LLM performance — but we're testing equity first, not quality.

**Key Points:**
- Core novelty: separating language-aware SCORING from language-aware THRESHOLDING for the first time
- CCNet's cutoff.csv is the specific artifact we're testing a fix for
- h-m1 gives us the exact baseline (Cramér's V = 0.29–0.41) and the English exclusion magnitude to beat

---

