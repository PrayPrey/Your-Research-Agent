## Related Work

**Related Papers**

1. **Title**: Planning and acting in partially observable stochastic domains (Kaelbling, Littman & Cassandra, 1998)
   - **Authors**: Kaelbling, Littman, Cassandra
   - **Summary**: Foundational work on POMDP framework for planning in partially observable environments, providing core algorithms for belief space planning and decision-making under uncertainty.
   - **Year**: 1998

2. **Title**: Probabilistic Robotics (Thrun, Burgard & Fox, 2005)
   - **Authors**: Thrun, Burgard, Fox
   - **Summary**: Comprehensive particle filter methods for robotics applications, establishing probabilistic approaches for hidden state estimation in robotic systems.
   - **Year**: 2005

3. **Title**: Action understanding as inverse planning (Baker, Saxe & Tenenbaum, 2009)
   - **Authors**: Baker, Saxe, Tenenbaum
   - **Summary**: Demonstrates action understanding through Bayesian inverse planning, validating propositional belief representations and Bayesian inference for Theory of Mind.
   - **Year**: 2009

4. **Title**: Machine theory of mind (ToMnet) (Rabinowitz et al., 2018)
   - **Authors**: Rabinowitz et al.
   - **Summary**: Introduces ToMnet framework for machine-based Theory of Mind, validating Bayesian inference approaches for mental state understanding.
   - **Year**: 2018

5. **Title**: Computational ToM with Abstractions (Erdogan et al., 2024)
   - **Authors**: Erdogan et al.
   - **Summary**: Demonstrates that abstracting beliefs into higher-level epistemic logic concepts improves multi-agent collaboration, validating modular ToM architecture feasibility.
   - **Year**: 2024

6. **Title**: Agentic-ToM (Sarangi et al., 2025)
   - **Authors**: Sarangi et al.
   - **Summary**: Shows that embedding psychologically-grounded functions (perspective-taking, mental state tracking) significantly improves LLM Theory of Mind performance on ToMBench through function-guided prompting.
   - **Year**: 2025

7. **Title**: Computational Language Acquisition with ToM (Liu et al., 2023)
   - **Authors**: Liu et al.
   - **Summary**: Demonstrates that training speakers with internal listener model (ToM component) improves referential game performance by 8-12%, providing empirical validation for explicit ToM models.
   - **Year**: 2023

8. **Title**: SymbolicToM (Sclar et al., 2023)
   - **Authors**: Sclar et al.
   - **Summary**: Introduces plug-and-play symbolic module using rule-based belief updates for Theory of Mind, offering interpretable but brittle approach without uncertainty quantification.
   - **Year**: 2023

9. **Title**: AutoToM (Gandhi et al., 2024)
   - **Authors**: Gandhi et al.
   - **Summary**: Proposes Bayesian inverse planning approach for inferring goals and beliefs, providing probabilistic and cognitively grounded ToM without LLM integration.
   - **Year**: 2024

10. **Title**: Hypothetical-Minds (Cross et al., 2024)
    - **Authors**: Cross et al.
    - **Summary**: Develops ToM module that generates hypotheses about mental states for high-level planning using modular architecture, though without probabilistic inference.
    - **Year**: 2024

11. **Title**: ToMBench (Chen et al., 2024)
    - **Authors**: Chen et al.
    - **Summary**: ACL 2024 benchmark with 2,860 samples covering 31 ToM abilities from ATOMS framework, bilingual, with current SOTA (GPT-4) achieving ~78% accuracy.
    - **Year**: 2024

12. **Title**: FANToM (Kim et al., 2023)
    - **Authors**: Kim et al.
    - **Summary**: Benchmark featuring diverse social scenarios with ambiguity and nuanced ToM tasks where most models achieve ~65% accuracy compared to humans.
    - **Year**: 2023

13. **Title**: Auto-Encoding Variational Bayes (Kingma & Welling, 2014)
    - **Authors**: Kingma, Welling
    - **Summary**: Foundational VAE framework for learning latent variable models through variational inference, applicable to training observation models when mental states are latent.
    - **Year**: 2014

**Key Challenges**

1. **Fragmentation between Cognitive Foundations and Scalable NLP**: Existing approaches sacrifice either cognitive grounding (pure neural models) or scale (symbolic ToM systems), lacking unified frameworks that bridge cognitive science Bayesian ToM with production NLP systems.

2. **Lack of Interpretability and Uncertainty Quantification**: LLMs produce opaque embeddings with overconfident point estimates for mental state inferences, lacking principled uncertainty quantification and human-inspectable belief representations.

3. **Limited Explicit Mental State Tracking**: Pure end-to-end trained LLMs rely on implicit mental state representations in embeddings without explicit probabilistic belief tracking, limiting interpretability and steerability.

4. **Rule-Based Systems Brittleness**: Symbolic ToM approaches use brittle hand-crafted rules without uncertainty quantification, failing to scale to complex real-world scenarios with ambiguous evidence.

5. **Absence of LLM-Integrated Probabilistic ToM**: Existing probabilistic ToM systems (AutoToM) are not integrated with production LLMs, requiring hand-crafted planning models and lacking learnable observation models.

6. **Benchmark Focus Limitations**: Existing ToM benchmarks disproportionately focus on belief reasoning while under-exploring intentions, desires, and emotions, creating gaps in affective ToM assessment.

7. **First-Order ToM Limitation**: Most systems focus on first-order beliefs (beliefs about world facts) without addressing higher-order recursive beliefs needed for strategic interaction, negotiation, and deception scenarios.

8. **Computational Overhead Concerns**: Adding explicit belief tracking modules risks introducing prohibitive computational costs that prevent practical deployment in real-time interactive systems.

9. **Data Requirements for Training**: Learning accurate observation models P(utterance|mental_state) requires sufficiently diverse ToM-annotated training data covering mental state variations, which may be limited for some domains.

10. **Propositional Representation Limitations**: First-order propositional belief representations may miss implicit affective states (emotions, trust) and cultural/contextual nuances beyond explicit propositions.
