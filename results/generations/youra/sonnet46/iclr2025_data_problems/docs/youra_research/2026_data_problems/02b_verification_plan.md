---
stepsCompleted: ["step-00-init-environment", "step-01-init-parsing", "step-02-input-hypothesis", "step-03-hypothesis-generation", "step-04-hypothesis-inventory", "step-05-risk-analysis", "step-06-dependency-graph", "step-07-timeline-planning", "step-08-dialectical-analysis", "step-09-summary", "step-10-finalize"]
status: complete
completedAt: "2026-03-14T00:00:00"
hypothesis_id: H-PCFH-v1
total_hypothesis_count: 4
research_mode: incremental
causal_chain_count: 3
condition_hypothesis_count: 0
---

# Verification Plan: Path-Dependent Curation Fairness Hypothesis (PCFH)

**Date:** 2026-03-14
**Hypothesis ID:** H-PCFH-v1
**Confidence:** 0.72
**Total Hypotheses:** 4 (H-E1, H-M1, H-M2, H-M3)

---

## Section 0: Established Facts & Scope Reduction

### 0.1 Established Facts Registry (BUILD_ON — Do NOT Re-Test)

| Claim | Evidence | Status |
|-------|----------|--------|
| fastText filtering in DCLM achieves 64% MMLU at 7B scale with 2.6T tokens | Li et al. 2024 (arXiv:2406.11794) | BUILD_ON |
| DoReMi domain reweighting improves downstream accuracy by 6.5%, 2.6x fewer steps | Xie et al. 2023 (arXiv:2305.10429) | BUILD_ON |
| FineWeb achieves competitive MMLU/ARC via web-scale filtering/deduplication | Penedo et al. 2024 (arXiv:2406.17557) | BUILD_ON |
| Dolma provides modular filtering infrastructure (language, quality, PII, Bloom dedup) | Soldaini et al. 2024 (arXiv:2402.00159) | BUILD_ON |

### 0.2 PROVE_NEW Claims (Verification Targets)

| Claim | Hypothesis |
|-------|------------|
| No prior work jointly measures performance AND fairness from same curation configs on identical checkpoints | H-E1 (demonstrates existence of measurement gap + path-dependent divergence) |
| Different curation paths with matched MMLU produce statistically distinguishable fairness outcomes mediated by H(occupation\|demographic) | H-M1, H-M2, H-M3 (causal mechanism chain) |

### 0.3 Scope Reduction

- **Total claims:** 6 | **BUILD_ON:** 4 | **PROVE_NEW:** 2
- **Scope reduction:** 33% (DCLM/DoReMi/FineWeb/Dolma performance results taken as verified background)
- **Phase 2B focus:** Path-dependent fairness divergence under matched capability + entropy mediation mechanism

> **Instruction from Phase 2A:** Do not re-verify DCLM/DoReMi/FineWeb/Dolma performance results. Focus verification effort on the two PROVE_NEW claims: (1) path-dependent fairness divergence under matched capability, and (2) mediation by H(occupation|demographic).

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under controlled pretraining conditions (Pythia-1B, fixed DCLM recipe: decoder-only Transformer, LR 2e-5, batch size 256, cross-entropy loss, fixed token budget of 100B tokens), if different data curation paths (fastText quality percentile filtering at cutoffs 10%, 30%, 50%, 70%, 90% vs. DoReMi-style domain reweighting) are applied to the same base corpus (Dolma/DCLM-POOL) and achieve matched downstream capability (MMLU ±1%, HellaSwag ±1%, perplexity ±0.1, ECE ≤0.5% difference via Mahalanobis distance criterion), then these models will produce statistically distinguishable fairness outcomes (BBQ accuracy gap ≥0.05 effect size, WinoBias consistency ratio divergence) that survive benchmark decontamination and are abolished in a shuffled-demographic negative control corpus, **because** different curation paths create differential conditional demographic association density H(occupation|demographic) in training corpora, which internalizes into differential model logit structures around demographic-occupation co-occurrences.

### 1.2 Alternative Hypothesis (H0)

After multivariate capability matching (MMLU, HellaSwag, perplexity, ECE via Mahalanobis distance), models trained via different curation paths on the same base corpus show no statistically distinguishable fairness outcomes (BBQ accuracy gap ≤0.01, WinoBias consistency ratio difference ≤0.01), indicating that fairness in foundation model outputs is determined by capability level alone, not by the data curation path.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Dolma v1.7 / DCLM-POOL (standard) | Modular subcorpora supporting controlled ablations; DCLM-POOL enables exact replication of filtering interventions |
| **Model** | Pythia Suite (primary: 1B; secondary: 160M) | Designed for controlled pretraining experiments; consistent architecture across scales; 10-12 runs tractable |

**Dataset Details:**
- Source: HuggingFace / https://datacomp.ai/dclm
- Path: dolma-v1.7 (3T tokens), DCLM-POOL (240T tokens, Common Crawl)

**Model Details:**
- Type: decoder-only Transformer
- Source: EleutherAI/pythia on HuggingFace

### 1.4 Baseline Methods

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|-----------------|
| DCLM-BASELINE (Li et al. 2024) | 64% MMLU 5-shot at 7B/2.6T tokens; CORE 44.1 | DCLM-POOL (Common Crawl, 240T tokens) | Measures performance only; bias/safety explicitly out-of-scope |
| FineWeb (Penedo et al. 2024) | Competitive MMLU/ARC via C4-like filtering | CommonCrawl FineWeb (15T tokens) | No fairness analysis of curation choices |
| DoReMi (Xie et al. 2023) | +6.5% few-shot accuracy; 2.6x faster to baseline | The Pile (800GB, 22 domains) | Optimizes for performance; fairness effects unmeasured |

