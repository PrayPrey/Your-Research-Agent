---
hypothesis_id: "H-DomainExposureBenchmarkSpecificity-v1"
confidence_level: 0.75
total_hypothesis_count: 4
stepsCompleted:
  - "step-00-init-environment"
  - "step-01-init-parsing"
  - "step-02-input-hypothesis"
  - "step-03-hypothesis-generation"
  - "step-04-hypothesis-inventory"
  - "step-05-risk-analysis"
  - "step-06-dependency-graph"
  - "step-07-timeline-planning"
  - "step-08-dialectical-analysis"
  - "step-09-summary"
  - "step-10-finalize"
status: complete
completedAt: "2026-08-20"
---

# Verification Plan: Domain Exposure–Benchmark Specificity in Pre-trained LLMs

**Date:** 2026-08-20
**Hypothesis ID:** H-DomainExposureBenchmarkSpecificity-v1
**Confidence:** 0.75
**Total Hypotheses:** 4 (H-E1, H-M1, H-M2, H-M3)
**Research Mode:** Incremental (Phase 2A Dialogue loaded)
**Scope Reduction:** 33% (2 of 6 claims are BUILD_ON; only PROVE_NEW claims verified)

---

## Section 0: Established Facts & Scope Reduction

### Established Facts (BUILD_ON — DO NOT RE-VERIFY)

| Claim | Evidence |
|-------|----------|
| DCLM shows model-based filtering outperforms heuristic filtering (64% vs ~57% MMLU at 7B) | Li et al., 2024 (DCLM, 2406.11794), 398 citations |
| Pythia provides 154 checkpoints per model (70M–12B) with exact dataloaders | Biderman et al., 2023 (Pythia, 2304.01373), 2071 citations |
| The Pile has 22 known domains with published proportions | Gao et al., 2020 (The Pile, 2101.00027), 2969 citations |
| CoLoR-Filter achieves 11–25× data efficiency via task-conditioned filtering | Brandfonbrener et al., 2024 (CoLoR-Filter, 2406.10670), 19 citations |

### PROVE_NEW Claims (Verified by this plan)

1. No prior study has produced a per-filter × per-benchmark correlation matrix for existing checkpoints
2. Domain composition has domain-benchmark specific effects (Wikipedia → MMLU, Books → HellaSwag)

**Scope Reduction:** 33% — 4 BUILD_ON claims excluded from hypothesis generation.

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under the Pythia model family trained on The Pile (a fixed heterogeneous corpus with known domain proportions), if cumulative domain exposure trajectories are computed from exact dataloaders at 154 training checkpoints across 16 model sizes (70M–12B), then domain-specific coefficients in a panel regression (with model-size fixed effects) will reveal benchmark-specific effects: Wikipedia exposure positively predicts MMLU more than HellaSwag; Books exposure positively predicts HellaSwag and WinoGrande more than MMLU, because different domains contain different distributions of cognitive task patterns that selectively strengthen the capabilities tested by each benchmark.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in domain regression coefficients across benchmarks (β_d is identical for all domains d across MMLU, HellaSwag, ARC, WinoGrande after controlling for model scale via fixed effects).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | The Pile (standard) | The Pile is Pythia's training corpus with 22 known domains and exact proportions; Pythia's dataloaders allow reconstruction of which tokens each checkpoint saw, enabling domain exposure trajectory computation |
| **Model** | Pythia model suite | 16 model sizes (70M–12B), 154 checkpoints each, identical architecture and data — the cleanest existing controlled infrastructure for within-family analysis |

**Dataset Details:**
- Source: EleutherAI
- Path: HuggingFace: EleutherAI/the_pile

**Model Details:**
- Type: Autoregressive LM (GPT-NeoX architecture)
- Source: EleutherAI/pythia-* on HuggingFace

