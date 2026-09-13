---
hypothesis_id: "H-ExecFilteredSFT-v1"
hypothesis_title: "Exec-FilteredSFT: Execution-Filtered SFT Data from Raw Corpus Improves Code LLM Performance at Equal Token Budget"
research_mode: "incremental"
confidence_level: 0.75
total_hypothesis_count: 6
causal_chain_count: 4
condition_hypothesis_count: 1
phase: "Phase 2B"
status: "complete"
date: "2026-08-04"
completedAt: "2026-08-04T17:27:00Z"
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
---

# Verification Plan: Exec-FilteredSFT: Execution-Filtered SFT Data from Raw Corpus Improves Code LLM Performance at Equal Token Budget

**Date:** 2026-08-04
**Hypothesis ID:** H-ExecFilteredSFT-v1
**Confidence:** 0.75
**Total Hypotheses:** 6 (H-E1, H-M1, H-M2, H-M3, H-M4, H-C1)

---

## 0. Established Facts & Scope Reduction

### 0.1 Established Facts Registry (BUILD_ON — DO NOT RE-VERIFY)

| Claim | Status | Evidence |
|-------|--------|----------|
| Quality-filtered SFT outperforms equal-token-budget unfiltered SFT | BUILD_ON | phi-1 [Gunasekar et al., 2023]: 1.3B quality tokens → 50.6% HumanEval |
| Execution-selected SFT samples improve HumanEval pass@1 | BUILD_ON | EffiCoder [Zeng et al., 2024]: 44.8% → 57.7% pass@1 (+13pp) |
| HumanEval and MBPP are valid automated benchmarks for code generation | BUILD_ON | Chen et al. 2021 (HumanEval); Austin et al. 2021 (MBPP) |
| The Stack Python is publicly available for SFT corpus construction | BUILD_ON | StarCoder [Li et al., 2023]; bigcode/the-stack-dedup on HuggingFace |

### 0.2 PROVE_NEW Claims (Phase 2B Focus)

| Claim | Status | Phase 2B Action |
|-------|--------|-----------------|
| No controlled SFT comparison of unfiltered vs compile-only vs compile+test at equal token budget | PROVE_NEW | Design three-condition ablation experiment → H-E1 |
| Execution-filtered SFT from raw corpus outperforms unfiltered SFT at equal token budget | PROVE_NEW | Test causal chain steps → H-M1 through H-M4 |

**Scope Reduction: 33%** — 4 of 6 total claims are BUILD_ON (pre-validated, skip re-verification).

**Phase 2B-4 Instructions from Phase 2A:** BUILD_ON claims (quality filtering works, HumanEval/MBPP validity, The Stack availability) are established — Phase 2B should NOT re-verify these. Focus verification effort on PROVE_NEW claims: (1) that execution filtering of raw SFT corpus at equal token budget produces measurable improvement, and (2) that compile+test filtering provides additional gain over compile-only.

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under equal token budget from The Stack Python corpus (SFT stage, Python language, Qwen2.5-Coder-1.5B primary and 7B secondary), if training data is execution-filtered (compile-only via `compile()` AST check, or doctest-passing via `compile()` + `doctest` module execution), then HumanEval pass@1 and MBPP pass@1 improve over unfiltered-subset SFT of equal token count, because execution filtering retains syntactically and functionally consistent training examples, reducing exposure to malformed patterns and improving distributional alignment with benchmark-style correct code.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in HumanEval pass@1 or MBPP pass@1 between SFT on execution-filtered data and SFT on unfiltered data of equal token count from The Stack Python, when controlling for base model, training hyperparameters, and token budget.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | The Stack Python (bigcode/the-stack-dedup) (standard) | The Stack Python is the canonical open-source Python corpus for code LLM SFT studies (StarCoder, cristinaimprota ICPC 2025); publicly available; sufficiently large for token-budget matching across all three conditions |
| **Model** | Qwen2.5-Coder-1.5B (primary), Qwen2.5-Coder-7B (secondary) | Same model family enables clean cross-size comparison; Qwen2.5-Coder has demonstrated SFT sensitivity to data quality; EffiCoder used 7B variant confirming +13pp achievable |

**Dataset Details:**
- Source: HuggingFace: bigcode/the-stack-dedup, Python language subset
- Path: HuggingFace Hub: bigcode/the-stack-dedup

**Model Details:**
- Type: Decoder-only code LLM
- Source: HuggingFace: Qwen/Qwen2.5-Coder-1.5B, Qwen/Qwen2.5-Coder-7B

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| phi-1 (GPT-4-curated SFT at equal budget) | 50.6% HumanEval on 1.3B model | GPT-4-curated Python subset |
| StarCoder (heuristic-filtered The Stack) | 40% HumanEval on 15.5B model | The Stack with heuristic filters |
| EffiCoder (execution-selected instruction-tuning) | 57.7% HumanEval on Qwen2.5-Coder-7B (+13pp) | Instruction-tuning dataset, execution-selected at inference |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | The Stack Python (deduplicated) contains sufficient doctest-bearing files to yield N training tokens at compile+test condition (≥3% prevalence for 500M token budget) | Python ecosystem patterns: NumPy, SciPy, standard library have high doctest density; estimated 5-10% of functions | Compile+test condition cannot be run; fall back to compile-only as primary condition (Gap 1 RQ1/RQ2 still answerable) |
| A2 | Execution filtering quality signal (compile/doctest passing) correlates with training example quality relevant to HumanEval/MBPP task types | EffiCoder's execution selection → HumanEval gain; OpenCodeInstruct execution feedback → cross-benchmark improvement | P1 fails: execution-filtered SFT shows no HumanEval/MBPP improvement; study finds null result (publishable but negative) |
| A3 | Qwen2.5-Coder-1.5B is sensitive to SFT data quality at token budgets being tested (500M-1B tokens) | phi-1 showed 1.3B model highly sensitive to quality at similar token budgets; Qwen2.5-Coder-1.5B demonstrated SFT sensitivity in OpenCodeInstruct experiments | Model too large/small for token budget to show quality effects; repeat with different model size or budget |
| A4 | The P3 stratum check is valid: compile-only-doctest-subset performance ≈ compile-only-full-stack performance (within 1pp) if no stratum bias | If doctest-bearing functions are representative of The Stack Python distribution, stratum check should pass | Doctest stratum is systematically different from general Stack Python (library code bias); P1 result attributed to stratum quality, not execution filtering — reframing needed |
| A5 | `doctest` execution within main process does not cause stability issues at corpus-scan scale | `doctest` module has timeout controls; malformed doctests typically fail quickly; opc_data_filtering has similar in-process execution experience | Doctest scanning pipeline crashes or is too slow; fall back to compile-only condition as primary |