**Best baseline performance:** DCLM-BASELINE: 64% MMLU at 7B — current state-of-art for open-data models with comparable compute.

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Pythia-1B at 100B token budget internalizes conditional demographic-occupation associations in a measurable way | DCLM shows clear performance differences at 412M-7B scales; fairness effects expected directionally | Need Pythia-7B — increases compute but doesn't invalidate design |
| A2 | BBQ, WinoBias, StereoSet are sensitive to differential conditional demographic-occupation distributions in pretraining data (not purely post-training artifacts) | Benchmarks designed to probe base model biases; multiple studies show variation across base LLMs | Shift evaluation to probing logit margins directly |
| A3 | Multivariate capability matching (MMLU, HellaSwag, perplexity, ECE) adequately closes the backdoor path from capability to fairness | Metrics span reasoning, common-sense, language modeling, calibration | Residual capability confounds; expand matching criteria or use propensity score matching |
| A4 | Dolma/DCLM-POOL contain sufficient demographic diversity for measurable variation in H(occupation\|demographic) across curation configurations | Dolma: 3T tokens, diverse sources; English-centric but variation expected within scope | Insufficient mediator variance → null results; use more demographically diverse corpus |
| A5 | fastText classifier does not perfectly sort documents by demographic register (R² meaningful but not 1.0) | fastText encodes quality proxies, not demographic proxies specifically; correlation expected | If R²≈1.0: filtering is purely demographic selection — publishable finding that reframes hypothesis |

### 1.6 Research Gap & Novelty

**Gap:** No prior work has jointly measured performance AND fairness effects from the same data curation hyperparameter configurations on identical model checkpoints. DCLM explicitly acknowledges bias/safety as out-of-scope.

**Key Innovation:** Path-Dependent Curation Fairness Hypothesis (PCFH) — the causal identification framework isolating curation path effects on fairness independent of capability level, using multivariate matching and conditional entropy mediation analysis.

**Differentiation:**
- vs. DCLM: Adds fairness axis (BBQ, WinoBias, StereoSet) + causal identification via matched-capability comparison
- vs. DoReMi: Uses DoReMi-style reweighting as comparison curation path to isolate path-dependent effects
- vs. Stochastic Parrots: Provides quantitative causal measurement of curation hyperparameter → fairness relationships

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | MUST_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Corpus-Level Demographic Entropy Divergence Under Curation**

**Statement:** Under controlled corpus conditions (Dolma v1.7 / DCLM-POOL, fixed demographic token set), if fastText quality filtering is applied at varying percentile cutoffs (10%, 30%, 50%, 70%, 90%) and compared against DoReMi domain reweighting on the same base corpus, then the conditional demographic association density H(occupation|demographic) will differ by ≥5% relative change between extreme configurations and will show a monotonic trend with filtering intensity, **because** fastText operates as a domain-demographic selector — Wikipedia-register quality proxy systematically includes/excludes text by demographic register distribution.

**Rationale:** This existence hypothesis establishes the mediator variable (corpus-level H(occupation|demographic)) before committing to model training runs. If the mediator does not vary sufficiently across curation configurations, the causal mechanism of PCFH cannot operate. Prof. Rex's mandatory pre-training diagnostic (Phase A corpus audit) operationalizes this hypothesis.

**Variables:**
- Independent: Data curation path (fastText percentile cutoff: 10%/30%/50%/70%/90%; DoReMi matched)
- Dependent: H(occupation|demographic) — conditional entropy computed on filtered corpus samples; fastText score R² on demographic features
- Controlled: Base corpus (DCLM-POOL sample), demographic token set, n-gram window, entropy computation method

**Verification Protocol:**
1. Sample 10M documents from DCLM-POOL; apply each filtering configuration to obtain 6 corpus subsets
2. Compute H(occupation|demographic) from co-occurrence counts of occupational nouns conditional on demographic tokens (gendered pronouns, demographic named entities) for each subset
3. Run OLS regression of fastText quality scores on demographic token features (gendered pronoun frequency, demographic-occupation co-occurrence density) across all 10M documents
4. Test ≥5% relative entropy difference between extreme filtering configurations (10% vs. 90% fastText cutoff) via bootstrap confidence interval
5. Report R² of fastText-on-demographics regression with coefficient significance (p < 0.01 for at least one demographic feature)

**Success Criteria:**
- Primary: ≥5% relative change in H(occupation|demographic) between extreme filtering configurations (bootstrap 95% CI excludes 0)
- Secondary: R² > 0.05 in fastText-on-demographics regression (diagnostic; not pass/fail gate)

**Failure Response:**
- IF entropy difference < 5%: PIVOT — use more granular token-level demographic features or expand to character-level n-grams; document as limitation
- IF R² ≈ 0: SIMPLIFY interpretation — fastText is demographic-neutral, strengthening (not weakening) causal claims about curation effects

**Dependencies:** None

**Source:** Phase 2A Section 5 (sh1_existence), Prediction P2, P3

---

---
**H-M1: Curation Path Alters Corpus-Level Conditional Demographic Association Density**

