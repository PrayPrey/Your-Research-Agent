# Experimental Setup

We design our experiments to answer five research questions that directly correspond to the claims in the Introduction:

**RQ1 (Existence):** Does semantic entropy outperform token entropy by a practically meaningful margin (≥ 0.05 AUROC) at Llama-2-7B scale on TriviaQA? *(Tests P1; Contribution 1)*

**RQ2 (Mechanism):** Is the SE > TE gap explained by intra-cluster TE variance — token entropy varying within semantically equivalent paraphrase groups? *(Tests mechanism; Contribution 2)*

**RQ3 (Scope):** Does the SE > TE advantage generalize to TruthfulQA, an adversarial misconception benchmark? *(Tests cross-benchmark; Contribution 3)*

**RQ4 (SCG Equivalence):** Is BERTScore-based SelfCheckGPT equivalent to SE (AUROC gap ≤ 0.03) on short factual QA? *(Tests P2)*

**RQ5 (VC Calibration):** Is verbalized confidence at 7B scale miscalibrated as measured by ECE? *(Tests P3)*

## Datasets

| Dataset | N | Task | Incorrect-Output Structure | Role in Study |
|---------|---|------|---------------------------|---------------|
| TriviaQA dev | 98 | Open-domain factual recall | Paraphrase-diverse | Primary evaluation (RQ1, RQ2, RQ4, RQ5) |
| TruthfulQA | 141 | Adversarial misconception | Deterministic-wrong | Cross-benchmark generalization (RQ3) |

**TriviaQA** (Joshi et al., 2017) is selected as the primary evaluation dataset because it provides open-domain factual recall questions where incorrect model outputs typically take diverse surface forms — a wrong answer for "What is the capital of X?" may appear in many paraphrasings. Correctness is determined by alias-normalized exact match against TriviaQA's reference alias lists, which handles surface variation in correct answers. N=98 is selected by random seed 42.

**TruthfulQA** (Lin et al., 2022) is selected as the cross-benchmark test precisely because it is designed to elicit confident, consistent wrong answers — adversarial misconceptions that models have absorbed from training data and consistently repeat. This makes TruthfulQA the natural contrast case for the task-structure hypothesis: if incorrect outputs are deterministically wrong (low diversity), SE's paraphrase-noise filtering advantage should disappear. N=141 questions with yes/no prefix matching for correctness labels.

The TriviaQA/TruthfulQA pair is a controlled contrast on the diversity structure of incorrect outputs, not an arbitrary choice of two benchmarks.

## Baselines and Methods

All four methods receive the same K=10 stochastic samples at temperature 0.7, max_new_tokens=50, from Llama-2-7B (or Llama-2-7B-Chat for VC). This shared-condition design eliminates sample quality, sample count, and prompt format as confounds.

| Method | Computation | External Model | Samples Required |
|--------|-------------|----------------|-----------------|
| Token Entropy (TE) | Mean per-token Shannon entropy, greedy decode | None | 0 (single forward pass) |
| Semantic Entropy (SE) | NLI clustering + logsumexp entropy | nli-deberta-v3-large | K=10 |
| SelfCheckGPT BERTScore (SCG) | 1 − mean BERTScore consistency | BERTScore model | K=10 |
| Verbalized Confidence (VC) | Self-reported 0-100% confidence | None (prompt-based) | 0 (single forward pass) |

**Token Entropy (TE)** serves as the primary comparison baseline because it is the simplest sampling-free method and the method SE is theoretically designed to improve upon via paraphrase-noise filtering. It represents the "efficiency-first" choice that practitioners might prefer given zero additional inference cost.

**Semantic Entropy (SE)** is the method under primary evaluation. Its computational overhead relative to TE — K=10 additional samples plus NLI model inference — is the cost the paraphrase-noise filtering advantage must justify.

**SelfCheckGPT BERTScore (SCG)** is included as an alternative semantic-level method. If SCG achieves SE-equivalent AUROC, it provides a lower-compute alternative to SE (BERTScore is faster than NLI inference). If not, the comparison characterizes when BERTScore-based consistency fails as a semantic proxy.

**Verbalized Confidence (VC)** is included to characterize the 7B-scale meta-cognitive calibration baseline. It requires no additional samples but a different model variant (Llama-2-7B-Chat).

## Implementation Details

**Model:** meta-llama/Llama-2-7b-hf (float16, device_map="auto") for TE/SE/SCG; meta-llama/Llama-2-7b-chat-hf for VC.

**NLI model:** cross-encoder/nli-deberta-v3-large for TriviaQA experiments; cross-encoder/nli-deberta-v3-small for TruthfulQA (H-C1). The model size difference between TriviaQA and TruthfulQA experiments is a limitation documented in Section 6.

**Sampling configuration:** temperature=0.7, K=10 samples, max_new_tokens=50, no repetition penalty.

**Exact match:** TriviaQA alias list normalization (lowercase, strip articles and punctuation); TruthfulQA yes/no prefix matching.

**Score convention:** All uncertainty scores are negated before AUROC computation (higher uncertainty = higher score = higher probability of incorrect). This convention, following Kuhn et al. [2023], is applied uniformly in H-E1. Pipeline variations (H-M3, H-M4) that omit this negation produce inverted SE AUROC values; we document and correct for this in Section 5.

## Evaluation Metrics

**AUROC** (Area Under the ROC Curve) measures the probability that a randomly chosen incorrect answer has a higher uncertainty score than a randomly chosen correct answer. AUROC = 0.5 indicates chance-level discrimination; AUROC = 1.0 is perfect discrimination. Bootstrap 95% confidence intervals (n=1000 iterations, stratified resampling, seed=42) are computed for all AUROC estimates. We use non-overlapping CIs as the primary significance criterion.

**ECE** (Expected Calibration Error, 10-bin adaptive binning) measures the gap between stated confidence and empirical accuracy for verbalized confidence. ECE = 0 indicates perfect calibration; higher values indicate miscalibration.

**Gate criteria (pre-specified):**
- RQ1: SE-TE gap ≥ 0.05 AUROC with non-overlapping 95% CIs (MUST_WORK)
- RQ2: Mean intra-cluster TE variance > 0.1 nats² on ≥15 questions (MUST_WORK)
- RQ3: SE AUROC > TE AUROC on TruthfulQA (SHOULD_WORK — hypothesis fails if reversed)
- RQ4: |SCG AUROC − SE AUROC| ≤ 0.03 (SHOULD_WORK — hypothesis fails if divergent)
- RQ5: VC AUROC < TE AUROC (SHOULD_WORK — hypothesis fails if equal or exceeds)