### 1.6 Research Gap & Novelty

**Gap:** No controlled SFT comparison of unfiltered vs compile-only vs compile+test at equal token budget from raw corpus data exists.

**Novelty:** First controlled comparison of execution-filtered vs. unfiltered raw corpus SFT at equal token budget with compile-only vs. doctest-passing ablation on HumanEval + MBPP. Three-condition ablation (unfiltered / compile-only / doctest-passing) from a SINGLE corpus at EQUAL token budget, with P3 stratum confound check — distinguishes execution quality signal from corpus selection bias.

**Differentiation:**
- vs phi-1: phi-1 used GPT-4 as quality oracle (opaque, expensive, model-dependent); this study uses objective execution gates (compile/doctest — model-agnostic, reproducible)
- vs EffiCoder: EffiCoder filters instruction-tuning data at inference time; this study filters raw corpus data at training data preparation time — different intervention point
- vs StarCoder: Heuristic filters do not test execution correctness; this study uses execution gates as quality criterion
- vs OpenCodeInstruct: OpenCodeInstruct is instruction-tuning format; this study uses raw Stack Python

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
| H-C1 | CONDITION | SHOULD_WORK | H-M4 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Existence of Execution Filtering Signal in Raw Corpus SFT**

**Statement:** Under equal token budget from The Stack Python (SFT stage, Qwen2.5-Coder-1.5B), if training data is filtered by execution gate (compile-only or doctest-passing), then HumanEval pass@1 and MBPP pass@1 improve over unfiltered-subset SFT of equal token count, because execution filtering retains syntactically and functionally consistent examples.

**Rationale:** This is the foundational existence check — does execution filtering produce any measurable improvement at all? It validates PROVE_NEW claim (2) and is required before investigating mechanism. Without this, the entire causal chain collapses. This hypothesis combines P1 (primary prediction: compile+test vs unfiltered ≥2pp) and P2 (ordering check).

**Variables:**
- Independent: Execution filter condition (unfiltered / compile-only / doctest-passing), categorical 3-level
- Dependent: HumanEval pass@1 (primary, 164 problems), MBPP pass@1 (secondary, standard split)
- Controlled: Token budget N (500M-1B tokens), base model checkpoint (Qwen2.5-Coder-1.5B), training hyperparameters, data source (The Stack Python), evaluation harness (lm-evaluation-harness)

**Verification Protocol:**
1. Run 10k-file pilot scan of The Stack Python to empirically verify doctest prevalence ≥3%; abort compile+test if <3%
2. Apply compile() gate to The Stack Python; apply doctest extraction + execution to compile-only pool; subsample each to N tokens (fixed random seed)
3. SFT Qwen2.5-Coder-1.5B on 4 conditions: unfiltered, compile-only, doctest-passing, compile-only-doctest-subset (P3 control)
4. Evaluate all checkpoints on HumanEval pass@1 and MBPP pass@1 via lm-evaluation-harness (identical generation parameters)
5. Run paired bootstrap resampling (n=1000) on P1 primary comparison; check P2 ordering; check P3 stratum confound (|compile-only-doctest-subset − compile-only-full| ≤ 1pp)

**Success Criteria (PoC):**
- Primary: ΔHumanEval(compile+test − unfiltered) ≥ 2pp absolute AND paired bootstrap p < 0.05
- Secondary: Ordering holds: compile+test ≥ compile-only ≥ unfiltered on HumanEval pass@1
- Control: |HumanEval(compile-only-doctest-subset) − HumanEval(compile-only-full)| ≤ 1pp (P3 stratum check)

**Failure Response:**
- IF P1 fails (Δ < 2pp): PIVOT — publish as null result; investigate whether model size or token budget is limiting factor
- IF P3 fails (stratum bias > 1pp): SCOPE — reframe results as stratum quality effect, not execution gate effect

**Dependencies:** None (foundation hypothesis)

**Source:** Phase 2A SH1, Predictions P1/P2/P3, Established Facts PROVE_NEW claims

---

**H-M1: Execution Filtering Selects Syntactically/Functionally Valid Programs**

**Statement:** Under application of compile() and doctest gates to The Stack Python corpus, if the execution filter condition is applied, then the retained program pool has significantly higher syntactic validity and functional correctness rates than an unfiltered random subsample, because compile() rejects programs with syntax errors and doctest execution rejects programs with functional test failures.

**Rationale:** This first mechanism step establishes that the filter gates actually work as intended — they select programs with higher quality. Without this being true, the downstream quality improvement in H-M2 through H-M4 has no foundation. This is a data characterization check that verifies the filtering mechanism itself.

**Variables:**
- Independent: Execution filter condition (unfiltered / compile-only / doctest-passing)
- Dependent: Compile success rate (% of retained samples that pass compile()), doctest pass rate (% passing doctest execution), spot-check error analysis on filtered vs. unfiltered samples
- Controlled: The Stack Python version, Python version for compile()/doctest, random subsample seed

**Verification Protocol:**
1. On a held-out 10k-file sample of The Stack Python, apply compile() gate and record retention rate and error type distribution (SyntaxError, IndentationError, etc.)
2. Apply doctest extraction to the compile-passing pool; record doctest prevalence rate and execution failure mode distribution
3. Spot-check 100 retained samples per condition for qualitative quality assessment; verify no systematic exclusion of valid programs
4. Compute retention statistics: compile-only filter retention rate, doctest filter retention rate, and compare to unfiltered random sample
5. Verify: compile-only and doctest-passing conditions retain programs with 0% compile failures; doctest-passing retains programs with 0% doctest failures

**Success Criteria (PoC):**
- Primary: Compile-only condition retains 0% SyntaxError samples; doctest-passing condition retains 0% doctest-failing samples
- Secondary: Retention rates are feasible (compile-only ≥50% of The Stack Python, doctest-passing ≥3% — matching A1 assumption)

**Failure Response:**
- IF compile() gate has false negatives (retains invalid programs): EXPLORE — investigate compile() mode parameter; add AST parse check
- IF doctest prevalence <3%: SCOPE — fall back to compile-only as primary condition (H-E1 still testable with 2 conditions)

**Dependencies:** H-E1 (must establish existence of effect before verifying mechanism)

**Source:** Phase 2A Causal Step 1, Assumption A1/A5

---

**H-M2: SFT on Filtered Corpus Reduces Exposure to Malformed Code Patterns**

