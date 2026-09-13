# Related Work

Uncertainty quantification for large language models has developed along several parallel tracks. We organize prior work into three categories—entropy-based methods, consistency-based methods, and verbalized confidence—then position our contribution relative to this landscape.

## Entropy-Based Uncertainty Estimation

Token-level entropy, computed from the softmax distribution over next-token predictions, has long served as a proxy for model uncertainty in language models. High entropy indicates a flat distribution where the model assigns similar probability to many continuations, signaling low confidence.

Kuhn et al. (2023) extended this approach with **semantic entropy**, which clusters generated responses by meaning before computing entropy. Their key insight is that multiple *phrasings* of the same answer should not inflate uncertainty—only semantically distinct responses matter. On closed-book QA benchmarks, semantic entropy achieves AUROC in the range 0.75-0.85, substantially outperforming raw token entropy.

However, entropy-based methods require access to model logits, excluding their application to commercial API-only models (GPT-4, Claude). They also conflate different sources of uncertainty: a model might be uncertain about word choice (low semantic impact) or uncertain about factual content (high semantic impact). Semantic clustering addresses the former but requires an additional clustering step with its own error modes.

Our work builds on entropy-based methods by including token entropy as a baseline signal, but we find it underperforms consistency even without semantic clustering—achieving only AUROC=0.65 on TriviaQA with Llama-2-7B-chat.

## Consistency-Based Hallucination Detection

Consistency-based methods leverage the intuition that models produce stable outputs for questions they can reliably answer, but divergent outputs when hallucinating.

Manakul et al. (2023) introduced **SelfCheckGPT**, which generates multiple responses and measures their consistency via BERTScore, question-answering overlap, or n-gram similarity. When responses contradict each other, the model is likely hallucinating. They demonstrated strong performance on WikiBio-generated biographies but did not report AUROC on standard QA benchmarks like TriviaQA.

Wang et al. (2023) explored **self-consistency** in the context of chain-of-thought reasoning, finding that majority voting over multiple reasoning paths improves accuracy. While their focus was on improving outputs rather than detecting errors, the underlying signal—consistency across samples—is the same.

Our approach follows the SelfCheckGPT paradigm but uses embedding cosine similarity (via SentenceTransformer all-MiniLM-L6-v2) rather than BERTScore. We provide the first AUROC quantification of this signal on TriviaQA, finding AUROC=0.81 with a large effect size (d=1.19).

## Verbalized Confidence

An alternative approach asks models to state their own confidence explicitly. Xiong et al. (2023) studied **verbalized confidence** across multiple benchmarks, prompting models to rate their certainty (e.g., "On a scale of 1-10, how confident are you?"). They found that verbalized confidence is poorly calibrated—models often express high confidence in wrong answers.

Lin et al. (2022) similarly found that models' self-reported uncertainty does not correlate well with actual correctness, particularly for instruction-tuned models trained to sound confident.

We do not include verbalized confidence as a baseline in our experiments because it requires prompt engineering and exhibits high variance across phrasings. Our focus is on signal-based methods (entropy, consistency) that derive uncertainty from model behavior rather than self-report.

## Positioning Our Contribution

Prior work has developed entropy and consistency signals largely in isolation. Kuhn et al. (2023) focused on improving entropy via semantic clustering; Manakul et al. (2023) focused on improving consistency via alternative similarity metrics. Neither directly compared the signals on the same benchmark under controlled conditions.

**What prior work leaves unanswered:**
- Which signal—entropy or consistency—is more predictive for factual QA?
- Do the signals capture complementary information such that combining them improves detection?
- What is the correlation between these signals, and does it limit fusion benefit?

We address these questions by evaluating both signals on TriviaQA with Llama-2-7B-chat under identical conditions. Our contribution is not a new method but a systematic comparison that provides actionable guidance: consistency outperforms entropy (AUROC 0.81 vs 0.65), and naive linear fusion does not help at proof-of-concept scale.

This finding has practical implications. Consistency-based detection requires only generated text, making it applicable to API-only models where logits are unavailable. If consistency alone achieves strong performance, the additional complexity of entropy computation—and the restriction to open-source models—may not be justified for factual QA applications.
