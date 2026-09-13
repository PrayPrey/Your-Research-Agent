# Related Work

Our work builds on three streams of research: uncertainty estimation methods for language models, error detection and hallucination mitigation, and systematic evaluation of machine learning methods.

## Uncertainty Estimation Methods

**Semantic entropy** (Kuhn et al., 2023) introduced the idea of computing entropy over semantically equivalent model outputs rather than raw strings. Their key insight is that models can express the same meaning in multiple ways ("Paris", "the capital is Paris", "Paris, France"), and uncertainty should be measured over meanings, not strings. They validate this approach on natural language generation tasks, showing improved hallucination detection compared to simple token entropy. However, their work does not include an ablation study isolating the clustering contribution from the computational budget of multiple sampling—our key methodological contribution.

**Self-consistency** (Wang et al., 2022) samples multiple outputs and measures agreement, using the most common answer. Originally developed for chain-of-thought reasoning on mathematical and commonsense tasks, this method has shown substantial improvements in reasoning accuracy. Wang et al. demonstrate that sampling diverse reasoning paths and taking the majority vote outperforms greedy decoding. However, their work focuses on reasoning tasks rather than factual error detection, and does not analyze orthogonality versus other uncertainty methods—a gap our correlation analysis addresses.

**Verbalized confidence** (Kadavath et al., 2022) takes a fundamentally different approach: prompting models to self-report their confidence. They show that language models can provide calibrated confidence estimates when explicitly asked, with the provocative title "Language Models (Mostly) Know What They Know." Their analysis focuses on calibration properties but does not compare verbalized confidence to output-based methods like semantic entropy or characterize when each approach works best.

**Token probability methods** represent the traditional baseline, using metrics like entropy or variance over token-level probability distributions. These methods require access to model logits but are computationally efficient (single forward pass). Our work includes token variance as a controlled baseline to compare against sampling-based methods.

What distinguishes our contribution is the systematic comparison across methods with controlled experimental design. While each prior work validates its method in isolation, we design experiments that reveal mechanistic differences—particularly the ablation isolating clustering from sampling and the correlation analysis quantifying method independence.

## Error Detection and Hallucination Mitigation

The broader context for uncertainty estimation is detecting when language models produce factual errors or hallucinations. **TruthfulQA** (Lin et al., 2021) provides a benchmark for testing whether models generate truthful answers, focusing on common misconceptions where models might confidently produce false information. **Natural Questions** (Kwiatkowski et al., 2019) offers a large-scale factual question answering dataset including unanswerable questions—useful for testing whether models recognize knowledge gaps.

Recent work on hallucination detection has explored various approaches: fact-checking against knowledge bases (Rashkin et al., 2021), consistency checking across multiple generations (Manakul et al., 2023), and confidence estimation (Xiong et al., 2023). However, these works typically employ a single uncertainty method rather than systematically comparing alternatives or characterizing method-error-type interactions.

Our work contributes to this literature by providing the first controlled comparison of uncertainty methods on factual error detection, using standard benchmarks that represent different error types.

## Systematic Evaluation of ML Methods

Beyond uncertainty estimation specifically, our work connects to the broader methodological question of how to evaluate machine learning methods systematically. Recent meta-analyses have highlighted issues with inconsistent evaluation practices (Bouthillier et al., 2021), the importance of controlled baselines (Lipton & Steinhardt, 2019), and the need for mechanistic understanding over empirical horse-races (Hooker, 2021).

Our ablation study design follows best practices for isolating contributions: we control computational budget (both semantic entropy and ensemble baseline use K=10 samples), test on identical samples, and use the same model. This contrasts with comparisons where methods differ in both mechanism and computational cost, making it impossible to attribute differences to either factor alone.

The correlation analysis addresses a common gap in ML evaluation: assuming methods are redundant without quantitative evidence. By measuring pairwise correlations across uncertainty methods, we provide empirical grounding for claims about method independence—a technique applicable beyond uncertainty estimation to any domain with multiple competing approaches.

## Positioning Our Contributions

Our work differs from prior uncertainty estimation research in three key ways:

First, we prioritize **mechanistic understanding** over empirical comparison alone. The ablation study isolating clustering from sampling, and the correlation analysis quantifying method independence, reveal why methods differ rather than just whether they differ.

Second, we embrace **honest negative results** as contributions to knowledge. Our finding that error types (as defined by dataset choice) do not show distinct uncertainty signatures refines the field's understanding and points toward instance-level characterization as the next frontier.

Third, we provide **actionable guidance** grounded in controlled experiments. Practitioners can use our finding that semantic entropy outperforms baselines by 9 AUROC points. Researchers can build on our framework for mechanistic analysis rather than proposing yet another uncertainty method without understanding its relationship to existing approaches.

This positioning reflects our belief that the field's next phase should focus on understanding mechanisms rather than proliferating methods—from "which wins" to "what works where."