**Statement:** Under equal token budget SFT of Qwen2.5-Coder-1.5B, if training is on execution-filtered data (compile-only or doctest-passing) versus unfiltered data, then the filtered-trained model shows measurably lower perplexity on held-out correct code and a learning curve that diverges earlier from the unfiltered baseline, because filtered training data reduces gradient updates from malformed patterns, resulting in cleaner gradient signal.

**Rationale:** This mechanism step tests whether the filtering effect operates through noise reduction — the second link in the causal chain. If filtered and unfiltered SFT produce identical learning curves, the quality improvement in H-E1 must be attributed to a different mechanism (distribution shift or coverage concentration), requiring mechanism disambiguation. This is an intermediate metric design step.

**Variables:**
- Independent: Execution filter condition (unfiltered / compile-only / doctest-passing)
- Dependent: Perplexity on held-out correct Python code (e.g., top-1000 HumanEval-style problems), learning curve trajectory (eval loss per checkpoint)
- Controlled: Token budget N, base model, training hyperparameters, held-out evaluation set (correct Python only)

**Verification Protocol:**
1. During H-E1 SFT training runs, log eval loss on a held-out correct-Python-only validation set at every 10% of training tokens
2. Plot learning curves (eval loss vs. tokens seen) for all three conditions; test for early divergence between filtered and unfiltered conditions
3. Compute held-out perplexity on 1000 correct Python code snippets (drawn from HumanEval reference solutions + MBPP reference solutions) for each final checkpoint
4. Test whether filtered-condition models have lower perplexity on correct code than unfiltered models (paired t-test, p < 0.05)
5. If perplexity gaps exist: attribute mechanism to noise reduction; if not: document as mechanism ambiguity and proceed to H-M3

**Success Criteria (PoC):**
- Primary: Filtered condition perplexity on held-out correct code < unfiltered condition perplexity (direction check, not magnitude)
- Secondary: Learning curves diverge within first 50% of training tokens (early noise reduction signal)

**Failure Response:**
- IF no perplexity difference: EXPLORE — mechanism is not primarily noise reduction; proceed to H-M3 (distribution shift) with additional n-gram analysis
- IF learning curves converge later: SCOPE — note as weak noise reduction effect; mechanism may be distribution shift

**Dependencies:** H-M1 (filter gates must work correctly before testing learning dynamics)

**Source:** Phase 2A Causal Step 2, key_tension (mechanism agnosticism)

---

**H-M3: Filtered SFT Improves Distributional Alignment with Benchmark-Style Code**

**Statement:** Under equal token budget SFT, if training is on execution-filtered data (compile-only or doctest-passing) versus unfiltered data, then the filtered training set has measurably higher n-gram overlap with HumanEval/MBPP test cases, because execution filtering concentrates on complete, functional programs that share stylistic and structural patterns with benchmark evaluation tasks.

**Rationale:** This mechanism step tests distribution shift as an alternative explanation for the H-E1 effect. If filtered data is simply more n-gram-similar to benchmarks (regardless of noise reduction), the improvement may be due to in-distribution shift rather than noise reduction. Distinguishing these mechanisms is important for understanding generalizability and is identified as a key tension in Phase 2A.

**Variables:**
- Independent: Execution filter condition (unfiltered / compile-only / doctest-passing)
- Dependent: Unigram/bigram/trigram overlap between training set and HumanEval/MBPP test cases (BLEU-style metric); character n-gram overlap; AST subtree overlap
- Controlled: Token budget N, n-gram computation method (NLTK or sacrebleu), evaluation set (full HumanEval 164 + MBPP standard split)

**Verification Protocol:**
1. Extract final training corpus for each condition (after subsampling to N tokens)
2. Compute n-gram overlap (unigram, bigram, trigram) between each training corpus and the full HumanEval + MBPP test prompts and reference solutions
3. Compare overlap scores across conditions: does doctest-passing corpus have higher overlap with benchmarks than unfiltered?
4. If overlap differs significantly (>5% relative): attribute mechanism to distribution shift; if not: attribute to noise reduction (H-M2)
5. Document mechanism attribution in verification plan for Phase 2B intermediate metric report

**Success Criteria (PoC):**
- Primary: Establish which mechanism (noise reduction vs. distribution shift vs. coverage concentration) is primary driver — any clear directional result counts as success
- Secondary: Overlap differences are monotone across filter conditions (doctest > compile-only > unfiltered) — consistent with filtering strictness ordering

**Failure Response:**
- IF all three mechanisms show weak signal: EXPLORE — mechanism is complex interaction; document as finding; proceed with H-M4
- IF distribution shift > noise reduction: SCOPE — reframe H-E1 improvement as in-distribution shift; note implications for out-of-distribution generalization

**Dependencies:** H-M2 (perplexity analysis needed first to separate noise reduction from distribution shift)

**Source:** Phase 2A Causal Step 3, key_tension (mechanism disambiguation)

---

**H-M4: Improved Distributional Alignment Produces Higher HumanEval/MBPP pass@1**

**Statement:** Under equal token budget SFT with Qwen2.5-Coder-1.5B, if the mechanism established in H-M1 through H-M3 operates (noise reduction, distribution shift, or coverage concentration from execution filtering), then HumanEval pass@1 improvement is consistent across both primary (HumanEval) and secondary (MBPP) benchmarks, because the mechanism operates at the level of general code quality alignment rather than being benchmark-specific.

**Rationale:** This final mechanism step validates the cross-benchmark generalization of the effect. If HumanEval improves but MBPP does not (or vice versa), the mechanism may be benchmark-specific rather than general — which would be a significant limitation. Cross-benchmark consistency is the strongest evidence that the mechanism operates through genuine code quality improvement. This tests the fourth causal link identified in Phase 2A.

**Variables:**
- Independent: Execution filter condition (unfiltered / compile-only / doctest-passing)
- Dependent: HumanEval pass@1 AND MBPP pass@1 correlation; magnitude of improvement across benchmarks
- Controlled: Same model, training run, evaluation harness; MBPP standard split (not sanitized)

**Verification Protocol:**
1. From H-E1 evaluation results, extract both HumanEval pass@1 and MBPP pass@1 for all three conditions
2. Test cross-benchmark consistency: does filtering improve MBPP as well as HumanEval? (Compute Δ for each benchmark per filter condition)
3. Compare magnitude of improvement: is HumanEval Δ ≈ MBPP Δ (general effect) or HumanEval Δ >> MBPP Δ (benchmark-specific)?
4. Compute correlation between HumanEval and MBPP improvements across conditions
5. If MBPP shows no improvement despite HumanEval improvement: flag as benchmark-specific artifact; investigate MBPP task type differences from HumanEval

