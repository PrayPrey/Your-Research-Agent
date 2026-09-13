# Related Work

## Temperature Scaling and Post-Hoc Calibration

Temperature scaling, introduced by Guo et al. (2017), optimizes a single parameter T to rescale logits before softmax, improving Expected Calibration Error (ECE) for modern neural networks. This method incurs zero inference overhead since T is applied post-training. However, Guo et al. focused on calibration metrics (ECE), not selective prediction AUROC—our work extends this by evaluating temperature scaling's effectiveness for rejecting incorrect predictions.

More recent work by Nixon et al. (2019) explored ensemble temperature scaling, and Desai & Durrett (2020) studied calibration in NLG tasks. **None report AUROC vs cost trade-offs**, instead treating calibration and selective prediction as separate problems.

## Conformal Prediction for Language Models

Conformal prediction provides distribution-free coverage guarantees for uncertainty sets. Kumar et al. (2023) introduced conformal prediction for selective NLG, demonstrating validity under distribution shift. Su et al. (2024) extended this to API-only settings (no logit access) using sample frequency and semantic similarity for nonconformity scores, achieving competitive performance on hallucination detection.

While these methods establish conformal prediction's viability for LLMs, **they do not compare inference cost across multiple UQ approaches**. Our work tests conformal prediction's cross-dataset generalization (HaluEval calibration → TruthfulQA test) and positions it within the cost-performance space.

## Monte Carlo Dropout

Gal & Ghahramani (2016) showed that dropout at inference time approximates Bayesian inference, enabling uncertainty estimation via variance across k stochastic forward passes. This approach has been applied to vision tasks (Kendall & Gal, 2017) and NLP (Xiao & Wang, 2019), typically using k=10-30 samples.

Recent work on LLM uncertainty includes Kuhn et al. (2023) on semantic entropy and Lin et al. (2023) on conformal language modeling. However, **k-dependency for LLMs remains understudied**—prior work does not systematically vary k to identify efficiency sweet spots. Our finding that k=3 suffices for AUROC ≥ 0.70 at 8B scale contrasts with vision domain conventions (k=30 in retinal-selective-prediction).

## Selective Prediction Benchmarks

Yang et al. (2023) applied selective prediction to TruthfulQA, showing that uncertainty-based rejection improves accuracy. Their work validates TruthfulQA as a selective prediction benchmark but **does not compare multiple UQ methods or report inference costs**.

Zhang et al. (2020) compared ensemble and compositional calibration methods, introducing kernel-density ECE estimators. While comprehensive on calibration metrics, this work predates LLM-scale models and lacks selective prediction evaluation.

## Our Positioning

Existing work evaluates UQ methods in isolation or compares methods without cost analysis. **We are the first to systematically benchmark AUROC vs inference cost** for multiple UQ method variants on the same selective prediction task. Our Pareto frontier framing shifts the question from "which method wins" to "which method for my budget," enabling practitioners to make informed trade-offs rather than defaulting to the most expensive option.
