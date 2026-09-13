# Verification Plan: LLAE: Length-Normalized Late-Layer Attention Entropy as a Training-Free Multi-Axis Hallucination Uncertainty Signal

**Date:** 2026-03-15
**Hypothesis ID:** H-LLAE-MultiAxis-v1
**Confidence:** 0.75
**Total Hypotheses:** 5 (H-E1, H-M1, H-M2, H-M3, H-M4)

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under open-domain QA settings with access-controlled decoder-only LLMs (LLaMA-3-8B, Mistral-7B), if we compute length-normalized late-layer attention entropy (LLAE = mean H_c / log(N_context), final L/3 layers, context tokens only) alongside logit entropy (LE), sequence log-probability (SLP), and semantic entropy (SE, QA-only), then we will observe statistically significant signal-task dissociation (Wilcoxon p < 0.05) in AUROC and cross-task rank stability (Spearman ρ), with LLAE capturing attentional routing instability and SE capturing output-level semantic dispersion — because these signals probe distinct internal failure modes: LLAE indexes context-routing commitment (grounding fragmentation), while SE, LE, and SLP index output-distribution ambiguity.

### 1.2 Alternative Hypothesis (H0)

There is no statistically significant difference in AUROC between LLAE, LE, SLP, and SE on TriviaQA or NQ-Open (Wilcoxon p > 0.05), and the SE+LLAE ensemble does not outperform SE alone by more than ΔAUROC = 0.02 with bootstrap CIs excluding zero. Perturbation conditions have no differential effect on LLAE vs SE (interaction F-test p > 0.05).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TriviaQA (primary), NQ-Open (primary), HaluEval-QA (secondary), TruthfulQA (mediation) (standard) | TriviaQA and NQ-Open provide human-verified factoid QA with retrieved context passages needed for LLAE computation. HaluEval-QA provides cross-task transfer test. TruthfulQA provides misconception-driven hallucination for mediation analysis. |
| **Model** | LLaMA-3-8B, Mistral-7B-v0.1 | Both models provide accessible attention weights via output_attentions=True. LLaMA-3-8B uses GQA with global context; Mistral-7B uses sliding-window attention — creating architectural boundary condition test. |

**Dataset Details:**
- Source: HuggingFace datasets; RUCAIBox/HaluEval GitHub; TruthfulQA GitHub
- Path: huggingface.co/datasets/trivia_qa, natural_questions, HaluEval, truthful_qa

**Model Details:**
- Type: Decoder-only autoregressive LLM (7-8B parameters)
- Source: HuggingFace Hub: meta-llama/Meta-Llama-3-8B, mistralai/Mistral-7B-v0.1

### 1.4 Baseline Methods (for comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Semantic Entropy (Farquhar et al. 2024) | AUROC ~0.75-0.82 | TriviaQA, NQ-Open |
| SelfCheckGPT (Manakul et al. 2023) | AUC-PR comparable to SE | WikiBio, factoid QA |
| Semantic Entropy Probes (Kossen et al. 2024) | Comparable to SE (single-pass) | TriviaQA, NQ-Open, BioASQ |
| Logit Entropy (Zhang et al. 2023) | AUROC 0.60–0.72 | HaluEval, factoid QA |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Grounded answers produce sparser context attention than ungrounded answers, holding answer length constant | Mechanistic interpretability literature on factual retrieval attention heads; length-normalization addresses confound | LLAE AUROC at chance; grounding-fragmentation mechanism collapses; H0 not rejected |
| A2 | HuggingFace output_attentions=True provides reliable per-layer attention weights for LLaMA-3-8B and Mistral-7B | Standard HuggingFace API; widely used in probing studies | Tensor extraction fails or returns incorrect attention maps; experiment not runnable |
| A3 | TriviaQA and NQ-Open correctness evaluable via exact-match/F1 without new annotation | Standard evaluation protocol in all prior SE/logit-entropy papers | Label noise inflates error variance; AUROC estimates unreliable |
| A4 | Semantic entropy NLI clustering valid for short-answer QA (TriviaQA, NQ-Open) but not long-form | Farquhar et al. 2024 validated SE on exactly these datasets | If SE applied to summarization, results theoretically invalid |
| A5 | Perturbation conditions (context-shuffle, question-paraphrase) implementable at inference-time only | Context-shuffle: word permutation; paraphrase: 5 rewrites via LLM API — no new datasets needed | Paraphrase generation may change question semantics beyond scope; SE inflation confounded |

### 1.6 Research Gap & Novelty

**Gap:** No existing study evaluates length-normalized late-layer context attention entropy (LLAE) as a standalone training-free hallucination proxy. No prior work uses controlled perturbation experiments to test mechanistic dissociation between attention-based and output-distribution uncertainty signals.

