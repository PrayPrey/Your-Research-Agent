---
hypothesis_title: "Human→AI Annotation Drift: Measuring Directional Stylistic Adaptation in RLHF Preference Datasets via the Alignment Asymmetry Index"
hypothesis_id: "H-AAI-v1"
confidence_level: 0.72
total_hypothesis_count: 5
research_mode: "incremental"
causal_chain_count: 4
condition_hypothesis_count: 0
phase: "2B"
status: "complete"
completedAt: "2026-05-03T00:00:00Z"
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
---

# Verification Plan: Human→AI Annotation Drift via Alignment Asymmetry Index (AAI)

**Date:** 2026-05-03
**Hypothesis ID:** H-AAI-v1
**Confidence:** 0.72
**Total Hypotheses:** 5 (H-E1, H-M1, H-M2, H-M3, H-M4)
**Research Mode:** Incremental (Phase 2A available)
**Scope Reduction:** 38% (5 BUILD_ON claims excluded from re-verification)

---

## Section 0: Established Facts & Scope Reduction

### 0.1 BUILD_ON Claims (DO NOT RE-TEST)

These 5 claims are established by prior literature and serve as background assumptions:

| ID | Claim | Evidence |
|----|-------|----------|
| EF1 | Human judges adapt evaluation criteria upon repeated AI output exposure | Thakur et al. 2024 (arXiv:2406.12624) |
| EF2 | Reward model overoptimization degrades downstream objective benchmarks | Pan et al. 2022 (arXiv:2201.03544); Coste et al. 2023 (arXiv:2310.02743) |
| EF3 | HH-RLHF contains 3 annotation rounds with temporal metadata | Bai et al. 2022 (arXiv:2204.05862) |
| EF4 | KL divergence asymmetry is theoretically grounded in RLHF PPO penalty | Ouyang et al. 2022 (arXiv:2203.02155) |
| EF5 | Automation bias is strongest under decision ambiguity | Skitka et al. HCI literature (30+ years); replicated in aviation, medicine |

### 0.2 PROVE_NEW Claims (ACTIVE RESEARCH TARGETS)

Phase 2B generates hypotheses exclusively for these 3 claims:

| ID | Claim | Maps To |
|----|-------|---------|
| PN1 | Temporal annotation drift in RLHF datasets has not been measured | H-E1 |
| PN2 | Human→AI stylistic adaptation corrupts RLHF training signal | H-M1 → H-M3 |
| PN3 | AAI correlates with downstream benchmark degradation | H-M4 |

**Scope Efficiency:** 38% of potential verification scope eliminated by leveraging established literature. Phase 2B-4 focuses exclusively on PROVE_NEW claims.

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under conditions of repeated RLHF annotation exposure (HH-RLHF 3-round structure; WebGPT longitudinal sessions), if human annotators have cumulative exposure to AI-generated text across annotation rounds, then their preference labels will exhibit directional stylistic drift toward AI-typical features (increased weight on verbosity, structured reasoning, hedging — measured via the Alignment Asymmetry Index AAI), because automation bias induces annotators to internalize AI stylistic norms as quality heuristics, particularly under high-ambiguity prompts where annotation uncertainty is greatest.

### 1.2 Alternative Hypothesis (H0)

After conditioning on prompt features, model checkpoint version, and affine-recalibrated early-round quality surrogate (Q_early), stylistic preference coefficients (β_L, β_H, β_S) do not change directionally across annotation rounds beyond what is expected from sampling variability or annotator cohort turnover. AAI trajectory shows no significant correlation (Spearman ρ ≤ 0.2) with TruthfulQA/BBH performance across rounds.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Anthropic HH-RLHF + OpenAI WebGPT Comparisons (standard) | HH-RLHF provides 3 annotation rounds enabling temporal drift analysis; WebGPT provides worker IDs and timestamps for within-annotator dose-response design |
| **Model** | HuggingFace TRL RewardTrainer (GPT-2 or LLaMA-7B base) | TRL RewardTrainer enables training reward models on temporal subsets of HH-RLHF with identical hyperparameters. PPO trainer enables RLHF fine-tuning for behavioral divergence analysis |

**Dataset Details:**
- Source: HuggingFace: Anthropic/hh-rlhf; GitHub: openai/summarize-from-feedback
- Path: Downloaded via HuggingFace datasets API
- Scale: HH-RLHF ~169K comparisons (full dataset); WebGPT comparisons (full dataset)

**Model Details:**
- Type: reward_model_and_RLHF_finetuned
- Source: HuggingFace TRL library (github.com/huggingface/trl)

### 1.4 Baseline Methods

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|-----------------|
| Standard RLHF (all rounds combined) | TruthfulQA ~50-60% MC1 (GPT-2 scale) | HH-RLHF (all rounds) | Does not separate early-round from late-round label influence; cannot detect temporal drift contribution |
| Reward model ensemble (Coste et al. 2023) | Reduces overoptimization but no drift measurement | Various RLHF datasets | Addresses annotation variance globally; does not isolate directional temporally-structured drift |
| LLM-as-judge evaluation (Thakur et al. 2024) | Documents judge adaptation in evaluation settings | Custom judge eval datasets | Measures downstream evaluation bias, not upstream training signal corruption |

### 1.5 Key Assumptions

| ID | Assumption | Supporting Evidence | Consequence If Violated |
|----|------------|--------------------|-----------------------|
| A1 | HH-RLHF annotation rounds represent genuine temporal exposure strata — later-round annotators had cumulative prior AI-text exposure | Bai et al. 2022 describes sequential annotation phases; annotator pool overlap plausible but not explicitly documented | Round-level analysis becomes cross-sectional cohort comparison; identification of adaptation mechanism weakens to population-level norm shift |
| A2 | Q_early (round-1 preference predictor) provides a stable quality surrogate for later rounds after affine recalibration | Standard covariate adjustment in causal inference; multiple quality proxies reduce omitted variable bias | Residual stylistic coefficients conflate quality with style; entire decomposition loses interpretive validity — Q_early calibration test is a go/no-go gate |
| A3 | The AI-typicality vector (centroid difference between model-generated and human-written text in round-1 embedding space) captures stylistic rather than topical variation | Computed from fixed round-1 data using static sentence-transformer encoder; placebo test validates robustness | Geometric projection measures domain/topic shift rather than stylistic adaptation; discriminant validity fails |
| A4 | WebGPT annotator worker IDs enable within-annotator fixed effects with sufficient within-worker exposure variation | WebGPT documented to contain worker IDs and timestamps (Stiennon et al. 2020); crowdwork typically asynchronous with multiple sessions | Dose-response analysis reduces to between-worker comparison; cannot distinguish individual adaptation from cohort-level selection effects |
| A5 | Automation bias ambiguity-modulation prediction holds in annotation settings — drift is strongest in high-annotator-disagreement prompts | Foundational automation bias literature; Thakur 2024 shows LLM-judge adaptation most pronounced for ambiguous quality judgments | Uniform drift across ambiguity levels would contradict the automation bias mechanism; hypothesis would require alternative theoretical grounding |

