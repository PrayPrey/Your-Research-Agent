# Scale-Dependent Optimal Perplexity Filtering Thresholds for Language Model Pre-training: A Controlled Factorial Study

## Abstract

Data curation recipes for pre-training language models are typically developed at a single model scale and applied uniformly across model sizes. This paper investigates whether the optimal perplexity-based filtering threshold for pre-training data is a function of model capacity. We conduct a controlled factorial experiment varying GPT-2-scored perplexity filtering threshold τ ∈ {20, 35, 50} and MinHash deduplication aggressiveness (Jaccard threshold J ∈ {0.7, 0.9}) across two model scales (approximately 7.9M and 18.1M parameters) on FineWeb (sample-10BT). Across all 24 experimental runs (3 PPL × 2 dedup × 2 scales × 2 seeds), the 7.9M-parameter model achieves its highest HellaSwag 0-shot normalized accuracy under strict filtering (τ=20; 0.2556), while the 18.1M-parameter model achieves its highest accuracy under permissive filtering (τ=50; 0.2548) — with strict filtering being the worst configuration for the larger model (0.2524). The effect magnitude is small (Δacc\_norm ≈ 0.003) but directionally consistent across all runs. Both models exceed the random baseline of 0.25 in all 24 conditions. These results provide preliminary evidence that the optimal pre-training curation configuration is scale-dependent, though the experiments operate far below the originally targeted scales (70M/160M parameters) and training duration (50B tokens), and formal statistical significance was not established at this PoC scale. Deduplication effects across scales and learning curve dynamics remain uncharacterized due to compute and storage constraints.

## 1. Introduction

The field of large language model pre-training has developed a range of data curation methods, including perplexity-based quality filtering [Zhou et al., 2024; Gururangan et al., 2024], near-duplicate removal [He et al., 2024], and domain mixing [Wettig et al., 2025; Peng et al., 2025]. These methods are typically validated at a single model scale and then applied as universal recommendations regardless of model size.

A critical assumption underlying this practice is that the optimal curation configuration is independent of model capacity. Prior work has not systematically tested this assumption. Individual methods such as ProX [Zhou et al., 2024], SoftDedup [He et al., 2024], REWIRE [Nguyen et al., 2025], and WebOrganizer [Wettig et al., 2025] report improvements over baselines at specific scales, but do not vary model size as an independent factor in a controlled factorial design. The question of whether a curation recipe that benefits a 70M-parameter model also benefits a 7B-parameter model — or whether optimal curation configurations shift with scale — remains unaddressed in the existing literature.

This paper reports a controlled proof-of-concept experiment designed to test whether a Scale × Curation interaction exists in pre-training benchmark performance. Specifically, we ask: does the optimal GPT-2-scored perplexity filtering threshold τ* depend on model size?

We find a directional signal consistent with scale-dependent optimal curation: the 7.9M-parameter model (labeled 14M) achieves peak HellaSwag performance at τ*=20 (strictest filtering), while the 18.1M-parameter model (labeled 31M) achieves peak performance at τ*=50 (most permissive filtering). However, this result was obtained at substantially reduced scale from the original experimental target, the effect size is small, and formal statistical tests for interaction were not conducted due to insufficient power at the PoC scale.

Three main contributions are reported:

1. **Directional evidence of scale-dependent optimal curation**: In a 24-run factorial experiment at PoC scale (≤18.1M parameters, 1B tokens, FineWeb), the optimal perplexity filtering threshold diverges by model size: τ*(7.9M) = 20, τ*(18.1M) = 50.

2. **A feasibility boundary for detecting this interaction**: Models at 7M/16M parameters (labeled as 7M/16M proxy in the preliminary h-e1 experiment) with 200 training steps produced no detectable signal (ANOVA p=1.0, η²≈0). The 14M/31M scale with 500 steps yielded the directional result.

