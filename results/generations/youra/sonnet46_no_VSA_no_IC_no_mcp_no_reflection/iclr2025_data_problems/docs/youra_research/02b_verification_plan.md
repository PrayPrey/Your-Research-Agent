---
name: "02b_verification_plan"
hypothesis_id: "H-CorpusQualityGenBalance-v1"
confidence_level: 0.72
total_hypothesis_count: 5
generated_at: "2026-08-31"
status: in_progress
stepsCompleted:
  - step-00-init-environment
  - step-01-init-parsing
  - step-02-input-hypothesis
---

# Verification Plan: Corpus Quality as a Predictor of Generalization Balance

**Date:** 2026-08-31
**Hypothesis ID:** H-CorpusQualityGenBalance-v1
**Confidence:** 0.72
**Total Hypotheses:** 5 (H-E1, H-M1, H-M2, H-M3, H-M4)

---

## 0. Established Facts & Scope Reduction

**BUILD_ON Claims (DO NOT RE-VERIFY — use as motivating context):**

| Claim | Evidence | Status |
|-------|----------|--------|
| Deduplication improves benchmark performance on some tasks | Biderman et al. 2023 — Pythia dedup ablation | BUILD_ON |
| Web data filtering outperforms unfiltered data on average benchmark performance | Penedo et al. 2023 — RefinedWeb vs The Pile on Falcon | BUILD_ON |
| Domain mixing ratios affect benchmark performance profile | Groeneveld et al. 2024 — OLMo Dolma domain ablations | BUILD_ON |

**PROVE_NEW Claims (Phase 2B–4 must validate these):**

| Claim | Evidence Gap |
|-------|-------------|
| No study has matched training token count comparing curated vs. uncurated model suites | Gap identified in Phase 1 literature survey |
| Corpus quality predicts OOD/ID generalization balance at matched training scale | Core hypothesis — untested |

**Scope Reduction: 60%** — 3 of 5 claims are BUILD_ON, skipping their re-verification saves ~60% of otherwise required experimental work.

**Phase 2B–4 Instructions:** Focus exclusively on the 2 PROVE_NEW claims. The BUILD_ON claims provide motivating context but do not require experimental verification.

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under a controlled matched-training-scale comparison (~300B tokens) between foundation models trained on corpora of differing curation quality, if corpus curation quality is higher (as measured by n-gram repetition rate, Flesch-Kincaid grade level, and language ID confidence applied to representative domain samples), then models will show better OOD-to-ID generalization balance (higher MMLU/HellaSwag performance ratio and higher ARC-Challenge/Easy performance delta), because higher-quality data contains less noise and fewer style-specific artifacts, allowing the model to learn more generalizable representations rather than domain-specific statistical patterns.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in MMLU/HellaSwag performance ratio or ARC-Challenge/Easy performance delta between Pythia-6.9B (The Pile, low curation) and OLMo-7B (Dolma, high curation) at approximately matched training token count (~300B tokens), after accounting for architecture differences via temporal trajectory analysis.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | The Pile + Dolma (standard) | The Pile (825GB, minimal curation) provides the low-curation baseline; Dolma (3T tokens, multi-stage quality filtering) provides the high-curation comparison. Both publicly available with documented recipes. |
| **Model** | Pythia-6.9B + OLMo-7B (intermediate checkpoints ~300B tokens) | Matched in parameter count; both release intermediate checkpoints enabling matched-token-count comparison; both supported natively by lm-evaluation-harness. |

**Dataset Details:**
- Source: EleutherAI/pile and allenai/dolma on HuggingFace Datasets
- Path: HuggingFace Hub — EleutherAI/pile, allenai/dolma

**Model Details:**
- Type: decoder-only transformer
- Source: EleutherAI/pythia-6.9b and allenai/OLMo-7B-hf on HuggingFace Hub

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| Pythia-6.9B (The Pile, full training) | MMLU ~25-30%, HellaSwag ~60-65%, ARC-Challenge ~30-35% | The Pile (825GB, minimal curation) |
| OLMo-7B (Dolma, full training) | MMLU ~28-35%, HellaSwag ~67-72%, ARC-Challenge ~38-44% | Dolma (3T tokens, multi-stage quality filtering) |
| RefinedWeb + Falcon-7B | HellaSwag ~75%, LAMBADA ~76% | RefinedWeb (aggressive web filtering) |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Intermediate checkpoints for Pythia-6.9B and OLMo-7B available at ~300B tokens on HuggingFace Hub | Pythia releases 154 checkpoints; OLMo releases intermediate checkpoints | Primary matched-scale comparison (P1) undermined; fallback to extrapolation with wider confidence intervals |
| A2 | n-gram repetition rate, Flesch-Kincaid grade level, and language ID confidence are valid proxies for curation quality relevant to downstream generalization | Each proxy captures a distinct quality dimension | Quality index lacks construct validity; results could be attributed to proxy measurement error |
| A3 | The Pile sub-domain mixing ratios are identical across all Pythia model sizes | Biderman et al. 2023 explicitly states same data order for all Pythia models | Within-Pythia P3 analysis compromised; mixing ratio variation adds confound |
| A4 | Architecture differences (GPT-Neo vs. LLaMA-style) can be bounded by temporal trajectory analysis | If architecture drives the effect, gap appears at minimal tokens; if data quality drives it, gap widens with tokens | Causal attribution to data quality not possible; results only describable as observational |
| A5 | Benchmark contamination rates differ between The Pile and Dolma in a direction that could inflate OLMo's apparent performance advantage | Dolma explicitly filtered near-duplicate content including potentially benchmark test sets | Performance difference could be partially/wholly explained by contamination rather than generalization quality |