### 1.4 Baseline Methods

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|-----------------|
| DCLM holistic filtering benchmark | 64% MMLU at 7B (DCLM-Baseline) | DCLM-Pool (filtered CommonCrawl) | Reports aggregate improvements across 53 tasks; does not isolate per-domain effects on individual benchmarks |
| Pythia vs Pythia-dedup | +1–2pp on most benchmarks | The Pile / The Pile (deduplicated) | Single binary ablation; no continuous domain exposure variation; no per-benchmark breakdown published |
| RegMix domain mixing optimization | Optimizes validation loss via proxy models; ICLR 2025 Spotlight | Various | Targets validation loss not individual benchmark scores; no per-domain × per-benchmark coefficient matrix |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Pythia's data ordering is non-uniform, providing within-family domain exposure variation across 154 checkpoints | Large-scale datasets often interleaved in domain-proportional blocks; Pythia paper does not confirm uniform shuffling | Panel regression within Pythia collapses; fallback to cross-family design (n≥15 model families) |
| A2 | Domain exposure effects are approximately linear and additive | RegMix and DoReMi show linear mixing law fits are predictive at proxy-model scale | Linear regression underfits; need interaction terms or non-linear model; directional claim still testable with ANOVA |
| A3 | Contamination between The Pile and benchmark test sets does not systematically correlate with domain exposure trajectories | Contamination concentrated in web-crawled data; Wikipedia/Books may have lower contamination rates | Contamination-adjusted scores differ substantially; adjustment is mandatory pre-step |
| A4 | Model-size fixed effects adequately control for scale-related confounds | Standard econometric approach for panel data; scaling laws show clean log-linear scale effects | Residual scale confound biases domain coefficients; mitigation: within-scale subgroup regressions |
| A5 | 4 target benchmarks are sufficiently distinct in cognitive demands | These 4 are standard precisely because they probe different capabilities (knowledge, commonsense, reasoning, linguistic) | If all 4 show identical domain profiles, specificity claim fails — but would itself be a publishable null finding |

### 1.6 Research Gap & Novelty

**Gap:** No prior study has produced a per-filter × per-benchmark correlation matrix for existing Pythia checkpoints using the exact dataloader ordering as the source of within-family domain exposure variation.

**Key Innovation:** First use of Pythia's exact dataloader ordering to construct a within-family domain exposure panel dataset for benchmark-specific analysis — eliminates cross-family confounds that plague prior mixing studies.

**Differentiation:**
- vs. DCLM: Provides per-domain × per-benchmark resolution (not 53-task aggregate)
- vs. Pythia: Uses checkpoints for domain attribution (not memorization/scaling)
- vs. RegMix/DoReMi: Maps domain composition to individual benchmark capability profiles
- vs. CoLoR-Filter: Observational analysis at pre-training scale (not task-conditioned filtering)

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |

**Total: 4 hypotheses** (1 existence + 3 mechanism; 0 condition; H-CP deferred to Phase 5)

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Domain Exposure Trajectory Measurability

**Type:** EXISTENCE
**Gate:** MUST_WORK

**Statement:** Under the Pythia model family trained on The Pile, if cumulative domain exposure trajectories are computed from exact dataloaders at 154 training checkpoints × 16 model sizes, then the resulting domain exposure fractions vary non-trivially across checkpoints (variance std > 0.001 for ≥10 of 22 domains), demonstrating that within-family domain variation is measurable and the panel regression framework is applicable.

**Rationale:**
This is the foundational existence check. Before testing mechanism hypotheses, we must confirm that The Pile's data ordering is non-uniform enough to produce measurable variation in cumulative domain exposure across Pythia's 154 checkpoints. Without this, the entire panel regression framework collapses (A1 risk). If uniform shuffle is confirmed, the cross-family fallback design (n≥15 model families) activates.

**Variables:**
- Independent: Training checkpoint index (1–154)
- Dependent: Variance of cumulative domain exposure fraction across checkpoints (per domain)
- Controlled: Model architecture (fixed: GPT-NeoX), domain label taxonomy (fixed: 22 The Pile domains)

**Verification Protocol:**
1. Download Pythia dataloader indices from EleutherAI/pythia HuggingFace repositories for all 16 model sizes.
2. Map token indices to The Pile domain labels using pile_metadata; compute cumulative_domain_fraction[d,t] for all domains d and checkpoints t.
3. Compute variance of cumulative_domain_fraction[d,:] across t=1..154 for each domain d; count domains with std > 0.001.
4. Filter checkpoints where all 4 benchmark scores < 30% (early floor); verify ≥100 usable checkpoints remain per model size.
5. Report domain exposure variance matrix; flag if <10 domains show measurable variation → activate cross-family fallback.

**Success Criteria (PoC):**
- Primary: ≥10 of 22 domains show std(cumulative_exposure_fraction) > 0.001 across 154 checkpoints in at least 8 of 16 model sizes
- Secondary: Domain exposure variance matrix is consistent across model sizes (Spearman ρ > 0.7 between any two model-size variance rankings)

**Failure Response:**
- IF fails (std ≤ 0.001 for <10 domains): PIVOT to cross-family design (collect n≥15 model families with known corpus domain proportions)
- IF borderline: EXPLORE with relaxed threshold (std > 0.0005) and document limitation

**Dependencies:** None (root hypothesis)

**Source:** Phase 2A Section 5 (sh1_existence), Assumption A1

---

#### H-M1: Domain-Specific Cognitive Pattern Distributions

**Type:** MECHANISM — Step 1 of 3
**Gate:** MUST_WORK

