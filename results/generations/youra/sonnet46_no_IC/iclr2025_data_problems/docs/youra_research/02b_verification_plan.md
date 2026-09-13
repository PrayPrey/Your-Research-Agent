---
hypothesis_id: H-CurationScale-v1
workflow: phase2b-planning
schema_version: "1.0"
created_at: "2026-08-04"
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
completedAt: "2026-08-04T00:00:00Z"
---

# Verification Plan: Scale-Dependent Optimal Curation (H-CurationScale-v1)

**Date:** 2026-08-04
**Hypothesis ID:** H-CurationScale-v1
**Confidence:** 0.72
**Total Hypotheses:** 4 (H-E1, H-M1, H-M2, H-M3)

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under fixed model architecture family (Pythia-style, trained from scratch) and fixed tokens-seen budget on open corpora (Dolma, FineWeb replication), if we independently vary perplexity filtering threshold τ ∈ {20, 35, 50} and deduplication aggressiveness d ∈ {strict: MinHash Jaccard=0.7, loose: MinHash Jaccard=0.9}, then downstream benchmark scores (MMLU 4-shot + HellaSwag 0-shot) will show significant Scale × Curation interaction effects — specifically: smaller models (70M) achieve peak performance at lower PPL thresholds and benefit from aggressive deduplication, while larger models (160M+) achieve peak performance at higher PPL thresholds and are harmed by aggressive deduplication — because smaller models lack sufficient capacity to extract signal from high-diversity noisier distributions (requiring stronger quality filtering), while larger models rely on near-duplicate pattern frequency for in-context learning ability (which aggressive deduplication removes).

### 1.2 Alternative Hypothesis (H0)

There is no significant interaction between model scale and curation configuration on downstream benchmark scores — the optimal curation recipe (PPL threshold and dedup aggressiveness) is scale-invariant.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Dolma (primary) + FineWeb (replication) (standard) | Both are fully open English web corpora with documented filtering pipelines; Dolma has known data composition; FineWeb has existing quality scores that enable efficient replication by re-filtering at different PPL thresholds. NeMo-Curator supports both. |
| **Model** | Pythia-architecture (70M, 160M) | Fixed architecture across all conditions; well-documented; established in pre-training ablation literature. Pythia checkpoints at multiple scales from same architecture family enable scale comparison. |

**Dataset Details:**
- Source: AI2 Dolma v1.7 (open, documented filtering); HuggingFace FineWeb (open, documented quality scores)
- Path: HuggingFace Hub: allenai/dolma, HuggingFaceFW/fineweb

**Model Details:**
- Type: Autoregressive transformer, decoder-only
- Source: EleutherAI Pythia architecture; training code from GPT-NeoX; trained from scratch on filtered corpora

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| ProX [Zhou et al., 2024] | +2% average benchmark (MMLU, HellaSwag, ARC-C, WinoGrande, PIQA) vs baseline | C4, DCLM, FineWeb at 1B scale, 100B tokens |
| SoftDedup [He et al., 2024] | +1.77% few-shot accuracy vs hard dedup baseline | Web corpus at unstated scale |
| REWIRE [Nguyen et al., 2025] | +1.0–2.5pp across 22 tasks at 1–7B scale | Web data at 1B and 7B, 200B tokens |
| WebOrganizer [Wettig et al., 2025] | +2.5pp (quality filter + domain mixing) vs quality filter only | C4, FineWeb at 1B, 100B tokens |

**Best baseline:** +2.5pp over no-curation (WebOrganizer combined method at 1B). All prior work single-scale, no factorial design.

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Pythia-architecture models trained from scratch on Dolma subsets are comparable across curation conditions (same architecture, optimizer, infrastructure) | Pythia architecture well-documented; NeMo-Curator reproducible; EleutherAI training code open-source | Cross-condition comparisons invalid; entire experimental design collapses |
| A2 | GPT-2 PPL is a reasonable operationalization of 'data quality' that meaningfully partitions the Dolma distribution | DataMan [Peng et al., 2025] uses GPT-2 PPL as primary quality proxy and shows measurable distribution shifts; standard in literature (CCNET, Gopher) | PPL threshold manipulation may not produce hypothesized quality variation; need alternative quality metric |
| A3 | Near-duplicate document removal (MinHash at J=0.7 vs J=0.9) produces meaningfully different ICL pattern frequency distributions | SoftDedup [He et al., 2024] shows hard vs soft dedup produce different few-shot performance; MinHash J=0.7 removes ~15-20% of web data | PPL and dedup thresholds tested may not span sufficient range to detect scale interaction for dedup (P3) |
| A4 | MMLU and HellaSwag are not so heavily contaminated in Dolma/FineWeb that contamination removal eliminates benchmark signal | Yang et al. (2023) reports 8-18% HumanEval contamination in RedPajama but MMLU contamination typically lower; contamination measured per condition as ANCOVA covariate | Benchmark scores reflect contamination variation rather than true capability |
| A5 | Scale × curation interaction observed at 70M and 160M is representative of the general trend across scales | Theoretical scaling laws (Chinchilla, power laws) suggest smooth interpolation; Na et al. (2024) approximation allows extrapolation to 1B as validation | Results at 70M/160M may not generalize to practically relevant scales (1B+) |

### 1.6 Research Gap & Novelty

