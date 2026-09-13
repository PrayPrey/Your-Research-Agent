# Discussion

## 6.1 Key Findings

Our experiments establish three robust empirical findings and two principled falsifications.

**Finding 1: Semantic accommodation to AI is large, robust, and interaction-specific.** The C_sem = 0.329 (d = 1.998 vs random) result leaves no room for doubt that humans exhibit strong semantic alignment to their actual AI partner in RLHF helpfulness conversations. The effect is above the KNN topic-matched baseline (d = 0.417), confirming it is not explained by topical coherence. At n = 155,362 pairs, this is a population-level fact about human behavior in AI-assisted conversations.

**Finding 2: RLHF alignment quality shapes human semantic behavior.** The monotonic increase in C_sem from T1 to T3 (J-T p = 0.001; confirmed across three independent SBERT architectures) demonstrates that the quality gradient encoded in RLHF training propagates bidirectionally — affecting not only AI output quality but the semantic patterns of human turns that follow. This is the core empirical contribution of the paper: RLHF systems are not merely optimizing AI behavior in isolation. They are shaping the conversational ecology of human-AI interaction.

**Finding 3: Humans accommodate more to AI than AI to humans.** The directional asymmetry (all 9 tier × model cells; d = 0.13–0.41) is consistent with power asymmetry theory applied to human-AI interaction: humans adapt to their AI interlocutors more than vice versa. Unlike in human-human power asymmetry (where institutional hierarchy designates the power differential), in human-AI conversation the "asymmetry" arises from the structural properties of RLHF-optimized AI responses — they are by design more semantically comprehensive, offering more content for humans to align with.

**Finding 4 (Falsification): The mechanism is population-structural, not perceptual.** The H-M3 reversal (Δ < 0 in 25/27 cells) definitively rules out within-conversation quality discrimination as the proximal accommodation mechanism. If accommodation were driven by humans perceiving and responding to AI response quality within each exchange, Δ should be positive: human follow-ups should align better with the chosen (higher quality) response. The reverse finding — H_next is more similar to the rejected response — points instead to verbosity and topical breadth as the key confound in this operationalization. The H-M4 null result (β_PM ≈ 0) further confirms that no content feature we can measure with a cosine proxy mediates the asymmetry.

### Connecting the Findings

These four findings cohere into a single story. At the population level, RLHF training creates a distributional enrichment of AI response character across tiers — higher-tier conversations feature AI responses that are more topically rich, semantically comprehensive, and conversationally substantive. Humans embedded in this richer semantic environment exhibit greater accommodation, as measured by C_sem. This is analogous to environmental language exposure effects: speakers in linguistically richer environments develop more elaborate semantic patterns, not because they consciously perceive quality differences in each interaction, but because the overall distribution of their interlocutor's language is richer.

The H-M3 reversal adds an important nuance: "quality" in the RLHF sense (chosen > rejected, as judged by human raters) is not the same as "conversational informativeness" in the semantic continuity sense (which predicts H_next better). Rejected RLHF responses are typically longer, more expansive, and more hedged — qualities that make them better predictors of the human's subsequent information agenda, even if they fail RLHF quality criteria on other dimensions. This suggests a fundamental distinction between RLHF quality and accommodation-relevant semantic richness that has not been previously identified.

## 6.2 Limitations

**L1: Cross-sectional design — cannot distinguish accommodation from user self-selection.** HH-RLHF lacks user identifiers; each conversation is anonymous and independent. Our finding that higher-tier conversations show stronger C_sem cannot rule out user self-selection as an alternative: it is possible that more sophisticated users prefer higher-tier AI (online PPO) and also happen to communicate in ways that are more semantically similar to any interlocutor. True within-user accommodation trajectories (the same user becoming more aligned over time) cannot be measured with this dataset.

*Why this is acceptable:* Cross-sectional design is standard for large-scale observational NLP studies, and our population-level findings are valid within their scope — they establish that higher-tier conversations are systematically associated with stronger accommodation, regardless of mechanism. The J-T p = 0.001 with IPW correction and n = 155,362 pairs provides a robust population-level estimate.

*Future mitigation:* LMSYS Chatbot Arena with user session identifiers would enable within-user longitudinal accommodation measurement. Computing C_sem as a function of conversation turn number within a session would directly test whether accommodation strengthens as the conversation proceeds.

**L2: SBERT conflates topical and stylistic accommodation.** All-MiniLM-L6-v2 and related SBERT models produce full-utterance embeddings that capture both content (topical similarity) and style (semantic register, phrasing). C_sem cannot be cleanly decomposed into "pure style accommodation" vs "topically informed alignment."

