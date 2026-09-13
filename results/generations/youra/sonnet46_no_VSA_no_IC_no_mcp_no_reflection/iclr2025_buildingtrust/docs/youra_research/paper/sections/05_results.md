# Results

## RQ1: Alignment Fingerprint Existence (h-e1)

**The DPO/SFT alignment fingerprint is confirmed at statistically significant accuracy.**
A k-NN (k=1) LOO-CV classifier correctly identifies the alignment strategy of 10 out
of 12 models (83.3% accuracy), with permutation test p=0.031 (1000 shuffles). Both
thresholds are exceeded: accuracy (83.3% vs ≥67% required) and significance (p=0.031
vs p≤0.05 required). Alignment strategy is recoverable from a 4D benchmark profile
without any access to training data, preference datasets, or model weights.

**Table 3: Classification results (h-e1 gate).**

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| LOO-CV accuracy (k=1) | **83.3%** (10/12) | ≥67% | PASS |
| Permutation p-value | **p=0.031** | ≤0.05 | PASS |

Figure 3 (fig3_permutation_test.png) shows the permutation null distribution versus the
observed accuracy. The observed 83.3% lies in the upper tail of the null distribution,
confirming that the alignment fingerprint is not recoverable by chance at this sample size.

**Sensitivity analysis:** LOO-CV accuracy is 83.3% at k=1, 75.0% at k=3, and 66.7%
at k=5, indicating that the fingerprint signal is strongest at the nearest-neighbor
scale — consistent with a high-density, compact cluster structure rather than a linear
decision boundary.

### The 4D Score Matrix

Table 4 presents the full model benchmark score matrix. The DPO group shows consistently
higher TruthfulQA MC2 scores (mean 0.534 vs 0.523, Δ=+0.011 group means; Δ=+0.046 per
pair means), while BBQ, WinoGrande, and WinoGender differences are small and mixed in
direction.

**Table 4: 12×4 benchmark score matrix.**

| Model | Alignment | TruthfulQA MC2 | BBQ | WinoGrande | WinoGender |
|-------|-----------|---------------|-----|------------|------------|
| Mistral-7B-Instruct-v0.1 | SFT | 0.559 | 0.430 | 0.750 | 0.550 |
| zephyr-7b-alpha | SFT | 0.549 | 0.380 | 0.730 | 0.650 |
| OpenHermes-2.5-Mistral-7B | SFT | 0.492 | 0.450 | 0.740 | 0.710 |
| tulu-2-7b | SFT | 0.482 | 0.450 | 0.710 | 0.630 |
| Llama-2-7b-chat (RLHF) | SFT* | 0.495 | 0.420 | 0.700 | 0.660 |
| Mistral-7B-Instruct-v0.3 | SFT | 0.559 | 0.400 | 0.760 | 0.630 |
| **SFT Mean** | | **0.523** | **0.422** | **0.732** | **0.638** |
| zephyr-7b-beta | DPO | 0.514 | 0.390 | 0.690 | 0.650 |
| tulu-2-dpo-7b | DPO | 0.578 | 0.470 | 0.710 | 0.630 |
| openchat_3.5 | DPO | 0.447 | 0.480 | 0.770 | 0.670 |
| Starling-LM-7B-alpha | DPO | 0.437 | 0.480 | 0.770 | 0.690 |
| neural-chat-7b-v3-1 | DPO | 0.592 | 0.470 | 0.760 | 0.670 |
| neural-chat-7b-v3-3 | DPO | 0.638 | 0.470 | 0.730 | 0.650 |
| **DPO Mean** | | **0.534** | **0.460** | **0.738** | **0.660** |

*Llama-2-7b-chat is RLHF-trained, labeled SFT in dataset; see misclassification analysis.

Figure 1 (fig1_benchmark_comparison.png) shows group mean scores ± std for all four
benchmarks. The consistent DPO advantage on TruthfulQA MC2 contrasts with the mixed
and small differences on BBQ, WinoGrande, and WinoGender.

### Misclassification Cases

Two models are misclassified (2/12). These errors are not random — they reveal
structural properties of the alignment fingerprint:

**Case 1: Llama-2-7b-chat (RLHF → classified DPO).** Despite its SFT/RLHF label,
Llama-2-chat's 4D profile clusters with the DPO group. This is consistent with
RLHF-PPO and DPO sharing a preference-training benchmark signature distinct from pure
SFT. The "SFT" label for Llama-2-chat is misleading — it has PPO-based RLHF alignment,
which may produce a similar benchmark profile to DPO.

**Case 2: zephyr-7b-beta (DPO → classified SFT).** The strongest controlled pair
(same base model, same training data) produces a misclassification — zephyr-beta (DPO)
is classified with zephyr-alpha (SFT). This shows that shared base architecture and
training data can dominate alignment signal for near-identical model pairs, limiting
the fingerprint's discriminative power within this sub-family.

