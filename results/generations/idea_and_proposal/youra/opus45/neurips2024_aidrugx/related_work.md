## Related Work

**Related Papers**
1. **Title**: AIDO.RNA: A Large-Scale Foundation Model for RNA Function and Structure Prediction
   - **Authors**: Zou et al.
   - **Summary**: A 1.6B parameter model trained on 42M ncRNA sequences that achieves state-of-the-art performance on structure prediction, demonstrating that large-scale RNA language models can capture functional properties.
   - **Year**: 2024

2. **Title**: Improving the Hit Rates of Virtual Screening by Active Learning from Bioactivity Feedback (ALBF)
   - **Authors**: Deng et al.
   - **Summary**: Demonstrates that active learning with bioactivity feedback improves drug discovery hit rates by 60% in 50-200 queries, validating the closed-loop optimization paradigm.
   - **Year**: 2025

3. **Title**: A versatile active learning workflow (METIS)
   - **Authors**: Pandi et al.
   - **Summary**: Shows that active machine learning achieves 1-2 orders of magnitude improvement in synthetic biology with minimal experiments, demonstrating sample efficiency of iterative optimization.
   - **Year**: 2022

4. **Title**: Active learning-assisted directed evolution (ALDE)
   - **Authors**: Yang et al.
   - **Summary**: Demonstrates that active learning improves enzyme yield from 12% to 93%, showing cross-domain applicability of closed-loop optimization in molecular biology.
   - **Year**: 2025

5. **Title**: RiboDecode: Deep generative optimization for enhanced mRNA translation
   - **Authors**: Li et al.
   - **Summary**: Achieves 10x antibody response through direct learning from ribosome profiling and provides a public dataset for warm-start approaches.
   - **Year**: 2025

6. **Title**: Helix-mRNA: Hybrid Foundation Model for Full Sequence mRNA Therapeutics
   - **Authors**: Wood et al.
   - **Summary**: A state-space and attention hybrid architecture that processes 6x longer sequences, serving as a one-shot baseline for comparison.
   - **Year**: 2025

7. **Title**: NeurIPS 2024 AI for New Drug Modalities Workshop
   - **Authors**: Not specified
   - **Summary**: Workshop proceedings that explicitly identified "How can foundation models be fine-tuned from laboratory feedback?" as an open research question, validating the research gap.
   - **Year**: 2024

8. **Title**: Calibrated ribosome profiling assesses the dynamics of ribosomal flux
   - **Authors**: Iwasaki et al.
   - **Summary**: Introduces Ribo-Calibration which enables quantitative measurement of translation efficiency, validating the reliability of feedback signals for optimization.
   - **Year**: 2024

**Key Challenges**
1. **Foundation Model Fine-tuning from Laboratory Feedback**: How to effectively fine-tune large-scale foundation models using experimental laboratory feedback remains an explicitly identified open question in the field.
2. **Sample Efficiency in Biological Optimization**: Achieving meaningful improvements with minimal experimental iterations is critical due to the high cost and time requirements of wet-lab experiments.
3. **Closed-Loop Integration**: Bridging the gap between computational predictions and experimental validation through iterative optimization workflows that incorporate real biological feedback.
4. **Quantitative Feedback Signal Reliability**: Ensuring that experimental measurements (such as translation efficiency from ribosome profiling) provide reliable and calibrated signals for model optimization.
5. **Sequence Length Processing**: Handling full-length mRNA sequences poses computational challenges that require specialized architectures to process longer sequences effectively.
