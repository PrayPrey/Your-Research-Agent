## Related Work

**Related Papers**
1. **Title**: Some PAC-Bayesian Theorems (McAllester, 1999)
   - **Authors**: McAllester
   - **Summary**: Introduced PAC-Bayesian inequalities connecting KL divergence to generalization, providing the foundation for PAC-Bayesian bound derivation that extends from i.i.d. to query-dependent sampling.
   - **Year**: 1999

2. **Title**: PAC-Bayes with Backprop (Rivasplata et al., 2020)
   - **Authors**: Rivasplata et al.
   - **Summary**: Introduced martingale PAC-Bayes bounds for dependent data in sequential learning, enabling bounds for adaptive, non-i.i.d. data through the martingale property.
   - **Year**: 2020

3. **Title**: Online PAC-Bayes Learning (Haddouche & Guedj, 2022)
   - **Authors**: Haddouche & Guedj
   - **Summary**: First PAC-Bayesian bounds for online learning with dependent data, providing sequential bound framework adapted from passive (adversarial stream) to active (learner queries) setting.
   - **Year**: 2022

4. **Title**: Deterministic PAC-Bayesian bounds for deep networks (Nagarajan & Kolter, 2019)
   - **Authors**: Nagarajan & Kolter
   - **Summary**: Extended PAC-Bayes to deterministic neural networks, enabling PAC-Bayesian analysis of deep active learning with neural network hypothesis classes.
   - **Year**: 2019

5. **Title**: Theory of Disagreement-Based Active Learning (Hanneke, 2014)
   - **Authors**: Hanneke
   - **Summary**: Sample complexity analysis for active learning using disagreement coefficient, providing frequentist analysis baseline using VC dimension and disagreement for comparison with PAC-Bayesian alternatives.
   - **Year**: 2014

6. **Title**: Agnostic Active Learning (Balcan et al., 2009)
   - **Authors**: Balcan et al.
   - **Summary**: Active learning without realizability assumption, introducing approximation error term η = min R(h) in agnostic bounds for cases where the true labeling function is not in the hypothesis class.
   - **Year**: 2009

7. **Title**: Information-Based Objective Functions for Active Data Selection (MacKay, 1992)
   - **Authors**: MacKay
   - **Summary**: Pioneered information gain for query selection, providing historical foundation for information-theoretic criteria now justified through PAC-Bayesian theory.
   - **Year**: 1992

8. **Title**: Bayesian Active Learning by Disagreement (BALD) (Houlsby et al., 2011)
   - **Authors**: Houlsby et al.
   - **Summary**: Introduced mutual information I(Y;θ|x,D) for neural network active learning, providing a heuristic approach now proven optimal in PAC-Bayesian framework for minimizing query-dependent bound terms.
   - **Year**: 2011

9. **Title**: PAC-Bayes Bounds for Bandit Problems: Survey (Flynn et al., 2022)
   - **Authors**: Flynn et al.
   - **Summary**: Comprehensive survey of PAC-Bayesian bandit algorithms providing insights on adaptive sampling in exploration-exploitation settings that inform query selection analysis for active learning.
   - **Year**: 2022

10. **Title**: Deep Bayesian Active Learning with Image Data (Gal et al., 2017)
    - **Authors**: Gal et al.
    - **Summary**: MC Dropout for uncertainty estimation in active learning, providing tractable variational approximation method for bound computation in neural networks.
    - **Year**: 2017

11. **Title**: PAC-Bayesian Reinforcement Learning Trains Generalizable Policies (Zitouni et al., 2025)
    - **Authors**: Zitouni et al.
    - **Summary**: PAC-Bayesian generalization bound for RL with Markov dependencies, parallel work addressing RL while this work addresses active learning, demonstrating PAC-Bayes extends to interactive settings.
    - **Year**: 2025

12. **Title**: PAC-Bayesian bounds for neural networks (Dziugaite & Roy, 2017)
    - **Authors**: Dziugaite & Roy
    - **Summary**: Showed effective dimension for neural networks is much smaller than parameter count, enabling non-vacuous PAC-Bayesian bounds for over-parameterized networks.
    - **Year**: 2017

13. **Title**: Bayesian uncertainty estimation using dropout (Gal & Ghahramani, 2016)
    - **Authors**: Gal & Ghahramani
    - **Summary**: Showed variational methods approximate true posterior well for neural networks using Monte Carlo Dropout, enabling tractable Bayesian inference for deep learning.
    - **Year**: 2016

14. **Title**: Simple and Scalable Predictive Uncertainty Estimation using Deep Ensembles (Lakshminarayanan et al., 2017)
    - **Authors**: Lakshminarayanan et al.
    - **Summary**: Deep Ensembles method for approximate Bayesian posterior estimation, providing an alternative variational approximation approach for neural network uncertainty quantification.
    - **Year**: 2017

15. **Title**: PAC Learning (Valiant, 1984)
    - **Authors**: Valiant
    - **Summary**: Standard realizability assumption in learning theory enabling tight analysis, assuming true labeling function belongs to hypothesis class for sample complexity bounds.
    - **Year**: 1984

16. **Title**: Statistical Learning Theory (Vapnik, 1998)
    - **Authors**: Vapnik
    - **Summary**: PAC learning framework requiring bounded capacity (VC dimension) for generalization, foundational work for sample complexity analysis.
    - **Year**: 1998

**Key Challenges**
1. **Query-Dependent Sampling Gap**: Prior PAC-Bayesian theory (McAllester 1999, Rivasplata 2020) addresses i.i.d. or passively sampled sequential data, but no prior work combines PAC-Bayesian sample complexity analysis with active learning's adaptive query selection.

2. **Theoretical Justification for BALD**: Information-theoretic active learning methods (MacKay 1992, BALD 2011) are used heuristically in practice but lack theoretical guarantees connecting query selection to PAC-Bayesian generalization bounds.

3. **Martingale Extension to Active Learning**: Extending martingale PAC-Bayes framework to settings where the learner controls data distribution (active learning) requires careful definition of filtration to account for learner's control over sampling.

4. **Computational vs. Label Cost Trade-off**: Information gain maximization requires computing expected information for each candidate query with complexity O(|pool| × |hypothesis space|) per query, potentially offsetting label cost savings.

5. **Variational Approximation Error**: Tractable computation of PAC-Bayesian bounds for neural networks requires approximating intractable posteriors, introducing approximation error that compounds in both bound computation and query selection quality.

6. **Realizability Restriction**: Tight O(d log(1/δ)/ε²) sample complexity bounds require the restrictive realizability assumption that the true labeling function belongs to the hypothesis class, limiting applicability to deep learning where model capacity is constrained.

7. **Effective VC Dimension for Neural Networks**: Neural networks with millions of parameters may have very large effective dimension, potentially leading to vacuous PAC-Bayesian bounds unless effective dimension is much smaller than parameter count.

8. **Prior Sensitivity**: PAC-Bayesian bounds depend on KL(Q||P) divergence, where poor prior choice leads to large KL term and loose bounds, requiring principled prior selection strategies.