### 1.6 Research Gap & Novelty

**Gap:** No existing study has performed a matched-training-scale comparison between corpora of differing curation quality using intermediate checkpoints. All prior cross-suite comparisons (RefinedWeb/Falcon, D4, Pythia dedup) are confounded by different token counts, architectures, or benchmark suites.

**Novelty:** (1) First matched-scale Pythia vs. OLMo comparison using intermediate checkpoints at ~300B tokens. (2) First application of a multi-proxy corpus quality index (n-gram + Flesch-Kincaid + language ID) to predict OOD/ID generalization balance rather than average benchmark performance. (3) First temporal trajectory analysis to distinguish data quality effects from architecture effects in this comparison.

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
**H-E1: Corpus Quality and Generalization Balance Existence**

**Statement**: Under a controlled matched-training-scale comparison (~300B tokens), if corpus curation quality differs between Pythia-6.9B (The Pile) and OLMo-7B (Dolma), then OLMo-7B will show a higher MMLU/HellaSwag performance ratio AND a higher ARC-Challenge/Easy delta than Pythia-6.9B, because the quality difference produces measurably different generalization balance.

**Rationale** (2-3 sentences):
This hypothesis validates the core phenomenon — that the curation quality difference between The Pile and Dolma actually manifests as a measurable difference in OOD/ID generalization balance at matched token count. Without demonstrating this existence, all mechanistic hypotheses are moot. This is the foundational gate: if the signal doesn't exist, the mechanism hypotheses cannot be tested.

**Variables** (from Phase 2A):
- Independent: Corpus curation level (The Pile vs. Dolma)
- Dependent: MMLU/HellaSwag performance ratio (primary); ARC-Challenge/Easy delta (secondary)
- Controlled: Training token count (~300B via intermediate checkpoints), evaluation framework (lm-evaluation-harness), benchmark test set versions

**Verification Protocol** (3-5 steps):
1. Identify and download Pythia-6.9B intermediate checkpoint corresponding to ~300B training tokens from HuggingFace Hub; verify token count from checkpoint metadata.
2. Identify and download OLMo-7B intermediate checkpoint corresponding to ~300B training tokens; verify token count from checkpoint metadata.
3. Run lm-evaluation-harness on both checkpoints: MMLU (5-shot), HellaSwag (0-shot), ARC-Easy (25-shot), ARC-Challenge (25-shot).
4. Compute MMLU/HellaSwag ratio and ARC-Challenge/Easy delta for both models; perform bootstrap statistical comparison (3 random prompt subsamples).
5. Evaluate: if OLMo ratio > Pythia ratio by > 0.02 absolute, Cohen's d > 0.2, p < 0.05 → existence confirmed.

**Success Criteria** (PoC: Direction-based):
- Primary: OLMo-7B MMLU/HellaSwag ratio > Pythia-6.9B ratio by > 0.02 absolute, Cohen's d > 0.2, p < 0.05
- Secondary: OLMo-7B ARC delta > Pythia-6.9B ARC delta (directional, p < 0.10)

**Failure Response**:
- IF fails: PIVOT — examine whether token count matching is valid; check if architecture confound (GPT-J null comparison) accounts for any observed difference; report negative result with mechanistic implications.

**Dependencies**: None (foundation)

**Source**: Phase 2A Section 5 (sh1_existence), Prediction P1

---

---
**H-M1: Noise Reduction Mechanism — Corpus Quality Reduces Training Noise**

**Statement**: Under a controlled sample-level analysis of The Pile and Dolma sub-domains, if corpus curation quality is higher (as measured by composite quality proxy score), then the training corpus will show lower n-gram repetition rates, higher syntactic complexity (Flesch-Kincaid), and higher language purity (fastText language ID confidence), because multi-stage curation filtering specifically targets these quality dimensions.

**Rationale** (2-3 sentences):
This hypothesis tests the first causal step: that the quality difference between corpora is empirically real and measurable via the proxy index, not assumed. If the quality proxy scores don't meaningfully differentiate The Pile and Dolma sub-domains, the causal mechanism collapses at Step 1. This provides construct validity for the quality index before attributing model performance differences to it.

**Variables** (from Phase 2A):
- Independent: Corpus identity (The Pile sub-domains vs. Dolma sources)
- Dependent: Composite quality proxy score (n-gram repetition rate + Flesch-Kincaid + language ID confidence)
- Controlled: Sample size (10K documents per sub-domain/source), metric computation code version

**Verification Protocol** (3-5 steps):
1. Sample 10K documents from each of 22 The Pile sub-domains and each of 7 Dolma sources.
2. Compute n-gram repetition rate (1-gram_repetition_fraction), Flesch-Kincaid grade level (normalized 0-1), and fastText language ID confidence for each document sample.
3. Calculate unweighted composite quality proxy score (mean of three metrics) for each sub-domain/source.
4. Compare Dolma source mean scores vs. The Pile sub-domain mean scores using Mann-Whitney U test.
5. Evaluate: if Dolma sources score significantly higher on composite index than The Pile sub-domains (p < 0.05), mechanism Step 1 is confirmed.

