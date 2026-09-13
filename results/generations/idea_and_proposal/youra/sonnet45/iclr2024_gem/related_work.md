## Related Work

**Related Papers**

1. **Title**: Thompson Sampling for Gaussian Bandits (Russo et al., 2018)
   - **Authors**: Daniel Russo, Benjamin Van Roy, Abbas Kazerouni, Ian Osband, Zheng Wen
   - **Summary**: Established regret bound O(√T log T) for Thompson Sampling in Gaussian bandits, providing theoretical foundation for probabilistic exploration-exploitation balance in Bayesian optimization.
   - **Year**: 2018

2. **Title**: Thompson Sampling with LLM Reward Prediction (Sun et al., 2025)
   - **Authors**: Sun et al.
   - **Summary**: Demonstrated that Thompson Sampling with large language model reward prediction maintains optimal exploration-exploitation balance in sequential decision-making tasks.
   - **Year**: 2025

3. **Title**: LoRA for Protein Pretrained Language Models (Li et al., 2025)
   - **Authors**: Li et al.
   - **Summary**: Showed that Low-Rank Adaptation (LoRA) with 99% parameter reduction prevents catastrophic forgetting in protein language models when fine-tuning on small datasets, enabling learning from n=50 samples.
   - **Year**: 2025

4. **Title**: Transfer Learning for Target-Specific Ligand Generation (Wang et al., 2023)
   - **Authors**: Wang et al.
   - **Summary**: Demonstrated that transfer learning can generate target-specific ligands from fewer than 100 training samples using fine-tuned generative models.
   - **Year**: 2023

5. **Title**: Kronecker-Factored Laplace Approximation for Bayesian Regularization (Chen & Garner, 2024)
   - **Authors**: Chen, Garner
   - **Summary**: Showed that Kronecker-factored Laplace approximation with KL divergence penalty maintains 95% pre-training accuracy while enabling task-specific adaptation in neural networks.
   - **Year**: 2024

6. **Title**: OPLoRA: Orthogonal Projection Low-Rank Adaptation (Xiong & Xie, 2025)
   - **Authors**: Xiong, Xie
   - **Summary**: Introduced orthogonal projection method for LoRA that mathematically guarantees preservation of pre-training capabilities during fine-tuning via orthogonal decomposition.
   - **Year**: 2025

7. **Title**: Discounted Thompson Sampling in Non-Stationary Multi-Armed Bandits (He et al., 2023)
   - **Authors**: He et al.
   - **Summary**: Proved regret bounds for discounted Thompson Sampling in non-stationary multi-armed bandit settings, demonstrating optimal discount factor balances memory retention versus adaptation to distribution shifts.
   - **Year**: 2023

8. **Title**: Multi-Fidelity Optimization for Materials Discovery (Deshwal, AAAI 2025)
   - **Authors**: Deshwal et al.
   - **Summary**: Demonstrated 40-60% cost reduction in nano-porous materials discovery using multi-fidelity Bayesian optimization with information gain per cost criterion for fidelity selection.
   - **Year**: 2025

9. **Title**: ProteinMPNN: Protein Structure to Sequence Design
   - **Authors**: Dauparas et al. (from reference to dauparas/ProteinMPNN repo)
   - **Summary**: Developed message-passing neural network for protein sequence design from backbone structures, trained on ~150K PDB structures with 52.4% sequence recovery rate on CATH benchmark.
   - **Year**: Not specified

10. **Title**: Chroma: Generative Model for Proteins
    - **Authors**: Generate Biomedicines (from reference to generatebio/chroma)
    - **Summary**: Created generative model for protein design using learned latent representations of protein structure-sequence-function relationships.
    - **Year**: Not specified

11. **Title**: AlphaFold: Protein Structure Prediction
    - **Authors**: Not specified
    - **Summary**: Deep learning system for protein structure prediction used as low-fidelity oracle with 0.6-0.8 correlation to experimental measurements at ~$1/evaluation cost and 10-second latency.
    - **Year**: Not specified

12. **Title**: ESM-IF1: Protein Function Prediction
    - **Authors**: Not specified
    - **Summary**: Evolutionary Scale Modeling inverse folding model used for predicting protein binding affinity and other functional properties from sequence.
    - **Year**: Not specified

13. **Title**: MAGECS: Model-Assisted Gene Editing and Characterization System
    - **Authors**: Not specified
    - **Summary**: Closed-loop experimental design system for biomolecular optimization, used as baseline comparison that does not update generative models during optimization.
    - **Year**: Not specified

**Key Challenges**

1. **Catastrophic Forgetting in Generative Model Fine-Tuning**: Standard full-model retraining on small experimental batches (10-50 samples) causes generative models to forget pre-trained chemical priors, resulting in <80% validity rates and generation of chemically implausible molecules.

2. **Non-Stationary Latent Spaces**: Continuous model retraining shifts the geometry of learned latent embeddings over time, causing historical observations to become outdated and posterior estimates to be overconfident in stale regions.

3. **Sample Inefficiency of Static Models**: Pre-trained generative models without closed-loop adaptation require 30-50% more experimental evaluations to reach optimal performance due to inability to learn from experimental feedback.

4. **Exploration-Exploitation Balance in High-Dimensional Design Spaces**: Traditional Bayesian optimization struggles to balance discovery of novel high-performing regions versus refinement of known good areas in biomolecular latent spaces with hundreds of dimensions.

5. **Experimental Cost in Wet-Lab Validation**: Protein expression, purification, and functional assays cost $500-5000 per candidate with 3-14 day latency, creating severe resource constraints that require strategic allocation between cheap computational predictions and expensive experimental measurements.

6. **Limited Experimental Data**: Biomolecular design campaigns typically generate only 100-500 wet-lab measurements due to cost and time constraints, requiring methods that can learn effectively from small batches without overfitting.

7. **Systematic Integration Gap**: Lack of systematic frameworks that combine adaptive experimental design (Thompson Sampling, Bayesian optimization) with continuous updating of generative biomolecular models in closed-loop systems.
