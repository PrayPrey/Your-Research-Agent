# 4. Experimental Setup

We design our experiments to answer four research questions, each corresponding to a validated sub-hypothesis in our sequential verification design.

**RQ1:** Is k=5 self-contained tier stratification viable — does it produce n≥20 problems per tier per model-benchmark pair?

**RQ2:** Are difficulty tier assignments consistent across model architectures (Jaccard > 0.30)?

**RQ3:** Does P(True) logprob extraction produce non-degenerate confidence distributions (std(c) > 0.05) for all three models?

**RQ4:** Does ΔECE = ECE(hard) − ECE(easy) differ by architecture, and does global temperature scaling correct the pattern?

Each RQ tests a necessary condition: RQ1–RQ3 validate infrastructure; RQ4 tests the core calibration hypothesis.

## 4.1 Datasets

We evaluate on **EvalPlus** [Liu et al., 2023], comprising:
- **HumanEval+** (164 problems): augmented with 80× more test cases compared to the original HumanEval [Chen et al., 2021]
- **MBPP+** (378 problems): augmented with 35× more test cases compared to the original MBPP [Austin et al., 2021]
- **Total:** 542 unique code generation problems across both benchmarks

**Why EvalPlus.** EvalPlus's augmented test suites reduce pass@k inflation present in the original benchmarks — HumanEval inflation is 28.9% on average. More reliable correctness oracles are essential for accurate ECE computation: false positive pass rates would inflate easy-tier ECE artificially, masking genuine calibration differences.

We analyze each benchmark independently and combined. When a model's easy tier is viable on only one benchmark (as with CodeLlama on HumanEval+, where n_easy=0), we use the viable benchmark as the primary tier assignment source.

## 4.2 Models

We evaluate three base LLMs at 7–8B parameter scale:

| Model | Parameters | Training | Tier Category |
|-------|-----------|----------|---------------|
| NousResearch/Meta-Llama-3-8B | 8B | General-purpose pre-training | General |
| codellama/CodeLlama-7b-hf | 7B | Code fine-tuning on Llama base | Code-adapted |
| deepseek-ai/deepseek-coder-6.7b-base | 6.7B | Code-specialized pre-training | Code-specialized |

All models are base (not instruction-tuned) variants to isolate pre-training calibration signals from RLHF/SFT effects.

## 4.3 Baselines and Comparisons

**Null baseline (RQ4).** We construct a Monte Carlo Bernoulli null model: draw confidence values from the model's empirical c distribution and assign correctness independently (n_sim=100,000). This tests whether observed ΔECE exceeds what would be expected if confidence and correctness were uncorrelated.

**Temperature scaling (RQ4).** We apply global temperature scaling [Guo et al., 2017] as a standard post-hoc calibration baseline: fit T* on 20% holdout (negative log-likelihood minimization), then recompute ΔECE on the remaining 80% with c/T* as confidence. This tests whether architecture-dependent ΔECE survives the most widely used calibration correction.

**M-sensitivity.** We recompute all ECE values for M ∈ {10, 15, 20} bins to verify that ΔECE direction is not an artifact of bin count selection.

## 4.4 Implementation Details

**Hardware.** Solution generation (h-e1) was performed on a single NVIDIA H100 GPU. P(True) extraction (h-m3) ran in ~4 minutes for 5,730 (problem, solution) pairs per model on H100. ECE computation (h-m4) is CPU-only: numpy/scipy, < 1 second for all models.

**Solution generation.** We use HuggingFace `transformers` with temperature=0.8, top_p=0.95, max_new_tokens=512. Each problem generates k=5 independent solutions with different random seeds.

**EvalPlus evaluation.** We use the EvalPlus Python API (`evalplus.evaluate`) to check solution correctness against augmented test suites. Coverage is verified to be 1.0000 for all model-benchmark combinations.

**P(True) extraction.** Zero-shot prompt: `{problem}\n\n{solution}\n\nIs the above solution correct? (True/False)`. Confidence c = softmax(logprob("True"), logprob("False")).

**ECE computation.** M=15 equal-width bins; bootstrap n=1,000 samples (seed=42); 95% CI as the 2.5th and 97.5th bootstrap percentiles.

**Reproducibility.** All code is organized into per-hypothesis source modules (`src/h_e1/`, `src/h_m1/`, ..., `src/h_m4/`) with full test coverage (26/26 tests passing for h-m4).

## 4.5 Evaluation Metrics

**Primary.** ΔECE = ECE(hard) − ECE(easy) with 95% bootstrap confidence interval. Positive ΔECE with CI excluding zero indicates significantly worse calibration on hard problems.

**Secondary.** (a) Jaccard similarity of tier assignments across model pairs (cross-architecture consistency). (b) Bootstrap p-value (fraction of bootstrap samples with ΔECE ≤ 0 for positive primary hypothesis). (c) Post-T* ΔECE (temperature scaling probe).

**Gate criteria.** ΔECE ≥ 0.03 AND CI lower bound > 0 in ≥2/3 model families (h-m4 MUST_WORK gate). This threshold was pre-registered in the Phase 2B verification plan.
