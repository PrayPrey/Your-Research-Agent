# Experimental Setup

## Experimental Questions

Our experiments address three questions:

1. **Framework validity**: Can both matrix-level and token-level objectives be implemented and trained in a unified framework? (H-E1)

2. **Teacher context limits**: Does Phi-1.5 exhibit extrapolation artifacts at extended sequence lengths? (H-M1)

3. **Representation stability**: Do token-level and matrix-level objectives produce different drift patterns across sequence lengths? (H-M2)

## Models

**Teacher**: Phi-1.5 (microsoft/phi-1_5), 1.3B parameters. Trained on 2048-token sequences with learned absolute positional embeddings. We discovered that Phi-1.5 has a *hard* 2048 token limit—attempting to process longer sequences produces IndexError on position embeddings, not degraded attention patterns. This architectural constraint defines the scope boundary for our length extrapolation analysis.

**Student**: Phi-Mamba with MOHAWK modifications:
- Multi-head SSM structure matching attention heads
- Removed Δ parameter (open gates)
- Embedding and output layers initialized from teacher
- 4 layers (PoC) / 24 layers (full)

**Simulated student proxy**: For drift analysis without full distillation training, we use MambaForCausalLM (state-spaces/mamba-1.4b-hf) with learned projection layers mapping teacher representations to SSM-compatible dimensions.

## Datasets

**Training**: C4 dataset (allenai/c4) via streaming access. 1M tokens (PoC) / 1.5B tokens per condition (full). Phi tokenizer for consistent vocabulary.

**Drift analysis**: 500 samples per sequence length from C4 validation split. Lengths: 512, 1024, 1536, 2048 tokens.

## Distillation Objectives

**MOHAWK (matrix-level)**:
- Stage 1: Mixer output alignment ||TeacherMixer - StudentMixer||²
- Stage 2: Hidden state matching ||TeacherHidden - StudentHidden||²
- Stage 3: Language modeling loss on C4

**CAB (token-level)**:
- Q/K → B/C bridge alignment via 2-layer MLPs
- Hidden size 256 (PoC) / 2048 (full)
- No attention map materialization

## Evaluation Metrics

**Primary metric**: Hidden state drift slope
- Linear regression of L2 drift against sequence length
- Lower slope = more stable representations across lengths
- Statistical significance at p < 0.05

**Secondary metrics**:
- Drift ratio: Drift(2048) / Drift(512)
- Cosine similarity degradation
- Per-layer drift heatmaps

## Hypotheses Tested

| ID | Hypothesis | Gate | Success Criterion |
|----|------------|------|-------------------|
| H-E1 | Unified framework validates both objectives | MUST_WORK | No execution errors |
| H-M1 | Phi-1.5 attention extrapolation artifacts | MUST_WORK | Measurable degradation >2048 |
| H-M2 | Token-level drift slope < matrix-level | MUST_WORK | CAB slope < MOHAWK slope (p<0.05) |
| H-M3 | F1 retention interaction effect | MUST_WORK | Interaction p < 0.05 |

## Implementation Details

Training conducted on NVIDIA A100 (40GB). PoC experiments: 500 steps per objective, batch size 8, sequence length 64. Full experiments: ~1.5B tokens, full sequence lengths.

Statistical analysis: scipy.stats.linregress for slope estimation, 95% confidence intervals via bootstrap (1000 resamples).