**Statement:** Under analysis of The Pile domain content distributions, if cognitive task pattern proxies (entity density for Wikipedia, narrative coherence markers for Books, formal syntax frequency for GitHub) are computed per domain, then Wikipedia domains show significantly higher factual-association density than Books/GitHub domains, and Books domains show significantly higher narrative-coherence features than Wikipedia/GitHub, because domain content differences drive differential alignment with benchmark task demands.

**Rationale:**
This tests the first causal step: that domain content differences are real and systematic. The regression's ability to detect benchmark-specific β coefficients depends on domains having distinct cognitive pattern distributions. This is a lightweight content analysis check, not a full training experiment — it validates the theoretical bridge from domain content to benchmark-specific capability alignment.

**Variables:**
- Independent: The Pile domain label (22 domains)
- Dependent: Cognitive task pattern proxy scores (entity density, narrative coherence, formal syntax frequency)
- Controlled: Document length, sampling methodology (stratified random sample per domain)

**Verification Protocol:**
1. Sample 1,000 documents per The Pile domain (stratified random sample using pile_metadata).
2. Compute entity density (NER entity count / token count) as proxy for factual-association content.
3. Compute narrative coherence proxy (sentence-level discourse connective frequency) for Books-type domains.
4. Compute formal syntax proxy (bracket/keyword density) for GitHub/code domains.
5. Run one-way ANOVA across domains for each proxy; report effect sizes (η²) and pairwise comparisons (Wikipedia vs Books, Wikipedia vs GitHub).

**Success Criteria (PoC):**
- Primary: Wikipedia entity density significantly > Books entity density (p < 0.05, η² > 0.1)
- Secondary: Books narrative-coherence proxy significantly > Wikipedia proxy (p < 0.05)

**Failure Response:**
- IF fails: EXPLORE — domain content differences may be more subtle; narrow to top-4 most distinct domains and re-test H-M2/H-M3 with reduced domain set
- Failure does NOT invalidate H-E1; documents a scope limitation

**Dependencies:** H-E1 (must confirm domain exposure is measurable before content analysis is interpretable)

**Source:** Phase 2A Section 1.3 Causal Step 1

---

#### H-M2: Differential Capability Strengthening via Domain Exposure

**Type:** MECHANISM — Step 2 of 3
**Gate:** SHOULD_WORK

**Statement:** Under the Pythia checkpoint trajectory (154 checkpoints × 16 model sizes), if cumulative Wikipedia exposure increases during training, then MMLU scores increase proportionally more than HellaSwag scores at comparable training steps (and vice versa for Books exposure), because domain-specific exposure accumulation selectively strengthens the capabilities aligned with each domain's cognitive pattern distribution.

**Rationale:**
This tests whether the domain-capability alignment implied by H-M1 actually manifests in training dynamics. If Wikipedia exposure drives MMLU more than HellaSwag during training, this provides temporal evidence of the mechanism before the full panel regression (H-M3). This is a necessary bridge between content analysis (H-M1) and the regression framework (H-M3).

**Variables:**
- Independent: Cumulative Wikipedia exposure fraction and Books exposure fraction at each checkpoint t
- Dependent: ΔMMLU / ΔHellaSwag ratio at each checkpoint (relative improvement rates)
- Controlled: Total training tokens seen (absorbed by checkpoint index), model size (analyzed per-size)

**Verification Protocol:**
1. From H-E1 output, extract Wikipedia and Books cumulative exposure fractions across 154 checkpoints for 3 representative model sizes (70M, 1B, 6.9B).
2. Run lm-evaluation-harness v0.4 on all 154 checkpoints × 3 model sizes for MMLU (5-shot) and HellaSwag (10-shot); apply 13-gram decontamination.
3. Compute Spearman correlation: ρ(Wikipedia_exposure_t, MMLU_t) and ρ(Wikipedia_exposure_t, HellaSwag_t) for each model size.
4. Test: ρ(Wikipedia→MMLU) > ρ(Wikipedia→HellaSwag) via Fisher z-test.
5. Repeat for Books → HellaSwag vs MMLU; report all correlations with 95% CI.

**Success Criteria (PoC):**
- Primary: ρ(Wikipedia→MMLU) > ρ(Wikipedia→HellaSwag) for ≥2 of 3 representative model sizes (directional confirmation)
- Secondary: ρ(Books→HellaSwag) > ρ(Books→MMLU) for ≥2 of 3 model sizes

**Failure Response:**
- IF fails: EXPLORE — correlations may be masked by scale effects; check within-scale-group correlations; document as limitation but proceed to H-M3 (regression may still detect effects with full panel)

**Dependencies:** H-M1 (domain content differences confirmed), H-E1 (domain exposure trajectories measurable)

