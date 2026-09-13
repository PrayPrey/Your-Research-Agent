# Related Work

## Uncertainty Quantification for Language Models

Uncertainty quantification in LLMs spans two broad paradigms distinguished by their information source: output-space methods that operate on generated text or logit distributions, and representation-space methods that interrogate internal model states.

**Token-probability methods** use the model's predicted probability distribution as a proxy for confidence. Negative log-probability and maximum softmax probability are standard baselines [Malinin and Gales, 2021; Kadavath et al., 2022]. Despite their simplicity, these methods demonstrate robust performance: Farquhar et al. (2024) report token-probability AUROC of ~0.67 on TriviaQA for Llama-2-70B, and our experiments replicate this with 0.6835 on Llama-3-8B-Base. Token-probability is valid under any sampling regime and requires only a single forward pass—properties we show are critical when sampling diversity is low.

**Sampling-based semantic methods** were introduced to overcome a limitation of token-probability: sensitivity to superficial lexical variation that does not reflect genuine epistemic uncertainty. *Semantic entropy* (SE) [Farquhar et al., 2024] clusters N stochastic responses into semantic equivalence classes via bidirectional NLI and computes entropy over cluster probability mass. Evaluated on Llama-2 variants (including instruction-tuned), TriviaQA, NQ, BioASQ, and SQuAD, SE achieves AUROC of 0.72–0.79 and establishes itself as the state of the art for sequence-level uncertainty. *Kernel Language Entropy* (KLE) [Nikitin et al., 2024] generalizes SE via von Neumann entropy over a semantic similarity kernel matrix, providing a theoretically unified framework that subsumes SE and clustering-free alternatives. Both SE and KLE depend on semantic diversity among the N samples: without diverse clusters, entropy collapses.

*Semantic Entropy Probes* (SEPs) [Kossen et al., 2024] approximate SE from a single forward pass using linear classifiers on hidden-state representations, achieving 5–10× speedup with comparable AUROC. Their evaluation uses Llama-2 variants on TriviaQA and NQ, but degenerate_fraction of the sampling distribution is not reported—leaving the diversity precondition implicit. This work is directly complementary to ours: if SE is invalid in the base-model regime, SEP approximations of SE inherit the same invalidity.

*SelfCheckGPT* [Manakul et al., 2023] takes a different approach: it measures consistency across N samples using NLI, BERTScore, or n-gram overlap, treating inconsistency as a hallucination signal. Evaluated primarily on GPT-3 outputs (WikiBio generation), SelfCheckGPT-NLI achieves strong performance. Our results unexpectedly show that SelfCheckGPT-NLI remains competitive with token-probability (AUROC=0.6862) even under high degeneracy—because NLI-based entailment detection exploits subtle paraphrase variations among the 11% of diverse queries, providing sufficient discriminative signal without requiring the clustering structure that SE requires.

**The sampling diversity assumption.** A consistent thread in SE and SelfCheckGPT evaluations is that the model produces semantically non-trivial variation across N=10 samples. This is reliable for instruction-tuned models: RLHF encourages varied response styles, and GPT-3/GPT-4-class models produce measurable semantic diversity on factual queries. For *base* models—optimized purely on next-token prediction—factual recall queries trigger near-deterministic behavior: the model assigns concentrated probability mass to a single answer sequence, producing near-identical samples. To our knowledge, no prior work has measured degenerate_fraction as an explicit diagnostic or evaluated SE validity as a function of sampling diversity.

## Representation-Based Uncertainty

Beyond sampling, internal model representations carry uncertainty signal. *Layer-wise Semantic Dynamics* (LSD) [Mir, 2025] trains contrastive representations aligned with factual encoders, achieving AUROC=0.96 on TruthfulQA. *Effective Rank-based Uncertainty* [Wang et al., 2025] uses spectral rank of hidden-state matrices without additional supervision. *HaluNet* [Tong et al., 2025] combines token-level probability with internal semantic representations. These methods bypass the sampling diversity requirement entirely, but require training additional probes or modules—limiting zero-shot applicability.

## Surveys and Meta-Analyses

Kang et al. (2025) survey 100+ UQ methods for LLMs and identify *evaluation fragmentation* as the field's primary limitation: methods are evaluated on different models, datasets, metrics, and splits, making cross-paper comparisons unreliable. Our work addresses a complementary fragmentation: the conflation of base and instruction-tuned models as equivalent evaluation targets for sampling-based methods. The degenerate_fraction metric we introduce provides a concrete operationalization of this fragmentation axis.

## Conformal Prediction

Cherian et al. (2024) and Su et al. (2024) apply conformal prediction to LLMs to provide statistical coverage guarantees on hallucination detection. These methods do not rely on semantic diversity and are orthogonal to our analysis; they represent a complementary approach to uncertainty-aware deployment that should remain valid across sampling regimes.

## Positioning of This Work

We do not challenge SE's validity in general. Our contribution is to *identify and operationalize the validity boundary*: SE and KLE require sampling diversity (degenerate_fraction < threshold) to function as uncertainty estimators. Published evaluations have implicitly operated within the valid regime by using instruction-tuned models; applying these methods to base models requires explicit diversity verification. This is a calibration and methodology contribution for the field's benchmarking practices, not a critique of the methods' theoretical foundations.