**Novelty:** Reframes hallucination uncertainty as a multi-axis diagnostic space (routing instability vs. semantic dispersion) rather than a single-metric leaderboard. LLAE detects grounding fragmentation (context-routing commitment); SE detects semantic ambiguity (output-level dispersion). The SE+LLAE ensemble captures orthogonal failure modes demonstrable via perturbation-based causal sensitivity experiments (context-shuffle × question-paraphrase 2×2 interaction).

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | TODO |
| H-M1 | Mechanism | MUST_WORK | H-E1 | TODO |
| H-M2 | Mechanism | MUST_WORK | H-M1 | TODO |
| H-M3 | Mechanism | MUST_WORK | H-M2 | TODO |
| H-M4 | Mechanism | SHOULD_WORK | H-M3 | TODO |

---

### 2.2 Hypothesis Specifications

---
**H-E1: LLAE Existence — Valid Training-Free Hallucination Signal**

**Statement**: Under open-domain short-answer QA with decoder-only LLMs (LLaMA-3-8B, Mistral-7B), if we compute LLAE (mean H_c / log(N_context), final L/3 layers, context tokens only), then LLAE AUROC > 0.60 on TriviaQA for both model families independently with at least one pairwise Wilcoxon p < 0.05 among {LLAE, LE, SLP, SE}, because grounding fragmentation produces measurably elevated context attention entropy.

**Rationale**: This is the foundation hypothesis — LLAE must be demonstrably better than chance before any mechanism or dissociation claims can be made. It validates LLAE as a useful signal and establishes the empirical baseline for all subsequent H-M tests. Without H-E1 passing, the entire multi-axis framework collapses.

**Variables**:
- Independent: Uncertainty signal type (LLAE vs LE vs SLP vs SE)
- Dependent: AUROC for hallucination binary classification (primary); Wilcoxon p-value (secondary)
- Controlled: Answer length (log(N_context) normalization), LLM family (per-family analysis), label quality (TriviaQA human-verified)

**Verification Protocol**:
1. Load LLaMA-3-8B and Mistral-7B with `output_attentions=True` on TriviaQA test set (≥1000 examples; minimum N=500 for bootstrap CI ≤±0.03).
2. Compute LLAE per example: partition attention rows by context/generated positions, compute H_c = -Σ a_j log(a_j) over context cols, normalize by log(N_context), average over final L/3 layers.
3. Compute LE, SLP, SE (k=10 samples, DeBERTa-large-MNLI clustering); assign binary correctness labels via exact-match/F1 vs TriviaQA gold.
4. Compute AUROC for each signal; run Wilcoxon signed-rank tests on paired per-example scores; report 95% bootstrap CIs (1000 resamples).
5. Run permutation negative control (shuffle correctness labels): verify all signal AUROCs within 0.5 ± 0.03.

**Success Criteria**:
- Primary: LLAE AUROC > 0.60 on TriviaQA (bootstrap lower CI > 0.55) for both LLaMA-3-8B AND Mistral-7B
- Secondary: At least one pairwise Wilcoxon p < 0.05 on TriviaQA; AUROC > 0.60 on NQ-Open (replication)

**Failure Response**:
- IF LLAE AUROC ≤ 0.55 on TriviaQA for both models: PIVOT — investigate layer window (early/middle) before abandoning; if all windows fail, grounding-fragmentation mechanism collapses → ABANDON

**Dependencies**: None (foundation; must pass before H-M1)

**Source**: Phase 2A SH1 (sh1_existence), Prediction P1

---

---
**H-M1: Grounding Sparsity — Correct Answers Produce Lower H_c Than Hallucinations**

**Statement**: Under extractive short-answer QA (TriviaQA gold-span subset), if factual recall succeeds, then H_c (length-normalized context attention entropy) is significantly lower for correct answers than hallucinated answers (ΔH_c = H_c_hallucinated - H_c_correct > 0, bootstrap CI excludes zero), because grounded factual recall concentrates attention on specific source tokens while hallucination disperses attention uniformly across context.

**Rationale**: H-M1 validates the mechanism underlying H-E1: LLAE must be high for hallucinations specifically due to routing failure, not generic task difficulty. This distinguishes the mechanistic claim (grounding-fragmentation) from a trivial difficulty confound. H-M1 failure would require reinterpreting LLAE as a difficulty signal rather than a grounding signal.

**Variables**:
- Independent: Answer correctness (correct vs hallucinated, binary)
- Dependent: H_c per example; ΔH_c (mean difference); AUROC(H_c) on extractive QA
- Controlled: Answer length (log-normalization), restricted to extractive QA subset (context contains answer span), per-model-family analysis

**Verification Protocol**:
1. Filter TriviaQA to extractive subset: examples where gold answer appears verbatim in retrieved context passage.
2. Compute H_c and H_s per example per model family (separate attention partition passes for context vs self positions).
3. Run Mann-Whitney U test: H_c correct vs incorrect; compute ΔH_c with bootstrap 95% CI (1000 resamples, N≥500).
4. Compute AUROC(H_c); confirm H_c AUROC replicates H-E1 AUROC on extractive subset.
5. Compare AUROC(H_c) vs AUROC(H_s) via Wilcoxon to isolate context-specificity (H-M2 prerequisite).

