# Related Work

## Communication Accommodation Theory

Communication Accommodation Theory (CAT), introduced by Giles \citep{giles1973accommodation}, posits that individuals adjust their communication style to signal social identity and regulate social distance. Convergence—adapting toward an interlocutor's style—signals affiliation and builds rapport, while divergence maintains distinctiveness.

Niederhoffer and Pennebaker \citep{niederhoffer2002linguistic} operationalized accommodation through Linguistic Style Matching (LSM), finding correlations around r≈0.3 between style matching and relationship quality in human-human dyads. This work established that accommodation is measurable through linguistic features and predicts interaction outcomes.

However, human-human accommodation research assumes symmetric agency: both parties can choose to accommodate. In human-AI interaction, this symmetry breaks. AI systems accommodate through training objectives, not social motivation; humans may not perceive AI as warranting reciprocal accommodation. Whether CAT predictions—particularly the positive accommodation-engagement link—transfer to human-AI contexts is an open question.

## Human-AI Linguistic Adaptation

Recent work confirms that accommodation occurs in human-AI dialogue. Chen et al. \citep{chen2026bidirectional} analyzed 1,319 GPT-4o conversations from WildChat, demonstrating bidirectional linguistic accommodation with distinct temporal dynamics: model accommodation is front-loaded (strongest in early turns), while user convergence develops gradually.

This finding validates that accommodation exists in human-AI interaction, but leaves the *outcome* relationship untested. Chen et al. measured accommodation patterns without connecting them to engagement metrics. Our work extends this line by testing whether accommodation magnitude predicts conversation continuation.

The LMSYS-Chat-1M dataset \citep{zheng2023lmsys} provides a large-scale resource for human-AI dialogue research (1M+ conversations across 25+ models). While designed for model evaluation, it enables analysis of interaction dynamics at unprecedented scale. We use the related Anthropic hh-rlhf dataset \citep{anthropic2022hh}, which offers cleaner turn structure for accommodation analysis.

## Chatbot Engagement and the Uncanny Valley

Ciechanowski et al. \citep{ciechanowski2019uncanny} documented uncanny valley effects in chatbot interaction: users respond negatively to AI behaviors that approximate but don't fully achieve human-like communication. This suggests that excessive accommodation—making AI "too human"—may backfire.

Our finding of an inverted-U accommodation-engagement relationship aligns with this framework. Moderate accommodation signals attentiveness without triggering artificiality concerns; excessive accommodation may activate uncanny valley responses. This provides theoretical grounding for why linear CAT predictions may not hold in human-AI contexts.

## Formality in Dialogue

Formality is a well-studied dimension of linguistic variation. Heylighen and Dewaele \citep{heylighen1999formality} proposed a computational formality measure based on part-of-speech distributions. Modern approaches use transformer-based classifiers; the DeBERTa formality ranker \citep{deberta2024formality} achieves 87.8% accuracy on the GYAFC benchmark and provides continuous formality scores suitable for delta computation.

Formality accommodation—adjusting formality level to match an interlocutor—is a specific instantiation of CAT. Formal users may expect formal responses; casual users may find overly formal AI off-putting. Our work operationalizes accommodation through formality deltas, treating smaller deltas as stronger accommodation.

## Summary

Prior work establishes: (1) CAT predicts accommodation benefits in human-human interaction, (2) accommodation exists in human-AI dialogue, (3) uncanny valley effects suggest limits to human-likeness. We contribute the first large-scale test of the accommodation-engagement link in human-AI conversation, revealing that moderate—not maximal—accommodation predicts highest engagement.
