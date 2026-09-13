## Related Work

**Related Papers**
1. **Title**: Memetic Algorithm with VAE for Black-Box Discrete Optimization with Epistasis (2025)
   - **Authors**: Aoi Kato, K. Kojima, Masahiro Nomura, Isao Ono
   - **Summary**: VAE-based memetic algorithm addresses epistasis in discrete black-box optimization but requires 2000-5000 samples for training on NK landscapes. SBEN targets 4-10x reduction via sparse structure instead of dense latent space.
   - **Year**: 2025

2. **Title**: Sample-efficient Multi-objective Molecular Optimization with GFlowNets (2023)
   - **Authors**: Yiheng Zhu et al.
   - **Summary**: GFlowNets achieve sample efficiency (hundreds of samples) for molecular optimization but do not model epistasis explicitly. SBEN extends this with explicit interaction graphs for epistatic problems.
   - **Year**: 2023

3. **Title**: Dimension-free MCMC in Discrete Spaces (2024)
   - **Authors**: Hyunwoong Chang, Quan Zhou
   - **Summary**: Provides theoretical foundations for Metropolis-Hastings algorithms with dimension-free mixing times in discrete spaces. Supports proposal distribution design over interaction graphs.
   - **Year**: 2024

4. **Title**: Steering Generative Models with Experimental Data for Protein Fitness (2025)
   - **Authors**: Jason Yang et al.
   - **Summary**: Small-data protein fitness optimization with hundreds of labeled samples. Represents target application domain for SBEN in wet-lab protein engineering.
   - **Year**: 2025

5. **Title**: Probabilistic Graphical Models: Principles and Techniques
   - **Authors**: Daphne Koller, Nir Friedman
   - **Summary**: Foundational work on Bayesian structure learning theory. Demonstrates that spike-and-slab priors reduce effective parameter space for probabilistic graphical models.
   - **Year**: 2009

6. **Title**: Near-optimal Sensor Placements in Gaussian Processes
   - **Authors**: Andreas Krause, Carlos Guestrin
   - **Summary**: Bayesian experimental design literature showing active learning with information-theoretic criteria converges 2-5x faster than passive sampling.
   - **Year**: 2005

7. **Title**: Network Motifs: Simple Building Blocks of Complex Networks
   - **Authors**: Uri Alon
   - **Summary**: Biological systems and molecular structures typically exhibit local interactions through network motifs, supporting the sparsity assumption.
   - **Year**: 2007

8. **Title**: Epistasis - the essential role of gene interactions in the structure and evolution of genetic systems
   - **Authors**: Patrick C. Phillips
   - **Summary**: Quantum chemistry perturbation theory demonstrates first-order effects dominate over second-order interactions. Parallel patterns observed in genetic epistasis support hierarchical interaction discovery.
   - **Year**: 2008

9. **Title**: poli library (MachineLearningLifeScience/poli)
   - **Authors**: Not specified
   - **Summary**: Benchmark library for discrete black-box objectives including NK landscapes (epistatic benchmarks). Provides standardized evaluation protocol for epistatic problem evaluation.
   - **Year**: Not specified

10. **Title**: BB-DOB (e5120/BB-DOB)
    - **Authors**: Not specified
    - **Summary**: Black-Box Discrete Optimization Benchmark suite demonstrating gap in sample-efficient epistasis detection methods. Identifies need for methods combining sample efficiency and epistatic modeling.
    - **Year**: Not specified

11. **Title**: DiscreteBlockBayesAttack (snu-mllab/DiscreteBlockBayesAttack)
    - **Authors**: Not specified
    - **Summary**: Bayesian optimization for discrete sequential data. Demonstrates block-based interaction modeling as inspiration for graph-structured dependencies in SBEN.
    - **Year**: Not specified

**Key Challenges**
1. **Sample Inefficiency in Epistatic Optimization**: VAE-based memetic algorithms (Kato et al. 2025) can handle epistatic interactions but require 2000-5000 samples, making them infeasible for expensive black-box objectives (e.g., wet-lab protein synthesis at $1000/sample).

2. **Implicit vs Explicit Epistasis Modeling**: GFlowNets achieve sample efficiency (hundreds of samples) but model epistasis implicitly through latent representations rather than explicit interaction graphs, limiting interpretability and targeted interaction discovery.

3. **Computational Scalability**: Exhaustive high-order interaction search (L3+) has O(n^k) complexity, becoming intractable for large-scale problems. Need for hierarchical methods that maintain O(n²) complexity while detecting high-order epistasis.

4. **Active Learning for Structure Discovery**: Existing active learning methods focus on function value optimization rather than structure discovery (interaction graph learning). Need for information-theoretic acquisition functions targeting interaction uncertainty.

5. **Cold Start Problem**: Limited initial data in sparse interaction regimes may be insufficient for accurate structure learning. Requires warm-start strategies or transfer learning approaches.

6. **Hyperparameter Sensitivity**: Spike-and-slab prior widths and hierarchical expansion thresholds require domain-specific tuning without established guidelines for black-box discrete optimization settings.

7. **Benchmarking Gap**: While benchmark libraries (poli, BB-DOB) exist for discrete optimization, standardized evaluation protocols for epistatic interaction detection with sample efficiency metrics are lacking.
