# Related Work

We survey two lines of work on uncertainty quantification for LLM hallucination detection—entropy-based and consistency-based methods—and highlight the gap our work addresses.

## Entropy-Based Uncertainty Quantification

Token-level entropy measures uncertainty in next-token prediction by computing the entropy of the softmax distribution over vocabulary. High entropy indicates the model is uncertain about which token to generate, potentially signaling lack of knowledge.

Kadavath et al. (2022) demonstrated that LLMs exhibit calibration properties, with confidence scores correlating with correctness on question-answering tasks. Their P(True) method directly queries models about answer correctness. Kuhn et al. (2023) introduced *semantic entropy*, which clusters semantically equivalent answers before computing entropy, addressing the problem that multiple phrasings of the same answer inflate raw entropy estimates. They evaluated on natural language generation tasks including question answering, but did not compare against consistency-based methods.

Malinin and Gales (2018) provided theoretical foundations for distinguishing epistemic and aleatoric uncertainty in neural networks using prior networks. More recently, Xiong et al. (2023) surveyed confidence estimation methods for LLMs, categorizing approaches by whether they require access to logits or only outputs.

**Limitation:** Entropy methods have primarily been evaluated on NLG tasks or with proprietary models, without systematic comparison to consistency-based approaches on factuality benchmarks.

## Consistency-Based Detection

An orthogonal approach measures hallucination through response consistency across multiple generations. If a model generates semantically different answers to the same question across independent samples, this suggests uncertainty or fabrication.

Manakul et al. (2023) introduced SelfCheckGPT, which generates multiple responses and computes consistency via BERTScore or embedding similarity. They demonstrated effectiveness on WikiBio biography generation, where inconsistent facts across samples indicate hallucination. Wang et al. (2023) explored self-consistency in chain-of-thought reasoning, showing that majority voting across sampled reasoning chains improves accuracy.

Chen et al. (2024) extended consistency methods with contrastive decoding, identifying hallucinations by comparing outputs from amateur and expert models. Lin et al. (2022) created TruthfulQA specifically to evaluate truthfulness, showing that models often generate false but plausible-sounding answers.

**Limitation:** Consistency methods have been evaluated on different benchmarks (WikiBio, reasoning tasks) than entropy methods, making it impossible to determine whether the signals are redundant or complementary.

## The Gap: Missing Head-to-Head Comparison

The two paradigms—entropy and consistency—have evolved independently:

| Method | Benchmark | Model | Direct Comparison |
|--------|-----------|-------|------------------|
| Semantic Entropy (Kuhn 2023) | NLG tasks | Various | No consistency baseline |
| SelfCheckGPT (Manakul 2023) | WikiBio | GPT-3 | No entropy baseline |
| P(True) (Kadavath 2022) | QA tasks | Proprietary | No consistency baseline |

No prior work has:
1. Compared both methods on the **same factuality benchmark** (e.g., TruthfulQA)
2. Using the **same model** (e.g., LLaMA-2-7B)
3. With analysis of whether signals are **redundant or orthogonal**

This gap prevents practitioners from making informed choices about which uncertainty signal to use—or whether combining them provides additional value.

## Our Positioning

We address this gap by conducting the first systematic comparison of token entropy and N-sample consistency on TruthfulQA with LLaMA-2-7B. Beyond comparing raw detection performance, we analyze the *correlation* between signals and the *complementary predictive value* on cases where methods disagree. This determines whether a hybrid approach is theoretically justified before investing in its implementation.