**Success Criteria**:
- Primary: ΔH_c > 0 with bootstrap 95% CI excluding zero on TriviaQA extractive subset
- Secondary: AUROC(H_c) replicates H-E1 result on extractive subset (≥0.60)

**Failure Response**:
- IF ΔH_c ≈ 0 (CI includes zero): PIVOT — investigate head-type stratification (induction heads vs retrieval heads); if systematic ΔH_c = 0 across all heads, grounding-sparsity mechanism not supported → reframe LLAE as difficulty signal

**Dependencies**: H-E1 must pass (LLAE must exist as signal before mechanism can be tested)

**Source**: Phase 2A Causal Step 1, Key Tension (H_c as routing proxy)

---

---
**H-M2: Context-Specificity Contrast — H_c Predicts Hallucination Better Than H_s**

**Statement**: Under extractive QA (TriviaQA gold-span subset), if LLAE captures context-routing commitment rather than generic decoding instability, then AUROC(H_c) - AUROC(H_s) > 0.02 (bootstrap CI excludes zero), where H_s = generated→self attention entropy, because routing instability is a context-specific failure mode that H_s (self-attention pattern) cannot capture.

**Rationale**: H-M2 eliminates the confound that LLAE merely tracks generic generation difficulty. If H_c and H_s have equivalent AUROCs, then LLAE is not specifically measuring context-grounding commitment but some general decoding difficulty signal. The H_c > H_s AUROC contrast formally distinguishes the mechanistic claim. This is Prof. Vera's formally-required mechanistic test.

**Variables**:
- Independent: Attention partition type (context tokens vs generated/self tokens)
- Dependent: AUROC(H_c) - AUROC(H_s) (pairwise difference)
- Controlled: Extractive QA subset only, same layer window (final L/3), per-model-family analysis

**Verification Protocol**:
1. Using same inference pass as H-M1, extract H_s: attention entropy from generated token rows over generated/self token columns, normalized by log(N_generated).
2. Compute AUROC(H_s) as hallucination predictor on extractive TriviaQA subset.
3. Compute ΔAUROC = AUROC(H_c) - AUROC(H_s); bootstrap 95% CI (1000 resamples).
4. Wilcoxon signed-rank test on paired per-example {H_c, H_s} scores.
5. Report both signal AUROCs and the signed difference with CI.

**Success Criteria**:
- Primary: ΔAUROC(H_c - H_s) > 0.02 with bootstrap CI excluding zero on extractive TriviaQA
- Secondary: Wilcoxon p < 0.05 for H_c vs H_s pairwise comparison

**Failure Response**:
- IF ΔAUROC ≤ 0.02 or CI includes zero: EXPLORE — stratify by head type (retrieval heads vs induction heads) to identify subset of heads driving H_c signal; if no subset shows context-specificity, LLAE reframed as generic difficulty signal, weakening mechanistic claim

**Dependencies**: H-M1 must pass (grounding sparsity must be confirmed before context-specificity test is meaningful)

**Source**: Phase 2A Causal Step 2, Key Tension, Prof. Vera/Prof. Rex mechanistic requirements

---

---
**H-M3: Mechanistic Orthogonality — LLAE and SE Capture Distinct Failure Modes**

**Statement**: Under TriviaQA, if LLAE and SE probe orthogonal hallucination failure modes, then the 2×2 perturbation interaction (perturbation type {context-shuffle, question-paraphrase} × signal type {LLAE, SE}) is statistically significant (F-test p < 0.05), with context-shuffle selectively degrading LLAE AUROC (ΔAUROC_LLAE > 0.05, ΔAUROC_SE ≤ 0.02) and question-paraphrase selectively inflating SE uncertainty (ΔAUROC_SE increase > 0.05, LLAE stable), because LLAE tracks context-routing commitment while SE tracks semantic output dispersion — orthogonal internal signals.

**Rationale**: H-M3 is the causal linchpin of the entire hypothesis. Without the perturbation 2×2 interaction, the orthogonality claim is merely correlational (Spearman ρ < 0.5). The 2×2 design provides controlled causal evidence: each perturbation selectively disrupts only one signal's information source. This is Prof. Rex's required falsifiability test. H-M3 also validates that the SE+LLAE ensemble (P2) provides non-redundant value.

**Variables**:
- Independent (factor 1): Perturbation type (context-shuffle vs question-paraphrase)
- Independent (factor 2): Uncertainty signal type (LLAE vs SE)
- Dependent: ΔAUROC from baseline per signal per perturbation condition; F-statistic for interaction
- Controlled: TriviaQA (≥500 examples), same inference seed, paraphrase quality check, per-model-family replication

