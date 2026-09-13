# 2. Related Work

Our work sits at the intersection of hallucination detection methods, NLI domain adaptation, and reproducibility challenges in NLP. This section positions our contributions within these three research areas.

## 2.1 Hallucination Detection Methods

Large language models (LLMs) generate plausible but factually incorrect text at rates of 10–30% even on constrained tasks (Huang et al., 2023). Hallucination detection methods aim to flag such errors automatically, falling into three broad categories:

**NLI-Based Methods**: Claim-Conditioned Probability (CCP, arxiv:2403.04696) computes token-level probabilities weighted by NLI-derived claim entailment status. AGSER (arxiv:2501.09997) uses multi-sample prompting with self-consistency scoring. Both rely on pre-trained NLI models (typically DeBERTa or RoBERTa fine-tuned on SNLI/MNLI) to assess claim-context consistency. These methods report modest ROC-AUC improvements (+0.05–0.10) over baselines but often lack public implementations or raw metric distributions.

**Sampling-Based Methods**: SelfCheckGPT (Manakul et al., 2023) generates multiple samples from the same prompt and measures consistency across outputs. Semantic Entropy (Farquhar et al., 2024) clusters semantically equivalent outputs and computes entropy over clusters as an uncertainty measure. These methods require no external knowledge but incur computational overhead (5–10 samples per prompt).

**Taxonomy-Based Methods**: HAD (Hallucination Annotation Dataset) trains detectors on span-level annotations with taxonomy labels (entity, relation, contradiction). This approach avoids reliance on NLI calibration but requires labeled training data, which is scarce for creative domains.

**Gap Identified**: No prior work tests CCP or similar NLI-based methods on creative text (fiction, poetry, metaphorical content). The implicit assumption is that hallucination detectors generalize across all text types, but this has not been empirically verified.

## 2.2 NLI Domain Adaptation

Natural Language Inference (NLI) models trained on SNLI (Bowman et al., 2015) and MNLI (Williams et al., 2018) are widely used as components in downstream tasks, including hallucination detection, fact verification, and question answering. However, these models are trained on **sentence-pair semantic similarity** tasks, not factual verification.

**SNLI**: 570k premise-hypothesis pairs labeled as entailment, contradiction, or neutral. Premises are image captions; hypotheses are crowd-sourced descriptions. Task: "Do these sentences describe the same situation?"

**MNLI**: 433k pairs across diverse genres (fiction, government, telephone). Task remains semantic similarity, not factual consistency checking.

**Domain Adaptation Challenges**: When NLI models are applied to factual verification datasets like FEVER (Thorne et al., 2018) or HotpotQA (Yang et al., 2018), performance often degrades. FEVER introduces claim-context pairs where the context is a Wikipedia passage and the claim is a statement requiring multi-hop reasoning. Guo et al. (2017) show that neural network probability outputs are often miscalibrated (overconfident), requiring temperature scaling or recalibration.

**Calibration in Hallucination Detection**: Himal-Badu/Prediction-of-Prediction found that NLI features dominate over attention mechanisms ($r < 0.1$ for attention-hallucination correlation), suggesting NLI calibration is a bottleneck. Shaguns26/HallucinoGenAI achieved 95% recall only after threshold tuning from 50% to 30%, confirming that off-the-shelf NLI outputs require task-specific adjustment.

**Gap Identified**: No systematic study of NLI calibration requirements for CCP or similar methods. Papers report ROC-AUC improvements but do not document whether NLI models were validated on known examples (e.g., TruthfulQA correct vs incorrect answers).

## 2.3 Reproducibility in NLP and ML

Reproducibility challenges in NLP/ML are well-documented. Belz et al. (2021) surveyed 513 NLP papers and found that 24% failed replication attempts due to missing implementation details (hyperparameters, random seeds, training procedures). Dodge et al. (2019) proposed a reproducibility checklist for ML papers, emphasizing the importance of reporting negative results, ablation studies, and sensitivity analyses.

**Replication Studies**: Several recent works attempt to replicate landmark NLP papers:
- **Le Folgoc et al. (2021)**: Replicated MC Dropout for uncertainty estimation in medical imaging, finding that calibration depends critically on dropout rate (not documented in original papers).
- **Gururangan et al. (2018)**: Replicated annotation artifacts in NLI datasets, revealing that models exploit spurious correlations not present in the original paper's analysis.

**Hallucination Detection Reproducibility**: The CCP paper does not provide public code or raw metric distributions ($\rho_j$ values), making replication difficult. In contrast, Semantic Entropy (Farquhar et al., 2024) released official code with unit tests and validation notebooks, enabling rapid adoption (over 200 citations in <1 year).

**Gap Identified**: No prior replication study of CCP. Our work represents the first systematic attempt to reproduce CCP and extend it to creative text.

## 2.4 Claim Decomposition for Verification

Accurate claim decomposition is critical for NLI-based hallucination detection. Three approaches dominate:

**Rule-Based Tokenization**: NLTK sentence tokenization, Spacy sentence segmentation. Fast and deterministic but conflates sentence boundaries with logical claim boundaries (sentences may contain multiple claims or incomplete propositions).

**Dependency Parsing**: Extract subject-verb-object triples or proposition-level structures. Higher precision but requires hand-crafted rules for each syntactic pattern.

**LLM-Based Extraction**: Use GPT-3.5 or GPT-4 with prompts like "Extract independent factual claims from this text." High recall but non-deterministic and computationally expensive.

**Gap Identified**: No consensus on best practice for claim decomposition in hallucination detection. Papers typically report using "sentence tokenization" without specifying the library, validation methodology, or inter-method agreement (Krippendorff's $\alpha$).

## 2.5 Positioning Our Contributions

**Empirical**: First test of CCP on creative text (no prior work exists).

**Methodological**: First systematic documentation of NLI calibration failure for factual verification tasks, with root cause hierarchy and falsifiability tests.

**Reproducibility**: Transparent failure reporting with full code, configuration files, and diagnostic notebooks. Proposes actionable reproducibility requirements for hallucination detection papers (Section 6.3).

**Theoretical**: Identifies task-domain gap (SNLI/MNLI semantic similarity ≠ factual verification) as distinct from traditional domain shift (vocabulary/style differences).

Our work extends the CCP paper by attempting domain transfer, but the primary contribution is the **methodological critique**: we could not reproduce the baseline, and we document why. This negative result is itself a contribution, as it exposes a reproducibility gap in the hallucination detection literature.
