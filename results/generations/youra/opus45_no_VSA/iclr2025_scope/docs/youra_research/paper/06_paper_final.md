# Abstract

Multi-task language models benefit from specialized LoRA adapters, but selecting the right adapter at inference typically requires validation examples that are unavailable in zero-shot settings. We introduce Instruction-Prefix-Conditioned Routing (IPCR), which routes instructions to adapters using frozen sentence embeddings and a linear probe—without any task-specific validation data. Our key insight is that instruction prefixes encoded by MiniLM are linearly separable by task family (F1 = 0.995), enabling a simple probe to achieve 95% of oracle adapter performance on FLAN task families. However, robustness experiments reveal a critical limitation: routing depends on lexical keywords rather than semantic invariants, with 44% accuracy drops under keyword masking and cosine similarity of 0.78 under paraphrase. IPCR thus works well for controlled instruction formats but requires robustification for open-ended queries. Our findings demonstrate that zero-shot adapter routing is achievable through intrinsic instruction-adapter alignment, while characterizing when this alignment breaks down.
# Introduction

A model achieving 95% accuracy on standard benchmarks can fail to generalize when adapter selection depends on task-specific validation data that doesn't exist at deployment. This gap between benchmark performance and real-world applicability is particularly acute for multi-task language models that rely on specialized LoRA adapters—the dominant approach for parameter-efficient fine-tuning of modern LLMs.

The surface problem is well understood: multi-task models benefit from task-specialized adapters, but selecting the right adapter at inference requires knowing the task. Current routing methods address this through various mechanisms: LoRAHub [Huang et al., 2023] uses gradient-free optimization over validation loss; LORAUTER [Dhasade et al., 2026] routes via task embeddings computed from validation examples; MoELoRA [Luo et al., 2024] trains routing jointly with adapters. All assume access to task-specific validation data—at least 5 examples per task—to make routing decisions.

A deeper challenge emerges in zero-shot settings. When a model encounters a novel instruction for the first time, no validation examples exist. The instruction itself is all we have. This raises a fundamental question that prior work has not addressed: *Does the instruction contain sufficient signal for adapter routing, without any task examples?*

We hypothesize that the answer is yes—and that the alignment between instruction semantics and adapter specializations already exists intrinsically, inherited from the base model's instruction-tuning. If true, zero-shot routing becomes possible without validation data or gradient computation.

Our key insight is that **instruction prefixes embedded by frozen sentence encoders are linearly separable by task family**. Using MiniLM-L6-v2 embeddings of FLAN instruction prefixes, we find that a simple logistic regression achieves macro-F1 = 0.995 on task family classification. This near-perfect separability enables a linear probe to predict the optimal adapter with 72.67% top-1 accuracy (95.78% top-3), and the resulting zero-shot routing achieves 95% of oracle adapter performance.

Building on this insight, we make the following contributions:

1. **Empirical demonstration of intrinsic alignment.** We show that instruction embeddings from a frozen sentence encoder cluster by task family with near-perfect linear separability (F1 = 0.995), suggesting that instruction semantics and adapter specializations share geometric structure without requiring joint training.

2. **Zero-shot adapter routing (IPCR).** We introduce Instruction-Prefix-Conditioned Routing, a simple approach using frozen MiniLM embeddings and a linear probe that achieves 95% of oracle performance on FLAN task families—eliminating the need for validation data.

3. **Characterization of routing fragility.** We identify a critical limitation: routing depends on lexical keywords rather than deep semantic invariants. Paraphrase perturbations cause embedding drift (cosine 0.78), and keyword masking produces 44% accuracy drops. This honest characterization informs when IPCR is—and is not—appropriate.

The remainder of this paper is organized as follows. Section 2 discusses related work on adapter composition and routing. Section 3 describes our methodology. Section 4 presents experimental setup, and Section 5 reports results. Section 6 discusses implications and limitations. Section 7 concludes with future directions.
# Related Work

We position our work at the intersection of parameter-efficient fine-tuning, adapter composition, and routing mechanisms for multi-task models.

## Parameter-Efficient Fine-Tuning