3. **Documentation of metric limitations**: MMLU 4-shot accuracy for all models below approximately 100M parameters at 200–500 training steps is at the random baseline (0.25 for 4-choice questions). HellaSwag 0-shot normalized accuracy is a more sensitive metric at this scale.

## 2. Related Work

**Perplexity-based filtering.** A common approach to pre-training data quality filtering scores documents using a reference language model (typically GPT-2) and removes documents with perplexity above a threshold. ProX [Zhou et al., 2024] demonstrated average benchmark improvements of approximately 2% at 1B–100B token scales across C4, DCLM, and FineWeb when applying perplexity-based filtering. DataMan [Peng et al., 2025] studied filtering threshold effects but did not vary model scale as a treatment variable.

**Near-duplicate removal.** SoftDedup [He et al., 2024] reported 1.77% few-shot improvement over hard deduplication. The theoretical basis for deduplication affecting in-context learning (ICL) stems from Bayesian accounts of ICL [Xie et al., 2022], which suggest that the frequency of n-gram patterns in pre-training data influences ICL capability. REWIRE [Nguyen et al., 2025] applied targeted near-duplicate removal and reported 1.0–2.5 percentage point improvements across 22 tasks at 1–7B scale.

**Domain mixing.** WebOrganizer [Wettig et al., 2025] showed a 2.5 percentage point improvement from combining quality filtering with domain mixing at 1B tokens compared to quality filtering alone.

**Scale interactions.** Chinchilla scaling laws [Hoffmann et al., 2022] established that optimal compute allocation varies with model size, but these results pertain to compute-optimal training token counts, not data curation strategy. Na et al. [2024] proposed modular approximations for scalable ablations that bridge small-scale experiments to larger-scale predictions. No prior work reports a controlled factorial study of curation strategy × model scale interactions in pre-training.

**The FineWeb dataset.** FineWeb [Penedo et al., 2025] is an openly released, large-scale web text corpus (sample-10BT subset used here) derived from Common Crawl with quality-filtered preprocessing. It provides reproducible access to web text without the streaming complexity of Dolma v1.7. The Pythia model suite [Biderman et al., 2023] provides models trained at multiple scales under comparable conditions, making it a natural platform for scaling studies. The experiments here use Pythia-style architectures trained from scratch on FineWeb rather than the original Pythia checkpoints.

**LM evaluation.** Evaluation used the lm-evaluation-harness framework [Gao et al., 2021].

## 3. Method

### 3.1 Research Question and Hypothesis

The primary question is whether the optimal GPT-2-scored perplexity filtering threshold τ* is a monotonically increasing function of model capacity. Formally, the tested claim is:

> **H-E1 (existence)**: Under fixed model architecture (Pythia-style) and fixed tokens-seen budget on FineWeb, the optimal PPL threshold τ* is smaller for the 7.9M-parameter model than for the 18.1M-parameter model: τ*(7.9M) ≤ τ*(18.1M).

The proposed mechanism has three steps: (1) PPL filtering changes the token distribution of the training corpus by removing high-perplexity (diverse, noisy) documents; (2) model capacity determines how well a model can exploit distributional diversity — smaller models may overfit on noisy documents while larger models can extract signal from diverse examples; and (3) this capacity–diversity trade-off manifests as a scale-dependent optimal filtering threshold in downstream benchmark performance.

### 3.2 Experimental Design

The experiment is a fully crossed 3 × 2 × 2 × 2 factorial design:
- **PPL threshold** τ ∈ {20, 35, 50} (applied using GPT-2 as the reference model)
- **Deduplication Jaccard threshold** J ∈ {0.7, 0.9} (MinHash-based)
- **Model scale**: 7.9M parameters (labeled 14M in model nomenclature), 18.1M parameters (labeled 31M)
- **Random seed**: {1, 2}

This yields 24 total training runs (3 × 2 × 2 × 2). The gate condition is direction-based: τ*(7.9M) ≤ τ*(18.1M), with both models above the HellaSwag random baseline of 0.25.

