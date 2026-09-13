# 4. Experimental Setup

We design our experiments to answer three questions, in order of priority:

**RQ1:** Is the M0 (full KV) pipeline functionally correct on LongBench 4-task QA — does it produce coherent, non-degenerate outputs at expected F1 values?

**RQ2:** Does the KV shape eviction mechanism (50% retention via top-k per head per layer) reduce cache dimensions as expected?

**RQ3:** Does M1 (prefill-observation with DynamicCache reconstruction) produce non-degenerate generation?

RQ1 and RQ2 are diagnostic — they establish that the pipeline is working correctly before the eviction method is applied. RQ3 is the condition that revealed the DynamicCache failure. The primary hypothesis comparison (M1 vs. M2) is deferred to a corrected experiment following the protocol in Section 3.5.

## 4.1 Dataset

We evaluate on LongBench v1 [Bai et al., 2023], a multi-task long-context benchmark with automated evaluation metrics. We use the following QA subset:

| Task | Type | Metric | Avg. Length (tokens) | Examples Used |
|------|------|--------|---------------------|---------------|
| NarrativeQA | Extractive QA | F1 | ~18K | 100 |
| HotpotQA | Multi-hop QA | F1 | ~9K | 100 |
| 2WikiMQA | Multi-hop QA | F1 | ~5K | 100 |
| MuSiQue | Multi-hop QA | F1 | ~11K | 100 |

All tasks are loaded from the HuggingFace Hub (THUDM/LongBench). We sample 100 examples per task uniformly using seed=42. We truncate inputs to 4096 tokens (LLaMA-2's native context window) following standard LongBench evaluation practice for smaller models.

The summarization tasks (GovReport, QMSum) were planned for the h-m2 task-conditional hypothesis test but were not reached in this experiment. All results below are on the 4-task QA subset only.

**Why this dataset:** LongBench provides (1) diverse long-context QA tasks with automated F1 evaluation, (2) standard benchmarks used in prior KV eviction papers (SnapKV, LongCache), and (3) sufficient examples for bootstrapped confidence intervals at 100 examples per task.

## 4.2 Model

We use LLaMA-2-7B-chat-hf (meta-llama/Llama-2-7b-chat-hf on HuggingFace Hub), an instruction-tuned 7B decoder-only transformer with grouped-query attention and a native 4096-token context window.

**Why this model:** Instruction-tuned variant was selected to avoid the base-model degeneration failure observed in a previous hypothesis (h-m2 used a base model at 80% KV eviction and failed catastrophically). SnapKV reports stable performance for this model at 40-60% KV retention. The 7B size fits on a single A100 40GB at FP16 (approximately 14GB VRAM for model weights).

## 4.3 Metric Conditions

| ID | Name | Timing | Score Function | Status in This Run |
|----|------|--------|----------------|-------------------|
| M0 | Full KV (no eviction) | N/A | No eviction | Completed |
| M1 | Prefill-Observation (SnapKV-style) | Prefill | Mean attn from last W=16 query tokens | Degenerate (F1=0.00) |
| M2 | Cumulative-Attention-at-Prefill | Prefill | Cumulative attn sum at prefill end | Not reached |
| M6 | StreamingLLM (static) | N/A | Attention sinks + sliding window | Not reached |

The planned experiment included M1 and M2 as the primary comparison (existence hypothesis h-e1) and M6 as the static lower-bound baseline. M3 (H2O-at-decode), M4 (ScissorHands warm-up), and M5 (attention entropy) were planned for subsequent hypothesis tests but were not implemented in this run.

## 4.4 Implementation Details

All experiments use the following configuration:

```yaml
model: meta-llama/Llama-2-7b-chat-hf
dataset: THUDM/LongBench
tasks: [narrativeqa, hotpotqa, 2wikimqa, musique]
examples_per_task: 100
seed: 42
max_context_length: 4096
retention_ratio: 0.50  # 50% KV retention for M1/M2
observation_window: 16  # M1 parameter (W in score_M1)
max_new_tokens: 50
torch_dtype: float16
device_map: auto
attn_implementation: eager
```

The `attn_implementation: "eager"` setting (explicit attention weight computation) is required to capture attention weights for importance scoring. With `sdpa` or `flash_attention_2`, attention weights are not exposed.

**Hardware:** Single A100 40GB GPU (H100 used in practice), FP16 precision.

**Runtime:** M0 evaluation completed across all 4 tasks in approximately 9 minutes (03:05 to 03:14). M1 on 3 tasks ran for approximately 7 minutes before experiment restart.

## 4.5 Evaluation Metrics

**Primary metric:** Macro-average F1 across the 4 QA tasks, computed using SQuAD-style normalization (lowercasing, punctuation removal, common function word removal). This matches the LongBench standard evaluation protocol.

**Hypothesis gate:** M1_macro_F1 − M2_macro_F1 ≥ 2.0 percentage points (raw F1 ≥ 0.02 difference) with 95% bootstrap CI lower bound > 0 (planned; not evaluable in this run).

**Note on F1 scale:** All F1 values in this paper are reported on the raw 0-1 scale (not percentage). The original gate criterion of "≥2.0 F1" was intended as 2 percentage points (consistent with LongBench paper reporting conventions). In raw scale, the criterion is ≥0.02. At M0 baseline of 0.0875 (8.75%), a 2-percentage-point improvement corresponds to M1 reaching approximately 0.1075 raw F1.
