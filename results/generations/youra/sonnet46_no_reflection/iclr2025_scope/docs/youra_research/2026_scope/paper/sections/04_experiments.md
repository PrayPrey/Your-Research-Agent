# 4. Experimental Setup

We design experiments to answer three research questions corresponding to the three completed sub-hypotheses in our verification plan:

- **RQ1:** Is there substantial and consistent misalignment between LoRA-adapted attention priorities and LM-trained Locret eviction scores on task-specific data? (H-E1)
- **RQ2:** Does task classification loss produce gradient signals that reach Locret retaining heads and improve GLUE accuracy over a frozen-Locret baseline? (H-M1)
- **RQ3:** Is joint training of LoRA and Locret parameters stable across multiple random seeds? (H-M2)

A fourth research question — **RQ4:** Does JointLoRA-KV achieve ≥3% improvement over the sequential baseline B3 on LongBench-QA at full training scale? — corresponds to H-M3 and is not answered in this paper. Code is implemented and validated; execution is pending full compute allocation.

## 4.1 Datasets

**GLUE Benchmark** [Wang et al., 2019]: We evaluate on three classification tasks — MNLI (Multi-Genre Natural Language Inference, 3-class), SST-2 (sentiment classification, 2-class), and QNLI (Question-NLI, 2-class). These tasks span different classification structures and provide established baselines. For H-E1, we use the MNLI validation_matched split (100 examples); for H-M1, we train on 500 examples per task and evaluate on 200 examples per task.

**LongBench** [Bai et al., 2024]: We evaluate on three long-context QA tasks — NarrativeQA, Qasper, and MultiFieldQA-en — requiring generation conditioned on long contexts (1K–30K tokens). These tasks represent the primary motivation for KV compression: they are infeasible without efficient KV management. For H-M2 stability verification, we evaluate on 50 examples per task.

We choose GLUE for mechanism verification (short-context, well-understood tasks with established accuracy baselines) and LongBench for the long-context QA evaluation where KV compression most directly impacts performance.

## 4.2 Model Configuration

| Component | Specification |
|-----------|--------------|
| Base model | meta-llama/Meta-Llama-3.1-8B-Instruct |
| LoRA rank | r=16, α=32, dropout=0.05 |
| LoRA target modules | q_proj, k_proj, v_proj |
| Locret checkpoint | hyx21/Locret-llama-3.1-8B-instruct |
| KV retention budget | 50% (b=0.50) for all compressed runs |
| Attention implementation | eager (required for projection hooks) |
| Hardware | NVIDIA H100 NVL |

## 4.3 Baselines

- **B1 (Frozen Locret):** LoRA training only; Locret retaining heads fixed at checkpoint values. No task-specific gradient reaches eviction policy. This is the direct ablation of JointLoRA-KV's joint training.
- **B2 (LoRA only, 100% budget):** No KV eviction — accuracy ceiling without compression. Used to quantify the compression-accuracy tradeoff.
- **B3 (Sequential LoRA→Locret, pending):** Standard pipeline: LoRA trained first with CE loss; Locret heads subsequently fine-tuned on the adapted model. Comparison vs B3 is the subject of H-M3.

B1 is the most critical baseline for mechanism verification: if JointLoRA-KV outperforms B1, it demonstrates that task-gradient signal to Locret heads produces measurable accuracy improvement. B2 bounds the analysis.

## 4.4 Evaluation Metrics

**GLUE tasks (MNLI, SST-2, QNLI):** Classification accuracy. We report mean accuracy across all three tasks as the primary GLUE metric.

**LongBench tasks (NarrativeQA, Qasper, MultiFieldQA-en):** Token-level F1 score [Rajpurkar et al., 2016] computed against ground-truth answer strings. We report mean F1 across tasks.

**Misalignment metric (H-E1):** Spearman rank correlation coefficient ρ between LoRA attention weights and Locret CIS scores, computed per example and averaged across 100 MNLI validation examples.

**Stability metrics (H-M2):** NaN event count and divergence event count (defined as loss increase >2.0× over a 100-step moving average), reported across 3 random seeds.

Statistical significance is evaluated via Spearman ρ for correlation analysis (H-E1) and by reporting results across all 3 random seeds for training stability (H-M2).

## 4.5 H-E1 Experimental Design

To measure the LoRA-Locret misalignment, we load two models sequentially (staying within GPU VRAM budget): first the LoRA-fine-tuned model (yophis/DRM-Llama-3.1-8B-mnli, a PeftModel), then the Locret model (hyx21/Locret-llama-3.1-8B-instruct). For each of 100 MNLI validation examples, we extract:

- **LoRA attention weights:** Per-token attention scores from the LoRA-adapted model, summed over heads. For LLaMA's GQA architecture (8 KV heads, 32 Q heads), we expand CIS scores to 32 query-head signals via repeat_interleave(4).
- **Locret CIS scores:** Contextual Importance Scores from the retaining heads, computed as CIS = σ([Q;K;V] @ W₁ᵀ) @ W₂ᵀ.

Spearman ρ is computed between the token-rank orders of the two score vectors per example, using only non-padding tokens. Padding tokens are excluded via the attention mask.

## 4.6 H-M1 Training Configuration (PoC Scale)

Due to compute constraints (4-hour timeout on H100 NVL), H-M1 runs at PoC scale:
- 1 seed (seed=42)
- 1 training epoch per task
- 500 training samples, 200 validation samples per task
- Batch size 4 per device, gradient accumulation steps 8 (effective batch 32)

Full protocol (3 seeds, 3 epochs MNLI / 5 epochs SST-2/QNLI, 2000 samples) is implemented in run_experiment.py and is the subject of H-M3.