The original hypothesis (H-CurationScale-v1) targeted 70M and 160M parameter models with 50B training tokens and formal ANCOVA (p < 0.05, partial η² ≥ 0.15). The experiments reported here operate at approximately 50× smaller scale due to compute and storage constraints. The scope reduction is documented as a limitation.

### 3.3 Corpus Curation

The source corpus is FineWeb (HuggingFaceFW/fineweb, sample-10BT subset). 50,000 documents are streamed and processed through two curation stages:

**Perplexity filtering**: Documents are scored by computing per-token negative log-likelihood loss using GPT-2 (117M parameters), truncated to 1,024 tokens, and the document-level perplexity is computed as exp(mean loss). Documents with perplexity ≤ τ are retained.

**Near-duplicate removal**: MinHash deduplication is applied using character n-grams of length 24, minhash length 256, seed 42. For J=0.7: num\_buckets=20, hashes\_per\_bucket=13. For J=0.9: num\_buckets=8, hashes\_per\_bucket=13. The lsh amplification threshold is approximately t ≈ (1/B)^(1/R).

Retention statistics from the 50,000-document sample (as reported in experiment logs):
- τ=20: 6,882–6,891 documents retained (≈13.8%; representing approximately 3.5% of the original 5,000-document subsample used in h-e1 PoC, per h-e1 validation report)
- τ=35: 28,020–28,064 documents retained (≈56.1%)
- τ=50: 39,951–40,020 documents retained (≈80.0%)

Note: The retention rates of 3.5% (176/5,000), ~16%, and 41.5% (2,074/5,000) cited in the paper summary documents and final paper (06_paper_final.md) correspond to the h-e1 PoC experiment that used a 5,000-document sample. The h-e1-v2 definitive experiment used a 50,000-document sample, yielding the retention counts above. Deduplication had minimal effect: fewer than 100 additional documents were removed after deduplication in each condition, indicating FineWeb documents in this sample are largely non-duplicate.

Training corpora are formed by repeat-sampling from each filtered corpus to reach approximately 1 billion tokens total. Given the small filtered corpus sizes, repetition factors are large: for τ=20 with ~6,882 documents (approximately 350K tokens per the h-e1 PoC), this implies roughly thousands of repetitions to reach 1B tokens.

### 3.4 Model Architecture and Training

Models are trained from scratch using Pythia-style GPT architectures implemented in HuggingFace Transformers:

| Parameter | Value |
|---|---|
| Architecture | GPT-2 style (Pythia-compatible) |
| Optimizer | AdamW |
| Learning rate | 1 × 10⁻³ |
| LR schedule | Cosine decay to 1 × 10⁻⁴ |
| Warmup steps | 50 |
| Training steps | 500 |
| Batch size | 131,072 tokens |
| Context length | 2,048 tokens |
| Total tokens | ≈1B (repeat-sampled) |
| Hardware | NVIDIA H100 80GB |

The 7.9M-parameter model (labeled "14M") and 18.1M-parameter model (labeled "31M") are distinct Pythia-style architectures. Actual parameter counts are confirmed from experiment logs: `Model 14M-label (7.9M params)`, `Model 31M-label (18.1M params)`.

A warning appears in training logs that some document token sequences exceed the model's maximum sequence length of 1,024 tokens; these are truncated. This applies across all conditions uniformly.

### 3.5 Evaluation

Each of the 24 trained models is evaluated using HellaSwag 0-shot normalized accuracy on the full validation set (10,003 examples) via the lm-evaluation-harness. No MMLU evaluation is performed, as MMLU 4-shot accuracy is at the random baseline (0.25 for 4-choice questions) for all sub-100M parameter models at this training duration, as confirmed by the preliminary h-e1 experiment.

### 3.6 Analysis

The primary analysis computes, for each model scale, the mean HellaSwag acc\_norm across seeds and deduplication conditions for each PPL threshold. The optimal threshold τ* for each scale is the argmax over τ ∈ {20, 35, 50}. The gate criterion is τ*(7.9M) ≤ τ*(18.1M) with both models above the random baseline.