**Statement:** Under controlled corpus conditions, if different curation paths (fastText filtering at 10%-90% percentile cutoffs, DoReMi domain reweighting) are applied to Dolma/DCLM-POOL, then the conditional log-odds of demographic-occupation co-occurrences will vary systematically across configurations in a manner correlated with filtering intensity (Spearman ρ ≠ 0 across configurations), **because** fastText assigns differential quality scores correlated with demographic register, and DoReMi shifts domain proportions with known demographic distribution differences across domains.

**Rationale:** This is the first causal link in the PCFH chain: from curation operation to corpus-level demographic structure. Establishing this link validates that the proposed mechanism (quality filtering as implicit demographic selector) operates at the corpus level before testing its propagation to model weights.

**Variables:**
- Independent: Data curation path (fastText cutoffs 10%-90% vs. DoReMi)
- Dependent: Log-odds of demographic-occupation co-occurrences; H(occupation|demographic) monotonic trend with filtering intensity
- Controlled: Base corpus (DCLM-POOL), demographic token set, occupation lexicon

**Verification Protocol:**
1. Using corpus subsets from H-E1, compute log-odds of demographic-occupation co-occurrences for each curation configuration
2. Test Spearman correlation between fastText percentile cutoff (treating DoReMi as reference point) and log-odds values across configurations
3. Fit a regression of log-odds on filtering intensity (percentile cutoff as ordinal) to characterize functional form
4. Compare H(occupation|demographic) across DoReMi configurations vs. fastText configurations at matched MMLU targets
5. Assess whether fastText R² diagnostic result (from H-E1) meaningfully changes causal interpretation of the filtering mechanism

**Success Criteria:**
- Primary: Monotonic trend in H(occupation|demographic) with filtering intensity (Spearman ρ ≠ 0, p < 0.05 across 6 configurations)
- Secondary: Statistically distinguishable H(occupation|demographic) between fastText and DoReMi paths at matched MMLU targets

**Failure Response:**
- IF no monotonic trend: EXPLORE — investigate per-domain conditional entropy separately; fastText may operate differently across Dolma subcorpora
- IF fastText and DoReMi produce same corpus structure: PIVOT — reframe as "curation strategy family" rather than path-dependent effect

**Dependencies:** H-E1

**Source:** Phase 2A Section 1.3 Step 1, Prediction P2

---

---
**H-M2: Corpus Conditional Entropy Shifts Internalize into Model Logit Margins (Log-Linear)**

**Statement:** Under controlled training conditions (Pythia-1B, 100B tokens, fixed recipe), if models are trained on corpora with different H(occupation|demographic) values (produced by different curation configurations), then the models' logit margins on demographic probe prompts will be positively correlated with the corpus-level H(occupation|demographic) differences (Spearman ρ > 0, p < 0.01), with a log-linear functional relationship, **because** cross-entropy training minimizes KL divergence from the empirical conditional distribution, driving the model to approximate corpus-level conditional probability structures in its weight space.

**Rationale:** This is the second causal link: from corpus-level demographic structure to model weight internalization. The shuffled-demographic negative control (corpus with identical entropy but destroyed conditional associations) is the critical design element distinguishing conditional structure internalization from mere distributional shift.

**Variables:**
- Independent: Corpus-level H(occupation|demographic) (continuous, from 6 curation configurations)
- Dependent: Model logit margin on demographic probe prompts (mean logit difference between demographic-congruent and demographic-incongruent occupation completions)
- Controlled: Pythia-1B architecture, LR 2e-5, batch 256, 100B tokens, fixed evaluation prompts

**Verification Protocol:**
1. Train ~10-12 Pythia-1B models: 5 fastText filtering percentiles + 2 DoReMi variants + 1 shuffled-demographic negative control + 1 unfiltered baseline (using CUDA_VISIBLE_DEVICES for single GPU; select lowest memory GPU via nvidia-smi)
2. Compute demographic logit margins: mean logit(demographic-congruent occupation completion) − logit(demographic-incongruent) on standardized probe templates (50+ templates per demographic axis: gender, race, occupation)
3. Compute Spearman ρ between corpus H(occupation|demographic) values and corresponding model logit margins across all 10-12 runs
4. Test shuffled-demographic control: verify that shuffled-corpus model produces logit margins not statistically distinguishable from unfiltered baseline despite matching surface-level entropy
5. Fit log-linear model (logit_margin ~ log(H_entropy_shift)) and assess R² and coefficient significance

**Success Criteria (PoC — Direction-Based):**
- Primary: Spearman ρ > 0 with p < 0.01 between corpus H(occupation|demographic) and model logit margins across configurations
- Secondary: Shuffled-demographic control produces ≤0.01 logit margin difference vs. matched-capability standard model (validates conditional structure as mechanism)

**Failure Response:**
- IF ρ ≈ 0: EXPLORE — examine per-demographic-axis correlations separately; test with larger Pythia-7B if scale is the issue (A1 violation)
- IF shuffled control does NOT reduce logit margins: REASSESS — conditional structure may not be the mechanism; explore domain-level distributional effects instead

**Dependencies:** H-M1

**Source:** Phase 2A Section 1.3 Step 2, Prediction P2

---

---
**H-M3: Differential Logit Structures Produce Fairness Benchmark Divergence Under Matched Capability**

