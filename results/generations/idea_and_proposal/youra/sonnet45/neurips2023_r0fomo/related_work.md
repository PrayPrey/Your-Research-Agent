## Related Work

**Related Papers**

1. **Title**: Generating with Confidence: Uncertainty Quantification for Black-box Large Language Models (2023)
   - **Authors**: Zhen Lin, Shubhendu Trivedi, Jimeng Sun
   - **Summary**: Demonstrates that semantic dispersion (a simple measure for output variance) reliably predicts LLM response quality in black-box settings, providing a foundation for black-box uncertainty quantification frameworks.
   - **Year**: 2023

2. **Title**: Fact-Checking the Output of Large Language Models via Token-Level Uncertainty Quantification (2024)
   - **Authors**: Fadeeva, E., et al.
   - **Summary**: Introduces Claim Conditioned Probability (CCP) at token level to identify hallucinations without oracle, demonstrating competitive performance with knowledge-base fact-checking and enabling oracle-free validation paradigms.
   - **Year**: 2024

3. **Title**: On Evaluating Adversarial Robustness of Large Vision-Language Models (AttackVLM) (2023)
   - **Authors**: Zhao, Y., Pang, T., Du, C., et al.
   - **Summary**: Demonstrates cross-modal attack transferability in vision-language models and establishes a black-box evaluation paradigm for multimodal robustness testing.
   - **Year**: 2023

4. **Title**: Automated Robustness Testing for LLMs (2024)
   - **Authors**: Xiao et al.
   - **Summary**: Presents automated testing paradigm that reduces manual effort for LLM-based systems robustness evaluation, though limited to NLP-only scenarios.
   - **Year**: 2024

5. **Title**: Robustness tests for biomedical foundation models should tailor to specifications (2025)
   - **Authors**: Xian, R. P., et al.
   - **Summary**: Argues that task-specific robustness testing is necessary and predefined specifications are required, highlighting the lack of unified automated frameworks in current approaches.
   - **Year**: 2025

6. **Title**: SE Metamorphic Testing Literature
   - **Authors**: Not specified
   - **Summary**: Establishes the principle of oracle-free testing via metamorphic relations (e.g., "paraphrase should preserve output"), enabling property-based testing that eliminates oracle dependency.
   - **Year**: Not specified

7. **Title**: Adaptive Sampling Theory (Sequential Experimental Design)
   - **Authors**: Not specified
   - **Summary**: Establishes the principle of allocating experimental resources to uncertain regions for efficient exploration, providing theoretical foundation for uncertainty-guided test budget allocation.
   - **Year**: Not specified

**Key Challenges**

1. **Evaluation-Deployment Gap**: Current robustness evaluation approaches lack correlation with real-world deployment failures, limiting practical value of testing frameworks.

2. **Manual Attack Crafting Overhead**: Existing approaches like AttackVLM require manual attack specification, resulting in significant engineering effort (40+ hours) and limiting scalability.

3. **Task-Specific Testing Requirements**: Current robustness testing lacks unified automated frameworks and requires manual adaptation for each new task or domain (as identified in biomedical foundation model testing).

4. **Black-Box Evaluation Limitations**: Uncertainty quantification methods have been demonstrated primarily in single-modality settings, with few-shot multimodal correlation not explicitly validated in prior work.

5. **Multimodal Coverage Gap**: NLP-only automated testing approaches don't extend to multimodal vision-language models with cross-modal attack support.

6. **Oracle Dependency**: Traditional robustness testing requires ground-truth labels or oracles, limiting applicability in production settings where oracles are unavailable or expensive.

7. **Uncertainty-Failure Correlation**: Uncertainty-based approaches have shown promise in generation tasks but generalizability across diverse VLM tasks (VQA vs captioning vs retrieval) remains unvalidated.

8. **Property Library Development Cost**: Metamorphic testing approaches require one-time engineering effort to define properties for new tasks, with transferability across related tasks unexplored.