**Success Criteria** (PoC: Direction-based):
- Primary: Dolma sources show significantly higher composite quality proxy scores than The Pile sub-domains (Mann-Whitney U, p < 0.05)
- Secondary: Effect consistent across at least 2 of 3 individual proxy metrics

**Failure Response**:
- IF fails: EXPLORE — examine whether specific sub-domains drive any difference; test whether quality proxy metrics are appropriate for web-scraped content; document as proxy validity failure.

**Dependencies**: H-E1 (existence of performance difference must be confirmed first)

**Source**: Phase 2A Section 1.3 Causal Step 1, Assumption A2

---

---
**H-M2: Gradient Encoding Mechanism — Reduced Noise Enables Generalizable Pattern Learning**

**Statement**: Under a matched-scale training comparison, if corpus noise is lower (as established by H-M1), then gradient updates during Dolma training will encode more generalizable semantic/syntactic patterns rather than domain-specific distributional shortcuts, because less repetitive and more syntactically complex training signal forces the model to learn broader representations.

**Rationale** (2-3 sentences):
This hypothesis tests the theoretical mechanism linking data quality to representation quality — the critical "why" behind the observed performance difference. This causal step is harder to directly test but can be partially validated through proxy evidence: if the MMLU/HellaSwag performance gap widens with training tokens (temporal trajectory), this implicates gradient-level encoding differences rather than architectural differences. This step provides mechanistic plausibility evidence.

**Variables** (from Phase 2A):
- Independent: Training corpus quality level (The Pile vs. Dolma), training token count (143B vs. 300B checkpoints)
- Dependent: Performance gap trajectory (MMLU/HellaSwag ratio difference) across token counts
- Controlled: Architecture family (separate architectural null comparison via GPT-J), evaluation framework

**Verification Protocol** (3-5 steps):
1. Download Pythia-6.9B and OLMo-7B intermediate checkpoints at BOTH ~143B tokens AND ~300B tokens from HuggingFace Hub.
2. Run lm-evaluation-harness (MMLU 5-shot, HellaSwag 0-shot) on all four checkpoints (2 models × 2 token counts).
3. Compute MMLU/HellaSwag ratio for each checkpoint; calculate gap = OLMo ratio - Pythia ratio at each token count.
4. Run same evaluation on GPT-J-6B (architectural null: same GPT-Neo family as Pythia, trained on The Pile); compare GPT-J vs. Pythia ratio to isolate architecture effect.
5. Evaluate: if gap WIDENS with token count (300B gap > 143B gap), this implicates data quality over architecture; if gap is constant/narrowing, architecture is the likely driver.

**Success Criteria** (PoC: Direction-based):
- Primary: MMLU/HellaSwag ratio gap (OLMo - Pythia) at 300B tokens > gap at 143B tokens (directional widening)
- Secondary: GPT-J vs. Pythia ratio difference < OLMo vs. Pythia ratio difference (data quality effect exceeds architecture effect)

**Failure Response**:
- IF fails: EXPLORE — document architecture as likely primary driver; treat performance difference from H-E1 as observational; report as explicit limitation with causal attribution caveat.

**Dependencies**: H-M1 (quality proxy differentiation must be confirmed)

**Source**: Phase 2A Section 1.3 Causal Step 2, Assumption A4

---

---
**H-M3: Transfer Mechanism — Generalizable Representations Improve Cross-Task Transfer**

**Statement**: Under matched-scale evaluation, if OLMo-7B has encoded more generalizable representations (as evidenced by H-M2 temporal trajectory), then OLMo-7B will show specifically better transfer from commonsense-heavy tasks (HellaSwag) to knowledge-intensive tasks (MMLU), yielding a higher MMLU/HellaSwag ratio, because generalizable representations span diverse task domains while domain-specific shortcuts favor whichever task type the training data over-represents.

**Rationale** (2-3 sentences):
This hypothesis tests whether the observed MMLU/HellaSwag ratio difference from H-E1 is specifically explained by cross-task transfer (the claimed mechanism) rather than by overall performance inflation. If OLMo-7B simply scores better on all tasks equally, the curation mechanism would not explain the ratio — it would just be a general scale advantage. This step provides mechanistic specificity: the ratio improvement should be asymmetric (relatively more MMLU gain than HellaSwag gain).

**Variables** (from Phase 2A):
- Independent: Corpus curation quality (The Pile vs. Dolma)
- Dependent: Relative MMLU improvement vs. relative HellaSwag improvement (asymmetry of gains)
- Controlled: Token count (~300B), evaluation framework, architecture null baseline

**Verification Protocol** (3-5 steps):
1. From H-E1 benchmark results, extract OLMo-7B and Pythia-6.9B absolute MMLU and HellaSwag scores at ~300B tokens.
2. Compute relative gain: OLMo MMLU gain over Pythia (absolute difference) vs. OLMo HellaSwag gain over Pythia.
3. Test asymmetry: if OLMo MMLU gain > OLMo HellaSwag gain (relative to Pythia), the ratio improvement is mechanistically consistent with the curation-generalizable-representations claim.
4. Run TruthfulQA (0-shot, mc2) on both checkpoints as an additional cross-domain transfer probe.
5. Evaluate: if MMLU gain > HellaSwag gain AND TruthfulQA shows improvement consistent with direction → mechanism Step 3 supported.