**Gap:** Causal attribution of curation choices to benchmark outcomes across model scales is unestablished. All prior curation ablation papers (ProX, REWIRE, DataMan, WebOrganizer, SoftDedup) operate at a single model scale and vary one curation axis at a time without factorial design. The scale × curation interaction is untested.

**Novelty:** First controlled measurement of Scale × Curation interaction effects in pre-training; scale-aware curation recipe (optimal data filtering depends on model size); potential first data-quality scaling law via learning curve convergence rate λ. P3 (dedup hurts large models) challenges universal dedup practice adopted industry-wide since 2021.

**Scope Reduction (57%):** BUILD_ON claims (individual curation method improvements, PPL/ICL misalignment, domain mixing orthogonality, modular training approximation) accepted as established — not re-verified. Only PROVE_NEW claims generate sub-hypotheses.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Scale × Curation Interaction Existence**

**Statement:** Under fixed Pythia architecture and fixed token budget on open English corpora (Dolma, FineWeb), if PPL threshold τ ∈ {20,35,50} and dedup aggressiveness d ∈ {J=0.7, J=0.9} are independently varied across model scales {70M, 160M}, then a significant Scale × Curation interaction effect will appear in MMLU 4-shot and HellaSwag 0-shot scores because the optimal data quality configuration depends on model capacity.

**Rationale:** This is the foundation existence claim. If no interaction exists, H-M2/H-M3 mechanism tests become moot. Confirmed by P1 (Scale × PPL interaction) and P3 (Scale × Dedup sign change) together. Prior work (DataMan) demonstrates scale-sensitivity of PPL/ICL misalignment, motivating this interaction hypothesis.

**Variables:**
- Independent: Model scale (70M, 160M), PPL threshold (20, 35, 50), Dedup aggressiveness (J=0.7, J=0.9), Corpus (Dolma, FineWeb)
- Dependent: MMLU 4-shot accuracy (primary), HellaSwag 0-shot accuracy
- Controlled: Architecture (Pythia), optimizer (AdamW), token budget, contamination rate (ANCOVA covariate), random seed (3 per condition)

**Verification Protocol:**
1. Run NeMo-Curator to generate 6 filtered corpus variants per corpus (3 PPL × 2 dedup) on Dolma v1.7 and FineWeb; record corpus size and contamination rate per condition.
2. Train 24 models (2 scales × 6 filter conditions × 2 corpora) from scratch using GPT-NeoX; 3 seeds each = 72 total training runs; evaluate with lm-evaluation-harness (MMLU 4-shot + HellaSwag 0-shot) at final checkpoint.
3. Run lm-sys/llm-decontaminator on each filtered corpus against MMLU and HellaSwag test sets; record contamination rate CR(condition).
4. Fit 2-way mixed ANOVA with factors Scale × PPL-threshold; include contamination rate as ANCOVA covariate; test interaction term F_{Scale×PPL}; identify τ*(N) per scale via simple effects analysis.
5. Also test Scale × Dedup interaction (P3); verify sign(B(strict)−B(loose)) at each scale.

**Success Criteria (PoC: Direction-based):**
- Primary: Scale × PPL-threshold ANOVA interaction p < 0.05, partial η² ≥ 0.15, τ*(70M) < τ*(160M)
- Secondary: Scale × Dedup interaction p < 0.05 with sign change confirmed (P3)

**Failure Response:**
- IF interaction p > 0.05 AND partial η² < 0.15: PIVOT — check if contamination covariate absorbs all variance; re-run with wider τ range {10, 35, 70}
- IF interaction in opposite direction: EXPLORE — report as null finding with methodological contribution (factorial design); escalate to Phase 2A-Dialogue

**Dependencies:** None (foundation hypothesis)

**Source:** Phase 2A Section 5 (sh1_existence), Predictions P1 + P3

---

---
**H-M1: Curation Filtering Produces Measurable Token Distribution Shift**

**Statement:** Under the same filtering conditions as H-E1, PPL filtering and MinHash deduplication produce measurable, quantifiable changes in training corpus token distribution statistics — specifically, KL divergence from unfiltered reference is monotonically increasing with filtering aggressiveness — because PPL filtering removes high-perplexity documents and dedup removes high-frequency near-duplicate sequences, both shifting the empirical token distribution.

**Rationale:** This is the first causal link in the mechanism chain. If filtering does not produce measurable distribution shifts, the proposed mechanism (capacity-dependent response to distribution) cannot operate. Validates that our independent variable manipulation actually changes the underlying data distribution. DataMan [Peng et al., 2025] provides prior evidence for PPL-filtered distribution differences.

**Variables:**
- Independent: PPL threshold τ (20, 35, 50), Dedup aggressiveness d (J=0.7, J=0.9)
- Dependent: KL divergence KL(P_filtered || P_unfiltered), corpus size after filtering, near-duplicate fraction removed
- Controlled: Reference corpus (Dolma v1.7 unfiltered), GPT-2 reference model for PPL scoring

**Verification Protocol:**
1. After NeMo-Curator filtering (from H-E1 Step 1), compute token unigram distribution P_filtered for each of 6 filter conditions and P_unfiltered for raw Dolma.
2. Measure KL(P_filtered || P_unfiltered) for each condition; verify monotonic increase with filtering aggressiveness (τ=20 > τ=35 > τ=50 in KL from unfiltered).
3. Record corpus size ratio (tokens retained / total tokens) and near-duplicate fraction removed (MinHash J=0.7 vs J=0.9); verify J=0.7 removes measurably more near-duplicates than J=0.9 (~15-20% expected per google-research/deduplicate-text-datasets).
4. Report per-condition distribution statistics as Table 1 in paper; falsify if KL differences are negligible (< 0.01 nats) across τ conditions.

