# Conclusion

We opened by asking: when humans interact with better AI assistants, do they start talking more like them? Our experiments answer yes — but with an important qualifier about *how* this happens.

## 7.1 Summary

We introduced C_sem, a training-free SBERT-based measure of semantic accommodation in human-AI conversational turn pairs with a three-level partner-specificity control hierarchy. Applied to 155,362 conversation pairs from the Anthropic HH-RLHF helpfulness dataset, C_sem reveals that humans exhibit robust, interaction-specific semantic accommodation to their AI partners (C_sem = 0.329, Cohen's d = 1.998 vs. random baseline). This accommodation scales monotonically with RLHF alignment tier quality (Jonckheere-Terpstra p = 0.001, confirmed across three SBERT architectures), establishing a direct empirical link between RLHF training quality and downstream human semantic behavior. Humans accommodate more to AI than AI to humans — a directional asymmetry consistent with power asymmetry theory — confirmed in all 9 tier × model cells with zero exceptions.

Yet the mechanism we initially hypothesized — that within-conversation quality discrimination drives accommodation — is definitively falsified. Human follow-up turns are paradoxically more similar to the rejected AI response than the approved one (Δ < 0 in 25/27 cells, d up to −0.74). A politeness-style mediation analysis finds β_PM ≈ 0. The mechanism is population-structural: RLHF training shifts the distributional character of AI responses across tiers, and humans embedded in this richer semantic environment exhibit greater accommodation — not because they perceive quality differences within each exchange, but because the overall conversational ecology is richer.

## 7.2 Future Directions

The H-M3 reversal opens a specific and tractable follow-up: **verbosity-controlled within-prompt quality probe.** Our three operationalizations (raw, length-matched, prompt-projected) partially addressed the length confound, but a fully length-controlled replication stratifying pairs by response length ratio would test whether the Δ < 0 signal persists after eliminating verbosity as the primary confound. If Δ reverses under strict length matching, it would confirm that RLHF "quality" and semantic continuity relevance are distinct dimensions mediated by response length.

More broadly, our cross-sectional design cannot distinguish population-level accommodation from within-user accommodation trajectories. **Longitudinal study using LMSYS Chatbot Arena** with session identifiers would enable within-user C_sem measurement as a function of turn number — testing whether accommodation strengthens over the course of a single conversation. This would provide the causal evidence missing from our observational design.

Finally, the C_sem infrastructure (SBERT inference, KNN controls, IPW correction, J-T monotonicity test) is directly transferable to other AI conversation datasets. **Cross-dataset replication on WildChat and LMSYS Chatbot Arena** would test whether tier-scalable accommodation generalizes beyond HH-RLHF helpfulness conversations to open-ended dialogue, red-teaming interactions, and diverse model capability levels.

## 7.3 Closing Thought

The H-M3 reversal suggests something deeper than a measurement artifact: RLHF's notion of "quality" — calibrated by human raters on dimensions like helpfulness, safety, and instruction-following — is not the same as semantic richness in the conversational continuity sense. Rejected responses, typically longer and more expansive, better predict what the human will say next, even as they score lower on quality. This mismatch is a fundamental property of how RLHF annotations are constructed, and it has implications for any research that uses chosen/rejected signal as a proxy for conversational effectiveness.

RLHF systems are not optimizing AI behavior in isolation — they are shaping the semantic ecology of human-AI conversations. Designing systems that are genuinely beneficial at the population level requires understanding both sides of that ecology.