**Verification Protocol**:
1. Re-run inference on TriviaQA (≥500 examples) under context-shuffle: randomly permute retrieved passage token order per example, recompute LLAE and SE.
2. Re-run inference under question-paraphrase: generate 5 paraphrases per question via small instruction LLM API, run inference on each, take mean signal score.
3. Compute ΔAUROC_LLAE and ΔAUROC_SE for each perturbation condition vs baseline.
4. Factorial ANOVA (2×2 design): perturbation type × signal type interaction F-test; report effect sizes (Cohen's d for each cell).
5. Permutation control for ANOVA: shuffle perturbation condition labels, verify F < critical value at α=0.05.

**Success Criteria**:
- Primary: 2×2 interaction F-test p < 0.05 on TriviaQA for at least one model family
- Secondary: Context-shuffle ΔAUROC_LLAE > 0.05 AND ΔAUROC_SE ≤ 0.02 (selective sensitivity confirmed)
- Tertiary: Cross-signal Spearman ρ < 0.5 at example level (confirming low rank-correlation)

**Failure Response**:
- IF F-test p > 0.05: PIVOT — compute within-family replication separately (LLaMA-3 vs Mistral-7B); if both fail, mechanistic dissociation is not supported by perturbation evidence, weaken causal framing to "complementary signals" without mechanistic claim

**Dependencies**: H-M2 must pass (context-specificity confirmed before selective perturbation interpretation is valid)

**Source**: Phase 2A Causal Step 3, Prediction P3, Prof. Rex/Dr. Ally perturbation design requirements

---

---
**H-M4: TruthfulQA Mediation — Parametric Belief Distortion vs Retrieval Instability**

**Statement**: Under TruthfulQA with context-prefix prompt format, if misconception-driven hallucinations reflect parametric belief distortion (model ignores context), then context-mass (sum of attention weights on context tokens) approaches zero for incorrect TruthfulQA answers, LLAE AUROC < 0.55 on TruthfulQA (routing is committed but to wrong parametric prior), while SE may still detect semantic dispersion — because TruthfulQA errors are context-independent parametric recall failures, mechanistically different from TriviaQA retrieval instability.

**Rationale**: H-M4 is an exploratory mediation test that demonstrates the diagnostic value of LLAE's architecture-specificity: it should *fail* on TruthfulQA precisely because misconception errors don't involve context-routing instability. This distinguishes two hallucination classes (retrieval instability vs. parametric belief distortion) and supports the multi-axis diagnostic framing. H-M4 failure to show the predicted asymmetry would not invalidate the main hypothesis but would require reinterpreting the scope.

**Variables**:
- Independent: Dataset type (TriviaQA context-dependent vs TruthfulQA parametric)
- Dependent: Context-mass (sum attention weights on context positions); LLAE AUROC on TruthfulQA; SE AUROC on TruthfulQA
- Controlled: Context-prefix format for TruthfulQA (provide minimal context to enable H_c computation), per-model-family analysis

**Verification Protocol**:
1. Load TruthfulQA (≥500 examples) with context-prefix format: prepend "Context: [minimal factual passage]" to each question to create context tokens.
2. Compute context-mass per example: sum(attention weights on context token positions, final L/3 layers).
3. Compare context-mass distributions for correct vs incorrect TruthfulQA answers; compute Cohen's d.
4. Compute LLAE AUROC and SE AUROC on TruthfulQA; compare to TriviaQA AUROC values.
5. Report LLAE AUROC asymmetry: TriviaQA > TruthfulQA (retrieval instability vs parametric distortion distinction confirmed).

**Success Criteria**:
- Primary: LLAE AUROC < 0.55 on TruthfulQA (routing committed to wrong parametric prior, not instability)
- Secondary: Context-mass near zero for incorrect TruthfulQA answers; Cohen's d effect size > 0.3 on context-mass distribution
- Tertiary: SE AUROC ≥ 0.55 on TruthfulQA (SE may still detect semantic dispersion)

**Failure Response**:
- IF LLAE AUROC ≥ 0.60 on TruthfulQA: EXPLORE — if routing-committed misconceptions exist, reinterpret: both hallucination classes may show routing instability under different prompt formats; weakens the retrieval vs parametric distinction but does not invalidate H-M3 or H-E1

**Dependencies**: H-M3 must pass or be in progress (orthogonality test informs interpretation of H-M4 mediation)

**Source**: Phase 2A Causal Step 4, known_limitations (Mistral-7B sliding window), TruthfulQA mediation design

---

## Risk Analysis

### Risk-Hypothesis Mapping

| Risk | Source | Description | Severity | Affected Hypotheses |
|------|--------|-------------|----------|---------------------|
| R1 | A1 | Grounding-sparsity assumption fails — LLAE AUROC at chance | **CRITICAL** | H-E1, H-M1, H-M2, H-M3 |
| R2 | A2 | HuggingFace output_attentions returns malformed tensors | **HIGH** | All hypotheses |
| R3 | A3 | TriviaQA/NQ-Open label noise degrades AUROC reliability | **HIGH** | H-E1, H-M1, H-M2 |
| R4 | A4 | SE applied outside valid scope (summarization) | **LOW** | (scope-constrained; prevented by design) |
| R5 | A5 | Paraphrase generation changes question semantics, confounding H-M3 | **MEDIUM** | H-M3 |
| R6 | (arch) | Mistral-7B sliding-window excludes context tokens for long examples | **HIGH** | H-E1, H-M1 (Mistral-7B only) |
| R7 | (arch) | GQA (LLaMA-3-8B) head heterogeneity conflates head types | **MEDIUM** | H-M1, H-M2 |
| R8 | (stat) | Multiple comparisons inflation (32 AUROC values) | **MEDIUM** | H-E1 (primary test) |
| R9 | (compute) | SE 10× compute overhead; single GPU may require 48h+ | **MEDIUM** | All SE-inclusive tests |

### Mitigation Strategies

**R1 — Grounding-Sparsity Failure (CRITICAL)**
- Prevention: Run 50-example pilot on LLaMA-3-8B before full compute commitment; check AUROC direction
- Detection: Pilot AUROC < 0.55 = early warning; if confirmed at N=200, stop and pivot
- Response: PIVOT → layer window sensitivity analysis (early/middle layers); if all windows fail → ABANDON H-E1 and revise scope

**R2 — Attention Tensor Reliability (HIGH)**
- Prevention: Unit test attention tensor shapes and row-sum normalization (row sums ≈ 1.0 ± 1e-5) before any examples processed
- Detection: Per-example shape assertion; flag examples where attention rows don't sum to 1.0
- Response: If systematic failures, investigate HuggingFace version compatibility; downgrade or upgrade as needed

**R3 — Label Noise from String Matching (HIGH)**
- Prevention: Use TriviaQA's multiple-alias exact-match (covers ~95% of correct answers) + F1 ≥ 0.5 soft-match fallback
- Detection: Validate matching on 50-example pilot: manually verify 10 borderline cases
- Response: If F1 soft-match changes >5% of labels vs exact-match, report both label sets; use F1 as primary

**R4 — SE Scope Violation (LOW)**
- Prevention: SE computation restricted to TriviaQA and NQ-Open only by design; no summarization datasets used
- Detection: Code-level assertion: SE computation blocked for non-QA datasets
- Response: N/A — scope constraint prevents violation

**R5 — Paraphrase Quality Contamination (MEDIUM)**
- Prevention: Validate paraphrase quality: BLEU-4 ≥ 0.6 between original and paraphrase; manually review 20 examples
- Detection: If BLEU-4 < 0.6 for >20% of paraphrases, quality insufficient
- Response: PIVOT → use T5-based paraphrase model with higher semantic similarity constraint; reduce to 3 paraphrases if quality insufficient

**R6 — Mistral-7B Sliding-Window Scope Limit (HIGH)**
- Prevention: Log effective context utilization per example (N_tokens_in_window / N_context_tokens); restrict Mistral-7B analysis to examples where N_context ≤ 3500 tokens
- Detection: Flag examples where context exceeds window; compute H_c only over accessible context tokens
- Response: Report Mistral-7B LLAE results with explicit context-length constraint; position as architectural boundary condition not failure

**R7 — GQA Head Heterogeneity (MEDIUM)**
- Prevention: Average over all heads as primary; exploratory per-head-group analysis as secondary
- Detection: Compute per-head AUROC variance; if variance > 0.1, head types are heterogeneous
- Response: EXPLORE → identify top-K AUROC heads; report all-head average as primary with head-type analysis as supplementary

**R8 — Multiple Comparisons Inflation (MEDIUM)**
- Prevention: Pre-register all statistical tests before experiments; apply Bonferroni correction within dataset-model test families (adjusted α = 0.0125 for 4 signals)
- Detection: Any p-value between 0.0125 and 0.05 requires Bonferroni-corrected reporting
- Response: Report both uncorrected and Bonferroni-corrected p-values; primary claim requires Bonferroni-corrected p < 0.05

**R9 — Compute Budget (MEDIUM)**
- Prevention: Pre-estimate SE compute time with 50-example pilot; target N=500 minimum if compute-limited
- Detection: If SE for 1000 examples exceeds 36h on single GPU, switch to N=500
- Response: N=500 is sufficient for bootstrap CI ≤ ±0.03 (power analysis); batched SE generation with vLLM or HuggingFace Pipeline for efficiency

### Pre-Experiment Checklist (Required Before Full Runs)

1. ✅ Unit test attention tensors shape + row-sum normalization [R2]
2. ✅ Validate multi-alias string matching on 50 pilot examples [R3]
3. ✅ Check context-length distribution for Mistral-7B (N_context vs 4096) [R6]
4. ✅ Pre-register all statistical tests in pipeline notebook [R8]
5. ✅ Run 50-example LLaMA-3-8B pilot; verify LLAE AUROC > 0.55 [R1]

**Risk Summary:** 1 Critical, 3 High, 4 Medium, 1 Low — all mitigable with standard practices.

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) — 5 Hypotheses, H-LLAE-MultiAxis-v1
═══════════════════════════════════════════════════════════════