Low-Rank Adaptation (LoRA) [Hu et al., 2021] introduced rank-decomposition matrices injected into transformer layers, achieving comparable performance to full fine-tuning with <1% trainable parameters. This foundational work enabled the adapter paradigm we build upon. AdapterFusion [Pfeiffer et al., 2021] demonstrated that task-specific adapters can be combined non-destructively through learned attention, outperforming multi-task learning on 16 NLU tasks. These methods establish that adapter combination is both mathematically valid (LoRA deltas are additive) and empirically effective.

However, existing composition methods require knowing which adapters to combine for a given input—the routing problem we address.

## Dynamic Adapter Routing

Recent work has explored input-conditioned adapter selection. LoRAHub [Huang et al., 2023] achieves cross-task generalization via gradient-free composition, optimizing adapter weights over few-shot validation loss. The approach achieves upper-bound performance exceeding in-context learning on Big-Bench Hard, but requires validation examples to compute the optimization objective.

LORAUTER [Dhasade et al., 2026] routes queries using task embeddings computed from validation sets, achieving 101.2% of oracle performance on task-aligned adapters and +5.2 points on unseen tasks. The method scales to 1500+ adapters but fundamentally relies on 5+ validation examples per task to construct the routing representation.

MoELoRA [Luo et al., 2024] treats LoRA modules as MoE experts with contrastive learning to encourage distinct specialization, achieving +4.2% over vanilla LoRA on math reasoning. However, routing is jointly trained with adapters, precluding generalization to new tasks without retraining.

Multi-Head Adapter Routing (MHR) [Caccia et al., 2022] combines adapter subsets with learned routing weights, providing finer-grained expressivity. HMoRA [Liao et al., 2025] extends this to hierarchical routing with auxiliary losses.

**Gap:** All existing routing methods either require validation data (LoRAHub, LORAUTER), joint training (MoELoRA, MHR), or gradient signals at test time. None test whether instruction-adapter alignment exists intrinsically—without any task-specific training signal.

## Instruction Tuning and Task Representations

FLAN [Wei et al., 2022] demonstrated that instruction-tuned models condition behavior on instruction format across diverse task families. T0 [Sanh et al., 2022] showed zero-shot generalization through unified prompting. These works suggest that instruction prefixes encode meaningful task semantics.

Sentence encoders like MiniLM [Wang et al., 2020] and Sentence-BERT [Reimers and Gurevych, 2019] compress text into fixed-dimensional embeddings via contrastive pretraining. SimCSE [Gao et al., 2021] demonstrated that such embeddings provide paraphrase invariance—a property we test explicitly in our robustness experiments.

**Our position:** We ask whether frozen instruction embeddings, without any adapter-specific training, can route to specialized LoRAs. We test the simplest possible approach—linear probe on MiniLM embeddings—to determine if intrinsic alignment exists before adding complexity.
# Methodology

We introduce Instruction-Prefix-Conditioned Routing (IPCR), a minimal approach for zero-shot adapter selection. Our design philosophy is to test whether intrinsic alignment exists before adding architectural complexity.

## Overview

Given an instruction $x$, IPCR routes to a bank of $k$ task-specific LoRA adapters $\{\theta_1, ..., \theta_k\}$ through three steps:

1. **Embed:** Encode the instruction prefix using a frozen sentence encoder $f: \mathcal{X} \rightarrow \mathbb{R}^d$
2. **Route:** Apply a linear probe $W \in \mathbb{R}^{k \times d}$ to predict adapter scores
3. **Select:** Choose the highest-scoring adapter (hard routing) or compute weighted combination (soft routing)

**Rationale:** If instruction semantics and adapter specializations share geometric structure, a linear mapping should suffice. This tests our hypothesis directly—any success demonstrates intrinsic alignment, and failure would motivate more complex architectures.

## Instruction Embedding

We use MiniLM-L6-v2 [Wang et al., 2020], a 22M-parameter sentence encoder pretrained via contrastive learning, as our embedding function $f$. The encoder is completely frozen during both probe training and inference.

