## Related Work

**Related Papers**

1. **Title**: Gaussian Process Optimization in the Bandit Setting: No Regret and Experimental Design (Srinivas et al. 2010)
   - **Authors**: Srinivas et al.
   - **Summary**: Established GP-UCB algorithm with O(√(γ_T T)) regret bound where γ_T is maximum information gain, providing foundational theoretical framework for Bayesian optimization convergence guarantees.
   - **Year**: 2010

2. **Title**: Coin Betting and Parameter-Free Online Learning (Orabona & Pál 2016)
   - **Authors**: Orabona & Pál
   - **Summary**: Parameter-free online learning achieving optimal regret via coin betting using Krichevsky-Trofimov estimator, enabling adaptive algorithms without hyperparameter tuning.
   - **Year**: 2016

3. **Title**: Online Learning with Feedback Graphs: Beyond Bandits (Alon et al. 2015)
   - **Authors**: Alon et al.
   - **Summary**: Regret bounds Θ(α^1/2 T^1/2) for online learning with feedback graphs and mixture formulation for multi-source integration with provable guarantees.
   - **Year**: 2015

4. **Title**: Efficient Exploration of Chemical Compound Space Using Active Learning for Prediction of Thermodynamic Properties (Xiang et al. 2023)
   - **Authors**: Xiang et al.
   - **Summary**: GPR-MGK algorithm with molecular fingerprints achieves R²>0.99 using only 0.124% of compound space (313/251,728 molecules), demonstrating extreme sample efficiency in molecular design.
   - **Year**: 2023

5. **Title**: Active Learning Exploration of Transition-Metal Complexes (Duan et al. 2022)
   - **Authors**: Duan et al.
   - **Summary**: Consensus across 23 DFT functionals achieves 1000x discovery acceleration in materials science through multi-source integration without theoretical guarantees.
   - **Year**: 2022

6. **Title**: LLM-Augmented Multi-Fidelity Bayesian Optimization (Xia et al. 2025)
   - **Authors**: Xia et al.
   - **Summary**: LVGP framework linking LLM priors with physics simulations for robotics assembly, demonstrating emerging application of LLM-augmented optimization.
   - **Year**: 2025

7. **Title**: Bayesian Optimization for Adaptive Experimental Design: A Review (Greenhill et al. 2020)
   - **Authors**: Greenhill et al.
   - **Summary**: Comprehensive BO review identifying "prior knowledge incorporation" as core challenge, noting that existing work on domain knowledge integration is "mostly heuristic" without theoretical guarantees.
   - **Year**: 2020

8. **Title**: GP-UCB with Unknown Mean Function (Liu & Wang 2022)
   - **Authors**: Liu & Wang
   - **Summary**: GO-UCB algorithm handling unknown mean function in GP with regret bounds under misspecification, addressing parametric function class errors but not domain priors.
   - **Year**: 2022

9. **Title**: Distributionally Robust Bayesian Optimization (Kirschner et al. 2020)
   - **Authors**: Kirschner et al.
   - **Summary**: Minimax regret bounds for worst-case uncertainty sets in adversarial settings, providing pessimistic robustness guarantees.
   - **Year**: 2020

10. **Title**: Probabilistic Model-Agnostic Meta-Learning (Finn et al. 2018)
    - **Authors**: Finn et al.
    - **Summary**: Variational approach to model ambiguity in few-shot learning with parameter distributions, providing framework for representing uncertain priors.
    - **Year**: 2018

11. **Title**: Transformer Neural Processes: Uncertainty-Aware Meta Learning (Nguyen & Grover 2022)
    - **Authors**: Nguyen & Grover
    - **Summary**: Autoregressive likelihood-based objective for uncertainty-aware adaptation, providing uncertainty quantification framework applicable to domain knowledge sources.
    - **Year**: 2022

12. **Title**: Improved Strongly Adaptive Online Learning using Coin Betting (Jun et al. 2016)
    - **Authors**: Jun et al.
    - **Summary**: Strongly adaptive regret bounds in changing environments via coin betting, providing theoretical foundation for detecting and adapting to prior-data mismatch over time.
    - **Year**: 2016

