# Title
Voting-Theoretic RLHF: Pluralistic AI Alignment Through Fairness-Constrained Social Choice Aggregation

# Motivation
Current RLHF systems implicitly use majority voting to aggregate human feedback, systematically marginalizing minority moral perspectives (representation score < 0.3). This creates AI systems that amplify dominant voices rather than reflecting society's pluralistic values. Existing approaches lack formal guarantees against minority exclusion and provide no interpretable mechanisms for understanding which values are embedded. This research addresses the critical gap in methodologies for systematic pluralistic value incorporation beyond standard RLHF.

# Main Idea
We replace RLHF's implicit majority aggregation with explicit, differentiable voting rules from social choice theory (Borda, Copeland, Maximal Lottery), constrained by fairness axioms from participatory budgeting. The core mechanism: Individual Fairness Share (IFS) and Group Fairness Share (GFS) constraints guarantee each perspective receives ≥1/n influence, preventing systematic marginalization. Interpretable membership vectors reveal annotators' moral dimensions, enabling context-adaptive voting rule selection (e.g., Copeland for high-stakes dilemmas, Maximal Lottery for value-diverse scenarios). 

Testing on PERSONA benchmark, we predict: minority representation score >0.5 (vs <0.3 baseline), IFS satisfaction >90%, and alignment tax <10%. The framework provides the first formal connection between social choice axioms and pluralistic alignment guarantees, with open-source implementation including an interpretability dashboard. This enables AI systems to verifiably represent diverse moral perspectives while maintaining practical performance.