**Source:** Phase 2A Section 1.3 Causal Step 2, Prediction P1/P2

---

#### H-M3: Panel Regression — Benchmark-Specific Domain Coefficients

**Type:** MECHANISM — Step 3 of 3
**Gate:** SHOULD_WORK

**Statement:** Under a panel OLS regression of benchmark scores on cumulative domain exposure fractions (22 domains × 154 checkpoints × 16 model sizes = 2,464 observations) with model-size fixed effects, the estimated domain coefficients β will be benchmark-specific: β_Wikipedia > β_Books for MMLU (p < 0.05, one-tailed) and β_Books > β_Wikipedia for HellaSwag (p < 0.05), and a likelihood ratio test will reject the constrained model (shared β across benchmarks) in favor of the benchmark-specific model (FDR q < 0.05 for ≥2 of 6 pairwise benchmark comparisons), because domain exposures act as benchmark-specific predictors reflecting domain-capability alignment.

**Rationale:**
This is the primary quantitative test of the main hypothesis. H-M3 operationalizes the full causal chain (H-M1 content differences + H-M2 training dynamics) into a statistical framework that produces the per-domain × per-benchmark coefficient matrix — the key novel contribution. MUST pass directional tests P1/P2; LRT (P3) is the formal model comparison.

**Variables:**
- Independent: 22 cumulative domain exposure fractions (time-varying covariates) + log(model_params) (fixed effect)
- Dependent: Contamination-adjusted benchmark score (MMLU, HellaSwag, ARC-Challenge, WinoGrande)
- Controlled: Model-size fixed effects (16 levels), temporal autocorrelation (clustered standard errors by model size)

**Verification Protocol:**
1. Construct full panel dataset: (model_size_i, checkpoint_t, domain_exposure_d(t), benchmark_score(i,t)) for all 4 benchmarks.
2. Apply 13-gram decontamination; adjust scores; filter checkpoints with all-benchmark floor < 30%.
3. Run VIF diagnostics on 22-domain exposure matrix; apply PCA dimensionality reduction if VIF > 10 for any domain.
4. Fit panel OLS per benchmark: score(i,t) = α_i + Σ_d β_d × exposure_d(t) + γ × log(params_i) + ε; cluster SEs by model size.
5. Test P1: β_Wikipedia > β_Books for MMLU (one-tailed t-test); Test P2: β_Books > β_Wikipedia for HellaSwag; Test P3: LRT of benchmark-specific vs shared-β model with FDR correction.
6. Robustness: within-scale subgroup regressions (70M–400M vs 1B–12B); permutation null (1000 random domain label shuffles); report R² decomposition (domain variables over scale-only model).

**Success Criteria (PoC):**
- Primary: P1 confirmed (β_Wikipedia > β_Books for MMLU, p < 0.05, one-tailed)
- Primary: P2 confirmed (β_Books > β_Wikipedia for HellaSwag, p < 0.05, one-tailed)
- Secondary: P3 confirmed (LRT rejects shared-β model, FDR q < 0.05 for ≥2 benchmark pairs)
- Secondary: P4 — domain coefficient rankings consistent across small (70M–400M) and large (1B–12B) model groups (Spearman ρ > 0.7)

**Failure Response:**
- IF P1/P2 fail but P3 passes: EXPLORE — some benchmark pairs differentiate even if Wikipedia/Books directions don't hold; refine hypothesis scope
- IF all tests fail: PIVOT — test if removing temporal autocorrelation correction changes results; if still null, document as null finding (publishable) and route to Phase 0

**Dependencies:** H-M2 (training dynamics confirmed), H-M1 (content differences confirmed), H-E1 (domain trajectories measurable)

**Source:** Phase 2A Section 1.3 Causal Step 3, Sections 1.6 (Predictions P1–P4), Section 2 (experimental setup)

---

## 3. Execution

### 3.1 Dependency Chain

