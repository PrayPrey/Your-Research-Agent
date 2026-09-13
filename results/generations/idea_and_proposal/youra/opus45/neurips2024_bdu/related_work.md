## Related Work

**Related Papers**
1. **Title**: GIT-BO: High-Dimensional Bayesian Optimization with Tabular Foundation Models
   - **Authors**: Yu, Picard, Ahmed
   - **Summary**: Demonstrates that TabPFN v2 enables zero-shot Bayesian optimization without retraining and scales to 500 dimensions using gradient-based active subspace methods.
   - **Year**: 2025

2. **Title**: LLM-BI: Towards Fully Automated Bayesian Inference with LLMs
   - **Authors**: Huang
   - **Summary**: Shows that large language models can successfully elicit priors from natural language descriptions for Bayesian regression tasks.
   - **Year**: 2025

3. **Title**: Eliciting the Priors of Large Language Models using Iterated In-Context Learning
   - **Authors**: Zhu, Griffiths
   - **Summary**: Demonstrates that GPT-4 priors qualitatively align with human priors across multiple domains, providing theoretical justification for using LLM-derived priors.
   - **Year**: 2024

4. **Title**: SAASBO
   - **Authors**: Not specified
   - **Summary**: Proposes sparse axis-aligned Gaussian processes for high-dimensional Bayesian optimization.
   - **Year**: Not specified

5. **Title**: TuRBO
   - **Authors**: Not specified
   - **Summary**: Introduces trust region Bayesian optimization with local modeling for improved performance in high-dimensional spaces.
   - **Year**: Not specified

6. **Title**: Predictive Coding Enhances Meta-RL
   - **Authors**: Not specified
   - **Summary**: Shows that predictive coding modules can generate Bayes-optimal belief representations, providing cross-domain inspiration for hierarchical architectures.
   - **Year**: 2025

7. **Title**: Direct Regret Optimization in Bayesian Optimization
   - **Authors**: Not specified
   - **Summary**: Demonstrates that directly targeting regret minimization outperforms separate acquisition function and surrogate model design approaches.
   - **Year**: 2025

**Key Challenges**
1. **Scalability to High Dimensions**: Existing Bayesian optimization methods struggle to scale effectively to high-dimensional search spaces, requiring specialized techniques like active subspaces or sparse representations.

2. **Prior Specification**: Traditional Bayesian optimization requires manual prior specification, which is difficult and domain-expertise dependent; automated prior elicitation from natural language remains an emerging area.

3. **Separate Acquisition and Surrogate Design**: Conventional approaches treat acquisition function design and surrogate modeling as separate problems, which may be suboptimal compared to directly optimizing for regret minimization.

4. **Zero-Shot Generalization**: Achieving effective Bayesian optimization without task-specific retraining remains challenging, limiting practical applicability across diverse optimization problems.