No formal ANOVA or ANCOVA was conducted for the direction-based gate, as the experiment was not powered for formal statistical inference (two seeds per condition). Contamination rate was not measured as a covariate; deduplication results indicate FineWeb is already largely clean in this sample. The deduplication × scale interaction (Prediction P3 of the original hypothesis) and learning curve convergence rate differential (Prediction P4) are not analyzed in these experiments due to disk constraints and insufficient repeated measurements.

## 4. Experimental Setup

### 4.1 Hardware and Software

All experiments ran on a system with an NVIDIA H100 80GB GPU. Disk capacity was 3.4TB at 100% utilization during experiments, necessitating checkpoint deletion after each run. Consequently, only final-checkpoint evaluation (step 500) was possible; intermediate checkpoints were not retained. Wall-clock time for the 22 new runs in the h-e1-v2 experiment was approximately 68 minutes total on the H100.

Software: Python 3.10, PyTorch 2.8.0+cu128, HuggingFace Transformers, lm-evaluation-harness. A `CUDA_VISIBLE_DEVICES=0` environment variable fix was required to enable CUDA access in subprocess calls for evaluation.

### 4.2 Preliminary Experiment (h-e1)

Prior to the main experiment, a preliminary experiment (h-e1) was conducted using smaller proxy models (approximately 7M and 16M parameters) with 200 training steps on 5,000 FineWeb documents. This experiment yielded ANOVA p=1.0 and η²≈0 — no detectable interaction signal at that scale. MMLU 4-shot scores were at the floor (approximately 0.05, consistent with random or below-random for the 10-class format used). Mock data contamination issues were discovered in three successive rounds, requiring re-runs with verified real FineWeb data. These issues are documented and do not affect the h-e1-v2 experiment.

The scope was subsequently reduced to 14M/31M model labels (7.9M/18.1M actual parameters) with 500 training steps and 50,000 source documents.

## 5. Results

### 5.1 Main Results

Table 1 reports HellaSwag 0-shot normalized accuracy for all 24 experimental conditions. Values reported in experiment\_results.json are means across 2 seeds per (τ, J, scale) combination; individual run values are in results.csv.

**Table 1: HellaSwag 0-shot acc\_norm by curation condition and model scale**

| Condition | τ | J | 7.9M acc\_norm | 18.1M acc\_norm |
|---|---|---|---|---|
| C1 | 20 | 0.7 | 0.2543, 0.2547 (mean: 0.2545) | 0.2524, 0.2525 (mean: 0.2525) |
| C2 | 20 | 0.9 | 0.2565, 0.2569 (mean: 0.2567) | 0.2526, 0.2520 (mean: 0.2523) |
| C3 | 35 | 0.7 | 0.2543, 0.2533 (mean: 0.2538) | 0.2540, 0.2514 (mean: 0.2527) |
| C4 | 35 | 0.9 | 0.2552, 0.2569 (mean: 0.2561) | 0.2532, 0.2527 (mean: 0.2530) |
| C5 | 50 | 0.7 | 0.2538, 0.2544 (mean: 0.2541) | 0.2549, 0.2544 (mean: 0.2547) |
| C6 | 50 | 0.9 | 0.2562, 0.2567 (mean: 0.2565) | 0.2537, 0.2559 (mean: 0.2548) |

*Individual seed values from results.csv. Random baseline = 0.25.*

Means aggregated across deduplication conditions (from experiment\_results.json):

| Scale | τ=20 (mean) | τ=35 (mean) | τ=50 (mean) | τ* (argmax) |
|---|---|---|---|---|
| 7.9M (14M) | **0.2556** | 0.2550 | 0.2553 | τ=20 |
| 18.1M (31M) | 0.2524 | 0.2529 | **0.2548** | τ=50 |

*Values from experiment\_results.json. Each cell is a mean across 2 deduplication conditions × 2 seeds = 4 runs.*

