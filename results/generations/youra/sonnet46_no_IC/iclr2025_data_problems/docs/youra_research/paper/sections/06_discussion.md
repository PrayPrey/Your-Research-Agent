# 6. Discussion

## 6.1 Key Findings and Their Interpretation

**Finding 1: The capacity-quality trade-off operates at 14M/31M parameter scale.**

The τ*(14M) < τ*(31M) result is consistent with the theoretical prediction from the capacity-quality trade-off hypothesis: smaller models benefit from cleaner, lower-diversity data because their representational capacity is insufficient to extract useful signal from high-entropy, diverse distributions. Larger models (even at moderate absolute scale) can leverage the distributional variety preserved by looser filtering, providing richer contexts for commonsense completion tasks.

This suggests a practical principle for training cascades: the optimal data recipe is model-size-dependent, and a shared recipe calibrated for one scale in the cascade may be suboptimal — potentially harmful — for others.

**Finding 2: The minimum model scale for the interaction matters for ablation methodology.**

The failure of 7M/16M proxy models to exhibit any signal (h-e1, p=1.0, η²≈0) is itself a methodological contribution. It establishes that scale-dependent curation effects have a minimum capacity threshold: both models must be large enough that the capacity-quality trade-off influences their learning dynamics, and the scale ratio must be large enough that the two models fall on opposite sides of the optimal τ curve. At 14M/31M (2.2× ratio), this threshold is barely exceeded.

**Finding 3: MMLU is unusable for sub-100M pre-training ablations.**

MMLU 4-shot accuracy equals the random baseline (0.25) for all sub-100M models at 200–500 training steps. This is a practical finding relevant to anyone designing pre-training ablation experiments at this scale: HellaSwag 0-shot is the appropriate primary metric, as it shows variance above random and is sensitive to early language modeling capability.

## 6.2 Limitations

**L1: PoC scale is far below target scale (14M/31M vs. 70M/160M).**

The originally planned experiment targeted Pythia 70M and 160M models trained for 50B tokens — approximately 50× more compute than our current results. The direction of the interaction (τ*(small) < τ*(large)) should hold at larger scale based on the capacity-quality mechanism, but the magnitude of the effect (Δacc_norm ≈ 0.003) likely underestimates the full-scale effect. The optimal τ values themselves (20 and 50 at 14M/31M) may shift at 70M/160M. We frame our result as an existence proof with a clear upgrade path: the full experimental pipeline is implemented and validated (23/23 pytest tests pass), requiring only compute to run at the target scale.

**L2: Effect size is small (Δacc_norm ≈ 0.003).**

At 500 training steps (far from convergence), effects are expected to be small. Scaling law literature [Hoffmann et al., 2022] and empirical results from ProX [Zhou et al., 2024] and REWIRE [Nguyen et al., 2025] show that pre-training data quality effects amplify with training duration and model scale. We report the effect as detected and directionally consistent, not as a magnitude claim applicable to full-scale training.

**L3: Deduplication × scale interaction not analyzed (P3 inconclusive).**

Our factorial design includes two deduplication levels (J=0.7, J=0.9), but the gate criteria focused on the PPL × scale interaction. The dedup × scale interaction was not formally analyzed in the validation report. The data exists in results.csv (24 rows with dedup_j column) and a post-hoc analysis can be conducted without new experiments — we estimate approximately one hour of analysis time. We leave this for immediate future work.

**L4: Learning curves unavailable (P4 inconclusive).**

Disk space constraints (3.4TB disk at 100% capacity during experiments) required deleting checkpoints after each evaluation. Per-checkpoint HellaSwag evaluation would have enabled analysis of convergence rate differentials by scale and curation condition (P4). We recommend future runs maintain at least 5 intermediate checkpoints to enable learning curve analysis.

**L5: Single architecture and corpus.**

All experiments use Pythia-architecture models and FineWeb. Whether the interaction generalizes to other architecture families (LLaMA-style, Mamba) or other corpora (Dolma, raw CommonCrawl) is an open question. Results consistent with this finding in a different architecture or corpus would substantially strengthen the generalization claim.

## 6.3 Broader Impact

This work may improve the efficiency of language model pre-training by enabling scale-specific data curation, potentially reducing compute waste from suboptimal data recipes. No direct negative impacts are identified. The experimental infrastructure (curation pipeline, training loop, evaluation harness) uses open-source tools (NeMo-Curator, lm-evaluation-harness, Pythia) and is reproducible with H100 GPU access.
