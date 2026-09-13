# 2. Related Work

Our work builds on three research threads: multi-dimensional trustworthiness evaluation frameworks, single-dimension benchmark development, and intervention studies targeting trustworthiness failures. We position our contribution as extending aggregation-based approaches (HELM, BIG-bench) by analyzing cross-dimensional correlation structure rather than just reporting separate scores.

## Multi-Dimensional Evaluation Frameworks

**HELM (Holistic Evaluation of Language Models)** aggregates performance across 50+ benchmarks spanning accuracy, robustness, fairness, bias, toxicity, and efficiency dimensions. While HELM represents the most comprehensive multi-dimensional evaluation to date, it reports separate scores per dimension without testing whether failures correlate across dimensions or cluster into shared failure modes.[^1] Our correlation analysis reveals that three HELM-included benchmarks (TrustfulQA, AdvBench, BOLD) exhibit r > 0.99 correlations, suggesting that score aggregation may mask latent structure. Where HELM treats benchmarks as independent scorecards, we treat them as measurement instruments for discovering correlation patterns.

[^1]: We verified via manual inspection of Liang et al. (2022) main paper, appendices, and supplementary materials — no cross-benchmark correlation analysis reported. HELM's evaluation protocol computes per-benchmark scores but does not analyze correlation structure across dimensions.

**BIG-bench** similarly aggregates 200+ tasks but focuses on capability breadth rather than trustworthiness-specific dimensions. Recent work analyzing BIG-bench performance has identified task clustering based on difficulty but not cross-dimensional trustworthiness correlations. Our approach differs by explicitly testing the independence assumption underlying dimension-separated evaluation: if reliability, robustness, and fairness arise from independent mechanisms, correlations should be near-zero; observed r > 0.99 challenges this framing.

## Single-Dimension Trustworthiness Benchmarks

**TruthfulQA** measures reliability by testing whether models generate truthful responses to 817 questions designed to elicit common misconceptions. The benchmark establishes that larger models do not necessarily produce more truthful outputs, with accuracy gains plateauing or declining at scale. Our work complements this by showing TruthfulQA scores correlate r = 0.998 with AdvBench robustness and r = 0.993 with BOLD fairness, suggesting reliability failures co-occur with failures in other dimensions at near-identical rates.

**AdvBench** evaluates robustness to adversarial attacks through jailbreak prompts and input perturbations. Prior work documents that adversarially robust models often require explicit robustness training (adversarial fine-tuning, certified defenses). Our correlation analysis shows AdvBench scores tightly coupled with TrustfulQA (r = 0.998) and BOLD (r = 0.996), raising the question whether robustness training simultaneously affects reliability and fairness—a prediction testable through targeted intervention experiments (deferred to future work due to clustering taxonomy failure).

**BOLD (Bias in Open-Ended Language Generation)** quantifies fairness by measuring sentiment and regard differences across demographic groups. BOLD establishes that pre-trained models exhibit systematic bias amplification, with disparities persisting even after alignment training. Our finding of r > 0.99 correlations between BOLD and reliability/robustness benchmarks suggests bias amplification may share root causes with hallucination and adversarial brittleness, though our 3-benchmark design cannot distinguish unified constructs from insufficient measurement resolution.

## Trustworthiness Interventions

Prior work documents that alignment fine-tuning improves multiple dimensions simultaneously: RLHF reduces hallucinations (reliability) while also decreasing toxic outputs (safety) and improving demographic parity (fairness). However, this literature lacks a quantitative taxonomy predicting *which* dimensions co-vary under interventions. Our correlation-based approach formalizes this intuition—if TrustfulQA and AdvBench correlate at r = 0.998, interventions targeting reliability plausibly affect robustness as well. Testing this prediction requires validated failure mode clusters, which our clustering analysis failed to produce (silhouette = 0.274 < 0.5), leaving intervention validation as future work.

## Positioning Our Contribution

We extend multi-dimensional evaluation from aggregation (HELM) to correlation analysis, revealing that three major benchmarks measure near-redundant constructs (r > 0.99) rather than orthogonal dimensions. This challenges the design assumption in single-dimension benchmarks (TrustfulQA, AdvBench, BOLD), which were developed in isolation without testing empirical independence. Unlike intervention studies that qualitatively observe multi-dimensional improvements, we formalize correlation structure to enable mechanism-guided intervention design—though taxonomy validation failed, revealing 3-benchmark designs insufficient for clustering despite perfect stability.

The key difference from all prior work: we explicitly test whether trustworthiness dimensions are independent (null hypothesis: r ~ 0) or correlated (alternative: r > 0.3), finding correlations 3× stronger than hypothesized thresholds. This shifts evaluation paradigm from dimension-independent scorecards to correlation-aware diagnostic tools, with the failure to resolve distinct clusters revealing methodological constraints rather than refuting the correlation-based approach itself.