[Phase 1 — Foundation]
    ┌─────────────────────────────────────────────────┐
    │  H-E1: LLAE Existence (MUST_WORK)               │
    │  Gate 1: AUROC > 0.60 on TriviaQA, both models  │
    └────────────────────┬────────────────────────────┘
                         │  ✓ PASS → continue
                         │  ✗ FAIL → STOP (all downstream blocked)
                         ▼
[Phase 2 — Core Mechanisms]
    ┌─────────────────────────────────────────────────┐
    │  H-M1: Grounding Sparsity (MUST_WORK)           │
    │  Gate: ΔH_c > 0 with CI excl. zero              │
    └────────────────────┬────────────────────────────┘
                         │  ✓ PASS → continue
                         │  ✗ FAIL → PIVOT (head-type analysis)
                         ▼
    ┌─────────────────────────────────────────────────┐
    │  H-M2: Context-Specificity Contrast (MUST_WORK) │
    │  Gate: ΔAUROC(H_c - H_s) > 0.02, CI excl. zero  │
    └────────────────────┬────────────────────────────┘
                         │  ✓ PASS → continue
                         │  ✗ FAIL → EXPLORE (head stratification)
                         ▼
    ┌─────────────────────────────────────────────────┐
    │  H-M3: Mechanistic Orthogonality (MUST_WORK)    │
    │  Gate: 2×2 perturbation F-test p < 0.05         │
    └────────────────────┬────────────────────────────┘
                         │  ✓ PASS → continue
                         │  ✗ FAIL → PIVOT (weaken causal framing)
                         ▼
