# Experimental Setup

Our experiments verify the complete causal chain from architecture conversion through landscape geometry to task-dependent adaptation efficiency. Each experiment tests a specific hypothesis with MUST_WORK gates ensuring rigorous validation.

## Experimental Questions

We structure experiments around five questions corresponding to our hypothesis chain:

1. **Does task-dependent adaptation transformation exist?** (H-E1)
2. **Does architecture conversion transform loss landscape geometry?** (H-M1)
3. **Does SSM state evolution create sequential-favorable landscapes?** (H-M2)
4. **Does landscape geometry predict LoRA adaptation efficiency?** (H-M3)
5. **Does task-dependent transformation emerge from architecture-task interaction?** (H-M4)

## Datasets

We evaluate on four benchmarks spanning the retrieval density spectrum:

**GSM8K** (retrieval density: 0.1): Grade school math problems requiring step-by-step reasoning. 1,319 test samples. Represents sequential reasoning tasks where chain-of-thought processing aligns with SSM state evolution.

**MMLU** (retrieval density: 0.5): Multiple-choice questions across 57 subjects mixing factual recall and reasoning. 14,042 test samples. Represents mixed-dependency tasks.

**HotpotQA** (retrieval density: 0.7): Multi-hop question answering requiring retrieval and reasoning over multiple documents. 7,405 test samples. Represents tasks needing both retrieval and synthesis.

**Natural Questions** (retrieval density: 0.9): Factual questions from real Google queries requiring precise knowledge retrieval. 3,610 test samples. Represents retrieval-heavy tasks where arbitrary token-to-token access is critical.

Total evaluation samples: 26,376 across the task spectrum.

## Baselines

**Transformer + LoRA**: Standard LoRA on Llama-2 architecture targeting attention projections (q_proj, k_proj, v_proj, o_proj). This is our primary baseline establishing pre-conversion performance.

**Mamba-converted + LoRA**: LoRA on Mamba architecture after conversion from Transformer, targeting analogous projections (in_proj, out_proj). Same LoRA configuration ensures fair comparison.

## Evaluation Metrics

**Primary Metrics**:
- Task accuracy: Correct responses / total samples
- Accuracy delta: Mamba accuracy - Transformer accuracy
- SAM sharpness: Maximum loss under perturbation
- Sharpness ratio: Sequential sharpness / Retrieval sharpness

**Correlation Metrics**:
- Spearman ρ (sharpness vs. effective rank)
- Spearman ρ (retrieval density vs. accuracy delta)
- p-values for statistical significance

**Gate Conditions**:
| Hypothesis | Metric | Threshold |
|------------|--------|-----------|
| H-E1 | GSM8K delta | ≥ -5% |
| H-E1 | NQ delta | ≤ -15% |
| H-E1 | Density correlation | > 0.5 |
| H-M1 | Sharpness delta | > 10% |
| H-M1 | KL divergence | > 0.1 |
| H-M2 | Sharpness ratio | < 0.8 |
| H-M3 | Sharpness-rank ρ | > 0.5 |
| H-M4 | Density-delta ρ | > 0.7 |

## Implementation Details

**Model Configuration**:
- Base model: 512-dimensional reduced architecture for proof-of-concept
- LoRA: rank=16, alpha=32, dropout=0.0
- Training: AdamW optimizer, lr=2e-4 (H-E1) or 1e-4 (H-M2-M4)
- Schedule: Cosine decay with 100 warmup steps
- Epochs: 3-5 per benchmark
- Batch size: 4
- Seed: 42

**Sharpness Measurement**:
- Method: SAM perturbation
- Epsilon: 0.05
- Batches: 100
- Computed post-adaptation on validation set

**Effective Rank Computation**:
- Method: SVD of learned LoRA AB matrices
- Threshold: 90% cumulative energy
- Computed after training convergence

## Experimental Flow

```
Phase 1: Existence Verification (H-E1)
├── Train Transformer + LoRA on all 4 benchmarks
├── Train Mamba-converted + LoRA on all 4 benchmarks
├── Compute accuracy deltas
└── Gate: Pattern exists if GSM8K preserved, NQ degraded, ρ > 0.5

Phase 2: Mechanism Verification (H-M1 → H-M4)
├── H-M1: Compare landscape geometry pre/post conversion
├── H-M2: Compare sharpness by task type
├── H-M3: Correlate sharpness with effective rank
└── H-M4: Correlate retrieval density with delta

Each phase gates the next; failure triggers hypothesis refinement.
```