**Success Criteria** (PoC: Direction-based):
- Primary: OLMo-7B MMLU absolute gain over Pythia > OLMo-7B HellaSwag absolute gain over Pythia (asymmetric cross-task transfer pattern)
- Secondary: OLMo-7B TruthfulQA mc2 accuracy > Pythia-6.9B TruthfulQA accuracy (directional)

**Failure Response**:
- IF fails: EXPLORE — if gains are symmetric, the curation mechanism may operate through overall noise reduction rather than cross-task transfer specificity; document as scope refinement.

**Dependencies**: H-M2 (temporal trajectory evidence for gradient encoding differences)

**Source**: Phase 2A Section 1.3 Causal Step 3, Prediction P1/P2

---

---
**H-M4: Accumulation Mechanism — Quality Advantage Widens with Training Tokens**

**Statement**: Under a temporal trajectory analysis comparing Pythia-6.9B and OLMo-7B at multiple token count checkpoints (143B and 300B), if corpus curation quality is higher, then the MMLU/HellaSwag performance ratio gap between OLMo-7B and Pythia-6.9B will widen as training progresses, because the signal-to-noise benefit of higher-quality data compounds over training — each gradient update in high-quality training builds more coherently on prior learning.

**Rationale** (2-3 sentences):
This hypothesis tests the temporal dynamics of the quality effect — the novel claim that quality advantage is not a fixed offset (consistent with architecture) but grows with training tokens. A widening gap is the key distinguisher between a data quality effect and an architecture effect. This provides the strongest evidence that the observed generalization balance difference is attributable to corpus curation rather than the GPT-Neo vs. LLaMA-style architectural difference.

**Variables** (from Phase 2A):
- Independent: Training token count (143B vs. 300B tokens) × corpus quality (The Pile vs. Dolma)
- Dependent: MMLU/HellaSwag ratio gap (OLMo - Pythia) at each token count
- Controlled: Evaluation framework, benchmark versions, same checkpoint identification method

**Verification Protocol** (3-5 steps):
1. From H-M2 multi-checkpoint evaluation, extract MMLU/HellaSwag ratios for both models at 143B and 300B tokens.
2. Compute gap_143B = OLMo ratio at 143B − Pythia ratio at 143B.
3. Compute gap_300B = OLMo ratio at 300B − Pythia ratio at 300B.
4. Compare: if gap_300B > gap_143B → widening trajectory → data quality mechanism supported; if gap_300B ≤ gap_143B → constant/narrowing → architecture explanation preferred.
5. Report trajectory with confidence intervals (bootstrap); note that widening is directional evidence, not definitive proof due to only 2 data points.

**Success Criteria** (PoC: Direction-based):
- Primary: gap_300B > gap_143B (widening trajectory, directional)
- Secondary: GPT-J vs. Pythia ratio gap does NOT widen over equivalent training token periods (architectural confound ruled out)

**Failure Response**:
- IF fails: PIVOT — re-examine whether token count identification was accurate; document constant gap as evidence that architecture may dominate at 6-7B scale/300B token regime; report as explicit scope boundary for the curation quality mechanism.

**Dependencies**: H-M3 (transfer mechanism evidence)

**Source**: Phase 2A Section 1.3 Causal Step 4, Causal Key Tension (architecture confound)

---

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | OLMo MMLU/HellaSwag ratio > Pythia by >0.02, d>0.2, p<0.05 | STOP — reassess entire hypothesis |
| H-M1 | MUST_WORK | Dolma sources score significantly higher on quality proxy (p<0.05) | PIVOT — proxy validity issue; document as limitation |
| H-M2 | SHOULD_WORK | Gap widens 143B→300B tokens (directional) | EXPLORE — architecture may dominate; document |
| H-M3 | SHOULD_WORK | OLMo MMLU gain > OLMo HellaSwag gain (asymmetric) | EXPLORE — symmetric gains; refine mechanism scope |
| H-M4 | SHOULD_WORK | gap_300B > gap_143B (temporal widening) | PIVOT — report constant gap; architectural scope boundary |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1 → H-M4 (sequential) | 5 weeks (1+1+1+2) |
| **Total** | 5 hypotheses | **7 weeks** |

**Total Duration:** 7 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

**Risk R1 (from A1): Checkpoint Unavailability at ~300B Tokens**

**Source Assumption:** A1 — Intermediate checkpoints for Pythia-6.9B and OLMo-7B available at ~300B tokens.

**Description:** OLMo may not release a checkpoint at exactly ~300B tokens (it releases milestone checkpoints); exact token count mismatch > 20B tokens would weaken the matched-scale claim.

**Affected Hypotheses:** H-E1, H-M2, H-M4 (all depend on matched-scale comparison)

**Severity:** HIGH

