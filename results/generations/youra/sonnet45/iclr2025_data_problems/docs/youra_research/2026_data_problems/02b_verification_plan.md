---
stepsCompleted: [step-00, step-01, step-02, step-03, step-04, step-05, step-06, step-07, step-08, step-09, step-10]
status: complete
completedAt: "2026-03-17T00:00:00Z"
hypothesis_id: H-DocCuration-v1
research_scope_mode: incremental
---

# Verification Plan: Curation Documentation as Benchmark Performance Predictor

**Date:** 2026-03-17
**Hypothesis ID:** H-DocCuration-v1
**Confidence:** 0.72
**Total Hypotheses:** 4 (H-E1, H-M1, H-M2, H-M3)

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under the set of open-weight LLMs listed on the Open LLM Leaderboard v1 snapshot with publicly
accessible model cards, if models have documented pretraining data curation practices (binary
indicators: deduplication, perplexity-based filtering, domain composition reporting, decontamination),
then those models exhibit ≥0.5 percentage points higher benchmark performance on knowledge-recall
benchmarks (MMLU, ARC) relative to a scale-and-architecture baseline (controlling for log(N),
log(D), and architecture family fixed effects), because documented curation practices serve as a
proxy for higher effective data quality Q in the Subramanyam et al. (2025) scaling framework —
labs that document curation rigorously are more likely to have implemented it rigorously, and
higher Q reduces effective data corruption, shifting L(N,D,Q) toward lower loss on
knowledge-intensive tasks.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in benchmark performance on MMLU or ARC between models with
documented curation practices and models without, after controlling for log(parameter count),
log(training tokens), and architecture family fixed effects (β_docs = 0).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Open LLM Leaderboard v1 Snapshot + Hugging Face Model Cards (standard) | Natural observational corpus with ~3000+ model evaluations; Thrush et al. (2024) used same source for perplexity-benchmark correlations; static v1 snapshot eliminates temporal confounds |
| **Model** | N/A (statistical analysis, not ML training) | Standard OLS regression sufficient for correlational observational study; no deep learning infrastructure required |

**Dataset Details:**
- Source: https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard
- Path: Public — downloadable via HuggingFace Datasets or web scraping

**Model Details:**
- Type: OLS regression / partial correlation
- Source: statsmodels, scipy, pandas (Python)

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| Scale-only OLS (log N + log D) | Explains ~60-70% benchmark variance | Open LLM Leaderboard v1 |
| Scale + Architecture FE OLS | Higher R² within families; ~60-75% benchmark variance | Open LLM Leaderboard v1 |
| Verbosity placebo (model card char count) | Placeholder — compare vs documentation block ΔR² | Open LLM Leaderboard v1 |
| Within-bin random permutation null | Null distribution for β_docs under H0 | Open LLM Leaderboard v1 |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Documentation presence reflects actual curation implementation | Djuhera et al. (2025) annotations; bridge validation designed to test this | Documentation reflects organizational competence only — changes interpretation, not falsification |
| A2 | Open LLM Leaderboard v1 scores comparable across models | Lunardi et al. (2025): benchmark rankings stable; fixed LM-Evaluation-Harness | Score incomparability attenuates coefficients; bias only if scoring errors correlate with documentation |
| A3 | N and D recoverable for ~500+ leaderboard models | LLaMA-2, Mistral, Falcon, Pythia all report N and D; HF model pages provide parameters | Reduced sample; N-only fallback sensitivity analysis available |
| A4 | Architecture family FE controls systematic between-family differences | Standard econometric panel design; leave-one-family-out validates | FE absorbs real signal if within-family variation too small; leave-out analysis addresses this |
| A5 | Effect detectable at n≈500-2000 with 0.3-1.2pp expected magnitude | Power analysis: n=500, Cohen's f²≈0.02, α=0.05 → power≈0.80 | If true effect <0.2pp, underpowered — accept null as negligible effect |

### 1.6 Research Gap & Novelty

**Gap:** No systematic observational study links documented LLM pretraining curation choices to benchmark performance variance. Prior work (Thrush et al. 2024) uses computed perplexity as proxy for prospective data selection, not retrospective characterization of deployed models. Subramanyam et al. (2025) establishes controlled experimental Q effects but not observational proxies via documentation.

**Novelty:** First observational study merging model card curation features with leaderboard benchmark data at scale. Creates the **LLM Documentation-Benchmark Registry** — a reusable annotated dataset enabling empirical testing of whether documentation discipline predicts deployment quality. Opens new research program: documentation as predictive feature (vs. documentation artifact).

**Scope Reduction:** 40% of claims are BUILD_ON (already validated) — Phase 2B focuses only on 2 PROVE_NEW claims: (1) documentation features predict above-scale-expected benchmark variance; (2) effect is concentrated in knowledge-recall benchmarks.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | PENDING |
| H-M2 | MECHANISM | MUST_WORK | H-M1 | PENDING |
| H-M3 | MECHANISM | MUST_WORK | H-M2 | PENDING |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Registry Construction Feasibility**

**Statement**: Under the Open LLM Leaderboard v1 snapshot, if model cards are publicly accessible on HuggingFace for a sufficient fraction of evaluated models, then a dataset of ≥200 models with non-missing binary curation documentation features, ≥4/6 benchmark scores, and recoverable parameter count can be assembled, because major open-weight model families (LLaMA, Falcon, Mistral, Pythia) consistently publish detailed model cards with the required feature information.