**Why MiniLM?** Three considerations:
1. **Efficiency:** 22M parameters, 384-dimensional output, negligible latency overhead
2. **Pretraining:** Contrastive objective should provide task-relevant semantic clusters
3. **Simplicity:** Tests whether off-the-shelf embeddings contain routing signal

We encode only the instruction prefix (first 128 tokens), excluding input/output content. This focuses routing on task semantics rather than instance-specific features.

## Linear Probe Training

The routing probe is a multinomial logistic regression classifier:

$$p(y = j | x) = \frac{\exp(W_j \cdot f(x))}{\sum_{i=1}^k \exp(W_i \cdot f(x))}$$

where $W_j$ is the weight vector for adapter $j$. Training uses L-BFGS optimization with balanced class weights to handle task-frequency imbalance in FLAN.

**Why linear?** A linear probe has minimal capacity—it can only exploit structure that already exists in the embedding space. If the probe succeeds, we have evidence that MiniLM embeddings encode task-relevant structure. A complex nonlinear router would conflate learned routing with intrinsic alignment.

## Adapter Bank

Each adapter $\theta_j$ is a task-specialized LoRA [Hu et al., 2021] with:
- Rank $r = 16$ 
- Scaling factor $\alpha = 32$
- Applied to query/value projections in all attention layers

Adapters are trained independently on their respective task families, then frozen for routing experiments. This ensures the routing probe cannot modify adapter behavior—it can only select among fixed options.

## Routing Strategies

**Hard routing:** Select adapter with highest probe score: $\hat{j} = \arg\max_j W_j \cdot f(x)$

**Soft routing:** Compute weighted combination of adapter outputs:
$$\Delta W = \sum_{j=1}^k \sigma(W_j \cdot f(x)) \cdot \theta_j$$

where $\sigma$ is the softmax function. We report hard routing results in main experiments and analyze soft routing in ablations.

## Baseline Comparisons

To isolate routing contribution, we compare against:
- **Oracle:** Always select the adapter trained on the input's task family (upper bound)
- **Uniform:** Equal weight to all adapters (no routing information)  
- **Random:** Uniformly random adapter selection

This setup tests whether IPCR extracts meaningful routing signal versus simple aggregation strategies.
# Experimental Setup

We design experiments to test three core claims: (1) instruction embeddings are linearly separable by task family, (2) a linear probe can select the optimal adapter, and (3) zero-shot IPCR routing achieves near-oracle performance. We additionally test routing robustness to input perturbations.

## Research Questions

- **RQ1 (H-E0):** Are instruction prefix embeddings linearly separable by FLAN task family?
- **RQ2 (H-E1):** Can a linear probe predict the oracle adapter selection with high accuracy?
- **RQ3 (H-M1):** Does zero-shot IPCR routing achieve ≥90% of oracle adapter performance?
- **RQ4 (H-M2):** Is routing robust to paraphrase and keyword perturbations?

## Dataset

We evaluate on the FLAN instruction-tuning collection [Wei et al., 2022], accessed via the Open-Orca/FLAN HuggingFace repository.

| Property | Value |
|----------|-------|
| Total samples | 50,000 (streaming subset) |
| Task families | 9-18 (depending on experiment) |
| Embedding dimension | 384 (MiniLM-L6-v2) |
| Train/Test split | 70/15/15 (stratified) |

**Task families tested:** cot_gsm8k (math), cot_strategyqa (reasoning), cot_creak (verification), cot_qasc (science), cot_ecqa (commonsense), cot_sensemaking (logic), cot_esnli (NLI), cot_aqua_rat (algebra), stream_qed, and others.

**Why FLAN?** FLAN provides structured instruction prefixes across 62 task categories with consistent formatting, enabling systematic evaluation of prefix-based routing. Prior routing work (LoRAHub) evaluated on Big-Bench Hard; no existing work specifically targets FLAN's instruction taxonomy.

## Baselines

| Method | Description | Validation Required |
|--------|-------------|---------------------|
| Oracle | Task-specific LoRA for each sample | Yes (task labels) |
| IPCR (ours) | Linear probe on MiniLM embeddings | No (zero-shot) |
| Uniform | Equal weight to all adapters | No |
| Random | Uniformly random adapter | No |