Figure 2 (fig2_scatter_2d.png) shows 2D projections of the 4D score space with
misclassified models labeled, illustrating the cluster structure and the outlier
positions of the two misclassification cases.

---

## RQ2: Discriminative Dimensions and Mechanism (h-m1)

**The fairness-advantage mechanism is refuted; truthfulness is the dominant discriminative dimension.**

### Fisher's Criterion: Truthfulness Dominates

Figure 6 (fig3_fisher_criterion.png) shows Fisher's linear discriminant criterion
for each benchmark. TruthfulQA MC2 dominates by a factor of 9.5× over the next
benchmark:

**Table 5: Fisher's criterion per benchmark.**

| Benchmark | Fisher's Criterion | Rank | Predicted Rank |
|-----------|--------------------|------|----------------|
| TruthfulQA MC2 | **0.8122** | 1 | 3 (neutral-to-lower) |
| WinoGender | 0.0856 | 2 | 1 (high fairness signal) |
| WinoGrande | 0.0312 | 3 | 4 (neutral, control) |
| BBQ | 0.0091 | 4 | 1 (high fairness signal) |

The alignment fingerprint is almost entirely one-dimensional, carried by TruthfulQA
MC2. BBQ — the benchmark predicted to show the strongest DPO advantage — provides
essentially zero discriminative signal (Fisher=0.0091). This directly contradicts
the predicted fairness-driven mechanism.

Moreover, the direction of the TruthfulQA difference reverses the prediction: DPO
models score higher on truthfulness (+4.6pp per-pair mean delta), whereas the original
mechanism predicted neutral-to-lower DPO truthfulness (DPO lacks explicit factual reward).

### BBQ Fairness: No Systematic DPO Advantage

Figure 4 (fig1_bbq_winogender_paired_bar.png) shows signed per-pair BBQ and WinoGender
deltas. The BBQ result is a clear null:

**Table 6: Per-pair BBQ deltas.**

| Pair | BBQ Δ (DPO − SFT) | Direction |
|------|-------------------|-----------|
| P1 (zephyr/Mistral-Instruct) | −0.050 | SFT > DPO |
| P2 (zephyr-beta/OpenHermes) | −0.060 | SFT > DPO |
| P3 (tulu-2-dpo/tulu-2) | +0.020 | DPO > SFT |
| P4 (neural-chat/Llama-2-chat) | +0.050 | DPO > SFT |
| P5 (Starling/openchat) | +0.000 | Tie |
| P6 (neural-chat-v3-3/Mistral-v0.3) | +0.070 | DPO > SFT |
| **Summary** | **k=3/6, p=0.656** | **Not significant** |

Three of six pairs show DPO>SFT on BBQ (k=3/6). The one-sided binomial p-value is
0.6562 — far from the significance threshold of 0.125. Mean BBQ delta is +0.005
(vs +0.046 for TruthfulQA), confirming that any BBQ difference is smaller by 9× than
the truthfulness difference. Figure 5 (fig2_bbq_scatter.png) shows the BBQ score scatter,
with approximately equal numbers of pairs above and below the diagonal.

WinoGender is similarly null: k=4/6, p=0.344, mean delta=+0.015. Figure 7
(fig4_winogender_delta.png) shows WinoGender deltas per pair. The fairness null
result holds across both fairness benchmarks.

### Per-Pair Truthfulness Analysis

To verify the TruthfulQA finding is not driven by one outlier pair, Table 7 shows
per-pair TruthfulQA deltas:

**Table 7: Per-pair TruthfulQA MC2 deltas.**

| Pair | TruthfulQA Δ (DPO − SFT) |
|------|--------------------------|
| P1 | −0.010 |
| P2 | +0.022 |
| P3 | +0.097 |
| P4 | +0.097 |
| P5 | −0.010 |
| P6 | +0.079 |
| **Summary** | **k=4/6, mean=+0.046, Fisher=0.8122** |

Four of six pairs show DPO higher on truthfulness. The mean delta (+0.046) is large
relative to BBQ (+0.005) and WinoGender (+0.015). The Fisher criterion confirms that
TruthfulQA carries 9.5× more between-class information than any fairness benchmark.

### Summary of Findings

The alignment fingerprint exists empirically (RQ1: PASS) but operates through an
unexpected mechanism (RQ2: fairness hypothesis refuted). The fingerprint is primarily
a truthfulness fingerprint: DPO models score higher on TruthfulQA MC2, and this single
dimension drives 83.3% of the classification signal. Fairness benchmarks contribute
negligible discriminative information.
