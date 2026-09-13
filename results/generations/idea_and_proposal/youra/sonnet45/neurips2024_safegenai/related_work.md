## Related Work

**Related Papers**
1. **Title**: Trustworthy LLMs: a Survey and Guideline for Evaluating Large Language Models' Alignment (Liu et al., 2023)
   - **Authors**: Liu et al.
   - **Summary**: Establishes 7-dimension trustworthiness taxonomy (reliability, safety, fairness, resistance to misuse, explainability, social norms, robustness) evaluated independently. PASMC addresses gap by unifying these dimensions under multi-objective optimization framework.
   - **Year**: 2023

2. **Title**: Generative AI for synthetic data in banking transactions: Balancing utility and compliance (Kumar & Gujjala, 2025)
   - **Authors**: Kumar, Gujjala
   - **Summary**: Hybrid loss combining Wasserstein distance with privacy leakage penalties achieves 94% performance retention for 2-dimension optimization (privacy + fidelity). Demonstrates learnable weight optimization feasibility; PASMC extends to 7 dimensions with context adaptation.
   - **Year**: 2025

3. **Title**: Navigating Privacy Risks in Generative AI: Concerns, Challenges, and Potential Solutions (Yang, 2026)
   - **Authors**: Yang
   - **Summary**: Demonstrates ε-differential privacy (ε=5, δ=10^-6) provides adequate protection but creates utility-privacy trade-off. Validates Pareto frontier existence assumption; static ε universally applied sacrifices utility unnecessarily.
   - **Year**: 2026

4. **Title**: Reframing Clinical AI Evaluation (Abikenari et al., 2025)
   - **Authors**: Abikenari et al.
   - **Summary**: Stakeholder-engaged multi-dimensional evaluation framework demonstrates need for context-specific safety priorities (medical domain requires high calibration, finance requires high ethical compliance). Provides domain taxonomy for PASMC context ontology.
   - **Year**: 2025

5. **Title**: Stability AI Acceptable Use Policy (Archon KB: d430867c)
   - **Authors**: Not specified
   - **Summary**: 7-category prohibition framework with no coordination mechanism. Represents industry standard for static safety configurations without cross-dimensional optimization.
   - **Year**: Not specified

6. **Title**: Stable Diffusion Safety Checker (Archon KB: 48b11cc8)
   - **Authors**: Not specified
   - **Summary**: CLIP-based filtering with known bypass issues. Demonstrates limitations of single-method safety checkers that motivate ensemble critic architecture.
   - **Year**: Not specified

7. **Title**: Safetensors Security Audit & Diffusers Safety Checker
   - **Authors**: Not specified
   - **Summary**: Known bypass vulnerabilities in single-method safety checkers motivate PASMC's ensemble critic architecture (3-5 methods per dimension) for robustness.
   - **Year**: Not specified

**Key Challenges**
1. **Static Safety Configurations Lack Context Adaptation**: Existing industry standards apply fixed safety configurations universally across all deployment contexts, sacrificing utility without meaningful safety gains where strict constraints are not needed.

2. **Independent Dimension Evaluation Without Interaction Modeling**: Liu 2023's 7-dimension trustworthiness taxonomy evaluates dimensions independently, missing opportunities to model conflicts and trade-offs between dimensions (privacy vs. utility, calibration vs. coverage).

3. **Limited Scalability of Multi-Objective Optimization**: Kumar 2025 demonstrates learnable hybrid loss weights for 2 dimensions (94% performance retention), but scaling to 7 dimensions introduces complexity - unclear if contextual bandit learning converges with reasonable sample efficiency.

4. **Single-Method Safety Checker Bypass Vulnerabilities**: Diffusers safety checker and other single-method approaches have known bypass issues, creating single-point-of-failure risks that require ensemble critic architectures for robustness.

5. **Deployment Cost of Domain-Specific Models**: Alternative approach of training separate specialized models per domain (medical, finance, entertainment) incurs 7× deployment cost and maintenance overhead compared to single unified model.

6. **Context-Specific Regulatory Compliance**: Different domains and regions (EU GDPR, China CAC, US frameworks) require distinct safety priorities, but existing approaches lack systematic mapping from regulatory requirements to safety dimension weights.

7. **Cold Start and Convergence Uncertainty**: Contextual bandit meta-controller requires sufficient deployment examples (estimated 1000-5000 per context type) to converge to optimal weight policies, creating performance uncertainty during early deployment phases.