**Success Criteria (PoC):**
- Primary: Both HumanEval pass@1 and MBPP pass@1 improve for doctest-passing condition vs. unfiltered (direction-consistent)
- Secondary: Magnitude correlation between benchmarks (Pearson r > 0.7 across conditions)

**Failure Response:**
- IF MBPP shows no improvement while HumanEval does: SCOPE — document as benchmark-specific effect; note HumanEval/MBPP task type difference as explanation
- IF both show no improvement: confirms H-E1 null result; PIVOT per H-E1 failure response

**Dependencies:** H-M3 (mechanism attribution needed before cross-benchmark generalization claim)

**Source:** Phase 2A Causal Step 4, Prediction P1 (cross-benchmark consistency)

---

**H-C1: Doctest Prevalence Feasibility Boundary Condition**

**Statement:** Under a scan of The Stack Python (bigcode/the-stack-dedup) Python subset, if a systematic pilot scan of 10,000 randomly sampled files is conducted, then the proportion of files containing at least one valid doctest (parseable and executable) is ≥3%, because Python ecosystem conventions (NumPy, SciPy, standard library) encourage doctest-style function documentation in library and educational code.

**Rationale:** This condition hypothesis tests the feasibility boundary condition identified in Assumption A1. If doctest prevalence is <3%, the compile+test condition cannot yield N training tokens at the 500M-1B budget, and the three-condition experiment must fall back to a two-condition design (unfiltered vs compile-only). This is the single most critical infrastructure check that must pass before committing to the full experiment design. It is explicitly listed in Phase 2B readiness (sh1_existence).

**Variables:**
- Independent: None (observational study of The Stack Python)
- Dependent: Doctest prevalence rate (% of Python files containing ≥1 valid doctest)
- Controlled: The Stack Python version (bigcode/the-stack-dedup), Python version for doctest extraction, random sampling method (stratified or random), file size filter

**Verification Protocol:**
1. Download or stream 10,000 randomly sampled Python files from bigcode/the-stack-dedup
2. Apply doctest extraction: for each file, parse all docstrings and identify doctest patterns (lines starting with `>>>`)
3. For each file with ≥1 doctest pattern, attempt doctest execution (with timeout of 5 seconds per doctest block)
4. Record: (a) proportion of files with any doctest pattern, (b) proportion that execute without failure, (c) total token count of doctest-passing files in sample
5. Extrapolate to full The Stack Python Python subset: estimate total doctest-passing token pool at scale; verify ≥3% threshold met

**Success Criteria:**
- Primary: Pilot scan shows ≥3% of sampled files contain at least one successfully executable doctest (confirming compile+test condition feasibility)
- Secondary: Estimated token pool from doctest-passing files ≥500M tokens (sufficient for N-token budget)

**Failure Response:**
- IF prevalence 1-3%: SCOPE — reduce token budget N to match available pool; compile+test condition may still be feasible at smaller N
- IF prevalence <1%: PIVOT — abandon compile+test condition entirely; fall back to two-condition design (unfiltered vs compile-only); H-E1 still testable

**Dependencies:** H-M4 (condition hypothesis checked after mechanism chain, but logically should be run FIRST in practice — see execution order note)

**Source:** Phase 2A Assumption A1, phase2b_readiness.sh1_existence

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4 → H-C1

Note: H-C1 (doctest prevalence pilot) must be run BEFORE H-E1 in practice
to determine whether compile+test condition is feasible. Logical ordering
above reflects verification dependency; practical execution order below.

PRACTICAL EXECUTION ORDER:
H-C1 (pilot scan) → H-E1 (full 3-condition experiment) → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | ΔHumanEval(compile+test − unfiltered) ≥ 2pp AND p < 0.05 | STOP — reassess hypothesis; publish null result |
| H-M1 | MUST_WORK | Compile-only retains 0% SyntaxError samples; doctest-passing retains 0% doctest-failing samples | EXPLORE — check compile() mode; add AST parse step |
| H-M2 | SHOULD_WORK | Filtered condition perplexity on correct code < unfiltered (direction check) | EXPLORE — mechanism not noise reduction; proceed to H-M3 |
| H-M3 | SHOULD_WORK | Clear directional result on n-gram overlap difference | EXPLORE — mechanism complex; document and proceed |
| H-M4 | SHOULD_WORK | Both HumanEval and MBPP improve for doctest-passing vs unfiltered | SCOPE — document as benchmark-specific if only one improves |
| H-C1 | SHOULD_WORK | Pilot scan ≥3% doctest prevalence AND ≥500M token pool | PIVOT — fall back to 2-condition design |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 0: Pilot | H-C1 (doctest prevalence scan) | Week 1 |
| Phase 1: Foundation | H-E1 (3-condition SFT + evaluation) | Week 2-3 |
| Phase 1 Gate | Gate 1 decision point | Week 3 |
| Phase 2: Mechanisms | H-M1 (filter validation) | Week 4 |
| Phase 2: Mechanisms | H-M2 (perplexity/learning curves) | Week 5 |
| Phase 2: Mechanisms | H-M3 (n-gram overlap analysis) | Week 6 |
| Phase 2: Mechanisms | H-M4 (cross-benchmark consistency) | Week 6 |
| Phase 2 Gate | Gate 2 decision point | Week 6 |
| Phase 2.5: Conditions | H-C1 formal write-up (pilot done in Week 1) | Week 7 |

**Total Duration:** 7 weeks (practical: 6 weeks if pilot + experiment overlap)

---

## 4. Risk Analysis

### 4.1 Risk Analysis (From Phase 2A Assumptions A1-A5)

**Risk R1: Doctest Prevalence Insufficient (from A1)**

**Source Assumption:** A1 — The Stack Python contains sufficient doctest-bearing files (≥3% prevalence) for N token budget

**Description:** The Stack Python may have lower doctest prevalence than estimated (5-10%), making the compile+test condition infeasible at the 500M-1B token budget.

**Affected Hypotheses:** H-E1 (three-condition experiment collapses to two), H-C1 (primary feasibility test), H-M1 (doctest gate validation impossible)

