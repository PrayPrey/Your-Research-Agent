# Related Work

Our work bridges reward model interpretability and human preference modeling by introducing structural sensitivity probing. We position our contribution relative to three areas: reward model evaluation, preference data characteristics, and reward model architectures.

## Reward Model Evaluation

The development of systematic reward model evaluation has accelerated with the growth of RLHF-based alignment. **RewardBench** [Lambert et al., 2024] provides a comprehensive benchmark spanning four categories: Chat (general helpfulness), Chat Hard (challenging instructions), Safety (harmful content rejection), and Reasoning (multi-step problem solving). RewardBench evaluates whether reward models correctly identify the better response in curated pairs, achieving strong differentiation among models---ArmoRM achieves 89.0% overall accuracy compared to baseline models near 50%.

However, RewardBench's evaluation paradigm assumes that reward models score based on content quality. The benchmark does not probe for systematic biases toward particular *formats* that might inflate scores independent of quality. A model could achieve high RewardBench accuracy while still encoding strong preferences for enumerated responses when content is controlled.

**MRMBench** extends reward model probing to multiple dimensions including instruction following, harmlessness, and factual accuracy. By decomposing reward model behavior into interpretable components, MRMBench reveals which quality dimensions different models prioritize. Yet like RewardBench, MRMBench focuses on *content* dimensions---whether models value helpfulness over conciseness, or accuracy over engagement. Structural formatting preferences remain outside its scope.

Our work complements these benchmarks by introducing a new dimension: *structural sensitivity*. Rather than asking whether reward models correctly rank responses by quality, we ask whether they exhibit systematic preferences for formatting features independent of content.

## Preference Data and Human Annotation Biases

Reward models learn from human preference data, inheriting both explicit quality judgments and implicit annotation biases. Research on annotation artifacts has shown that human raters exhibit systematic patterns that models learn to exploit [Gururangan et al., 2018].

In the context of RLHF, human raters compare response pairs and select which they prefer. Several factors may introduce structural biases into this process. **Cognitive load**: Enumerated responses may be easier to scan and evaluate, leading raters to prefer them when time-constrained. **Perceived thoroughness**: Lists suggest exhaustive coverage even when content is equivalent to prose. **Visual distinctiveness**: Numbered markers create clear structure that prose cannot match.

**HumanAgencyBench** [Sturgeon et al., 2025] evaluates whether LLM responses support user autonomy across six dimensions including option provision and epistemic humility. While not directly probing reward models, HumanAgencyBench demonstrates that formatting choices affect perceived helpfulness. Responses that enumerate options score higher on agency support, suggesting human raters may encode format-quality associations during preference labeling.

Our work tests whether these implicit formatting preferences transfer to reward models during RLHF training. If human raters systematically prefer enumerated responses, reward models should learn this preference as a stable, high-detectability feature.

## Reward Model Architectures

Modern reward models span diverse architectures and training objectives. Understanding these differences is essential for interpreting cross-model patterns.

**Decoder-only reward models** adapt pretrained language models by adding a scalar head that predicts preference scores. ArmoRM [Wang et al., 2024] extends this approach with multi-objective training and mixture-of-experts aggregation, achieving state-of-the-art RewardBench performance (89.0%). UltraRM [Cui et al., 2023] uses scalar regression on the UltraFeedback dataset with a Llama backbone. Starling-RM [Zhu et al., 2023] applies K-wise Bradley-Terry training to Llama2-7B-Chat using the Nectar dataset.

**Encoder-only reward models** take a different approach. PairRM [Jiang et al., 2023] uses DeBERTa-v3-large (0.4B parameters) with pairwise comparison---it scores two responses relative to each other rather than assigning absolute scores. This architectural choice fundamentally changes how the model processes structural features: bidirectional attention sees enumeration markers in context of the full response rather than accumulating sequential signals.

We leverage this architectural diversity to test whether enumeration preference is architecture-dependent. If causal attention in decoder-only models creates cumulative structural signals that bidirectional attention does not, we would expect enumeration preference in decoder models but not encoder models. Our results confirm this prediction, providing evidence for architecture-conditional structural encoding.

## Positioning Our Contribution

Prior work has established robust methods for evaluating reward model *content* preferences but leaves structural dimensions unexplored. We fill this gap by introducing controlled behavioral probing for formatting biases. Our factorial stimulus design isolates structure from content quality, and our multi-architecture evaluation reveals an architectural boundary in structural encoding.

This positions our work as complementary to existing benchmarks: RewardBench and MRMBench evaluate *what* reward models prefer in content terms; we evaluate *how* they respond to structural formatting independent of content. Understanding both dimensions is necessary for building reward models that optimize for genuine quality rather than superficial formatting patterns.
