# 4. Experimental Setup

## 4.1 Research Questions

We design experiments to answer three ordered questions:

**RQ1 (Mechanism Gate):** Does MOHAWK's SSD structured mixer approximate LLaMA-3-8B attention
matrices with sub-linear normalized Frobenius error as sequence length increases from 512 to 2048
tokens? This gate must be evaluated before behavioral tests can be interpreted.

**RQ2 (Behavioral Interaction):** Does conversion strategy (MOHAWK-SSM vs LAWCAT) produce a
statistically significant task-type × strategy interaction on LongBench v2 normalized accuracy
degradation — specifically, does MOHAWK-SSM degrade disproportionately more on retrieval-heavy
categories than LAWCAT? (*Results pending H-E1 completion.*)

**RQ3 (Depth-Slope Mechanism):** Does LAWCAT's Conv1D local attention produce a shallower
needle-depth accuracy degradation slope than MOHAWK-SSM's bounded state on LongBench v2
retrieval tasks? (*Infrastructure validated; requires H-E1 checkpoints.*)

RQ1 maps directly to Contribution 1 (mechanism gate). RQ2 and RQ3 map to Contributions 2 and 3
(behavioral test and depth-slope analysis). The sequencing reflects the causal logic: RQ1 must
be resolved before RQ2 and RQ3 can be correctly interpreted.

## 4.2 Datasets

**Mechanism Gate (RQ1):** 50 random sequences from `monology/pile-uncopyrighted` (seed=42) at
N ∈ {512, 1024, 2048} tokens, producing 1,760 attention matrix measurements (50 samples × 32
layers at N=512; 5 samples × 32 layers at N=1024 and N=2048).

| Dataset | Purpose | N Samples |
|---------|---------|-----------|
| monology/pile-uncopyrighted | Attention matrix extraction for mechanism gate | 50 (N=512), 5 (N=1024,2048) |
| THUDM/LongBench v2 | Task-type × strategy behavioral evaluation | 503 questions |

**Behavioral Test (RQ2–3):** LongBench v2 [Bai et al., ACL 2025] (503 questions, 6 categories,
context 8K–2M tokens). We use the full question set for RQ2 and the retrieval subset (158
multi-document QA and synthetic questions, 111 unique depth percentile values) for RQ3.

*Why LongBench v2:* It provides the category structure (retrieval-heavy vs generation-heavy tasks)
needed for the interaction test. The benchmark has established baselines from scratch-trained SSMs
[Overflow Prevention, 2025] enabling external comparison. The 503-question set provides adequate
statistical power for the category-level mixed-effects model.

## 4.3 Baselines

| Model | Method | Why Included |
|-------|--------|--------------|
| LLaMA-3-8B (teacher) | Unconverted, full attention | Establishes Δ_norm denominator; control condition |
| MOHAWK-SSM | 3-stage distillation, SSD mixer | Primary conversion strategy; mechanism gate subject |
| LAWCAT | 2-phase distillation, Conv1D + gated linear attention | Comparison strategy; different forgetting mechanism |
| Hybrid-4 | MOHAWK Stage 3 + 4 middle attention layers | Tests whether 4 attention layers recover retrieval |
| Falcon3-Mamba-7B (external) | Scratch-trained SSM [Overflow Prevention, 2025] | External reference: is distilled SSM better than scratch-trained? |

The Falcon3-Mamba-7B numbers are taken directly from the Overflow Prevention paper [arXiv:2505.07793]
and are not re-evaluated (different model family and training paradigm; included as context only).

## 4.4 Evaluation Metrics

**Mechanism Gate:**
- Log-log slope β of normalized Frobenius error vs N (threshold: ≤ 0.5)
- 90th percentile normalized error at maximum N (threshold: ≤ 0.3)

**Behavioral Test:**
- Δ_norm = (Acc_teacher − Acc_student) / Acc_teacher per category per strategy
- Ratio Δ_norm^MOHAWK(retrieval) / Δ_norm^LAWCAT(retrieval) (gate: ≥ 2.0)
- Task-type × strategy interaction p-value (gate: < 0.01, Holm correction)

**Depth-Slope:**
- β_depth from per-model logistic regression: P(correct) ~ DepthPercentile + (1|Task)
- Ratio |β_depth^MOHAWK| / |β_depth^LAWCAT| (gate: ≥ 2.0, non-overlapping CIs)

Statistical significance is evaluated using 95% bootstrap confidence intervals (10,000 resamples)
for the ratio and Holm-corrected Wald tests for the mixed-effects interaction term.

## 4.5 Implementation Details

| Setting | Value |
|---------|-------|
| Teacher model | meta-llama/Llama-3.1-8B |
| Teacher dtype | bfloat16 |
| SSD fitting dtype | float32 (SSMs sensitive to precision) |
| SSD fitting steps | 500 |
| SSD fitting lr | 1e-3 (Adam, β=(0.9, 0.999)) |
| d_state | 64 |
| Hardware | 4× H100 NVL 96GB |
| MOHAWK total budget | ~1B tokens (Stage 1: 26M, Stage 2: 52M, Stage 3: 922M) |
| Max sequence length | 2048 (N=4096+ OOM with eager attention at N×N×n_heads) |

The experiment was implemented using `goombalab/mohawk` (official MOHAWK implementation),
`THUDM/LongBench` evaluation harness, and `statsmodels` / `rpy2` for mixed-effects regression.
All 22 unit tests pass. Code artifacts are available at [repository URL pending].
