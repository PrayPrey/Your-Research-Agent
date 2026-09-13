## Related Work

**Related Papers**
1. **Title**: Construction of the Literature Graph in Semantic Scholar (Paper ID: 649def34f8be52c8b66281af98ae884c09aef38b)
   - **Authors**: Ammar et al. (24 authors from Allen Institute for AI)
   - **Summary**: This paper describes the construction of Semantic Scholar's literature graph by reducing it into familiar NLP tasks, pointing out research challenges and reporting empirical results. The heterogeneous graph contains 280M+ nodes including papers, authors, entities, and citations, demonstrating scalability of metadata-rich platforms with quality signals.
   - **Year**: 2018

2. **Title**: Reincarnating Reinforcement Learning (Referenced throughout as "Reincarnating RL paper")
   - **Authors**: Not specified
   - **Summary**: Paper motivating the need for compute democratization in RL research, identifying high compute costs (estimated $10K+) as entry barriers and proposing artifact reuse to reduce costs to ~$100 fine-tuning expenses.
   - **Year**: Not specified

3. **Title**: LLM Post-Training Survey (DOI: 10.48550/arXiv.2501.01931)
   - **Authors**: Not specified
   - **Summary**: Attempted reference for infrastructure importance in LLM success, but paper was not found in search (may be too recent or DOI incorrect).
   - **Year**: 2025

4. **Title**: TRL (Transformer Reinforcement Learning) library (Referenced as Hugging Face success case)
   - **Authors**: Not specified
   - **Summary**: NLP model sharing platform that reduced friction from manual GitHub uploads to one-click downloads, enabling 10K+ community growth. Demonstrates how infrastructure can accelerate community adoption through standardized sharing.
   - **Year**: Not specified

**Key Challenges**
1. **Compute Access Barriers**: RL research requires significant computational resources ($10K+ for training), creating barriers for researchers without large compute budgets and limiting democratization of research.

2. **Artifact Sharing Friction**: Existing sharing mechanisms (GitHub, manual uploads) create high friction for sharing trained RL policies and datasets, preventing effective reuse of prior computation across the community.

3. **Cross-Framework Compatibility**: RL artifacts are typically framework-specific (PyTorch, JAX, TensorFlow), creating lock-in barriers that limit artifact reuse across different research groups using different frameworks.

4. **Quality Verification Challenges**: Lack of standardized quality certification for shared artifacts creates trust issues, as researchers cannot easily verify reliability of shared computation without independent validation.

5. **Infrastructure Sustainability**: Previous attempts at research infrastructure platforms struggle with long-term sustainability due to unclear funding models and lack of institutional commitment.

6. **Incentive Alignment**: Researchers lack academic incentives to share artifacts, as current academic reward systems (citations, publications) do not adequately credit artifact contributions.

7. **Decentralization vs Centralization Trade-off**: Choice between centralized storage (simpler, faster like AWS S3) versus decentralized storage (more trustworthy like IPFS) involves complex trade-offs in performance, cost, and community trust.

8. **Platform Democratization Failures**: General challenge of ensuring infrastructure platforms truly democratize access rather than concentrating usage among well-resourced institutions (referenced in Archon KB search, but limited specific evidence found).
