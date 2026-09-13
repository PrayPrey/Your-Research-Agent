# Semantic Scholar Results - Phase 1 Targeted Research

## Round 1: Question-Focused Search (8 queries, 50+ papers found)

### HIGHLY CITED FOUNDATIONAL PAPERS (>100 citations)

1. **[VERIFIED - SCHOLAR]** "Dropout as a Bayesian Approximation: Representing Model Uncertainty in Deep Learning" (2015)
   - Authors: Yarin Gal, Zoubin Ghahramani
   - Citations: 12,174
   - SS ID: f35de4f9b1a7c4d3fa96a0d2ab1bf8937671f6b6
   - arXiv ID: 1506.02142
   - URL: https://www.semanticscholar.org/paper/f35de4f9b1a7c4d3fa96a0d2ab1bf8937671f6b6
   - Relevance: Foundational work on MC Dropout baseline method
   - Key Contribution: Casts dropout training as approximate Bayesian inference, enabling uncertainty estimation

2. **[VERIFIED - SCHOLAR]** "Just Ask for Calibration: Strategies for Eliciting Calibrated Confidence Scores from Language Models Fine-Tuned with Human Feedback" (2023)
   - Authors: Katherine Tian, Eric Mitchell, et al.
   - Citations: 792
   - SS ID: ab4ce5dda7ad4d9032995c9c049a89d65723c6aa
   - arXiv ID: 2305.14975
   - URL: https://www.semanticscholar.org/paper/ab4ce5dda7ad4d9032995c9c049a89d65723c6aa
   - Search Query: "calibration language models factual question answering"
   - Relevance: Directly addresses calibration on TriviaQA, TruthfulQA benchmarks
   - Key Contribution: Verbalized confidences from RLHF-LMs better calibrated than conditional probabilities, reducing ECE by 50%

3. **[VERIFIED - SCHOLAR]** "Semantic Entropy Probes: Robust and Cheap Hallucination Detection in LLMs" (2024)
   - Authors: Jannik Kossen, Jiatong Han, et al.
   - Citations: 219
   - SS ID: 648375ec8d90cb792de76030223539498612102e
   - arXiv ID: 2406.15927
   - URL: https://www.semanticscholar.org/paper/648375ec8d90cb792de76030223539498612102e
   - Search Query: "semantic entropy hallucination detection"
   - Relevance: **SINGLE-PASS** semantic entropy approximation (addresses efficiency goal)
   - Key Contribution: Approximates semantic entropy from hidden states of ONE generation (no sampling needed), reducing overhead to near zero

4. **[VERIFIED - SCHOLAR]** "Fact-Checking the Output of Large Language Models via Token-Level Uncertainty Quantification" (2024)
   - Authors: Ekaterina Fadeeva, Aleksandr Rubashevskii, et al.
   - Citations: 173
   - SS ID: 8c5acaafe43e710d55b08c63d567550ad26ec437
   - arXiv ID: 2403.04696
   - URL: https://www.semanticscholar.org/paper/8c5acaafe43e710d55b08c63d567550ad26ec437
   - Search Query: "uncertainty quantification LLMs output probabilities"
   - Relevance: Token-level uncertainty with fact-checking pipeline
   - Key Contribution: Competitive with external knowledge fact-checking using only internal uncertainty signals

### RECENT HIGH-IMPACT PAPERS (2024-2026, >10 citations)

5. **[VERIFIED - SCHOLAR]** "Hallucination Detection in Large Language Models via Multi-Granular Uncertainty Quantification" (2026)
   - Authors: Abdullah Önden
   - Citations: 0 (very recent)
   - SS ID: 6326fbdfdd20b157cd9dad2082aa39c0be05acab
   - arXiv ID: None (DOI: 10.59543/comdem.v3i.17665)
   - URL: https://www.semanticscholar.org/paper/6326fbdfdd20b157cd9dad2082aa39c0be05acab
   - Search Query: "uncertainty quantification LLMs output probabilities"
   - Relevance: **SINGLE-PASS** with 12 uncertainty features, tested on HaluEval
   - Key Contribution: 89.27% AUROC on HaluEval, 8.2x latency reduction vs semantic entropy, single forward pass