**Rationale**: The entire analysis depends on having adequate sample size with sufficient documentation variation. Without n ≥ 200 and meaningful variance in doc_score (0-4), no regression analysis is possible. This existence check is the prerequisite gate for all mechanism hypotheses.

**Variables**:
- Independent: Presence/absence of HuggingFace model card with ≥1 documented curation feature
- Dependent: Number of models with complete feature set (n_complete); doc_score distribution (0-4)
- Controlled: Benchmark score availability threshold (≥4/6 benchmarks)

**Verification Protocol**:
1. Download Open LLM Leaderboard v1 static snapshot via HuggingFace Datasets API or direct scrape.
2. For each model, attempt model card retrieval via HuggingFace Hub API and extract 4 binary features using pre-registered keyword rules.
3. Filter to models with ≥4/6 benchmark scores AND recoverable parameter count (N); record dropout rate.
4. Compute doc_score distribution and verify non-trivial variance (not >90% at 0 or >90% at 4).
5. Report final n_analyzable; confirm ≥200 with all required fields.

**Success Criteria**:
- Primary: n_analyzable ≥ 200 models with complete feature set
- Secondary: doc_score variance > 0 in at least 3 of 4 features; n with training tokens D recoverable ≥ 100

**Failure Response**:
- IF n < 200: PIVOT — expand to v1+v2 snapshot or relax to ≥3/6 benchmarks; document as limitation
- IF doc_score uniformly 0 or 4: EXPLORE — manual review of feature extraction rules; consider annotation revision

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A Section 5 (sh1_existence), Prediction P1 data requirements

---
**H-M1: Documentation-Implementation Bridge**

**Statement**: Under the subset of Open LLM Leaderboard models with accessible pretraining corpora (Pythia, OLMo, LLaMA family variants), if a model's card documents deduplication or perplexity-based filtering, then that model's training corpus exhibits measurably lower 13-gram duplication rate and lower cross-entropy relative to a reference LM, because labs that document curation practices have also implemented them with sufficient rigor to leave hygiene artifacts detectable in the corpus.

**Rationale**: This bridge validation step tests Assumption A1 — the core interpretive claim that documentation proxies for actual Q. If documentation does not predict hygiene artifacts, the main hypothesis must be reinterpreted as "organizational competence signal" rather than Q-mechanism, which changes the contribution framing. The bridge result is a pre-registered conditional that determines interpretation regardless of main regression outcome.

**Variables**:
- Independent: dedup_documented (binary), perplexity_filter_documented (binary)
- Dependent: 13-gram duplication rate in corpus (lower = better dedup); mean cross-entropy vs. GPT-2 reference model
- Controlled: Corpus size (tokens), domain composition

**Verification Protocol**:
1. Identify models with accessible pretraining corpora — expected: Pythia (The Pile), OLMo (Dolma), LLaMA-1 (subset).
2. For each accessible corpus, compute 13-gram duplication rate using suffix array or MinHash approximation.
3. Compute mean cross-entropy of corpus text against GPT-2 as proxy for perplexity filtering stringency.
4. Regress hygiene metrics on documentation binary indicators controlling for corpus size.
5. Report bridge validation coefficient and 95% CI; determine conditional interpretation pathway.

**Success Criteria**:
- Primary: dedup_documented predicts lower 13-gram duplication rate (β < 0, p < 0.1; n is small, lower threshold acceptable)
- Secondary: perplexity_filter_documented predicts lower mean cross-entropy vs. reference model

**Failure Response**:
- IF bridge fails: EXPLORE — reframe main hypothesis as organizational competence proxy; update interpretation section; proceed to H-M2 with modified framing
- IF corpus access <5 models: document as limitation; skip bridge; proceed with caveat

**Dependencies**: H-E1 (registry must exist)

**Source**: Phase 2A Section 1.3 Causal Step 1, Assumption A1

---
**H-M2: Documentation Predicts Scale-Adjusted Benchmark Performance**

**Statement**: Under open-weight LLMs in the assembled Registry (n ≥ 200), if models have higher doc_score (sum of 4 binary curation documentation features), then those models exhibit ≥0.5 percentage points higher MMLU accuracy after controlling for log(parameter count), log(training tokens), and architecture family fixed effects, because documented curation practices proxy for higher effective data quality Q which reduces knowledge-intensive task loss via the Subramanyam et al. (2025) L(N,D,Q) framework.

**Rationale**: This is the primary empirical claim of the study. Testing whether documentation features explain residual benchmark variance above scale-and-architecture controls directly validates the core hypothesis. A positive result provides observational evidence that data documentation discipline correlates with deployment quality; a null result is also informative as an upper bound on the magnitude of any documentation-quality signal.

**Variables**:
- Independent: doc_score (0-4 continuous), or binary high-doc (≥3) vs. low-doc (0-1)
- Dependent: MMLU accuracy (5-shot, primary); ARC accuracy (25-shot, secondary)
- Controlled: log(parameter_count), log(training_tokens), architecture_family (fixed effects)