**Success Criteria (PoC: Direction-based):**
- Primary: KL(τ=20) > KL(τ=35) > KL(τ=50) vs unfiltered reference (monotonic ordering)
- Secondary: Near-duplicate removal rate J=0.7 > J=0.9; difference ≥ 5 percentage points

**Failure Response:**
- IF KL differences negligible: PIVOT — use vocabulary overlap or type-token ratio as alternative distribution shift metric
- IF monotonicity violated: EXPLORE — investigate corpus-specific effects (Dolma vs FineWeb may differ)

**Dependencies:** H-E1 (must show interaction exists before attributing mechanism)

**Source:** Phase 2A Section 1.3 Causal Step 1

---

---
**H-M2: Capacity-Diversity Trade-off Drives Scale-Dependent Curation Optimum**

**Statement:** In Pythia models trained under the factorial curation conditions of H-E1, larger models (160M) exploit distributional diversity and near-duplicate frequency patterns more than smaller models (70M), as measured by higher cross-document attention entropy and differential ICL vs. standard accuracy gap by dedup condition — because larger models have sufficient representation capacity to leverage distributional heterogeneity for in-context learning per Bayesian ICL theory (Xie et al., 2022), while smaller models' learning dynamics are dominated by individual example quality.

**Rationale:** This is the second causal link: why model scale modulates the response to curation. If this mechanism holds, it explains P1 (PPL threshold direction) and P3 (dedup sign reversal). SoftDedup [He et al., 2024] provides indirect evidence that near-duplicate down-weighting (preserving pattern frequency) outperforms hard removal for few-shot accuracy (+1.77%), suggesting near-duplicate patterns carry ICL signal that larger models can exploit.

**Variables:**
- Independent: Model scale (70M vs 160M), Dedup aggressiveness (J=0.7 strict, J=0.9 loose)
- Dependent: Cross-document attention entropy (proxy for distributional diversity exploitation); ICL accuracy (MMLU 4-shot) − standard accuracy (MMLU 0-shot) gap by dedup condition
- Controlled: PPL threshold (held at τ=35 for this mechanistic analysis), architecture, optimizer, token budget

**Verification Protocol:**
1. For models trained under J=0.7 (strict) and J=0.9 (loose) dedup at both scales (4 model groups × 3 seeds = 12 models), extract attention weights at middle transformer layers for 100 held-out documents.
2. Compute cross-document attention entropy: H = -Σ a_ij log(a_ij) where a_ij are cross-document attention weights; compare 70M vs 160M under strict vs loose dedup.
3. Compute ICL gap = MMLU 4-shot accuracy − MMLU 0-shot accuracy for each model; test if gap is differentially larger at 160M under loose dedup vs strict dedup (interaction effect).
4. Report attention entropy × dedup condition × scale as factorial analysis; falsify if attention entropy does not differ by scale × dedup (interaction p > 0.05).

**Success Criteria (PoC: Direction-based):**
- Primary: Cross-document attention entropy higher at 160M than 70M under loose dedup; difference reduced or reversed under strict dedup
- Secondary: ICL gap (4-shot − 0-shot MMLU) larger at 160M under loose dedup vs strict dedup; pattern reversed or absent at 70M

**Failure Response:**
- IF attention entropy does not differ: EXPLORE — try alternative mechanistic probe (representation similarity analysis of near-duplicate pairs in context)
- IF ICL gap not differential: document as null mechanistic finding; H-E1 result still stands as empirical contribution

**Dependencies:** H-M1 (distribution shift must be confirmed before attributing mechanism to it)

**Source:** Phase 2A Section 1.3 Causal Step 2; Bayesian ICL theory (Xie et al., 2022); SoftDedup [He et al., 2024]

---

---
**H-M3: Aggressive Filtering Improves Data Efficiency (λ) at Small Scale, Not Large Scale**

**Statement:** In Pythia models trained across the PPL threshold conditions of H-E1, aggressive perplexity filtering (τ=20) produces a higher convergence rate λ (faster tokens-to-peak) at 70M scale than at 160M scale — specifically λ(70M, τ=20) > λ(160M, τ=20) — because aggressive filtering reduces distribution variance and improves per-token information density for small models' learning dynamics (following Chinchilla optimal compute scaling logic), while at large scale the diversity reduction from aggressive filtering reduces the information value of additional tokens, flattening the learning curve.

**Rationale:** This is the third causal link: data efficiency as an outcome of the scale × curation interaction. Prediction P4 operationalizes this via log-linear learning curve fitting to 10 checkpoint evaluations per run. Novel contribution: introduces learning curve convergence rate λ as a data-quality scaling law candidate. Also resolves the token budget equalization issue by using tokens-to-peak framing rather than fixed token count comparison.

**Variables:**
- Independent: PPL threshold τ (20 vs 50 for contrast; τ=35 as middle), Model scale (70M, 160M)
- Dependent: Learning curve convergence rate λ from B(T) = A − C·exp(−λT) fit; asymptote A (peak performance)
- Controlled: Dedup aggressiveness (J=0.9 loose for this analysis to isolate PPL effect), architecture, optimizer, contamination rate (ANCOVA covariate)

