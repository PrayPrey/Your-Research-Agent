# Title
Moral Curriculum Learning: Kohlberg-Inspired Progressive Training for LLM Value Alignment

# Motivation
Current LLM alignment methods like RLHF train on moral scenarios without considering complexity structure, potentially limiting generalization to novel ethical dilemmas. Human moral development follows a well-documented progression from simple rule-following to principled reasoning (Kohlberg's stages). Recent work shows developmental psychology principles can improve AI generalization in other domains (Piloto et al. 2022), yet this approach remains unexplored for moral reasoning—a critical gap given AI's expanding role in value-laden decisions.

# Main Idea
We hypothesize that structuring LLM fine-tuning as a Kohlberg-inspired moral curriculum—progressing from preconventional (self-interest) through conventional (social norms) to postconventional (universal principles)—will yield superior moral generalization compared to flat RLHF training. The causal mechanism: progressive complexity builds hierarchical moral representations, enabling decomposition of novel dilemmas into learned component principles.

**Methodology:** Train matched LLMs using (1) 6-stage moral curriculum with 80-90% mastery gates versus (2) standard RLHF, controlling for compute. Evaluate on held-out moral benchmarks (ETHICS, MoralBench).

**Predictions:** MCL achieves ≥10% higher accuracy on novel dilemmas; shows greater robustness to distribution shift. Falsified if curriculum ordering provides no advantage over random ordering.

**Impact:** Establishes developmental psychology as a principled framework for value alignment methodology.