### 1.6 Research Gap & Novelty

**Gap:** No published study has directly measured temporal annotation drift in RLHF preference datasets, nor linked such drift to downstream benchmark degradation via a validated composite instrument.

**Novelty:** The Alignment Asymmetry Index (AAI) is the first signed, directional, fully automated monitoring instrument for Human→AI preference adaptation in RLHF pipelines, validated against objective benchmarks (TruthfulQA, BBH) without human evaluation. It triangulates three independent measurement approaches: stylistic coefficient drift (β_L, β_H, β_S), geometric projection onto AI-typicality embedding vector, and behavioral divergence in split-training models.

**Differentiation:**
- vs. Thakur 2024: Annotation setting (training data collection) vs. evaluation setting; links to reward model corruption
- vs. Coste 2023: Directional temporal drift vs. global annotation variance
- vs. Pan 2022: Fills the unmeasured upstream source (temporal annotation drift) of benchmark degradation
- vs. Christiano 2017: First empirical test of the static human preference assumption

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Statement (Brief) | Gate | Prerequisites | Status |
|----|------|-------------------|------|---------------|--------|
| H-E1 | EXISTENCE | Temporal stylistic coefficient drift exists in HH-RLHF annotation rounds after Q_early recalibration | MUST_WORK | None | READY |
| H-M1 | MECHANISM | Repeated exposure internalizes AI-typical stylistic norms as quality heuristics (ambiguity-modulated) | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | Internalized norms cause systematic upweighting of AI-typical stylistic features in preference labels | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | Stylistic preference drift corrupts RLHF reward model training signal (split-training behavioral divergence) | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | MECHANISM | Stylistic reward bias propagates to RLHF fine-tuned model causing style-invariant benchmark degradation | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Temporal Stylistic Coefficient Drift Exists in HH-RLHF

**Statement:** Under conditions where HH-RLHF annotation rounds represent genuine temporal exposure strata, if stylistic preference coefficients (β_L, β_H, β_S) are estimated per round via logistic regression with Q_early covariate, then the coefficients exhibit statistically significant directional drift across rounds (increasing weights on verbosity, hedging, structured reasoning), particularly in high-annotator-disagreement prompts, because annotation rounds serve as a proxy for cumulative AI-text exposure inducing automation bias.

**Rationale:** This is the foundational existence test — if stylistic coefficient drift is absent after Q_early recalibration, the entire downstream mechanism chain (H-M1 through H-M4) is unmotivated. The ambiguity-modulation interaction (round × high_ambiguity) is the theoretically-grounded specificity check that distinguishes genuine annotation adaptation from non-directional noise. Positive result establishes the AAI instrument's first component.

**Variables (from Phase 2A):**
- Independent: Annotation round (ordinal 1–3 in HH-RLHF); prompt ambiguity level (Fleiss κ < 0.4 = high ambiguity)
- Dependent: Stylistic preference coefficients β_L (verbosity), β_H (hedging), β_S (structured reasoning) from round-conditioned logistic regression
- Controlled: Model checkpoint version, prompt topic distribution, affine-recalibrated Q_early (frozen logistic regression on round-1 labels)

**Verification Protocol:**
1. Load full HH-RLHF dataset (~169K comparisons); partition into round-1, round-2, round-3 strata by annotation phase metadata.
2. Train Q_early logistic regression on round-1 preference labels; apply affine recalibration (scale+shift only) to rounds 2–3; verify calibration stability (go/no-go gate: Brier score difference < 0.02).
3. Extract stylistic features per response (token length, hedging phrase count, structured reasoning markers); run round-conditioned logistic regression with Q_early covariate and round × ambiguity interaction term; bootstrap 95% CI on coefficient differences.
4. Compute Fleiss κ per prompt to partition high-ambiguity (κ < 0.4) vs. low-ambiguity strata; verify interaction term round × high_ambiguity is positive and significant.
5. Run placebo test: permute round labels within matched prompt groups; verify coefficient drift disappears under permutation.

**Success Criteria (PoC: Direction-based):**
- Primary: Interaction term round × high_ambiguity is positive and significant (p < 0.05 after Bonferroni correction); stylistic coefficients show net positive directional shift in high-ambiguity stratum across rounds
- Secondary: Q_early calibration go/no-go gate passes (Brier score difference < 0.02 between rounds)

**Failure Response:**
- IF Q_early gate fails: STOP downstream analyses — pivot to alternative quality control strategy before re-running
- IF drift absent (interaction non-significant): EXPLORE — check if effect requires larger effect size threshold or WebGPT dose-response evidence before ABANDON

**Dependencies:** None (foundation hypothesis)

**Source:** Phase 2A Section 5 (SH1), Section 1.6 (P1), Section 1.4 (A1, A2)

---

#### H-M1: Automation Bias Mediates Ambiguity-Modulated Norm Internalization

**Statement:** Under conditions of verified temporal stylistic drift (H-E1 passed), if annotators with higher cumulative AI-text exposure (operationalized as later rounds in HH-RLHF; cumulative tokens viewed in WebGPT) are faced with high-ambiguity prompts, then their within-round preference patterns will show stronger AI-typicality geometric projection than low-exposure or low-ambiguity counterparts, because automation bias theory predicts strongest AI-norm internalization precisely when annotation uncertainty is highest.

**Rationale:** H-M1 tests the causal mechanism behind H-E1's observed drift by verifying the automation-bias-specific ambiguity-modulation signature. A finding that drift is non-uniform across ambiguity levels — strongest under uncertainty — is the key discriminating prediction that separates genuine automation bias from generic cohort-level quality shift. This step bridges the empirical observation (H-E1) to the mechanistic explanation.

**Variables (from Phase 2A):**
- Independent: Cumulative AI-text exposure proxy (round ordinal in HH-RLHF; cumulative tokens viewed per worker in WebGPT)
- Dependent: AI-typicality geometric projection score (cosine projection of late-round residual preference gradient onto pre-defined AI-typicality embedding vector, computed from frozen round-1 sentence-transformer)
- Controlled: Prompt topic distribution, annotator fixed effects (WebGPT worker FE), model checkpoint version

