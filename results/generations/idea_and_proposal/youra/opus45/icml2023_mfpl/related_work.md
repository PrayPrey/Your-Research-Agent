## Related Work

**Related Papers**
1. **Title**: Efficient Shapley Value Driven Federated Learning System for Smart Grid
   - **Authors**: Qinqin Wu, Yaoxin Pan, Famao Mei, Mingxin Lu
   - **Summary**: Validates that Shapley values ensure fair and transparent evaluation of participant contributions in ML federated settings and provides efficient Monte Carlo approximation methods applicable to gradient-based approaches.
   - **Year**: 2024

2. **Title**: Fairness in Preference Queries: Social Choice Theories Meet Data Management
   - **Authors**: Senjuti Basu Roy, B. Schieber, Nimrod Talmon
   - **Summary**: Establishes theoretical bridge between social choice fairness principles and preference aggregation methods, validating applicability of game-theoretic fairness to preference learning.
   - **Year**: 2024

3. **Title**: Safe RLHF: Safe Reinforcement Learning from Human Feedback
   - **Authors**: Dai et al.
   - **Summary**: Demonstrates constrained optimization approach in RLHF using Lagrangian methods and shows that reward-level constraints propagate to policy behavior.
   - **Year**: 2023

4. **Title**: Private Data Valuation and Fair Payment in Data Marketplaces
   - **Authors**: Zhihua Tian et al.
   - **Summary**: Validates Shapley-based data valuation with efficient approximation algorithms and demonstrates Shapley's effectiveness for fair contribution measurement in ML contexts.
   - **Year**: 2022

5. **Title**: Training a Helpful and Harmless Assistant with RLHF
   - **Authors**: Bai et al. (Anthropic)
   - **Summary**: Foundational RLHF methodology establishing preference dataset structure and alignment training paradigm that serves as the basis for subsequent preference optimization methods.
   - **Year**: 2022

6. **Title**: FARO (Fairness Aware Reward Optimization) (arXiv:2602.07799)
   - **Authors**: Not specified
   - **Summary**: Proposes in-processing fairness constraints approach for reward optimization in preference learning settings.
   - **Year**: 2026

7. **Title**: GRPO (Group Robust Preference Optimization) (arXiv:2405.20304)
   - **Authors**: Not specified
   - **Summary**: Introduces group-robust optimization via minimax formulation for preference optimization, addressing fairness through robust optimization paradigm.
   - **Year**: 2024

8. **Title**: HELM Framework (arXiv:2601.19197)
   - **Authors**: Not specified
   - **Summary**: Demonstrates that advanced LLMs like GPT-4 exhibit significant popularity bias (Gini coefficient 0.73) compared to traditional collaborative filtering (0.58), establishing measurement frameworks for bias in LLM systems.
   - **Year**: 2026

9. **Title**: Open Problems and Fundamental Limitations of RLHF
   - **Authors**: Casper et al.
   - **Summary**: Comprehensive survey documenting limitations of current RLHF methods, identifying demographic bias as an open problem without established solutions.
   - **Year**: 2023

**Key Challenges**
1. **Lack of Fairness Integration in RLHF**: Current RLHF methods lack established mechanisms for integrating fairness considerations, with demographic bias identified as an open problem without solutions.
2. **Popularity Bias in LLM Preference Learning**: Advanced LLMs exhibit significant popularity bias compared to traditional methods, demonstrating the need for fairness integration in LLM preference learning.
3. **Fair Contribution Measurement**: Existing approaches lack principled methods for measuring and weighting contributions from different demographic groups or data sources in preference learning.
4. **Theoretical Guarantees for Fairness**: Current fairness-aware approaches like in-processing constraints and minimax formulations may lack strong theoretical guarantees compared to game-theoretic foundations like Shapley values.