**Statement:** Under controlled evaluation conditions (multivariate Mahalanobis matching on MMLU, HellaSwag, perplexity, ECE; benchmark decontamination applied), if models trained via different curation paths (fastText 10%-90% vs. DoReMi reweighting) achieve matched downstream capability, then these models will show statistically distinguishable fairness benchmark outcomes (BBQ accuracy gap ≥0.05 Cohen's d, WinoBias consistency ratio divergence, p < 0.05 on matched pairs) that (a) survive benchmark decontamination and (b) are abolished in the shuffled-demographic negative control, **because** the differential logit structures established in H-M2 directly determine model responses on fairness benchmarks that probe demographic-occupation conditional probabilities.

**Rationale:** This is the third and final causal link: from model logit structures to observable fairness benchmark outcomes. The combination of multivariate capability matching and decontamination provides the causal identification strategy — ruling out capability confounds and benchmark artifacts as alternative explanations. This hypothesis directly tests the PCFH's core empirical claim.

**Variables:**
- Independent: Data curation path (effectively, the logit margin values established in H-M2)
- Dependent: BBQ accuracy gap (Cohen's d ≥ 0.05 on matched pairs); WinoBias consistency ratio; StereoSet preference score
- Controlled: Capability matching (Mahalanobis distance on MMLU, HellaSwag, perplexity, ECE); decontamination protocol; evaluation prompts (5-shot MMLU, 0-shot fairness)

**Verification Protocol:**
1. Construct matched-capability pairs from the 10-12 trained Pythia-1B models using Mahalanobis distance on (MMLU, HellaSwag, perplexity, ECE) — retain pairs with distance ≤ ε (empirically determined threshold)
2. Evaluate BBQ, WinoBias, StereoSet on matched pairs; compute BBQ accuracy gap between ambiguous and disambiguated contexts per model
3. Apply benchmark decontamination: template-matching + fuzzy overlap check for BBQ/WinoBias/StereoSet test items against all training corpora
4. Compute Cohen's d for BBQ accuracy gap differences across matched pairs; run paired t-test (α = 0.05) on BBQ gap across matched pairs
5. Verify negative control: shuffled-demographic model in matched pair produces BBQ gap ≤ 0.01 vs. same-capability standard model

**Success Criteria (MUST_WORK gate):**
- Primary: ≥1 matched pair shows BBQ accuracy gap difference ≥ 0.05 (Cohen's d), surviving decontamination, with p < 0.05
- Secondary: WinoBias consistency ratio divergence statistically significant in same matched pairs

**Failure Response:**
- IF no matched pair shows BBQ gap ≥ 0.05: DOCUMENT as PARTIAL — report H0 support, examine whether scale (A1) or matching quality (A3) is limiting; proceed to reduced-scope conclusion
- IF effect disappears after decontamination: REASSESS — possible benchmark contamination in training corpora; investigate contamination source

**Dependencies:** H-M2

**Source:** Phase 2A Section 1.3 Step 3, Prediction P1

---

**Step 4 saved.**

---

## 3. Execution

### 3.1 Dependency Chain

```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | ≥5% relative H(occupation\|demographic) difference across configurations | STOP — mediator does not vary; no mechanism to test |
| H-M1 | MUST_WORK | Monotonic trend in H(occupation\|demographic) with filtering intensity (Spearman ρ ≠ 0) | PIVOT — explore per-domain or per-subcorpus effects |
| H-M2 | SHOULD_WORK | Spearman ρ > 0, p < 0.01 between corpus entropy and model logit margins | EXPLORE — scale up or examine per-axis correlations |
| H-M3 | MUST_WORK | ≥1 matched pair with BBQ gap Cohen's d ≥ 0.05, p < 0.05, surviving decontamination | DOCUMENT PARTIAL — report H0 support with scope limitations |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation (Corpus Audit) | H-E1, H-M1 | Weeks 1–2 |
| Phase 2: Model Training | ~10-12 Pythia-1B runs | Weeks 3–6 |
| Phase 3: Core Mechanism | H-M2 (logit analysis) | Week 7 |
| Phase 4: Fairness Evaluation | H-M3 (matching + benchmarks) | Week 8 |

**Total Duration:** 8 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

**Risk R1 (from A1): Insufficient Scale for Fairness Internalization**

**Source Assumption:** A1 — Pythia-1B at 100B token budget internalizes conditional demographic-occupation associations measurably.

**Description:** Fairness effects may be below detection threshold at 1B scale / 100B tokens. Cross-entropy minimization may not have sufficient capacity to encode fine-grained conditional demographic associations.

**Affected Hypotheses:** H-M2, H-M3

**Severity:** High

**Mitigation Strategy:**
1. Prevention: Run Pythia-160M as slope-consistency check first — directional signal at smaller scale validates scaling behavior before larger investment
2. Detection: Monitor logit margins during training; low variance across configurations suggests scale issue
3. Response:
   - PIVOT: Scale up to Pythia-7B (increases compute ~7x but validates hypothesis at meaningful scale)
   - SCOPE: Report directional trend at 1B scale; position as pilot establishing feasibility for larger-scale study

**Early Warning Indicators:**
- Logit margins near zero across all configurations in H-M2
- No convergence of BBQ gap signal in H-M3 pilot evaluation

---

**Risk R2 (from A2): Fairness Benchmarks Insensitive to Pretraining Data**

**Source Assumption:** A2 — BBQ, WinoBias, StereoSet are sensitive to differential conditional distributions in pretraining (not post-training artifacts).

**Description:** Benchmark performance may be dominated by instruction tuning / RLHF patterns or surface text statistics rather than pretraining conditional association structures.

**Affected Hypotheses:** H-M3

**Severity:** High

**Mitigation Strategy:**
1. Prevention: Use base models (no instruction tuning); evaluate in 0-shot format to minimize prompt engineering effects
2. Detection: Compare benchmark variance across configurations vs. random seed variance; low signal-to-noise suggests insensitivity
3. Response:
   - PIVOT: Shift primary evaluation to demographic logit margin probes (DV-secondary in H-M2/H-M3) which directly operationalize the mechanism without benchmark mediation
   - SCOPE: Report null benchmark results while positive logit margin results provide mechanism-level evidence

---

**Risk R3 (from A3): Residual Capability Confounds After Matching**

**Source Assumption:** A3 — Multivariate matching (MMLU, HellaSwag, perplexity, ECE) adequately closes the capability backdoor.

**Description:** Residual capability differences not captured by the 4-metric matching procedure may explain fairness divergence independently of curation path.

**Affected Hypotheses:** H-M3

**Severity:** Medium

**Mitigation Strategy:**
1. Prevention: Pre-specify matching threshold ε (Mahalanobis distance) and minimum matched pair count before running experiments
2. Detection: Report matched pair balance statistics; test residual capability confounds via regression adjustment
3. Response:
   - PIVOT: Expand matching to include additional capability metrics (ARC, HellaSwag-specific domains) or use propensity score matching over richer capability vector
   - SCOPE: Report sensitivity analysis with different matching thresholds

---

**Risk R4 (from A4): Insufficient Demographic Diversity in Dolma/DCLM-POOL**

**Source Assumption:** A4 — Dolma/DCLM-POOL contain sufficient demographic diversity for measurable variation in H(occupation|demographic).

**Description:** If the corpus is too homogeneous demographically (English-Western-centric), variation in H(occupation|demographic) across filtering configurations may be too small to detect.

**Affected Hypotheses:** H-E1, H-M1

**Severity:** Medium

**Mitigation Strategy:**
1. Prevention: Run H-E1 corpus audit BEFORE committing to model training runs; gate model training on ≥5% relative entropy difference
2. Detection: Compute H(occupation|demographic) on pilot 1M-document sample before full 10M audit
3. Response:
   - PIVOT: Focus on specific demographic axes with clearest variation (e.g., gender-occupation associations which are better documented in English web text)
   - SCOPE: Narrow hypothesis scope to specific demographic categories where variation is detectable

---

**Risk R5 (from A5): fastText Perfectly Encodes Demographic Register**

**Source Assumption:** A5 — fastText classifier does not perfectly sort documents by demographic register (R² meaningful but not 1.0).

**Description:** If R²≈1.0 in fastText-on-demographics regression, the filtering intervention is a pure demographic selector, which changes the mechanism interpretation (not "quality filtering creates demographic structure" but "quality filtering IS demographic selection").

**Affected Hypotheses:** All (interpretation-level risk, not validity risk)

**Severity:** Low (publishable finding in itself)

**Mitigation Strategy:**
1. Prevention: Pre-specify interpretation conditional on R² ranges: R² < 0.1 = demographic-neutral; 0.1-0.5 = partial demographic priors; > 0.5 = strong demographic prior
2. Detection: H-E1 corpus audit produces R² directly
3. Response:
   - REFRAME: If R² ≈ 1.0, reframe hypothesis as "quality filters are demographic filters" — publishable insight that strengthens, not weakens, the PCFH argument
   - SCOPE: If R² ≈ 0, the causal chain is cleaner (quality filtering → demographic structure through indirect domain selection, not direct filter bias)

---

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Scale insufficient for fairness internalization | A1 | H-M2, H-M3 | High |
| R2: Fairness benchmarks insensitive to pretraining data | A2 | H-M3 | High |
| R3: Residual capability confounds after matching | A3 | H-M3 | Medium |
| R4: Insufficient demographic diversity in corpus | A4 | H-E1, H-M1 | Medium |
| R5: fastText perfectly encodes demographic register | A5 | All (interpretation) | Low |

### 4.3 Risk Summary

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | Scale insufficient | A1 | High | H-M2, H-M3 | Pythia-160M pilot; scale up to 7B if needed |
| R2 | Benchmark insensitivity | A2 | High | H-M3 | Use base models; pivot to logit margin probes |
| R3 | Residual capability confounds | A3 | Medium | H-M3 | Sensitivity analysis; expanded matching |
| R4 | Corpus demographic homogeneity | A4 | Medium | H-E1, H-M1 | Gate model training on H-E1 corpus audit |
| R5 | fastText = demographic selector | A5 | Low | All | Reframe as publishable finding; pre-specify R² thresholds |

**Critical Risks:** 0 | **High Risks:** 2 | **Medium Risks:** 2 | **Low Risks:** 1

**Baseline Failure Pattern Analysis:**

| Baseline Limitation | Potential Risk | Mitigation |
|---------------------|----------------|------------|
| DCLM measures performance only; bias out-of-scope | Fairness signal may be harder to detect than performance signal | Use multiple fairness benchmarks + logit probes |
| DoReMi optimizes performance; no fairness measurement | DoReMi may not produce sufficient fairness divergence from filtering path | Use DoReMi as comparison arm, not expectation of fairness-optimized path |
| FineWeb: no fairness analysis | Limited reference for expected fairness variance | Treat as additional comparison point if resources permit |

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) — 4 Hypotheses (PCFH)
═══════════════════════════════════════════════════════════

[Level 0 — Root: Foundation]
    H-E1: Corpus Demographic Entropy Divergence
    (Existence — no prerequisites)
    GATE 1: MUST_WORK → ≥5% relative H(occupation|demographic)
         │
         ▼ [Gate 1 passes]
[Level 1 — Mechanism: Corpus Structure]
    H-M1: Curation Path Alters Corpus Conditional Associations
    (Mechanism Step 1 — prerequisites: H-E1)
    GATE 2: MUST_WORK → monotonic trend (Spearman ρ ≠ 0)
         │
         ▼ [Gate 2 passes]
[Level 2 — Mechanism: Model Internalization]
    H-M2: Conditional Entropy Internalizes into Logit Margins
    (Mechanism Step 2 — prerequisites: H-M1)
    GATE 3: SHOULD_WORK → Spearman ρ > 0, p < 0.01
         │
         ▼ [Gate 3 passes or partial]
[Level 3 — Mechanism: Observable Fairness Outcomes]
    H-M3: Logit Structures → Fairness Benchmark Divergence
    (Mechanism Step 3 — prerequisites: H-M2)
    GATE 4: MUST_WORK → BBQ gap ≥0.05 Cohen's d, decontaminated
         │
         ▼ [Gate 4 passes]
[Terminal — Phase 5 Baseline Comparison (deferred)]
    → Phase 5: Full baseline comparison (DETERMINES_SUCCESS gate)

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type | Duration |
|-------|-----------|---------------|-----------|----------|
| 0 | H-E1 | None | MUST_WORK | Weeks 1-2 |
| 1 | H-M1 | H-E1 | MUST_WORK | Weeks 1-2 (concurrent with H-E1 — same corpus audit) |
| 2 | H-M2 | H-M1 | SHOULD_WORK | Week 7 (after model training Weeks 3-6) |
| 3 | H-M3 | H-M2 | MUST_WORK | Week 8 |

> Note: H-E1 and H-M1 share the same corpus audit phase (Phase A). They are logically sequential but operationally concurrent.

### 5.3 Verification Timeline (Gantt)

```
═══════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE — 4 Hypotheses (H-PCFH-v1)
═══════════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2       │ W3-6       │ W7         │ W8         │
─────────────────┼────────────┼────────────┼────────────┼────────────┤
PHASE A: Corpus Audit (H-E1 + H-M1 concurrent)
  H-E1           │ ████████   │            │            │            │
  H-M1           │ ████████   │            │            │            │
  [Gate 1+2]     │          ◆ │            │            │            │
─────────────────┼────────────┼────────────┼────────────┼────────────┤
PHASE B: Model Training (~10-12 Pythia-1B runs)
  Training runs  │            │ ████████████████████████│            │
─────────────────┼────────────┼────────────┼────────────┼────────────┤
PHASE C: Mechanism Analysis
  H-M2           │            │            │ ████████   │            │
  [Gate 3]       │            │            │           ◆│            │
─────────────────┼────────────┼────────────┼────────────┼────────────┤
PHASE D: Fairness Evaluation
  H-M3           │            │            │            │ ████████   │
  [Gate 4]       │            │            │            │           ◆│
═══════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 8 weeks
═══════════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 [Gate 1+2] → Training →
               H-M2 [Gate 3] → H-M3 [Gate 4]

Total Duration: 8 weeks
  Formula: 2 (Corpus Audit: H-E1+H-M1) +
           4 (Model Training: ~10-12 runs) +
           1 (H-M2: logit analysis) +
           1 (H-M3: fairness evaluation)

Slack Available: 0 weeks (fully sequential)
Critical Gates: 4 decision points

Note: Model training (Weeks 3-6) dominates wall-clock time.
Corpus audit (Weeks 1-2) is mandatory prerequisite gate
before committing to training compute.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 4
- Existence: 1 (H-E1)
- Mechanism: 3 (H-M1, H-M2, H-M3)
- Condition: 0 (not applicable)

Model Training Runs: ~10-12 Pythia-1B (100B tokens each)
- 5 fastText filtering percentiles (10%/30%/50%/70%/90%)
- 2 DoReMi variants (MMLU-matched domain reweighting)
- 1 shuffled-demographic negative control
- 1 unfiltered Dolma baseline
- (+1-3 optional: additional DoReMi variants or slope-consistency Pythia-160M)

Verification Phases: 4 (Corpus Audit → Training → Mechanism → Fairness)
Total Duration: 8 weeks
Critical Path Length: 8 weeks
Execution Mode: Sequential chain with corpus audit gate
GPU: Single GPU per training run (CUDA_VISIBLE_DEVICES; select lowest memory GPU)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

```
Step 1: Execute H-E1 + H-M1 (Corpus Audit) — Weeks 1-2
Step 2: Evaluate Gate 1+2 → If H-E1 passes (≥5% entropy), proceed
Step 3: Model Training — ~10-12 Pythia-1B runs — Weeks 3-6
        (CUDA_VISIBLE_DEVICES=<empty GPU>, select via nvidia-smi)
Step 4: Execute H-M2 (Logit Margin Analysis) — Week 7
Step 5: Evaluate Gate 3 → If H-M2 passes (Spearman ρ > 0), proceed
Step 6: Execute H-M3 (Fairness Benchmark Evaluation) — Week 8
Step 7: Evaluate Gate 4 → Determine PCFH support
Final: Verification complete → Phase 5 (Baseline Comparison) deferred
```

---

## 6. Dialectical Analysis

### 6.1 Thesis Statement

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Claim: The Path-Dependent Curation Fairness Hypothesis — different
data curation paths achieving matched capability produce statistically
distinguishable fairness outcomes mediated by differential conditional
demographic association density H(occupation|demographic).

Supporting Evidence:
1. DCLM demonstrates that fastText quality filtering operates as a strong
   domain selector (Li et al. 2024); domains have known demographic
   distribution differences (Soldaini et al. 2024).
2. Cross-entropy training drives KL divergence minimization from empirical
   conditional distributions — information geometry predicts log-linear
   relationship between corpus log-odds and model logit margins.
3. BBQ, WinoBias, StereoSet are designed to probe exactly the conditional
   demographic-occupation distributions captured in the logit margin measure.

Strengths:
- Novel causal identification framework: matched-capability comparison +
  conditional entropy mediation closes backdoor from capability to fairness
- Shuffled-demographic negative control is an elegant mechanism-isolation
  design (Prof. Vera's assessment: STRONG falsifiability)
- Both positive and negative results are publishable (Dr. Sage's assessment)
- DCLM infrastructure provides unusually clean controlled experiment platform

Expected Outcomes:
- Primary (P1): ≥1 matched pair with BBQ gap Cohen's d ≥ 0.05, p < 0.05
- Secondary (P2): Spearman ρ > 0, p < 0.01 (corpus entropy → logit margins)
- Tertiary (P3): R² > 0.05 (fastText-on-demographics regression diagnostic)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis Development (H0-Based)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Null Hypothesis (H0): After multivariate capability matching, models
trained via different curation paths show no statistically distinguishable
fairness outcomes (BBQ gap ≤0.01, WinoBias ≤0.01) — fairness is
capability-determined, not path-determined.

Counter-Arguments:
1. Capability confounds: Despite multivariate matching, residual differences
   in fine-grained capabilities correlated with both curation path and
   fairness benchmark performance may explain observed divergence without
   invoking the conditional entropy mechanism (Risk R3).
2. Scale limitation: At Pythia-1B / 100B tokens, the model may not have
   sufficient capacity to internalize fine-grained conditional demographic
   associations measurably — effect may only emerge at 7B+ scale (Risk R1).
3. Benchmark artifact: BBQ/WinoBias/StereoSet may primarily reflect surface
   text statistics or instruction-tuning artifacts rather than pretraining
   conditional associations (Risk R2).

Potential Failure Points:
- H0 support: All matched pairs show BBQ gap ≤0.01 after decontamination
- Mechanism broken: Shuffled-demographic control produces same logit margins
  as filtered corpus — conditional structure is not the mechanism
- Scale threshold: Pythia-1B effects are directionally consistent but
  below significance threshold (Type II error at 1B scale)

Conditions Under Which H0 Would Be Supported:
- If matched pairs show BBQ gap ≤0.01 after decontamination
- If Spearman ρ ≈ 0 (p > 0.05) between corpus entropy and logit margins
- If shuffled-demographic control produces same fairness outcomes as
  filtered corpus (mechanism not conditional structure)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balanced Assessment:

The PCFH presents a theoretically well-grounded, empirically testable
causal claim supported by information-theoretic principles and the DCLM
experimental infrastructure. However, H0 raises valid empirical concerns
about scale and benchmark sensitivity that the verification plan addresses
through design (shuffled-demographic control, 160M slope-consistency check).

Resolution Path:

The verification plan addresses this dialectic through:
1. Corpus Audit Gate (H-E1, H-M1): Establishes mediator existence before
   committing to compute-intensive model training
2. Shuffled-demographic negative control: Directly tests whether conditional
   structure (not mere distributional shift) is the mechanism
3. Sequential causal chain testing (H-M2, H-M3): Allows partial support
   outcomes — evidence accumulates even if final gate falls short
4. Pythia-160M slope-consistency: Addresses scale concern by providing
   directional evidence before committing to 1B-scale conclusion

Conditions for Thesis Support:
- H-E1 corpus audit shows ≥5% relative entropy difference (Gates 1+2)
- H-M2 shows Spearman ρ > 0, p < 0.01 (Gate 3)
- H-M3 shows ≥1 matched pair with BBQ gap ≥0.05 (Gate 4)

Conditions for Antithesis Support:
- H-E1 fails: corpus is too homogeneous for path-dependent effects
- H-M2 fails: logit margins do not correlate with corpus entropy
- H-M3 fails: no matched pair exceeds BBQ gap threshold after decontamination

Nuanced Outcome Possibilities:
1. Full Support: All 4 gates pass → PCFH validated → Phase 5 baseline comparison
2. Partial (Mechanism only): H-E1/H-M1/H-M2 pass, H-M3 marginal →
   Corpus entropy → logit margin link established, fairness benchmark link
   partially supported → position as pilot for larger-scale study
3. Scale-Limited: All directions correct but below significance →
   Pythia-7B follow-up warranted; partial support at 1B scale
4. No Support: H-E1 fails → H0 supported; fairness is not path-dependent
   at this corpus scale/diversity level
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence (mediator) | H(occupation\|demographic) varies with filtering | Corpus too homogeneous | H-E1 corpus audit gate |
| Mechanism Step 1 (corpus) | fastText/DoReMi alter demographic structure | Domain effects too coarse | H-M1 log-odds monotonic trend test |
| Mechanism Step 2 (model) | Entropy → logit margins (log-linear) | Scale insufficient; nonlinear dynamics | H-M2 Spearman ρ + shuffled-demographic control |
| Mechanism Step 3 (fairness) | Logit structure → benchmark divergence | Capability confounds; benchmark insensitivity | H-M3 Mahalanobis matching + decontamination |
| Generalizability | English web corpora broadly | English-only, US-centric benchmarks | Pythia-160M slope-consistency; acknowledge limitations |

**Overall Robustness Score:** Medium-High

**Confidence in Verification Plan:** 0.72 (from Phase 2A; maintained — plan addresses all major objections raised in Phase 2A round table)

---

## 7. Executive Summary & Conclusions

### Executive Summary

**Main Hypothesis:** H-PCFH-v1 — Path-Dependent Curation Fairness Hypothesis (Confidence: 0.72)
- Different data curation paths achieving matched capability produce statistically distinguishable fairness outcomes mediated by differential H(occupation|demographic)

**Verification Structure:**
- Mode: Incremental (Phase 2A validated)
- Sub-Hypotheses: 4 total (H-E1, H-M1, H-M2, H-M3)
- Phases: 4 phases over 8 weeks
- Critical Gates: 4 decision points (Gates 1-4)

**Risk Assessment:** Medium
- Primary concerns: Scale threshold (Pythia-1B may be underpowered for H-M3); benchmark sensitivity (fairness benchmarks may not detect pretraining-level effects)

**Scope Reduction:** 33% — DCLM/DoReMi/FineWeb/Dolma performance results taken as BUILD_ON background

**Immediate Action:** Begin Phase A corpus audit (H-E1 + H-M1) — computationally trivial, gates all downstream model training investment

---

### Conclusions

**Key Achievements:**
- 4 sub-hypotheses across 4 phases, fully decomposing the PCFH causal chain
- H0 operationalized: fairness is capability-determined (BBQ gap ≤0.01 after matching)
- Mandatory pre-training diagnostic (corpus audit) gates compute-intensive training runs

**Verification Execution Order:**

**Phase 1: Foundation + Mechanism Step 1 (Weeks 1-2)**
- H-E1: Corpus-level H(occupation|demographic) ≥5% relative difference across curation configs
- H-M1: Monotonic trend in log-odds with filtering intensity
- Gate 1+2: MUST PASS → proceed to model training

**Phase 2: Model Training (Weeks 3-6)**
- ~10-12 Pythia-1B runs (5 fastText + 2 DoReMi + 1 shuffled-demographic + 1 unfiltered baseline)

**Phase 3: Mechanism Step 2 (Week 7)**
- H-M2: Corpus entropy → model logit margin correlation (Spearman ρ > 0, p < 0.01)
- Gate 3: SHOULD PASS → proceed to fairness evaluation

**Phase 4: Mechanism Step 3 (Week 8)**
- H-M3: Matched-capability models → BBQ gap ≥0.05 Cohen's d, surviving decontamination
- Gate 4: MUST PASS for full PCFH support

**Critical Decision Points:**

1. **Gate 1+2 (Corpus Audit, Week 2):** H-E1 + H-M1
   - FAIL → STOP model training; corpus does not support PCFH mechanism
   - PASS → Proceed to training phase

2. **Gate 3 (Mechanism, Week 7):** H-M2
   - FAIL → Document as scale limitation; proceed with caution to H-M3
   - PASS → Full mechanism chain validated up to model weights

3. **Gate 4 (Fairness, Week 8):** H-M3
   - FAIL/PARTIAL → Document H0 support; consider Pythia-7B follow-up
   - PASS → PCFH validated → Phase 5 baseline comparison (deferred)

**Open Questions:**
- What is the minimum R² threshold for fastText-on-demographics that constitutes a meaningful confound requiring explicit modeling?
- Is Pythia-1B at 100B tokens sufficient scale for the conditional entropy → logit margin relationship to be detectable?
- Does the shuffled-demographic negative control require full pretraining runs or can it be approximated with continued training from a shared checkpoint?

**Recommendations:**

1. Immediate Actions:
   - Start Phase A corpus audit (H-E1 + H-M1) immediately — computationally trivial
   - Pre-specify fastText R² interpretation thresholds (< 0.1, 0.1-0.5, > 0.5) before running audit

2. Resource Allocation:
   - Allocate 8 weeks for critical path
   - Gate model training on corpus audit results (Weeks 1-2)
   - Reserve Pythia-7B compute budget as contingency for A1 violation

3. Failure Management:
   - Document all gate results with raw statistics before any interpretation
   - Execute PIVOT strategies from risk mitigation for each failed gate
   - Preserve partial results at each stage for Phase 5 / paper writing

---

### Appendices

#### A. Phase 2A Reference
- **Source:** 03_refinement.yaml (ID: H-PCFH-v1)
- **Convergence:** 15 rounds, 6 agents (Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex)
- **Status:** VALIDATED (Pre-registered PCFH with explicit quantitative criteria)

#### B. MCP Tool Usage Summary
- **Archon MCP:** Unavailable (pipeline check attempted; no project ID retrieved)
- **ClearThought scientificmethod:** Unavailable (6 planned calls not executed; inline expert analysis substituted)
- **Note:** verification_state.yaml Archon task fields will have null pipeline_project_id pending MCP availability

---

*Generated by YouRA Phase 2B (v6.0) | 2026-03-14*