**Verification Protocol:**
1. Compute AI-typicality vector as centroid difference between model-generated and human-written text in round-1 embedding space (frozen all-MiniLM-L6-v2 encoder); run placebo validation (prompt-matched permutation test) to confirm stylistic vs. topical capture.
2. For HH-RLHF: compute per-round geometric projection of residual preference gradients (after Q_early partialing) onto AI-typicality vector; test monotonic increase across rounds, stratified by ambiguity level.
3. For WebGPT: run panel regression projection_score ~ cumulative_tokens_viewed + worker_FE + task_type_FE with standard errors clustered by worker; verify β_exposure > 0.
4. Test ambiguity-modulation interaction: projection increase is significantly larger in high-ambiguity (κ < 0.4) stratum than low-ambiguity stratum in both datasets.
5. Discriminant validity check: run parallel regression on topic-axis projection (control); verify stylistic projection increases significantly while topic projection does not.

**Success Criteria (PoC: Direction-based):**
- Primary: β_exposure > 0 with p < 0.05 in WebGPT worker fixed-effects regression; effect ≥ 0.1 SD increase in projection per 1000 tokens viewed
- Secondary: Ambiguity-modulation interaction significant in HH-RLHF (stronger projection increase in high-ambiguity stratum); discriminant validity confirmed (stylistic > topic projection)

**Failure Response:**
- IF β_exposure ≤ 0 or non-significant: PIVOT — test whether calendar time (not cumulative tokens) predicts projection, which would suggest cohort norm shift rather than individual adaptation
- IF ambiguity interaction absent: EXPLORE — document as boundary condition failure; hypothesis scope narrows to general drift without automation-bias mechanism

**Dependencies:** H-E1 (existence of drift must be established first)

**Source:** Phase 2A Section 1.3 (Causal Step 1), Section 1.6 (P3), Section 1.4 (A3, A4, A5)

---

#### H-M2: Drift-Contaminated Preference Labels Show Measurable AI-Typicality Upweighting

**Statement:** Under conditions of verified exposure-dependent norm internalization (H-M1 passed), if preference labels from later annotation rounds are used to train a logistic regression preference predictor, then the learned stylistic coefficients (β_L, β_H, β_S) will be systematically and directionally larger than coefficients from early-round-trained predictors on identical held-out prompt sets, because internalized AI-typicality norms are reflected in annotation decisions and thus encoded in the label distribution of later rounds.

**Rationale:** H-M2 operationalizes the training-signal corruption by demonstrating that later-round label distributions have quantifiably different stylistic weightings than early-round distributions, independent of semantic quality. This is the direct evidence that the drift identified in H-M1 propagates into the training signal that downstream reward models will consume. It closes the gap between annotator behavior change and data-level signal corruption.

**Variables (from Phase 2A):**
- Independent: Annotation round stratum (early: round-1; late: round-3)
- Dependent: Stylistic preference coefficients β_L, β_H, β_S estimated from round-stratified preference prediction models
- Controlled: Q_early quality predictor (included as covariate in all models), prompt topic distribution (stratified sampling), model checkpoint version

**Verification Protocol:**
1. Split HH-RLHF into early-round (round-1, ~56K comparisons) and late-round (round-3, ~56K comparisons) subsets using temporal metadata; verify topic distribution balance via chi-square test.
2. Fit separate logistic regression preference predictors on early and late subsets, each including Q_early as covariate and same stylistic features (length, hedging count, structure markers).
3. Compare β_L, β_H, β_S coefficients between early and late models using bootstrap confidence intervals (2000 resamples); test for directional difference (late > early for all three features).
4. Validate on held-out cross-round test set (25% of each round): late-round model should systematically prefer longer, more hedged, more structured responses than early-round model on identical prompts.
5. Test for sign-consistency: all three stylistic coefficients should shift in the same direction (positive for verbosity and structured reasoning, relative increase in hedging); inconsistent signs constitute falsification.

**Success Criteria (PoC: Direction-based):**
- Primary: At least 2 of 3 stylistic coefficients (β_L, β_H, β_S) are directionally larger in late-round model vs. early-round model with non-overlapping 95% bootstrap CIs
- Secondary: Late-round model predicts ≥ 10% longer responses than early-round model on identical high-ambiguity held-out prompts

**Failure Response:**
- IF coefficients non-directional or sign-inconsistent: PIVOT — check whether Q_early calibration captured residual stylistic variance (revisit A2 gate); narrow claim to specific stylistic features that do shift
- IF effect exists but tiny (overlapping CIs): EXPLORE — increase statistical power with full dataset; document as weak effect

**Dependencies:** H-M1 (exposure-dependent norm internalization must be established)

**Source:** Phase 2A Section 1.3 (Causal Step 2), Section 1.2 (variables), Section 1.4 (A2)

---

#### H-M3: Drift-Contaminated Labels Produce Reward Model with Altered Stylistic Preferences

**Statement:** Under conditions of verified label-level stylistic upweighting (H-M2 passed), if reward models are trained separately on early-round vs. late-round HH-RLHF labels using identical architectures and hyperparameters (TRL RewardTrainer), then the late-round-trained reward model will assign systematically higher scores to longer, more structured, more hedged responses on a shared prompt test set, even after controlling for semantic quality (Q_early score), because drift-contaminated training labels encode the annotator's adapted stylistic preferences into reward model weights.

**Rationale:** H-M3 is the critical training-signal-to-model-weights transfer test. If the label-level drift (H-M2) does not propagate into learned reward model behavior, then the downstream concern about RLHF pipeline corruption is empirically unfounded. A positive result demonstrates that temporal annotation drift is not merely a statistical artifact in annotation distributions but a causal driver of reward model behavior divergence — the core empirical contribution of this research.

**Variables (from Phase 2A):**
- Independent: Training data stratum (early-round labels vs. late-round labels), response stylistic features (length, hedging, structure)
- Dependent: Reward model score differential (late-round RM score − early-round RM score) on matched prompt test set; behavioral divergence metrics (mean token length, hedging phrase frequency, structure marker count) in RM-preferred outputs
- Controlled: Model architecture (identical GPT-2/LLaMA-7B base), hyperparameters (identical TRL RewardTrainer config), prompt set (identical 500-prompt held-out test set with Q_early scores)

**Verification Protocol:**
1. Train early-RM on round-1 HH-RLHF (full ~56K comparisons) and late-RM on round-3 HH-RLHF using identical TRL RewardTrainer config (same base model, same epochs, same batch size, same LR schedule).
2. Evaluate both RMs on 500-prompt held-out test set; extract reward scores for each response; compute score differential (late-RM − early-RM) per response.
3. Regress score differential on stylistic features (length, hedging, structure) and Q_early score; test that stylistic features have significant positive coefficients while Q_early coefficient is near zero.
4. Identify top-100 responses where late-RM score > early-RM score; verify these responses are significantly longer (t-test), more hedged, and more structured than top-100 responses where early-RM score > late-RM score.
5. Run random-split control: train random-RM on same-size random subset of all rounds; verify temporal-split divergence significantly exceeds random-split divergence (confirms temporal structure, not sample variance, drives divergence).