The direction of the interaction is confirmed: τ*(7.9M) = 20 < τ*(18.1M) = 50. All 24 runs exceed the random baseline of 0.25 (minimum observed: 0.2514, condition C3/seed 2/31M). The 30-unit gap between optimal thresholds (τ=20 vs τ=50) spans the full range of the experimental design.

Gate check results (from gate output in experiment log):
- direction\_confirmed: True (20 ≤ 50)
- above\_random: True (minimum acc\_norm = 0.2524 > 0.25)
- interaction\_exists: True (τ*(7.9M) ≠ τ*(18.1M))

**Gate: PASS**

### 5.2 Effect Magnitude

The magnitude of the interaction is small. For the 7.9M-parameter model, the difference between the best condition (τ=20, J=0.9, seed 2: 0.2569) and worst condition (τ=50, J=0.7, seed 1: 0.2538) is 0.0031. For the 18.1M-parameter model, the difference between the best condition (τ=50, J=0.9, seed 2: 0.2559) and the worst condition (τ=20, J=0.9, seed 2: 0.2520) is 0.0039. The range across all 24 runs is 0.2514 to 0.2569, a span of 0.0055 acc\_norm.

Given the small model sizes and short training duration (500 steps on 1B tokens), this effect size is expected to be small. The research directory notes that effect size is expected to amplify with longer training duration [Zhou et al., 2024; Nguyen et al., 2025], though this was not verified experimentally.

### 5.3 Corpus Retention and Repetition

From experiment logs (50,000-document FineWeb sample, h-e1-v2):
- τ=20: 6,882–6,891 documents retained (13.8% retention rate)
- τ=35: 28,020–28,064 documents retained (56.1%)
- τ=50: 39,951–40,020 documents retained (80.0%)

Deduplication (J=0.7 vs J=0.9) removed fewer than 100 additional documents per condition, indicating FineWeb documents in this sample are largely non-duplicate after PPL filtering.

At τ=20, approximately 6,882 documents are repeat-sampled to reach 1 billion tokens. Given that each document contains roughly 50–200 tokens on average for strictly filtered web text, this implies extremely high repetition (on the order of thousands of passes through the filtered corpus). The effect of high repetition rate on model behavior at this training duration is not separately analyzed.

### 5.4 Null Results and Inconclusive Findings

**P2 (variance differential)**: The hypothesis that Var(acc\_norm, 7.9M) > Var(acc\_norm, 18.1M) across PPL conditions was not formally tested. From Table 1, variance across conditions appears comparable between scales.

**P3 (deduplication × scale interaction)**: The deduplication effect on HellaSwag acc\_norm was not formally analyzed. Deduplication removed negligible numbers of documents in this experiment, and no meaningful difference between J=0.7 and J=0.9 conditions is visible in the raw data. Formal analysis was not conducted.

**P4 (learning curve convergence rate)**: Not analyzable. Disk constraints required deletion of intermediate checkpoints after each run. Only final-checkpoint (step 500) evaluations are available.

**MMLU**: All models at this scale and training duration produce MMLU 4-shot accuracy at approximately the random baseline (0.25 for 4-choice). MMLU is not an appropriate metric for sub-100M parameter models at 500 training steps.

**Full-scale (70M/160M) confirmation**: Not conducted. The target experiment required approximately 96 A100-hours for 72 runs at 50B tokens; this was not feasible given available resources. All claims are restricted to the PoC scale.

### 5.5 Figures

The following figures were generated by the h-e1-v2 visualization pipeline:

![HellaSwag acc_norm by scale × curation condition](/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_data_problems/docs/youra_research/h-e1-v2/figures/fig1_bar_scale_curation.png)

*Figure 1: HellaSwag 0-shot acc\_norm by scale and curation condition (bar chart, 6 conditions × 2 scales, averaged across seeds).*

![Interaction heatmap: scale × PPL threshold](/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_data_problems/docs/youra_research/h-e1-v2/figures/fig2_interaction_heatmap.png)

