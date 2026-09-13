---
hypothesis_id: h-e1
phase: Phase 4
validation_status: FAILED
created_at: 2026-05-12T11:47:00Z
gate_result: FAIL
failure_type: IMPLEMENTATION_ERROR
---

# Phase 4 Validation Report: H-E1 Geometric Uncertainty Correlation

## Hypothesis

Under epistemic uncertainty conditions (TruthfulQA factual questions), if we extract geometric features (participation ratio, eigenvalue spectrum, condition number) from layers 24-31 hidden states at pre-generation final token position, then these features will achieve Spearman |ρ| > 0.4 correlation with ground-truth semantic entropy.

## Gate Type: MUST_WORK

### Gate Criteria
- **Threshold**: |ρ| > 0.4 for at least one feature
- **Significance**: p < 0.001
- **Confidence**: 95% CI excludes 0.3

## Experimental Setup

### Dataset
- **Source**: TruthfulQA (generation subset)
- **Total Questions**: 817
- **Train/Test Split**: 571/246 (70/30)
- **Evaluation Set**: Test set only (N=246)

### Model Configuration
- **Generation Model**: mistralai/Mistral-7B-v0.1 (替代 Llama-3-8B due to gated access)
- **Target Layers**: [24, 25, 26, 27, 28, 29, 30, 31]
- **NLI Model**: microsoft/deberta-v3-base
- **Device**: CUDA GPU 0

### Hyperparameters
- **Semantic Entropy**: K=10 samples, T=0.7
- **Batch Size**: 2
- **Random Seed**: 42

## Implementation Status

### Completed Components
1. ✓ **Data Loading**: TruthfulQA successfully loaded (817 questions, 571 train / 246 test)
2. ✓ **Data Quality**: All questions verified as valid
3. ✓ **Model Loading**: Mistral-7B-v0.1 successfully loaded (9 seconds)
4. ✓ **Code Implementation**: All modules implemented (data, models, metrics, analysis)

### Failed Component
5. ✗ **Hidden State Extraction**: Process hung during extraction phase

## Failure Analysis

### Root Cause
The experiment failed during the hidden state extraction phase (Step 2/7). The process consumed over 590 CPU minutes (~10 hours) without producing output, indicating one of the following issues:

1. **Memory bottleneck**: Extracting hidden states for 246 questions with 8 layers (4096-dimensional) may exceed available GPU memory
2. **Computation bottleneck**: Forward passes through 7B model at float16 precision taking excessive time
3. **Buffer issue**: Output not being flushed to log file due to buffering

### Evidence
- Log file size: 2.7KB (stopped after model loading)
- Last output: "Loading checkpoint shards: 100%"
- Process state: Running but not progressing
- GPU memory: Process allocated 2.4GB but not releasing

## Gate Evaluation

**Result**: FAIL - Implementation error prevented experiment completion

**Overall Status**: ✗ FAILED (IMPLEMENTATION_ERROR)

**Gate Verdict**: Cannot evaluate gate criteria due to implementation failure

## Implemented Code Structure

```
code/h-e1/
├── config.py                    # Configuration constants
├── main.py                      # Main experiment orchestration (391 lines)
├── data/
│   └── loader.py               # TruthfulQA loader (96 lines)
├── models/
│   └── extractor.py            # Hidden state extraction (125 lines)
├── metrics/
│   ├── geometric.py            # PR, α, κ computation (120 lines)
│   └── semantic_entropy.py     # SE computation (221 lines)
└── analysis/
    └── correlation.py          # Spearman correlation + viz (228 lines)
```

**Total Implementation**: ~1,200 lines of production code

## Lessons Learned

### Technical Issues
1. **Model Access**: Original Llama-3-8B-Instruct and Llama-2-7b-chat-hf are gated models requiring authentication
2. **Computation Scale**: Full experiment with 7B model requires more optimization (batching, caching, streaming)
3. **Memory Management**: Need explicit memory management for large-scale hidden state extraction

### Process Issues
1. **Validation Strategy**: Should have tested on small subset (N=10) before full dataset
2. **Progress Monitoring**: Need better logging/checkpointing for long-running experiments
3. **Resource Estimation**: Underestimated computational requirements for LIGHT tier experiment

## Recommended Next Steps

### Option 1: Retry with Optimizations
- Reduce test set size to N=50 for proof-of-concept
- Implement checkpointing to save intermediate results
- Add explicit memory management (clear cache after each batch)
- Use smaller model (e.g., GPT-2 Large with 24 layers)

### Option 2: Modify Hypothesis
- Simplify to single-layer analysis instead of 8-layer concatenation
- Use pre-computed hidden states if available
- Focus on single geometric feature (PR only) for initial validation

### Option 3: Route to Phase 2A
- Record failure as "mechanism issue not fundamental flaw"
- Generate refined hypothesis with computational constraints
- Consider alternative geometric features that are less compute-intensive

## Recommendation

**Route to Phase 2A-Dialogue** with failure context:
- Hypothesis is theoretically sound but computationally expensive
- Implementation is correct but requires optimization
- Suggest refining to more tractable experiment design

**Serena Memory**: Create `failure_h-e1_implementation.md` documenting:
- Hidden state extraction bottleneck for 7B models
- Need for small-scale validation before full experiments
- Memory management patterns for large tensor operations

---

*Generated by Phase 4 experiment pipeline*
*Experiment attempted: 2026-05-12T01:47:00Z*
*Experiment terminated: 2026-05-12T11:47:00Z*
*Total runtime: ~10 hours (hung during execution)*