**Severity:** High (collapses a major experimental condition but doesn't kill the study)

**Mitigation Strategy:**
1. **Prevention:** Run H-C1 pilot (10k files) before committing to full experiment infrastructure
2. **Detection:** Pilot prevalence rate < 3% is early warning; extrapolated token pool < 500M tokens is confirmation
3. **Response:**
   - PIVOT: Fall back to two-condition design (unfiltered vs compile-only) — P1 primary comparison still testable
   - SCOPE: Reduce token budget N if prevalence is 1-3% (compile+test still feasible at smaller scale)
   - ABORT compile+test condition only: Core study (compile-only vs unfiltered) remains intact

**Early Warning Indicators:**
- Pilot scan shows <1% files with any doctest pattern
- Extrapolated token pool estimate < 300M tokens (too small even with budget reduction)

---

**Risk R2: Null Signal — Execution Filtering Quality Does Not Correlate with HumanEval Quality (from A2)**

**Source Assumption:** A2 — Execution filtering quality signal (compile/doctest passing) correlates with training example quality relevant to HumanEval/MBPP

**Description:** Compile-passing and doctest-passing code in The Stack Python may not be more similar to HumanEval/MBPP benchmark code than unfiltered code — the filtering signal may select for "any runnable code" rather than "benchmark-quality code."

**Affected Hypotheses:** H-E1 (P1 primary prediction fails), H-M2 (no perplexity difference), H-M3 (no n-gram overlap difference), H-M4 (no cross-benchmark improvement)

**Severity:** Critical (null result for primary prediction; publishable but changes study narrative)

**Mitigation Strategy:**
1. **Prevention:** Design P3 stratum confound check to isolate execution quality signal from stratum selection bias
2. **Detection:** P1 result Δ < 2pp at Week 3 evaluation is confirmation; learning curve convergence at H-M2 is early warning
3. **Response:**
   - EXPLORE: Investigate alternative quality signals (function complexity, docstring quality, test coverage ratio)
   - SCOPE: Publish as null result with mechanism analysis — negative result is publishable given gap novelty
   - PIVOT: If null result, investigate whether token budget N is too small; try at 2N budget

**Early Warning Indicators:**
- HumanEval pass@1 difference between conditions < 1pp at week 3 evaluation
- Learning curves for filtered vs. unfiltered models converge within 5% of eval loss throughout training

---

**Risk R3: Model Insensitivity — Qwen2.5-Coder-1.5B Too Large/Small for Quality Effects (from A3)**

**Source Assumption:** A3 — Qwen2.5-Coder-1.5B is sensitive to SFT data quality at 500M-1B token budgets

**Description:** Qwen2.5-Coder-1.5B may be at a "data quality saturation" point where it already performs well on HumanEval regardless of filtering, or may be too small to benefit from the specific quality signal in execution-filtered data at these token budgets.

**Affected Hypotheses:** H-E1 (no differential benefit of filtering on 1.5B model), H-M2 (learning curves indistinguishable), H-M4 (no cross-benchmark improvement)

**Severity:** High (undermines primary model; 7B secondary model becomes primary)

**Mitigation Strategy:**
1. **Prevention:** Include 7B model as secondary check; if 1.5B shows no effect, 7B result provides alternative evidence
2. **Detection:** Compare 1.5B vs 7B filter effect magnitudes — if 7B shows effect but 1.5B does not, size mismatch confirmed
3. **Response:**
   - EXPLORE: Run experiment at different token budgets (250M, 500M, 1B) to find sensitivity region
   - SCOPE: Report 7B results as primary; reframe 1.5B as "model size boundary condition"
   - PIVOT: Switch primary model to 7B; cost implication is compute budget increase

**Early Warning Indicators:**
- 1.5B baseline HumanEval (unfiltered SFT) already exceeds 50% (saturated model)
- 1.5B model shows <1pp variance across training seeds (training is stable/saturated)

---

**Risk R4: Stratum Selection Bias Confounds P1 Result (from A4)**

**Source Assumption:** A4 — P3 stratum check is valid: compile-only-doctest-subset ≈ compile-only-full-stack within 1pp

**Description:** Doctest-bearing Python files in The Stack may be systematically better-quality code (library code, educational examples, open-source packages) independent of execution filtering. If so, the P1 improvement is attributable to stratum quality (documentation culture selection bias) rather than the execution gate itself.

**Affected Hypotheses:** H-E1 (P1 result confounded if P3 fails), H-M3 (n-gram overlap may reflect stratum bias not filtering)

**Severity:** High (undermines causal interpretation of P1 result, not the result itself)

**Mitigation Strategy:**
1. **Prevention:** P3 stratum confound check is pre-registered as part of experimental design (already in Phase 2A)
2. **Detection:** |compile-only-doctest-subset − compile-only-full| > 1pp at H-E1 evaluation confirms stratum bias
3. **Response:**
   - SCOPE: Reframe P1 result as "execution-gate-selected-stratum SFT outperforms random Stack Python SFT" — still novel and publishable
   - EXPLORE: Investigate stratum characteristics (average file complexity, docstring density, package source) to quantify bias
   - PIVOT: Design additional confound control with matched-quality unfiltered subset (by file complexity) to isolate execution gate effect

**Early Warning Indicators:**
- Pilot scan shows doctest-bearing files are predominantly from top-100 Python packages (systematic bias)
- Qualitative review shows doctest files have systematically longer/cleaner code than random files

---

**Risk R5: Doctest Execution Stability Issues at Scale (from A5)**

**Source Assumption:** A5 — `doctest` execution within main process does not cause stability issues at corpus-scan scale

**Description:** Scanning millions of Python files with doctest execution in-process may cause memory leaks, infinite loops from malformed doctests, or slow throughput that makes the filtering pipeline infeasible at scale.

**Affected Hypotheses:** H-M1 (filter gate validation requires stable pipeline), H-C1 (pilot may fail if stability issues exist), H-E1 (full dataset filtering blocked)

**Severity:** Medium (technical infrastructure issue, solvable with engineering)

**Mitigation Strategy:**
1. **Prevention:** Use per-doctest timeout (5 second max), process-level memory limit, and early termination on >3 consecutive failures
2. **Detection:** Pilot throughput rate < 1000 files/hour at stable memory; memory growth > 100MB/1000 files
3. **Response:**
   - EXPLORE: Implement subprocess isolation for doctest execution (accept 10x slower throughput)
   - SCOPE: Filter only files up to max size threshold (e.g., <50KB) to avoid large module files
   - PIVOT: Fall back to compile-only condition if doctest scanning proves unstable

**Early Warning Indicators:**
- Pilot (10k files) takes > 4 hours to complete
- Process memory grows linearly without GC collection during pilot

---

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Doctest prevalence insufficient | A1 | H-E1, H-M1, H-C1 | High |
| R2: Null signal — no quality correlation | A2 | H-E1, H-M2, H-M3, H-M4 | Critical |
| R3: Model insensitivity at token budget | A3 | H-E1, H-M2, H-M4 | High |
| R4: Stratum selection bias confounds P1 | A4 | H-E1, H-M3 | High |
| R5: Doctest execution stability at scale | A5 | H-M1, H-C1, H-E1 | Medium |

**Critical Risks: 1 (R2)**
**High Risks: 3 (R1, R3, R4)**
**Medium Risks: 1 (R5)**
**Low Risks: 0**

### 4.3 Baseline Failure Pattern Analysis

| Baseline Limitation | Potential Risk for This Study | Mitigation |
|---------------------|-------------------------------|------------|
| phi-1: GPT-4 oracle — opaque quality signal | Our compile/doctest gate may select code unrelated to HumanEval quality (→ R2) | P3 stratum check isolates execution signal |
| EffiCoder: instruction data at inference time | Raw corpus doctest may not map to instruction-following quality (→ R2) | Stick to pass@1 benchmarks; avoid instruction metrics |
| StarCoder: no equal-budget control | Token budget mismatch may dominate over quality signal (→ R3) | Strict equal-token-budget protocol |

---

## 5. Dependency Graph (DAG) + Timeline

### 5.1 Dependency Graph

```
═══════════════════════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) — 6 Hypotheses (H-E1, H-M1-4, H-C1)
PRACTICAL EXECUTION ORDER SHOWN
═══════════════════════════════════════════════════════════════════════════

[Phase 0 - Pilot (PRACTICAL FIRST STEP)]
    H-C1 (Condition — doctest prevalence feasibility check)
    [No dependencies — can run immediately]
         │
         ▼
    [Gate 0.5: H-C1 result determines compile+test feasibility]
    IF ≥3%: 3-condition experiment → proceed
    IF 1-3%: reduced-N compile+test → adapt
    IF <1%: 2-condition experiment → remove compile+test from H-E1
         │
         ▼
[Level 0 - Foundation]
    H-E1 (Existence — no logical dependencies; requires H-C1 pilot result)
         │
         ▼
    [Gate 1: H-E1 MUST PASS — MUST_WORK gate]
    IF FAIL: STOP entire hypothesis; publish null result
    IF PASS: proceed to mechanism chain
         │
         ▼
[Level 1 - Mechanism]
    H-M1 ← H-E1
    (Filter gate validation: are retained programs actually valid?)
         │
         ▼
[Level 2 - Mechanism]
    H-M2 ← H-M1
    (Noise reduction: do filtered models show lower perplexity on correct code?)
         │
         ▼
[Level 3 - Mechanism]
    H-M3 ← H-M2
    (Distribution shift: does filtered corpus have higher n-gram overlap with benchmarks?)
         │
         ▼
[Level 4 - Mechanism]
    H-M4 ← H-M3
    (Cross-benchmark generalization: does effect hold on both HumanEval and MBPP?)
         │
         ▼
    [Gate 2: H-M1 MUST PASS; H-M2-4 SHOULD PASS — mechanism confirmed]
         │
         ▼
[END — Verification Complete]

═══════════════════════════════════════════════════════════════════════════
Critical Path: H-C1 → H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Total Logical Depth: 6 levels (including H-C1 pilot)
═══════════════════════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 (Pilot) | H-C1 | None | SHOULD_WORK |
| 1 | H-E1 | H-C1 (informs conditions) | MUST_WORK |
| 2 | H-M1 | H-E1 | MUST_WORK |
| 3 | H-M2 | H-M1 | SHOULD_WORK |
| 4 | H-M3 | H-M2 | SHOULD_WORK |
| 5 | H-M4 | H-M3 | SHOULD_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE — 6 Hypotheses
═══════════════════════════════════════════════════════════════════════════════════
Phase/Hypothesis        │ W1   │ W2-3 │ W4   │ W5   │ W6   │ W7  
────────────────────────┼──────┼──────┼──────┼──────┼──────┼─────
PHASE 0: Pilot
  H-C1 (10k pilot scan) │ ████ │      │      │      │      │     
  [Gate 0.5]            │    ◆ │      │      │      │      │     
────────────────────────┼──────┼──────┼──────┼──────┼──────┼─────
PHASE 1: Foundation
  H-E1 (SFT experiment) │      │ ████ │      │      │      │     
  [Gate 1: MUST_WORK]   │      │    ◆ │      │      │      │     
────────────────────────┼──────┼──────┼──────┼──────┼──────┼─────
PHASE 2: Mechanisms
  H-M1 (filter valid.)  │      │      │ ████ │      │      │     
  H-M2 (perplexity)     │      │      │      │ ████ │      │     
  H-M3 (n-gram overlap) │      │      │      │      │ ████ │     
  H-M4 (cross-bench.)   │      │      │      │      │ ████ │     
  [Gate 2: MUST_WORK]   │      │      │      │      │    ◆ │     
────────────────────────┼──────┼──────┼──────┼──────┼──────┼─────
PHASE 2.5: Write-up
  H-C1 formal report    │      │      │      │      │      │ ████
════════════════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 7 weeks (practical: 6 weeks if pilot overlaps with infrastructure setup)
════════════════════════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-C1 (W1) → H-E1 (W2-3) → H-M1 (W4) → H-M2 (W5) → H-M3+H-M4 (W6)

Total Duration: 7 weeks
  Breakdown: 1 (H-C1 pilot) + 2 (H-E1 SFT) + 1 (H-M1) + 1 (H-M2) + 1 (H-M3+H-M4) + 1 (write-up)

Slack Available: 0 weeks (all sequential; H-M3 and H-M4 run in parallel in W6)
Critical Bottleneck: H-E1 SFT experiment (compute-intensive, 3-4 model training runs)

Note: H-M2, H-M3, H-M4 data collection runs DURING H-E1 training (intermediate checkpoints)
      Effective wall-clock may be closer to 5 weeks with good compute scheduling
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 6
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1 to H-M4)
- Condition: 1 (H-C1)

Verification Phases: 3
1. Pilot (H-C1 doctest prevalence scan) — Week 1
2. Foundation (H-E1 three-condition SFT) — Weeks 2-3
3. Mechanisms (H-M1-4 intermediate metrics) — Weeks 4-6

Total Duration: 7 weeks (wall-clock: ~5 weeks with parallel execution)
Critical Path Length: 7 weeks
Execution Mode: Sequential chain with H-M3/H-M4 parallel in W6

Compute Requirements (estimated):
- H-C1: CPU-only, ~2-4 hours for 10k file scan
- H-E1: 4 SFT training runs on Qwen2.5-Coder-1.5B (500M-1B tokens each)
         ~16-32 GPU-hours per run on A100 → 64-128 GPU-hours total for 1.5B
         Optional 7B secondary: ~5-10x compute cost
- H-M1-4: CPU/lightweight GPU, negligible additional compute (reuse H-E1 artifacts)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

**Step 1:** Execute H-C1 pilot (10k file doctest prevalence scan) — Week 1
**Step 2:** Evaluate Gate 0.5 → Determine compile+test feasibility; adapt H-E1 conditions
**Step 3:** Execute H-E1 (3 or 4 SFT training runs: unfiltered, compile-only, doctest-passing, P3 control) — Weeks 2-3
  - Collect intermediate checkpoints during training (for H-M2 learning curves)
**Step 4:** Evaluate Gate 1 → If H-E1 passes (P1: ≥2pp, p<0.05), proceed; else STOP
**Step 5:** Execute H-M1 (filter gate validation on pilot corpus) — Week 4
**Step 6:** Execute H-M2 (perplexity analysis using H-E1 checkpoint artifacts) — Week 5
**Step 7:** Execute H-M3 + H-M4 in parallel (n-gram overlap + cross-benchmark consistency, using H-E1 evaluation artifacts) — Week 6
**Step 8:** Evaluate Gate 2 → H-M1 must pass; H-M2-4 document findings
**Step 9:** Write H-C1 formal report and mechanism attribution summary — Week 7
**Final:** Phase 2B verification complete → proceed to Phase 2C experiment design

---

## 6. Dialectical Analysis

### 6.1 Thesis Statement

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Claim: Under equal token budget from The Stack Python corpus (SFT stage,
Qwen2.5-Coder-1.5B primary and 7B secondary), execution-filtered training data
(compile-only or doctest-passing) improves HumanEval pass@1 and MBPP pass@1 over
unfiltered data of equal token count, because execution filtering retains syntactically
and functionally consistent training examples.

Supporting Evidence:
1. phi-1 [Gunasekar et al., 2023] demonstrates quality-filtered SFT at equal token
   budget produces benchmark gains (1.3B model, 50.6% HumanEval) — validates
   equal-budget methodology
2. EffiCoder [Zeng et al., 2024] demonstrates execution-selected SFT improves
   HumanEval by +13pp on Qwen2.5-Coder-7B — validates execution selection signal
3. Curriculum learning theory [Bengio et al., 2009] predicts negative interference
   from invalid examples reduces gradient quality — validates noise reduction pathway
4. Python ecosystem (NumPy, SciPy, stdlib) generates high doctest prevalence (~5-10%)
   — validates feasibility of compile+test condition

Strengths:
- Objective, model-agnostic execution gates (vs. GPT-4 oracle in phi-1)
- Single-corpus three-condition ablation eliminates corpus confound
- P3 stratum check isolates execution signal from documentation culture bias
- 4-step causal chain with empirical falsifiers at each step

Expected Outcomes:
- Primary: ΔHumanEval(compile+test − unfiltered) ≥ 2pp, p < 0.05
- Secondary: Ordering holds: compile+test ≥ compile-only ≥ unfiltered
- Tertiary: Stratum check passes (|P3| ≤ 1pp), validating causal attribution

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis Development (H0-Based)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Null Hypothesis (H0): There is no significant difference in HumanEval pass@1 or
MBPP pass@1 between SFT on execution-filtered data and SFT on unfiltered data of
equal token count from The Stack Python, when controlling for base model,
training hyperparameters, and token budget.

Counter-Arguments:
1. The Stack Python is already heuristically filtered (deduplication, URL removal,
   license filtering by StarCoder pipeline) — incremental execution quality signal
   may be marginal after existing filtering (baseline limitation from StarCoder)
2. Qwen2.5-Coder-1.5B was pretrained on code data including execution-filtered
   sources — SFT may not distinguish filtering quality at 500M-1B token budgets
   (consistent with A3 assumption risk)
3. Doctest-bearing code in The Stack may be systematically library/educational code
   that benefits HumanEval via in-distribution overlap rather than execution quality
   (consistent with A4 stratum bias risk)

Potential Failure Points:
- R2 (null signal): Execution gate selects "any runnable code," not "HumanEval-quality code"
- R3 (model insensitivity): 1.5B model saturated at this token budget
- R4 (stratum bias): P1 improvement driven by documentation culture, not execution gate

Conditions Under Which H0 Would Be Supported:
- If ΔHumanEval < 2pp OR paired bootstrap p > 0.05 → P1 falsified, H0 not rejected
- If H-M1 shows compile-passing samples include substantial invalid code (filter broken)
- If P3 shows |compile-only-doctest-subset − compile-only-full| > 1pp (stratum dominates)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balanced Assessment:

The hypothesis H-ExecFilteredSFT-v1 presents a testable claim that execution-based
filtering of raw SFT corpus at equal token budget improves code LLM performance
through noise reduction and distributional alignment. However, the null hypothesis
raises valid concerns: The Stack Python is already heuristically filtered, the 1.5B
model may be insensitive at these token budgets, and doctest stratum selection may
confound the execution quality signal.

Resolution Path:

The verification plan addresses this dialectic through:
1. Foundation verification (H-E1): Three-condition ablation with P3 stratum confound
   check isolates execution signal from stratum selection bias
2. H-C1 pilot (Week 1): Empirically resolves feasibility uncertainty before
   committing full experiment resources
3. Sequential mechanism testing (H-M1 through H-M4): Tests each causal chain step
   independently, allowing mechanism attribution even if primary effect is confirmed
4. Gate conditions: H-E1 MUST_WORK gate allows early detection of H0 support
   without wasted compute on mechanism analysis

Conditions for Thesis Support:
- H-E1 passes (P1: ≥2pp, p<0.05) AND P3 stratum check passes (|P3| ≤ 1pp)
- H-M1 confirms filter gates work correctly
- At least one mechanism (H-M2 or H-M3) shows directional confirmation

Conditions for Antithesis (H0) Support:
- H-E1 P1 fails: Δ < 2pp or p > 0.05
- Or H-E1 P3 fails: stratum dominates (|P3| > 1pp) without execution gate contribution
- Or H-M1 fails: compile() retains systematic invalidity

Nuanced Outcome Possibilities:
1. Full Support: H-E1 passes + P3 passes + H-M* directional → Thesis fully validated
2. Partial Support: H-E1 passes + H-M* ambiguous → Effect confirmed, mechanism unclear
3. Stratum Confound: H-E1 passes + P3 fails → Effect exists but attributed to stratum, not execution gate
4. Null Result: H-E1 fails → H0 not rejected; publishable negative result

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence of effect | Execution filtering improves HumanEval/MBPP | No significant difference after equal-budget control | H-E1 P1 test (paired bootstrap) |
| Causal mechanism | Noise reduction + distribution shift chain | Alternative: stratum selection bias | P3 stratum confound check + H-M2/M3 |
| Filter gate validity | compile() and doctest select valid programs | Gates may have false positives/negatives | H-M1 spot-check validation |
| Cross-benchmark generalization | Effect holds on both HumanEval and MBPP | Effect may be HumanEval-specific | H-M4 cross-benchmark consistency |
| Model sensitivity | 1.5B model sensitive at 500M-1B token budget | Model may be too large/small for quality effects | 7B secondary + multi-budget analysis |
| Feasibility | Doctest prevalence ≥3% in The Stack Python | Prevalence may be too low for compile+test | H-C1 pilot scan (empirical check) |

**Overall Robustness Score:** Medium-High (strong falsification design, multiple confound controls; primary risk is null result from model insensitivity or low doctest prevalence — both manageable)

**Confidence in Verification Plan:** 0.75 (matching Phase 2A confidence level)

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** H-ExecFilteredSFT-v1 (confidence: 0.75)
- Execution-filtered SFT from raw corpus (The Stack Python) improves HumanEval/MBPP pass@1 at equal token budget
- Primary test: 3-condition SFT ablation (unfiltered / compile-only / doctest-passing) on Qwen2.5-Coder-1.5B

**Verification Structure:**
- Mode: Incremental (33% scope reduction via BUILD_ON established facts)
- Sub-Hypotheses: 6 total (H-E1, H-M1-4, H-C1)
  - H-E: 1 | H-M: 4 | H-C: 1
- Phases: 3 phases over 7 weeks (5 weeks wall-clock with parallel execution)
- Critical Gates: 2 decision points (Gate 0.5: feasibility; Gate 1: MUST_WORK)

**Risk Assessment:** High
- Primary concerns: Null signal risk (R2, Critical) and doctest prevalence (R1, High)
- Mitigations: P3 stratum check pre-registered; H-C1 pilot in Week 1

**Immediate Action:** Begin H-C1 pilot scan (10k files from The Stack Python) in Week 1 before committing compute to H-E1 SFT experiment

### 7.2 Conclusions

**Key Achievements:**
- 6 sub-hypotheses defined across 3 verification phases
- H0 directly addressed: paired bootstrap P1 test provides statistical rigor
- Mechanism agnosticism maintained: H-M2/M3/M4 disambiguate mechanism without committing upfront
- Stratum confound pre-registered (P3 check) — addresses strongest methodological critique

**Verification Execution Order:**

**Phase 0: Pilot** (Week 1)
- H-C1: Doctest prevalence pilot scan (10k files)
- Gate 0.5: Determines compile+test feasibility

**Phase 1: Foundation** (Weeks 2-3)
- H-E1: Three-condition SFT (unfiltered / compile-only / doctest-passing / P3 control) on Qwen2.5-Coder-1.5B
- Gate 1 (MUST_WORK): ΔHumanEval ≥ 2pp AND p < 0.05

**Phase 2: Mechanisms** (Weeks 4-6)
- H-M1: Filter gate validation (spot-check retained programs)
- H-M2: Perplexity analysis (noise reduction pathway)
- H-M3: N-gram overlap analysis (distribution shift pathway)
- H-M4: Cross-benchmark consistency (HumanEval + MBPP)
- Gate 2: H-M1 MUST pass; H-M2-4 SHOULD pass

**Critical Decision Points:**

1. **Gate 0.5 (Pilot):** H-C1 doctest prevalence result
   - ≥3%: Full 3-condition experiment as designed
   - 1-3%: Reduced-N compile+test condition
   - <1%: Fall back to 2-condition (unfiltered vs compile-only)

2. **Gate 1 (Foundation):** H-E1 MUST_WORK
   - FAIL: STOP — publish null result; investigate token budget or model size
   - PASS: Proceed to mechanism analysis

3. **Gate 2 (Mechanisms):** H-M1 MUST_WORK
   - H-M1 FAIL: EXPLORE filter gate implementation; do not proceed to H-M2-4
   - H-M2-4 FAIL: Document mechanism ambiguity; does not block Phase 5

**Open Questions (from Phase 2A):**
- Doctest prevalence in The Stack Python — empirical pilot required (H-C1 answers this)
- Optimal token budget N — 500M or 1B tokens? Depends on doctest pool size (A1)
- Does compile+test advantage hold on MBPP as well as HumanEval? (H-M4 answers this)
- Mechanism disambiguation (noise reduction vs. distribution shift vs. coverage concentration) — H-M2/M3 answer this

**Recommendations:**

1. **Immediate Actions:**
   - Start H-C1 pilot scan Week 1 (10k files, CPU-only, ~2-4 hours)
   - Set up SFT infrastructure (HuggingFace data streaming, lm-evaluation-harness) in parallel with pilot
   - Register token budget N based on H-C1 result before starting H-E1

2. **Resource Allocation:**
   - Allocate 7 weeks for critical path; plan for 5 weeks wall-clock with parallel compute
   - Reserve GPU budget for 4 SFT runs on 1.5B + optional 7B secondary
   - Use intermediate checkpoints during H-E1 training to collect H-M2 learning curve data at no extra cost

3. **Failure Management:**
   - H-C1 <3%: Pivot to 2-condition design immediately; do not wait
   - H-E1 null result: Publish with n-gram analysis to explain mechanism; note as valuable negative
   - Document all pilot statistics (not just final results) for paper's experimental details section

### 7.3 Appendices

**Appendix A: Phase 2A Reference**
- Source: docs/youra_research/03_refinement.yaml (ID: H-ExecFilteredSFT-v1)
- Supplementary: docs/youra_research/02_synthesis.yaml, 01_round_table/final_opinions.yaml
- Phase 2A convergence: Natural at Exchange 15; all 6 convergence criteria PASS

**Appendix B: MCP Tool Usage Summary**
- Total MCP calls planned: 4-6 (incremental mode)
- Tools: mcp__clearThought__scientificmethod (Step 3), mcp__clearThought__collaborativereasoning (Step 5)
- Note: MCP calls executed conceptually in this unattended run; full tool invocations
  will occur in Phase 2C per-hypothesis experiment design

**Appendix C: Established Facts Bypass List (DO NOT RE-VERIFY)**
- phi-1 equal-budget quality SFT methodology: ESTABLISHED
- EffiCoder execution selection → HumanEval improvement: ESTABLISHED
- HumanEval/MBPP as valid pass@1 benchmarks: ESTABLISHED
- The Stack Python availability on HuggingFace: ESTABLISHED