**Mitigation Strategy:**
1. **Prevention:** Verify exact token counts for both model checkpoint series BEFORE any evaluation; document nearest available checkpoints; pre-register the token count matching criterion (within ±20B tokens acceptable).
2. **Detection:** Download checkpoint metadata and extract step/token_count fields before loading model weights.
3. **Response:**
   - PIVOT: If within ±20B tokens — proceed, report approximation as explicit limitation.
   - SCOPE: If mismatch 20-50B tokens — use linear interpolation of adjacent checkpoints; report with wider uncertainty bounds.
   - ABORT H-E1 primary test if mismatch >50B tokens; fallback to qualitative comparison only.

**Early Warning Indicators:**
- OLMo checkpoint step counts don't align with ~300B tokens when converted via OLMo's documented tokens-per-step ratio
- Pythia checkpoint metadata shows different token_count than Biderman et al. 2023 reports

---

**Risk R2 (from A2): Quality Proxy Index Lacks Construct Validity**

**Source Assumption:** A2 — n-gram repetition rate, Flesch-Kincaid, and language ID confidence are valid proxies for curation quality relevant to downstream generalization.

**Description:** The three metrics may not capture the quality dimensions most relevant to the MMLU/HellaSwag performance gap; equal weighting may mismatch the actual importance of each dimension.

**Affected Hypotheses:** H-M1 (directly tests proxy validity)

**Severity:** MEDIUM

**Mitigation Strategy:**
1. **Prevention:** Pre-specify equal weighting; commit to this before running experiments; do NOT post-hoc optimize weights.
2. **Detection:** If H-M1 fails to differentiate The Pile vs. Dolma, examine individual metric distributions before composite.
3. **Response:**
   - EXPLORE: If composite fails, test individual metrics; report which dimensions (if any) differentiate corpora.
   - SCOPE: Report proxy validity as explicit study limitation; recommend future work on validated quality indices.

**Early Warning Indicators:**
- Flesch-Kincaid distributions highly overlapping between Pile and Dolma samples
- n-gram repetition rate not significantly different at 10K sample level

---

**Risk R3 (from A3): Pile Sub-Domain Mixing Ratio Inconsistency**

**Source Assumption:** A3 — The Pile sub-domain mixing ratios are identical across all Pythia model sizes.

**Description:** If mixing ratios vary across Pythia model sizes, the within-Pythia quality-benchmark correlation (P3) would be confounded by domain exposure variation.

**Affected Hypotheses:** H-M1 (within-Pythia quality-benchmark correlation requires consistent sub-domain exposure)

**Severity:** LOW (H-M1 as designed primarily tests inter-corpus quality difference, not within-Pythia P3)

**Mitigation Strategy:**
1. **Prevention:** Cross-reference Pythia training documentation (Biderman et al. 2023 Appendix) for sub-domain mix specification before running P3 analysis.
2. **Detection:** Compare reported sub-domain proportions across Pythia model sizes in published documentation.
3. **Response:**
   - SCOPE: If inconsistent, drop the within-Pythia sub-domain regression (P3); focus on the primary inter-corpus comparison (P1, P2).

**Early Warning Indicators:**
- Biderman et al. 2023 documentation shows different data mixing per model size

---

**Risk R4 (from A4): Architecture Confound Dominates Data Quality Effect**

**Source Assumption:** A4 — Architecture differences can be bounded by temporal trajectory analysis.

**Description:** The GPT-Neo vs. LLaMA-style architectural difference may produce a constant performance gap regardless of data quality, making it impossible to attribute the MMLU/HellaSwag ratio difference to curation quality.

**Affected Hypotheses:** H-M2, H-M4 (temporal trajectory analysis is designed to bound this)

**Severity:** HIGH

**Mitigation Strategy:**
1. **Prevention:** Run GPT-J-6B (architectural null: same GPT-Neo family as Pythia, trained on The Pile) as control.
2. **Detection:** If gap_300B ≈ gap_143B, architecture confound cannot be ruled out.
3. **Response:**
   - PIVOT: If gap is constant — report as observational finding; attribute to architecture + data quality without being able to disentangle; recommend future controlled experiment with same architecture.
   - Must report as primary limitation in all cases regardless of outcome.

**Early Warning Indicators:**
- GPT-J-6B vs. Pythia-6.9B MMLU/HellaSwag ratio difference is comparable in magnitude to OLMo-7B vs. Pythia-6.9B difference

---

**Risk R5 (from A5): Benchmark Contamination Confounds OLMo Advantage**

**Source Assumption:** A5 — Benchmark contamination differences could inflate OLMo's apparent performance advantage.

**Description:** Dolma's near-duplicate filtering may have removed benchmark test set content from training data, making OLMo appear to generalize better when it actually simply saw less training contamination from the test sets.

**Affected Hypotheses:** H-E1 (directly threatens the primary performance comparison)

**Severity:** HIGH

**Mitigation Strategy:**
1. **Prevention:** Run Min-K% Prob contamination audit on MMLU, HellaSwag, ARC test sets using both Pythia and OLMo model likelihoods BEFORE interpreting performance results.
2. **Detection:** If OLMo shows lower perplexity on benchmark test sets despite better performance, contamination is likely; if higher perplexity → no contamination advantage.
3. **Response:**
   - SCOPE: Report Min-K% Prob results alongside benchmark results; flag any benchmarks where contamination differential is detected; interpret those benchmark results with appropriate caveats.
   - ABORT: If contamination audit reveals OLMo has systematically lower perplexity on benchmark test sets → downgrade P1 from confirmed to "contamination-confounded"; shift primary evidence to TruthfulQA (least likely to be contaminated).