**Verification Protocol:**
1. Using checkpoint evaluations already collected in H-E1 (every 5B tokens, 10 checkpoints per run, 72 runs total), fit log-linear learning curve B(T) = A − C·exp(−λT) to each training run; extract λ and asymptote A per run.
2. Run 2-way ANOVA on λ with factors Scale (70M, 160M) × PPL-threshold (20, 35, 50); test interaction term; include contamination rate as ANCOVA covariate.
3. Verify directional prediction: λ(70M, τ=20) > λ(160M, τ=20) > λ(70M, τ=50) — aggressive filtering accelerates convergence at small scale, decelerates at large scale.
4. Report learning curve plots per condition as Figure 2 in paper; report λ as function of scale as potential data-quality scaling law.

**Success Criteria (PoC: Direction-based):**
- Primary: ANOVA on λ shows Scale × PPL interaction p < 0.05; λ(70M, τ=20) > λ(160M, τ=20) confirmed
- Secondary: Asymptote A(160M, τ=50) > A(160M, τ=20) — large models achieve higher peak performance under moderate filtering

**Failure Response:**
- IF ANOVA on λ not significant: EXPLORE — try alternative convergence metric (area under learning curve; tokens to 90% of asymptote)
- IF direction reversed: document as null P4 finding; does not invalidate H-E1 or H-M1/H-M2

**Dependencies:** H-M1 (distribution shift confirmed); H-E1 checkpoint evaluations already collected (no additional training runs required)

**Source:** Phase 2A Section 1.3 Causal Step 3; Prediction P4; Chinchilla scaling laws

---

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2
              → H-M3