6. **[VERIFIED - SCHOLAR]** "Uncertainty Quantification for LLMs through Minimum Bayes Risk: Bridging Confidence and Consistency" (2025)
   - Authors: Roman Vashurin, Maiya Goloburda, et al.
   - Citations: 19
   - SS ID: 4d698dbbf49a046f1da1e48a6d8a4c3efc28fbb3
   - arXiv ID: 2502.04964
   - URL: https://www.semanticscholar.org/paper/4d698dbbf49a046f1da1e48a6d8a4c3efc28fbb3
   - Search Query: "uncertainty quantification LLMs output probabilities"
   - Relevance: Combines confidence (probabilities) with consistency (semantic similarity)
   - Key Contribution: Links uncertainty to minimum Bayes risk, sizable improvements on QA, summarization, MT

7. **[VERIFIED - SCHOLAR]** "UNCERTAINTY-LINE: Length-Invariant Estimation of Uncertainty for Large Language Models" (2025)
   - Authors: Roman Vashurin, Maiya Goloburda, et al.
   - Citations: 3
   - SS ID: 171183622ae115b23dfcf696abf15a38db7c9649
   - arXiv ID: 2505.19060
   - URL: https://www.semanticscholar.org/paper/171183622ae115b23dfcf696abf15a38db7c9649
   - Search Query: "uncertainty quantification LLMs output probabilities"
   - Relevance: Addresses length bias in uncertainty estimation
   - Key Contribution: Debiasing procedure using residuals after regressing on output length

8. **[VERIFIED - SCHOLAR]** "Bayesian Prompt Ensembles: Model Uncertainty Estimation for Black-Box Large Language Models" (2024)
   - Authors: Francesco Tonolini, Jordan Massiah, et al.
   - Citations: 30
   - SS ID: 55f50127a87d07e51316c163c2123b115fff126b
   - arXiv ID: None (DOI: 10.18653/v1/2024.findings-acl.728)
   - URL: https://www.semanticscholar.org/paper/55f50127a87d07e51316c163c2123b115fff126b
   - Search Query: "uncertainty quantification LLMs output probabilities"
   - Relevance: Bayesian approach for black-box LLMs using prompt ensembles
   - Key Contribution: Weighted ensemble of semantically equivalent prompts with variational inference

### SURVEY PAPERS (2024-2025)

9. **[VERIFIED - SCHOLAR]** "Uncertainty Quantification and Confidence Calibration in Large Language Models: A Survey" (2025)
   - Authors: Xiaoou Liu, Tiejin Chen, et al.
   - Citations: 108
   - SS ID: 422b00c330a16a00ef182abfd1d66e12369db9e8
   - arXiv ID: 2503.15850
   - URL: https://www.semanticscholar.org/paper/422b00c330a16a00ef182abfd1d66e12369db9e8
   - Search Query: "uncertainty quantification large language models survey"
   - Relevance: Comprehensive taxonomy of UQ methods for LLMs
   - Key Contribution: Categorizes methods by computational efficiency and uncertainty dimensions

10. **[VERIFIED - SCHOLAR]** "A Survey on Uncertainty Quantification of Large Language Models: Taxonomy, Open Research Challenges, and Future Directions" (2024)
    - Authors: Omo Shorinwa, Zhiting Mei, et al.
    - Citations: 133
    - SS ID: eac37c416c89a8eafd655dee639344379e2df33e
    - arXiv ID: 2412.05563
    - URL: https://www.semanticscholar.org/paper/eac37c416c89a8eafd655dee639344379e2df33e
    - Search Query: "uncertainty quantification large language models survey"
    - Relevance: Reviews hallucination detection and UQ methods
    - Key Contribution: Taxonomy of existing methods with applications to robotics and chatbots

### BENCHMARK-SPECIFIC PAPERS (TriviaQA, TruthfulQA, HaluEval)