*Why this is acceptable:* The KNN K=5 topic-matched baseline provides a conservative lower bound on style-specific accommodation: d = 0.417 above a topic-matched control is a strong signal even if some residual topical similarity remains. This is a stricter control than most prior accommodation literature.

*Future mitigation:* Style-factored sentence representations (STRAP [Cao & Xu, 2020]) or topic-free embeddings would enable decomposition of topical vs. stylistic components of C_sem.

**L3: Tier confound — HH-RLHF tiers differ in content distribution beyond RLHF quality.** The three splits were collected at different stages of Anthropic's deployment pipeline, making it plausible that user demographics, conversation topics, and interaction styles differ across tiers for reasons unrelated to RLHF quality.

*Why this is acceptable:* IPW covariate correction is applied whenever KS p < 0.0001 (triggered for all tier pairs), and the IPW-corrected C_sem values maintain monotonicity (Figure 5). The convergence of results across three independent SBERT architectures further reduces the likelihood that a spurious confound drives the finding.

*Future mitigation:* A controlled generation experiment — same prompt, same user, AI responses at different RLHF quality levels via temperature manipulation or base vs. RLHF model — would enable causal identification.

**L4: Proximal mechanism unresolved after h-m3 and h-m4 falsifications.** Both specific mechanism hypotheses we tested (within-conversation quality discrimination, PM-proxy mediation) were falsified. The proximal mechanism by which RLHF training quality induces population-level accommodation remains an open question.

*Why this is acceptable:* The population-level findings (h-e1, h-m1, h-m2) are empirically valid independently of any confirmed mechanism. Mechanism falsification is itself a contribution — we have ruled out two specific pathways, narrowing the space of plausible mechanisms for future investigation.

*Future mitigation:* Reward model scores as PM proxy (instead of hand-curated politeness centroid); NLI-based quality dimension analysis; length-controlled H-M3 replication (stratifying pairs by response length ratio to isolate verbosity from quality).

**L5: PM-proxy operationalization limitations.** H-M4 used cosine similarity to a hand-curated politeness centroid as the PM-score proxy. This is a weak operationalization of AI response quality that may miss the relevant quality signal.

*Why this is acceptable:* β_PM ≈ 0 with p ≈ 0.99 across all three models. Even if a stronger PM proxy exists, the effect size at this p-value is essentially zero — a stronger proxy would need to explain not only statistical significance but also meaningful variance in C_sem, which the low R² (≤ 0.012) suggests is not present.

## 6.3 Implications for Bidirectional Alignment Research

Our findings have several implications for how we design, evaluate, and interpret RLHF training.

**RLHF has bidirectional consequences.** Current RLHF evaluation measures AI output quality directly (human preference ratings, reward model scores). Our results demonstrate that RLHF quality propagates to human semantic behavior — a second-order effect that is invisible in standard evaluation. Future alignment research should consider whether the human-side adaptation response is desirable, neutral, or concerning, particularly for deployed systems at scale.

**The population-structural mechanism suggests a new design target.** If accommodation is driven by distributional enrichment of AI responses rather than per-response quality signals, then RLHF training should aim to produce AI responses that are not only high-quality on preference dimensions but also semantically rich and informationally comprehensive — optimizing for the distributional profile of human-AI conversations, not just individual response quality.

**The H-M3 reversal is a measurement artifact warning.** The finding that rejected RLHF responses better predict human follow-up semantics than chosen ones suggests that RLHF's chosen/rejected annotation captures quality dimensions (helpfulness, safety, instruction-following) that are partly orthogonal to conversational semantic continuity. Researchers using HH-RLHF chosen/rejected structure as a proxy for any quality signal should be aware of this dissonance.

## 6.4 Broader Impact

This work advances understanding of how AI system quality affects human communicative behavior at scale. Positive impacts include: providing tools for monitoring bidirectional adaptation effects in deployed AI systems; opening a measurement paradigm for studying human behavioral responses to RLHF quality beyond preference ratings; and connecting NLP alignment research to established sociolinguistic theory on accommodation and power dynamics.

A potential concern is the misuse of these findings to design AI systems that deliberately maximize human accommodation for persuasive or manipulative purposes — for example, by optimizing AI responses to induce users to adopt the AI's semantic patterns. We emphasize that our measurement is observational and does not endorse or enable such applications. The C_sem metric is a measurement tool, not a training objective. Researchers deploying it in system optimization should carefully evaluate ethical implications with respect to user autonomy and informed consent.
