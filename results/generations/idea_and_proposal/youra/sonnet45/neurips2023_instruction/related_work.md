## Related Work

**Related Papers**

1. **Title**: Self-Instruct (Wang et al., 2022)
   - **Authors**: Wang et al.
   - **Summary**: Introduced synthetic instruction generation with simple heuristic filtering (length + keyword filtering) that improves over no filtering. Achieved ~55% accuracy on Super-NaturalInstructions benchmark.
   - **Year**: 2022

2. **Title**: EcomGPT (Li et al., 2023)
   - **Authors**: Li et al.
   - **Summary**: Demonstrated volume-only approach with chain-of-task methodology on 2.5M synthetic instructions for domain adaptation in e-commerce, but quality was not systematically controlled.
   - **Year**: 2023

3. **Title**: AlpacaFarm (Dubois et al., 2023)
   - **Authors**: Dubois et al. (Stanford)
   - **Summary**: Used human preference collection (expensive human feedback) on 20K human-labeled examples, achieving 70% AlpacaEval win rate and validating that high-quality preference data transfers to strong performance.
   - **Year**: 2023

4. **Title**: G-Eval (Liu et al., 2023)
   - **Authors**: Liu et al. (Microsoft)
   - **Summary**: Single-dimension LLM-as-judge evaluation using GPT-4 for sequential assessment of coherence, consistency, fluency, and relevance, achieving Spearman 0.514 correlation with humans. Demonstrates quality dimensions vary independently in NLG tasks.
   - **Year**: 2023

5. **Title**: InstructCoder (Li et al., 2023)
   - **Authors**: Li et al.
   - **Summary**: Iterative expansion approach using GitHub commits on 114K examples for code editing tasks, with no systematic quality control but inspired validation set design concepts.
   - **Year**: 2023

6. **Title**: UL2 (Tay et al., 2022)
   - **Authors**: Tay et al.
   - **Summary**: Mixture-of-Denoisers paradigm demonstrating the importance of diversity dimension in training data composition.
   - **Year**: 2022

7. **Title**: MA-RLHF (Chai et al., 2024)
   - **Authors**: Chai et al.
   - **Summary**: Identified credit assignment problem in RLHF showing quality degradation over long sequences, motivating the need for quality monitoring in LLM generators over time.
   - **Year**: 2024

8. **Title**: ISO 2859-1 Acceptance Sampling
   - **Authors**: Not specified
   - **Summary**: Manufacturing quality control standard demonstrating multi-attribute inspection identifies defects in specific dimensions (weight, dimensions, hardness), providing foundation for multi-dimensional quality assessment transfer to instruction data.
   - **Year**: Not specified

9. **Title**: Shewhart Control Charts (1931)
   - **Authors**: Shewhart
   - **Summary**: Foundational manufacturing theory showing control charts detect process degradation 2-3σ before defect rates increase significantly, providing early warning system for quality degradation.
   - **Year**: 1931

**Key Challenges**

1. **Gap in Multi-Dimensional Quality Control**: Existing approaches use either no quality control (EcomGPT volume-only), single-metric heuristics (Self-Instruct), or expensive human feedback (AlpacaFarm). No prior work directly tests multi-dimensional quality filtering impact on instruction-following models.

2. **Quality-Performance Transfer Uncertainty**: Optimizing for proxy quality metrics (clarity, correctness, diversity, etc.) may not improve actual instruction-following capability due to Goodhart's Law / Campbell's Law. Need validation that quality dimensions transfer to downstream performance.

3. **Volume vs. Quality Tradeoff**: Large-scale pre-training literature suggests "more data → better models" (scaling laws), but filtering reduces volume (e.g., 500K → 350K, -30%). Tension between quality improvement and volume reduction needs resolution.

4. **LLM-as-Judge Reliability**: G-Eval demonstrates single-dimension automated assessment achieves only moderate reliability (0.514 correlation with humans). Multi-judge ensemble methods show improvement to 0.75-0.90, but reliability for correctness dimension in multi-dimensional framework requires validation.

5. **Dimension Independence Validation**: Quality dimensions (clarity, correctness, diversity, difficulty, safety) are assumed orthogonal but not empirically validated. If dimensions correlate (|r| ≥ 0.5), multi-dimensional framework collapses to redundant computation.

6. **SPC Transferability to Non-Stationary Processes**: Manufacturing SPC (Shewhart charts) assumes stationary processes, but LLM synthetic generators are non-stationary (Self-Instruct explores task space, MA-RLHF shows quality variation). Adaptation required for dynamic generators through sliding window control limits.

7. **Computational Cost vs. Performance Tradeoff**: Sequential multi-dimensional evaluation (G-Eval approach with 5 dimensions) would cost ~$5,000 for 2.5M examples. Need efficient parallel evaluation maintaining quality assessment reliability while reducing cost.

8. **Threshold Sensitivity and Generalization**: Optimal filtering thresholds (e.g., clarity > 0.7, correctness > 0.8) may be dataset-specific or task-specific, requiring re-tuning for each application and limiting generalizability.

9. **Safety Classifier Limitations**: Safety dimension may miss subtle harmful content (implicit bias, covert toxicity, culturally-specific harms), with false negative rates potentially undermining safety guarantees.

10. **Evaluation Dataset Contamination Risk**: Overlap between training and test sets, model selection bias (cherry-picking best checkpoint), and annotator variability can confound experimental results and require careful control.