**Verification Protocol**:
1. Fit OLS baseline models: (a) scale-only, (b) scale + architecture FE; record R² and residual variance.
2. Fit full model: MMLU ~ log(N) + log(D) + arch_FE + doc_score; extract β_docs and 95% CI.
3. Run within-bin permutation test: 1,000 shuffles of doc_score within architecture × ±50% parameter bands; compute permutation p-value.
4. Compute partial R² for documentation block (full vs. reduced model nested F-test).
5. Run leave-one-architecture-family-out stability: verify β_docs retains sign and ≥50% magnitude.

**Success Criteria**:
- Primary: β_docs ≥ 0.5pp for MMLU AND permutation p < 0.01 (within-bin)
- Secondary: Partial R² ≥ 0.03 for documentation block; β_docs retains sign in all leave-one-family-out runs

**Failure Response**:
- IF β_docs < 0.2pp: ABANDON — accept null; report upper bound on documentation-quality signal
- IF 0.2pp ≤ β_docs < 0.5pp: EXPLORE — investigate subgroup heterogeneity; report as suggestive
- IF permutation p ≥ 0.05: EXPLORE — check for residual stratification; verify within-bin balance

**Dependencies**: H-E1 (registry assembled); H-M1 (bridge interpretation informed)

**Source**: Phase 2A Section 1.3 Causal Step 2, Predictions P1 and P3

---
**H-M3: Differential Benchmark Sensitivity**

**Statement**: Under the same Registry and regression framework, if documentation features predict benchmark performance, then the documentation coefficient (β_docs) is significantly larger for knowledge-recall benchmarks (MMLU, ARC) than for reasoning benchmarks (HellaSwag, WinoGrande), because knowledge-recall performance is more sensitive to training data quality Q — knowledge is encoded in training data, while structural reasoning ability is less dependent on data purity.

**Rationale**: This differential sensitivity test is the key mechanistic prediction that distinguishes the Q-mechanism interpretation from generic organizational competence. If documentation effects are uniformly distributed across benchmark types, the Q-interpretation is weakened. A concentrated knowledge-recall effect would provide evidence consistent with the Subramanyam et al. framework where Q primarily affects knowledge encoding, not reasoning structure.

**Variables**:
- Independent: doc_score (same as H-M2)
- Dependent: β_docs coefficient per benchmark type (MMLU, ARC, HellaSwag, WinoGrande, TruthfulQA)
- Controlled: Same as H-M2 (log(N), log(D), arch_FE)

**Verification Protocol**:
1. Fit separate OLS regressions for each of 5 benchmarks (MMLU, ARC, HellaSwag, WinoGrande, TruthfulQA) with identical controls.
2. Extract β_docs and 95% CI for each benchmark regression.
3. Test cross-benchmark coefficient equality: F-test on stacked/SUR regression with cross-equation constraints.
4. Compute ratio β_docs(MMLU) / β_docs(HellaSwag) and β_docs(ARC) / β_docs(WinoGrande).
5. Run verbosity placebo: replace doc_score with model card word count; verify ΔR² < 50% of documentation block ΔR².

**Success Criteria**:
- Primary: β_docs(MMLU) > β_docs(HellaSwag) AND β_docs(ARC) > β_docs(WinoGrande) with p < 0.05 (F-test of coefficient difference)
- Secondary: Verbosity placebo ΔR² < 50% of documentation block ΔR² on MMLU

**Failure Response**:
- IF β_docs uniform across benchmarks: EXPLORE — reframe as documentation predicts overall quality, not specifically knowledge-recall; weaken but don't abandon main claim
- IF reasoning > knowledge: PIVOT — revisit mechanism; organizational competence interpretation strengthened

**Dependencies**: H-E1 (registry), H-M2 (main effect must exist to test heterogeneity)

**Source**: Phase 2A Section 1.3 Causal Step 3, Prediction P2

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 (MUST_WORK) → H-M1 (MUST_WORK) → H-M2 (MUST_WORK) → H-M3 (MUST_WORK)
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | n ≥ 200 with full feature set | STOP — reassess data strategy |
| H-M1 | MUST_WORK | Bridge coefficient β > 0 | Reframe interpretation; still proceed |
| H-M2 | MUST_WORK | β_docs ≥ 0.5pp, perm. p < 0.01 | ABANDON — null result is informative |
| H-M3 | MUST_WORK | β(MMLU) > β(HellaSwag), p < 0.05 | EXPLORE — weaken differential claim |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanism Chain | H-M1, H-M2, H-M3 | 3 weeks |

**Total Duration:** 5 weeks (+ 1 week buffer for bridge validation corpus access)

---

## 4. Risk Analysis

### 4.1 Risk Register

**R1: Organizational Competence Confound** (Source: A1)
- **Description**: β_docs may reflect "good labs document AND train better models" rather than a true documentation→Q→performance effect. Labs with more resources document more carefully AND invest more in training infrastructure, hyperparameter optimization, and evaluation hygiene.
- **Severity**: High | **Likelihood**: Near-certain
- **Affected Hypotheses**: H-M2, H-M3

**R2: H-M1 Bridge Failure Invalidates Chain** (Source: A1)
- **Description**: If bridge validation fails (documentation does not predict corpus hygiene artifacts), the Q-mechanism interpretation collapses. H-M2 and H-M3 can still be run, but interpretation must switch to "organizational competence proxy" framing.
- **Severity**: High | **Likelihood**: Moderate
- **Affected Hypotheses**: H-M1, H-M2, H-M3