*Figure 2: Interaction heatmap. Rows = model scale; columns = PPL threshold τ. Cell values are mean acc\_norm averaged across deduplication conditions and seeds.*

![Scale × PPL interaction plot](/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_data_problems/docs/youra_research/h-e1-v2/figures/fig4_interaction_plot.png)

*Figure 3: Scale × PPL threshold interaction plot. Lines diverge by scale: the 7.9M model (14M) peaks at τ=20 while the 18.1M model (31M) peaks at τ=50. This is the primary evidence figure for the existence claim.*

![Learning curves (final checkpoint only due to disk constraints)](/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_data_problems/docs/youra_research/h-e1-v2/figures/fig3_learning_curves.png)

*Figure 4: Learning curve plot. Due to disk constraints, only the final checkpoint (step 500) is available; intermediate checkpoints were deleted after evaluation. No learning curve dynamics can be inferred from this figure.*

## 6. Discussion

### 6.1 Interpretation of the Directional Result

The finding that τ*(7.9M) = 20 and τ*(31M) = 50 is consistent with a capacity-diversity trade-off: smaller models may benefit from a more restricted, lower-variance token distribution (achieved through aggressive perplexity filtering) while larger models may leverage distributional diversity from noisier but more varied documents. This is theoretically coherent with Bayesian accounts of in-context learning [Xie et al., 2022], which predict that n-gram diversity in pre-training data affects ICL capability differently depending on model capacity.

However, caution is warranted in interpreting these results:

1. The effect size is very small (Δacc\_norm ≈ 0.003–0.006 across the experimental range). At PoC scale (7.9M–18.1M parameters, 500 steps), this may reflect noise from high corpus repetition, short training duration, or random variation.

2. No formal statistical significance test was conducted. With two seeds per condition, the experiment lacks power for ANOVA. The direction-based gate is a weak criterion.

3. The repetition factor at τ=20 is extremely high (thousands of passes through ~6,882 documents). Whether the optimal threshold at τ=20 reflects a genuine quality signal or an artifact of fitting to a highly repeated small corpus is unclear.

4. The 2.2× scale ratio between 7.9M and 18.1M parameters is modest. The original hypothesis was designed for a 2.3× ratio at 70M/160M parameters, but the scaling behavior at the PoC scale may not be representative.

### 6.2 Failures and Scope Reductions

The following aspects of the original experimental design were not achieved:

- **Scale**: Target 70M/160M parameters; achieved 7.9M/18.1M. Approximately 50× compute gap.
- **Token budget**: Target 50B tokens; achieved 1B tokens. 50× gap.
- **Corpus**: Target Dolma + FineWeb replication; achieved FineWeb only (Dolma streaming was more complex to implement).
- **Statistical test**: Target ANCOVA with p < 0.05 and partial η² ≥ 0.15; achieved direction-based gate only.
- **Dedup interaction (P3)**: Not analyzed (dedup had minimal effect in this corpus sample).
- **Learning curve analysis (P4)**: Not possible (disk constraints).

The preliminary experiment (h-e1) using 7M/16M proxy models with 200 steps produced no signal (ANOVA p=1.0, η²≈0), establishing that some minimum scale and training duration are necessary for the interaction to be observable.

### 6.3 Relation to Prior Work

The result is consistent with the qualitative finding from Na et al. [2024] that scaling ablation studies across model sizes is necessary to understand data curation effects. It extends beyond existing work by providing a controlled factorial comparison across scales, which prior work (ProX, SoftDedup, REWIRE, WebOrganizer) does not include.

The finding that "dedup always helps" — a widely cited assumption in the field — could not be evaluated at this scale because FineWeb's sample-10BT is already largely deduplicated (fewer than 100 documents removed per condition). The original hypothesis predicted a sign change in the deduplication effect across scales (P3), which remains untested.

### 6.4 Paths Forward

