# Related Work

## Uncertainty Estimation in LLMs

Detecting when language models hallucinate requires reliable uncertainty estimation. Token-level entropy — the average entropy of next-token distributions — provides a simple baseline but achieves only AUROC 0.52–0.65 [Kadavath et al., 2022], barely above chance. The key insight of semantic entropy [Farquhar et al., 2024] is that uncertainty should be measured at the meaning level: sample multiple outputs, cluster them by semantic equivalence using natural language inference, and compute entropy over clusters. This approach achieves AUROC 0.75–0.90 on TruthfulQA but requires 5–10 forward passes per query.

Ensemble methods extend this further. UQLM [Vasilev et al., 2025] combines multiple uncertainty scorers — including semantic entropy, token entropy, and verbalizations — achieving state-of-the-art detection. However, ensemble overhead compounds the multi-sample cost, limiting deployment to offline applications.

## Probing Hidden States

An alternative to sampling-based methods is probing: train a classifier on model hidden states to predict properties of interest. Probing has revealed that transformers encode syntactic structure [Hewitt and Manning, 2019], factual knowledge [Petroni et al., 2019], and truthfulness [Azaria and Mitchell, 2023]. Linear probes suffice for many properties, suggesting the underlying representations are approximately linear.

Semantic Entropy Probes [Kossen et al., 2024] apply this insight to uncertainty. By training a logistic regression on hidden states to predict binarized semantic entropy, SEPs achieve AUROC competitive with multi-sample estimation while requiring only a single forward pass. Recent work [arxiv 2606.02628] confirms that truthfulness is linearly decodable from mid-layer hidden states, with peak performance at layer 2/3 depth across model families.

However, existing SEP work tests limited model configurations. The original paper [Kossen et al., 2024] validates on a narrow set of models; subsequent studies focus on scaling within families rather than transfer across them. The critical question — whether a probe trained on Llama works on Mistral — remains unanswered.

## Cross-Model Transfer

Representation transfer between neural networks is well-studied in vision [Yosinski et al., 2014] and increasingly in language. Model stitching [Lenc and Vedaldi, 2015; Chen et al., 2025] demonstrates that intermediate representations can be mapped between models via learned transformations. Recent work [Kim et al., 2026] shows that models trained on the same benchmark develop similar representation subspaces, with Gram matrix cosine similarity of 0.87 suggesting transferable structure.

These findings suggest that transfer might succeed for uncertainty probes, but the specific case of SEPs across LLM families has not been tested. Our work bridges this gap, providing the first systematic study of cross-family probe transfer for hallucination detection.

## Our Position

We build on the efficiency of SEPs [Kossen et al., 2024] and the transferability insights from model stitching [Chen et al., 2025]. Unlike prior work that validates probes within individual models, we test transfer across three distinct LLM families (Meta, Mistral AI, Alibaba). Our affine alignment approach directly implements the least-squares mapping from Chen et al. [2025], but applies it to uncertainty estimation rather than task transfer. The result is a single probe that serves multiple model families without retraining.
