# Related Work

Our work sits at the intersection of multi-objective optimization for code generation, multi-task learning with disentanglement, and empirical validation of architectural assumptions. We position our contribution as providing the empirical foundation that prior architectural work assumed but did not validate.

## Multi-Objective Code Generation

Recent advances in code generation have focused primarily on single-objective optimization—correctness measured through unit test execution. **PPOCoder** [Shojaee et al., 2023] pioneered execution-based reinforcement learning, using PPO with compilation feedback and functional correctness rewards to achieve significant improvements on HumanEval and MBPP benchmarks. **CodeRL** [Le et al., 2022] similarly leverages RL with execution feedback for program synthesis. These approaches are task-agnostic and model-agnostic, establishing execution-based RL as a standard paradigm.

However, production code generation requires optimizing multiple objectives beyond correctness: security (no vulnerabilities), quality (maintainability, style adherence), and efficiency (runtime performance). The standard approach to multi-objective optimization uses **weighted reward combinations** with manual weight tuning per domain [Srivastava & Aggarwal, 2025; ReTool, Feng et al., 2025]. Practitioners tune 4D weight vectors (w_correctness, w_quality, w_security, w_efficiency) through grid search or Bayesian optimization, training separate models to approximate the Pareto frontier.

Recent work has proposed **architectural factorization** as an alternative. **Wong & Tan [2025]** apply RLHF with crowd-sourced feedback for code generation, using Bayesian optimization to integrate human preferences across multiple quality dimensions. **PairCoder** [Zhang et al., 2024] introduces navigator-driver agent collaboration with feedback-driven refinement, achieving 12-162% relative improvements through multi-plan exploration. These methods implicitly assume that quality objectives can be decomposed into architectural modules—an assumption our work questions empirically.

**Our contribution:** We validate whether the data exhibits structure justifying architectural factorization. Prior work borrowed multi-task learning intuitions without empirical validation. If separability doesn't exist in real code modifications, simpler weighted methods are empirically justified, not merely convenient defaults.

## Multi-Task Learning and Disentanglement

The architectural factorization approach for code draws heavily from multi-task learning literature in vision and NLP, where task-specific subspaces with orthogonality constraints have proven effective. Standard MTL architectures assume shared encoders with task-specific heads [Caruana, 1997; Ruder, 2017], often with **orthogonality regularization** to prevent task interference [Liu et al., 2019; OrthoReg].

Recent work on **Pareto Multi-Task Learning** [Lin et al., 2019; MGDA] demonstrates that tasks can conflict even when metrics are independent, requiring careful gradient balancing. **PCGrad** [Yu et al., 2020] projects conflicting gradients to prevent negative transfer. These methods assume task conflict exists but don't validate whether empirical separability justifies architectural complexity.

The **disentanglement literature** [Bengio et al., 2013; β-VAE] seeks to learn representations where latent dimensions correspond to interpretable factors of variation. Applied to multi-objective alignment, this suggests learning aspect-specific subspaces (security representations orthogonal to efficiency representations). However, disentanglement success stories come from domains with known ground-truth factors (image rotation, color, scale). Whether code quality aspects have analogous structure is an empirical question.

**Limitation:** Multi-task learning methods assume task-specific subspaces exist and architectural constraints enforce separation. Our contribution is testing this assumption for code through spectral analysis. If quality dimensions are inherently entangled (spherical geometry), imposing orthogonality is arbitrary rather than data-driven. We find that while metrics are independent by construction (distinct measurement tools), code modifications don't exhibit directional alignment—suggesting architectural orthogonality may be redundant.

## Empirical Validation of Architectural Assumptions

Prior work on multi-objective code generation has proceeded directly from architectural intuition to system design, without validating the empirical separability assumption. **PPOCoder** optimizes correctness; extending to multi-objective would require validating whether quality aspects factor cleanly. **Weighted RL methods** assume objective conflict and tune weights, but don't test whether factorization offers advantages. **Multi-task learning** borrows from vision/NLP without checking if code exhibits similar structure.

A notable exception is **MORL (Multi-Objective Reinforcement Learning)** survey work [Hayes et al., 2022; Roijers & Whiteson, 2017], which acknowledges that objective conflict must be empirically characterized per domain. However, this literature focuses on gradient-level conflict, not outcome-space geometry. Our spectral analysis addresses a complementary question: do human expert modifications exhibit aspect-dominant directional structure that would justify architectural factorization?

**Our position:** Empirical validation should precede architectural commitment. We test the foundational assumption through large-scale spectral analysis with rigorous statistical validation (permutation testing, cross-validation). Our negative result—independence without factorization—suggests that simpler architectures (weighted scalarization) are not just convenient but empirically grounded. The field can now make informed architectural choices based on data rather than borrowed intuitions.

## Quality Metrics for Code

Our analysis relies on automated quality metrics across four dimensions. **Correctness** is measured through test execution (pytest/jest pass rates), a standard approach in code generation evaluation [HumanEval, MBPP benchmarks]. **Quality** uses SonarQube maintainability ratings, which aggregate code smells, complexity, and duplication metrics. **Security** employs CodeQL static analysis to detect vulnerabilities (SQL injection, XSS, path traversal). **Efficiency** leverages pytest-benchmark to measure runtime performance.

These tools are widely adopted in software engineering practice, but their reliability and construct validity for research purposes is underexplored. Prior work [Johnson et al., 2013; Chowdhury & Hindle, 2021] has validated static analysis tools against expert judgment with moderate agreement (κ≈0.6). Our work acknowledges metric reliability as a limitation—without Phase 0 validation (ICC≥0.8, r≥0.7 with expert ratings), we cannot rule out measurement artifacts. However, our finding of low coupling (0.072) despite potential noise suggests metrics do measure distinct constructs, even if imperfectly.

## Commit-Level Analysis of Code Changes

Analyzing commit-level code modifications to understand developer behavior has precedent in mining software repositories [Hassan, 2008; Zimmermann et al., 2012]. Prior work has studied commit message quality [Jiang & McCall, 2013], refactoring patterns [Murphy-Hill et al., 2012], and bug-fix characteristics [Pan et al., 2009]. However, these studies focus on categorical classification or frequency analysis, not covariance structure across quality dimensions.

The closest related work is **empirical studies of code quality evolution** [Marinescu, 2012; Alves et al., 2010], which track metric trajectories over project history. These studies find that quality metrics can improve or degrade independently, supporting our independence finding. However, they don't test for aspect-dominant directional structure or employ spectral methods. Our contribution is applying rigorous geometric analysis (eigendecomposition, permutation testing) to quantify the absence of factorization.

## Summary

Existing work on multi-objective code generation borrows architectural patterns from multi-task learning without empirical validation of separability assumptions. Weighted RL methods are standard practice but lack theoretical justification beyond convenience. Disentanglement literature suggests aspect-specific subspaces may help, but evidence comes from different domains. Our contribution: systematic empirical study showing independence does not imply factorization for code, redirecting research toward simpler, empirically justified methods or alternative structural hypotheses (contextual, hierarchical, temporal).
