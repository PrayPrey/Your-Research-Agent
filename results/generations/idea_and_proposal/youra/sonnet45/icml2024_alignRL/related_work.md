## Related Work

**Related Papers**

1. **Title**: Optimistic posterior sampling for reinforcement learning: worst-case regret bounds (Agrawal & Jia, 2022) (b799c782f168b0a02ebab9e50ff38ded1bc79aee)
   - **Authors**: Agrawal, Jia
   - **Summary**: Presents algorithm based on posterior sampling that achieves near-optimal worst-case regret bounds Õ(√DSAT) for Thompson sampling in communicating MDPs with finite diameter D. Proof appendix provides explicit constant derivations through Hoeffding and Azuma concentration inequalities.
   - **Year**: 2022

2. **Title**: Episodic Reinforcement Learning in Finite MDPs: Minimax Lower Bounds Revisited (Domingues et al., 2020) (0b0c82e33d3328246b6adc3ef2b55be9b606a0cd)
   - **Authors**: Domingues et al.
   - **Summary**: Establishes novel lower bound Ω((H³SA/ε²)log(1/δ)) on sample complexity for PAC algorithms and rigorous proof of Ω(√(H³SAT)) regret bound. Shows minimax lower bounds are tight up to poly-log factors and demonstrates parameter-dependent performance regimes.
   - **Year**: 2020

3. **Title**: Theoretical Guarantees of Fictitious Discount Algorithms for Episodic Reinforcement Learning and Global Convergence of Policy Gradient Methods (Guo et al., 2021) (24fda3cbf8b776aea69ef4f2d5ef11f92d3d4011)
   - **Authors**: Guo et al.
   - **Summary**: Provides first theoretical guarantee for fictitious discount methods widely used in practice, establishing non-asymptotic convergence guarantees for vanilla policy gradient variants with discounted advantage estimations. Demonstrates computational tractability of finite-horizon regret formulas computable in polynomial time for specific S,A,H,T.
   - **Year**: 2021

4. **Title**: UCB-VI (referenced in Domingues 2020)
   - **Authors**: Not specified
   - **Summary**: Upper Confidence Bound Value Iteration algorithm with formal regret bounds for episodic MDPs. Used as baseline comparison for algorithm selection based on regret predictions.
   - **Year**: Not specified

5. **Title**: UCRL2 (Jaksch 2010)
   - **Authors**: Jaksch et al.
   - **Summary**: Upper Confidence Reinforcement Learning algorithm with approximately 500 citations, providing formal regret bounds for tabular RL settings.
   - **Year**: 2010

6. **Title**: Model-based UCB (Azar 2017)
   - **Authors**: Azar et al.
   - **Summary**: Model-based Upper Confidence Bound approach with approximately 200 citations, providing theoretical guarantees for model-based reinforcement learning.
   - **Year**: 2017

**Key Challenges**

1. **Theory-Practice Translation Gap**: Traditional RL theory compares algorithms asymptotically (e.g., "both are Õ(√T)"), hiding constants and making practical comparison impossible. No existing tool systematically converts theoretical bounds into practical algorithm selection guidance.

2. **Instance-Specific Prediction Absence**: Existing resources compare algorithms asymptotically (Õ notation) or empirically (specific environments), but lack capability to predict "for MY problem size (S=100, A=10, H=50)".

3. **Inaccessible Concrete Constants**: Constants buried in proof appendices remain inaccessible to practitioners, preventing quantitative comparison beyond big-O analysis.

4. **Worst-Case vs Average-Case Mismatch**: Theoretical bounds are worst-case (adversarial MDPs) while practitioners operate in benign average-case environments. Bounds may be 10x-100x loose, potentially breaking predictive power for practical algorithm selection.

5. **Limited Algorithm Coverage with Formal Bounds**: Deep RL algorithms (PPO, SAC, DQN) lack formal regret bounds, limiting the scope of theory-based algorithm selection to tabular settings with discrete state/action spaces.

6. **Constant Extraction Accuracy**: Automated extraction of constants from complex proofs (e.g., concentration inequalities over martingales) faces challenges with LLM parsing accuracy and handling of multi-parameter constants vs scalar constants.

7. **Validation Generalization**: Validation limited to benchmark environments (~50 MDPs in OpenRL Benchmark) may not generalize to real-world MDPs with different characteristics (non-stationary, partial observability, extremely large state spaces).

8. **Bound Looseness Impact on Rankings**: Even if worst-case bounds are tight asymptotically, constant looseness (10x-100x) in finite-time regimes could cause theoretical rankings to diverge from empirical performance, breaking the correlation needed for practical algorithm selection.