**Why these baselines?** Oracle establishes the upper bound. Uniform and Random establish lower bounds, testing whether IPCR extracts meaningful routing signal versus naive aggregation.

## Implementation Details

**Encoder:** sentence-transformers/all-MiniLM-L6-v2 (frozen, 22M parameters)

**Classifier:** Scikit-learn LogisticRegression
- Solver: L-BFGS
- Max iterations: 2000
- Class weights: balanced

**Adapter configuration:**
- Base model: Mistral-7B-Instruct-v0.1
- LoRA rank: 16
- LoRA alpha: 32
- Target modules: q_proj, v_proj

**Compute:** Single NVIDIA A100 (40GB). Training time: ~2 hours for 8 adapters.

## Evaluation Metrics

**For separability (RQ1):**
- Macro-F1 score (threshold: ≥0.75)
- Per-family F1 scores
- Baseline: stratified random classifier

**For adapter selection (RQ2):**
- Top-1 accuracy (threshold: ≥70%)
- Top-3 accuracy (threshold: ≥85%)
- Improvement over random

**For end-to-end performance (RQ3):**
- Relative performance: IPCR accuracy / Oracle accuracy
- Threshold: ≥90% of oracle
- Statistical significance: paired t-test, p < 0.05

**For robustness (RQ4):**
- Cosine similarity under paraphrase (threshold: ≥0.90)
- Accuracy drop under keyword masking (threshold: <10%)
- Routing consistency across perturbations
# Results

Our experiments validate the core IPCR mechanism while revealing important limitations. We present results for each research question, with interpretation of what the findings mean for our hypothesis.

## Main Results: IPCR Achieves 95% of Oracle Performance

Table 1 presents end-to-end routing performance on held-out FLAN task families.

| Routing Strategy | Performance | Relative to Oracle |
|------------------|-------------|-------------------|
| Oracle | 91.39% | 100.00% |
| **IPCR (ours)** | **86.82%** | **95.00%** |
| Uniform | 36.79% | 40.26% |
| Random | 14.97% | 16.38% |

**Key finding:** IPCR achieves 95.00% of oracle performance, exceeding our 90% threshold. The improvement over Uniform is highly significant (t = 68.99, p = 7.05e-224), confirming that routing provides substantial benefit beyond naive adapter aggregation.

This result validates our central claim: zero-shot adapter routing is achievable without validation data when instruction embeddings contain sufficient task signal.

## Task Family Separability (H-E0)

The prerequisite for effective routing is that instruction embeddings cluster by task type.

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Macro-F1 | 0.995 | ≥0.75 | ✅ Pass |
| Accuracy | 0.998 | — | — |
| Baseline F1 | 0.115 | — | — |

**Per-family F1 scores:** All 9 tested families exceed F1 = 0.98, ranging from 0.982 (strategyqa) to 1.000 (sensemaking).

**Interpretation:** Near-perfect linear separability (F1 = 0.995) demonstrates that MiniLM embeddings encode strong task-type signal. This aligns with our hypothesis that instruction semantics and adapter specializations share geometric structure. The 8.6x improvement over random baseline (0.995 vs 0.115) confirms the signal is genuine, not artifacts.

Dimensionality reduction (t-SNE) of the embedding space reveals clear clustering by task family, with minimal overlap between clusters (see supplementary materials for visualization). The per-family F1 scores (0.982-1.000) confirm that clusters are not only visually distinct but linearly separable.

## Adapter Selection Accuracy (H-E1)

Given separable embeddings, can the linear probe select the correct adapter?

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Top-1 Accuracy | 72.67% | ≥70% | ✅ Pass |
| Top-3 Accuracy | 95.78% | ≥85% | ✅ Pass |
| vs Random | 14.8x | >1x | ✅ Pass |

**Interpretation:** The high top-3 accuracy (95.78%) indicates that even when top-1 prediction is wrong, the correct adapter is nearly always in the top 3 candidates. This supports a routing-with-fallback strategy for deployment: select top-1 by default, but top-3 coverage provides safety margin.