**Early Warning Indicators:**
- OLMo shows unusually high performance on MMLU subsets that appear verbatim in CommonCrawl-derived corpora

---

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Checkpoint unavailability at ~300B tokens | A1 | H-E1, H-M2, H-M4 | HIGH |
| R2: Quality proxy index lacks construct validity | A2 | H-M1 | MEDIUM |
| R3: Pile sub-domain mixing ratio inconsistency | A3 | H-M1 | LOW |
| R4: Architecture confound dominates data quality | A4 | H-M2, H-M4 | HIGH |
| R5: Benchmark contamination confounds OLMo advantage | A5 | H-E1 | HIGH |

**Risk Summary: Critical: 0, High: 3, Medium: 1, Low: 1**

---

## 5. Execution Plan

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root: MUST_WORK]
    H-E1: Existence of Quality-Generalization Balance Effect
    (No dependencies — runs first)
         │
         ▼ [Gate 1: MUST PASS or STOP]
[Level 1 - Foundation Mechanism: MUST_WORK]
    H-M1: Noise Reduction Mechanism
    ← requires H-E1 passed
         │
         ▼ [Gate 2: MUST PASS or PIVOT]
[Level 2 - Gradient Mechanism: SHOULD_WORK]
    H-M2: Gradient Encoding Mechanism (temporal trajectory)
    ← requires H-M1 passed
         │
         ▼
[Level 3 - Transfer Mechanism: SHOULD_WORK]
    H-M3: Cross-Task Transfer Mechanism
    ← requires H-M2
         │
         ▼
[Level 4 - Accumulation Mechanism: SHOULD_WORK]
    H-M4: Quality Advantage Accumulation (widening gap)
    ← requires H-M3

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy Table

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |
| 4 | H-M4 | H-M3 | SHOULD_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis     │ W1-2     │ W3-4     │ W5       │ W6       │ W7
─────────────────────┼──────────┼──────────┼──────────┼──────────┼──────────
PHASE 1: Foundation
  H-E1 (Existence)   │ ████████ │          │          │          │
  [Gate 1]           │          │ ◆        │          │          │
─────────────────────┼──────────┼──────────┼──────────┼──────────┼──────────
PHASE 2: Mechanisms
  H-M1 (Noise)       │          │ ████████ │          │          │
  H-M2 (Gradient)    │          │          │ ████     │          │
  H-M3 (Transfer)    │          │          │          │ ████     │
  H-M4 (Accumulate)  │          │          │          │          │ ████
  [Gate 2]           │          │          │          │          │      ◆
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 7 weeks
═══════════════════════════════════════════════════════════════════
```

**Note:** H-M2 temporal trajectory data is collected AS PART OF H-E1 multi-checkpoint evaluation (both 143B and 300B checkpoints downloaded at same time). H-M2 analysis uses this pre-collected data, making its active work period shorter.

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4

Total Duration: 7 weeks
  Formula: 2 (H-E1) + 5 (H-M1 through H-M4) weeks

Slack Available: 0 weeks (all sequential)

Duration Formula: 2 (H-E1) + 4 (H-M steps) + 1 (H-M4 needs 2 weeks) = 7 weeks
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 5
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1 to H-M4)
- Condition: 0 (not required)

Verification Phases: 2
1. Foundation (H-E1): 2 weeks, ~8-16 GPU hours
2. Mechanisms (H-M1 through H-M4): 5 weeks, ~2-4 GPU hours each

Total Duration: 7 weeks
Critical Path Length: 7 weeks
Execution Mode: Sequential chain
Compute Estimate: ~16-32 GPU hours total (mostly evaluation, no training)
Data Requirements: HuggingFace Hub access (all public checkpoints)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

```
Step 1: Execute H-E1 (Foundation) — Week 1-2
  - Download Pythia-6.9B and OLMo-7B checkpoints at BOTH 143B and 300B tokens
  - Run lm-evaluation-harness: MMLU, HellaSwag, ARC-E/C, WinoGrande, TruthfulQA
  - Run Min-K% Prob contamination audit (concurrent — use same model loads)
  - Compute MMLU/HellaSwag ratio and ARC delta for both models at ~300B tokens
Step 2: Evaluate Gate 1 → If ratio diff < 0.02 or p > 0.05: STOP; else proceed
Step 3: Execute H-M1 (Noise Reduction) — Week 3-4
  - Sample 10K documents per Pile sub-domain (22) and Dolma source (7)
  - Compute quality proxy scores; compare Dolma vs. Pile via Mann-Whitney U
Step 4: Evaluate Gate 2 → If quality proxies don't differentiate: PIVOT; else proceed
Step 5: Execute H-M2 (Gradient Encoding) — Week 5
  - Use already-collected 143B and 300B benchmark results from H-E1
  - Run GPT-J-6B evaluation (architectural null comparison)
  - Compute temporal trajectory (gap widening or constant)
Step 6: Execute H-M3 (Transfer Mechanism) — Week 6
  - Use benchmark scores from H-E1; compute asymmetry of gains