**R3: Missing Training Token Counts (D)** (Source: A3)
- **Description**: If >60% of leaderboard models lack accessible D (training tokens), the regression degrades to N-only controls, weakening the scale-control argument and potentially introducing omitted variable bias.
- **Severity**: High | **Likelihood**: Moderate-High
- **Affected Hypotheses**: H-E1, H-M2, H-M3

**R4: Feature Extraction Reliability** (Source: A1 extension)
- **Description**: Binary coding of "deduplication performed" may mean different things across labs. Without second-annotator validation, systematic miscoding could attenuate (false negative) or inflate (false positive) documentation effects.
- **Severity**: Medium | **Likelihood**: Moderate
- **Affected Hypotheses**: H-M2, H-M3

**R5: Registry Recall / Selection Bias** (Source: A3)
- **Description**: Systematic omission of non-English-language model cards or small-lab entries biases toward well-resourced labs that both document better and train better — amplifying the organizational competence confound.
- **Severity**: Medium | **Likelihood**: Moderate-Low
- **Affected Hypotheses**: H-E1

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity | Likelihood |
|------|--------|---------------------|----------|------------|
| R1: Organizational competence confound | A1 | H-M2, H-M3 | High | Near-certain |
| R2: Bridge validation failure / chain invalidation | A1 | H-M1, H-M2, H-M3 | High | Moderate |
| R3: Missing training token count (D) | A3 | H-E1, H-M2, H-M3 | High | Moderate-High |
| R4: Feature extraction reliability / miscoding | A1 ext. | H-M2, H-M3 | Medium | Moderate |
| R5: Registry recall / selection bias | A3 | H-E1 | Medium | Moderate-Low |

### 4.3 Mitigation Strategies

**R1 Mitigation — Organizational Competence Confound:**
1. **Prevention**: Pre-register interpretive framing before data collection — commit to interpreting β_docs as "documentation as organizational quality proxy" if lab fixed effects absorb signal.
2. **Detection**: Run specification with lab fixed effects as robustness check; if β_docs drops to zero, confound confirmed.
3. **Response**: EXPLORE — report conditional interpretation; prominently acknowledge in limitations; reframe contribution as "documentation as predictive feature for quality, agnostic to mechanism."

**R2 Mitigation — Bridge Validation Failure:**
1. **Prevention**: Pre-define H-M1 pass threshold (R² ≥ 0.40, p < 0.001) before data collection; register at OSF.
2. **Detection**: Bridge validation is H-M1 — failure is detectable by design.
3. **Response**: EXPLORE — switch to organizational competence framing; proceed to H-M2/H-M3 with modified interpretation; document as conditional finding.

**R3 Mitigation — Missing D:**
1. **Prevention**: Conduct pilot missing-data audit on 100 model cards before committing to design; go/no-go threshold: D-missingness < 60%.
2. **Detection**: Track D-recovery rate during data collection phase; alert if <40% recovered.
3. **Response**: PIVOT — apply multiple imputation (D ~ N, architecture family) as primary; N-only sensitivity analysis as secondary; restrict to base models with explicit scale disclosures if missingness > 60%.

**R4 Mitigation — Feature Extraction Reliability:**
1. **Prevention**: Pre-define keyword taxonomy for all four binary features before extraction; publish taxonomy in supplementary materials.
2. **Detection**: Double-code a 10% random sample (50+ models); compute Cohen's κ; gate: κ ≥ 0.70 required before H-M2/H-M3.
3. **Response**: PIVOT — refine taxonomy and re-code if κ < 0.70; use only features with κ ≥ 0.70 in primary analysis.

**R5 Mitigation — Registry Recall Bias:**
1. **Prevention**: Merge sources (HuggingFace Hub, Papers With Code, leaderboard API dump); document sampling frame.
2. **Detection**: Coverage audit: cross-reference registry against known major model releases; report recall fraction.
3. **Response**: SCOPE — if bias is severe, restrict to pre-identified model families (LLaMA, Falcon, Mistral, Pythia) with full coverage; note as scope limitation.

### 4.4 Risk Summary

| ID | Risk | Source | Severity | Likelihood | Affected | Mitigation |
|----|------|--------|----------|------------|----------|------------|
| R1 | Org. competence confound | A1 | High | Near-certain | H-M2, H-M3 | Pre-register interpretive framing; lab FE robustness check |
| R2 | Bridge failure / chain invalidation | A1 | High | Moderate | H-M1-3 | Pre-define H-M1 pass threshold; conditional interpretation |
| R3 | Missing training tokens (D) | A3 | High | Moderate-High | H-E1, H-M2, H-M3 | Pilot D-audit before design commit; imputation; N-only fallback |
| R4 | Feature extraction miscoding | A1 ext. | Medium | Moderate | H-M2, H-M3 | Double-code 10% sample; κ ≥ 0.70 gate |
| R5 | Registry recall/selection bias | A3 | Medium | Moderate-Low | H-E1 | Multi-source merge; coverage audit |

**Critical Risks:** 0 | **High Risks:** 3 | **Medium Risks:** 2 | **Low Risks:** 0

**Pre-Registration Gates Required:**
1. Pilot D-missingness audit → go/no-go threshold < 60%
2. H-M1 bridge pass threshold pre-registered (R² ≥ 0.40)
3. Feature extraction κ ≥ 0.70 gate (10% double-coded sample)
4. Interpretive framing for organizational confound pre-committed