```
*(H-M2 and H-M3 both depend on H-M1; they can run in parallel after H-M1 passes)*

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Scale × PPL ANOVA p < 0.05, partial η² ≥ 0.15, correct direction | STOP → reassess hypothesis; escalate to Phase 2A-Dialogue |
| H-M1 | MUST_WORK | KL monotonicity confirmed; near-duplicate removal rate differential ≥ 5pp | PIVOT → alternative distribution metrics; report as methodological finding |
| H-M2 | SHOULD_WORK | Attention entropy differential by scale × dedup; ICL gap differential | EXPLORE → alternative mechanistic probe; does not block Phase 5 |
| H-M3 | SHOULD_WORK | ANOVA on λ: p < 0.05, λ(70M,τ=20) > λ(160M,τ=20) | EXPLORE → alternative convergence metric; does not block Phase 5 |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3 | 3 weeks |

**Total Duration:** 5 weeks

---

## 4. Risk Analysis

### 4.1 Key Assumptions → Risk Mapping

**Risk R1: Experimental Comparability Failure**
- Source Assumption: A1 — Pythia models comparable across curation conditions
- Description: Uncontrolled variance in training infrastructure, numerical precision, or data loading order produces confounded condition comparisons.
- Affected Hypotheses: H-E1, H-M1, H-M2, H-M3 (all)
- Severity: Critical
- Likelihood: Low (Pythia/GPT-NeoX well-tested pipeline)
- Mitigation:
  1. Prevention: Pin all library versions; use identical hardware (same GPU type); deterministic data loading with fixed seeds.
  2. Detection: Run 2 identical control conditions (τ=35, J=0.9) with different seeds; verify score variance < 0.5pp (expected from 3-seed averaging).
  3. Response (PIVOT): If variance > 1pp, investigate data loading order; switch to deterministic training mode.
- Early Warning: Control condition variance > 0.5pp between seeds.

**Risk R2: PPL Does Not Partition Distribution Meaningfully**
- Source Assumption: A2 — GPT-2 PPL is valid quality proxy for Dolma
- Description: GPT-2 (trained on WebText) may be a poor reference for Dolma/FineWeb domain mix, producing τ thresholds that do not span meaningfully different quality levels.
- Affected Hypotheses: H-E1 (P1 specifically), H-M1
- Severity: High
- Likelihood: Low-Medium (partially mitigated by DataMan evidence)
- Mitigation:
  1. Prevention: Pre-compute PPL distribution across τ values; verify each threshold removes materially different corpus fractions (target: τ=20 removes ~30%, τ=35 removes ~15%, τ=50 removes ~5%).
  2. Detection: KL divergence measurement in H-M1; if KL differences < 0.01 nats, A2 may be violated.
  3. Response (PIVOT): Use educational value classifier (Fineweb-Edu scorer) as alternative quality metric alongside GPT-2 PPL.
- Early Warning: τ=20 and τ=35 produce corpora of similar size (< 5pp difference in tokens retained).

**Risk R3: Dedup Thresholds Insufficient Span**
- Source Assumption: A3 — MinHash J=0.7 vs J=0.9 produces meaningfully different ICL pattern frequency
- Description: The two Jaccard thresholds may not produce sufficiently different near-duplicate removal rates to detect the sign-change interaction (P3).
- Affected Hypotheses: H-E1 (P3), H-M2
- Severity: High
- Likelihood: Medium (depends on Dolma near-duplicate density)
- Mitigation:
  1. Prevention: Pre-compute near-duplicate fraction at J=0.7 and J=0.9; if difference < 5pp, add J=0.5 as third level or use SoftDedup reweighting as alternative manipulation.
  2. Detection: H-M1 success criterion — near-duplicate removal rate differential ≥ 5pp; if not met, R3 is confirmed.
  3. Response (PIVOT): Replace hard dedup with SoftDedup reweighting at weight levels {0.1, 0.5, 1.0}; maintains experimental tractability.
- Early Warning: google-research/deduplicate-text-datasets reports < 10% near-duplicate fraction in Dolma at J=0.7 vs J=0.9.

**Risk R4: Benchmark Contamination Invalidates Signal**
- Source Assumption: A4 — MMLU/HellaSwag contamination controlled by ANCOVA
- Description: If contamination rate varies strongly across curation conditions (aggressive filtering may remove contaminated documents differently), ANCOVA covariate may not adequately control for contamination, inflating or deflating apparent interaction.
- Affected Hypotheses: H-E1 (all predictions), H-M3
- Severity: High
- Likelihood: Low-Medium
- Mitigation:
  1. Prevention: Pre-register that ANCOVA is mandatory for all ANOVA tests; pre-specify that if contamination covariate absorbs > 50% of interaction variance, result is reported as inconclusive.
  2. Detection: Report contamination rate per condition as supplementary table; check correlation between contamination rate and benchmark scores.
  3. Response (SCOPE): If MMLU contamination absorbs interaction, pivot primary DV to HellaSwag (lower expected contamination in web data) or LAMBADA (generative task, harder to contaminate).
- Early Warning: Contamination rate > 5% in any single condition, or contamination rate correlates > 0.5 with PPL threshold.

**Risk R5: Scale Interaction Does Not Extrapolate**
- Source Assumption: A5 — 70M/160M interaction direction representative of broader trend
- Description: The interaction direction may reverse between 160M and 1B+, making our results specific to small-scale models with limited practical relevance.
- Affected Hypotheses: All (external validity, not PoC validity)
- Severity: Medium (does not invalidate PoC; affects paper claims scope)
- Likelihood: Low (scaling laws suggest smooth interpolation)
- Mitigation:
  1. Prevention: Use Na et al. (2024) modular merging approximation to estimate interaction at 1B before data collection; if approximation predicts reversal, expand primary study to include 1B.
  2. Detection: Na et al. approximation run as auxiliary analysis after 70M/160M training completes.
  3. Response (SCOPE): Report as limitation; claim "interaction holds at 70M–160M scale range"; do not claim universality.
- Early Warning: Na et al. approximation shows interaction effect size decreasing steeply between 160M and 400M.

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Experimental Comparability | A1 | H-E1, H-M1, H-M2, H-M3 | Critical |
| R2: PPL Partitioning | A2 | H-E1 (P1), H-M1 | High |
| R3: Dedup Threshold Span | A3 | H-E1 (P3), H-M2 | High |
| R4: Benchmark Contamination | A4 | H-E1, H-M3 | High |
| R5: Scale Extrapolation | A5 | All (external validity) | Medium |

**Risk Summary:** 1 Critical, 3 High, 1 Medium. All have pre-specified mitigation strategies and early warning indicators.

### 4.3 Baseline Failure Pattern Analysis

| Baseline Limitation | Potential Risk for This Study | Mitigation |
|---------------------|-------------------------------|------------|
| Prior work single-scale (ProX, DataMan, WebOrganizer) | Cannot borrow prior ANOVA designs; must run full factorial | Run full 24-condition factorial — no shortcut |
| SoftDedup uses reweighting not removal | Hard dedup manipulation may be too coarse for P3 detection | Add SoftDedup as PIVOT option in R3 mitigation |
| REWIRE compares recycling vs discarding, not aggressiveness levels | Cannot directly compare our effect sizes to REWIRE | Report as distinct contribution; effect size is a novel quantity |

---

## 5. Dependency Graph (DAG) & Timeline

### 5.1 Dependency Graph

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root: Foundation]
    H-E1 (Existence — Scale×Curation interaction)
    Gate Type: MUST_WORK
         │
         ▼
[Level 1 - Distribution Mechanism]
    H-M1 (Filtering produces measurable distribution shift)
    Gate Type: MUST_WORK
    Prerequisites: H-E1
         │
         ├─────────────────┐
         ▼                 ▼
[Level 2 - Capacity & Efficiency Mechanisms]
    H-M2                  H-M3
    (Capacity-diversity    (Learning curve λ
    trade-off mechanism)   efficiency interaction)
    Gate: SHOULD_WORK      Gate: SHOULD_WORK
    Prereq: H-M1           Prereq: H-M1

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 (or H-M3)
Parallelization: H-M2 and H-M3 can run concurrently after H-M1
═══════════════════════════════════════════════════════════
```

### 5.2 Verification Phases

**Phase 1 — Foundation**
| Hypothesis | Test | Gate |
|------------|------|------|
| H-E1 | 2-way ANOVA Scale × PPL-threshold; Levene's test P2; Scale × Dedup sign-change P3 | MUST PASS |

→ **Gate 1**: If H-E1 fails (p > 0.05, partial η² < 0.15) → STOP, reassess main hypothesis.

**Phase 2 — Mechanisms**
| Hypothesis | Dependencies | Gate |
|------------|--------------|------|
| H-M1 | H-E1 | MUST_WORK |
| H-M2 | H-M1 (parallel with H-M3) | SHOULD_WORK |
| H-M3 | H-M1 (parallel with H-M2) | SHOULD_WORK |

