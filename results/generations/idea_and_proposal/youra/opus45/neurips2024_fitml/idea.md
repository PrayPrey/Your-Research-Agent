# Research Idea

## Title
OSLO: Optimized Sparse and Low-rank Allocation for Parameter-Efficient Fine-Tuning via Reconstruction Error Sensitivity

## Motivation
Parameter-efficient fine-tuning (PEFT) methods like LoRA uniformly distribute capacity across transformer layers, ignoring that layers contribute differently to task adaptation. Recent work shows reconstruction error correlates with downstream performance, but existing approaches use heuristics for budget allocation. This creates a gap: no principled method optimally distributes sparse and low-rank capacity across layers under fixed parameter budgets, leaving 15-30% potential performance gains unrealized.

## Main Idea
OSLO proposes that layer-wise allocation of sparse and low-rank parameters, optimized via reconstruction error sensitivity, achieves superior fine-tuning performance compared to uniform allocation. The core mechanism operates in four steps: (1) compute gradient-based sensitivity ∂E_l/∂budget for each layer, (2) rank layers by adaptation potential, (3) allocate budget proportionally to sensitivity, and (4) optimize per-layer decomposition via alternating minimization.

The method will be validated on LLaMA-7B/13B using WikiText-2 perplexity, comparing against uniform allocation and LoSA baselines across 1-5% parameter budgets. We predict ≥15% perplexity reduction over uniform allocation, with strong correlation (r>0.7) between sensitivity and allocated budget. Falsification occurs if reduction falls below 5%. This advances PEFT theory by establishing principled allocation criteria and enables more efficient deployment under computational constraints.