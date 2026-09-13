# ContinualKV: Adaptive KV Cache Compression via Continual Importance Learning

## Overview

This experiment implements and evaluates **ContinualKV**, a dynamic KV cache compression framework
that learns task-adaptive token importance scores through lightweight continual meta-learning.

**Key contributions tested:**
1. **Lightweight per-head importance scoring MLP** vs. attention-based baselines (H2O, SnapKV, etc.)
2. **Continual adaptation with EWC + sparse gradients** across 5 domain shifts (QA → Summarization → Code → RAG → Legal)
3. **Retrieval-aware budgeting for RAG** using relevance-score proportional allocation

## Experiment Setup

- **Model**: Synthetic attention heads (4 layers, 8 heads, d_head=32) to enable fast controlled evaluation
- **Task sequence**: QA → Summarization → Code → RAG → Legal (continual learning)
- **Sequence lengths**: 256 and 512 tokens
- **Compression ratios**: 0.3, 0.4, 0.5, 0.6, 0.7, 0.8 (fraction of tokens to keep)
- **Baselines**: Full KV Cache, H2O, StreamingLLM, SnapKV, DynamicKV

## How to Run

```bash
cd tasks_youra_result_sonnet46/iclr2025_scope/claude_code/
python run_experiment.py 2>&1 | tee outputs/log.txt
```

## Output Files

All outputs are saved to `outputs/`:
- `results.json` - Full numerical results
- `summary_table.csv` - Method comparison table
- `continual_learning_table.csv` - Continual learning metrics
- `training_curves.png` - Training loss curves across task domains
- `compression_performance.png` - Output similarity vs. compression ratio
- `memory_efficiency.png` - Memory reduction and overhead analysis
- `continual_learning.png` - BWT/FWT performance matrix
- `rag_performance.png` - RAG-aware budget allocation results
- `ablation_study.png` - Component ablation analysis
- `scaling_analysis.png` - Performance vs. sequence length scaling

## Requirements

```
torch>=2.0.0
numpy
matplotlib
```
