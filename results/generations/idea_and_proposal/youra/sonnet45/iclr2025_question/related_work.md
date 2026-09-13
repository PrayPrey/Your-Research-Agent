## Related Work

**Related Papers**

1. **Title**: SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative Large Language Models (Semantic Scholar ID: 7c1707db9aafd209aa93db3251e7ebd593d55876)
   - **Authors**: Manakul, P., Liusie, A., Gales, M.
   - **Summary**: Sampling-based consistency checking method that samples K responses from LLM with same prompt and computes consistency scores to detect hallucinations. Zero-resource approach requiring no external knowledge base, achieving F1 ~0.82 on WikiBio dataset.
   - **Year**: 2023

2. **Title**: Unsupervised Real-Time Hallucination Detection based on the Internal States of Large Language Models (MIND) (Semantic Scholar ID: 411b725522e2747e890ba5acfbf43d22f759c00a)
   - **Authors**: Su, W., et al.
   - **Summary**: Analyzes internal hidden states during generation for real-time hallucination detection without requiring post-hoc sampling. Requires model access (not API-only).
   - **Year**: 2024

3. **Title**: Hallucination Detection in Large Language Models with Metamorphic Relations (MetaQA) (Semantic Scholar ID: 425d16205b28ce175c8429965a964d19b6f390c1)
   - **Authors**: Yang, B., et al.
   - **Summary**: Metamorphic testing approach that generates variations of queries and checks output consistency, achieving 112.2% F1 improvement over SelfCheckGPT on some benchmarks.
   - **Year**: 2025

4. **Title**: SEAL: Steerable Reasoning Calibration of Large Language Models for Free (Semantic Scholar ID: b5e43268320b197c1530daefe6cdfdf8b07d3857)
   - **Authors**: Chen, Y., et al.
   - **Summary**: Calibration method that improves efficiency by reducing reasoning tokens by 50%, improving efficiency and reducing verbose outputs but potentially harming analytical/creative tasks.
   - **Year**: 2025

5. **Title**: Task-dependent creativity framework
   - **Authors**: Ward
   - **Summary**: Cognitive psychology framework showing humans naturally modulate creativity based on task context - technical documentation requires low originality tolerance with strict fact-checking, while creative writing allows high originality tolerance with permissive exploration.
   - **Year**: 2004

6. **Title**: Context determines interpretation (Pragmatics)
   - **Authors**: Geurts
   - **Summary**: NLP pragmatics theory demonstrating that context determines whether statements are interpreted as literal (factual context) or figurative (creative context). Pragmatic features like hedging, domain markers, and prompt structure reveal speaker intent.
   - **Year**: 2010

7. **Title**: Temperature scaling for classifier calibration
   - **Authors**: Guo et al.
   - **Summary**: Demonstrates that well-calibrated classifiers have confidence scores that correlate with prediction accuracy, enabling confidence-based decision making.
   - **Year**: Not specified

8. **Title**: Distinct-N metrics for NLG evaluation
   - **Authors**: Melas et al.
   - **Summary**: Established lexical diversity metrics (distinct-N) for measuring output richness in natural language generation, correlating with human creativity ratings (r=0.65).
   - **Year**: Not specified

9. **Title**: Hallucination Survey
   - **Authors**: Not specified
   - **Summary**: Comprehensive survey on hallucination in large language models providing foundational understanding of the problem space.
   - **Year**: Not specified

**Key Challenges**

1. **Uniform Detection Thresholds**: Existing hallucination detection methods (SelfCheckGPT, MIND, MetaQA, SEAL) apply uniform fixed detection thresholds regardless of task context, creating a forced binary choice between "safe but uncreative" (strict threshold) and "creative but risky" (permissive threshold).

2. **Creativity Suppression**: Strict hallucination detection thresholds (e.g., 0.9) achieve high precision in factual domains but suppress creative outputs by reducing reasoning tokens and lexical diversity, as demonstrated by SEAL's 50% reduction in reasoning tokens.

3. **No Context-Awareness**: All existing methods treat hallucination as uniformly harmful across all contexts, lacking principled frameworks to adaptively balance safety and creativity based on inferred task intent.

4. **Binary Detection Focus**: Current methods optimize detection accuracy alone without measuring or preserving creative capabilities, missing the dual-objective optimization of detection accuracy + creativity preservation.

5. **Missing Creativity Metrics**: Existing hallucination detection literature focuses solely on detection F1 scores without measuring impact on lexical diversity, semantic novelty, or reasoning token counts that reflect creative capability.

6. **Real-World Deployment Constraint**: Organizations deploying LLMs face impossible choice - conservative mode is safe for medical QA but unusable for creative tasks (over-constrained), while permissive mode works for brainstorming but risks dangerous hallucinations in high-stakes factual queries (under-protected).

7. **No Task-Appropriate Operating Points**: Fixed thresholds force single global operating point on precision-recall curve, preventing task-specific optimization where different domains have different tolerance for divergence (medical requires strict, creative writing requires permissive).

8. **Lack of Statistical Guarantees**: Unlike conformal prediction approaches, most hallucination detection methods lack formal statistical guarantees for error control in high-stakes deployment scenarios.
