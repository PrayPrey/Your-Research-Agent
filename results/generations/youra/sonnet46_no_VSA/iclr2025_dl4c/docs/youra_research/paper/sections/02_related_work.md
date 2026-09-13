## 2. Related Work

Three bodies of work approach the question of source identity effects in SFT, but none closes
the gap we address.

### 2.1 Domain Mixture Optimization for Language Models

The influence of training data composition on model performance is well established for
pretraining. DoReMi [Xie et al., 2023] optimizes domain weights via Group Distributionally
Robust Optimization (DRO), demonstrating that the proportion of text from different domains
significantly affects downstream performance. BiMix [Ge et al., 2024] provides a bivariate
scaling law for mixture prediction. These works establish that composition matters — but they
operate at pretraining scale on general text, not code-specific SFT with execution-based
evaluation.

More recent work bridges toward SFT. DomainPilot [Zhang, 2026] applies domain-level loss
monitoring to optimize SFT data mixture, achieving +3.8% on LiveCodeBench. Chameleon
[Xie et al., 2025] uses leverage-score weighting for heterogeneous corpora in both pretraining
and finetuning settings. However, both of these approaches optimize mixture proportions from a
fixed pool of diverse sources — they do not isolate the causal effect of training on a single
source dataset identity. The question "what happens if you train only on HumanEval problems
versus only on MBPP problems?" remains unasked.

Our work is the code-specific instantiation of source-identity ablation: we fix the model,
token budget, format, and hyperparameters and vary only which source the training problems
come from.

### 2.2 Data Composition for Code SFT

Code SFT papers universally report training data compositions but do not ablate source
identity. WizardCoder [Luo et al., 2023] and OctoPack [Muennighoff et al., 2023] demonstrate
that augmenting data quality via Evol-Instruct or instruction formatting improves HumanEval
pass@1 — but they vary data quality and style simultaneously with source, making causal
attribution impossible. DeepSeek-Coder [Guo et al., 2024] reports fixed pretraining and
SFT compositions without source isolation.

Lv et al. [2025] show that 40% of OSS-Instruct data outperforms 100%, demonstrating
saturation effects in code SFT data — but they use a curated multi-source dataset, not a
single-source isolation. Chen et al. [2024] ablate atomic versus synthetic source types for
code SFT, finding both indispensable — the closest existing work to source-type comparison,
but not source dataset identity (HumanEval vs MBPP vs LeetCode), and without a cross-benchmark
transfer matrix or distributional alignment measurement.

The critical missing piece is a controlled 4-source × 2-benchmark transfer matrix under
token-budget equalization — the 2×4 grid of pass@1 values connecting training source
identity to test benchmark performance. Our work provides this.

### 2.3 Distributional Alignment as a Predictor

The principle that training-distribution alignment with the test distribution drives
performance is theoretically well-motivated [Ben-David et al., 2010] and empirically
validated for general instruction tuning. Zhang et al. [2025] (GRAPE) show that selecting
instruction-tuning data by distribution alignment outperforms 3× more data across diverse
tasks — the most direct precedent for our mechanistic claim. However, GRAPE operates on
general instruction-following tasks, not code-specific SFT, and does not measure the
alignment mechanism using code-specialized embeddings (CodeBERT) with a permutation test.

Parallel-SFT [arXiv 2604.20835, 2026] demonstrates asymmetric cross-language transfer in
code SFT — consistent with our asymmetric cross-benchmark finding. Magic Correlations [Fan
et al., 2025] document that transfer reliability varies by benchmark and scale — motivating
our scale comparison (H-C1).

Our contribution extends this line of work by providing the first permutation-tested evidence
(CodeBERT Spearman ρ=1.0, p=0.042, n=10,000) that embedding-space alignment between SFT
source and test benchmark governs pass@1 rank order for code generation.

### 2.4 Our Position

We synthesize these three threads: we apply the domain mixture insight (composition matters)
to code-specific SFT with source-identity isolation (no prior work does this), and we
validate the alignment mechanism using code-specialized embeddings with rigorous statistical
testing (extending GRAPE to code). The result is both an empirical finding (29.6pp source
identity effect) and a mechanistic explanation (embedding alignment predicts rank) that
enables principled data selection before training.