**Success Criteria (PoC: Direction-based):**
- Primary: Late-RM assigns significantly higher scores to longer, more structured responses than early-RM after Q_early control (stylistic coefficient p < 0.05; Q_early coefficient p > 0.1)
- Secondary: Temporal-split RM divergence significantly exceeds random-split RM divergence (confirms temporal structure drives effect)

**Failure Response:**
- IF no significant reward score divergence: PIVOT — check whether GPT-2-scale model has insufficient capacity to encode subtle stylistic preferences; retry with LLaMA-7B scale
- IF Q_early dominates divergence: STOP — A2 assumption violated; Q_early calibration failed to isolate stylistic from quality drift; return to H-E1 with revised quality control strategy

**Dependencies:** H-M2 (label-level stylistic upweighting must be established)

**Source:** Phase 2A Section 1.3 (Causal Step 3), Section 2 (experimental setup), Section 1.4 (A2)

---

#### H-M4: Stylistic Reward Bias Propagates to RLHF Fine-Tuned Model Causing Benchmark Degradation

**Statement:** Under conditions of verified reward model stylistic divergence (H-M3 passed), if language models are RLHF fine-tuned using early-round vs. late-round reward models (via TRL PPO), then the late-round RLHF model will generate outputs that are systematically longer and more stylistically AI-typical, while exhibiting significantly lower accuracy on TruthfulQA (MC1) and/or BBH (exact match) compared to the early-round RLHF model, because stylistic reward bias displaces optimization pressure away from factual accuracy, constituting empirical evidence of Human→AI alignment drift propagating through the RLHF pipeline.

**Rationale:** H-M4 closes the full causal chain by demonstrating that reward model behavioral divergence (H-M3) propagates into downstream model outputs and degrades performance on style-invariant objective benchmarks. This is the highest-stakes test: if confirmed, it establishes temporal annotation drift as a measurable and consequential source of alignment failure in deployed RLHF pipelines. The AAI composite score integrates evidence from H-E1, H-M1, and H-M4 into a single scalar instrument. The Spearman correlation between AAI trajectory and benchmark degradation is the primary Phase 2B readiness signal (SH2).

**Variables (from Phase 2A):**
- Independent: RLHF training data stratum (early-round RM vs. late-round RM as reward signal)
- Dependent (primary): AAI composite score per model (triangulating coefficient drift + geometric projection + behavioral divergence); TruthfulQA MC1 accuracy (817 questions); BBH exact match accuracy (6511 questions)
- Controlled: Base model (identical checkpoint), PPO hyperparameters (identical TRL config), evaluation harness (identical EleutherAI lm-evaluation-harness config)

**Verification Protocol:**
1. RLHF fine-tune base model from early-RM (early-RLHF model) and from late-RM (late-RLHF model) using identical TRL PPO configuration (same KL penalty β, same prompt distribution, same number of PPO steps).
2. Evaluate both models on full TruthfulQA benchmark (817 MC1 questions) and full BIG-Bench Hard (6511 questions) via EleutherAI lm-evaluation-harness; record MC1 accuracy and exact match accuracy.
3. Compute AAI composite score per model: (1) stylistic coefficient drift magnitude from H-E1; (2) geometric projection score from H-M1; (3) behavioral divergence (token length Δ, structure score Δ) between early-RLHF and late-RLHF on matched prompt set.
4. Compute Spearman rank correlation between AAI trajectory and TruthfulQA/BBH accuracy trajectory across early, mid, and late annotation round models; test ρ > 0.4 and ρ < 0 (negative direction: higher AAI → lower benchmark accuracy).
5. Run mediation analysis: test whether length increase (indirect path) fully mediates any factual accuracy change (direct effect should remain negative); verify indirect path ≤ 50% to exclude pure length confound.

**Success Criteria (PoC: Direction-based):**
- Primary: Spearman ρ > 0.4 for at least one benchmark (TruthfulQA or BBH); ρ < 0 (negative: higher AAI associated with lower accuracy); late-RLHF model outputs ≥ 10% longer with ≤ 1% factual accuracy gain
- Secondary: Direct effect of drift on benchmark accuracy remains negative after mediating length (indirect path ≤ 50%)

**Failure Response:**
- IF Spearman ρ ≤ 0.2 for both benchmarks: EXPLORE — test whether ρ is positive (adaptive drift hypothesis), which would constitute a scientifically valid null result reframing the AAI as a robustness validator
- IF ρ > 0.2 but ≤ 0.4: Document as weak-effect result; report as partial evidence with limited effect size; this threshold requires power analysis in Phase 2C

**Dependencies:** H-M3 (reward model stylistic divergence must be established)

**Source:** Phase 2A Section 1.3 (Causal Step 4), Section 1.6 (P2), Section 5 (SH2)

---

## 3. Execution

### 3.1 Dependency Chain