```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | ≥10 domains show std > 0.001 across checkpoints | STOP — activate cross-family fallback |
| H-M1 | MUST_WORK | Wikipedia entity density > Books (p < 0.05, η² > 0.1) | PIVOT — reduce domain set; explore subtler proxies |
| H-M2 | SHOULD_WORK | ρ(Wikipedia→MMLU) > ρ(Wikipedia→HellaSwag) for ≥2 model sizes | EXPLORE — proceed to H-M3 with limitation documented |
| H-M3 | SHOULD_WORK | P1+P2 confirmed (p < 0.05); P3 FDR q < 0.05 for ≥2 pairs | EXPLORE/PIVOT — null finding route or scope refinement |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3 | 3 weeks (1 week each after first) |

**Total Duration:** 5 weeks

---

## 4. Risk Analysis

### 4.1 Risk–Assumption Mapping

**R1: Data Ordering Uniformity (from A1)**
- **Source:** A1 — Pythia's data ordering may be uniformly shuffled
- **Severity:** CRITICAL
- **Likelihood:** Medium
- **Affected Hypotheses:** H-E1, H-M1, H-M2, H-M3 (all)
- **Mitigation:**
  1. Prevention: Verify Pythia dataloader documentation and The Pile tokenization pipeline before committing to panel design
  2. Detection: Compute cumulative domain exposure variance in H-E1; if std < 0.001 for >12 domains, uniform shuffle confirmed
  3. Response: PIVOT — activate cross-family design (n≥15 model families: Pythia, OLMo, Falcon, etc.) using published corpus domain proportions as cross-sectional IVs
- **Early Warning:** H-E1 variance results; check within first 2 days of execution

**R2: Multicollinearity of Domain Predictors (from A2)**
- **Source:** A2 — 22 domain exposure fractions are correlated (similar training dynamics)
- **Severity:** High
- **Likelihood:** Medium-High
- **Affected Hypotheses:** H-M3
- **Mitigation:**
  1. Prevention: Run VIF diagnostics before fitting final regression; apply PCA if VIF > 10
  2. Detection: Inspect VIF values; high condition number in design matrix
  3. Response: SCOPE — reduce to top-8 most distinct domains via PCA; report PCA-domain coefficients mapped back to original domain interpretation
- **Early Warning:** High correlation in domain exposure trajectory matrix (step 3 of H-M3 protocol)

**R3: Contamination–Domain Confound (from A3)**
- **Source:** A3 — contamination may correlate with domain exposure
- **Severity:** Medium
- **Likelihood:** Low
- **Affected Hypotheses:** H-M2, H-M3
- **Mitigation:**
  1. Prevention: Run 13-gram decontamination audit before any regression; treat as mandatory pre-step
  2. Detection: Compare raw vs contamination-adjusted scores; if delta > 3pp for any benchmark, flag
  3. Response: EXPLORE — report both raw and adjusted regressions; if directional conclusions differ, treat adjusted as primary

**R4: Scale Confound Residual (from A4)**
- **Source:** A4 — model-size fixed effects may not fully control scale confound
- **Severity:** Medium
- **Likelihood:** Low
- **Affected Hypotheses:** H-M3
- **Mitigation:**
  1. Prevention: Include log(params) as continuous covariate in addition to model-size fixed effects
  2. Detection: R² decomposition — compare domain-variable contribution over scale-only model
  3. Response: EXPLORE — report within-scale subgroup regressions (70M–400M, 1B–12B) separately

**R5: Benchmark Cognitive Overlap (from A5)**
- **Source:** A5 — 4 benchmarks may tap the same underlying competence
- **Severity:** Medium
- **Likelihood:** Low
- **Affected Hypotheses:** H-M3 (P3, P4)
- **Mitigation:**
  1. Prevention: Pre-check benchmark intercorrelation; if all pairwise ρ > 0.95, document limitation
  2. Detection: LRT comparing shared-β vs benchmark-specific-β models; if LRT is non-significant, H0 is supported
  3. Response: ACCEPT null finding — identical domain profiles across 4 benchmarks is itself a publishable finding that reframes the hypothesis for Phase 6

### 4.2 Risk Summary Table

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    RISK SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| ID | Risk                          | Source | Severity | Affected        | Mitigation        |
|----|-------------------------------|--------|----------|-----------------|-------------------|
| R1 | Uniform shuffle (no variation)| A1     | CRITICAL | All (H-E1→H-M3) | Cross-family pivot|
| R2 | Multicollinearity (22 domains)| A2     | High     | H-M3            | PCA fallback      |
| R3 | Contamination-domain confound | A3     | Medium   | H-M2, H-M3     | Mandatory decontam|
| R4 | Residual scale confound       | A4     | Medium   | H-M3            | Within-scale reg  |
| R5 | Benchmark cognitive overlap   | A5     | Medium   | H-M3 (P3/P4)   | Accept null finding|

Critical Risks: 1 (R1)
High Risks: 1 (R2)
Medium Risks: 3 (R3, R4, R5)
Low Risks: 0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) — 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 — Root / Foundation]
    H-E1: Domain Exposure Trajectory Measurability
    (EXISTENCE — no prerequisites)
    Gate: MUST_WORK
         │
         ▼
[Level 1 — Mechanism Step 1]
    H-M1: Domain-Specific Cognitive Pattern Distributions
    ← H-E1
    Gate: MUST_WORK
         │
         ▼
[Level 2 — Mechanism Step 2]
    H-M2: Differential Capability Strengthening
    ← H-M1
    Gate: SHOULD_WORK
         │
         ▼
[Level 3 — Mechanism Step 3]
    H-M3: Panel Regression — Benchmark-Specific Coefficients
    ← H-M2
    Gate: SHOULD_WORK
         │
         ▼
[TERMINAL — Phase 5 gate]
    Main Hypothesis Validated → Phase 5 Baseline Comparison
    (DETERMINES_SUCCESS gate)

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Depth: 4 levels
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy Table

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 DEPENDENCY HIERARCHY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Level | Hypothesis | Prerequisites | Gate Type   |
|-------|------------|---------------|-------------|
| 0     | H-E1       | None          | MUST_WORK   |
| 1     | H-M1       | H-E1          | MUST_WORK   |
| 2     | H-M2       | H-M1          | SHOULD_WORK |
| 3     | H-M3       | H-M2          | SHOULD_WORK |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE — 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis     │  W1–2    │  W3–4    │  W5      │
─────────────────────┼──────────┼──────────┼──────────┤
PHASE 1: Foundation  │          │          │          │
  H-E1               │ ████████ │          │          │
  [Gate 1: MUST_WORK]│        ◆ │          │          │
─────────────────────┼──────────┼──────────┼──────────┤
PHASE 2: Mechanisms  │          │          │          │
  H-M1               │          │ ████████ │          │
  H-M2               │          │      ████│ ████     │
  H-M3               │          │          │     █████│
  [Gate 2: H-M1 MUST]│          │        ◆ │          │
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 5 weeks (2 + 3)
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Duration: 5 weeks
  Formula: 2 (H-E1) + 3 (H-M1+H-M2+H-M3)

Slack Available: 0 weeks (all sequential)

Duration breakdown:
  H-E1: 2 weeks (dataloader parsing + variance analysis)
  H-M1: 1 week (content proxy analysis, 1000 docs/domain)
  H-M2: 1 week (checkpoint eval for 3 model sizes)
  H-M3: 1 week (full panel regression + robustness checks)
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
- Condition: 0 (none; boundaries documented as constraints)

Verification Phases: 2
1. Foundation (H-E1) — 2 weeks
2. Mechanisms (H-M1, H-M2, H-M3) — 3 weeks

Total Duration: 5 weeks
Critical Path Length: 5 weeks
Execution Mode: Sequential chain

Compute Estimate: 50–100 GPU-hours
- H-E1: ~5 GPU-hours (dataloader parsing, lightweight)
- H-M1: ~2 GPU-hours (NLP content analysis only)
- H-M2: ~30–40 GPU-hours (lm-eval on 154 ckpts × 3 model sizes × 2 benchmarks)
- H-M3: ~15–20 GPU-hours (full panel lm-eval + regression fitting)

Data Sources: All open-access on HuggingFace
- EleutherAI/pythia-* (checkpoints)
- EleutherAI/the_pile (corpus + metadata)
- hendrycks/mmlu, Rowan/hellaswag, allenai/ai2_arc, allenai/winogrande
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

1. **Step 1:** Execute H-E1 (Foundation) — Week 1–2; verify data ordering non-uniformity
2. **Step 2:** Evaluate Gate 1 — If FAIL → activate cross-family fallback; If PASS → proceed
3. **Step 3:** Execute H-M1 (Content Analysis) — Week 3; validate domain content differences
4. **Step 4:** Evaluate Gate 2 (H-M1) — If FAIL → explore reduced domain set; If PASS → proceed
5. **Step 5:** Execute H-M2 (Training Dynamics) — Week 4; Spearman correlations on 3 model sizes
6. **Step 6:** Execute H-M3 (Full Panel Regression) — Week 5; primary quantitative test
7. **Final:** Verification complete → Phase 4.5 Synthesis → Phase 5 Baseline Comparison

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Within the Pythia model family trained on The Pile, cumulative domain exposure trajectories reveal benchmark-specific effects: Wikipedia exposure predicts MMLU more than HellaSwag; Books exposure predicts HellaSwag/WinoGrande more than MMLU — quantifiable via panel regression with model-size fixed effects.

**Supporting Evidence:**
1. Different domains contain systematically different distributions of cognitive task patterns (CoLoR-Filter's task-conditioned efficiency gain implies domain-localized task-relevant signal)
2. Panel regression framework validated by RegMix/DoReMi at proxy-model scale; 2,464 observations provide statistical power
3. First within-family design eliminates cross-family corpus-size confound; contamination control integrated as mandatory pre-step

**Strengths:**
- First exploitation of Pythia dataloader ordering as domain exposure timeline
- 4 directional predictions with explicit falsification criteria (P1–P4)
- All data open-access; zero new training required; 50–100 GPU-hours

**Expected Outcomes:**
- Primary: β_Wikipedia > β_Books for MMLU (p < 0.05, one-tailed)
- Secondary: β_Books > β_Wikipedia for HellaSwag (p < 0.05, one-tailed)
- Tertiary: Domain profiles differ across ≥2 of 4 benchmarks (FDR q < 0.05)

### 6.2 Antithesis (H0-Based)

**Null Hypothesis (H0):** There is no significant difference in domain regression coefficients across benchmarks — β_d is identical for MMLU, HellaSwag, ARC-Challenge, and WinoGrande for all 22 domains after controlling for model scale.

**Counter-Arguments:**
1. The Pile may use uniform shuffle, collapsing within-family domain exposure variation (A1 violation) — the entire panel framework rests on an unverified assumption
2. 22-domain multicollinearity (VIF > 10 likely) makes it impossible to isolate individual domain effects; estimates will have large standard errors even if effects exist
3. Scale effects may dominate: model-size fixed effects may absorb most variance, leaving domain coefficients statistically indistinguishable from noise

**Potential Failure Points:**
- R1 (CRITICAL): Data ordering uniform shuffle — identified as the single most dangerous risk
- R2 (High): Multicollinearity inflates standard errors, deflating statistical power for P1/P2

**Conditions Under Which H0 Would Be Supported:**
- If std(cumulative_exposure_fraction) < 0.001 for ≥13 domains (H-E1 fails)
- If β_Wikipedia ≤ β_Books for MMLU (P1 falsification)
- If LRT cannot reject shared-β model (P3 fails)

### 6.3 Synthesis

**Balanced Assessment:**

The hypothesis H-DomainExposureBenchmarkSpecificity-v1 presents a well-structured testable claim grounded in the theoretical bridge from CoLoR-Filter's domain-localized task signal to Pythia's dataloader-derived exposure trajectories. However, the null hypothesis raises a valid structural concern: the entire verification rests on A1 (non-uniform data ordering), which is unverified and could collapse the within-family design.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Gate 1 (H-E1):** Immediately tests A1 before investing compute in H-M2/H-M3; activates cross-family fallback if A1 fails
2. **Sequential mechanism testing (H-M1→H-M3):** Tests causal chain step-by-step; each step provides informative evidence even on partial failure
3. **Gate conditions:** MUST_WORK (H-E1, H-M1) vs SHOULD_WORK (H-M2, H-M3) gate hierarchy allows PoC to proceed even with partial mechanism confirmation

**Conditions for Thesis Support:**
- H-E1 passes (domain trajectories measurable, A1 confirmed)
- H-M1 passes (domain content differences confirmed)
- P1 and P2 confirmed (β_Wikipedia > β_Books for MMLU; β_Books > β_Wikipedia for HellaSwag)

**Conditions for Antithesis Support:**
- H-E1 fails (uniform shuffle confirmed — cross-family fallback activates)
- H-M1 fails (domain content patterns more uniform than expected)
- β_Wikipedia ≈ β_Books for both MMLU and HellaSwag (P1 and P2 simultaneously fail)

**Nuanced Outcome Possibilities:**
1. **Full Support:** All 4 hypotheses pass → Thesis validated; directional domain-benchmark specificity confirmed
2. **Partial Support:** H-M2/H-M3 partial (some directions confirmed) → Refined thesis with narrowed domain set (e.g., Wikipedia→MMLU confirmed; Books→HellaSwag inconclusive)
3. **Mechanism Partial:** H-E1/H-M1 pass but H-M3 P1/P2 fail → Null finding: domains don't differentially predict benchmarks despite content differences (publishable reframing)
4. **No Support:** H-E1 fails → Cross-family design pivot; within-family thesis requires redesign

### 6.4 Robustness Assessment

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 ROBUSTNESS ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Aspect            | Thesis Position                    | Antithesis Challenge            | Resolution        |
|-------------------|------------------------------------|---------------------------------|-------------------|
| Existence (H-E1)  | Data ordering non-uniform (likely) | May be uniformly shuffled (A1)  | Gate 1 diagnostic |
| Mechanism (H-M1)  | Domain content differences real    | Subtle/uniform patterns         | Content proxy test|
| Dynamics (H-M2)   | Differential exposure drives ΔScore| Scale dominates signal          | Spearman ρ test   |
| Regression (H-M3) | β vectors benchmark-specific       | Multicollinearity + shared β    | PCA + LRT         |
| Performance       | Novel domain-benchmark matrix      | Marginal over scale-only model  | R² decomposition  |

Overall Robustness Score: Medium-High
- Strong: Theoretical grounding, clear falsification, established infrastructure
- Weak: A1 unverified; multicollinearity risk for 22-domain OLS

Confidence in Verification Plan: 0.75

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 7. Executive Summary & Conclusions

### Executive Summary

**Main Hypothesis:** H-DomainExposureBenchmarkSpecificity-v1
- Within Pythia (The Pile, 154 ckpts × 16 sizes): domain-specific β coefficients via panel regression
- ID: H-DomainExposureBenchmarkSpecificity-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A Dialogue loaded; 33% scope reduction applied)
- Sub-Hypotheses: 4 total (H-E1 + H-M1 + H-M2 + H-M3; no H-C; H-CP deferred to Phase 5)
- Phases: 2 phases over 5 weeks; Critical Gates: 2 (Gate 1: H-E1 MUST_WORK, Gate 2: H-M1 MUST_WORK)
- Compute: 50–100 GPU-hours; all data open-access on HuggingFace

**Risk Assessment:** Medium-High
- Primary concerns: R1 (uniform shuffle — CRITICAL; verify in H-E1 immediately), R2 (22-domain multicollinearity — PCA fallback ready)

**Immediate Action:** Begin Phase 1 with H-E1 — verify Pythia dataloader non-uniformity before committing to panel design

### Conclusions

**Key Achievements:**
- 4 sub-hypotheses designed covering complete causal chain: existence → content mechanism → training dynamics → regression quantification
- H0 (β identical across benchmarks) formally addressed via LRT in H-M3
- Cross-family fallback design specified for A1 failure
- All PROVE_NEW claims covered; BUILD_ON claims excluded (33% scope reduction)

**Verification Execution Order:**

Phase 1: Foundation (2 weeks)
- H-E1: Compute cumulative domain exposure variance from Pythia dataloaders; confirm non-uniform ordering
- Gate 1: MUST PASS — if fail, activate cross-family design pivot

Phase 2: Core Mechanisms (3 weeks)
- H-M1: Domain content proxy analysis (1,000 docs/domain, entity density, narrative coherence)
- H-M2: Spearman correlation of domain exposure trajectories with benchmark improvement rates (3 model sizes)
- H-M3: Full panel OLS regression (2,464 obs), LRT benchmark-specific vs shared-β, P1–P4 tests
- Gate 2: H-M1 MUST PASS; H-M2 and H-M3 are SHOULD_WORK

**Critical Decision Points:**

1. Gate 1 (H-E1): std(exposure_fraction) for ≥10 domains > 0.001
   - FAIL → PIVOT to cross-family design (n≥15 model families)
   - PASS → Proceed to Phase 2

2. Gate 2 (H-M1): Wikipedia entity density > Books (p < 0.05)
   - FAIL → EXPLORE reduced domain set; proceed to H-M3 with limitation
   - PASS → Proceed with full domain set

**Open Questions (from Phase 2A):**
- Is The Pile data ordering uniform shuffle or domain-blocked? Check Pythia dataloader documentation first (H-E1)
- What is the multicollinearity structure of 22-domain exposure trajectories? May need PCA-reduced features (H-M3 step 3)
- Does 13-gram contamination audit significantly change benchmark scores for any of the 4 target benchmarks? (H-M2 pre-step)

**Recommendations:**

1. Immediate Actions:
   - Start Phase 1 with H-E1 (dataloader verification); do NOT begin H-M2/H-M3 compute before A1 is confirmed
   - Set up lm-evaluation-harness v0.4 environment with 13-gram decontamination pipeline before Week 2

2. Resource Allocation:
   - Allocate 5 weeks for critical path; reserve 1-week buffer for A1 contingency pivot
   - Download Pythia checkpoints for 70M, 1B, 6.9B first (representative sizes); scale to all 16 after H-E1 confirms

3. Failure Management:
   - Document all failures in checkpoint files; execute PIVOT strategies per risk table
   - If R1 triggers (uniform shuffle), cross-family design is pre-specified — do not re-run Phase 2A

### Appendices

**A. Phase 2A Reference**
- Source: docs/youra_research/03_refinement.yaml (ID: H-DomainExposureBenchmarkSpecificity-v1)
- Gap ID: gap-1 — "No Systematic Per-Filter × Per-Benchmark Correlation Analysis on Existing Checkpoints"
- Convergence: Exchange 11/12, all 6 criteria met

**B. MCP Tool Usage Summary**
- Total MCP calls: 4 (incremental mode)
- scientificmethod: 2 calls (H-E1-verification, H-M-integrated)
- structuredargumentation: 2 calls (thesis + antithesis)
- Archon: timeout (pipeline ID not retrieved; Archon tasks created in state block below)