[Phase 3 — Mediation Analysis]
    ┌─────────────────────────────────────────────────┐
    │  H-M4: TruthfulQA Mediation (SHOULD_WORK)       │
    │  Gate: LLAE AUROC < 0.55 on TruthfulQA          │
    └─────────────────────────────────────────────────┘
                         │  ✓ PASS → Two hallucination classes confirmed
                         │  ✗ FAIL → EXPLORE (reinterpret parametric errors)

═══════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 (phases 1-2)
Mediation Path: → H-M4 (phase 3, exploratory)
═══════════════════════════════════════════════════════════════
```

### 3.3 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type | Fail Action |
|-------|-----------|---------------|-----------|-------------|
| 0 | H-E1 | None | MUST_WORK | STOP all |
| 1 | H-M1 | H-E1 | MUST_WORK | PIVOT |
| 2 | H-M2 | H-M1 | MUST_WORK | EXPLORE |
| 3 | H-M3 | H-M2 | MUST_WORK | PIVOT |
| 4 | H-M4 | H-M3 | SHOULD_WORK | EXPLORE |

### 3.4 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | LLAE AUROC > 0.60 (bootstrap CI > 0.55) on TriviaQA, both model families | STOP — re-examine layer window; if all windows fail, revise hypothesis |
| H-M1 | MUST_WORK | ΔH_c > 0 with bootstrap 95% CI excluding zero on extractive TriviaQA | PIVOT — stratify by attention head type |
| H-M2 | MUST_WORK | ΔAUROC(H_c − H_s) > 0.02 with CI excluding zero | EXPLORE — head-type stratification; if no subset, reframe as difficulty signal |
| H-M3 | MUST_WORK | 2×2 perturbation interaction F-test p < 0.05 on TriviaQA | PIVOT — report as "complementary signals" without causal framing |
| H-M4 | SHOULD_WORK | LLAE AUROC < 0.55 on TruthfulQA; context-mass near zero for misconception errors | EXPLORE — reinterpret parametric error class |

### 3.5 Timeline

| Phase | Hypotheses | Duration | Dependencies |
|-------|------------|----------|-------------|
| Phase 1: Foundation | H-E1 | 1–2 days | Pre-experiment checklist first |
| Phase 2A: Grounding | H-M1, H-M2 | 1–2 days | H-E1 pass required |
| Phase 2B: Orthogonality | H-M3 | 2–3 days | H-M2 pass required; 2×2 inference passes |
| Phase 3: Mediation | H-M4 | 1 day | H-M3 complete (SHOULD_WORK) |

**Total Duration:** 5–8 days (single GPU; SE compute may extend Phase 1 by 1 day)

---

## 4. Execution Timeline

### 4.1 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE — 5 Hypotheses (H-LLAE-MultiAxis-v1)
═══════════════════════════════════════════════════════════════════════════
Phase / Hypothesis    │ W1-2     │ W3-4     │ W5       │ W6       │ W7
──────────────────────┼──────────┼──────────┼──────────┼──────────┼──────
Pre-Experiment Setup  │ ████     │          │          │          │
  (checklist R1-R9)   │          │          │          │          │
──────────────────────┼──────────┼──────────┼──────────┼──────────┼──────
PHASE 1: Foundation   │          │          │          │          │
  H-E1 (LLAE Exist.)  │     █████│█████     │          │          │
  [Gate 1 ◆]          │          │ ◆        │          │          │
──────────────────────┼──────────┼──────────┼──────────┼──────────┼──────
PHASE 2A: Grounding   │          │          │          │          │
  H-M1 (H_c sparsity) │          │     █████│█████     │          │
  H-M2 (H_c vs H_s)   │          │          │     █████│          │
  [Gate 2A ◆]         │          │          │          │ ◆        │
──────────────────────┼──────────┼──────────┼──────────┼──────────┼──────
PHASE 2B: Dissociation│          │          │          │          │
  H-M3 (2×2 perturb.) │          │          │          │ █████████│█████
  [Gate 2B ◆]         │          │          │          │          │     ◆
──────────────────────┼──────────┼──────────┼──────────┼──────────┼──────
PHASE 3: Mediation    │          │          │          │          │
  H-M4 (TruthfulQA)   │          │          │          │          │  ███
──────────────────────┼──────────┼──────────┼──────────┼──────────┼──────
═══════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 (Phases 1-2B)
Total Duration: ~6 weeks (single GPU, sequential)
═══════════════════════════════════════════════════════════════════════════
```

