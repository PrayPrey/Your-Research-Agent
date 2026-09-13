# 2. Related Work

## 2.1 Hallucination Detection Methods

Large language models generate fluent but factually incorrect outputs (hallucinations) that pose risks for high-stakes applications [Huang et al., 2023]. Recent detection methods fall into three categories:

**NLI-based approaches** leverage Natural Language Inference models to verify consistency between generated text and source context. CCP (Constrained Category Probability) [arxiv:2403.04696] computes claim-type mass ratio ρ_j from NLI distributions over {contradiction, entailment, neutral}. AGSER [arxiv:2501.09997] combines multi-sample prompting with self-consistency scoring, achieving +0.154 to +0.368 F1 improvements over SelfCheckGPT baselines.

**Semantic entropy methods** measure uncertainty at meaning level rather than word-sequence level [Farquhar et al., 2024, Nature]. Semantic Entropy Probes [Kossen et al., 2024] approximate SE from hidden states in a single forward pass, reducing overhead by 5-10× while retaining hallucination detection performance.

**Self-consistency approaches** generate multiple responses and measure agreement. SelfCheckGPT [Manakul et al., 2023] detects hallucinations via sampling-based consistency without external knowledge. SDLG [Aichberger et al., 2024] steers LLMs to generate semantically diverse alternatives, quantifying aleatoric uncertainty through intra-cluster consistency.

Our work focuses on CCP replication because (1) it provides a principled uncertainty quantification framework (ρ_j metric), (2) paper claims measurable improvements (+0.05-0.10 ROC-AUC) but lacks public implementation, and (3) proposed ontology-mismatch hypothesis tests whether NLI-based methods embed factual-ontology assumptions.

## 2.2 NLI Model Domain Adaptation

Natural Language Inference models trained on SNLI [Bowman et al., 2015] and MNLI [Williams et al., 2018] excel at semantic similarity tasks (92-94% accuracy on test sets). However, downstream applications require task-specific calibration:

**Factual verification tasks**: FEVER [Thorne et al., 2018] and HotpotQA [Yang et al., 2018] datasets enable fine-tuning NLI models for claim-evidence verification. Shaguns26/HallucinoGenAI achieves 95% hallucination recall only after threshold tuning (50% → 30%) and hard negative mining (99% identical text, 1% critical fact changed).

**Attention vs NLI features**: Himal-Badu/Prediction-of-Prediction finds attention mechanisms show negligible correlation (r < 0.1) with hallucination labels when using standard NLI models, concluding "NLI features dominate over attention" → NLI model quality is primary bottleneck.

**Calibration challenges**: "Is MC Dropout Bayesian?" [Le Folgoc et al., 2021] questions whether dropout-based uncertainty estimation yields valid Bayesian posteriors, finding it assigns zero probability to true models on closed-form benchmarks. Similarly, calibration of NLI outputs for uncertainty quantification requires task-specific validation.

Our failure mode (neutral-class dominance, Section 4.4) aligns with these findings: DeBERTa-v3-base trained on SNLI/MNLI does not automatically generalize to factual verification (claim-context consistency), exhibiting task-domain gap distinct from traditional domain shift.

## 2.3 Reproducibility in NLP/ML

**Replication studies**: Belz et al. [2021] survey reproducibility challenges in NLP, finding that 24% of papers lack sufficient detail for replication. Dodge et al. [2019] propose reproducibility checklists requiring: (1) model hyperparameters, (2) dataset versions, (3) evaluation code, (4) variance estimates across runs.

**Hallucination detection gap**: While semantic entropy [Farquhar et al., 2024] provides official code (jlko/semantic_uncertainty), CCP [arxiv:2403.04696] has no public repository. Paper reports ROC-AUC improvements but omits: raw ρ_j distributions (expected: 0.75-0.85; we observe: 0.01-0.04), NLI calibration diagnostics, claim decomposition methodology, context pairing strategies.

**Production implementations**: CVS Health UQLM package (1183 GitHub stars) provides enterprise-grade semantic entropy with LangChain integration, demonstrating feasibility of reproducible UQ methods. Our contribution documents the gap between research claims and reproducible implementations for CCP.

## 2.4 Claim Decomposition for Verification

Existing NLI-based hallucination detectors use varied claim extraction methods:

- **Sentence tokenization** (cavaquinho, this work): NLTK `sent_tokenize` splits on punctuation, deterministic but conflates sentences with logical propositions
- **LLM-based extraction**: GPT-3.5/GPT-4 prompted to "extract independent factual claims," higher semantic validity but non-deterministic
- **Dependency parsing**: Spacy identifies subject-predicate-object triples, linguistically grounded but may miss implicit claims

No prior work systematically compares these methods' impact on ρ_j distribution or hallucination detection performance. Our failure analysis (Section 5.3) identifies claim decomposition quality as contributory factor requiring method comparison in future work.

## 2.5 Positioning of This Work

Our replication study differs from prior hallucination detection work in three ways:

1. **Transparent failure documentation**: We report negative result (ρ_j 50× lower than expected) with root cause analysis, rather than post-hoc optimization to achieve publishable metrics
2. **Task-domain gap identification**: We distinguish SNLI/MNLI semantic similarity training from factual verification application, a gap not explicitly discussed in CCP paper or related NLI-based detectors
3. **Methodological requirements**: We derive concrete prerequisites (NLI calibration validation, claim decomposition comparison, baseline replication) that future hallucination detection papers should address

No prior work systematically documents CCP replication failure modes or identifies NLI training distribution mismatch as root cause for factual verification tasks.