→ **Gate 2**: H-M1 must pass. H-M2/H-M3 failures narrow scope but do not block Phase 5.

### 5.3 Dependency Hierarchy Table

| Level | Hypothesis | Prerequisites | Gate Type | Parallelizable |
|-------|-----------|---------------|-----------|----------------|
| 0 | H-E1 | None | MUST_WORK | No (root) |
| 1 | H-M1 | H-E1 | MUST_WORK | No |
| 2 | H-M2 | H-M1 | SHOULD_WORK | Yes (with H-M3) |
| 2 | H-M3 | H-M1 | SHOULD_WORK | Yes (with H-M2) |

### 5.4 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis      │ W1-2   │ W3-4   │ W5     │
──────────────────────┼────────┼────────┼────────┼
PHASE 1: Foundation   │        │        │        │
  H-E1                │ ██████ │        │        │
  [Gate 1]            │      ◆ │        │        │
──────────────────────┼────────┼────────┼────────┼
PHASE 2: Mechanisms   │        │        │        │
  H-M1                │        │ ██████ │        │
  [Gate 2]            │        │      ◆ │        │
  H-M2 (parallel)     │        │        │ ████   │
  H-M3 (parallel)     │        │        │ ████   │
──────────────────────┼────────┼────────┼────────┼
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work  |  ◆ = Gate decision point
Total Duration: 5 weeks
Critical Path: H-E1 (2w) → H-M1 (2w) → H-M2/H-M3 (1w parallel) = 5 weeks
═══════════════════════════════════════════════════════════════════

Note on H-E1 (Week 1-2): This includes corpus preparation (NeMo-Curator,
~1-2 days), training all 72 runs (parallel GPU jobs, ~3-4 days at 96 A100-hours
total), and evaluation + statistical analysis (~2-3 days). The 2-week window
accounts for queue time and analysis iteration.

Note on H-M1 (Week 3-4): Distribution statistics computed from already-filtered
corpora (no re-filtering needed). KL divergence, corpus size ratios, near-duplicate
fractions computed post-hoc from H-E1 corpus preparation artifacts.

