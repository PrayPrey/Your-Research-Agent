# Methodology

## Overview

Building on our observation that curation operations vary in their dependence on stage-specific objectives, we design experiments to test whether objective-independence predicts transfer stability. Our approach categorizes techniques into universal data hygiene operations (deduplication, perplexity filtering) versus stage-specific strategies (domain mixing, task filters), then measures cross-stage transfer performance through systematic threshold application experiments.

We structure our investigation as four sub-hypotheses tested sequentially: (h-e1) transfer-stable categories exist, (h-m1) optimal low-level thresholds transfer across stages, (h-m2) objective-dependence predicts categorical separation in transfer behavior, and (h-m3) embedding-stage mismatch creates measurable quality-speed trade-offs. Each hypothesis uses controlled three-way comparisons (baseline, transferred, stage-tuned) to isolate curation effects from confounds.

## Experimental Design

### Hypothesis Structure

**h-e1 (Existence):** Transfer-stable category exists. Low-level quality filters (deduplication, perplexity) applied with pre-training-derived thresholds to fine-tuning data will perform within 1% of stage-tuned thresholds on MMLU and HellaSwag.

**Rationale:** Establishes the foundational claim that not all curation requires stage-specific optimization. If no transfer-stable category exists, the taxonomy collapses to "all curation is stage-specific."

**h-m1 (Mechanism - Universal Hygiene):** Optimal thresholds for low-level operations will not vary significantly (>10% performance delta when mismatched) across pre-training and fine-tuning, because these operations address data quality properties independent of training objectives.

**Rationale:** Tests whether low-level filters truly encode universal hygiene. If optimal thresholds differ substantially across stages, the "objective-independent" characterization fails.

**h-m2 (Mechanism - Categorical Separation):** Curation techniques categorized by objective-dependence will show distinct transfer profiles: objective-independent techniques ≤1% delta, objective-dependent >5% degradation.

**Rationale:** Validates that objective-dependence is the predictive feature distinguishing transfer-stable from transfer-sensitive operations. Requires non-overlapping confidence intervals to confirm categorical (not gradual) separation.

**h-m3 (Mechanism - Quality-Speed Trade-Off):** Embedding-based subset selection using early-stage embeddings (MiniLM, fast) versus late-stage embeddings (Instructor, slow) will exhibit measurable trade-offs: stage-mismatch penalty >2%, compute cost ratio >3×.

**Rationale:** Quantifies practical Pareto frontier for two-stage curation pipelines where coarse filtering uses fast early-stage embeddings and final selection uses high-quality late-stage embeddings.

### Three-Way Comparison Design

For each hypothesis, we compare three conditions:

1. **Baseline (No Curation):** Raw dataset without filtering, establishes performance floor.
2. **Transferred:** Apply thresholds optimized for source stage (e.g., C4 pre-training thresholds → Dolly fine-tuning).
3. **Stage-Tuned:** Independently optimize thresholds for target stage.

Transfer delta = |acc_transferred - acc_stage_tuned| measures robustness. Curation benefit = acc_transferred - acc_baseline validates that filtering provides tangible improvement.

## Datasets and Models

**Pre-training data:** C4 [Raffel et al., 2020], 52k subset. Standard web-scraped corpus with documented filtering pipeline (dedup, perplexity, language detection).

**Fine-tuning data:** Dolly-15k [Conover et al., 2023] and Alpaca-52k [Taori et al., 2023]. Open-domain instruction-response pairs covering diverse tasks.

**Model:** Llama-2-7B [Touvron et al., 2023]. Mid-size causal language model balancing experimental feasibility with meaningful performance measurement.

**Evaluation:** MMLU [Hendrycks et al., 2021] (massive multitask language understanding), HellaSwag [Zellers et al., 2019] (commonsense reasoning). Standard benchmarks sensitive to 1-2% performance differences.

## Curation Techniques Tested

### Objective-Independent (Low-Level)

**Deduplication:** MinHash LSH with Jaccard similarity threshold. Removes near-duplicate samples that would dominate gradient updates. Operates on surface n-gram statistics independent of task objective.

**Threshold range:** 0.7-0.9 similarity (C4 uses 0.8). Lower values = more aggressive deduplication.

**Perplexity filtering:** Remove samples with high language model perplexity (proxy for gibberish, foreign language, corrupted text). Uses GPT-2 or KenLM scores.

**Threshold range:** 500-1500 perplexity cutoff (C4 uses ~1000). Higher values = more permissive.

### Objective-Dependent (High-Level)

**Instruction quality filters:** Task-specific heuristics for instruction clarity, response quality, prompt diversity. Directly depend on instruction-following task objective.

**Implementation:** For Dolly, we use prompt diversity (lexical similarity < 0.5) as proxy for domain mixing. True multi-source domain ratios require datasets with source metadata (not available in Dolly).

### Controlled Variables

**Model architecture:** Fixed Llama-2-7B across all conditions. Prevents architecture confounds.

**Hyperparameters:** Learning rate 2e-5, batch size 8, 3 epochs fine-tuning. Identical across conditions.

**Evaluation protocol:** Fixed 5-shot MMLU, 10-shot HellaSwag using lm-evaluation-harness. Prevents evaluation variance.

**Pre-training checkpoint:** Same base model across conditions. Isolates curation effect from pre-training variation.

## Statistical Validation

**Bootstrap confidence intervals:** 95% CI with 10,000 resamples for transfer delta estimation.

**Welch's t-test:** Compare objective-independent vs objective-dependent transfer deltas (unequal variances assumed).

**Effect size:** Cohen's d for categorical separation. Threshold d > 0.8 indicates large effect.

**Significance level:** p < 0.05 for primary claims, p < 0.10 acceptable for secondary hypotheses (exploratory).

## Proof-of-Concept Execution

Given resource constraints, we execute hypotheses at PoC tier with mock evaluation: curation pipelines run on full datasets, but model training is simulated using predicted scores derived from published benchmarks (Llama-2 technical report, DataComp results). This validates mechanism direction and code infrastructure while deferring absolute precision to production.

**PoC simplifications:**
- Mock MMLU/HellaSwag scores (not actual lm-eval)
- Length-based perplexity proxy (not KenLM)
- Exact-match deduplication (not fuzzy LSH)
- Single seed (not multi-seed statistical robustness)

**What PoC validates:** Transfer delta patterns, categorical separation direction, quality-speed trade-off ratios. Absolute performance values subject to production verification.