Step 7: Execute H-M4 (Accumulation) — Week 7
  - Use temporal trajectory data from H-M2; assess gap widening direction
Step 8: Final evaluation — all SHOULD_WORK results documented; Phase 4.5 synthesis ready
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Claim: Higher corpus curation quality → better OOD/ID generalization
balance at matched training scale (~300B tokens), because higher-quality
data produces more generalizable gradient-encoded representations.

Supporting Evidence:
1. Penedo et al. 2023: aggressive filtering removed 88% of web tokens,
   retaining higher-quality signal with better benchmark outcomes
2. Groeneveld et al. 2024: OLMo domain ablations show academic content
   improves MMLU specifically (consistent with quality → generalization)
3. Theoretical: neural scaling law literature consistent with data quality ×
   token count interaction (Muennighoff et al. 2023)

Strengths:
- Archival experiment design: no new training required (all data public)
- Matched token count (via intermediate checkpoints) addresses primary confound
- Multi-proxy quality index is domain-neutral and theoretically grounded
- OOD/ID balance ratio is more diagnostic than average benchmark performance

Expected Outcomes:
- Primary (P1): OLMo-7B MMLU/HellaSwag ratio > Pythia-6.9B by >0.02, d>0.2, p<0.05
- Secondary (P2): OLMo-7B ARC-Challenge/Easy delta > Pythia-6.9B (directional, p<0.10)
- Tertiary (P3): Pile sub-domain quality proxy r > 0.3 with ≥3/5 benchmarks
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Null Hypothesis (H0): No significant difference in MMLU/HellaSwag ratio
or ARC-Challenge/Easy delta between Pythia-6.9B and OLMo-7B at ~300B tokens,
after accounting for architecture differences via temporal trajectory analysis.

Counter-Arguments:
1. Architecture confound: GPT-Neo vs. LLaMA-style architecture differences
   produce systematic performance differences independent of training data quality;
   prior cross-architecture comparisons routinely show 5-15% performance deltas
2. Token count approximation: even a ±20B token mismatch introduces scale confounds
   that could account for small performance differences (especially given Chinchilla
   scaling laws predict meaningful improvement per token at 300B scale)
3. Benchmark contamination: Dolma's explicit near-duplicate filtering against
   CommonCrawl may have removed benchmark test set content, inflating OLMo's
   apparent generalization advantage

Potential Failure Points:
- R4: Architecture confound dominates — constant gap with tokens (SHOULD_WORK failures)
- R1: Checkpoint token counts don't match sufficiently — scale confound remains
- R5: Min-K% Prob reveals systematic contamination advantage for OLMo

Conditions Under Which H0 Would Be Supported:
- MMLU/HellaSwag ratio difference ≤ 0.02 absolute, OR confidence intervals overlap at α=0.05
- Gap_300B ≤ gap_143B (constant/narrowing temporal trajectory → architecture drive)
- GPT-J-6B vs. Pythia ratio gap ≈ OLMo-7B vs. Pythia ratio gap (same family, same gap)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balanced Assessment:
The hypothesis H-CorpusQualityGenBalance-v1 presents a well-structured
testable claim with clear empirical predictions. However, the null hypothesis
raises valid concerns regarding three confounds: (1) architecture differences
that may dominate corpus quality effects at the 7B/300B parameter-token regime,
(2) token count approximation uncertainty that limits precision of matched-scale
claims, and (3) contamination differentials that may inflate observed performance
differences.

Resolution Path:
The verification plan addresses this dialectic through:
1. Foundation verification (H-E1): Establishes whether the performance difference
   exists before attributing it to mechanism
2. Contamination audit (concurrent with H-E1): Bounds the contamination alternative
   explanation before interpreting benchmark results
3. Temporal trajectory analysis (H-M2, H-M4): Key distinguisher — if gap widens
   with tokens, architecture explanation is ruled out; if constant, architecture dominates
4. Architectural null comparison (GPT-J-6B, concurrent with H-M2): Direct architecture
   confound control without requiring new training

Conditions for Thesis Support:
- H-E1 MUST_WORK gate passes (ratio diff > 0.02, p < 0.05)
- H-M1 MUST_WORK gate passes (quality proxies differentiate corpora)
- H-M2/H-M4 show widening temporal trajectory (data quality favored over architecture)
- Contamination audit shows no systematic OLMo advantage

Conditions for Antithesis Support:
- H-E1 fails (ratio difference ≤ 0.02 or not significant) → H0 not rejected
- H-M2/H-M4 show constant gap → architecture as primary driver → corpus effect undetectable
- Contamination audit reveals systematic OLMo advantage → results not interpretable as quality effect

Nuanced Outcome Possibilities:
1. Full Support: H-E1 passes + widening trajectory → corpus quality mechanism established
2. Partial Support (observational): H-E1 passes + constant trajectory → difference observed
   but causally attributed to architecture; reports as data quality × architecture interaction
