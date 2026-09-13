---
hypothesis_id: H-GeomRoute-v1
confidence_level: 0.78
total_hypothesis_count: 5
research_mode: incremental
date: 2026-05-13
stepsCompleted:
  - step-00-init-environment
  - step-01-init-parsing
  - step-02-input-hypothesis
  - step-03-hypothesis-generation
  - step-04-hypothesis-inventory
  - step-05-risk-analysis
  - step-06-dependency-graph
  - step-07-timeline-planning
  - step-08-dialectical-analysis
  - step-09-summary
  - step-10-finalize
status: complete
completedAt: 2026-05-13T02:10:00Z
---

# Verification Plan: Geometry-Governed Contamination Detection — Three-Zone Phase Diagram

**Date:** 2026-05-13
**Hypothesis ID:** H-GeomRoute-v1
**Confidence:** 0.78
**Total Hypotheses:** 5 (H-E1, H-M1, H-M2, H-M3, H-M4)
**Research Mode:** Incremental (Phase 2A available)
**Scope Reduction:** 50% (4 BUILD_ON claims skipped; 3 PROVE_NEW claims drive this plan)

---

## Section 0: Established Facts & Scope Reduction

### 0.1 Established Facts Registry (BUILD_ON — Do Not Re-Verify)

| Claim | Evidence | Status |
|-------|----------|--------|
| N-gram overlap (13-gram) detects exact lexical contamination; used in EleutherAI/lm-eval-harness production | GPT-3 Appendix C; EleutherAI lm-eval-harness 12K★ pipeline | BUILD_ON |
| Min-K% Prob and Min-K%++ are established MIA-based detectors with published code | Shi et al. 2023 [2310.16789] 368 citations; zjysteven/mink-plus-plus ICLR'25 Spotlight | BUILD_ON |
| DC-PDD outperforms Min-K% Prob on its own evaluation setup | Zhang et al. 2024 [2409.14781] 60 citations | BUILD_ON |
| MIA-based methods can perform at random guessing under realistic conditions | Fu et al. 2024 [2410.18966] — 50-paper review | BUILD_ON |

### 0.2 Claims Requiring Verification (PROVE_NEW)

| Claim | Evidence Gap | Drives Hypothesis |
|-------|-------------|-------------------|
| No unified head-to-head comparison across all three paradigms on the same benchmarks/corpora exists | Xu et al. 2024 survey [2406.04244] identifies as open problem | H-E1 (existence of separable comparison) |
| Corpus geometry predicts detector ordering — three-zone phase diagram separability | Novel hypothesis — no prior work tests geometry-based detector routing | H-M1, H-M2, H-M3 |
| An indeterminate detection zone exists where no current detector dominates | Inferred from Singh et al. 2024 inconsistent signals; Fu et al. random-guessing result | H-M4, H-E1 |

**Scope Reduction:** 50% (4 of 7 claims are BUILD_ON — these are cited as pre-validated baselines with no dedicated experiment arms)

### 0.3 Phase 2B-4 Instructions

BUILD_ON claims (n-gram baseline, MIA existence, DC-PDD advantage) are cited as established baselines without re-verification experiments. PROVE_NEW claims (geometry-routing separability, three-zone diagram, indeterminate zone) require dedicated experiment arms. Sub-hypotheses below address exclusively the PROVE_NEW claims.

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

**H-GeomRoute-v1:** Under the setting of contamination detection for FM evaluation benchmarks (MMLU, HellaSwag, GSM8K) against real pretraining corpora (The Pile, C4, RedPajama) using open-weight models (Llama-2-7B, Mistral-7B, Pythia-7B), if corpus-side geometric signals (max 13-gram overlap count and embedding cosine similarity to nearest corpus neighbor via frozen SBERT) are used to classify benchmark items into contamination geometry strata, then a logistic regression routing rule trained on one corpus will predict the top-performing detector family (from: n-gram, embedding, Min-K%++, DC-PDD, ConStat) with cross-corpus top-1 accuracy > 40% and Kendall's τ > simulation-calibrated threshold on determinate items (margin ≥ 0.05 F1 gap under bootstrap), because contamination detection methods operate on fundamentally different signal types whose efficacy is structurally determined by which corpus overlap geometry dominates in each benchmark-corpus pair.

### 1.2 Alternative Hypothesis (H0)

Corpus-side geometric signals (13-gram overlap, embedding cosine similarity) are not sufficient to predict detector ordering above chance (top-1 accuracy ≤ 40% cross-corpus, τ ≤ simulation-calibrated threshold), indicating that contamination detection performance is not structurally determined by contamination geometry — i.e., method choice does not interact with overlap regime in a learnable, transferable way.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | MMLU + HellaSwag + GSM8K (test splits) × The Pile + C4 + RedPajama (standard) | Covers three reasoning modalities (knowledge, commonsense, math) × three corpus families (curated/web/deduplicated). 9 benchmark-corpus pairs; ~25K total benchmark items tractable (~48 GPU-hours). |
| **Model** | Llama-2-7B, Mistral-7B, Pythia-7B (open-weight LLM, decoder-only) | White-box access required for per-token log probabilities (Min-K%++, DC-PDD). Three models provide cross-model robustness check. Pythia trained on The Pile provides known-corpus case. |

**Dataset Details:**
- Source: HuggingFace datasets (benchmarks); EleutherAI/pile, allenai/c4, togethercomputer/RedPajama-Data-1T (corpora)
- Path: Public — downloadable via HuggingFace hub

**Model Details:**
- Type: Open-weight LLM (decoder-only, autoregressive)
- Source: HuggingFace model hub (all publicly available)

### 1.4 Baseline Methods

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|-----------------|
| Min-K% Prob [Shi et al. 2023] | 7.4% improvement over prior MIA on WikiMIA; 368 citations | WikiMIA benchmark | Single dataset, no cross-paradigm comparison, no geometry stratum analysis |
| DC-PDD [Zhang et al. 2024] | Outperforms Min-K% Prob on its own evaluation; 60 citations | Internal benchmark | Evaluated in isolation; reference model dependency not controlled; no cross-corpus threshold transfer test |
| ConTAM [Singh et al. 2024] | 13 benchmarks × 7 models; longest contaminated substring most informative | Multi-benchmark | Shows inconsistent signals but does not explain why; no geometry-based decomposition |
| LLMSanitize [ntunlp] | Multi-method library; pip-installable; closest to unified framework | Various | Aggregates methods but does not compare systematically or provide routing logic |