```
H-E1 (MUST_WORK) → H-M1 (MUST_WORK) → H-M2 (SHOULD_WORK) → H-M3 (SHOULD_WORK) → H-M4 (SHOULD_WORK)
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Interaction round × high_ambiguity significant (p < 0.05 Bonferroni); directional β drift in high-ambiguity stratum | STOP entire pipeline; reassess main hypothesis H-AAI-v1 |
| H-M1 | MUST_WORK | β_exposure > 0 with p < 0.05 in WebGPT worker FE regression; ambiguity modulation confirmed | PIVOT to alternative mechanism explanation; document automation-bias mechanism as unconfirmed |
| H-M2 | SHOULD_WORK | ≥ 2 of 3 stylistic coefficients directionally larger in late-round model (non-overlapping 95% CI) | PIVOT to narrower claim (specific features only); continue to H-M3 with reduced scope |
| H-M3 | SHOULD_WORK | Late-RM assigns higher scores to stylistically AI-typical responses after Q_early control (stylistic coeff p < 0.05) | PIVOT to LLaMA-7B scale; if still fails, document reward model capacity limitation |
| H-M4 | SHOULD_WORK | Spearman ρ > 0.4 for ≥ 1 benchmark; ρ < 0; late-RLHF outputs ≥ 10% longer | EXPLORE null-result interpretation (drift is adaptive); report with full uncertainty bounds |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Gate 1 Decision | — | End of Week 2 |
| Phase 2: Core Mechanisms | H-M1 | 2 weeks |
| Phase 2 continued | H-M2 | 1 week |
| Phase 2 continued | H-M3 | 1 week |
| Phase 2 continued | H-M4 | 1 week |
| Gate 2 Decision | — | End of Week 7 |

**Total Duration:** 7 weeks (H-E1: 2w + H-M1: 2w + H-M2: 1w + H-M3: 1w + H-M4: 1w)

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

**Risk R1: HH-RLHF Annotator Continuity Not Verified (from A1)**

**Source Assumption:** A1 — HH-RLHF annotation rounds represent genuine temporal exposure strata with annotator pool overlap across rounds.

**Description:** If annotators in later rounds are a different cohort with no prior AI-text exposure (i.e., fresh annotators each round), then round-level drift reflects cohort-level quality differences rather than individual adaptation. The causal identification strategy for within-annotator exposure effects breaks down.

**Affected Hypotheses:** H-E1, H-M1, H-M2

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Pre-analysis — verify annotator overlap in HH-RLHF metadata before running regression; if overlap < 20%, treat as cohort comparison and adjust hypothesis scope accordingly.
2. **Detection:** Bootstrap cohort-turnover null: simulate 100 random reassignments of annotators across rounds; if observed drift falls within null distribution, R1 is materializing.
3. **Response:**
   - PIVOT: Fall back to cohort-level population norm shift interpretation (weaker but valid claim); adjust H-E1 statement to reflect cohort-level rather than within-annotator evidence.
   - SCOPE: Focus primary existence evidence on WebGPT (worker IDs enable true within-annotator design); treat HH-RLHF as corroborative evidence only.
   - ABORT: Do not abort — cohort-level drift is still a publishable finding about RLHF population dynamics.

**Early Warning Indicators:**
- HH-RLHF metadata shows < 10% worker ID overlap across rounds
- Bootstrap cohort-turnover null contains observed drift coefficient

---

**Risk R2: Q_early Calibration Instability (from A2)**

**Source Assumption:** A2 — Q_early provides a stable quality surrogate after affine recalibration.

**Description:** If semantic quality of AI-generated text improves substantially between rounds (e.g., better model checkpoints used), then Q_early's affine recalibration may fail to capture the full quality shift, leaving residual quality variance in the stylistic coefficients. This would render the stylistic-vs-quality decomposition invalid.

**Affected Hypotheses:** H-E1, H-M1, H-M2, H-M3 (all downstream analyses)

**Severity:** Critical (go/no-go gate)

**Mitigation Strategy:**
1. **Prevention:** Run Q_early calibration test before any downstream analysis: compare Brier scores of Q_early on round-1 vs. rounds 2–3 after affine recalibration; set threshold at Brier score difference < 0.02.
2. **Detection:** Plot Q_early calibration curves per round; visual inspection plus statistical test (Hosmer-Lemeshow goodness-of-fit).
3. **Response:**
   - PIVOT: If affine recalibration insufficient, try non-linear recalibration (isotonic regression); if still fails, add supplementary quality proxies (perplexity, toxicity scores) to reduce omitted variable bias.
   - ABORT: If all recalibration strategies fail and Brier score difference > 0.05, halt downstream analyses and report calibration failure as the primary finding (itself publishable: RLHF quality control is harder than assumed).

**Early Warning Indicators:**
- Brier score difference between rounds > 0.02 after initial affine recalibration
- Q_early calibration curves diverge substantially for rounds 2–3

---

**Risk R3: AI-Typicality Vector Captures Topical Rather Than Stylistic Variation (from A3)**

**Source Assumption:** A3 — AI-typicality embedding vector captures stylistic variation, not topical domain shift.

**Description:** If the centroid difference between model-generated and human-written text in round-1 embedding space reflects topical or domain differences (e.g., AI responses discuss different topics than human responses) rather than stylistic adaptation, then geometric projection scores are measuring domain shift rather than stylistic drift.

**Affected Hypotheses:** H-M1, H-M2

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Run placebo test at construction time: permute AI/human labels within matched prompt groups; verify AI-typicality vector dissipates under permutation (confirming it captures response-level stylistic contrast, not prompt-level domain).
2. **Detection:** Run parallel regression on topic-axis projection (PCA of topic features); if topic projection increases at same rate as stylistic projection, R3 is materializing.
3. **Response:**
   - PIVOT: If AI-typicality vector captures topical variation, construct a topic-residualized version (project out topic principal components before computing centroid difference).
   - SCOPE: Fall back to purely coefficient-based AAI components (β_L, β_H, β_S) without geometric projection; report discriminant validity failure as a limitation.

**Early Warning Indicators:**
- Placebo test shows AI-typicality vector largely unchanged under label permutation
- Topic projection increases at comparable rate to stylistic projection

---

**Risk R4: WebGPT Worker ID Granularity Insufficient for Dose-Response (from A4)**

**Source Assumption:** A4 — WebGPT worker IDs enable within-annotator fixed effects with sufficient within-worker exposure variation.

**Description:** If WebGPT workers participated in very few sessions each (low within-worker variation in cumulative token exposure), then worker fixed effects will absorb nearly all variance and the dose-response regression will have insufficient statistical power to detect β_exposure > 0.

**Affected Hypotheses:** H-M1

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Pre-analysis exploratory data analysis: compute distribution of session counts and cumulative token counts per worker; verify median within-worker exposure range spans ≥ 3 orders of magnitude.
2. **Detection:** Run feasibility check regression with worker FE; report within-worker R² alongside total R²; if within-worker R² < 0.01, power is critically low.
3. **Response:**
   - PIVOT: If within-worker variation insufficient, use between-worker comparison with exposure terciles as a weaker but still valid identification strategy; flag as observational cross-sectional design.
   - SCOPE: If WebGPT dose-response fails entirely, rely primarily on HH-RLHF round-level evidence for H-M1; narrow WebGPT claim to secondary corroboration.

**Early Warning Indicators:**
- Median sessions per WebGPT worker < 3
- Within-worker exposure range spans < 1 order of magnitude

---

**Risk R5: Automation Bias Ambiguity-Modulation Absent in Annotation Settings (from A5)**

**Source Assumption:** A5 — Automation bias ambiguity-modulation prediction holds: drift strongest in high-annotator-disagreement prompts.

**Description:** If annotation drift is uniform across ambiguity levels (or stronger in low-ambiguity settings), then the automation-bias theoretical grounding of H-M1 is refuted. The hypothesis would require alternative theoretical framing (e.g., pure exposure conditioning rather than uncertainty-mediated adaptation).

**Affected Hypotheses:** H-M1, and by extension the automation-bias framing of all H-M hypotheses

**Severity:** Medium (theoretical rather than empirical falsification)

**Mitigation Strategy:**
1. **Prevention:** Pre-register the directional prediction (high-ambiguity > low-ambiguity drift) before analysis to prevent post-hoc reinterpretation.
2. **Detection:** The interaction term round × high_ambiguity in H-E1 regression is the direct test; if non-significant or reversed, R5 is confirmed.
3. **Response:**
   - PIVOT: If uniform drift confirmed, reframe mechanism as general AI-norm exposure conditioning (drop automation bias specificity); still publishable as "RLHF annotators develop AI-typical preferences regardless of prompt difficulty."
   - SCOPE: Automation-bias mechanism becomes one possible explanation among others; note as open question requiring additional evidence (e.g., annotator self-report surveys).

**Early Warning Indicators:**
- H-E1 ambiguity interaction term non-significant or negative at p < 0.1 significance level
- Drift magnitude is equal or larger in low-ambiguity prompts

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: HH-RLHF Annotator Continuity | A1 | H-E1, H-M1, H-M2 | High |
| R2: Q_early Calibration Instability | A2 | H-E1, H-M1, H-M2, H-M3 | Critical |
| R3: AI-Typicality Vector Topical Capture | A3 | H-M1, H-M2 | High |
| R4: WebGPT Worker ID Granularity | A4 | H-M1 | Medium |
| R5: Ambiguity Modulation Absent | A5 | H-M1 (theory framing) | Medium |

**Critical Risks:** 1 (R2 — Q_early calibration is go/no-go gate)
**High Risks:** 2 (R1, R3)
**Medium Risks:** 2 (R4, R5)
**Low Risks:** 0

### 4.3 Baseline Failure Patterns → Additional Risks

| Baseline Limitation | Potential Risk | Mitigation |
|---------------------|----------------|------------|
| Standard RLHF (all rounds combined) masks temporal structure | Null result if round partitioning creates too-small subsets | Use full available comparisons per round (~56K each in HH-RLHF); power analysis in Phase 2C |
| Coste et al. ensemble approach does not detect directional drift | AAI construction relies on valid Q_early decomposition | R2 mitigation applies |
| Thakur et al. judge adaptation in evaluation (not training) | External validity — annotation drift may differ from judge adaptation | Cross-dataset design (HH-RLHF + WebGPT) provides generalizability evidence |

---

## 5. Dependency Graph (DAG) + Timeline

### 5.1 Dependency Graph

```
═══════════════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses, H-AAI-v1
═══════════════════════════════════════════════════════════════════