13. **Title**: Accelerating drug discovery with Artificial: a whole-lab orchestration system for self-driving labs (Fehlis et al. 2025)
    - **Authors**: Fehlis et al.
    - **Summary**: Comprehensive orchestration system integrating extensive domain knowledge (chemistry constraints, safety rules) without formal guarantees in real-world drug discovery deployment.
    - **Year**: 2025

14. **Title**: Thompson Sampling for BO (Kandasamy et al. 2018)
    - **Authors**: Kandasamy et al.
    - **Summary**: Bayesian posterior sampling approach achieving O(√(T log T)) regret bound under GP assumptions but ignoring domain structure.
    - **Year**: 2018

15. **Title**: Improved GP-UCB (Chowdhury & Gopalan 2017)
    - **Authors**: Chowdhury & Gopalan
    - **Summary**: Tighter information-theoretic analysis achieving Õ(√T) regret bound with improved constants while remaining purely data-driven.
    - **Year**: 2017

16. **Title**: SafeOpt (Sui et al. 2015)
    - **Authors**: Sui et al.
    - **Summary**: Safety constraints during optimization with probabilistic safety and convergence guarantees, addressing safe exploration but not incorrect priors.
    - **Year**: 2015

17. **Title**: AutoOED Platform
    - **Authors**: yunshengtian (GitHub)
    - **Summary**: Automated optimal experimental design platform with constraint handling framework, providing practical implementation but lacking formal analysis of constraint violations.
    - **Year**: Not specified

18. **Title**: saasbo
    - **Authors**: martinjankowiak (GitHub)
    - **Summary**: Sparse axis-aligned subspace Bayesian optimization for high-dimensional optimization without domain knowledge integration.
    - **Year**: Not specified

**Key Challenges**

1. **Theory-Practice Gap in Domain-Informed BO**: Pure data-driven BO (GP-UCB, Thompson Sampling) provides provable O(√T log T) regret bounds but ignores domain structure leading to sample inefficiency (thousands of evaluations required), while domain-informed BO achieves 100-1000x sample efficiency gains empirically but lacks formal analysis and fails catastrophically when priors are incorrect.

2. **Lack of Robustness Guarantees for Domain Knowledge Integration**: Existing domain-informed methods (GPR-MGK with molecular fingerprints, consensus of DFT functionals, LLM-augmented frameworks) achieve extreme sample efficiency but provide no theoretical guarantees when domain knowledge is partially incorrect or biased, creating risk in high-stakes applications.

3. **Parameter Tuning Requirements in Adaptive Methods**: Existing robust BO methods require careful hyperparameter tuning (learning rates, uncertainty set sizes) which limits practical deployment, while parameter-free approaches exist only for convex settings not applicable to GP/RKHS non-convex optimization.

4. **Multi-Source Knowledge Integration Without Theory**: Real-world applications integrate heterogeneous domain knowledge from multiple sources (physics models, expert features, LLM suggestions) but lack formal framework for assessing source quality and weighting contributions, leading to ad-hoc ensemble methods.

5. **Computational Scalability of Robustness Mechanisms**: Robust BO methods often introduce significant computational overhead (worst-case optimization, multiple model evaluations) that may exceed function evaluation time, limiting applicability to expensive experimental design settings.

6. **Domain Knowledge Formalizability**: Implicit tacit knowledge and expert intuition are difficult to formalize as GP priors or kernel parameters, limiting the scope of domain knowledge that can be integrated into theoretically grounded frameworks.

7. **Detection of Prior-Data Mismatch with Limited Samples**: Early iterations (t<10) in BO provide limited statistical power for detecting prior-data mismatch through posterior predictive checks, potentially delaying adaptive correction of incorrect domain knowledge.

8. **Bounded vs. Adversarial Error Models**: Existing robust methods assume either no misspecification (pure data-driven) or adversarial worst-case errors (distributionally robust), lacking framework for realistic "bounded but non-adversarial" error scenarios where domain knowledge is partially correct.