---

## 5. Dependency Graph & Timeline

### 5.1 DAG Visualization

```
═══════════════════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) — H-DocCuration-v1 (4 Hypotheses)
═══════════════════════════════════════════════════════════════════════

[PHASE 1 — Foundation / Registry Construction]

    ┌─────────────────────────────────────────────────────┐
    │  H-E1: Registry Construction Feasibility            │
    │  Type: EXISTENCE  Gate: MUST_WORK                   │
    │  Prerequisites: None                                │
    │  Test: n_analyzable ≥ 200 models with full feature  │
    └─────────────────────────────────────────────────────┘
                          │
                          │ ← H-E1 MUST PASS (Gate 1)
                          ▼

[PHASE 2 — Mechanism Chain (Bridge → Primary → Heterogeneity)]

    ┌─────────────────────────────────────────────────────┐
    │  H-M1: Documentation–Implementation Bridge          │
    │  Type: MECHANISM  Gate: MUST_WORK                   │
    │  Prerequisites: H-E1                               │
    │  Test: Documentation predicts corpus hygiene        │
    │        (13-gram dedup rate, reference model xent)   │
    └─────────────────────────────────────────────────────┘
                          │
                          │ ← H-M1 MUST PASS or reframe
                          ▼
    ┌─────────────────────────────────────────────────────┐
    │  H-M2: Documentation Predicts Scale-Adjusted MMLU   │
    │  Type: MECHANISM  Gate: MUST_WORK                   │
    │  Prerequisites: H-M1                               │
    │  Test: β_docs ≥ 0.5pp, permutation p < 0.01        │
    └─────────────────────────────────────────────────────┘
                          │
                          │ ← H-M2 MUST PASS (main claim)
                          ▼
    ┌─────────────────────────────────────────────────────┐
    │  H-M3: Differential Benchmark Sensitivity           │
    │  Type: MECHANISM  Gate: MUST_WORK                   │
    │  Prerequisites: H-M2                               │
    │  Test: β_docs(MMLU) > β_docs(HellaSwag) p < 0.05   │
    └─────────────────────────────────────────────────────┘
                          │
                          ▼
                    [ COMPLETE ]
                 → Phase 2C → Phase 3 → Phase 4

═══════════════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Depth: 4 levels | Parallelization: None (sequential)
═══════════════════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type | Phase | If Fail |
|-------|-----------|---------------|-----------|-------|---------|
| 0 | H-E1: Registry Construction | None | MUST_WORK | Phase 1 | STOP — reassess data availability; expand to v2 or relax inclusion |
| 1 | H-M1: Bridge Validation | H-E1 | MUST_WORK | Phase 2 | Reframe to organizational competence proxy; proceed with modified interpretation |
| 2 | H-M2: Primary Regression | H-M1 | MUST_WORK | Phase 2 | ABANDON main claim; report upper bound; null result is publishable |
| 3 | H-M3: Benchmark Heterogeneity | H-M2 | MUST_WORK | Phase 2 | EXPLORE — uniform effect still informative; weaken differential claim |

**Gate Conditions:**
- Gate 1 (H-E1): n_analyzable ≥ 200 AND doc_score variance non-trivial → PROCEED to H-M1
- Gate 2 (H-M1): Bridge coefficient β > 0 for dedup_documented → PROCEED to H-M2 with Q-mechanism framing; if fails → PROCEED with organizational competence framing
- Gate 3 (H-M2): β_docs ≥ 0.5pp AND permutation p < 0.01 → PROCEED to H-M3; else STOP
- Gate 4 (H-M3): β_docs(MMLU) > β_docs(HellaSwag) p < 0.05 → Full verification COMPLETE

### 5.3 Gantt Timeline

```
═════════════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE — H-DocCuration-v1 (4 Hypotheses, 5 Weeks)
═════════════════════════════════════════════════════════════════════════════════
Phase / Hypothesis     │ W1      │ W2      │ W3-4    │ W5      │ W6+
───────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────
PHASE 1: Foundation
  H-E1 Registry Build  │ ████████│ ████████│         │         │
  D-audit pilot        │ ████████│         │         │         │
  Feature taxonomy def │         │ ████████│         │         │
  [◆ GATE 1: n≥200?]   │         │         ◆         │         │
───────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────
PHASE 2: Mechanism Chain
  H-M1 Bridge Valid.   │         │         │ ████████│         │
    Corpus hygiene      │         │         │ ████████│         │
  [◆ GATE 2: κ≥0.70?]  │         │         │         ◆         │
  H-M2 Primary Regress │         │         │         │ ████████│
    OLS + permut. tests │         │         │         │ ████████│
  [◆ GATE 3: ≥0.5pp?]  │         │         │         │         ◆
  H-M3 Heterogeneity   │         │         │         │         │ ████████
    Cross-bench regress │         │         │         │         │ ████████
  [◆ GATE 4: MMLU>HSwg]│         │         │         │         │        ◆
───────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────
COMPLETE → Phase 2C    │         │         │         │         │   ✓
═════════════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work period  ◆ = Gate decision point
Total Duration: 5 weeks (+ buffer for pilot audit)
═════════════════════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3

