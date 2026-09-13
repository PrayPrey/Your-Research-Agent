# 2. Related Work

Our work sits at the intersection of three research threads: controlled pre-training infrastructure, domain mixing optimization, and task-specific data selection. We review each and explain why, despite rich progress in each area, the per-domain × per-benchmark specificity question remains open.

## 2.1 Controlled Pre-Training Infrastructure

The Pile [Gao et al., 2020] introduced a 22-domain heterogeneous corpus designed to improve cross-domain generalization. With 800GB of text spanning Wikipedia, Books, GitHub, PubMed, StackExchange, and 17 other domains, The Pile remains the most carefully documented large-scale pre-training corpus in terms of domain composition and proportions.

Pythia [Biderman et al., 2023] extended this infrastructure by training 16 autoregressive language models (70M–12B parameters) on The Pile with exact dataloader documentation, releasing 154 intermediate checkpoints per model. Pythia's explicit design goal was to enable training dynamics and data attribution studies — yet prior work using Pythia has focused on memorization, scaling laws, and deduplication effects [Biderman et al., 2023], not on exploiting the checkpoint trajectory for domain exposure analysis. MiniPile [Kaddour, 2023] demonstrated that a 6GB embedding-filtered subset of The Pile retains ~98% of GLUE performance — confirming that quality filtering matters — but focused on aggregate performance rather than per-domain × per-benchmark decomposition.

We use the same Pythia/Pile infrastructure but exploit it differently: rather than comparing different training runs, we treat the 154-checkpoint trajectory as a panel dataset with naturally occurring domain exposure variation, enabling within-family analysis without new training.

## 2.2 Domain Mixing Optimization

The most direct precursor to our work is the line of research optimizing domain mixing ratios during pre-training. DoReMi [Xie et al., 2023] uses a small proxy model to find domain weights that minimize excess loss, demonstrating that optimized domain mixing improves aggregate validation loss and downstream benchmarks. RegMix [Liu et al., 2024] extends this to regression-based mixing law: fitting a linear model from domain weights to validation loss at proxy-model scale, then extrapolating to larger models. This linear mixing law framework is the statistical foundation our panel regression adopts, though we apply it to individual benchmark scores rather than aggregate validation loss.

Data Mixing Laws [Ye et al., 2024] provided the most direct evidence that domain mixing ratios have predictable effects: their scaling laws incorporate domain proportions as explicit predictors. Our work is consistent with this framing but adds within-family variation as the source of domain exposure differences, rather than cross-run variation. AutoScale [Feiyang et al., 2025] and Data Mixing Agent [Yang et al., 2025] extend the optimization framing with scale-aware and RL-based approaches, respectively — highlighting that optimal mixing ratios may be scale-dependent, a concern directly relevant to our 70M preliminary results.

None of these approaches produce a per-domain coefficient for individual benchmarks (MMLU, HellaSwag, ARC, WinoGrande separately). They optimize or characterize *aggregate* performance. Our panel regression framework is the first designed to estimate benchmark-specific domain coefficients from within-family variation.

## 2.3 Task-Specific Data Selection

CoLoR-Filter [Brandfonbrener et al., 2024] demonstrates that task-conditioned data selection (choosing training examples that most reduce per-task loss) achieves 11–25× data efficiency for specific downstream benchmarks. This is the theoretical motivation for domain-benchmark specificity: different tasks benefit from different data subsets. However, CoLoR-Filter operates at the document-selection level (filtering entire corpora) rather than domain-exposure level, and does not quantify which pre-training domains produce capability gains in fixed-data settings.

Topic Over Source [Peng et al., 2025] provides the most relevant finding: topic-based mixing consistently outperforms source-based mixing across RegMix, DoReMi, and temperature sampling strategies. This suggests that the *semantic content* of training data (what topics documents cover) matters more than the source label — consistent with our hypothesis that cognitive content proxies (entity density, narrative coherence, formal syntax) are the operative mechanism, not domain labels per se.

## 2.4 Benchmark Contamination

Our methodology requires benchmark evaluation scores that reflect genuine model capability rather than training data memorization. LatestEval [Li et al., 2023] and Evading Data Contamination Detection [Dekoninck et al., 2024] highlight the difficulty of contamination auditing. We note this concern explicitly and include contamination-adjusted scores in our evaluation pipeline (lm-evaluation-harness 13-gram decontamination). Our observational design means contamination would bias domain-benchmark correlations if Wikipedia's training data systematically overlaps with MMLU test questions more than other domains do — we treat this as a documented limitation (L3 in Section 6).

## 2.5 Positioning

Our approach is complementary to each prior thread. We use Pythia/Pile infrastructure (§2.1) but exploit within-family checkpoint variation rather than cross-run comparison. We adopt the linear mixing law framework (§2.2) but apply it to per-benchmark scores rather than aggregate loss. We are motivated by task-specific data selection (§2.3) but operate in an observational rather than interventional setting. The specific contribution — per-domain coefficients for individual benchmarks from a within-family panel analysis — has not been produced by any prior work.
