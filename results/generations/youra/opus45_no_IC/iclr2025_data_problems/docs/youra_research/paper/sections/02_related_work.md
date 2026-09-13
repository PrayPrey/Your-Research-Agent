# Related Work

Our work intersects contamination detection, benchmark reliability, and learning dynamics analysis. We position against each area to show why existing approaches, while valuable, do not address contamination-performance quantification.

## Contamination Detection Methods

**N-gram overlap detection.** The GPT-3 decontamination methodology [Brown et al., 2020] established 13-gram matching as the standard for identifying verbatim overlap between training and evaluation data. EleutherAI's lm-evaluation-harness implements this approach for benchmark decontamination. Yang et al. [2023] extended this analysis to RedPajama, finding 8-18% overlap with HumanEval and demonstrating that simple paraphrasing bypasses n-gram detection. These methods detect contamination presence but do not quantify performance impact—a contaminated sample is flagged regardless of whether it affects model scores by 0.1% or 10%.

**Membership inference attacks.** MIA-based approaches [Carlini et al., 2021; Shi et al., 2024] determine whether specific examples appeared in training data by analyzing model behavior signals: loss, perplexity, confidence distributions. The MIMIR benchmark [Duan et al., 2024] standardizes these approaches for LLMs. Recent work on semantic membership inference [Mozaffari and Marathe, 2024] and keyword-based attacks [Antebi et al., 2025] improves detection accuracy. However, MIA methods answer "was this seen?" not "how much did seeing it help?"

**Output distribution analysis.** Dong et al. [2024] proposed CDD (Contamination Detection via Distribution) to identify contaminated samples through output distribution peakedness, paired with TED (Test Data Deviation) for mitigation. Choi et al. [2025] introduced Kernel Divergence Score for dataset-level contamination detection via fine-tuning sensitivity. These methods advance detection but remain focused on contamination presence rather than performance correlation.

## Benchmark Reliability

**Contamination-resistant benchmarks.** Recognizing contamination concerns, recent work has developed frequently-updated benchmarks resistant to training data leakage. LiveBench [White et al., 2024] provides monthly-updated questions with objective ground-truth scoring. LessLeak-Bench [Zhou et al., 2025] covers 83 software engineering benchmarks with automated anti-leakage measures. These efforts sidestep contamination rather than quantifying its effects.

**Benchmark analysis.** Sainz et al. [2023] catalyzed the contamination discussion with "NLP Evaluation in Trouble," documenting contamination levels across major benchmarks and arguing for community detection efforts. Their work establishes contamination as widespread but stops at detection—the correlation between contamination levels and score inflation remains unaddressed.

## Learning Dynamics and Memorization

**Training dynamics analysis.** Research on learning dynamics [Swayamdipta et al., 2020; Toneva et al., 2019] reveals that models learn different examples at different rates, with some samples memorized early while others require extended training. This work inspired our checkpoint-gradient approach—if memorization accumulates during training, contamination effects should correlate with training progress.

**Memorization studies.** Carlini et al. [2023] demonstrated that LLMs memorize substantial training content, with extractable memorization scaling with model size and data repetition. Biderman et al. [2023] provided training dynamics for the Pythia model family with documented checkpoint availability—the transparency enabling our checkpoint-gradient methodology.

## Our Position

Existing work establishes that contamination exists, can be detected, and that models memorize training content. What remains missing is the quantitative bridge: given X% contamination, how much does the benchmark score inflate? We address this gap through checkpoint-gradient analysis with capability detrending, providing the first contamination-inflation correlation measurement. Unlike detection methods that produce binary contaminated/clean labels, we quantify the relationship between contamination intensity and performance impact.