[Level 0 - Root: Foundation]
    H-E1: Temporal Stylistic Coefficient Drift Exists
    (Gate: MUST_WORK — if fail, STOP pipeline)
         │
         ▼
[Level 1 - Mechanism: Automation Bias]
    H-M1: Exposure-Mediated Norm Internalization (Ambiguity-Modulated)
    (Gate: MUST_WORK — if fail, PIVOT mechanism framing)
         │
         ▼
[Level 2 - Mechanism: Label-Level Signal]
    H-M2: Drift-Contaminated Labels Show AI-Typicality Upweighting
    (Gate: SHOULD_WORK — failure narrows scope, does not stop)
         │
         ▼
[Level 3 - Mechanism: Reward Model Corruption]
    H-M3: Late-Round RM Has Altered Stylistic Preferences
    (Gate: SHOULD_WORK — failure prompts scale-up pivot)
         │
         ▼
[Level 4 - Mechanism: Pipeline Propagation + AAI Validation]
    H-M4: Stylistic Bias Propagates → Benchmark Degradation (AAI validated)
    (Gate: SHOULD_WORK — null result is also informative)

═══════════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
All hypotheses sequential (no parallelization — each requires prior gate)
═══════════════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy Table

| Level | Hypothesis | Prerequisites | Gate Type | Status |
|-------|-----------|---------------|-----------|--------|
| 0 | H-E1 | None | MUST_WORK | READY |
| 1 | H-M1 | H-E1 | MUST_WORK | NOT_STARTED |
| 2 | H-M2 | H-M1 | SHOULD_WORK | NOT_STARTED |
| 3 | H-M3 | H-M2 | SHOULD_WORK | NOT_STARTED |
| 4 | H-M4 | H-M3 | SHOULD_WORK | NOT_STARTED |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses, H-AAI-v1
Total Duration: 7 weeks
═══════════════════════════════════════════════════════════════════════════════
Phase/Hypothesis  │ W1-2      │ W3-4      │ W5        │ W6        │ W7
──────────────────┼───────────┼───────────┼───────────┼───────────┼──────────
PHASE 1: Foundation
  H-E1            │ ██████████│           │           │           │
  [Gate 1] ◆      │         ◆ │           │           │           │
──────────────────┼───────────┼───────────┼───────────┼───────────┼──────────
PHASE 2: Core Mechanisms
  H-M1            │           │ ██████████│           │           │
  [Gate 2a] ◆     │           │         ◆ │           │           │
  H-M2            │           │           │ ██████████│           │
  H-M3            │           │           │           │ ██████████│
  H-M4            │           │           │           │           │ ██████████
  [Gate 2] ◆      │           │           │           │           │         ◆
──────────────────┴───────────┴───────────┴───────────┴───────────┴──────────
Legend: ██ = Active work | ◆ = Gate decision point
Total Duration: 7 weeks
Duration Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M2) + 1 (H-M3) + 1 (H-M4)
═══════════════════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Total Duration: 7 weeks
  H-E1: 2 weeks (data loading + Q_early calibration gate + regression)
  H-M1: 2 weeks (AI-typicality vector + WebGPT panel regression + HH-RLHF interaction test)
  H-M2: 1 week (early vs. late preference predictor comparison)
  H-M3: 1 week (split-training RM evaluation on held-out test set)
  H-M4: 1 week (PPO fine-tuning + TruthfulQA/BBH evaluation + Spearman correlation)
Slack Available: 0 weeks (all sequential, each gate-dependent)
Compute Constraint: Under 4 hours single GPU (per Prof. Pax feasibility assessment)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Hypotheses: 5
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1 through H-M4)
- Condition: 0 (excluded — scope boundaries qualitative)

Verification Phases: 2
1. Foundation (H-E1): Weeks 1-2
2. Mechanisms (H-M1 through H-M4): Weeks 3-7

Total Duration: 7 weeks
Critical Path Length: 7 weeks
Execution Mode: Sequential chain (all hypotheses gate-dependent)

Compute Resources:
- Single GPU (CUDA_VISIBLE_DEVICES = selected empty GPU)
- Datasets: HH-RLHF (~169K comparisons, full); WebGPT comparisons (full)
- Models: GPT-2 or LLaMA-7B base (TRL RewardTrainer + PPO)
- Evaluation: EleutherAI lm-evaluation-harness (TruthfulQA 817q + BBH 6511q)
- Estimated total GPU time: < 4 hours (Prof. Pax feasibility assessment)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