**Total Duration:** 5 weeks (2 + 1 + 1 + 1)
- H-E1: Weeks 1-2 (2 weeks — data collection and registry construction)
- H-M1: Weeks 3-4 (2 weeks — bridge validation with corpus hygiene metrics)
- H-M2: Week 5 (1 week — primary OLS regression + permutation tests)
- H-M3: Week 6 (1 week — cross-benchmark heterogeneity analysis)

**Slack Available:** 0 weeks (fully sequential — each phase requires previous gate to pass)

**Bottleneck:** H-E1 is the critical bottleneck — if model card scraping or D-recovery is slower than expected, all downstream phases shift proportionally.

**Early Warning:** Conduct pilot D-missingness audit in Week 1 (first 100 model cards) to determine whether N-only fallback is needed before committing to full design.

### 5.5 Resource Summary

**Total Hypotheses:** 4 (H-E1, H-M1, H-M2, H-M3)
- Existence: 1 (H-E1)
- Mechanism: 3 (H-M1, H-M2, H-M3)
- Condition: 0 (not required)

**Compute Requirements:** CPU only (no GPU needed — OLS regression on tabular data)
- Data processing: Python/pandas for model card scraping and feature extraction
- Statistics: statsmodels OLS, scipy permutation tests
- Storage: ~100MB for leaderboard snapshot + model cards

**Data Requirements:**
- Open LLM Leaderboard v1 static snapshot (~3000 entries)
- HuggingFace model cards (accessible via Hub API)
- Subset of pretraining corpora for bridge validation (Pythia/The Pile, OLMo/Dolma, LLaMA-1 accessible portions)

**Verification Phases:** 2 (Foundation + Mechanism Chain)
**Total Duration:** 5 weeks
**Execution Mode:** Sequential (all phases depend on previous gate)

### 5.6 Execution Order

1. **Week 1-2 — H-E1 (Foundation)**: Download Open LLM Leaderboard v1 snapshot; scrape model cards; extract 4 binary features; filter by inclusion criteria; assess n_analyzable. Pilot D-missingness audit on 100 cards in Week 1. Double-code 10% sample for κ validation.
2. **Gate 1 (End Week 2)**: Confirm n_analyzable ≥ 200 AND κ ≥ 0.70 → PROCEED or PIVOT.
3. **Weeks 3-4 — H-M1 (Bridge Validation)**: Identify models with accessible corpora; compute 13-gram duplication rates and cross-entropy vs. reference model; regress hygiene metrics on documentation features.
4. **Gate 2 (End Week 4)**: Evaluate bridge coefficient direction → determine interpretation pathway (Q-mechanism vs. org. competence).
5. **Week 5 — H-M2 (Primary Regression)**: Fit OLS baseline models; fit full model with documentation block; run permutation tests (1,000 shuffles); compute partial R²; run leave-one-family-out stability.
6. **Gate 3 (End Week 5)**: Confirm β_docs ≥ 0.5pp AND permutation p < 0.01 → PROCEED to H-M3 or ABANDON.
7. **Week 6 — H-M3 (Heterogeneity)**: Fit per-benchmark regressions; test cross-benchmark coefficient equality; run verbosity placebo comparison.
8. **Gate 4 (End Week 6)**: Confirm β_docs(MMLU) > β_docs(HellaSwag) → COMPLETE; proceed to Phase 2C experiment design.

---

## 6. Dialectical Analysis

### 6.1 Full Analysis

ClearThought Structured Argumentation (mcp__clearThought__structuredargumentation) completed 3-stage dialectical evaluation. Summary:

**Thesis Confidence:** 0.62 (before verification) | **Antithesis Confidence:** 0.55 | **Synthesis Confidence:** 0.78

The dialectic between documentation-as-quality-proxy (thesis) and organizational competence confound (antithesis) is resolvable through a four-gate sequential verification plan. Each antithesis threat is converted into a falsifiable empirical gate. Pre-registered thresholds prevent post-hoc manipulation. Three defined epistemic outcomes provide scientific honesty about the range of possible conclusions.

### 6.2 Thesis Statement

**Core Claim:** Documented pretraining data curation practices (4 binary indicators: deduplication, perplexity filtering, domain composition, decontamination) in open-weight LLM model cards predict ≥0.5pp higher benchmark performance on knowledge-recall benchmarks (MMLU, ARC) after controlling for log(N), log(D), and architecture family FE.

**Supporting Evidence:**
1. L(N,D,Q) scaling law (Subramanyam et al. 2025): γ_CLM ≈ 0.39 — documentation proxies for Q, higher Q reduces benchmark loss sublinearly but measurably
2. Documentation-implementation correlation (Djuhera et al. 2025): systematic quality annotation shows documentation presence correlates with actual dataset properties
3. Benchmark type differentiation (Myntti et al. 2025; Zhu et al. 2024): knowledge-recall benchmarks more sensitive to data quality; contamination inflates MMLU more than reasoning tasks

**Strengths:** Theoretically grounded in scaling law framework; empirically testable with public data; novel gap confirmed by Phase 1; standardized evaluation corpus; pre-registered design prevents HARKing.

**Expected Outcomes:**
- P1: ≥0.5pp MMLU improvement, permutation p < 0.01 within bins
- P2: β_docs(MMLU) > β_docs(HellaSwag) with p < 0.05
- P3: Partial R² ≥ 0.03 for documentation block on MMLU

### 6.3 Antithesis

**Null Hypothesis (H0):** β_docs = 0 — there is no significant documentation effect on MMLU or ARC after controlling for log(N), log(D), and architecture family FE.

