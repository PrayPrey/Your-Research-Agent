## Related Work

**Related Papers**
1. **Title**: How Faithful are Self-Explainable GNNs?
   - **Authors**: Christiansen, M., Villadsen, L., Zhong, Z., Teso, S., & Mottin, D.
   - **Summary**: Identifies faithfulness problem in ante-hoc models, showing that self-explainable GNNs have faithfulness limitations where explanations don't always reflect actual model reasoning. Motivates the need for systematic verification methodologies.
   - **Year**: 2023

2. **Title**: Towards Better Understanding Attribution Methods
   - **Authors**: Rao, S., Bohle, M., & Schiele, B.
   - **Summary**: Introduces evaluation metrics for attribution faithfulness including DiFull, ML-Att, and AggAtt schemes for measuring explanation quality. Demonstrates quantitative faithfulness metrics when ground-truth is available.
   - **Year**: 2022

3. **Title**: Ante-Hoc Methods for Interpretable Deep Models: A Survey (Recent Advances in AI)
   - **Authors**: Di Marino, A., Bevilacqua, V., Ciaramella, A., De Falco, I., & Sannino, G.
   - **Summary**: Comprehensive survey of ante-hoc interpretable methods revealing the difficulty of interpreting internal behavior of deep models and the need for strong interpretability. Identifies evaluation gap across all ante-hoc methods.
   - **Year**: 2025

4. **Title**: Verification & Validation Methods for Complex AI-enabled Cyber-Physical Learning-Based Systems: A Systematic Literature Review (Engineering Applications of AI)
   - **Authors**: Meyer, W., & Oosthuizen, R.
   - **Summary**: Systematic review of V&V methods for AI systems from systems engineering domain. Introduces test oracle methodology where systems are verified against known specifications. Demonstrates that synthetic testing can predict real performance when test oracles are well-designed.
   - **Year**: 2023

5. **Title**: Revolutionizing Validation and Verification: Explainable Testing Methodologies for Intelligent Automotive Decision-Making Systems (IEEE Transactions on Intelligent Vehicles)
   - **Authors**: Eris, H., & Wagner, S.
   - **Summary**: Presents explainable test scenarios with automated oracle checking for automotive safety systems. Demonstrates automated verification pipeline for autonomous systems with safety oracles.
   - **Year**: 2025

6. **Title**: Exploring Effectiveness of Explanations for Appropriate Trust: Lessons from Cognitive Psychology (IJCAI)
   - **Authors**: Verhagen, R., Mehrotra, S., Neerincx, M.A., Jonker, C., & Tielman, M.
   - **Summary**: Investigates multi-faceted explanation assessment from cognitive psychology perspective, showing that explanation quality includes perception, semantics, and intent dimensions, not just technical accuracy. Recognizes that technical faithfulness does not equal user understanding.
   - **Year**: 2022

**Key Challenges**
1. **Ante-hoc Faithfulness Verification Gap**: No systematic verification framework exists for ante-hoc interpretable models. Current evaluation relies on inconsistent methods including qualitative inspection, post-hoc comparison, or no unified verification standard.

2. **Synthetic-Real Transfer Uncertainty**: Existing synthetic XAI benchmarks (e.g., CLEVR-XAI, synthetic MNIST) lack empirical validation that synthetic faithfulness predicts real-world faithfulness. Transfer is assumed but not tested systematically.

3. **Domain-Specific Evaluation Gap**: XAI for scientific applications is evaluated with generic metrics (deletion, insertion) without domain alignment to physics laws, chemical principles, or clinical guidelines. No framework integrates scientific domain knowledge into verification.

4. **Circular Dependency in Post-Hoc Comparison**: Current ante-hoc evaluation often compares ante-hoc explanations to post-hoc methods (SHAP, LIME), which creates circular reasoning since post-hoc methods have their own faithfulness issues.

5. **Scalability vs. Objectivity Trade-off**: Qualitative assessment is subjective and not scalable, while quantitative methods require expensive expert validation on real data without ground-truth explanations for verification.

6. **Explanation Gaming Risk**: Models may generate plausible but unfaithful explanations, providing false confidence while maintaining opacity. This makes unfaithful ante-hoc models more dangerous than black boxes.

7. **Cost Barrier for Expert Validation**: Real-world faithfulness validation requires extensive domain expert time for annotation and assessment, creating a barrier for systematic evaluation across multiple model variants.