11. **[VERIFIED - SCHOLAR]** "Exploring RAG Solutions to Reduce Hallucinations in LLMs" (2025)
    - Authors: Samar AboulEla, Paria Zabihitari, et al.
    - Citations: 18
    - SS ID: 90c30747db366b49de2141617b061ab5637100b7
    - arXiv ID: None (DOI: 10.1109/SysCon64521.2025.11014810)
    - URL: https://www.semanticscholar.org/paper/90c30747db366b49de2141617b061ab5637100b7
    - Search Query: "TriviaQA TruthfulQA HaluEval benchmark evaluation"
    - Relevance: Direct evaluation on all three target benchmarks
    - Key Contribution: Comparative study of RAG architectures on HaluEval, Squad-V2, TriviaQA

### EFFICIENCY-FOCUSED PAPERS (Single-Pass Methods)

12. **[VERIFIED - SCHOLAR]** "On Feature Collapse and Deep Kernel Learning for Single Forward Pass Uncertainty" (2021)
    - Authors: Joost van Amersfoort, Lewis Smith, et al.
    - Citations: 127
    - SS ID: 58de6cf06651017fba729cfbc37ed28ab2eaf507
    - arXiv ID: 2102.11409
    - URL: https://www.semanticscholar.org/paper/58de6cf06651017fba729cfbc37ed28ab2eaf507
    - Search Query: "efficient uncertainty estimation transformers single forward pass"
    - Relevance: Single forward pass uncertainty for deep models
    - Key Contribution: DUE (Deep Uncertainty Estimation) with bi-Lipschitz constraints

13. **[VERIFIED - SCHOLAR]** "Packed-Ensembles for Efficient Uncertainty Estimation" (2022)
    - Authors: Olivier Laurent, Adrien Lafage, et al.
    - Citations: 61
    - SS ID: 00961426bef856073e7a57d785883b1b0a2f6050
    - arXiv ID: 2210.09184
    - URL: https://www.semanticscholar.org/paper/00961426bef856073e7a57d785883b1b0a2f6050
    - Search Query: "efficient uncertainty estimation transformers single forward pass"
    - Relevance: Lightweight structured ensembles with grouped convolutions
    - Key Contribution: Parallelizes ensemble into single backbone, preserves DE properties with lower memory

### CONFIDENCE ESTIMATION PAPERS

14. **[VERIFIED - SCHOLAR]** "InternalInspector I2: Robust Confidence Estimation in LLMs through Internal States" (2024)
    - Authors: Mohammad Beigi, Ying Shen, et al.
    - Citations: 29
    - SS ID: 2d5b8eed2fdf9f7ba237f986946c573d2b6aa258
    - arXiv ID: 2406.12053
    - URL: https://www.semanticscholar.org/paper/2d5b8eed2fdf9f7ba237f986946c573d2b6aa258
    - Search Query: "confidence estimation neural language generation"
    - Relevance: Internal states for confidence estimation
    - Key Contribution: Contrastive learning on attention, FF, activation states across all layers

15. **[VERIFIED - SCHOLAR]** "Mind the Confidence Gap: Overconfidence, Calibration, and Distractor Effects in Large Language Models" (2025)
    - Authors: Prateek Chhikara
    - Citations: 43
    - SS ID: 420e69f655b8974f8d6f47869d6e0497bb060fcb
    - arXiv ID: 2502.11028
    - URL: https://www.semanticscholar.org/paper/420e69f655b8974f8d6f47869d6e0497bb060fcb
    - Search Query: "calibration language models factual question answering"
    - Relevance: Calibration analysis across 9 LLMs on 3 factual QA datasets
    - Key Contribution: Distractor-augmented prompts reduce ECE up to 90%, accuracy improvements up to 460%

## Total Papers Found: 50+
## Curated Selection: Top 15 based on citations, relevance, and efficiency focus
## All papers tagged with [VERIFIED - SCHOLAR] + Semantic Scholar IDs
## arXiv IDs extracted for Phase 2A paper download (where available)