### 4.2 Critical Path Analysis

```
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Critical Path Duration: ~5 weeks (excluding pre-experiment setup)
Off-Critical Path: H-M4 (mediation, can run concurrently with H-M3 write-up)

Duration Breakdown:
  Pre-experiment checklist:  3-5 days
  H-E1 (AUROC, 2 models):    5-7 days (SE compute dominates)
  H-M1 (extractive subset):  3-4 days (piggybacks H-E1 inference)
  H-M2 (H_c vs H_s):         2-3 days (same inference pass as H-M1)
  H-M3 (2×2 perturbation):   5-7 days (3 additional inference passes × 2 models)
  H-M4 (TruthfulQA):         2-3 days (new dataset, existing pipeline)

Slack Available: 0 days (all gated sequential)
Gate Decision Points: Gate 1 (after H-E1), Gate 2A (after H-M2), Gate 2B (after H-M3)
```

### 4.3 Resource Summary

```
Total Hypotheses: 5 (H-E1, H-M1, H-M2, H-M3, H-M4)
Verification Phases: 3 (Foundation, Grounding+Dissociation, Mediation)
Total Duration: ~6 weeks calendar / ~8-10 GPU-days active compute

Compute Estimates (single A100 80GB or equivalent):
  LLAE/LE/SLP per example: ~0.1s (batched)
  SE per example: ~1s (k=10 sampling passes)
  1000 examples × 2 models × SE: ~6-8h total
  Perturbation passes (×3): ~4-6h
  Total GPU time: ~12-18h active + overhead

Datasets Required (all publicly available):
  - TriviaQA (primary): huggingface.co/datasets/trivia_qa
  - NQ-Open (primary): huggingface.co/datasets/natural_questions
  - HaluEval-QA (secondary): RUCAIBox/HaluEval GitHub
  - TruthfulQA (mediation): sylinrl/TruthfulQA GitHub

Models Required:
  - meta-llama/Meta-Llama-3-8B (HuggingFace Hub)
  - mistralai/Mistral-7B-v0.1 (HuggingFace Hub)
```

### 4.4 Execution Order

```
Step 1: Pre-experiment checklist (R1-R9 mitigations) — 3-5 days
Step 2: Execute H-E1 (full TriviaQA + NQ-Open, both models) — 5-7 days
Step 3: Gate 1 evaluation → LLAE AUROC > 0.60 required
Step 4: Execute H-M1 + H-M2 (extractive subset, H_c vs H_s) — 5-7 days
Step 5: Gate 2A evaluation → ΔH_c > 0 and ΔAUROC(H_c-H_s) > 0.02 required
Step 6: Execute H-M3 (2×2 perturbation experiment) — 5-7 days
Step 7: Gate 2B evaluation → F-test p < 0.05 required
Step 8: Execute H-M4 (TruthfulQA mediation, SHOULD_WORK)
Step 9: Compile results → Pass to Phase 2C for experiment design
```

---

## 5. Dialectical Analysis

### 5.1 Thesis

**The LLAE multi-axis framework provides scientifically justified, practically significant advances in hallucination detection.**

LLAE probes an attention-based internal signal (context-routing commitment) that is mechanistically distinct from output-distribution signals (SE, LE, SLP). The perturbation 2×2 design provides controlled causal evidence for orthogonality. The multi-axis framework reframes hallucination detection from "which signal is best?" to "which signal captures which failure mode?" — a structural theory rather than another metric. All statistical tests are pre-registered with crisp falsifiers. The pipeline is inference-only, single-GPU, and uses publicly available models and datasets.

### 5.2 Antithesis

**The LLAE mechanism claim may not survive empirical testing, and the orthogonality claim is not yet established.**