**Counter-Arguments:**
1. **Organizational Competence Confound:** Labs that document carefully also invest more in hyperparameter optimization, evaluation hygiene, and training infrastructure. β_docs may reflect "good labs" rather than documentation→Q mechanism. Cannot be eliminated with observational data alone.
2. **Documentation Theater:** Model cards may be aspirational descriptions rather than accurate accounts of implemented practices (Liang et al. 2022 model card adequacy findings). Binary feature extraction may code "we intended to deduplicate" as equivalent to "we verified 23% duplication reduction."
3. **Sub-detectable Effect Size:** If the true effect is <0.2pp (below practical significance threshold), the study will be underpowered at n=500-2000. Sublinear Q sensitivity (γ ≈ 0.39) and the small Q shift from a 4-feature binary sum may not produce detectable effects.
4. **Architecture FE Signal Absorption:** If documentation patterns correlate within architecture families (e.g., all LLaMA-derived models document similarly), family fixed effects may absorb documentation signal, leaving β_docs artifactually near zero.

**Potential Failure Points:**
- R3: Missing D data reduces effective N below detectable threshold
- R1: Org. competence confound makes β_docs uninterpretable as Q-mechanism effect
- R2: Bridge validation failure eliminates Q-mechanism framing

**Conditions Supporting H0:**
- Adjusted mean difference < 0.2pp (practical negligibility) — accept null
- Permutation p ≥ 0.05 within bins — residual stratification detected
- Documentation block ΔR² < 0.01 (below practical significance)

### 6.4 Synthesis

The hypothesis H-DocCuration-v1 presents a theoretically motivated and empirically testable claim that documentation discipline proxies for data quality, producing detectable knowledge-recall benchmark improvements. However, the null hypothesis raises valid concerns — particularly the organizational competence confound, which cannot be eliminated with observational data alone, and the possibility of documentation theater undermining the proxy assumption.

**Resolution Path:** The verification plan addresses this dialectic through a four-gate sequential design where each antithesis threat is converted into a falsifiable gate:

| Gate | Antithesis Threat Addressed |
|------|----------------------------|
| H-E1 (n ≥ 200, κ ≥ 0.70) | Proxy invalidity — documentation must be extractable and reliable |
| H-M1 (bridge β > 0) | Documentation theater — bridge tests if documentation predicts hygiene artifacts |
| H-M2 (β_docs ≥ 0.5pp, perm. p < 0.01) | Effect size insufficiency — threshold pre-registered |
| H-M3 (MMLU > HellaSwag, p < 0.05) | FE absorption + Q-mechanism specificity |

**Three Defined Epistemic Outcomes:**
1. **SUPPORTED:** H-E1 ∧ H-M1 ∧ H-M2 ∧ H-M3 all pass → Thesis validated with Q-mechanism framing
2. **SUPPORTED-CONDITIONALLY:** H-E1 ∧ H-M1 pass; H-M2 or H-M3 fail with documented boundaries → Organizational competence framing; documentation as predictive feature
3. **REFUTED:** H-E1 fails OR H-M2 fails (β_docs < 0.2pp) → Null result reported; upper bound published

**Key Insight from Synthesis:** Even a null result is scientifically informative — it establishes an empirical upper bound on the documentation-performance signal and validates (or challenges) current model card adequacy standards. The study is publishable under all three outcome scenarios.

### 6.5 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence (registry) | n ≥ 200 with adequate doc variation | Insufficient coverage; feature extraction unreliable | H-E1 gate + κ validation |
| Bridge (A1) | Documentation reflects implementation | Documentation theater; aspirational descriptions | H-M1 bridge test; conditional interpretation |
| Primary mechanism | β_docs ≥ 0.5pp, org confound tolerable | Confound dominates; β_docs reflects lab quality not Q | Pre-registered org. framing; lab FE robustness check |
| Differential sensitivity | MMLU > HellaSwag (Q theory) | Uniform effect → org. competence uniform too | H-M3 cross-benchmark test; verbosity placebo |
| Causality | Q-mechanism plausible via bridge | Observational; cannot claim causality | Explicitly framed as correlational; limitations stated |

**Overall Robustness Score:** Medium-High (methodologically disciplined; confound acknowledged but unresolvable; outcomes pre-specified to prevent HARKing)

**Confidence in Verification Plan:** 0.72 (carried from Phase 2A)

**Key Robustness Feature:** The pre-registered conditional interpretation pathways mean that bridge validation failure does not invalidate the study — it redirects interpretation. This is the primary mechanism for maintaining scientific integrity given the irreducible organizational competence confound.

---

## 7. Executive Summary & Appendices

### 7.1 Executive Summary

**Main Hypothesis:** Binary curation documentation features in model cards predict ≥0.5pp higher MMLU/ARC performance after scale + architecture controls
- ID: H-DocCuration-v1 | Confidence: 0.72 | Mode: Incremental (40% scope reduction from BUILD_ON facts)

**Verification Structure:**
- Sub-Hypotheses: 4 (H-E1: registry, H-M1: bridge, H-M2: primary regression, H-M3: heterogeneity)
- Phases: 2 phases over 5 weeks | Gates: 4 decision points
- Compute: CPU-only (OLS on tabular data — no GPU required)

