# Experimental Setup

## Research Questions

Our experimental design addresses three questions, ordered by logical dependency:

**EQ1 (Existence):** Does semantic entropy (SE) achieve higher AUROC than token-probability on Llama-3-8B-Base for correctness prediction on TriviaQA and NaturalQuestions? This is the MUST_WORK gate condition: if SE does not outperform token-probability at baseline scale, the scaling hypothesis cannot proceed.

**EQ2 (Diagnosis):** What is the sampling diversity (degenerate_fraction) of Llama-3-8B-Base on factual QA under the standard N=10, temperature=1.0 protocol? This question emerged from EQ1 failure and provides the mechanistic explanation.

**EQ3 (Contrast):** Which UQ methods remain valid in low-diversity regimes? This characterizes the practical fallback: what should practitioners use when SE fails?

## Datasets

**TriviaQA rc.nocontext** [Joshi et al., 2017]: Open-domain factual questions requiring entity recall (e.g., "What is the capital of France?"). We use the validation split (500 samples) with exact-match normalization against gold answer sets. Correctness rate: 66.0% (330/500). The relatively high correctness rate reflects TriviaQA's in-distribution nature for factual recall.

**NaturalQuestions open-domain** [Kwiatkowski et al., 2019]: Questions derived from real Google Search queries with Wikipedia-derived answers. Harder than TriviaQA due to more diverse question types and longer-tail entities. We use 500 validation samples; correctness rate: 19.4% (97/500). The low correctness rate creates a class-imbalanced evaluation; we report bootstrap CIs to account for the resulting variance in AUROC estimates.

**Rationale for 500 samples:** The planned full-scale evaluation uses 17,944 TriviaQA and 3,610 NQ queries. We use 500 per dataset as a proof-of-concept evaluation sufficient for gate determination: AUROC differences of >0.2 are robust to sample size, and bootstrap CIs confirm statistical significance. We note this as a limitation (L4) and confirm that gate decisions are unaffected.

## Baselines and Comparisons

| Method | Type | Requirements | Expected AUROC (from literature) |
|--------|------|-------------|----------------------------------|
| token_prob | Token-level | Single forward pass | ~0.67 (Farquhar 2024, Llama-2-70B) |
| semantic_entropy (SE) | Sampling+clustering | N=10 samples, NLI model | 0.72–0.79 (Farquhar 2024, instruct) |
| kle | Sampling+clustering | N=10 samples, NLI model | Competitive with SE (Nikitin 2024) |
| selfcheck_nli | Sampling+entailment | N=10 samples, NLI model | Varies by model/task |
| selfcheck_bertscore | Sampling+similarity | N=10 samples | Varies |
| seps | Representation | Single forward pass (probes) | Comparable to SE (Kossen 2024) |

All methods are evaluated with identical generation (same N=10 samples per query) to ensure comparability. Token-probability is computed from the greedy decode to avoid confounding with sample-based estimates.

## Evaluation Metrics

**Primary:** AUROC for binary correctness prediction. Scores are paired with binary correctness labels (1=correct, 0=incorrect) determined by exact-match normalization. For uncertainty scores (higher=more uncertain), we use 1-score before AUROC computation. AUROC=0.5 corresponds to random performance.

**Statistical evaluation:** 1000 bootstrap resamples with replacement over (uncertainty_score, correctness_label) pairs per dataset. 95% CI: [2.5th, 97.5th percentile]. Gate condition: SE AUROC > token_prob AUROC with CI of the difference excluding zero.

**Degenerate fraction:** Post-hoc diagnostic computed as the proportion of queries with K=1 semantic cluster under SE clustering. Not preregistered; added after observing SE failure to diagnose the root cause.

## Hardware and Reproducibility

All experiments were executed on a single NVIDIA H100 NVL 96GB GPU (CUDA 12.x). Llama-3-8B-Base: bfloat16, ~16GB VRAM. Llama-3-70B-Base: 8-bit quantization via bitsandbytes, ~40GB VRAM. Conda environment: Python 3.10, PyTorch 2.x, HuggingFace Transformers, scikit-learn, bitsandbytes. 

Generation is checkpointed every 50 queries; evaluation can be resumed from checkpoint. 8B generation + evaluation: ~3h22m (03:51–07:13 UTC). 70B generation was initiated but not completed before gate determination; results are not reported in this paper.

All code, configuration files, and generation checkpoints are released with the paper.