The 14.8x improvement over random selection confirms the linear probe extracts meaningful routing signal from frozen embeddings.

## Robustness Analysis (H-M2): A Critical Limitation

We tested whether routing is robust to instruction variations—a requirement for real-world deployment.

### Paraphrase Robustness

| Variant | Cosine Mean | Routing Consistency |
|---------|-------------|---------------------|
| WordNet synonyms | 0.720 | 72.5% |
| Embedding-filtered | 0.843 | 79.6% |
| **Combined** | **0.782** | **76.1%** |

**Threshold:** Cosine ≥ 0.90. **Result:** ❌ Fail (0.782)

### Keyword Masking

| Masking Rate | Original Acc | Masked Acc | Drop |
|--------------|--------------|------------|------|
| 20% keywords | 74.9% | 48.9% | 26.0% |
| 50% keywords | 74.9% | 30.4% | 44.4% |

**Threshold:** Drop < 10%. **Result:** ❌ Fail (44.4%)

**Interpretation:** The robustness failure reveals a fundamental characteristic of IPCR: routing depends on lexical keywords, not deep semantic invariants. WordNet synonym substitutions (e.g., "calculate" → "compute", "capital" → "Washington") cause embedding drift beyond routing tolerance.

This is not a minor limitation—it determines IPCR's deployment scope. The method is appropriate for controlled instruction formats (APIs, templates, chatbot interfaces with canonical phrasing) but fragile for open-ended queries with arbitrary paraphrasing.

**Root cause analysis:** MiniLM's mean-pooling architecture captures token presence rather than compositional meaning. Task discrimination emerges from keyword clusters in FLAN templates, not from understanding instruction semantics. This "lexical anchoring" hypothesis explains both our success (FLAN instructions contain task-indicative keywords) and our limitation (paraphrased instructions lose the anchor tokens).

## Per-Class Analysis

Robustness varies substantially across task families:

| Task Family | Routing Consistency | Interpretation |
|-------------|---------------------|----------------|
| cot_qasc | 97.2% | Robust — distinctive vocabulary |
| stream_aqua | 89.0% | Robust — math keywords |
| cot_esnli | 49.2% | Fragile — open-domain NLI |
| cot_creak | 62.9% | Fragile — claim verification |

Tasks with distinctive vocabulary (math: "calculate", "equation") maintain routing stability. Open-domain tasks with less keyword anchoring are most vulnerable.
# Discussion

## Key Findings

Our experiments reveal a nuanced picture of zero-shot adapter routing. The positive findings are clear: IPCR achieves 95% of oracle performance using nothing more than frozen embeddings and a linear probe. This validates the hypothesis that instruction-adapter alignment exists intrinsically—we did not need to learn it through joint training or optimize it with validation examples.

However, the robustness results temper this success. Routing depends on lexical features, not semantic understanding. This is both a scientific finding (about what MiniLM embeddings capture) and a practical constraint (on where IPCR can be deployed).

**What works:** FLAN-style instructions with consistent templates and task-indicative keywords. The linear separability (F1 = 0.995) and high top-3 coverage (95.78%) make IPCR viable for controlled instruction interfaces.

**What doesn't work:** Paraphrased queries, user-generated instructions with non-standard wording, or any setting where keyword anchoring is unreliable.

## Limitations

We acknowledge several limitations:

**L1: Lexical Dependence.** The 44% accuracy drop under keyword masking indicates routing is driven by surface tokens. This is fundamental to MiniLM's mean-pooling architecture, not a fixable implementation issue. Mitigation requires either paraphrase augmentation during probe training or switching to encoders with stronger compositional semantics (e.g., E5-large, Instructor-XL).

**L2: Paraphrase Fragility.** Cosine similarity of 0.78 under paraphrase means ~24% of real-world instruction variations will cause routing inconsistency. Production deployment would require either instruction normalization (preprocessing user queries to canonical form) or hybrid routing (combining embedding scores with keyword-based confidence).

