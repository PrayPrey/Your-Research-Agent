## Related Work

**Related Papers**
1. **Title**: Soft Prompt Threats: Attacking Safety Alignment and Unlearning in Open-Source LLMs (Schwinn et al., 2024)
   - **Authors**: Schwinn et al.
   - **Summary**: Identifies embedding space attacks that bypass current alignment methods in open-source LLMs, demonstrating vulnerabilities in existing safety mechanisms.
   - **Year**: 2024

2. **Title**: OpenOmni: Advancing Open-Source Omnimodal Large Language Models (Luo et al., 2025)
   - **Authors**: Luo et al.
   - **Summary**: Presents progressive multi-modal alignment with DPO for omnimodal LLMs, lacking formal safety guarantees.
   - **Year**: 2025

3. **Title**: Yi: Open Foundation Models by 01.AI (01.AI Team, 2024)
   - **Authors**: 01.AI Team
   - **Summary**: Demonstrates systematic data quality engineering at 3.1T token scale with cascaded deduplication approaches.
   - **Year**: 2024

4. **Title**: Constitutional AI: Harmlessness from AI Feedback (Anthropic, 2023)
   - **Authors**: Not specified
   - **Summary**: Natural language principles guide RLHF training using heuristic principle matching without formal verification.
   - **Year**: 2023

5. **Title**: Systems Engineering With Architecture Modeling, Formal Verification, and Human Interactions for Learning-Enabled Autonomous Agent (Ganeriwala et al., 2025)
   - **Authors**: Ganeriwala et al.
   - **Summary**: Demonstrates hybrid symbolic-neural architecture (Soar/nuXmv integration) with automated verification preventing unsafe RL agent actions.
   - **Year**: 2025

6. **Title**: Systems Engineering Process Enhancement: Requirements Verification Methodology using Natural Language Processing (Júnior et al., 2024)
   - **Authors**: Júnior et al.
   - **Summary**: EARS (Easy Approach to Requirements Syntax) template formalization technique from automotive requirements engineering (ISO 26262).
   - **Year**: 2024

7. **Title**: Upholding human dignity in AI: Advocating moral reasoning over consensus ethics for value alignment (Machidon, 2025)
   - **Authors**: Machidon
   - **Summary**: Philosophical framework arguing for stable moral axioms transcending consensus-based ethics for AI alignment.
   - **Year**: 2025

8. **Title**: Ethical Reasoning and Moral Value Alignment of LLMs Depend on the Language We Prompt Them in (Agarwal et al., 2024)
   - **Authors**: Agarwal et al.
   - **Summary**: Demonstrates that LLM moral reasoning varies significantly across languages, showing language-dependent ethical reasoning vulnerabilities.
   - **Year**: 2024

9. **Title**: Fully Automatic Neural Network Reduction for Formal Verification (Ladner & Althoff, 2023)
   - **Authors**: Ladner & Althoff
   - **Summary**: Demonstrates automated reduction techniques enabling formal verification of large neural networks.
   - **Year**: 2023

10. **Title**: VeriFlow: Modeling Distributions for Neural Network Verification (Abu Zaid et al., 2024)
    - **Authors**: Abu Zaid et al.
    - **Summary**: Probabilistic verification method over data distributions for neural network verification.
    - **Year**: 2024

**Key Challenges**
1. **Empirical Safety Limitations**: Current alignment methods (Constitutional AI, pure RLHF) provide only empirical sampling-based safety guarantees without mathematical proofs, leaving systems vulnerable to undiscovered failure modes.

2. **Embedding Space Attacks**: Soft prompt threats and other embedding space attacks can bypass current safety alignments, demonstrating fundamental vulnerabilities in continuous optimization approaches.

3. **Language-Dependent Alignment**: LLM ethical reasoning and moral value alignment varies across languages, undermining universality of natural-language-based alignment approaches.

4. **Lack of Formal Verification**: Existing LLM alignment methods lack formal verification frameworks, preventing mathematical safety guarantees that are standard in safety-critical systems (aerospace, automotive).

5. **Specification Ambiguity**: Natural language alignment specifications are ambiguous and not machine-parseable, limiting reproducibility and independent verification.

6. **Adversarial Robustness Gap**: Reactive red teaming and adversarial training cannot prove absence of vulnerabilities, only detect sampled failure modes.

7. **Scaling Verification to LLMs**: While formal verification succeeds in small-scale systems (RL agents, automotive systems), scaling to billion-parameter LLMs remains an open challenge.

8. **Multi-Stakeholder Governance**: Achieving consensus on safety axioms across diverse ethical frameworks and cultural contexts presents significant social and political challenges beyond technical solutions.

9. **Specification Completeness vs. Expressiveness Trade-off**: Creating complete specifications that prevent safety violations while remaining expressive enough to avoid over-constraining model usability.

10. **Runtime Performance Overhead**: Adding formal verification and runtime assertion monitoring introduces latency overhead that may be unacceptable for real-time consumer applications.
