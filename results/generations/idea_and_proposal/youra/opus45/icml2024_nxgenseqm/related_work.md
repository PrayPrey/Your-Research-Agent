## Related Work

**Related Papers**
1. **Title**: Linking In-context Learning in Transformers to Human Episodic Memory (arXiv:2405.14992)
   - **Authors**: Ji-An Li, Corey Zhou, Marcus K. Benna, Marcelo G. Mattar
   - **Summary**: Demonstrates that induction heads in transformers are behaviorally, functionally, and mechanistically similar to the Context Maintenance and Retrieval (CMR) model from cognitive neuroscience, providing theoretical foundation for connecting neural network mechanisms to human episodic memory.
   - **Year**: 2024

2. **Title**: Mamba: Linear-Time Sequence Modeling with Selective State Spaces
   - **Authors**: Albert Gu, Tri Dao
   - **Summary**: Introduces selective scan mechanism that enables content-based reasoning in state space models while maintaining linear-time complexity, establishing the foundational architecture for efficient sequence modeling.
   - **Year**: 2023

3. **Title**: Is Mamba Capable of In-Context Learning? (arXiv:2402.03170)
   - **Authors**: Riccardo Grazzi, Julien Siems, Simon Schrodi, Thomas Brox, Frank Hutter
   - **Summary**: Investigates Mamba's in-context learning capabilities and finds that it appears to solve ICL problems by incrementally optimizing internal representations during inference.
   - **Year**: 2024

4. **Title**: Mamba Can Learn Low-Dimensional Targets In-Context via Test-Time Feature Learning (arXiv:2510.12026)
   - **Authors**: Junsoo Oh, Wei Huang, Taiji Suzuki
   - **Summary**: Demonstrates that the nonlinear gating mechanism in Mamba is crucial for feature extraction during in-context learning of low-dimensional targets.
   - **Year**: 2025

5. **Title**: Can Mamba Learn How To Learn? A Comparative Study on In-Context Learning Tasks
   - **Authors**: Park et al.
   - **Summary**: Conducts comparative analysis showing that MambaFormer hybrid architectures outperform pure Mamba on in-context learning tasks, establishing performance baselines for ICL evaluation.
   - **Year**: 2024

6. **Title**: Understanding In-Context Learning Beyond Transformers
   - **Authors**: Shenran Wang et al.
   - **Summary**: Reveals that function vectors in Mamba differ from those in Transformers and suggests that Mamba2 may utilize different in-context learning mechanisms than its predecessor.
   - **Year**: 2025

7. **Title**: The Context Maintenance and Retrieval Model of Episodic Memory
   - **Authors**: Howard & Kahana
   - **Summary**: Presents the original CMR computational model that describes how humans maintain and retrieve contextual information in episodic memory, providing the neuroscience foundation for memory-inspired architectures.
   - **Year**: 2002

8. **Title**: MemMamba: Memory-Augmented State Space Model for Defect Recognition
   - **Authors**: Not specified
   - **Summary**: Identifies exponential memory decay as a fundamental weakness in state space models, motivating the need for memory augmentation mechanisms to address long-range dependency limitations.
   - **Year**: 2025

**Key Challenges**
1. **Exponential Memory Decay in SSMs**: State space models suffer from exponential decay of historical information, limiting their ability to maintain and retrieve relevant context over long sequences.
2. **Divergent ICL Mechanisms**: Function vectors and in-context learning mechanisms differ between Mamba variants and Transformers, suggesting that direct architectural translations may not preserve learning capabilities.
3. **Pure Mamba ICL Limitations**: Pure Mamba architectures underperform hybrid approaches (e.g., MambaFormer) on in-context learning tasks, indicating architectural gaps in context utilization.
4. **Lack of Explicit Context Reinstatement**: Current SSM architectures lack mechanisms analogous to human episodic memory's context maintenance and retrieval processes, limiting their ability to leverage relevant historical context during inference.