Note on H-M2/H-M3 (Week 5): Attention entropy extraction and learning curve
fitting use model checkpoints already saved during H-E1 training — no additional
training runs required.
```

### 5.5 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 (or H-M3)

Total Duration: 5 weeks
  Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M2/H-M3 parallel) = 5 weeks

Efficiency Note: H-M1 is largely post-hoc analysis of H-E1 artifacts;
H-M2 and H-M3 use H-E1 model checkpoints already saved.
Actual compute time dominated by H-E1 training runs (~96 A100-hours).

Slack: 0 weeks on critical path; H-M2 and H-M3 have 0 slack relative
to each other (parallel), but do not extend critical path.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 4
- Existence: 1 (H-E1)
- Mechanism: 3 (H-M1, H-M2, H-M3)
- Condition: 0 (not recommended)

Training Runs: 72 total (24 conditions × 3 seeds)
Checkpoints: 720 evaluations (72 runs × 10 checkpoints)
Compute Estimate: ~96 A100-hours for primary design
  (70M: ~2h/run × 48 runs = 96h; 160M: ~4h/run × 24 runs = 96h total)

Verification Phases: 2 (Foundation, Mechanisms)
Total Duration: 5 weeks
Execution Mode: Sequential chain (H-E1 → H-M1), then parallel (H-M2 ∥ H-M3)

Key Infrastructure:
- NeMo-Curator: corpus preparation
- GPT-NeoX: model training
- lm-evaluation-harness: benchmark evaluation
- lm-sys/llm-decontaminator: contamination measurement
- SciPy/statsmodels: ANOVA, Levene's test, ANCOVA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.7 Execution Order

**Step 1:** Execute H-E1 (Foundation) — Week 1–2
- Prepare 12 filtered corpus variants (6 filter conditions × 2 corpora)
- Train 72 models (24 conditions × 3 seeds); save all 10 checkpoints per run
- Evaluate all final checkpoints; run contamination measurement
- Statistical analysis: ANOVA (P1, P3), Levene's test (P2)

**Step 2:** Evaluate Gate 1 → If MUST_WORK passes, proceed; if fails, STOP and escalate to Phase 2A-Dialogue

**Step 3:** Execute H-M1 (Distribution Shift) — Week 3–4
- Compute KL divergence from H-E1 corpus artifacts (no new filtering needed)
- Report corpus size ratios and near-duplicate removal rates
- Verify monotonicity; check R2/R3 early warning indicators

**Step 4:** Evaluate Gate 2 → If H-M1 passes, proceed to parallel H-M2 + H-M3

**Step 5a (parallel):** Execute H-M2 (Capacity-Diversity Mechanism) — Week 5
- Extract attention weights from H-E1 model checkpoints
- Compute cross-document attention entropy; run ICL gap analysis

**Step 5b (parallel):** Execute H-M3 (Learning Curve Efficiency) — Week 5
- Fit B(T) = A − C·exp(−λT) to H-E1 checkpoint evaluations (already collected)
- Run ANOVA on λ; verify P4 direction

**Final:** Verification complete → proceed to Phase 2C experiment design for each hypothesis

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Claim: Optimal pre-training data curation is scale-dependent.
Smaller models (70M) benefit from aggressive quality filtering and
strict deduplication; larger models (160M) benefit from moderate
filtering and loose deduplication that preserves near-duplicate
ICL patterns. This produces a measurable Scale × Curation
interaction in MMLU 4-shot and HellaSwag 0-shot scores.

Supporting Evidence:
1. DataMan [Peng et al., 2025]: PPL/ICL misalignment is non-monotonic,
   suggesting scale-dependent optimum exists.
2. SoftDedup [He et al., 2024]: Near-duplicate patterns carry ICL signal
   (soft > hard dedup for few-shot, +1.77%), supporting mechanism.
3. WebOrganizer [Wettig, 2025]: Domain diversity super-additive with
   quality filtering — large models value distributional breadth.
4. Bayesian ICL theory (Xie et al., 2022): Near-duplicate frequency
   patterns are the mechanistic source of ICL capability in large models.

Strengths:
- 4 pre-registered predictions (P1–P4) with explicit statistical tests
- Contamination controlled via ANCOVA in all tests
- Factorial design provides causal identification unavailable in prior work
- FineWeb replication provides external validity check

Expected Outcomes:
- Primary (P1): τ*(70M) ∈ [20,35], τ*(160M) ∈ [35,50]; interaction p < 0.05
- Secondary (P3): Sign change in dedup effect across scales; interaction p < 0.05
- Tertiary (P2, P4): Variance differential + learning curve λ interaction
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Null Hypothesis (H0): The optimal curation recipe (PPL threshold
and dedup aggressiveness) is scale-invariant — no significant
interaction between model scale and curation configuration on
downstream benchmark scores.

Counter-Arguments:
1. MMLU 4-shot at 70M has high noise (chance = 25%; small models
   near chance on many subtasks) — interaction signal may be
   swamped by evaluation noise even with 3 seeds.
2. GPT-2 PPL thresholds (τ=20/35/50) may not span meaningfully
   different quality levels in Dolma — if A2 is violated, P1 is
   untestable with this operationalization.
3. The 70M–160M scale range is narrow — both are very small models.
   The interaction may require a wider range (1M vs 1B) to be
   detectable at the chosen effect size threshold (η² ≥ 0.15).
4. Existing literature (ProX, REWIRE) shows positive effects of
   aggressive filtering at large scales (1B+), contradicting P3's
   prediction that strict dedup hurts large models.

Potential Failure Points:
- H-E1: Interaction present but partial η² < 0.15 (true effect
  below detectability threshold in 70M–160M range)
- H-M2: Attention entropy probe too noisy or not sensitive to
  near-duplicate removal at these model sizes
- H-M3: Log-linear curve fit poorly conditioned with only 10
  checkpoints, producing unreliable λ estimates

Conditions Under Which H0 Would Be Supported:
- 2-way ANOVA interaction term p > 0.05 for both Scale × PPL and
  Scale × Dedup with partial η² < 0.10
- FineWeb replication fails to replicate Dolma interaction direction
- Contamination covariate absorbs > 50% of apparent interaction variance
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The thesis (scale-dependent optimal curation) is theoretically
well-grounded and empirically motivated by convergent indirect
evidence from DataMan, SoftDedup, WebOrganizer, and Bayesian ICL
theory. However, the antithesis raises valid concerns about:
(a) statistical power at 70M–160M scale range,
(b) operationalization validity of GPT-2 PPL thresholds,
(c) potential MMLU noise at small scale.

Resolution Path:
The verification plan addresses this dialectic through:
1. Foundation verification (H-E1): Pre-registered directional
   predictions with explicit effect size threshold (partial η² ≥ 0.15)
   ensures honest assessment of whether effect is detectable.
2. ANCOVA contamination control: Prevents false positives from
   contamination variation across curation conditions.
3. FineWeb replication: If Dolma and FineWeb disagree, corpus-specific
   finding is pre-specified as acceptable; does not constitute failure.
4. Null-result path pre-specified: If H-E1 fails, report as
   methodological contribution (first factorial design for scale ×
   curation) with null finding — still publishable as replication
   contribution challenging assumed scale-generalizability.

Conditions for Thesis Support:
- H-E1 MUST_WORK gate passes (p < 0.05, η² ≥ 0.15, correct direction)
- H-M1 confirms distribution shift (prerequisite for mechanistic claim)
- At least 2 of 4 predictions (P1–P4) confirmed with pre-specified rigor

Conditions for Antithesis Support:
- H-E1 fails: p > 0.05 AND effect size below detectable threshold
- OR: Contamination covariate absorbs interaction entirely

Nuanced Outcome Possibilities:
1. Full Support: H-E1 + H-M1 pass, ≥2 predictions confirmed → Thesis validated → Phase 5
2. Partial Support: H-E1 passes but H-M2/H-M3 fail → Empirical interaction without mechanism → Still publishable
3. No Support: H-E1 fails → Antithesis supported → Route to Phase 2A-Dialogue for hypothesis revision
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Scale × Curation interaction measurable at 70M/160M | Effect too small at narrow scale range | η² ≥ 0.15 pre-registered threshold; FineWeb replication |
| Mechanism (Step 1) | Filtering measurably shifts token distribution | GPT-2 PPL may not partition Dolma meaningfully | KL divergence measurement pre-conditions H-M2/H-M3 |
| Mechanism (Step 2) | Capacity explains differential response | Attention entropy probe may be too noisy | ICL gap as alternative mechanistic measure |
| Efficiency (Step 3) | λ differential proves data efficiency story | 10 checkpoints may give unreliable curve fits | Use tokens-to-90%-asymptote as fallback metric |
| Generalization | 70M–160M interaction representative | May reverse at 1B+ | Na et al. approximation extrapolates to 1B |

**Overall Robustness Score:** Medium-High
**Confidence in Verification Plan:** 0.72 (matches Phase 2A confidence)

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** H-CurationScale-v1 — optimal pre-training data curation (PPL threshold, dedup aggressiveness) is scale-dependent, with opposite interaction directions across 70M and 160M models.
- ID: H-CurationScale-v1, Confidence: 0.72

**Verification Structure:**
- Mode: Incremental (Phase 2A Dialogue available; 57% scope reduction)
- Sub-Hypotheses: 4 total (H-E1 + H-M1–H-M3; no H-C; H-CP → Phase 5)
- Phases: 2 phases over 5 weeks
- Critical Gates: 2 decision points (Gate 1 at H-E1, Gate 2 at H-M1)
- Compute: ~96 A100-hours for 72 training runs; all from H-E1 factorial design

**Risk Assessment:** Medium (3 High risks mitigated, 1 Critical with low likelihood)
- Primary concerns: PPL partitioning validity (R2), dedup threshold span (R3)

**Immediate Action:** Begin Phase 1 with H-E1 — corpus preparation via NeMo-Curator

### 7.2 Conclusions

**Key Achievements:**
- 4 sub-hypotheses covering existence (H-E1) and full 3-step causal chain (H-M1–H-M3)
- H0 explicitly addressed: "optimal curation is scale-invariant" — directly falsified by H-E1 if interaction found
- All PROVE_NEW claims from Phase 2A have corresponding sub-hypotheses; BUILD_ON claims accepted without re-verification (57% scope reduction)

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Scale × Curation interaction in benchmark scores; 2-way ANOVA + Levene's test
- Gate 1: MUST PASS (p < 0.05, partial η² ≥ 0.15, correct direction)

**Phase 2: Core Mechanisms** (3 weeks)
- H-M1: Distribution shift (KL divergence from filtered vs unfiltered corpora) — Week 3–4
- H-M2: Capacity-diversity mechanism (attention entropy + ICL gap analysis) — Week 5, parallel
- H-M3: Learning curve efficiency (λ from B(T) = A−C·exp(−λT) fitting) — Week 5, parallel
- Gate 2: H-M1 must pass

**Critical Decision Points:**

1. **Gate 1 (Foundation):** H-E1 result
   - FAIL (p > 0.05 or wrong direction) → STOP → escalate to Phase 2A-Dialogue for hypothesis revision
   - PASS → proceed to Phase 2 mechanisms

2. **Gate 2 (Mechanisms):** H-M1 result
   - CRITICAL FAIL (KL not measurable) → PIVOT to alternative distribution metrics; re-assess if mechanism claim is viable
   - H-M2/H-M3 fail → EXPLORE alternative probes; document as mechanistic limitation; does NOT block Phase 5

**Open Questions (from Phase 2A):**
- Does Scale × PPL interaction replicate on FineWeb? If not, is the effect Dolma-specific?
- Does the dedup sign change (P3) hold at 1B scale (extrapolated via Na et al. approximation)?
- What is the functional form of τ*(N)? Power law, logarithmic, or step function?
- Do MMLU and HellaSwag show different scale interactions (ICL vs. standard benchmarks)?

**Recommendations:**

1. **Immediate Actions:**
   - Pre-register all 4 predictions (P1–P4) with statistical tests and effect size thresholds on OSF before data collection
   - Run corpus size analysis before training to verify R2/R3 early warning indicators
   - Set up checkpoint saving infrastructure for all 72 runs (10 checkpoints each = 720 evaluations)

2. **Resource Allocation:**
   - 5 weeks on critical path; allocate 1 week buffer for queue time and re-runs
   - H-M2/H-M3 use existing model checkpoints — no additional compute needed beyond H-E1

3. **Failure Management:**
   - Document all gate failures with exact statistics (p-values, η², effect sizes)
   - Execute R2 PIVOT (educational value classifier) if KL differences < 0.01 nats
   - Execute R3 PIVOT (SoftDedup reweighting) if near-duplicate removal rate differential < 5pp

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: `/docs/youra_research/03_refinement.yaml` (ID: H-CurationScale-v1)
- Supplementary: `02_synthesis.yaml`, `01_round_table/final_opinions.yaml`
- Gap ID: gap-1 — "Causal Attribution of Curation Choices to Benchmark Outcomes Is Unestablished"

**B. MCP Tool Usage Summary**
- Total MCP calls: 3 (scientificmethod ×3: H-E1 hypothesis, H-E1 experiment, H-M integrated analysis)
- Tools: `mcp__clearThought__scientificmethod`
- Mode: Incremental (Phase 2A Dialogue available; 4–6 MCP calls budget; 3 used)

**C. Scope Reduction Summary**
- BUILD_ON (not re-verified): Individual curation method improvements (ProX, SoftDedup, REWIRE); PPL/ICL misalignment (DataMan); domain mixing orthogonality (WebOrganizer); modular training approximation (Na et al.)
- PROVE_NEW (verified by sub-hypotheses): Scale-dependent optimal PPL threshold (→ H-E1, H-M2); dedup sign reversal across scales (→ H-E1, H-M2); aggressive filtering efficiency at small scale (→ H-M3)
