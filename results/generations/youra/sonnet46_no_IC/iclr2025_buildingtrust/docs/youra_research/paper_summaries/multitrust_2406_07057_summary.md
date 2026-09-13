# MultiTrust: A Comprehensive Benchmark Towards Trustworthy Multimodal Large Language Models

## Key Metadata
- **Authors:** Yichi Zhang et al.
- **Year:** 2024
- **Venue:** NeurIPS 2024 Datasets & Benchmarks
- **Core Contribution:** 5-dimensional trustworthiness benchmark for multimodal LLMs evaluating 21 models, revealing dimension-specific vulnerability patterns.

## Section Summaries

### Abstract
We introduce MultiTrust, the first comprehensive benchmark evaluating trustworthiness of multimodal large language models (MLLMs) across 5 dimensions: truthfulness, safety, robustness, fairness, and privacy. We evaluate 21 state-of-the-art MLLMs and find striking dimension-specific vulnerability patterns that differ across model families, demonstrating that trustworthiness cannot be characterized by a single score.

### Introduction & Motivation
Existing MLLM evaluations focus on visual understanding capabilities, leaving trustworthiness largely unstudied in the multimodal context. MultiTrust extends the text-only trustworthiness literature (TrustLLM, HELM) to multimodal models, where new attack surfaces (visual adversarial examples, cross-modal inconsistency) create novel trustworthiness challenges.

### Methodology
21 MLLMs evaluated including GPT-4V, Claude-3, Gemini Pro Vision, LLaVA variants (1.5/1.6, 7B/13B/34B), InstructBLIP, mPLUG-Owl, ShareGPT4V. 5 dimensions: Truthfulness (visual hallucination, factual accuracy), Safety (harmful instruction resistance), Robustness (visual adversarial perturbations), Fairness (demographic bias in visual reasoning), Privacy (sensitive information in images). For each dimension, multiple datasets and evaluation protocols. Scores normalized to [0,1] per model per dimension. Key analysis: radar charts show per-model profiles; dimension-specific vulnerability analysis shows which models fail on which dimensions.

### Experiments & Results
Key findings: (1) GPT-4V achieves highest overall trustworthiness but shows vulnerability on fairness; (2) Open-source models (LLaVA-1.6) show high robustness relative to safety scores — robustness-safety dimension dissociation; (3) Models with best truthfulness scores do not have best safety scores (ρ not computed but visually anti-correlated in Figure 4); (4) Larger models within LLaVA family improve truthfulness but safety improvement is non-monotonic; (5) Cross-dimension Spearman correlation matrix explicitly NOT computed — same gap as TrustLLM for text models; (6) Figure 4 radar chart shows visually distinct dimension profiles per model, suggesting dimensions are not perfectly correlated.

### Discussion & Conclusion
MultiTrust demonstrates that MLLM trustworthiness is multi-dimensional with distinct failure modes per dimension. The paper calls for "cross-dimension analysis to understand whether improving one dimension systematically trades off against others." This is the multimodal analogue of Gap 1 for text LLMs.

## Key Contributions
- First 5-dimension trustworthiness benchmark for 21 MLLMs
- Reveals dimension-specific vulnerability patterns (robustness-safety dissociation)
- Radar chart analysis shows non-uniform dimension profiles across models

## Potential Relevance
MultiTrust provides evidence that dimension-specific patterns (not captured by single scores) exist in multimodal settings. Its findings motivate Gap 1 for text LLMs: if visual radar charts show dimension dissociation, computing Spearman ρ across text trustworthiness dimensions would quantify this formally. The LLaVA family size scaling results (truthfulness improves, safety non-monotone) are the multimodal analogue of the inverse-scaling pattern noted in the CoT survey for text LLMs.