1. **Step 1:** Execute H-E1 (Foundation: Q_early calibration gate + coefficient drift regression) — Weeks 1-2
2. **Step 2:** Evaluate Gate 1 (MUST_WORK) — End of Week 2 → If PASS, proceed; if FAIL, STOP pipeline and reassess H-AAI-v1
3. **Step 3:** Execute H-M1 (Automation bias: AI-typicality vector + WebGPT dose-response + HH-RLHF interaction) — Weeks 3-4
4. **Step 4:** Evaluate Gate 2a (MUST_WORK) — End of Week 4 → If PASS, proceed; if FAIL, PIVOT mechanism framing
5. **Step 5:** Execute H-M2 (Label-level AI-typicality upweighting comparison) — Week 5
6. **Step 6:** Execute H-M3 (Split-training reward model behavioral divergence) — Week 6
7. **Step 7:** Execute H-M4 (PPO fine-tuning + TruthfulQA/BBH evaluation + AAI Spearman correlation) — Week 7
8. **Step 8:** Evaluate Gate 2 (SHOULD_WORK) — End of Week 7 → Document results, proceed to Phase 4.5 synthesis

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Human annotators in RLHF pipelines exhibit systematic, directional stylistic adaptation toward AI-typical features under repeated annotation exposure, measurable via the Alignment Asymmetry Index (AAI), and this adaptation causally propagates through reward model training to degrade downstream benchmark performance on style-invariant tasks.

**Supporting Evidence:**
1. Automation bias theory (Skitka et al.) and empirical precedent (Thakur 2024): AI-text exposure systematically shifts evaluator criteria — directly applicable to annotation settings
2. HH-RLHF 3-round structure and WebGPT worker IDs provide unique temporal variation unavailable in most prior RLHF studies
3. Pan et al. 2022 and Coste et al. 2023 establish the reward misspecification → benchmark degradation pathway; this work fills the unmeasured upstream causal link

**Strengths:**
- Multi-dataset design (HH-RLHF + WebGPT) provides cross-task generalizability evidence
- AAI triangulates three independent measurement approaches — convergent evidence structure is robust to single-measure failure
- Both positive and null results are scientifically informative (null = RLHF robustness evidence)
- Fully automated evaluation using objective benchmarks — no human evaluation required for validation

**Expected Outcomes:**
- P1: Interaction term round × high_ambiguity positive and significant (p < 0.05) — ambiguity-modulated drift confirmed
- P2: Spearman ρ > 0.4 between AAI and TruthfulQA/BBH degradation (negative direction)
- P3: β_exposure > 0 in WebGPT worker fixed effects regression (p < 0.05)

### 6.2 Antithesis

**Null Hypothesis (H0):** After conditioning on prompt features, model checkpoint version, and affine-recalibrated Q_early, stylistic preference coefficients do not change directionally across annotation rounds beyond sampling variability or annotator cohort turnover. AAI shows no significant correlation (Spearman ρ ≤ 0.2) with TruthfulQA/BBH performance.

**Counter-Arguments:**
1. HH-RLHF rounds may not represent within-annotator temporal exposure — cohort turnover could explain apparent "drift" without any individual adaptation (R1 risk)
2. Q_early recalibration may fail to fully isolate quality from style — if AI-generated text genuinely improved in quality across rounds, the observed coefficient shift reflects rational Bayesian updating by annotators, not automation bias (A2 violation)
3. The annotation sample sizes per round (~56K each) may be underpowered for detecting the small effect sizes expected for stylistic coefficient drift (effect size anchoring deferred to Phase 2C)

**Potential Failure Points:**
- H-E1 failure: Q_early calibration unstable (R2/Critical) → entire decomposition invalid
- H-M1 failure: WebGPT worker ID granularity insufficient (R4) → dose-response underpowered
- H-M4 failure: Benchmark degradation absent → annotation drift is not consequential for alignment quality at GPT-2 scale

**Conditions Under Which H0 Would Be Supported:**
- Interaction term round × high_ambiguity non-significant or negative across both datasets
- WebGPT β_exposure ≤ 0 after worker fixed effects
- Spearman ρ ≤ 0.2 between AAI and TruthfulQA/BBH degradation for both benchmarks
- Or positive correlation (higher AAI → better benchmarks) suggesting drift is adaptive

### 6.3 Synthesis

**Balanced Assessment:** The hypothesis H-AAI-v1 presents a theoretically grounded, empirically testable claim that annotation adaptation corrupts RLHF training signals. The null hypothesis raises legitimate concerns about the identification strategy (cohort turnover vs. individual adaptation) and the generalizability from annotation settings to model behavior at current scale.

**Resolution Path:** The verification plan directly addresses this dialectic through a sequential gate architecture:
1. **H-E1 (Foundation):** Establishes that drift signal exists in the data before claiming mechanism — distinguishes real signal from noise; bootstrap cohort-turnover null provides direct test of H0's cohort-turnover explanation
2. **H-M1 (Mechanism):** The dose-response design in WebGPT (continuous exposure variable + worker fixed effects) provides the strongest available within-annotator identification, directly testing the individual adaptation mechanism vs. cohort selection explanation
3. **H-M2→H-M4 (Chain):** Sequential mechanism tests provide multiple independent opportunities to detect or refute H0 — failure at any gate provides informative evidence about where the causal chain breaks

**Conditions for Thesis Support:**
- H-E1 gate passes (Q_early calibration stable; drift directional and ambiguity-modulated)
- H-M1 gate passes (dose-response confirmed in WebGPT)
- H-M4 Spearman ρ > 0.4 and negative direction

**Conditions for Antithesis Support:**
- H-E1 gate fails (drift absent or non-directional after Q_early recalibration)
- H-M1 fails (β_exposure ≤ 0 after worker FE)
- H-M4 ρ ≤ 0.2 for both benchmarks

**Nuanced Outcome Possibilities:**
1. **Full Support:** All 5 hypotheses pass → AAI validated as monitoring instrument; full causal chain demonstrated → NeurIPS-level contribution
2. **Partial Support (H-E1 + H-M1 pass, H-M4 weak):** Drift exists and mechanism confirmed; benchmark impact at current scale too small to detect → report with power analysis; valid for workshop publication
3. **Existence Only (H-E1 passes, H-M1 fails):** Drift exists in data but mechanism is cohort-level, not individual adaptation → valuable observational finding; reframe as "RLHF annotation drift" without automation bias mechanism
4. **Full Null (H-E1 fails):** No drift detected after Q_early recalibration → constitutes empirical evidence that RLHF annotation preferences are temporally stable → publishable robustness result

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution in Verification Plan |
|--------|-----------------|----------------------|----------------------------------|
| Existence | Temporal stylistic drift present in H-RLHF annotation rounds | May be cohort turnover artifact, not individual adaptation | Bootstrap cohort-turnover null (H-E1); within-annotator design in WebGPT (H-M1) |
| Mechanism | Automation bias induces ambiguity-modulated norm internalization | Rational Bayesian updating: annotators correctly track improved AI quality | Q_early affine recalibration go/no-go gate (H-E1/H-M2); ambiguity modulation specificity test (H-M1) |
| Signal | Drift contaminates reward model training signal | Reward models may be robust to label distribution shift at training scale | Split-training behavioral divergence test (H-M3); random-split control comparison |
| Impact | Benchmark degradation from stylistic reward bias | Effect too small at GPT-2 scale; may not generalize to production models | Full TruthfulQA + BBH evaluation (H-M4); mediation analysis for length confound |
| Validity | AAI triangulates three independent signals | Individual AAI components may be correlated, not independent | Component-wise criterion validity against TruthfulQA/BBH (confirmed by Prof. Pax) |

