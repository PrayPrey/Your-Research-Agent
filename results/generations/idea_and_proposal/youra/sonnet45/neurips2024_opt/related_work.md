## Related Work

**Related Papers**
1. **Title**: Training Compute-Optimal Large Language Models (Chinchilla) (8342b592fe238f3d230e4959b06fd10153c45db1)
   - **Authors**: Hoffmann et al.
   - **Summary**: Foundation for compute-optimal training; establishes N ∝ C^0.5, D ∝ C^0.5 scaling laws showing optimal model size and training tokens scale with square root of compute budget. Assumes fixed architecture without optimizing architectural hyperparameters jointly with N/D.
   - **Year**: 2022

2. **Title**: Completed Hyperparameter Transfer across Modules, Width, Depth, Batch and Duration (ab4bca3207d370621202c90cc31159cabf043994)
   - **Authors**: Mlodozeniec et al.
   - **Summary**: Demonstrates systematic hyperparameter transfer rules exist across width, depth, batch, duration dimensions (Complete^(d) Parameterisation). Enables per-module hyperparameter optimization and efficient small-to-large transfer.
   - **Year**: 2025

3. **Title**: Adaptive Data Optimization: Dynamic Sample Selection with Scaling Laws (b83bdc85bd041690f13cd3823269b63f3b771306)
   - **Authors**: Jiang et al.
   - **Summary**: Shows per-domain scaling laws enable dynamic optimization during training without proxy models. ADO adjusts data mixture concurrently with training using domain-specific scaling laws to achieve compute-optimal performance.
   - **Year**: 2024

4. **Title**: NAS-HPO-Bench-II: Joint Optimization of CNN Architecture and Training HPs (670db7a1cc4e113ea9957cdf8aae3a40ba3580cf)
   - **Authors**: Hirose et al.
   - **Summary**: First benchmark demonstrating architecture-hyperparameter interdependence using 192K configurations. Confirms joint optimization finds 3.5% better configurations than sequential NAS→HPO for CNNs, though empirical approach lacks scaling law grounding.
   - **Year**: 2021

5. **Title**: Scaling Laws for Neural Language Models
   - **Authors**: Kaplan et al.
   - **Summary**: Original power-law scaling formulation showing N_optimal ∝ C^0.73. Established the power-law framework later revised by Chinchilla, demonstrating systematic relationships between compute, model size, and performance.
   - **Year**: 2020

6. **Title**: Understanding the Mechanisms of Fast Hyperparameter Transfer
   - **Authors**: Ghosh et al.
   - **Summary**: Theoretical framework explaining why μP enables fast hyperparameter transfer. Proves fast transfer is equivalent to useful transfer for compute-optimal grid search, identifying width-stable and width-sensitive trajectory components.
   - **Year**: 2025

7. **Title**: PyTorch Inductor Config (Archon KB)
   - **Authors**: Not specified
   - **Summary**: Hardware-aware optimization demonstrating different architectures have different compute profiles. Shows architectural choices (α) directly affect FLOPs per training step, validating compute accounting considerations.
   - **Year**: Not specified

8. **Title**: Hugging Face Optimum Intel (Archon KB)
   - **Authors**: Not specified
   - **Summary**: Hardware-optimized transformers implementing architecture-optimization co-design for Intel hardware. Demonstrates that architecture and optimization choices interact with hardware characteristics.
   - **Year**: Not specified

**Key Challenges**
1. **Fixed Architecture Assumption in Chinchilla**: Chinchilla scaling laws assume fixed transformer architecture and only optimize model size (N) and training tokens (D), not accounting for architectural hyperparameters like width/depth ratio or attention configuration. This leaves architectural dimensions unexplored in compute-optimal frameworks.

2. **Sequential Optimization Suboptimality**: Current practice follows sequential optimization: first apply Chinchilla for N/D allocation, then independently tune architectural parameters and hyperparameters via grid search or Bayesian optimization. This misses configurations where different architectural choices enable better N/D allocations.

3. **Architecture-Hyperparameter Coupling Unexplored for LLMs**: While Hirose 2021 demonstrated architecture-HP interdependence for CNNs (3.5% improvement from joint optimization), this coupling has not been investigated for LLMs within a scaling law framework.

4. **Power-Law Extension Uncertainty**: Unknown whether Chinchilla's power-law relationships (L ∝ N^(-a) × D^(-b)) extend to architectural dimensions (width/depth ratio, attention heads) and optimization dimensions (learning rate, batch size). Discontinuities could prevent surrogate-based optimization.

5. **Compute Accounting for Diverse Architectures**: C = 6ND formula from Chinchilla may not accurately capture FLOPs across different architectural configurations. Memory bandwidth bottlenecks for wider architectures could violate theoretical compute equivalence, making comparisons unfair.

6. **Sample Complexity for Multi-Dimensional Scaling Laws**: Extending scaling laws from 2D (N, D) to 4D (N, D, α, β) space requires sufficient training runs for accurate surrogate modeling. Uncertainty about whether 100-200 small-scale configurations provide adequate coverage for R² > 0.9 predictions.

7. **Hyperparameter Transfer Validation at Scale**: While Mlodozeniec 2025 demonstrates HP transfer rules exist, applying these as Bayesian priors for LLM scaling law prediction from small models (100M-1B) to target scale (10B+) remains empirically unvalidated.

8. **Hardware Heterogeneity Effects**: Architectural choices interact with hardware characteristics (GPU memory bandwidth, interconnect), as shown in Archon KB cases. Hardware-specific optimizations could confound pure algorithmic performance comparisons.

9. **Optimizer Generalization**: Current research focuses on AdamW optimizer. Unknown whether architecture-optimization coupling generalizes to other optimizers (SGD, Lion, Sophia) that may have fundamentally different loss landscapes.

10. **Validation Loss vs Task Performance Gap**: Compute-optimal frameworks optimize validation loss as proxy metric. The relationship between validation loss improvements and downstream task-specific performance (reasoning, coding, instruction-following) remains indirect.