**Best Baseline Performance:** DC-PDD [Zhang et al. 2024] is current SOTA for token-level MIA detection. Min-K%++ [ICLR'25] is SOTA for black-box-adjacent MIA. N-gram (EleutherAI) is production SOTA for lexical decontamination.

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Corpus-side geometric signals (13-gram overlap, SBERT cosine similarity) are measurable proxies for contamination type | Yang et al. [2023] verified 8-18% HumanEval in RedPajama; EleutherAI lm-eval-harness uses 13-gram in production | Ground truth labels become unreliable; precision/recall reflects corpus overlap noise |
| A2 | Detector performance differences between top-1 and top-2 families are ≥ 0.05 F1 margin on > 50% of items | Fu et al. [2024] documents clear gaps; Singh et al. [2024] shows variation | Indeterminacy rate > 50%; routing utility limited; hypothesis scope must narrow |
| A3 | Geometric feature distribution has sufficient overlap across The Pile, C4, RedPajama (low MMD or resolvable via importance weighting) | All three corpora contain web-scraped text with similar domain distributions | Cross-corpus routing degrades after importance weighting; geometry claim becomes corpus-local |
| A4 | Fixed DC-PDD reference model provides stable calibration baseline across all three corpora | Zhang et al. [2024] uses fixed reference in original experiments | DC-PDD performance varies by ≥ 0.10 AUROC across corpora; DC-PDD arm must be analyzed separately |
| A5 | Simulated leakage injection protocol (Hidayat et al. 2025, three regimes) captures relevant contamination geometry space | Hidayat et al. [2025, 2505.24263] demonstrated controlled leakage on MMLU+HellaSwag | Phase structure stability (Kendall's τ) varies dramatically across injection regimes; findings are injection-mechanism-specific |

### 1.6 Research Gap & Novelty

**Gap:** No systematic multi-method, multi-benchmark contamination detection comparison exists. Singh et al. [2024] observe inconsistent signals across methods without explaining why. LLMSanitize aggregates without routing. No prior work uses corpus-side geometry to predict detector performance ordering.

**Novelty:**
- First systematic empirical test of whether contamination detection decomposes structurally across geometry regimes
- First proposal and validation of a geometry-aware routing rule for detector selection
- First characterization of the indeterminate detection zone as a structural blind spot — explains Singh et al.'s inconsistency finding at the mechanistic level

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | MECHANISM | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Contamination Geometry Decomposition Exists

**Type:** EXISTENCE
**Statement:** Under contamination detection for MMLU/HellaSwag/GSM8K against The Pile/C4/RedPajama using open-weight models, if corpus-side geometric signals (max 13-gram overlap count, SBERT cosine similarity) are used to define geometry strata, then n-gram detectors will exhibit recall ≥ 0.80 in the lexical stratum and ≤ 0.40 in the semantic stratum, and Min-K%++ F1 variance across three corpora will be ≥ 0.15, because detector families operate on orthogonal signal types that align with different corpus overlap regimes.

**Rationale:** This is the foundational existence claim: if geometry strata do not separate detector performance, the entire routing hypothesis collapses. Establishing that n-gram detectors strongly outperform in lexical regimes while failing in semantic regimes directly validates the core structural premise. The indeterminacy rate finding (10–50%) is also a primary structural contribution independent of routing accuracy.

**Variables (from Phase 2A):**
- Independent: Contamination Geometry Stratum (lexical/semantic/indeterminate defined by 13-gram top-quartile and SBERT cosine threshold)
- Dependent: N-gram detector recall by stratum; Min-K%++ F1 variance across corpora; Indeterminacy Rate
- Controlled: Equal-prevalence subsampling (10%); fixed DC-PDD reference; frozen SBERT encoder

**Verification Protocol (5 steps):**
1. Build 13-gram inverted index (EleutherAI pipeline) and FAISS SBERT embedding index for The Pile, C4, RedPajama.
2. Compute geometry features (max 13-gram count, max SBERT cosine) for all ~25K benchmark items across 3 corpora; define strata using top-quartile thresholds.
3. Apply all 5 detector families (n-gram, embedding, Min-K%++, DC-PDD, ConStat) to Approach A (known inclusion audit) and Approach B (simulated leakage, 3 injection regimes) labeled items.
4. Compute per-stratum recall/F1 with bootstrap 95% CIs (N=10,000); compute indeterminacy rate across all items; compute Min-K%++ F1 variance across 3 corpora.
5. Generate 2D contamination phase diagram (13-gram × cosine) colored by dominant detector family; report indeterminacy rate as primary structural outcome.

**Success Criteria (PoC — Direction-based):**
- Primary: N-gram recall ≥ 0.80 in lexical stratum AND ≤ 0.40 in semantic stratum
- Secondary: Min-K%++ F1 variance ≥ 0.15 across The Pile/C4/RedPajama for MMLU or HellaSwag
- Tertiary: Indeterminacy rate in [10%, 50%] — blind spot confirmed but routing remains useful

**Failure Response:**
- IF fails (n-gram recall ≥ 0.60 in semantic stratum OR Min-K%++ variance < 0.10): STOP — H-GeomRoute-v1 does not hold; indeterminate zone finding still reportable as negative result

**Dependencies:** None (foundation)
**Source:** Phase 2A Section 1.6 Prediction P2; Section 5 SH1_existence

---

#### H-M1: Corpus-Side Geometry Determines Stratum (Feature Orthogonality)

**Type:** MECHANISM
**Statement:** Under the same experimental setting, if 13-gram overlap count and SBERT cosine similarity are computed for all benchmark items across all three corpora, then Pearson correlation r(13-gram, cosine) ≤ 0.8, because these two signals capture orthogonal aspects of corpus overlap (exact lexical matching vs. semantic proximity) that are by construction independent feature spaces.

**Rationale:** This tests whether the two geometry features are genuinely orthogonal — a prerequisite for meaningful stratum decomposition. If r > 0.8, the lexical and semantic strata collapse, making the three-zone diagram degenerate. This is a fast, inexpensive verification that validates the feature engineering foundation.

**Variables:**
- Independent: 13-gram overlap count; SBERT cosine similarity (both corpus-side)
- Dependent: Pearson r and Spearman ρ between features across all 25K items
- Controlled: Frozen SBERT encoder; same corpus index for both features

**Verification Protocol (3 steps):**
1. Compute max 13-gram count (inverted index) and max SBERT cosine similarity (FAISS) for all ~25K benchmark items × 3 corpora.
2. Compute Pearson r and Spearman ρ between the two feature vectors; report per-corpus and pooled correlation.
3. If r ≤ 0.8 in all corpora: strata are genuinely separable; if r > 0.8: geometry decomposition is trivial and H-M2+ cannot proceed.

**Success Criteria:**
- Primary: Pearson r(13-gram, cosine) ≤ 0.8 in all three corpora (pooled and per-corpus)
- Secondary: Spearman ρ ≤ 0.8 as robustness check

**Failure Response:**
- IF fails (r > 0.8): PIVOT — investigate whether a single geometry dimension suffices for two-zone (not three-zone) routing; report as scope limitation

**Dependencies:** H-E1
**Source:** Phase 2A Section 1.3 Causal Step 1; Falsifier: "if r > 0.8, strata collapse"

---

#### H-M2: Detector Sensitivity Aligns with Signal Type

**Type:** MECHANISM
**Statement:** Under the experimental setting, if detector families are applied to items stratified by geometry stratum, then Min-K%++ will exhibit lower F1 in the semantic stratum (SBERT-dominant, low 13-gram) than in the lexical stratum, and its F1 variance across The Pile/C4/RedPajama for the same benchmark will be ≥ 0.15, because MIA-based detectors rely on memorization likelihood signals that are absent when contamination is purely semantic/paraphrastic.

**Rationale:** Validates that detector failure modes are geometry-contingent, not random. Min-K%++ is chosen as the test case because its mechanism (min-k% token log probabilities) is theoretically sensitive to exact memorization rather than paraphrased overlap — making it the cleanest test of signal-type alignment. If Min-K%++ performs uniformly across strata, the mechanism hypothesis breaks.

**Variables:**
- Independent: Contamination Geometry Stratum (from H-E1 stratification)
- Dependent: Min-K%++ F1 by stratum; Min-K%++ F1 variance across 3 corpora for same benchmark
- Controlled: Same model checkpoints (Llama-2-7B, Mistral-7B, Pythia-7B); same labeled items as H-E1

**Verification Protocol (4 steps):**
1. Using stratification from H-E1, compute Min-K%++ F1 separately for lexical, semantic, and indeterminate strata across Approach A and B items.
2. Compute Min-K%++ F1 variance across The Pile, C4, RedPajama for MMLU and HellaSwag.
3. Compute bootstrap 95% CIs for all F1 estimates; report stratum-by-stratum comparison with effect size (Cohen's d).
4. Check Kendall's τ of Min-K%++ F1 ranking across 3 injection regimes (Approach B) — high τ indicates geometry-stable failure mode.

**Success Criteria:**
- Primary: Min-K%++ F1 significantly lower (p < 0.05, bootstrap) in semantic stratum vs. lexical stratum
- Secondary: Min-K%++ F1 variance ≥ 0.15 across 3 corpora for MMLU or HellaSwag

**Failure Response:**
- IF fails (Min-K%++ F1 ≥ 0.60 in semantic stratum): EXPLORE — test whether DC-PDD or embedding detector shows stratum-sensitivity; document as detector-specific finding rather than geometry-general mechanism

**Dependencies:** H-M1
**Source:** Phase 2A Section 1.3 Causal Step 2; Section 1.6 Prediction P2

---

#### H-M3: Geometry Creates Learnable Detector Dominance Regions

**Type:** MECHANISM
**Statement:** Under the experimental setting, if a logistic regression routing classifier is trained on corpus-side geometry features (13-gram count, SBERT cosine) from The Pile to predict the top-performing detector family, then it will achieve cross-corpus top-1 accuracy > 40% and Kendall's τ > simulation-calibrated threshold on determinate items (F1 margin ≥ 0.05) when evaluated on C4 and RedPajama, because geometry separability from H-E1 and signal-type alignment from H-M2 together create learnable dominance regions in 2D geometry space.

**Rationale:** This is the central operationalization of the routing hypothesis — converting the structural observations (H-E1, H-M1, H-M2) into a learnable prediction task. The 40% threshold is benchmarked against chance (25% for 4 families). The simulation-calibrated threshold from Hidayat synthetic surfaces provides a data-driven rather than arbitrary falsification criterion.

**Variables:**
- Independent: Corpus-side geometry features (max 13-gram count, SBERT cosine) — training corpus: The Pile
- Dependent: Cross-corpus top-1 routing accuracy on C4 and RedPajama; Kendall's τ of predicted vs. actual detector ordering
- Controlled: Logistic regression with L2 regularization; 5-fold CV on The Pile for hyperparameter selection; strict train/test corpus split

**Verification Protocol (5 steps):**
1. From The Pile labeled determinate items (margin ≥ 0.05 from H-E1), train multinomial logistic regression on (max 13-gram count, SBERT cosine) → top detector family label.
2. Derive simulation-calibrated Kendall's τ threshold from Hidayat et al. synthetic separability surfaces (pre-registered before analysis).
3. Evaluate classifier on C4 and RedPajama determinate items: compute top-1 accuracy and Kendall's τ.
4. Pre-registered ablation: remove DC-PDD arm from routing target, retrain, and measure accuracy change.
5. Pre-registered ablation: 70% corpus proxy stress test — repeat evaluation using 70% random subsample of each corpus index; check if routing accuracy drops ≥ 0.10.

**Success Criteria:**
- Primary: Top-1 accuracy > 40% AND Kendall's τ > simulation-calibrated threshold on determinate items (C4 + RedPajama)
- Secondary: DC-PDD ablation accuracy drop < 0.05 — routing robust to removal of one detector arm

**Failure Response:**
- IF fails (accuracy ≤ 40% after importance weighting): PIVOT — reduce scope to "geometry governs detection in easy/lexical regimes only"; report as partial negative result with indeterminate zone as primary finding

**Dependencies:** H-M2
**Source:** Phase 2A Section 1.3 Causal Step 3; Section 1.6 Prediction P1

---

#### H-M4: Logistic Regression Routing Generalizes Cross-Corpus

**Type:** MECHANISM
**Statement:** Under the experimental setting, the logistic regression routing classifier from H-M3 will show routing accuracy drop < 0.10 after MMD-based importance weighting for covariate shift (The Pile → C4/RedPajama), and MMD computation will not reveal fully disjoint feature support, because corpus-side geometry features (13-gram overlap patterns, SBERT cosine similarity to common web text) are corpus-agnostic properties of benchmark item content rather than corpus-specific artifacts.

**Rationale:** Cross-corpus generalization is the key practical claim — without it, the routing rule is corpus-local and cannot be deployed in new settings. The MMD + importance weighting protocol provides a principled test of whether feature distribution shift explains any accuracy degradation. This step also validates whether the geometry features are fundamental properties of benchmark items or artifacts of specific corpus characteristics.

**Variables:**
- Independent: Source corpus (The Pile, training) vs. target corpus (C4, RedPajama, evaluation)
- Dependent: Routing accuracy before vs. after importance weighting; MMD between feature distributions; Threshold-Transfer Stability (|ΔFPR| ≤ 0.03, |ΔFNR| ≤ 0.05 for n-gram methods)
- Controlled: Same logistic regression from H-M3; same geometry features; same labeled items

**Verification Protocol (4 steps):**
1. Compute MMD between The Pile geometry features and C4/RedPajama geometry features using Gaussian kernel.
2. If MMD significant (p < 0.05): derive importance weights via kernel density ratio estimation; reweight training distribution.
3. Re-evaluate routing accuracy after importance weighting; compute accuracy difference (pre vs. post weighting).
4. For n-gram methods: apply fixed-FPR=5% threshold (learned on The Pile) unchanged to C4 and RedPajama; compute |ΔFPR| and |ΔFNR|.

**Success Criteria:**
- Primary: Routing accuracy drop < 0.10 after importance weighting (MMD-corrected evaluation)
- Secondary: MMD does not indicate fully disjoint feature support (overlap exists between corpora)
- Tertiary: |ΔFPR| ≤ 0.03 and |ΔFNR| ≤ 0.05 for n-gram detector threshold transfer (n-gram methods are distribution-stable)

**Failure Response:**
- IF fails (accuracy drops ≥ 0.10 after weighting OR fully disjoint MMD): SCOPE — restrict routing claim to "corpus-local" with The Pile as reference; propose future work on domain-adaptive routing; report covariate shift extent as finding

**Dependencies:** H-M3
**Source:** Phase 2A Section 1.3 Causal Step 4; Section 1.4 Assumption A3; Section 1.5 Known Limitations

---

## 3. Risk Analysis

### 3.1 Assumption-to-Risk Mapping

| ID | Assumption | Consequence if Violated | Risk Level |
|----|------------|------------------------|------------|
| A1 | Corpus-side geometry signals are measurable proxies | Ground truth labels unreliable | High |
| A2 | ≥ 0.05 F1 margin on > 50% of items | Indeterminacy rate > 50%; routing utility limited | High |
| A3 | Feature distribution overlap across corpora (low MMD) | Routing degrades after importance weighting | Medium |
| A4 | Fixed DC-PDD reference model stable across corpora | DC-PDD arm unusable in cross-corpus comparison | Medium |
| A5 | Injection protocol captures relevant geometry space | Phase structure unstable across injection regimes | High |

### 3.2 Risk Descriptions and Mitigations

---

**Risk R1: Corpus Geometry Proxy Unreliability**
**Source Assumption:** A1 — Corpus inclusion ≠ memorization; ground truth derived from corpus overlap signals

**Description:** If 13-gram overlap and SBERT cosine similarity do not reliably distinguish contaminated from clean items (e.g., very short benchmark items match many corpus passages by chance), ground truth labels become noisy and all downstream metrics become unreliable.

**Affected Hypotheses:** H-E1, H-M1, H-M2, H-M3, H-M4 (all hypotheses use ground truth from geometry-based labels)

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Use two-pronged ground truth: Approach A (known inclusion audit from Yang et al. 2023 — verified real contamination) alongside Approach B (simulated leakage with perfect ground truth). Strong/weak positive stratification in Approach A (≥ 0.20 precision gap criterion) further controls latent-variable noise.
2. **Detection:** Compare Approach A and Approach B metric distributions — large divergence flags proxy unreliability.
3. **Response:**
   - PIVOT: If Approach A metrics diverge substantially from Approach B, report Approach B (simulated) results as primary and Approach A as exploratory.
   - SCOPE: Restrict all claims to "detector sensitivity to observable corpus overlap signals" (not causal memorization chains) — the framing is already explicit in the hypothesis.

**Early Warning Indicators:**
- Approach A precision < 0.60 on 13-gram-labeled positives (too many false positives)
- Approach A vs. Approach B metric correlation < 0.5

---

**Risk R2: High Indeterminacy Rate (> 50%)**
**Source Assumption:** A2 — Determinacy rate > 50% required for routing utility

**Description:** If fewer than 50% of benchmark items have a clear dominant detector (F1 margin ≥ 0.05 above second-best), the routing classifier has insufficient training signal and limited practical value, even if geometry correlates with performance on determinate items.

**Affected Hypotheses:** H-M3 (routing accuracy test requires determinate items), H-M4 (cross-corpus transfer requires sufficient determinate set size)

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Pre-register indeterminacy rate as a primary structural outcome before running experiments — not a post-hoc limitation.
2. **Detection:** Compute indeterminacy rate (fraction with F1 margin < 0.05) early in H-E1 verification as a go/no-go gate for H-M3.
3. **Response:**
   - PIVOT: If indeterminacy rate > 50%, shift primary claim from "routing rule is practically useful" to "indeterminate zone characterization is the primary finding" — the blind spot mapping is a valid contribution independent of routing accuracy.
   - SCOPE: Report routing accuracy only on determinate items with explicit denominator reporting.

**Early Warning Indicators:**
- Indeterminacy rate > 40% in initial H-E1 analysis
- Top-1 vs. top-2 detector F1 gap < 0.03 for majority of items

---

**Risk R3: Covariate Shift — Disjoint Feature Distributions**
**Source Assumption:** A3 — Feature distribution overlap between The Pile, C4, RedPajama

**Description:** If the geometry feature distributions of The Pile and C4/RedPajama are largely disjoint (high MMD, no common support), importance weighting cannot correct for covariate shift, and routing accuracy degrades substantially when transferred cross-corpus.

**Affected Hypotheses:** H-M3 (cross-corpus routing accuracy), H-M4 (MMD-controlled generalization)

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Compute MMD before routing evaluation; this is a pre-registered check.
2. **Detection:** MMD computation reveals feature distribution overlap; kernel density ratio estimation identifies regions of poor support.
3. **Response:**
   - SCOPE: If routing accuracy drops ≥ 0.10 after importance weighting, restrict cross-corpus claim to corpora with similar geometry distributions; identify which corpus pairs transfer successfully.
   - EXPLORE: Propose corpus-domain-adaptive routing as future work.

**Early Warning Indicators:**
- High MMD between The Pile and RedPajama (RedPajama deduplication may reduce lexical overlap features systematically)
- Routing accuracy on RedPajama substantially lower than on C4

---

**Risk R4: DC-PDD Reference Model Instability**
**Source Assumption:** A4 — Fixed DC-PDD reference model provides stable calibration

**Description:** If the fixed neutral-corpus reference model for DC-PDD has domain shift relative to C4 or RedPajama, DC-PDD performance will vary by ≥ 0.10 AUROC across corpora independently of contamination geometry — confounding the routing analysis.

**Affected Hypotheses:** H-M2 (DC-PDD as one detector arm), H-M3 (routing across all detector families including DC-PDD)

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Document and fix DC-PDD reference model before experiments; pre-register DC-PDD ablation (remove DC-PDD arm and retrain router — measure accuracy change).
2. **Detection:** Compare DC-PDD AUROC across The Pile, C4, RedPajama — variance > 0.10 flags instability.
3. **Response:**
   - SCOPE: If DC-PDD shows instability, analyze DC-PDD arm separately with fixed-corpus scope; report routing accuracy with and without DC-PDD.
   - Pre-registered ablation covers this: DC-PDD ablation is standard part of H-M3 verification protocol.

**Early Warning Indicators:**
- DC-PDD AUROC variance > 0.08 across corpora in preliminary runs
- DC-PDD threshold transfer failure (|ΔFPR| > 0.05 cross-corpus)

---

**Risk R5: Injection Protocol Validity — Phase Instability Across Regimes**
**Source Assumption:** A5 — Simulated injection protocol captures relevant contamination geometry space

**Description:** If the three injection regimes (uniform, clustered, paraphrased) produce dramatically different phase diagrams (Kendall's τ < 0.4 across regimes), the phase structure is injection-mechanism-specific rather than geometry-specific — undermining the generalizability claim.

**Affected Hypotheses:** H-E1 (indeterminacy rate depends on injection regime), H-M3 (routing accuracy may differ across regimes)

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Pre-register Kendall's τ cross-regime stability (τ ≥ 0.7 = structurally stable) as a success criterion before running Approach B experiments.
2. **Detection:** Compute detector rank correlation (Kendall's τ) across the three injection regimes after each hypothesis verification.
3. **Response:**
   - SCOPE: If τ < 0.7 across regimes, identify which regime(s) produce stable results; restrict scope to compatible injection types.
   - EXPLORE: Characterize injection-mechanism sensitivity as a finding — not all contamination patterns produce geometry-separable detection.

**Early Warning Indicators:**
- Detector rankings on uniform vs. clustered injection show τ < 0.5 in preliminary runs
- Paraphrased injection (via llm-decontaminator) produces substantially different stratum assignments than uniform injection

---

### 3.3 Baseline Failure Pattern Analysis

| Baseline Limitation | Potential Risk | Mitigation |
|---------------------|----------------|------------|
| Min-K%++ evaluated on WikiMIA only — no cross-corpus test | MIA performance variance hidden (R1, R5) | Multi-corpus evaluation with explicit variance reporting |
| DC-PDD reference model not standardized across evaluations | Reference-model confound (R4) | Fixed neutral-corpus reference; DC-PDD ablation pre-registered |
| ConTAM shows inconsistent signals without explanation | Inconsistency may reflect geometry structure we don't capture (R2, R5) | Three-zone diagram explains inconsistency; indeterminacy zone as primary finding |
| LLMSanitize aggregates without routing logic | Aggregation hides geometry-specific performance (R1) | Per-stratum disaggregation throughout all analyses |

### 3.4 Risk Summary Table

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | Corpus geometry proxy unreliability | A1 | High | All (H-E1 through H-M4) | Two-pronged ground truth (Approach A + B); strong/weak positive stratification |
| R2 | High indeterminacy rate > 50% | A2 | High | H-M3, H-M4 | Pre-register as primary outcome; shift claim to blind-spot characterization if exceeded |
| R3 | Disjoint feature distributions (high MMD) | A3 | Medium | H-M3, H-M4 | MMD computation + importance weighting; scope restriction per corpus pair |
| R4 | DC-PDD reference instability | A4 | Medium | H-M2, H-M3 | Fixed reference model; DC-PDD ablation pre-registered |
| R5 | Phase instability across injection regimes | A5 | High | H-E1, H-M3 | Pre-register τ ≥ 0.7 stability criterion; Approach A as real-contamination check |

**Critical Risks:** 0 | **High Risks:** 3 (R1, R2, R5) | **Medium Risks:** 2 (R3, R4) | **Low Risks:** 0

---

## 4. Execution Plan

### 4.1 Dependency Chain

```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 4.2 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) — 5 Hypotheses (Sequential Chain)
═══════════════════════════════════════════════════════════════════

[Level 0 — Root: EXISTENCE]
    H-E1: Geometry Decomposition Exists
    (No dependencies — MUST_WORK gate)
         │
         ▼  [Gate 1: MUST_WORK — if fail, STOP]
[Level 1 — Mechanism Step 1]
    H-M1: Corpus-Side Geometry → Stratum (Feature Orthogonality)
    (Prerequisites: H-E1)
         │
         ▼  [Gate 2: MUST_WORK for H-M1]
[Level 2 — Mechanism Step 2]
    H-M2: Detector Signal-Type Alignment
    (Prerequisites: H-M1)
         │
         ▼  [Gate 3: SHOULD_WORK]
[Level 3 — Mechanism Step 3]
    H-M3: Learnable Detector Dominance Regions (Routing Classifier)
    (Prerequisites: H-M2)
         │
         ▼  [Gate 4: SHOULD_WORK]
[Level 4 — Mechanism Step 4]
    H-M4: Cross-Corpus Routing Generalization
    (Prerequisites: H-M3)
         │
         ▼  [Gate 5: SHOULD_WORK]
    [VERIFICATION COMPLETE]

═══════════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Total Levels: 5 | Total Phases: 2
═══════════════════════════════════════════════════════════════════
```

### 4.3 Dependency Hierarchy Table

| Level | Hypothesis | Prerequisites | Gate Type | Fail Action |
|-------|-----------|---------------|-----------|-------------|
| 0 | H-E1 | None | MUST_WORK | STOP — reassess H-GeomRoute-v1 |
| 1 | H-M1 | H-E1 | MUST_WORK | PIVOT — two-zone (not three-zone) routing |
| 2 | H-M2 | H-M1 | SHOULD_WORK | EXPLORE — detector-specific analysis |
| 3 | H-M3 | H-M2 | SHOULD_WORK | PIVOT — scope to indeterminate zone finding |
| 4 | H-M4 | H-M3 | SHOULD_WORK | SCOPE — corpus-local routing claim |

### 4.4 Verification Phases

**Phase 1 — Foundation (2 weeks)**

| Hypothesis | Test | Gate |
|------------|------|------|
| H-E1 | N-gram recall ≥ 0.80 lexical / ≤ 0.40 semantic; Min-K%++ variance ≥ 0.15; indeterminacy rate [10%, 50%] | MUST_WORK |

→ **Gate 1:** If H-E1 fails → STOP entire verification plan; report indeterminate zone characterization as negative finding.

**Phase 2 — Core Mechanisms (4 weeks: H-M1 through H-M4)**

| Hypothesis | Dependencies | Test | Gate |
|------------|--------------|------|------|
| H-M1 | H-E1 | r(13-gram, cosine) ≤ 0.8 in all corpora | MUST_WORK |
| H-M2 | H-M1 | Min-K%++ F1 lower in semantic stratum; variance ≥ 0.15 | SHOULD_WORK |
| H-M3 | H-M2 | Cross-corpus top-1 accuracy > 40%; Kendall's τ > calibrated threshold | SHOULD_WORK |
| H-M4 | H-M3 | Accuracy drop < 0.10 after importance weighting; MMD not disjoint | SHOULD_WORK |

→ **Gate 2:** H-M1 MUST pass. H-M2, H-M3, H-M4 failures document limitations and trigger PIVOT/SCOPE/EXPLORE — do not invalidate H-E1 finding.

### 4.5 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE — 5 Hypotheses | Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════════
Phase/Hypothesis   │ W1-2    │ W3-4    │ W5      │ W6      │ W7
───────────────────┼─────────┼─────────┼─────────┼─────────┼─────────
PHASE 1: Foundation
  H-E1             │ ████████│         │         │         │
  [Gate 1]         │       ◆ │         │         │         │
───────────────────┼─────────┼─────────┼─────────┼─────────┼─────────
PHASE 2: Mechanisms
  H-M1             │         │ ████████│         │         │
  [Gate 2]         │         │       ◆ │         │         │
  H-M2             │         │         │ ████    │         │
  H-M3             │         │         │ ████    │         │
  [Gate 3+4]       │         │         │       ◆ │         │
  H-M4             │         │         │         │ ████    │
  [Gate 5]         │         │         │         │       ◆ │
───────────────────┼─────────┼─────────┼─────────┼─────────┼─────────
  Pre-reg ablations│         │         │         │         │ ████
═══════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks (2 H-E1 + 4 mechanism chain)
Compute: ~24-48 GPU-hours (A100) for detector evaluation
═══════════════════════════════════════════════════════════════════════
```

### 4.6 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4

Total Duration: 6 weeks
  Formula: 2 (H-E1) + 4 (H-M1 through H-M4) = 6 weeks
  Note: H-M2 and H-M3 can share Week 5 (parallel sub-tasks within same data)

Slack Available: ~0 weeks (sequential chain, one experiment per phase)

Compute Budget: ~24-48 GPU-hours total on A100
  - Corpus index building: ~8 GPU-hours (FAISS SBERT indexing for 3 corpora)
  - Detector evaluation: ~25K items × 5 detectors × 3 corpora = ~24-40 GPU-hours
  - Routing classifier training: negligible (logistic regression on geometry features)

Pre-Registered Ablations (Week 7):
  - DC-PDD ablation: remove DC-PDD arm, retrain router, measure accuracy change
  - 70% corpus proxy stress test: routing with 70% corpus index subsample
  - Prevalence shift analysis: evaluate at 5%, 10%, 30% contamination rates
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4.7 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 5
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1 to H-M4)
- Condition: 0 (none recommended)

Verification Phases: 2
1. Foundation (H-E1) — 2 weeks
2. Mechanisms (H-M1 → H-M4) — 4 weeks

Total Duration: 6 weeks + 1 week ablations
Critical Path Length: 6 weeks
Execution Mode: Sequential chain (data reuse across steps)

Key Infrastructure Requirements:
- 13-gram inverted index: EleutherAI/lm-evaluation-harness
- SBERT embedding index: FAISS + all-MiniLM-L6-v2 or similar frozen encoder
- Detector implementations: zjysteven/mink-plus-plus, ntunlp/LLMSanitize, Zhang et al. DC-PDD
- GPU: Single A100 (24-48 GPU-hours total)
- Compute: 25K items × 5 detectors × 3 corpora × 3 LLMs

Open-Source Tools (all available):
- EleutherAI/lm-evaluation-harness (13-gram decontamination pipeline)
- zjysteven/mink-plus-plus (ICLR'25 Spotlight, includes all baselines)
- ntunlp/LLMSanitize (embedding similarity via FAISS)
- lm-sys/llm-decontaminator (paraphrased injection for Approach B)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4.8 Execution Order

```
Step 1: Pre-registration — register hypothesis, falsification thresholds,
        indeterminacy rate as primary outcome, DC-PDD ablation, 70% proxy test

Step 2: Build infrastructure — 13-gram inverted index + FAISS SBERT index
        for The Pile, C4, RedPajama (~8 GPU-hours)

Step 3: Execute H-E1 (Foundation) — Weeks 1-2
        Compute geometry features; define strata; apply all 5 detectors;
        compute per-stratum metrics; generate phase diagram

Step 4: Evaluate Gate 1 → If H-E1 MUST_WORK passes, proceed to Phase 2

Step 5: Execute H-M1 (Feature Orthogonality) — Weeks 3-4
        Compute r(13-gram, cosine); verify ≤ 0.8 in all corpora

Step 6: Evaluate Gate 2 → If H-M1 passes, proceed

Step 7: Execute H-M2 + H-M3 (Signal-Type Alignment + Routing) — Week 5
        Per-stratum Min-K%++ F1; train logistic regression router;
        evaluate cross-corpus top-1 accuracy and Kendall's τ

Step 8: Execute H-M4 (Cross-Corpus Generalization) — Week 6
        Compute MMD; apply importance weighting; evaluate accuracy drop;
        check n-gram threshold transfer stability (|ΔFPR|, |ΔFNR|)

Step 9: Pre-registered ablations — Week 7
        DC-PDD ablation + 70% proxy stress test + prevalence shift analysis

Step 10: Synthesis — Determine final verification outcome
         Gate decisions → verification_state.yaml updates → Phase 4.5 / Phase 5
```

---

## 5. Dialectical Analysis

### 5.1 Thesis

**Core Claim:** Corpus-side geometric signals (max 13-gram overlap count and SBERT cosine similarity to nearest corpus neighbor) are sufficient to predict the top-performing contamination detector family cross-corpus on determinate benchmark items, producing a learnable three-zone contamination phase diagram (lexical-dominant, semantic-dominant, indeterminate) that transforms detector comparison from a leaderboard arms race into a structural regime characterization.

**Supporting Evidence:**
1. Detector signal types are orthogonal by construction: n-gram detects exact substring overlap; MIA-based methods detect likelihood perturbation on memorized tokens; embedding-based methods detect semantic proximity — supported by [Shi et al. 2023], [Zhang et al. 2024], [Fu et al. 2024]
2. Singh et al. [2024] observe inconsistent signals across methods on 13 benchmarks × 7 models — our hypothesis explains this inconsistency as geometry-regime-specific performance rather than random noise
3. The indeterminate zone (where no detector dominates) is logically implied by the joint failure of lexical and semantic overlap signals, which Fu et al. [2024] indirectly document as "random guessing under realistic conditions"

**Strengths:**
- Clear causal mechanism with 4 testable steps (feature orthogonality → signal-type alignment → learnable regions → cross-corpus transfer)
- All tools are open-source and immediately available
- Simulation-calibrated falsification thresholds prevent threshold arbitrariness
- Indeterminate zone finding is a contribution independent of routing accuracy

**Expected Outcomes:**
- P1: Cross-corpus top-1 accuracy > 40%; Kendall's τ > simulation-calibrated threshold on determinate items
- P2: N-gram recall ≥ 0.80 lexical stratum, ≤ 0.40 semantic stratum; Min-K%++ F1 variance ≥ 0.15 cross-corpus
- P3: Indeterminacy rate in [10%, 50%] — blind spot exists but routing remains practically useful

### 5.2 Antithesis

**Null Hypothesis (H0):** Corpus-side geometric signals are not sufficient to predict detector ordering above chance (top-1 accuracy ≤ 40% cross-corpus, τ ≤ simulation-calibrated threshold). Contamination detection performance is not structurally determined by corpus overlap geometry — method choice does not interact with overlap regime in a learnable, transferable way.

**Counter-Arguments:**
1. **Latent variable problem:** Corpus inclusion ≠ memorization — 13-gram overlap may be a noisy proxy that fails to capture which items are actually memorized by LLMs, making geometry strata unreliable ground truth
2. **Indeterminacy dominance:** If > 50% of items fall in the indeterminate zone, the routing rule has no practical utility even if geometry governs determinate items — the hypothesis may be technically true but practically vacuous
3. **Corpus-specificity:** The Pile, C4, and RedPajama have substantially different deduplication strategies and domain compositions — geometry features learned on The Pile may not transfer to RedPajama's deduplicated distribution

**Potential Failure Points:**
- R1 (High): Proxy unreliability — 13-gram overlap on benchmark items may match many corpus passages by chance, inflating false positives
- R2 (High): High indeterminacy rate (> 50%) — routing utility is bounded by determinacy rate
- R5 (High): Injection protocol instability — three injection regimes may produce inconsistent phase diagrams (τ < 0.4 cross-regime)

**Conditions Under Which H0 Would Be Supported:**
- Cross-corpus routing accuracy ≤ 40% after importance weighting for covariate shift
- Kendall's τ ≤ simulation-calibrated threshold on determinate items
- ≥ 30% of geometry bins showing unstable detector dominance (no separability)
- A single detector achieving F1 ≥ 0.8 uniformly across all strata (decomposition collapses)

### 5.3 Synthesis

**Balanced Assessment:**

H-GeomRoute-v1 presents a well-specified, testable claim grounded in mechanistic reasoning about detector signal types. The thesis is strongest for the indeterminate zone finding — even if routing accuracy fails, characterizing the fraction of benchmark items where no current detector dominates is a genuine field contribution that explains Singh et al.'s observed inconsistencies. The routing claim (cross-corpus accuracy > 40%) is the most vulnerable to the antithesis: the latent-variable critique and high-indeterminacy-rate scenario are legitimate threats.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes existence of geometry-performance correlation before claiming learnability
2. **Sequential mechanism testing (H-M1 → H-M4):** Each step must pass before the next is attempted; early failures are informative rather than catastrophic
3. **Gate conditions:** Allow early detection of H0 support — H-E1 or H-M1 failure triggers immediate scope reassessment
4. **Two-pronged ground truth:** Approach A (real contamination) + Approach B (simulated) cross-validates findings against proxy unreliability
5. **Pre-registered falsification thresholds:** Simulation-calibrated thresholds prevent post-hoc boundary adjustment

**Conditions for Thesis Support:**
- H-E1 MUST_WORK gate passes (geometry strata separate detector performance)
- H-M1 passes (features are orthogonal — strata are genuinely distinct)
- P1 confirmed (cross-corpus routing accuracy > 40%; Kendall's τ > calibrated threshold)

**Conditions for Antithesis Support:**
- H-E1 fails (n-gram recall ≥ 0.60 in semantic stratum — geometry does not govern performance)
- H-M1 fails (r > 0.8 — geometry features are redundant)
- Routing accuracy ≤ 40% after importance weighting on both C4 and RedPajama

**Nuanced Outcome Possibilities:**
1. **Full Support:** All 5 hypotheses pass → Three-zone phase diagram validated with practical routing rule
2. **Partial Support (Indeterminate Zone Primary):** H-E1 passes + H-M3 fails → Blind spot characterization is the primary finding; routing utility is limited but detection landscape mapping is novel
3. **Mechanism Partial:** H-E1 + H-M1 + H-M2 pass but H-M3 fails → Geometry governs individual detector performance by stratum but not cross-corpus routing prediction
4. **No Support:** H-E1 fails → Geometry strata do not separate detector performance; null hypothesis supported; contribute as empirical negative finding for future benchmark audit methods

### 5.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Geometry strata create separable detector-dominance regions | Proxy unreliability — corpus overlap ≠ memorization | H-E1 two-pronged test (Approach A + B); strong/weak stratification |
| Mechanism (Steps 1-2) | Feature orthogonality + signal-type alignment | Features may be correlated; MIA geometry-invariant | H-M1 correlation test; H-M2 stratum-specific F1 evaluation |
| Mechanism (Steps 3-4) | Learnable routing rule generalizes cross-corpus | High indeterminacy; covariate shift; corpus-local | H-M3 routing accuracy test; H-M4 MMD + importance weighting |
| Scope | Open-weight models, 3 benchmarks, 3 corpora | Proprietary models excluded; injection protocol | Explicit scope boundary in hypothesis statement |
| Indeterminate Zone | Primary novel contribution — blind spot characterization | > 50% indeterminacy → routing vacuous | Pre-registered as primary outcome; standalone contribution |

**Overall Robustness Score:** Medium-High
- Strong on mechanism design and falsifiability (simulation-calibrated thresholds, pre-registered ablations)
- Moderate on cross-corpus generalizability (MMD uncertainty for RedPajama)
- Indeterminate zone finding is robust — contributes regardless of routing outcome

**Confidence in Verification Plan:** 0.78 (inherits from Phase 2A validated hypothesis confidence)

---

## 6. Executive Summary & Conclusions

### 6.1 Executive Summary

**Main Hypothesis:** H-GeomRoute-v1 — Corpus-side geometric signals (13-gram overlap + SBERT cosine similarity) predict the top-performing contamination detector family cross-corpus via logistic regression routing with accuracy > 40% and Kendall's τ > simulation-calibrated threshold on determinate items.
- ID: H-GeomRoute-v1 | Confidence: 0.78 | Mode: Incremental (50% scope reduction from Phase 2A)

**Verification Structure:**
- Sub-Hypotheses: 5 total (H-E1 existence; H-M1–H-M4 causal chain mechanism)
- Phases: 2 phases over 6 weeks + 1 week ablations
- Critical Gates: Gate 1 (H-E1 MUST_WORK); Gate 2 (H-M1 MUST_WORK); Gates 3-5 (H-M2–H-M4 SHOULD_WORK)
- Compute: ~24-48 GPU-hours on A100; all tools open-source

**Risk Assessment:** Medium-High
- Primary concerns: High indeterminacy rate (> 50% would limit routing utility); injection protocol stability (Kendall's τ cross-regime); proxy unreliability (corpus inclusion ≠ memorization)

**Immediate Action:** Pre-register hypothesis, thresholds, and ablations; then begin Phase 1 with H-E1 (build corpus indices + run all 5 detectors + compute geometry strata)

### 6.2 Conclusions

**Key Achievements of This Verification Plan:**
- 5 hypotheses defined across 2 phases with explicit gate conditions and failure responses
- H0 addressed: geometry signals insufficient to predict detector ordering above chance
- 50% scope reduction from Phase 2A established facts — 4 BUILD_ON claims require no experiments
- All 5 pre-registered ablations defined (indeterminacy primary outcome, DC-PDD ablation, 70% proxy, prevalence shift, cross-injection-regime τ)

**Verification Execution Order:**

**Phase 1: Foundation** (Weeks 1-2)
- H-E1: Geometry decomposition exists — n-gram recall separability by stratum; indeterminacy rate [10%, 50%]; Min-K%++ F1 variance ≥ 0.15
- Gate 1: MUST PASS — if fail, STOP and report negative finding with indeterminate zone characterization

**Phase 2: Core Mechanisms** (Weeks 3-6)
- H-M1 (Weeks 3-4): r(13-gram, cosine) ≤ 0.8 — feature orthogonality — Gate 2: MUST PASS
- H-M2 (Week 5): Min-K%++ stratum-sensitivity — SHOULD_WORK
- H-M3 (Week 5): Cross-corpus routing accuracy > 40%; Kendall's τ > calibrated threshold — SHOULD_WORK
- H-M4 (Week 6): MMD-controlled accuracy drop < 0.10; threshold transfer stability — SHOULD_WORK

**Critical Decision Points:**

1. **Gate 1 (H-E1 — Foundation):** MUST PASS
   - PASS → Proceed to Phase 2
   - FAIL → STOP; report as negative finding; indeterminate zone characterization still publishable

2. **Gate 2 (H-M1 — Feature Orthogonality):** MUST PASS
   - PASS → Proceed to H-M2
   - FAIL → PIVOT to two-zone routing (single geometry dimension)

3. **Gates 3-5 (H-M2–H-M4):** SHOULD PASS
   - Any FAIL → Execute EXPLORE/SCOPE/PIVOT strategy per specification; do not invalidate H-E1 finding

**Open Questions (from Phase 2A):**
- What is the actual indeterminacy rate on real (Approach A) vs. simulated (Approach B) ground truth? If they diverge substantially, injection protocol validity must be re-examined.
- Does the routing rule generalize across model families (Llama vs. Mistral vs. Pythia), or is it model-specific?
- Can the three-zone phase diagram be used prospectively for benchmark design (avoiding items that fall in the indeterminate zone)?

**Recommendations:**

1. **Immediate Actions:**
   - Pre-register indeterminacy rate as primary structural outcome (not a secondary caveat) before running any experiments
   - Fix and document DC-PDD reference model before building corpus indices
   - Start Phase 1 with H-E1 — compute geometry strata before running detectors (stratification must be corpus-side, not detector-informed)

2. **Resource Allocation:**
   - Allocate 6 weeks for critical path + 1 week for pre-registered ablations
   - Reserve GPU buffer: 24 hours baseline + 24 hours buffer for ablations
   - Ensure corpus index storage (~100GB estimated for 3-gram inverted indices + FAISS indices)

3. **Failure Management:**
   - Document all gate failures with explicit metric values
   - Execute PIVOT/SCOPE strategies as defined per hypothesis specification
   - Indeterminate zone finding (H-E1 secondary outcome) is independently publishable regardless of routing accuracy

### 6.3 Appendices

**Appendix A: Phase 2A Reference**
- Source: `docs/youra_research/20260513_data_problems/03_refinement.yaml` (ID: H-GeomRoute-v1)
- Phase 2A Discussion: 16 exchanges, 6 agents, all convergence criteria met
- Schema: v10.0.0 Free-Parse

**Appendix B: MCP Tool Usage Summary**
- Total MCP calls: 3 (mcp__clearThought__scientificmethod)
  - Call 1: H-E1 verification (hypothesis + experiment stages)
  - Call 2a: H-M1+H-M2 mechanism chain (steps 1-2)
  - Call 2b: H-M3+H-M4 mechanism chain (steps 3-4)
- Mode: Incremental (4-6 MCP calls target; 3 calls achieved with combined calls)

**Appendix C: Pre-Registration Checklist**
- [ ] Indeterminacy rate as primary structural outcome (not a limitation)
- [ ] DC-PDD ablation: remove DC-PDD arm, retrain router, measure accuracy Δ
- [ ] 70% corpus proxy stress test: routing with 70% index subsample
- [ ] Prevalence shift analysis: evaluate at 5%, 10%, 30% contamination rates
- [ ] Cross-injection-regime τ: Kendall's τ ≥ 0.7 stability criterion across uniform/clustered/paraphrased

---

*Generated by YouRA Phase 2B (v7.7.0) | 2026-05-13 | UNATTENDED mode*