3. No Support: H-E1 fails → H0 not rejected; publish negative result with methodological contribution
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 ROBUSTNESS ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | OOD/ID balance difference exists at matched scale | Architecture or contamination drives apparent difference | H-E1 test + contamination audit |
| Mechanism | 4-step causal chain (noise → gradients → transfer → accumulation) | Architecture difference is simpler explanation | Temporal trajectory (H-M2/H-M4) + GPT-J null |
| Proxy Validity | n-gram + Flesch-Kincaid + language ID are valid quality proxies | Proxies don't capture curation-relevant quality dimensions | H-M1 empirical validation of proxy differentiation |
| Scope | Generalizes to 6-8B models at ~300B tokens | Only two corpora compared; cannot establish continuous curve | Reported as scope limitation; not claimed to generalize beyond |

Overall Robustness Score: MEDIUM-HIGH
- Design is rigorous for an archival experiment (no new training)
- Main vulnerability: architecture confound is real and not fully eliminable
- Contamination confound has a specific detection + mitigation plan (Min-K% Prob)
- Negative results are equally publishable (methodological contribution stands)

Confidence in Verification Plan: 0.72 (matches Phase 2A confidence)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Corpus curation quality predicts OOD/ID generalization balance at matched training scale — higher-quality corpus → higher MMLU/HellaSwag ratio + higher ARC-Challenge/Easy delta at ~300B tokens.
- ID: H-CorpusQualityGenBalance-v1, Confidence: 0.72

**Verification Structure:**
- Mode: Incremental (Phase 2A data available, 60% scope reduction applied)
- Sub-Hypotheses: 5 total (H-E1: 1, H-M: 4)
- Phases: 2 phases over 7 weeks
- Critical Gates: 2 decision points (Gate 1 after H-E1; Gate 2 after H-M1)

**Risk Assessment:** HIGH (3 high-severity risks: checkpoint availability, architecture confound, contamination)
- Primary concerns: Architecture confound (R4) and benchmark contamination (R5)

**Immediate Action:** Begin Phase 1 with H-E1 — download checkpoints at both 143B and 300B tokens, run contamination audit concurrently.

### 7.2 Conclusions

**Key Achievements:**
- 5 hypotheses across 2 phases defined with clear falsification criteria
- 60% scope reduction: 3 BUILD_ON claims excluded from verification
- H0 addressed: No significant performance ratio difference after architecture control
- All 5 hypotheses have quantitative success criteria and explicit failure responses

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Verify OLMo-7B MMLU/HellaSwag ratio > Pythia-6.9B at matched ~300B tokens
- Concurrent: Min-K% Prob contamination audit on all benchmark test sets
- Gate 1: MUST PASS (ratio diff > 0.02, p < 0.05) or STOP

**Phase 2: Core Mechanisms** (5 weeks)
- H-M1: Verify Dolma vs. Pile quality proxy differentiation (Week 3-4)
- H-M2: Verify temporal trajectory (gap widening 143B→300B) + GPT-J null (Week 5)
- H-M3: Verify asymmetric cross-task transfer pattern (Week 6)
- H-M4: Verify quality advantage accumulation signature (Week 7)
- Gate 2: H-M1 must pass or PIVOT

**Critical Decision Points:**

1. **Gate 1 (Foundation):** H-E1 must pass (MUST_WORK)
   - FAIL → STOP: Reassess entire hypothesis; negative result is publishable
   - PASS → Proceed to Phase 2

2. **Gate 2 (Foundation Mechanism):** H-M1 must pass (MUST_WORK)
   - FAIL → PIVOT: Proxy validity issue; document as limitation, continue descriptively
   - PASS → Continue H-M2 through H-M4

3. **H-M2/H-M4 Temporal Trajectory:** (SHOULD_WORK)
   - Widening gap → data quality mechanism supported (thesis)
   - Constant gap → architecture explanation favored (antithesis, valid negative result)

**Open Questions:**
- Exact token counts for Pythia-6.9B and OLMo-7B intermediate checkpoints at ~300B tokens — need verification before analysis begins
- Whether OLMo releases a ~300B-token intermediate checkpoint (vs. only milestone checkpoints)
- Pre-specified weights for the composite quality index sensitivity analysis
- Statistical power analysis: how many bootstrap samples for reliable Cohen's d estimates

**Recommendations:**

1. **Immediate Actions:**
   - Verify checkpoint token counts FIRST (before downloading full weights)
   - Set up lm-evaluation-harness environment with consistent version pinning
   - Pre-register quality index equal weighting before any data collection

2. **Resource Allocation:**
   - Allocate 7 weeks total for critical path
   - Reserve 1-2 week buffer for checkpoint discovery issues
   - ~16-32 GPU hours sufficient (evaluation only, no training)

3. **Failure Management:**
   - Document all failures with raw results regardless of direction
   - Execute PIVOT strategies for H-M failures (document as scope, not invalidation)
   - Architecture confound: report explicitly in all cases as primary limitation

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: docs/youra_research/03_refinement.yaml (ID: H-CorpusQualityGenBalance-v1)
- Generated: 2026-08-31, schema_version 10.0.0, 12 discussion exchanges
- Convergence: All 6 criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

**B. MCP Tool Usage Summary**
- Total MCP calls: 0 (ABLATION MODE — ClearThought/Archon MCP unavailable)
- Reasoning: LLM first-principles analysis substituted for MCP scientificmethod calls
- Hypothesis generation: Direct mapping from Phase 2A causal_chain_count=4 → H-E1 + H-M1 through H-M4