**Overall Robustness Score:** Medium-High
- Strong theoretical grounding and multi-method design
- Key vulnerability: Q_early calibration stability (go/no-go gate — if this fails, downstream analyses are invalid)
- Informative under all outcome scenarios

**Confidence in Verification Plan:** 0.72 (aligned with Phase 2A confidence level)

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** H-AAI-v1 — RLHF annotators exhibit directional stylistic drift toward AI-typical features under repeated annotation exposure, measurable via the Alignment Asymmetry Index (AAI), with downstream benchmark degradation.
- Confidence: 0.72; Scope reduction: 38% (5 BUILD_ON claims excluded)

**Verification Structure:**
- Mode: Incremental (Phase 2A Dialogue data available)
- Sub-Hypotheses: 5 total — H-E1 (Existence), H-M1–H-M4 (Mechanism, 4-step causal chain)
- Phases: 2 phases over 7 weeks
- Critical Gates: 2 MUST_WORK gates (H-E1, H-M1) + 3 SHOULD_WORK gates (H-M2–H-M4)
- Critical go/no-go: Q_early calibration stability (R2, pre-analysis gate)

**Risk Assessment:** Medium-High
- Primary concern (Critical): Q_early calibration stability — must verify before downstream analyses
- Secondary concern (High): HH-RLHF annotator continuity across rounds (R1); AI-typicality vector discriminant validity (R3)

**Immediate Action:** Begin Phase 1 with H-E1 — download HH-RLHF and WebGPT datasets, run Q_early calibration gate first

### 7.2 Conclusions

**Key Achievements:**
- 5 sub-hypotheses defined across 2 verification phases (7 weeks total)
- H0 (null hypothesis) fully addressed: sequential gate architecture tests cohort-turnover alternative at H-E1; within-annotator design at H-M1
- Both PROVE_NEW claims (PN1, PN2, PN3) covered: H-E1 → PN1; H-M1–H-M3 → PN2; H-M4 → PN3
- All BUILD_ON claims (5) excluded from re-verification per Established Facts registry

**Verification Execution Order:**

Phase 1: Foundation (Weeks 1-2)
- H-E1: Temporal stylistic coefficient drift in HH-RLHF (Q_early calibration gate → round-conditioned regression → ambiguity interaction)
- Gate 1 (MUST_WORK): End of Week 2

Phase 2: Core Mechanisms (Weeks 3-7)
- H-M1: Exposure-dependent norm internalization via WebGPT dose-response + HH-RLHF ambiguity modulation (Weeks 3-4)
- H-M2: Label-level AI-typicality upweighting in early vs. late round preference predictors (Week 5)
- H-M3: Split-training reward model behavioral divergence test (Week 6)
- H-M4: PPO fine-tuned model TruthfulQA/BBH evaluation + AAI Spearman correlation (Week 7)
- Gate 2 (SHOULD_WORK): End of Week 7

**Critical Decision Points:**

1. **Pre-analysis Gate (Q_early Calibration):** Before any analysis — verify Brier score difference < 0.02 across rounds after affine recalibration. FAIL → STOP, pivot to alternative quality control before proceeding.

2. **Gate 1 (H-E1, MUST_WORK):** End of Week 2. FAIL → STOP entire pipeline; reassess main hypothesis H-AAI-v1 (null result = valuable robustness evidence).

3. **Gate 2a (H-M1, MUST_WORK):** End of Week 4. FAIL → PIVOT mechanism framing (drop automation-bias specificity; retain broader drift observation).

4. **Gate 2 (H-M4, SHOULD_WORK):** End of Week 7. FAIL (ρ ≤ 0.2) → EXPLORE positive-ρ interpretation; document full uncertainty bounds.

**Open Questions (from Phase 2A):**
- Are HH-RLHF annotator worker IDs available in the public dataset? (Determines within-annotator vs. cohort-level analysis for H-M1)
- What is the actual distribution of annotation rounds in HH-RLHF — are the 3 rounds equal in size? (Power analysis input for Phase 2C)
- Does WebGPT comparison dataset have sufficient within-worker variation in exposure counts? (R4 mitigation)
- What is baseline variance in TruthfulQA/BBH for GPT-2-scale RLHF models? (Needed for Phase 2C power analysis — effect size threshold anchoring)

**Recommendations:**

1. **Immediate Actions:**
   - Verify HH-RLHF annotator ID availability in dataset documentation before committing to within-annotator design
   - Run Q_early calibration feasibility check on round-1 data before full pipeline execution
   - Set CUDA_VISIBLE_DEVICES to single empty GPU before any training

2. **Resource Allocation:**
   - Allocate 7 weeks for critical path (no slack — all sequential)
   - Reserve 2-week buffer for Q_early gate failure investigation
   - GPU: Single GPU sufficient per Prof. Pax assessment (< 4h total compute)

3. **Failure Management:**
   - Document all gate outcomes in verification_state.yaml immediately after each gate evaluation
   - Execute PIVOT strategies for R1 (cohort-level fallback) and R3 (topic-residualized vector) proactively if early indicators appear
   - Treat null result (H-E1 FAIL) as publishable finding about RLHF annotation stability

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: 03_refinement.yaml (Hypothesis ID: H-AAI-v1, generated 2026-05-03, schema v10.0.0)
- Supplementary: 02_synthesis.yaml (measurement plan, validation strategy), 01_round_table/final_opinions.yaml (agent assessments)
- All 6 Phase 2A convergence criteria met (15 discussion exchanges)

**B. MCP Tool Usage Summary**
- Total MCP calls: 0 (no-mcp test environment — TEST_bi_align_3)
- Analytical substitution: All hypothesis generation, risk analysis, and dialectical analysis performed via direct Phase 2A data extraction and domain reasoning
- Note: In production environment, mcp__clearThought__scientificmethod would be called 3x (H-E1, H-M integrated, H-M4 AAI validation) and mcp__clearThought__collaborativereasoning 1x (risk analysis expert panel)

---

*Generated by YouRA Phase 2B (v6.0 Step-File Architecture) | 2026-05-03*
*Workflow: phase2b-planning | Mode: UNATTENDED | Research: Incremental*
