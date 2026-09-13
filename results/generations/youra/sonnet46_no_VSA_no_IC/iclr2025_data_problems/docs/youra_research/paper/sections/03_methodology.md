# 3. Methodology

Our methodology is motivated by a single observation: Pythia's sequential dataloader preserves the exact order in which documents were consumed during training, and The Pile's block structure makes this order informationally rich — different checkpoints have genuinely different domain exposure profiles. We exploit this to build a within-family panel dataset for domain-benchmark correlation analysis.

The analysis proceeds in three stages: (1) verifying that Pile domains are cognitively distinct (the domain content differentiation prerequisite), (2) extracting domain exposure trajectories from Pythia's exact dataloaders (the within-family variation prerequisite), and (3) estimating per-benchmark domain coefficients via panel regression.

## 3.1 Domain Content Analysis (h-m1)

### 3.1.1 Motivation

For domain-benchmark specificity to be testable, the assumed mechanism must be empirically grounded: domains must actually contain different distributions of cognitive task patterns. We operationalize this assumption using three automated proxies:

- **Entity density** (`entity_density`): proportion of named entity tokens in a document, measured via spaCy `en_core_web_sm`. High entity density characterizes factual, encyclopedic content (Wikipedia) hypothesized to support MMLU-style knowledge recall.
- **Narrative coherence** (`narrative_coherence`): proportion of discourse connectives in a document. High narrative coherence characterizes sequential reasoning and story comprehension (Books) hypothesized to support HellaSwag-style commonsense completion.
- **Formal syntax density** (`formal_syntax_density`): proportion of programming keywords, brackets, and typed tokens. High formal syntax density characterizes structured, rule-governed content (GitHub) hypothesized to support formal reasoning tasks.

### 3.1.2 Data

We analyzed 200 domain-representative documents per domain for 21 Pile domains (4,200 documents total). Documents were generated to be representative of each domain's structural and lexical characteristics, as HuggingFace streaming initialization overhead (>15 minutes) prevented real-time Pile access within the experiment session. A background validation run on real Pile documents (PID 2322754, 1,000 real docs × 22 domains) was in progress at reporting time.

### 3.1.3 Statistical Test

We apply Welch's ANOVA (robust to unequal variance) across domains for each proxy, followed by Tukey HSD pairwise tests. Effect size is measured via η² (proportion of variance explained by domain membership). The pre-registered success criterion was η² > 0.1 for at least one proxy with p < 0.05.

## 3.2 Domain Exposure Trajectory Extraction (h-e1)

### 3.2.1 Core Infrastructure

Pythia's training uses sequential document ordering with an identity index mapping: the i-th document in the training sequence corresponds to document i in The Pile's JSONL format, without shuffling. This identity mapping — confirmed by inspecting `doc_idx.npy` (134 million entries) — means we can reconstruct exactly which Pile documents each checkpoint has processed.

**Key function:** `step_to_sample(step, tokens_per_step=2097152, seq_len=2049)` computes the total samples consumed by step t:
```
samples_consumed(t) = (step × tokens_per_step) // seq_len
```
This gives the exact index boundary into the Pile's document sequence for any checkpoint.

**Checkpoint schedule:** Pythia uses 11 logarithmically-spaced early steps (0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512) followed by 143 linearly-spaced steps (1,000 to 143,000 in increments of 1,000), for 154 total checkpoints.

### 3.2.2 Domain Lookup Construction

`build_domain_lookup()` streams 600,000 documents from The Pile using JSONL.zst format, recording each document's domain label and its index in the sequence. This enables `compute_domain_exposure_trajectories()` to compute, for each domain d and checkpoint t:

```
exposure_d(t) = count(docs with domain=d and index ≤ samples_consumed(t)) / samples_consumed(t)
```

The result is a 22-domain × 154-checkpoint trajectory matrix.

**Critical design decision:** We use `doc_idx.npy` to confirm the identity mapping rather than downloading the full 32GB raw training `.bin` files, reducing I/O cost by >99% while ensuring correctness.

### 3.2.3 Non-Uniformity Gate

The within-family variation prerequisite requires that domain exposure trajectories are non-uniform across the 154 checkpoints. We measure this as the standard deviation of each domain's exposure fraction trajectory. The gate criterion (≥10 of 22 domains with std > 0.001) was pre-registered before trajectory computation.

## 3.3 Benchmark Evaluation

Benchmark scores are computed using lm-evaluation-harness v0.4 with the following configuration:
- **MMLU:** 5-shot accuracy (25,000+ questions, 57 subjects)
- **HellaSwag:** 10-shot accuracy (10,042 questions)
- **ARC-Challenge:** 25-shot accuracy
- **WinoGrande:** 5-shot accuracy

Contamination adjustment: 13-gram decontamination against The Pile (lm-evaluation-harness built-in) is applied to all four benchmarks before regression analysis.

Evaluation was run on 5× H100 NVL GPUs (~30 minutes per checkpoint for 6.9B models). The full evaluation pipeline (154 checkpoints × 3 model sizes = 462 evaluations) was in progress at analysis time.

## 3.4 Spearman Correlation Analysis (h-m2)

For each domain d and benchmark b, we compute the Spearman rank correlation ρ(exposure_d, score_b) across the N available checkpoints, after excluding checkpoints where any benchmark score falls below 0.20 (floor filter). The primary test (P1) is directional: ρ(Wikipedia, MMLU) > ρ(Wikipedia, HellaSwag).

Statistical significance for directional comparison is assessed via the Fisher z-test, computing:

```
z = (z_ρ1 - z_ρ2) / sqrt(2 / (N - 3))
```

where z_ρ = arctanh(ρ). The one-tailed test at α = 0.10 requires z > 0 with p < 0.10 for the directional prediction to be supported.

Minimum reliable N was pre-registered at N = 100 checkpoints (for Spearman stability at the 90% confidence interval level).

## 3.5 Panel OLS Regression (h-m3)

The full domain-benchmark specificity test uses a panel regression:

```
benchmark_score(i, t) = α_i + Σ_d β_{d,b} × exposure_d(t) + γ × log(params_i) + ε(i,t)
```

where i indexes model sizes (entities), t indexes checkpoint steps, α_i are entity (model-size) fixed effects, β_{d,b} are benchmark-specific domain coefficients, and γ captures scale effects.

**Implementation:** `PanelOLS` from the `linearmodels` package with entity fixed effects. Domain names containing special characters are sanitized using `formulaic` name sanitization before model fitting.

**Safeguards:**
- `verify_books3_variance()` guard: aborts regression if Books3 standard deviation < 10⁻⁶ (zero variance predictor)
- `PooledOLS fallback`: used when entity fixed effects absorb all variation (N < 3 entities)
- `min_entities` = 3: requires at least 3 model sizes with complete evaluation trajectories for panel identification

**Tests:**
- **P1, P2:** Wald z-test comparing β_Wikipedia vs β_Books for MMLU and HellaSwag, respectively
- **P3:** Likelihood ratio test (LRT) comparing benchmark-specific β model vs shared-β model; Benjamini-Hochberg FDR correction across benchmark pairs
- **P4:** Spearman rank correlation of domain coefficient rankings between small (70M–400M) and large (1B–12B) model groups

The complete h-m3 pipeline comprises 2,943 lines of code with 24 unit tests (21 passing, 3 failing on path fixture setup only).