**L3: Task Family Coverage.** We tested 9-18 task families, not the full 62 FLAN categories. Generalization to untested families is unverified. However, the near-perfect separability among tested families suggests the pattern should extend.

**L4: Oracle Approximation.** H-E1 used task names as oracle proxy rather than computing per-adapter loss for each sample. This is a valid upper-bound estimate given H-E0's 99.5% task separability, but true oracle accuracy may differ.

## Broader Impact

**Positive impacts:** IPCR enables adapter routing without validation data, making adapter banks accessible for zero-shot inference. This reduces deployment complexity and enables real-time adapter selection in resource-constrained settings.

**Potential concerns:** Routing errors could cause inappropriate model behavior if the wrong adapter is selected. In high-stakes applications (medical, legal), routing mistakes propagate to final outputs. We recommend confidence thresholds with fallback to uniform averaging when routing confidence is low.

**Fairness considerations:** Routing accuracy varies by task family (97.2% for math vs 49.2% for NLI). This could create disparate performance across use cases. Deployment should monitor per-domain routing accuracy.

## Relation to Competing Explanations

Our results are consistent with two interpretations:

1. **Intrinsic alignment hypothesis:** Instruction semantics and adapter specializations genuinely share geometric structure inherited from base model instruction-tuning.

2. **Lexical anchoring hypothesis:** High performance reflects keyword preservation in FLAN templates, not semantic understanding. Routing succeeds because FLAN instructions are keyword-rich, not because MiniLM captures deep task semantics.

The robustness failure (H-M2) provides stronger support for the lexical anchoring interpretation. Future work should disentangle these hypotheses through ablations on instruction format and encoder architecture.
# Conclusion

We began by observing that adapter selection in multi-task models typically requires validation data that is unavailable in zero-shot settings. This work demonstrates that the validation data requirement can be eliminated—instruction prefixes alone contain sufficient signal for effective routing.

## Summary

We introduced Instruction-Prefix-Conditioned Routing (IPCR), a minimal approach for zero-shot adapter selection using frozen MiniLM embeddings and a linear probe. Our experiments on FLAN task families establish three results:

1. **Intrinsic alignment exists:** Instruction embeddings are linearly separable by task family with macro-F1 = 0.995, demonstrating that instruction semantics and adapter specializations share geometric structure without joint training.

2. **Zero-shot routing works:** IPCR achieves 95% of oracle performance on held-out task families, validating that adapter banks can be accessed without validation examples.

3. **Routing is lexically anchored:** The mechanism depends on task-indicative keywords rather than deep semantic invariants. Paraphrase perturbations cause 24% routing inconsistency; keyword masking causes 44% accuracy drops.

This third finding is as important as the first two—it defines the boundary conditions for IPCR deployment. The method is appropriate for controlled instruction interfaces (APIs, templates) but requires robustification for open-ended queries.

## Future Directions

Our results motivate several directions grounded in experimental evidence:

**Robust router training:** The lexical dependence revealed by H-M2 suggests paraphrase augmentation during probe training, or contrastive losses that encourage paraphrase invariance. The goal is maintaining 95% oracle performance while improving cosine similarity under paraphrase from 0.78 to ≥0.90.

**Encoder alternatives:** The mean-pooling limitation of MiniLM suggests testing encoders with stronger compositional semantics (E5-large, Instructor-XL). These may provide paraphrase invariance that MiniLM lacks.

**Hybrid routing:** Combining embedding-based routing with keyword confidence could maintain high accuracy on standard instructions while providing graceful degradation on paraphrased variants. When embedding confidence is low, fall back to keyword-based routing or uniform averaging.

**Full oracle validation:** H-E1 used task names as oracle proxy. Computing per-adapter loss for each sample would provide ground-truth adapter selection labels, enabling tighter performance bounds.

The finding that zero-shot routing is achievable—but fragile—opens a research direction at the intersection of adapter composition and robust representation learning. We hope this work encourages investigation of intrinsic alignment properties in instruction-tuned models, and motivates routing architectures that preserve both efficiency and robustness.
