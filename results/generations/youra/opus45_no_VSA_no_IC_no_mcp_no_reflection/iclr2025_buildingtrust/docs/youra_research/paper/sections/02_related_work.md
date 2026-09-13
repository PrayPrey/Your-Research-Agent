# Related Work

Our work relates to three areas: uncertainty-based hallucination detection, sampling-based consistency methods, and confidence calibration. We discuss each in turn, highlighting the evaluation gaps our work addresses.

## Uncertainty Quantification for Language Models

Uncertainty estimation in neural networks has a rich history [Gal and Ghahramani, 2016], with recent adaptations for large language models. **Semantic entropy** [Kuhn et al., 2023] extends classical entropy-based uncertainty to account for semantic equivalence—responses that differ in surface form but convey the same meaning are clustered together before computing entropy. The method uses bidirectional NLI (natural language inference) to determine semantic equivalence, then computes entropy over the cluster distribution. Higher entropy indicates greater uncertainty and potential hallucination. Follow-up work demonstrated semantic entropy's effectiveness on detecting confabulations in long-form generation [Farquhar et al., 2024], achieving state-of-the-art results on several benchmarks.

However, semantic entropy has been evaluated primarily on TruthfulQA and related factual QA tasks. The reliance on NLI-based clustering raises questions about transfer to benchmarks with different hallucination definitions—if the benchmark's notion of "hallucination" does not align with semantic disagreement patterns, the method may not generalize.

## Self-Consistency Methods

**SelfCheckGPT** [Manakul et al., 2023] takes a different approach: rather than clustering by semantic equivalence, it measures surface-level agreement across multiple generations. The intuition is that factual knowledge, being reproducible, should yield consistent responses, while hallucinations vary. The method computes pairwise similarity (using BERTScore, n-gram overlap, or NLI-based comparison) and aggregates into a consistency score. SelfCheckGPT was evaluated on WikiBio hallucination detection, achieving strong results.

The critical gap: SelfCheckGPT uses different benchmarks, different sample counts, and different base models than semantic entropy evaluations. Direct comparison of the two methods requires matching these variables—a comparison that, to our knowledge, does not exist in the literature.

## Confidence Calibration

Before sampling-based methods, **confidence calibration** addressed the problem of overconfident predictions. Contextual calibration [Zhao et al., 2021] adjusts model confidence using content-free inputs to estimate inherent biases. Temperature scaling and Platt scaling [Guo et al., 2017] post-process confidence scores to improve calibration. While these methods primarily target classification tasks, they provide natural baselines for hallucination detection.

Notably, calibration methods have not been systematically compared to sampling-based uncertainty methods on hallucination detection benchmarks. Our pilot framework enables such comparison by establishing matched evaluation conditions.

## Hallucination Benchmarks

**TruthfulQA** [Lin et al., 2022] evaluates model truthfulness on questions designed to elicit common misconceptions. The benchmark labels responses as truthful or not based on "Best Answer" matching, which may not align with uncertainty-based detection definitions. **HaluEval** [Li et al., 2023] provides hallucinated and correct response pairs across QA, summarization, and dialogue tasks, with explicit hallucination labels.

These benchmarks encode different notions of "hallucination." TruthfulQA focuses on factual misconceptions; HaluEval includes fabricated facts and unsupported claims. Whether detection methods perform consistently across these different definitions remains unexplored.

## Our Position

Existing work establishes that semantic entropy and self-consistency can detect hallucinations in isolation. What is missing is a controlled comparison under matched computational budgets. Our work fills this gap by evaluating both methods on the same benchmarks (TruthfulQA, HaluEval), with the same sample counts (N=10), the same model (Llama-3-8B-Instruct), and the same temperature (0.7). This matched-budget design enables direct comparison and reveals benchmark sensitivity that isolated evaluations obscure.