The critical weakness is that LLAE's AUROC advantage over LE/SLP could reflect generic generation difficulty rather than context-routing commitment. Without H-M2 (H_c vs H_s AUROC contrast) passing, the mechanistic interpretation is unfounded. The perturbation 2×2 design is inferential, not interventional — perturbations could introduce confounds (context-shuffle may change difficulty, not just routing). Mistral-7B sliding-window attention creates a fundamental architectural scope limitation that could undermine generalization claims. If H-M3 (orthogonality) fails, SE+LLAE ensemble becomes redundant. The causal framing depends entirely on one statistical interaction passing.

H0 is plausible: if LLAE tracks generic decoding uncertainty rather than grounding commitment, all AUROC differences would be explained by difficulty effects already captured by LE/SLP, and the SE+LLAE ensemble would show ΔAUROC ≤ 0.02. The TruthfulQA mediation could equally show LLAE detecting misconception uncertainty rather than failing — which would contradict the context-routing framing.

### 5.3 Synthesis

**LLAE's value depends on empirical validation hierarchy: existence first, mechanism second, orthogonality third.**

The hypothesis is scientifically rigorous precisely because it has pre-registered falsifiers at every level. The most likely empirical outcome: H-E1 passes (LLAE has non-trivial AUROC), H-M1 partially passes (ΔH_c > 0 but small), H-M2 provides a nuanced picture (H_c > H_s by a small margin in extractive QA), H-M3 is the decisive test. Even if H-M3 fails (orthogonality not supported by perturbation), the work contributes a negative result showing attention entropy is a complementary difficulty signal rather than a mechanistically independent routing signal — still publishable and informative.

The synthesis recommendation: proceed with the verification roadmap as designed. Gate architecture ensures fast failure if H-E1 is at chance. The 50-example pilot provides early warning. The result space includes multiple publishable outcomes even under partial confirmation.

### 5.4 Robustness Assessment

| Scenario | Outcome | Publishability |
|----------|---------|----------------|
| All gates pass (H-E1 through H-M3) | Full multi-axis framework confirmed | Strong (ICLR/NeurIPS target) |
| H-E1 + H-M1/M2 pass, H-M3 fails | LLAE is complementary difficulty signal, not orthogonal | Moderate (EMNLP/findings) |
| H-E1 passes, H-M1/M2 fail | LLAE exists but mechanism is not grounding-specific | Limited (negative result; publishable as benchmark finding) |
| H-E1 fails | LLAE has no signal; grounding-sparsity mechanism wrong | Null result; pivot to head-type stratification before abandoning |

---

## 6. Executive Summary & Conclusions

### Summary

**Hypothesis:** H-LLAE-MultiAxis-v1 proposes that length-normalized late-layer context attention entropy (LLAE) is a training-free hallucination detection signal that captures context-routing instability — a failure mode orthogonal to semantic output dispersion (SE). Together, LLAE+SE constitute a two-axis uncertainty framework for LLM hallucination detection.

**Verification Roadmap (5 hypotheses, 6 weeks):**
- H-E1: Validate LLAE exists as non-trivial signal (AUROC > 0.60 on TriviaQA)
- H-M1: Confirm grounding produces sparse context attention (ΔH_c > 0)
- H-M2: Establish context-specificity (H_c > H_s AUROC contrast)
- H-M3: Prove orthogonality via 2×2 perturbation interaction (F-test p < 0.05)
- H-M4: Distinguish hallucination classes via TruthfulQA mediation (exploratory)

**Key Risks:** R1 (grounding-sparsity at chance, CRITICAL) → mitigated by 50-example pilot; R6 (Mistral sliding-window, HIGH) → context-length stratification; R2 (tensor extraction, HIGH) → unit tests.

**Phase 2A Established Facts (BUILD_ON, skipped):**
- SE detects hallucinations above chance (Farquhar et al. 2024) ✓
- Logit entropy correlates with factual errors ✓
- LLMs are systematically overconfident ✓
- SelfCheckGPT provides competitive black-box baseline ✓

**Scope Reduction:** 50% — only PROVE_NEW claims require new hypotheses.

### Conclusions

1. **Execution Order:** Pre-experiment checklist → H-E1 → [Gate 1] → H-M1+M2 → [Gate 2A] → H-M3 → [Gate 2B] → H-M4
2. **Decision Points:** Gate 1 (H-E1 AUROC > 0.60) is the critical decision point — all downstream hypotheses depend on it
3. **Success Definition:** Full confirmation requires H-E1 through H-M3 all passing; partial confirmation (H-E1+H-M1+H-M2) is publishable
4. **Phase 5 Note:** Baseline comparison (LLAE+SE vs SelfCheckGPT, SEPs at scale) deferred to Phase 5 per v3.0 design

### Open Questions

1. Does attention entropy gate on specific head types (induction heads, retrieval heads) or all heads equally?
2. What is the minimum context length for LLAE to be informative — does it degrade with very short contexts?
3. Can LLAE be combined with selective abstention to improve coverage-accuracy trade-off vs SE threshold?

---

*Generated by YouRA Phase 2B (Compact v1.0) | 2026-03-15*
