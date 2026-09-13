# Related Work

Our work connects to three research areas: semantic entropy for hallucination detection, probe-based uncertainty quantification, and the broader challenge of efficient uncertainty estimation in LLMs.

## Semantic Entropy

Farquhar et al. introduced semantic entropy (SE) as a principled measure of uncertainty that accounts for semantic equivalence among generated responses. Unlike lexical measures that treat "Paris" and "The capital of France is Paris" as different answers, SE clusters semantically equivalent responses using natural language inference and computes entropy over these clusters. This approach achieves AUROC 0.76-0.97 for hallucination detection across TruthfulQA, TriviaQA, and other benchmarks, establishing SE as the gold standard for LLM uncertainty quantification.

However, SE computation requires generating N=10-20 diverse responses per query (temperature sampling), embedding each response, and performing O(N²) pairwise entailment checks via a DeBERTa-v3 NLI model. This 5-10x computational overhead relative to single-pass inference prohibits deployment in latency-sensitive applications.

## Probe-Based Uncertainty Estimation

To address SE's computational burden, Kossen et al. proposed Semantic Entropy Probes (SEPs)—lightweight linear classifiers trained on LLM hidden states to predict SE labels. The key insight is that hidden states may encode uncertainty information that can be extracted without multiple generations. SEPs achieve AUROC within 2-3% of full SE on TruthfulQA while requiring only a single forward pass.

SEPs extract hidden states from specific layers (typically middle-to-late, e.g., layer 25 of 32 in Llama models) and token positions (Token-Before-Generation or Selected-Layer-Token). A logistic regression probe then maps these high-dimensional representations to SE predictions. The approach assumes SE-relevant information is encoded in hidden states at these positions—an assumption our work challenges.

Related work on probing LLM representations includes uncertainty quantification via attention patterns and pre-trained UQ heads. These methods share the goal of cheap uncertainty estimation but differ in what representations they probe and how they train classifiers.

## Efficient Uncertainty Alternatives

Beyond probing, researchers have explored alternative efficient uncertainty measures. First-token entropy uses the entropy of the initial token distribution as a proxy for response uncertainty. However, this signal operates at the token level and fails to capture semantic uncertainty—our prior work found rho = 0.13 correlation with true SE.

Kernel Language Entropy (KLE) offers a non-parametric alternative that constructs positive semidefinite kernels over response sets. While computationally more efficient than full SE, KLE still requires multiple generations. Its relevance to our work lies in demonstrating that similarity structure contains uncertainty information—the inspiration for our similarity-augmented SEDP approach.

Semantic Self-Distillation (SSD) trains a student model to mimic full SE predictions from a teacher, achieving efficient inference after distillation. This paradigm validates that SE information can be compressed, though SSD uses full model capacity rather than lightweight probes.

## Our Position

We are not proposing a superior uncertainty method. Instead, we document a significant failure of SE probing under a reasonable configuration. Published SEP results report AUROC ~0.85 on TruthfulQA; our careful replication achieves 0.52 (near random). This 39% gap reveals configuration sensitivity that the literature does not adequately address.

Our contribution is exposing failure modes that practitioners will encounter. Where prior work emphasizes successes, we characterize what happens when configurations do not align—information essential for reliable deployment.
