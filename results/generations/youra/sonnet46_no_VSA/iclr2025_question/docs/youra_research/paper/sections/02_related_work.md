# Related Work

Our work sits at the intersection of three active areas: consistency-based uncertainty quantification, token log-probability signals for hallucination detection, and LM-as-a-judge evaluation methodology. We review each in turn, highlighting how our contribution bridges gaps that prior work leaves open.

## Consistency-Based Uncertainty Quantification

Self-consistency as a reliability signal was established by Wang et al. [2022], who showed that sampling N outputs and selecting the most frequent answer reliably improves reasoning task performance — demonstrating that output diversity correlates with uncertainty. Manakul et al. [2023] operationalized this as SelfCheckGPT: a black-box hallucination detection method that scores consistency across N samples using NLI-based contradiction detection, BERTScore, or n-gram overlap. The NLI variant achieves NonFact AUC-PR of 92.50 vs. 83.21 for log-probability signals on WikiBio, establishing that consistency-based signals outperform log-prob signals in document generation tasks.

The foundational formalization of consistency-based UQ is Semantic Entropy (SE) [Kuhn et al., 2023], which defines uncertainty as the entropy over semantic equivalence classes: H(p(C|x)) = −Σ_C p(C|x) log p(C|x), where p(C|x) = Σ_{s∈C} p(s|x) sums token probabilities of all outputs in the same NLI-defined cluster. This formulation explicitly avoids conflating lexical variation with semantic uncertainty — two paraphrases of the same fact produce low entropy despite surface-level differences. Kuhn et al. demonstrate that SE outperforms raw token entropy on TriviaQA and BioASQ. Our work directly builds on this formulation (N=5, bidirectional DeBERTa-MNLI NLI clustering per Kuhn et al. Eq. 3).

More recent work extends SE to address its limitations in longer-form generation. Nguyen [2025] (SNNE) introduces pairwise SE computation to handle multi-sentence answers where the original SE formulation weakens. This directly motivates our scope restriction to short-answer factual QA (TriviaQA, ≤50 token answers), where original SE remains the strongest consistency-based signal. Bouchard et al. [2025] (UQLM) benchmark 50+ UQ methods across 24 model-dataset combinations and find that NLI-based black-box scorers are best in 13/24 AUROC scenarios — providing strong external validation that SE-family signals are competitive at the benchmark level.

**Gap:** None of these works directly measure the Pearson correlation between SE and min\_logprob on open-weight LLMs. They report standalone AUROC comparisons, not cross-signal statistical independence. Our work closes this gap.

## Token Log-Probability Signals for Hallucination Detection

Token log-probabilities are the most computationally efficient UQ signal class, requiring only a single forward pass. Malinin and Gales [2021] formalize sequence-level uncertainty measures from log-probabilities. Min\_logprob (the minimum token log-probability over a greedy decode path) captures the model's "weakest link" — the single token where it was least confident — and has been empirically shown to achieve AUROC ~0.825 on TriviaQA dev with Llama-3.1-8B [prior work in this pipeline].

The relationship between first-token confidence and SE was characterized by Slobodkin et al. [2025] (arxiv 2605.05166), who find r = 0.54–0.76 between first-token probability and semantic agreement in Llama-3.1-8B, TriviaQA — suggesting that for first-token signals, moderate correlation with SE exists. A critical distinction: min\_logprob is NOT first-token confidence. It is the minimum over ALL tokens in greedy decode, including arbitrarily late positions. This operational difference drives near-zero Pearson r in our measurements (|r| = 0.049).

Raghuvanshi et al. [2025] combine token log-probability, NLI, and SE signals into a hybrid scoring system achieving AUC 0.818 on SQuAD2.0, demonstrating that multi-signal ensembles are competitive. However, they do not report the cross-signal independence structure that would justify the ensemble — a gap our work addresses directly. Dey et al. [2025] (UAF Ensemble) show that fusing UQ signals improves factual accuracy by 8%, further motivating the ensemble direction we characterize the independence foundation for.

**Gap:** No prior work directly measures the statistical independence of min\_logprob (not first-token, not mean) and SE on open-weight LLMs under a controlled evaluation protocol. Our |r|=0.049 measurement fills this gap.

## LM-as-a-Judge Evaluation Methodology

Accurate hallucination detection evaluation requires reliable correctness labels. Santilli et al. [2025] (ACL 2025) show that AUROC rankings for hallucination detection methods are systematically distorted by response length bias — ROUGE-L evaluation is most severely affected (Spearman |ρ| up to 0.9 between length and correctness label). They recommend LM-as-a-judge with cross-model design as the most human-aligned correctness function, and note that OLS residualization can partially correct length bias in log-prob signals.

Xiong et al. [2023] benchmark verbalized confidence, black-box UQ methods, and internal state methods across multiple LLMs, finding that consistency-based signals are the most reliable black-box UQ method overall. We implement their cross-model judge recommendation directly: Qwen-2.5-7B-Instruct evaluates Llama-3.1-8B-Instruct outputs on TriviaQA dev, preventing shared model-specific biases from producing circularity between the SE signal (which uses NLI-based semantic reasoning) and the judge (which also applies semantic reasoning to evaluate correctness).

Our Spearman ρ(SE, judge) = −0.081 directly validates this design choice: the circularity threshold of |ρ| < 0.40 is satisfied with substantial margin, confirming that SE scores do not circularly predict judge labels when the cross-model design is applied.

**Our Position:** We do not replace any of these prior contributions — we complement them by characterizing the cross-signal statistical relationship (SE vs. min\_logprob independence) that justifies their combination in an ensemble, using the evaluation best practices (cross-model LM-judge, length-aware evaluation) that prior work has established.