**Risk Assessment:** Medium-High
- Primary concerns: Organizational competence confound (irreducible); Missing training token data (D)
- Mitigations: Pre-registered interpretive framing; pilot D-audit; κ ≥ 0.70 gate

**Immediate Action:** Begin Phase 1 — download Open LLM Leaderboard v1 snapshot; scrape model cards; pilot D-audit on first 100 entries

### 7.2 Final Summary

**Key Achievements:**
- 4 sub-hypotheses across 2 verification phases; H0 (β_docs = 0) addressed via pre-registered gates
- 3 defined epistemic outcomes prevent post-hoc rationalization
- 5 risks identified with mitigation strategies and 4 pre-registration gates required

**Verification Execution Order:**

**Phase 1: Foundation** (Weeks 1-2)
- H-E1: Assemble LLM Documentation-Benchmark Registry; n ≥ 200; κ ≥ 0.70
- Gate 1: MUST PASS → proceed to Phase 2

**Phase 2: Mechanism Chain** (Weeks 3-6)
- H-M1: Bridge validation — documentation predicts corpus hygiene artifacts
- H-M2: Primary OLS regression — β_docs ≥ 0.5pp, perm. p < 0.01
- H-M3: Cross-benchmark heterogeneity — β_docs(MMLU) > β_docs(HellaSwag)
- Gates 2-4: Sequential — MUST PASS or reframe

**Critical Decision Points:**
1. Gate 1 (n ≥ 200, κ ≥ 0.70): FAIL → STOP, reassess data availability
2. Gate 2 (H-M1 bridge): FAIL → reframe to org. competence; proceed with conditional framing
3. Gate 3 (β_docs ≥ 0.5pp): FAIL (< 0.2pp) → ABANDON; report null result
4. Gate 4 (MMLU > HellaSwag): FAIL → EXPLORE benchmark uniformity; weaken differential claim

**Open Questions:**
- What fraction of Open LLM Leaderboard v1 models have sufficient model card documentation?
- Is training token count (D) recoverable for enough models (pilot audit required)?
- What is the empirically observed prevalence of D disclosure in target sample?
- Is bridge validation feasible with available accessible corpora (Pythia/OLMo/LLaMA)?

**Recommendations:**
1. **Immediate:** Conduct pilot D-missingness audit (100 cards) before committing to design
2. **Pre-registration:** Register keyword taxonomy, H-M1 threshold (R² ≥ 0.40), κ threshold at OSF before data collection
3. **Failure management:** All three epistemic outcomes (SUPPORTED, SUPPORTED-CONDITIONALLY, REFUTED) are publishable — proceed confidently

### 7.3 Conclusions

The Phase 2B verification plan for H-DocCuration-v1 is complete. The plan decomposes the main hypothesis into 4 sequential sub-hypotheses with clear gate conditions, risk mitigations, and pre-registered interpretive pathways. The study is methodologically disciplined — the organizational competence confound is acknowledged as irreducible, but pre-registered conditional interpretation ensures scientific honesty regardless of outcome. The three epistemic outcomes (SUPPORTED, SUPPORTED-CONDITIONALLY, REFUTED) provide complete coverage of possible results, all of which are publishable contributions to the DATA-FM workshop topic.

### 7.4 Appendices

### A. Phase 2A Reference
- **Source:** `docs/youra_research/20260317_data_problems/03_refinement.yaml`
- **Hypothesis ID:** H-DocCuration-v1 | Schema: v10.0.0 | Status: VALIDATED
- **Established Facts (BUILD_ON, 4 claims):** Thrush et al. 2024, Subramanyam et al. 2025, Myntti et al. 2025, Zhu et al. 2024
- **PROVE_NEW (2 claims):** Documentation→performance signal; differential benchmark sensitivity

### B. MCP Tool Usage Summary
- **Total MCP calls:** 4 calls (H-E1-verification ×2 stages, H-M-integrated ×2 stages, collaborative reasoning ×1, structured argumentation ×3 stages)
- **Tools:** mcp__clearThought__scientificmethod (Step 3), mcp__clearThought__collaborativereasoning (Step 5), mcp__clearThought__structuredargumentation (Step 8)
- **Archon MCP:** Unavailable (3 timeout retries) — will retry in Step 10

### C. Scope Reduction Summary
- Total Phase 2A claims: 6 | BUILD_ON: 4 (40% reduction) | PROVE_NEW: 2
- Transfer Validation: Not required (no cross-domain transfer)
- Condition Hypotheses: Not required (no testable scope boundaries detected)

---

## 8. Finalization Status

**verification_state.yaml:** CREATED — `docs/youra_research/20260317_data_problems/verification_state.yaml` (schema v3.5, 4 sub-hypotheses)
**Pipeline Tasks Updated:** ✅ Phase 2B → done | Phase 2C → doing (project: ab7430cf-fad5-4150-a3ff-00ae07f02be5)
**Hypothesis Tasks Created:** ✅ 4 tasks created in Archon
- H-E1: `40e94362-d05c-4f8f-812f-a80fdd6f5ad8`
- H-M1: `fdf7edf6-8f07-4f41-a99c-04ae3989f82d`
- H-M2: `c781e64a-eca6-4407-ac8b-1a473e7d412c`
- H-M3: `6c82885c-0130-4313-8f63-e9187a09b489`

---

*Generated by YouRA Phase 2B (v7.7.0) | 2026-03-17*