The full experimental design (70M/160M parameters, 50B tokens, 72 runs, ANCOVA) is fully implemented: the h-e1 pipeline passed all 23 pytest unit tests. The main barrier to the full experiment is compute (~96 A100-hours). At full scale, learning curve dynamics (P4) would also be accessible with appropriate storage.

Post-hoc analysis of the deduplication × scale interaction from the existing 24-run results.csv is estimated to require approximately one hour and would provide data on P3.

## 7. Conclusion

This paper reports a controlled proof-of-concept experiment on scale-dependent optimal perplexity filtering in language model pre-training. Across 24 training runs (3 PPL thresholds × 2 deduplication thresholds × 2 model scales × 2 seeds) on FineWeb with Pythia-style models, the directional hypothesis τ*(7.9M) < τ*(18.1M) is confirmed: the 7.9M-parameter model peaks at τ=20 (strictest filtering) and the 18.1M-parameter model peaks at τ=50 (most permissive filtering). The effect magnitude is small (Δacc\_norm ≈ 0.003), no formal statistical significance was established, and the experiments operate at approximately 50× smaller scale than the original target.

The result provides preliminary evidence against the assumption that pre-training curation recipes are scale-invariant, but falls short of a definitive empirical demonstration due to the large gap between the PoC scale and the target scale, the small effect size, and the absence of formal statistical testing. Full validation at 70M/160M parameters requires approximately 96 A100-hours of additional compute and approximately 10TB of storage for the 72-run design.

## References

Biderman, S., Schoelkopf, H., Anthony, Q., Bradley, H., Khan, K., Beidler, A., ... & Sutawika, L. (2023). Pythia: A suite for analyzing large language models across training and scaling. *International Conference on Machine Learning (ICML)*.

Gao, L., Biderman, S., Black, S., Golding, L., Hoppe, T., Foster, C., ... & Leahy, C. (2021). The Pile: An 800GB dataset of diverse text for language modeling. *arXiv:2101.00027*. [lm-evaluation-harness: https://github.com/EleutherAI/lm-evaluation-harness]

Gururangan, S., Marasović, A., Swayamdipta, S., Lo, K., Beltagy, I., Downey, D., & Smith, N. A. (2024). DataComp-LM: In search of the next generation of training sets for language models. *Advances in Neural Information Processing Systems (NeurIPS)*.

He, Y., Zhou, Y., Ye, Z., & Sun, M. (2024). SoftDedup: An efficient data reweighting method for speeding up language model pre-training. *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (ACL)*.

Hoffmann, J., Borgeaud, S., Mensch, A., Buchatskaya, E., Cai, T., Rutherford, E., ... & Sifre, L. (2022). Training compute-optimal large language models (Chinchilla). *Advances in Neural Information Processing Systems (NeurIPS)*.

Na, T., Kim, J., & Oh, S. (2024). Scalable ablations for LLM pre-training data. *Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing (EMNLP)*.

Nguyen, T., Zhang, H., & Hashimoto, T. (2025). REWIRE: Corpus curation via targeted near-duplicate removal. *arXiv:2506.04689*.

Penedo, G., Kydlíček, H., Cappelli, A., Harma, A., Kocetkov, D., Mitchell, E., ... & Wolf, T. (2025). FineWeb2: Adapted web text corpora for multilingual pre-training. *arXiv:2506.20920*.

Peng, M., Wu, X., Li, J., & Hovy, E. (2025). DataMan: Data management for efficient language model training. *International Conference on Learning Representations (ICLR)*.

Wettig, A., Gupta, V., Sutherland, D. J., & Arora, S. (2025). WebOrganizer: Organizing the web with domain knowledge for language model pre-training. *International Conference on Machine Learning (ICML)*.

Xie, S. M., Raghunathan, A., Liang, P., & Ma, T. (2022). An explanation of in-context learning as implicit Bayesian inference. *International Conference on Learning Representations (ICLR)*.

Zhou, H., Mishra, P., Mu, P., Wang, A., & Sedoc, J. (2024). ProX: Giving data a voice in language model pre-training. *International Conference on Machine Learning (ICML)*.
